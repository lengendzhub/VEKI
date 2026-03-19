# backend/app/schemas/auth.py
from __future__ import annotations

from pydantic import BaseModel, Field


class LoginRequest(BaseModel):
    username: str = Field(min_length=3, max_length=64)
    password: str = Field(min_length=6, max_length=128)


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


class TokenPayload(BaseModel):
    sub: str
    role: str


class DeviceTokenRequest(BaseModel):
    token: str = Field(min_length=10, max_length=512)
    platform: str = Field(pattern="^(ios|android)$")
