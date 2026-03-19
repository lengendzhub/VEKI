# backend/app/broker/binance_broker.py
from __future__ import annotations

import pandas as pd

from app.broker.base import BaseBroker
from app.schemas.proposal import TradeProposal


class BinanceBroker(BaseBroker):
    """
    Future-ready Binance Futures broker adapter.

    TODO for production implementation:
    1. Authenticate using API key/secret with HMAC SHA256 signing.
    2. Implement exchange info + symbol precision cache.
    3. Add isolated/cross margin configuration and leverage setup.
    4. Support MARKET, LIMIT, STOP_MARKET, TAKE_PROFIT_MARKET orders.
    5. Add websocket user stream for fills and position updates.
    6. Normalize Binance payloads into BaseBroker contract dictionaries.
    7. Implement robust retry and timestamp drift correction.
    8. Enforce per-symbol risk and minNotional constraints.
    """

    async def connect(self) -> bool:
        raise NotImplementedError("Binance Futures integration is not yet implemented.")

    async def disconnect(self) -> None:
        raise NotImplementedError("Binance Futures integration is not yet implemented.")

    async def execute(self, proposal: TradeProposal) -> dict:
        raise NotImplementedError("Implement Binance order execution with signed REST endpoint.")

    async def modify_sl_tp(self, ticket: int, sl: float, tp: float) -> bool:
        raise NotImplementedError("Implement SL/TP updates via conditional order management.")

    async def close_position(self, ticket: int) -> bool:
        raise NotImplementedError("Implement position close by reduce-only market order.")

    async def get_positions(self) -> list[dict]:
        raise NotImplementedError("Implement position risk endpoint mapping.")

    async def get_account_info(self) -> dict:
        raise NotImplementedError("Implement futures account endpoint mapping.")

    async def get_ohlcv(self, symbol: str, timeframe: str, count: int) -> pd.DataFrame:
        raise NotImplementedError("Implement klines pull and DataFrame normalization.")

    def is_connected(self) -> bool:
        return False

    @property
    def broker_name(self) -> str:
        return "binance_futures"
