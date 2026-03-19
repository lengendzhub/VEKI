# backend/tests/conftest.py
from __future__ import annotations

from datetime import UTC, datetime, timedelta

import fakeredis.aioredis
import pandas as pd
import pytest
from httpx import AsyncClient

from app.main import app
from app.schemas.proposal import TradeProposal


@pytest.fixture
async def async_client():
    async with AsyncClient(app=app, base_url="http://test") as client:
        yield client


@pytest.fixture
def mock_redis():
    return fakeredis.aioredis.FakeRedis(decode_responses=True)


@pytest.fixture
def sample_ohlcv_df() -> pd.DataFrame:
    idx = pd.date_range(end=datetime.now(UTC), periods=500, freq="5min")
    df = pd.DataFrame(index=idx)
    df["open"] = 1.0800
    df["high"] = 1.0808
    df["low"] = 1.0792
    df["close"] = 1.0802
    df["volume"] = 1000
    return df


@pytest.fixture
def sample_proposal() -> TradeProposal:
    return TradeProposal(
        symbol="EURUSD",
        timeframe="M5",
        direction="long",
        confidence=0.9,
        entry_price=1.08,
        stop_loss=1.079,
        take_profit=1.082,
        atr=0.001,
        regime="trend",
        explanation="test",
    )
