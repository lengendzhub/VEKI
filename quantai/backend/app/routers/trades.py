# backend/app/routers/trades.py
from __future__ import annotations

import asyncio

from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.auth import get_current_user
from app.database import get_db
from app.models.trade import Trade
from app.schemas.trade import TradeResponse
from app.services.audit_service import AuditService

router = APIRouter(prefix="/trades", tags=["trades"])


@router.get("", response_model=list[TradeResponse])
async def list_trades(user=Depends(get_current_user), db: AsyncSession = Depends(get_db)) -> list[Trade]:
    _ = user
    result = await db.execute(select(Trade).order_by(Trade.created_at.desc()).limit(100))
    return list(result.scalars().all())


@router.post("/{trade_id}/close")
async def close_trade(trade_id: str, request: Request, user=Depends(get_current_user), db: AsyncSession = Depends(get_db), broker=Depends(lambda: None)) -> dict:
    result = await db.execute(select(Trade).where(Trade.id == trade_id))
    trade = result.scalar_one_or_none()
    if trade is None:
        raise HTTPException(status_code=404, detail="Trade not found")

    if broker is not None and trade.broker_ticket:
        await broker.close_position(trade.broker_ticket)

    trade.status = "closed"
    await db.commit()

    asyncio.create_task(AuditService(db).log(actor=user.id, action="trade.close", entity_type="trade", entity_id=trade.id, payload={"status": trade.status}, ip_address=request.client.host if request.client else None))
    return {"closed": True, "trade_id": trade.id}
