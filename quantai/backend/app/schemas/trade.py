# backend/app/schemas/trade.py
from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, Field


class TradeResponse(BaseModel):
    id: str
    symbol: str
    timeframe: str
    direction: str
    status: str
    lot_size: float
    entry_price: float
    stop_loss: float
    take_profit: float
    close_price: float | None = None
    pnl: float
    rr: float | None = None
    broker_ticket: int | None = None
    opened_at: datetime
    closed_at: datetime | None = None

    class Config:
        from_attributes = True


class TradeCloseRequest(BaseModel):
    trade_id: str = Field(min_length=36, max_length=36)
    close_price: float = Field(gt=0)
    note: str | None = None
