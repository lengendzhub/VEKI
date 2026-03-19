# backend/app/services/kill_switch.py
from __future__ import annotations

from datetime import UTC, datetime

from redis.asyncio import Redis

from app.broker.base import BaseBroker
from app.services.logger import quant_logger


class KillSwitch:
    def __init__(self, redis_client: Redis) -> None:
        self.redis = redis_client

    async def activate(self, reason: str, actor: str, broker: BaseBroker) -> dict:
        await self.redis.set("kill_switch:active", "1")
        await self.redis.set("kill_switch:reason", reason)
        await self.redis.set("kill_switch:activated_at", datetime.now(UTC).isoformat())
        await self.redis.set("kill_switch:activated_by", actor)

        closed = 0
        for pos in await broker.get_positions():
            ticket = int(pos.get("ticket", 0))
            if ticket and await broker.close_position(ticket):
                closed += 1

        quant_logger.kill_switch_activated(reason=reason, actor=actor)
        return {"activated": True, "positions_closed": closed}

    async def reset(self, actor: str) -> dict:
        await self.redis.delete("kill_switch:active", "kill_switch:reason", "kill_switch:activated_at", "kill_switch:activated_by")
        quant_logger.trade_closed(trade_id="system", pnl=0.0, rr=0.0, duration_s=0.0)
        return {"reset": True, "actor": actor}

    async def is_active(self) -> bool:
        return (await self.redis.get("kill_switch:active")) == "1"

    async def get_status(self) -> dict:
        active = await self.redis.get("kill_switch:active")
        reason = await self.redis.get("kill_switch:reason")
        at = await self.redis.get("kill_switch:activated_at")
        by = await self.redis.get("kill_switch:activated_by")
        return {
            "active": active == "1",
            "reason": reason,
            "activated_at": at,
            "activated_by": by,
        }
