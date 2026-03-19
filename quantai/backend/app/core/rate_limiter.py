# backend/app/core/rate_limiter.py
from __future__ import annotations

import time

from fastapi import HTTPException, Request
from redis.asyncio import Redis

from app.config import get_settings


class RateLimiter:
    def __init__(self, redis_client: Redis) -> None:
        self.redis = redis_client
        self.settings = get_settings()

    async def check(self, request: Request, user_id: str | None = None) -> None:
        path = request.url.path
        if path in {"/health", "/api/v1/metrics"}:
            return

        now = time.time()
        window = 60
        limit = self.settings.RATE_LIMIT_REQUESTS_PER_MINUTE
        key = f"rl:ip:{request.client.host if request.client else 'unknown'}"
        if user_id:
            limit *= 2
            key = f"rl:user:{user_id}"

        p = self.redis.pipeline()
        await p.zremrangebyscore(key, 0, now - window)
        await p.zadd(key, {str(now): now})
        await p.zcard(key)
        await p.expire(key, window)
        _, _, count, _ = await p.execute()

        if int(count) > limit + self.settings.RATE_LIMIT_BURST:
            retry_after = 5
            raise HTTPException(status_code=429, detail={"detail": "Rate limit exceeded", "retry_after": retry_after}, headers={"Retry-After": str(retry_after)})
