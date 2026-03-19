# backend/app/services/audit_service.py
from __future__ import annotations

from datetime import datetime

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.audit_log import AuditLog


class AuditService:
    """Insert-only audit trail writer."""

    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    async def log(
        self,
        actor: str,
        action: str,
        entity_type: str,
        entity_id: str,
        payload: dict,
        ip_address: str | None = None,
    ) -> None:
        row = AuditLog(
            actor=actor,
            action=action,
            entity_type=entity_type,
            entity_id=entity_id,
            payload=payload,
            ip_address=ip_address,
        )
        self.db.add(row)
        await self.db.commit()

    async def get_audit_trail(
        self,
        entity_type: str | None = None,
        actor: str | None = None,
        from_dt: datetime | None = None,
        to_dt: datetime | None = None,
        limit: int = 100,
    ) -> list[AuditLog]:
        stmt = select(AuditLog).order_by(AuditLog.timestamp.desc()).limit(limit)
        if entity_type:
            stmt = stmt.where(AuditLog.entity_type == entity_type)
        if actor:
            stmt = stmt.where(AuditLog.actor == actor)
        if from_dt:
            stmt = stmt.where(AuditLog.timestamp >= from_dt)
        if to_dt:
            stmt = stmt.where(AuditLog.timestamp <= to_dt)
        result = await self.db.execute(stmt)
        return list(result.scalars().all())
