# backend/app/models/trade.py
from __future__ import annotations

import enum
import uuid
from datetime import datetime

from sqlalchemy import DateTime, Enum, Float, ForeignKey, Index, Integer, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class TradeStatus(str, enum.Enum):
    OPEN = "open"
    CLOSED = "closed"
    REJECTED = "rejected"


class TradeDirection(str, enum.Enum):
    LONG = "long"
    SHORT = "short"


class Trade(Base):
    __tablename__ = "trades"
    __table_args__ = (
        Index("ix_trades_symbol_status", "symbol", "status"),
        Index("ix_trades_created_at", "created_at"),
    )

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    proposal_id: Mapped[str | None] = mapped_column(String(36), ForeignKey("proposals.id"), nullable=True)
    user_id: Mapped[str | None] = mapped_column(String(36), ForeignKey("users.id"), nullable=True)

    symbol: Mapped[str] = mapped_column(String(32), nullable=False)
    timeframe: Mapped[str] = mapped_column(String(16), nullable=False)
    direction: Mapped[TradeDirection] = mapped_column(Enum(TradeDirection), nullable=False)
    status: Mapped[TradeStatus] = mapped_column(Enum(TradeStatus), default=TradeStatus.OPEN, nullable=False)

    lot_size: Mapped[float] = mapped_column(Float, nullable=False)
    entry_price: Mapped[float] = mapped_column(Float, nullable=False)
    stop_loss: Mapped[float] = mapped_column(Float, nullable=False)
    take_profit: Mapped[float] = mapped_column(Float, nullable=False)
    close_price: Mapped[float | None] = mapped_column(Float, nullable=True)
    pnl: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    rr: Mapped[float | None] = mapped_column(Float, nullable=True)
    broker_ticket: Mapped[int | None] = mapped_column(Integer, nullable=True)
    note: Mapped[str | None] = mapped_column(Text, nullable=True)

    opened_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=func.now(), nullable=False)
    closed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=func.now(), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=func.now(), onupdate=func.now())

    proposal = relationship("Proposal", back_populates="trade")
    user = relationship("User", back_populates="trades")
