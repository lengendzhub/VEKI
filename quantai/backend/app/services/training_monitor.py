from __future__ import annotations

import asyncio
import logging
from collections import deque
from datetime import UTC, datetime
from typing import Awaitable, Callable

logger = logging.getLogger(__name__)

BroadcastCallback = Callable[[dict], Awaitable[None]]


class TrainingMonitor:
    def __init__(self, max_points: int = 200) -> None:
        self._lock = asyncio.Lock()
        self._history: deque[dict] = deque(maxlen=max_points)
        self._broadcast_cb: BroadcastCallback | None = None
        self._state: dict = {
            "stage": "idle",
            "epoch": 0,
            "total_epochs": 0,
            "loss": 0.0,
            "val_loss": 0.0,
            "accuracy": 0.0,
            "f1_score": 0.0,
            "status": "idle",
            "error": None,
            "health": "unknown",
            "overfitting": False,
            "updated_at": datetime.now(UTC).isoformat(),
        }

    def set_broadcast_callback(self, cb: BroadcastCallback | None) -> None:
        self._broadcast_cb = cb

    async def start(self, stage: str, total_epochs: int = 0) -> None:
        async with self._lock:
            self._state.update(
                {
                    "stage": stage,
                    "epoch": 0,
                    "total_epochs": int(max(0, total_epochs)),
                    "loss": 0.0,
                    "val_loss": 0.0,
                    "accuracy": 0.0,
                    "f1_score": 0.0,
                    "status": "training",
                    "error": None,
                    "health": "unknown",
                    "overfitting": False,
                    "updated_at": datetime.now(UTC).isoformat(),
                }
            )
            logger.info("training_monitor.start", extra={"stage": stage, "total_epochs": total_epochs})
            snapshot = self._state_payload_locked()
        await self._broadcast(snapshot)

    async def update(
        self,
        epoch: int,
        total_epochs: int,
        loss: float,
        val_loss: float,
        accuracy: float,
        f1: float,
    ) -> None:
        point: dict
        async with self._lock:
            point = {
                "stage": self._state["stage"],
                "epoch": int(epoch),
                "total_epochs": int(max(0, total_epochs)),
                "loss": float(loss),
                "val_loss": float(val_loss),
                "accuracy": float(accuracy),
                "f1_score": float(f1),
                "status": "training",
                "updated_at": datetime.now(UTC).isoformat(),
            }
            self._history.append(point)
            health, overfitting = self._compute_health_locked(point)
            self._state.update(
                {
                    **point,
                    "health": health,
                    "overfitting": overfitting,
                    "error": None,
                }
            )
            logger.info(
                "training_monitor.update",
                extra={
                    "stage": point["stage"],
                    "epoch": point["epoch"],
                    "total_epochs": point["total_epochs"],
                    "loss": point["loss"],
                    "val_loss": point["val_loss"],
                    "accuracy": point["accuracy"],
                    "f1_score": point["f1_score"],
                    "health": health,
                    "overfitting": overfitting,
                },
            )
            snapshot = self._state_payload_locked()
        await self._broadcast(snapshot)

    async def complete(self) -> None:
        async with self._lock:
            self._state.update(
                {
                    "status": "completed",
                    "updated_at": datetime.now(UTC).isoformat(),
                }
            )
            logger.info("training_monitor.complete", extra={"stage": self._state.get("stage")})
            snapshot = self._state_payload_locked()
        await self._broadcast(snapshot)

    async def fail(self, error: str) -> None:
        async with self._lock:
            self._state.update(
                {
                    "status": "failed",
                    "error": error,
                    "updated_at": datetime.now(UTC).isoformat(),
                }
            )
            logger.error("training_monitor.fail", extra={"stage": self._state.get("stage"), "error": error})
            snapshot = self._state_payload_locked()
        await self._broadcast(snapshot)

    async def get_state(self) -> dict:
        async with self._lock:
            return self._state_payload_locked()

    async def get_history(self) -> list[dict]:
        async with self._lock:
            return list(self._history)

    async def _broadcast(self, state: dict) -> None:
        if self._broadcast_cb is None:
            return
        payload = {"type": "training_update", "data": state}
        try:
            await self._broadcast_cb(payload)
        except Exception as exc:  # pragma: no cover
            logger.warning("training_monitor.broadcast_failed", extra={"error": str(exc)})

    def _state_payload_locked(self) -> dict:
        return {
            **self._state,
            "history_points": len(self._history),
        }

    def _compute_health_locked(self, current: dict) -> tuple[str, bool]:
        history = list(self._history)
        if len(history) < 3:
            return "unknown", False

        window = history[-3:]
        train_delta = float(window[-1]["loss"]) - float(window[0]["loss"])
        val_delta = float(window[-1]["val_loss"]) - float(window[0]["val_loss"])

        overfitting = train_delta < 0 and val_delta > 0
        if overfitting:
            return "warning", True

        if train_delta < 0 and val_delta <= 0:
            return "good", False

        if train_delta > 0 and val_delta > 0:
            return "bad", False

        return "warning", False


training_monitor = TrainingMonitor()
