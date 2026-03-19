# backend/app/services/data_validator.py
from __future__ import annotations

from dataclasses import dataclass

import numpy as np
import pandas as pd


class DataQualityError(Exception):
    pass


@dataclass
class ValidationResult:
    is_valid: bool
    issues: list[str]
    clean_df: pd.DataFrame
    missing_pct: float
    repaired_count: int


class DataValidator:
    """OHLCV data quality guard called before feature engineering."""

    def validate(self, df: pd.DataFrame, symbol: str, timeframe: str) -> ValidationResult:
        issues: list[str] = []
        repaired_count = 0

        if df.empty or len(df) < 100:
            raise DataQualityError(f"Insufficient candles for {symbol}/{timeframe}. Need >= 100 rows.")

        clean = df.copy()
        if not clean.index.is_monotonic_increasing:
            issues.append("non_monotonic_index")
            clean = clean.sort_index()

        duplicate_count = int(clean.index.duplicated().sum())
        if duplicate_count:
            issues.append("duplicate_timestamps")
            clean = clean[~clean.index.duplicated(keep="last")]
            repaired_count += duplicate_count

        missing_pct = float(clean.isna().mean().max() * 100)
        if missing_pct > 5:
            issues.append("too_many_nans")

        invalid_high_low = (clean["high"] < clean["low"]).sum()
        if int(invalid_high_low) > 0:
            issues.append("inverted_bars")

        out_of_range = ((clean["open"] > clean["high"]) | (clean["open"] < clean["low"]) | (clean["close"] > clean["high"]) | (clean["close"] < clean["low"])).sum()
        if int(out_of_range) > 0:
            issues.append("open_close_outside_range")

        clean = clean.replace([np.inf, -np.inf], np.nan).ffill().bfill()

        rolling_mean = clean["close"].rolling(50, min_periods=10).mean()
        rolling_std = clean["close"].rolling(50, min_periods=10).std().replace(0, np.nan)
        z = ((clean["close"] - rolling_mean) / rolling_std).abs().fillna(0)
        outliers = int((z > 5).sum())
        if outliers > 0:
            issues.append("extreme_outliers")

        if len(issues) and (len(issues) / max(1, len(clean)) * 100 > 10):
            raise DataQualityError(f"Too many data issues for {symbol}/{timeframe}: {issues}")

        return ValidationResult(is_valid=True, issues=issues, clean_df=clean, missing_pct=missing_pct, repaired_count=repaired_count)
