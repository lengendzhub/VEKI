from __future__ import annotations

from datetime import UTC, datetime, timedelta

import pandas as pd
import pytest

from app.services.dukascopy_collector import DukascopyCollector


@pytest.mark.asyncio
async def test_convert_to_ohlc_fills_missing_candles() -> None:
    collector = DukascopyCollector(db_session=None)  # type: ignore[arg-type]
    try:
        df = pd.DataFrame(
            {
                "timestamp": [
                    datetime(2025, 1, 1, 0, 0, tzinfo=UTC),
                    datetime(2025, 1, 1, 0, 2, tzinfo=UTC),
                ],
                "price": [1.1000, 1.1002],
                "volume": [10.0, 12.0],
            }
        )

        out = await collector.convert_to_ohlc(df, timeframe="1m")
        assert len(out) == 3
        assert out["timestamp"].is_monotonic_increasing
        assert out[["open", "high", "low", "close", "volume"]].isna().sum().sum() == 0
    finally:
        await collector.close()


@pytest.mark.asyncio
async def test_clean_data_removes_invalid_and_spike_rows() -> None:
    collector = DukascopyCollector(db_session=None)  # type: ignore[arg-type]
    try:
        df = pd.DataFrame(
            {
                "timestamp": [
                    datetime(2025, 1, 1, 0, 0, tzinfo=UTC),
                    datetime(2025, 1, 1, 0, 1, tzinfo=UTC),
                    datetime(2025, 1, 1, 0, 2, tzinfo=UTC),
                ],
                "open": [1.0, 1.2, 1.01],
                "high": [1.01, 1.10, 1.02],
                "low": [0.99, 1.15, 1.0],
                "close": [1.0, 1.2, 1.01],
                "volume": [10, 10, 10],
            }
        )

        out = await collector.clean_data(df)

        assert len(out) == 2
        assert out["close"].max() < 1.1
    finally:
        await collector.close()


@pytest.mark.asyncio
async def test_clean_data_drops_non_positive_prices() -> None:
    collector = DukascopyCollector(db_session=None)  # type: ignore[arg-type]
    try:
        df = pd.DataFrame(
            {
                "timestamp": [
                    datetime(2025, 1, 1, 0, 0, tzinfo=UTC),
                    datetime(2025, 1, 1, 0, 1, tzinfo=UTC),
                ],
                "price": [1.0, -1.0],
                "bid": [1.0, -1.0],
                "ask": [1.0, -1.0],
                "volume": [1.0, 1.0],
            }
        )

        out = await collector.clean_data(df)
        assert len(out) == 1
    finally:
        await collector.close()
