# backend/app/routers/account.py
from __future__ import annotations

from fastapi import APIRouter, Depends

from app.core.auth import get_current_user

router = APIRouter(prefix="/account", tags=["account"])


@router.get("/info")
async def account_info(user=Depends(get_current_user)) -> dict:
    return {
        "id": user.id,
        "username": user.username,
        "role": user.role,
        "device_platform": user.device_platform,
        "has_device_token": bool(user.device_token),
    }
