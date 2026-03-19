# backend/app/broker/mt5_broker.py
from __future__ import annotations

import random
from datetime import UTC, datetime

import pandas as pd

from app.broker.base import BaseBroker
from app.schemas.proposal import TradeProposal


class MT5Broker(BaseBroker):
    def __init__(self, mock_mode: bool = True) -> None:
        self.mock_mode = mock_mode
        self._connected = False
        self._positions: list[dict] = []
        self._ticket = 1000

    async def connect(self) -> bool:
        self._connected = True
        return True

    async def disconnect(self) -> None:
        self._connected = False

    async def execute(self, proposal: TradeProposal) -> dict:
        self._ticket += 1
        slip = random.uniform(-0.0001, 0.0001)
        filled = proposal.entry_price + slip
        row = {
            "ticket": self._ticket,
            "symbol": proposal.symbol,
            "direction": proposal.direction,
            "price": filled,
            "sl": proposal.stop_loss,
            "tp": proposal.take_profit,
            "opened_at": datetime.now(UTC).isoformat(),
        }
        self._positions.append(row)
        return {"ticket": self._ticket, "filled_price": filled}

    async def modify_sl_tp(self, ticket: int, sl: float, tp: float) -> bool:
        for p in self._positions:
            if int(p["ticket"]) == ticket:
                p["sl"] = sl
                p["tp"] = tp
                return True
        return False

    async def close_position(self, ticket: int) -> bool:
        before = len(self._positions)
        self._positions = [p for p in self._positions if int(p.get("ticket", 0)) != ticket]
        return len(self._positions) < before

    async def get_positions(self) -> list[dict]:
        return list(self._positions)

    async def get_account_info(self) -> dict:
        return {"balance": 100000.0, "equity": 100000.0 - len(self._positions) * 10, "leverage": 100}

    async def get_ohlcv(self, symbol: str, timeframe: str, count: int) -> pd.DataFrame:
        _ = symbol, timeframe
        idx = pd.date_range(end=datetime.now(UTC), periods=count, freq="5min")
        base = 1.08
        df = pd.DataFrame(index=idx)
        df["open"] = base
        df["high"] = base + 0.0007
        df["low"] = base - 0.0007
        df["close"] = base + 0.0001
        df["volume"] = 1200
        return df

    def is_connected(self) -> bool:
        return self._connected

    @property
    def broker_name(self) -> str:
        return "mt5_mock" if self.mock_mode else "mt5"

    def _calc_lot(self, entry: float, sl: float, symbol: str) -> float:
        _ = symbol
        distance = max(abs(entry - sl), 0.0001)
        risk_dollars = 1000
        lot = min(10.0, max(0.01, risk_dollars / (distance * 100000)))
        return round(lot, 2)
