# backend/app/schemas/proposal.py
from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, Field


class TradeProposal(BaseModel):
    id: str | None = None
    symbol: str
    timeframe: str
    direction: str
    confidence: float = Field(ge=0.0, le=1.0)
    entry_price: float = Field(gt=0)
    stop_loss: float = Field(gt=0)
    take_profit: float = Field(gt=0)
    atr: float = Field(gt=0)
    regime: str
    explanation: str


class ProposalResponse(BaseModel):
    id: str
    symbol: str
    timeframe: str
    direction: str
    confidence: float
    status: str
    created_at: datetime

    class Config:
        from_attributes = True
