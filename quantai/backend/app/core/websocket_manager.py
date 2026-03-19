# backend/app/core/websocket_manager.py
from __future__ import annotations

import json
import logging
from datetime import UTC, datetime

from fastapi import WebSocket
from redis.asyncio import Redis

logger = logging.getLogger(__name__)


class ConnectionManager:
    def __init__(self, redis_client: Redis) -> None:
        self.active: dict[str, list[WebSocket]] = {}
        self.redis = redis_client

    async def connect(self, user_id: str, websocket: WebSocket) -> None:
        await websocket.accept()
        self.active.setdefault(user_id, []).append(websocket)

    def disconnect(self, user_id: str, websocket: WebSocket) -> None:
        items = self.active.get(user_id, [])
        if websocket in items:
            items.remove(websocket)
        if not items and user_id in self.active:
            del self.active[user_id]

    async def send_personal(self, user_id: str, payload: dict) -> None:
        sockets = self.active.get(user_id, [])
        if not sockets:
            key = f"ws_queue:{user_id}"
            msg = json.dumps({**payload, "timestamp": datetime.now(UTC).isoformat()})
            await self.redis.lpush(key, msg)
            await self.redis.ltrim(key, 0, 99)
            await self.redis.expire(key, 300)
            return
        for ws in sockets:
            await ws.send_json(payload)

    async def broadcast(self, payload: dict) -> None:
        stale: list[tuple[str, WebSocket]] = []
        for user_id, sockets in self.active.items():
            for ws in sockets:
                try:
                    await ws.send_json(payload)
                except Exception:
                    stale.append((user_id, ws))
        for user_id, ws in stale:
            self.disconnect(user_id=user_id, websocket=ws)

    async def broadcast_training_update(self, state: dict) -> None:
        await self.broadcast({"type": "training_update", "data": state})

    async def replay(self, user_id: str, since_iso: str) -> list[dict]:
        items = await self.redis.lrange(f"ws_queue:{user_id}", 0, 99)
        try:
            since = datetime.fromisoformat(since_iso)
        except Exception:
            logger.warning("websocket.invalid_replay_since", extra={"user_id": user_id, "since": since_iso})
            since = datetime.now(UTC)
        filtered = []
        for raw in reversed(items):
            item = json.loads(raw)
            ts = datetime.fromisoformat(item["timestamp"])
            if ts >= since:
                filtered.append(item)
        return filtered
