# backend/app/services/mt5_bridge.py
from __future__ import annotations

from app.broker.mt5_broker import MT5Broker


class MT5Bridge:
    """Backward compatible shim that delegates to MT5Broker."""

    def __init__(self, mock_mode: bool = True) -> None:
        self.broker = MT5Broker(mock_mode=mock_mode)

    async def connect(self) -> bool:
        return await self.broker.connect()

    async def disconnect(self) -> None:
        await self.broker.disconnect()

    async def execute(self, proposal):
        return await self.broker.execute(proposal)

    async def modify_sl_tp(self, ticket: int, sl: float, tp: float) -> bool:
        return await self.broker.modify_sl_tp(ticket, sl, tp)

    async def close_position(self, ticket: int) -> bool:
        return await self.broker.close_position(ticket)

    async def get_positions(self):
        return await self.broker.get_positions()

    async def get_account_info(self):
        return await self.broker.get_account_info()

    async def get_ohlcv(self, symbol: str, timeframe: str, count: int):
        return await self.broker.get_ohlcv(symbol, timeframe, count)
