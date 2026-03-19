# backend/app/routers/strategy.py
from __future__ import annotations

import asyncio

from fastapi import APIRouter, Depends, HTTPException, Request

from app.core.auth import get_current_user
from app.services.audit_service import AuditService

router = APIRouter(prefix="/strategy", tags=["strategy"])


@router.post("/kill-switch")
async def activate_kill_switch(payload: dict, request: Request, user=Depends(get_current_user), db=Depends(lambda: None), kill_switch=Depends(lambda: None), broker=Depends(lambda: None)) -> dict:
    if user.role != "admin":
        raise HTTPException(status_code=403, detail="Admin only")
    if kill_switch is None or broker is None:
        raise HTTPException(status_code=503, detail="Kill switch unavailable")
    data = await kill_switch.activate(reason=payload.get("reason", "manual"), actor=user.username, broker=broker)
    if db is not None:
        asyncio.create_task(AuditService(db).log(actor=user.id, action="risk.kill_switch", entity_type="system", entity_id="kill_switch", payload=data, ip_address=request.client.host if request.client else None))
    return data


@router.post("/kill-switch/reset")
async def reset_kill_switch(user=Depends(get_current_user), db=Depends(lambda: None), kill_switch=Depends(lambda: None)) -> dict:
    if user.role != "admin":
        raise HTTPException(status_code=403, detail="Admin only")
    if kill_switch is None:
        raise HTTPException(status_code=503, detail="Kill switch unavailable")
    data = await kill_switch.reset(actor=user.username)
    if db is not None:
        asyncio.create_task(AuditService(db).log(actor=user.id, action="risk.kill_switch.reset", entity_type="system", entity_id="kill_switch", payload=data))
    return data


@router.get("/kill-switch/status")
async def kill_switch_status(user=Depends(get_current_user), kill_switch=Depends(lambda: None)) -> dict:
    _ = user
    if kill_switch is None:
        return {"active": False}
    return await kill_switch.get_status()


@router.get("/risk-scaling")
async def risk_scaling(user=Depends(get_current_user), risk_manager=Depends(lambda: None)) -> dict:
    _ = user
    if risk_manager is None:
        return {"streak": 0, "effective_risk_pct": 0.0}
    session_mult = risk_manager.get_session_risk_multiplier()
    effective = risk_manager.calculate_dynamic_risk(0.01, 100000, 0, session_mult)
    return {
        "streak": 0,
        "streak_multiplier": 1.0,
        "session": "auto",
        "session_multiplier": session_mult,
        "drawdown_pct": 0.0,
        "drawdown_multiplier": 1.0,
        "effective_risk_pct": effective,
    }
