# backend/app/models/user.py
from __future__ import annotations

import uuid
from datetime import datetime

from sqlalchemy import DateTime, Index, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class User(Base):
    __tablename__ = "users"
    __table_args__ = (Index("ix_users_username", "username", unique=True),)

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    username: Mapped[str] = mapped_column(String(64), nullable=False)
    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)
    role: Mapped[str] = mapped_column(String(16), default="user", nullable=False)
    telegram_chat_id: Mapped[str | None] = mapped_column(String(64), nullable=True)
    device_token: Mapped[str | None] = mapped_column(String(512), nullable=True)
    device_platform: Mapped[str | None] = mapped_column(String(16), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=func.now(), nullable=False)

    trades = relationship("Trade", back_populates="user")
