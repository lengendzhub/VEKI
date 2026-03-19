# backend/app/models/ohlcv.py
from __future__ import annotations

import uuid
from datetime import datetime

from sqlalchemy import DateTime, Float, Index, String
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class OhlcvCache(Base):
    __tablename__ = "ohlcv_cache"
    __table_args__ = (
        Index("ix_ohlcv_symbol_tf_ts", "symbol", "timeframe", "timestamp", unique=True),
    )

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    symbol: Mapped[str] = mapped_column(String(32), nullable=False)
    timeframe: Mapped[str] = mapped_column(String(16), nullable=False)
    timestamp: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)

    open: Mapped[float] = mapped_column(Float, nullable=False)
    high: Mapped[float] = mapped_column(Float, nullable=False)
    low: Mapped[float] = mapped_column(Float, nullable=False)
    close: Mapped[float] = mapped_column(Float, nullable=False)
    volume: Mapped[float] = mapped_column(Float, nullable=False)
