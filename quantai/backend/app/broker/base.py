# backend/app/broker/base.py
from __future__ import annotations

from abc import ABC, abstractmethod

import pandas as pd

from app.schemas.proposal import TradeProposal


class BaseBroker(ABC):
    @abstractmethod
    async def connect(self) -> bool:
        raise NotImplementedError

    @abstractmethod
    async def disconnect(self) -> None:
        raise NotImplementedError

    @abstractmethod
    async def execute(self, proposal: TradeProposal) -> dict:
        raise NotImplementedError

    @abstractmethod
    async def modify_sl_tp(self, ticket: int, sl: float, tp: float) -> bool:
        raise NotImplementedError

    @abstractmethod
    async def close_position(self, ticket: int) -> bool:
        raise NotImplementedError

    @abstractmethod
    async def get_positions(self) -> list[dict]:
        raise NotImplementedError

    @abstractmethod
    async def get_account_info(self) -> dict:
        raise NotImplementedError

    @abstractmethod
    async def get_ohlcv(self, symbol: str, timeframe: str, count: int) -> pd.DataFrame:
        raise NotImplementedError

    @abstractmethod
    def is_connected(self) -> bool:
        raise NotImplementedError

    @property
    @abstractmethod
    def broker_name(self) -> str:
        raise NotImplementedError
