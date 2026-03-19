# backend/tests/test_ai_engine.py
from __future__ import annotations

import pickle
from datetime import UTC, datetime
from pathlib import Path

import pandas as pd
import pytest

from app.schemas.analysis import MarketRegime
from app.services.ai_engine import AIEngine
from app.services.data_validator import DataValidator
from app.services.feature_engineer import FeatureEngineer
from app.services.news_filter import NewsFilter


@pytest.mark.asyncio
async def test_ai_engine_returns_optional(sample_ohlcv_df) -> None:
    engine = AIEngine(FeatureEngineer(), NewsFilter(), DataValidator())
    await engine.load_models()
    out = await engine.analyse("EURUSD", sample_ohlcv_df.resample("4h").last().dropna(), sample_ohlcv_df.resample("1h").last().dropna(), sample_ohlcv_df)
    assert out is None or out.symbol == "EURUSD"


class _NoNews:
    def is_high_impact_window(self, current_time):
        _ = current_time
        return False, None


@pytest.mark.asyncio
async def test_ai_engine_uses_trained_artifact(tmp_path: Path) -> None:
    models_dir = tmp_path / "models"
    version = "vtest"
    version_dir = models_dir / version
    version_dir.mkdir(parents=True, exist_ok=True)

    artifact = {
        "xgb": {"name": "xgb_surrogate", "weights": {"ret_3": 50.0}, "bias": 0.1},
        "lstm": {"name": "lstm_surrogate", "momentum": 0.5, "volatility": 0.1, "bias": 0.1},
        "meta": {"name": "meta_surrogate", "alpha": 0.7, "beta": 0.3, "base": 0.5},
        "feature_columns": ["ret_1", "ret_3", "ret_12", "volatility_12", "range_norm", "body_norm", "volume_z"],
    }
    with (version_dir / "artifact.pkl").open("wb") as f:
        pickle.dump(artifact, f)
    (models_dir / "ACTIVE").write_text(version, encoding="utf-8")

    idx = pd.date_range(end=datetime.now(UTC), periods=220, freq="5min")
    close = pd.Series([1.05 + (i * 0.0002) for i in range(220)], index=idx)
    df_5m = pd.DataFrame(index=idx)
    df_5m["open"] = close - 0.0001
    df_5m["high"] = close + 0.0003
    df_5m["low"] = close - 0.0003
    df_5m["close"] = close
    df_5m["volume"] = 1000 + pd.Series(range(220), index=idx)

    engine = AIEngine(FeatureEngineer(), _NoNews(), DataValidator())
    engine.settings.MODELS_DIR = str(models_dir)
    engine.registry.models_dir = models_dir
    engine.settings.CONFIDENCE_GATE = 0.0
    engine.settings.MTF_CONFLUENCE_REQUIRED = False
    engine.fe._detect_market_regime = lambda _df: MarketRegime.TREND  # type: ignore[method-assign]

    await engine.load_models()
    score = engine._score_probability(df_5m)
    out = await engine.analyse(
        "EURUSD",
        df_5m.resample("4h").last().dropna(),
        df_5m.resample("1h").last().dropna(),
        df_5m,
    )

    assert engine._active_version == version
    assert engine._artifact is not None
    assert 0.0 <= score <= 1.0
    assert out is None or out.symbol == "EURUSD"
