# backend/app/services/notification_service.py
from __future__ import annotations

import logging

import httpx

from app.config import get_settings

logger = logging.getLogger(__name__)


class NotificationService:
    def __init__(self) -> None:
        self.settings = get_settings()

    async def send_news_block_alert(self, event_name: str, minutes_remaining: int) -> None:
        await self._send_text(f"📰 News Block\nEvent: {event_name}\nMinutes remaining: {minutes_remaining}")

    async def send_kill_switch_activated(self, reason: str) -> None:
        await self._send_text(f"⛔ Kill Switch Activated\nReason: {reason}")

    async def send_regime_change(self, symbol: str, old_regime: str, new_regime: str) -> None:
        await self._send_text(f"📈 Regime Change\n{symbol}: {old_regime} -> {new_regime}")

    async def send_mtf_misalignment(self, symbol: str) -> None:
        await self._send_text(f"⚠️ MTF Misalignment\n{symbol}")

    async def send_data_quality_warning(self, symbol: str, issues: list[str]) -> None:
        await self._send_text(f"⚠️ Data Quality Warning\n{symbol}\nIssues: {', '.join(issues)}")

    async def send_training_started(self, stage: str) -> None:
        await self._send_text(f"🧠 Training Started\nStage: {stage}")

    async def send_training_update(self, stage: str, epoch: int, total_epochs: int, loss: float, accuracy: float) -> None:
        await self._send_text(
            "🧠 Training Update\n"
            f"Stage: {stage.upper()}\n"
            f"Epoch: {epoch}/{total_epochs}\n"
            f"Loss: {loss:.4f}\n"
            f"Accuracy: {accuracy * 100:.2f}%"
        )

    async def send_training_completed(self, stage: str, accuracy: float, f1_score: float) -> None:
        await self._send_text(
            "✅ Training Completed\n"
            f"Stage: {stage.upper()}\n"
            f"Accuracy: {accuracy * 100:.2f}%\n"
            f"F1: {f1_score:.4f}"
        )

    async def send_training_failed(self, stage: str, error: str) -> None:
        await self._send_text(
            "❌ Training Failed\n"
            f"Stage: {stage.upper()}\n"
            f"Error: {error}"
        )

    async def _send_text(self, text: str) -> None:
        token = self.settings.TELEGRAM_BOT_TOKEN
        chat_id = self.settings.TELEGRAM_ADMIN_CHAT_ID
        if not token or not chat_id:
            return

        url = f"https://api.telegram.org/bot{token}/sendMessage"
        payload = {"chat_id": chat_id, "text": text}
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                resp = await client.post(url, json=payload)
                resp.raise_for_status()
        except Exception as exc:  # pragma: no cover
            logger.warning("notification.telegram_send_failed", extra={"error": str(exc)})
