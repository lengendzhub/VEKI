# backend/tests/test_backtester.py
from __future__ import annotations

from datetime import UTC, datetime, timedelta

import pytest

from app.services.ai_engine import AIEngine
from app.services.backtester import Backtester
from app.services.data_validator import DataValidator
from app.services.feature_engineer import FeatureEngineer
from app.services.news_filter import NewsFilter


@pytest.mark.asyncio
async def test_backtester_returns_result() -> None:
    ai = AIEngine(FeatureEngineer(), NewsFilter(), DataValidator())
    await ai.load_models()
    bt = Backtester(ai, FeatureEngineer())
    end = datetime.now(UTC)
    start = end - timedelta(days=2)
    result = await bt.simulate("EURUSD", "M5", start, end)
    assert result.symbol == "EURUSD"
    assert result.equity_curve[0] == result.initial_balance
