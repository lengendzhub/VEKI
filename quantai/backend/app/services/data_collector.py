# backend/app/services/data_collector.py
from __future__ import annotations

from datetime import UTC, datetime

from app.services.logger import quant_logger


class DataCollector:
    def __init__(self) -> None:
        self.last_session: str | None = None

    def detect_session(self, now: datetime | None = None) -> str:
        now = now or datetime.now(UTC)
        h = now.hour
        if 2 <= h <= 5:
            return "london"
        if 8 <= h <= 11:
            return "new_york"
        if 20 <= h <= 23:
            return "asian"
        return "off"

    async def tick(self) -> None:
        current = self.detect_session()
        if self.last_session is not None and self.last_session != current:
            quant_logger.proposal_rejected("session", f"session changed {self.last_session} -> {current}")
        self.last_session = current
