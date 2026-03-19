# backend/tests/test_feature_engineer.py
from __future__ import annotations

import pandas as pd

from app.schemas.analysis import MarketRegime
from app.services.feature_engineer import FeatureEngineer


def _df(values: list[float]) -> pd.DataFrame:
    n = len(values)
    idx = pd.date_range("2025-01-01", periods=n, freq="5min")
    return pd.DataFrame({"open": values, "high": [v + 0.001 for v in values], "low": [v - 0.001 for v in values], "close": values, "volume": [1000] * n}, index=idx)


def test_regime_trend() -> None:
    fe = FeatureEngineer()
    df = _df([1 + i * 0.001 for i in range(120)])
    regime = fe._detect_market_regime(df)
    assert regime in {MarketRegime.TREND, MarketRegime.VOLATILE}


def test_mtf_confluence_true() -> None:
    fe = FeatureEngineer()
    assert fe._check_mtf_confluence("long", "long", "long")


def test_mtf_confluence_false() -> None:
    fe = FeatureEngineer()
    assert not fe._check_mtf_confluence("long", "short", "long")
