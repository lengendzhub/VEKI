# backend/app/services/feature_engineer.py
from __future__ import annotations

from dataclasses import dataclass

import pandas as pd

from app.schemas.analysis import MarketRegime


@dataclass
class Features:
    direction_4h: str
    direction_1h: str
    direction_5m: str
    regime: MarketRegime
    rsi_5m: float
    atr_5m: float


class FeatureEngineer:
    def build(self, df_4h: pd.DataFrame, df_1h: pd.DataFrame, df_5m: pd.DataFrame) -> Features:
        direction_4h = "long" if df_4h["close"].iloc[-1] >= df_4h["open"].iloc[-1] else "short"
        direction_1h = "long" if df_1h["close"].iloc[-1] >= df_1h["open"].iloc[-1] else "short"
        direction_5m = "long" if df_5m["close"].iloc[-1] >= df_5m["open"].iloc[-1] else "short"
        regime = self._detect_market_regime(df_5m)
        return Features(
            direction_4h=direction_4h,
            direction_1h=direction_1h,
            direction_5m=direction_5m,
            regime=regime,
            rsi_5m=self._rsi(df_5m, 14),
            atr_5m=self._atr(df_5m, 14),
        )

    def _rsi(self, df: pd.DataFrame, n: int) -> float:
        delta = df["close"].diff()
        gain = delta.clip(lower=0).rolling(n).mean()
        loss = -delta.clip(upper=0).rolling(n).mean().replace(0, 1e-9)
        rs = gain / loss
        return float((100 - 100 / (1 + rs)).iloc[-1])

    def _atr(self, df: pd.DataFrame, n: int) -> float:
        tr = (df["high"] - df["low"]).rolling(n).mean()
        return float(tr.iloc[-1])

    def _detect_market_regime(self, df: pd.DataFrame) -> MarketRegime:
        atr = (df["high"] - df["low"]).rolling(14).mean()
        atr20 = atr.rolling(20).mean().iloc[-1]
        atr_now = atr.iloc[-1]
        if atr20 and atr_now > atr20 * 2:
            return MarketRegime.VOLATILE
        if atr20 and atr_now < atr20 * 0.3:
            return MarketRegime.LOW_VOLATILITY

        highs = df["high"].tail(5).tolist()
        lows = df["low"].tail(5).tolist()
        up = all(x < y for x, y in zip(highs, highs[1:])) and all(x < y for x, y in zip(lows, lows[1:]))
        down = all(x > y for x, y in zip(highs, highs[1:])) and all(x > y for x, y in zip(lows, lows[1:]))
        if up or down:
            return MarketRegime.TREND
        return MarketRegime.RANGE

    def _check_mtf_confluence(self, features_4h: str, features_1h: str, features_5m: str) -> bool:
        return features_4h == features_1h == features_5m
