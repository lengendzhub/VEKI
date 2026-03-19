# backend/app/models/proposal.py
from __future__ import annotations

import enum
import uuid
from datetime import datetime

from sqlalchemy import DateTime, Enum, Float, Index, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class ProposalStatus(str, enum.Enum):
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"
    EXPIRED = "expired"


class ProposalDirection(str, enum.Enum):
    LONG = "long"
    SHORT = "short"


class Proposal(Base):
    __tablename__ = "proposals"
    __table_args__ = (
        Index("ix_proposals_symbol_time", "symbol", "created_at"),
        Index("ix_proposals_status", "status"),
    )

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    symbol: Mapped[str] = mapped_column(String(32), nullable=False)
    timeframe: Mapped[str] = mapped_column(String(16), nullable=False)
    direction: Mapped[ProposalDirection] = mapped_column(Enum(ProposalDirection), nullable=False)
    confidence: Mapped[float] = mapped_column(Float, nullable=False)
    entry_price: Mapped[float] = mapped_column(Float, nullable=False)
    stop_loss: Mapped[float] = mapped_column(Float, nullable=False)
    take_profit: Mapped[float] = mapped_column(Float, nullable=False)
    regime: Mapped[str] = mapped_column(String(32), default="range", nullable=False)
    explanation: Mapped[str] = mapped_column(Text, nullable=False)
    status: Mapped[ProposalStatus] = mapped_column(Enum(ProposalStatus), default=ProposalStatus.PENDING, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=func.now(), nullable=False)

    trade = relationship("Trade", back_populates="proposal", uselist=False)
