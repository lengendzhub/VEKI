# backend/tests/test_mt5_bridge.py
from __future__ import annotations

import pytest

from app.services.mt5_bridge import MT5Bridge


@pytest.mark.asyncio
async def test_mt5_mock_connect() -> None:
    bridge = MT5Bridge(mock_mode=True)
    assert await bridge.connect()
    info = await bridge.get_account_info()
    assert info["balance"] == 100000.0
