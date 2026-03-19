# backend/app/models/performance.py
from __future__ import annotations

import uuid
from datetime import date, datetime

from sqlalchemy import Date, DateTime, Float, Index, Integer, JSON, String, func
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class DailyPerformance(Base):
    __tablename__ = "daily_performance"
    __table_args__ = (Index("ix_daily_performance_date", "date", unique=True),)

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    date: Mapped[date] = mapped_column(Date, nullable=False)
    pnl: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    drawdown_pct: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    win_streak: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    loss_streak: Mapped[int] = mapped_column(Integer, default=0, nullable=False)


class ModelVersion(Base):
    __tablename__ = "model_versions"
    __table_args__ = (Index("ix_model_versions_created_at", "created_at"),)

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    version: Mapped[str] = mapped_column(String(64), nullable=False, unique=True)
    metrics: Mapped[dict] = mapped_column(JSON, nullable=False, default=dict)
    is_active: Mapped[bool] = mapped_column(default=False, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=func.now(), nullable=False)


class FeatureLabel(Base):
    __tablename__ = "feature_labels"
    __table_args__ = (Index("ix_feature_labels_symbol_ts", "symbol", "timestamp"),)

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    symbol: Mapped[str] = mapped_column(String(32), nullable=False)
    timeframe: Mapped[str] = mapped_column(String(16), nullable=False)
    timestamp: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    features: Mapped[dict] = mapped_column(JSON, nullable=False)
    label: Mapped[int] = mapped_column(Integer, nullable=False)
