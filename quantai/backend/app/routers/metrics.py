# backend/app/routers/metrics.py
from __future__ import annotations

from fastapi import APIRouter, Depends, Header, HTTPException

from app.config import get_settings
from app.services.metrics import metrics_collector

router = APIRouter(prefix="/metrics", tags=["metrics"])


@router.get("")
async def metrics(x_internal_key: str | None = Header(default=None)) -> dict:
    settings = get_settings()
    if x_internal_key != settings.INTERNAL_API_KEY:
        raise HTTPException(status_code=403, detail="Forbidden")
    return metrics_collector.get_snapshot()


@router.get("/history")
async def metrics_history(hours: int = 24, x_internal_key: str | None = Header(default=None)) -> dict:
    settings = get_settings()
    if x_internal_key != settings.INTERNAL_API_KEY:
        raise HTTPException(status_code=403, detail="Forbidden")
    return {"hours": hours, "items": [metrics_collector.get_snapshot()]}
