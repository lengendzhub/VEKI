# backend/app/services/ai_engine.py
from __future__ import annotations

import pickle
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd

from app.config import get_settings
from app.ml.model_registry import ModelRegistry
from app.schemas.analysis import MarketRegime
from app.schemas.proposal import TradeProposal
from app.services.data_validator import DataQualityError, DataValidator
from app.services.feature_engineer import FeatureEngineer
from app.services.logger import quant_logger
from app.services.news_filter import NewsFilter


class AIEngine:
    def __init__(self, feature_engineer: FeatureEngineer, news_filter: NewsFilter, validator: DataValidator) -> None:
        self.settings = get_settings()
        self.registry = ModelRegistry(models_dir=self.settings.MODELS_DIR)
        self.fe = feature_engineer
        self.news = news_filter
        self.validator = validator
        self._loaded = False
        self._artifact: dict[str, Any] | None = None
        self._active_version = "untrained"

    async def load_models(self) -> None:
        version = self.registry.get_active_version()
        await self.reload_models(version=version)

    async def analyse(self, symbol: str, df_4h: pd.DataFrame, df_1h: pd.DataFrame, df_5m: pd.DataFrame) -> TradeProposal | None:
        if not self._loaded:
            await self.load_models()

        blocked, event_name = self.news.is_high_impact_window(df_5m.index[-1].to_pydatetime())
        if blocked:
            quant_logger.news_block(symbol=symbol, event_name=event_name or "unknown", minutes_remaining=15)
            return None

        try:
            clean4 = self.validator.validate(df_4h, symbol, "H4").clean_df
            clean1 = self.validator.validate(df_1h, symbol, "H1").clean_df
            clean5 = self.validator.validate(df_5m, symbol, "M5").clean_df
        except DataQualityError:
            return None

        features = self.fe.build(clean4, clean1, clean5)

        if self.settings.MTF_CONFLUENCE_REQUIRED and not self.fe._check_mtf_confluence(features.direction_4h, features.direction_1h, features.direction_5m):
            quant_logger.mtf_misalignment(symbol, features.direction_4h, features.direction_1h, features.direction_5m)
            return None

        if features.regime == MarketRegime.LOW_VOLATILITY:
            return None

        meta_p = self._score_probability(clean5)
        if features.regime == MarketRegime.RANGE:
            meta_p *= 0.9

        if meta_p < self.settings.CONFIDENCE_GATE:
            return None

        direction = features.direction_5m
        entry = float(clean5["close"].iloc[-1])
        atr = max(float((clean5["high"] - clean5["low"]).rolling(14).mean().iloc[-1]), 0.0004)
        sl = entry - atr if direction == "long" else entry + atr
        tp = entry + (atr * 2) if direction == "long" else entry - (atr * 2)

        return TradeProposal(
            symbol=symbol,
            timeframe="M5",
            direction=direction,
            confidence=round(meta_p, 4),
            entry_price=entry,
            stop_loss=sl,
            take_profit=tp,
            atr=atr,
            regime=features.regime.value,
            explanation=self._explain(features, direction, features.regime.value, [0.1, 0.2, 0.3, 0.4], self._active_version),
        )

    def _explain(self, features, direction: str, regime: str, attention_weights: list[float], model_version: str) -> str:
        top_attention = max(range(len(attention_weights)), key=attention_weights.__getitem__)
        return (
            f"ICT signal {direction.upper()} in {regime}. "
            f"MTF alignment: {features.direction_4h}/{features.direction_1h}/{features.direction_5m}. "
            f"RSI={features.rsi_5m:.2f}, ATR={features.atr_5m:.5f}, attention_peak_t={top_attention}, model={model_version}."
        )

    async def reload_models(self, version: str) -> None:
        self._artifact = None
        self._active_version = "untrained"
        if not version or version == "untrained":
            self._loaded = True
            return

        path = Path(self.settings.MODELS_DIR) / version / "artifact.pkl"
        if path.exists():
            with path.open("rb") as f:
                self._artifact = pickle.load(f)
            self._active_version = version

        self._loaded = True

    def _score_probability(self, df_5m: pd.DataFrame) -> float:
        X = self._build_inference_features(df_5m)
        if X is None:
            return 0.5

        if self._artifact is None:
            return self._heuristic_probability(X)

        xgb = self._artifact.get("xgb")
        lstm = self._artifact.get("lstm")
        meta = self._artifact.get("meta")

        xgb_p = self._predict_model(xgb, X) if isinstance(xgb, dict) else 0.5
        lstm_p = self._predict_model(lstm, X) if isinstance(lstm, dict) else 0.5
        if not isinstance(meta, dict):
            return float(np.clip((xgb_p + lstm_p) / 2, 0.0, 1.0))

        alpha = float(meta.get("alpha", 0.6))
        beta = float(meta.get("beta", 0.4))
        base = float(meta.get("base", 0.5))
        denom = max(1e-9, alpha + beta + 0.1)
        p = (alpha * xgb_p + beta * lstm_p + 0.1 * base) / denom
        return float(np.clip(p, 0.0, 1.0))

    def _build_inference_features(self, df_5m: pd.DataFrame) -> pd.DataFrame | None:
        if len(df_5m) < 25:
            return None

        close = df_5m["close"].astype(float)
        high = df_5m["high"].astype(float)
        low = df_5m["low"].astype(float)
        open_ = df_5m["open"].astype(float)
        volume = df_5m["volume"].astype(float)

        ret_1 = close.pct_change(1)
        ret_3 = close.pct_change(3)
        ret_12 = close.pct_change(12)
        volatility_12 = ret_1.rolling(12, min_periods=12).std()

        close_safe = close.replace(0, np.nan)
        range_norm = (high - low) / close_safe
        body_norm = (close - open_).abs() / close_safe

        vol_mean = volume.rolling(20, min_periods=20).mean()
        vol_std = volume.rolling(20, min_periods=20).std().replace(0, np.nan)
        volume_z = (volume - vol_mean) / vol_std

        frame = pd.DataFrame(
            {
                "ret_1": [float(ret_1.iloc[-1])],
                "ret_3": [float(ret_3.iloc[-1])],
                "ret_12": [float(ret_12.iloc[-1])],
                "volatility_12": [float(volatility_12.iloc[-1])],
                "range_norm": [float(range_norm.iloc[-1])],
                "body_norm": [float(body_norm.iloc[-1])],
                "volume_z": [float(volume_z.iloc[-1])],
            }
        )

        frame = frame.replace([np.inf, -np.inf], np.nan).fillna(0.0)
        return frame

    def _heuristic_probability(self, X: pd.DataFrame) -> float:
        ret = float(X["ret_3"].iloc[0])
        vol = float(X["volatility_12"].iloc[0])
        body = float(X["body_norm"].iloc[0])
        score = (ret * 120.0) - (vol * 20.0) + (body * 5.0)
        p = 1.0 / (1.0 + float(np.exp(-np.clip(score, -20, 20))))
        return float(np.clip(p, 0.0, 1.0))

    def _predict_model(self, model: dict[str, Any], X: pd.DataFrame) -> float:
        name = str(model.get("name", "")).lower()

        if "xgb" in name:
            weights = model.get("weights", {})
            bias = float(model.get("bias", 0.5))
            score = bias
            if isinstance(weights, dict):
                for col, w in weights.items():
                    if col in X.columns:
                        score += float(X[col].iloc[0]) * float(w)
            p = 1.0 / (1.0 + float(np.exp(-np.clip(score, -20, 20))))
            return float(np.clip(p, 0.0, 1.0))

        if "lstm" in name:
            momentum = float(model.get("momentum", 0.0))
            vol = float(model.get("volatility", 0.0))
            bias = float(model.get("bias", 0.5))
            ret = float(X["ret_3"].iloc[0])
            vol_x = float(X["volatility_12"].iloc[0])
            score = bias + (ret * (1.0 + momentum)) - (vol_x * (1.0 + vol))
            p = 1.0 / (1.0 + float(np.exp(-np.clip(score, -20, 20))))
            return float(np.clip(p, 0.0, 1.0))

        return 0.5
