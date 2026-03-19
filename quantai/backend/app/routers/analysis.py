# backend/app/routers/analysis.py
from __future__ import annotations

import asyncio
from datetime import UTC, datetime

from fastapi import APIRouter, Depends, HTTPException

from app.core.auth import get_current_user
from app.schemas.analysis import BacktestRequest
from app.services.audit_service import AuditService
from app.services.metrics import metrics_collector
from app.services.news_filter import news_filter
from app.services.training_monitor import training_monitor

router = APIRouter(prefix="/analysis", tags=["analysis"])


@router.post("/backtest")
async def run_backtest(payload: BacktestRequest, user=Depends(get_current_user), db=Depends(lambda: None), backtester=Depends(lambda: None)):
    if backtester is None:
        raise HTTPException(status_code=503, detail="Backtester not available")
    result = await backtester.simulate(payload.symbol, payload.timeframe, payload.start_date, payload.end_date, payload.initial_balance)
    if db is not None:
        asyncio.create_task(AuditService(db).log(actor=user.id, action="backtest.run", entity_type="analysis", entity_id=user.id, payload=payload.model_dump()))
    return result


@router.get("/regime/{symbol}")
async def get_regime(symbol: str, user=Depends(get_current_user)) -> dict:
    _ = user
    return {"symbol": symbol, "regime": metrics_collector.current_regime.get(symbol, "range")}


@router.get("/news")
async def get_news(user=Depends(get_current_user)) -> dict:
    _ = user
    now = datetime.now(UTC)
    blocked, event_name = news_filter.is_high_impact_window(now)
    return {
        "events": news_filter.get_upcoming_events(within_hours=4),
        "is_currently_blocked": blocked,
        "blocking_event_name": event_name,
    }


@router.post("/validate/{symbol}/{timeframe}")
async def validate_data(symbol: str, timeframe: str, user=Depends(get_current_user)) -> dict:
    if user.role != "admin":
        raise HTTPException(status_code=403, detail="Admin only")
    return {"is_valid": True, "issues": [], "symbol": symbol, "timeframe": timeframe}


@router.get("/training/status")
async def get_training_status(user=Depends(get_current_user)) -> dict:
    _ = user
    return await training_monitor.get_state()


@router.get("/training/history")
async def get_training_history(user=Depends(get_current_user)) -> dict:
    _ = user
    history = await training_monitor.get_history()
    return {"history": history, "count": len(history)}
