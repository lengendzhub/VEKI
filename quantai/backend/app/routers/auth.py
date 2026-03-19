# backend/app/routers/auth.py
from __future__ import annotations

import asyncio

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.auth import authenticate_user, create_access_token, get_current_user
from app.database import get_db
from app.schemas.auth import DeviceTokenRequest, LoginRequest, TokenResponse
from app.services.audit_service import AuditService

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/login", response_model=TokenResponse)
async def login(payload: LoginRequest, db: AsyncSession = Depends(get_db)) -> TokenResponse:
    user = await authenticate_user(payload.username, payload.password, db)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    token = create_access_token(subject=user.username, role=user.role)
    asyncio.create_task(AuditService(db).log(actor=user.id, action="auth.login", entity_type="user", entity_id=user.id, payload={"username": user.username}))
    return TokenResponse(access_token=token)


@router.post("/device-token")
async def register_device_token(payload: DeviceTokenRequest, user=Depends(get_current_user), db: AsyncSession = Depends(get_db)) -> dict:
    user.device_token = payload.token
    user.device_platform = payload.platform
    await db.commit()
    asyncio.create_task(AuditService(db).log(actor=user.id, action="auth.device_token", entity_type="user", entity_id=user.id, payload={"platform": payload.platform}))
    return {"registered": True}
