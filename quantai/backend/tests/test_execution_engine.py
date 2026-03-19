# backend/tests/test_execution_engine.py
from __future__ import annotations

import pytest

from app.broker.mt5_broker import MT5Broker
from app.services.execution_engine import ExecutionEngine


@pytest.mark.asyncio
async def test_execution_result(sample_proposal) -> None:
    broker = MT5Broker(mock_mode=True)
    await broker.connect()
    engine = ExecutionEngine(kill_switch_checker=lambda: _false())
    result = await engine.execute_trade(sample_proposal, broker)
    assert result.filled_price > 0


async def _false() -> bool:
    return False
