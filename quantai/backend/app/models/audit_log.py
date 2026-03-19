# backend/app/models/audit_log.py
from __future__ import annotations

import uuid
from datetime import datetime

from sqlalchemy import DateTime, Index, JSON, String, func
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class AuditLog(Base):
    """Append-only audit trail table for compliance."""

    __tablename__ = "audit_logs"
    __table_args__ = (
        Index("ix_audit_actor_ts", "actor", "timestamp"),
        Index("ix_audit_entity", "entity_type", "entity_id"),
    )

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    timestamp: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=func.now(), nullable=False)
    actor: Mapped[str] = mapped_column(String(128), nullable=False)
    action: Mapped[str] = mapped_column(String(128), nullable=False)
    entity_type: Mapped[str] = mapped_column(String(64), nullable=False)
    entity_id: Mapped[str] = mapped_column(String(36), nullable=False)
    payload: Mapped[dict] = mapped_column(JSON, nullable=False, default=dict)
    ip_address: Mapped[str | None] = mapped_column(String(64), nullable=True)
