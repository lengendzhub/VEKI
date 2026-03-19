# backend/tests/test_routers.py
from __future__ import annotations

import pytest


@pytest.mark.asyncio
async def test_health(async_client) -> None:
    res = await async_client.get("/health")
    assert res.status_code == 200


@pytest.mark.asyncio
async def test_metrics_requires_key(async_client) -> None:
    res = await async_client.get("/api/v1/metrics")
    assert res.status_code == 403
