# backend/app/telegram/middleware/auth.py
from __future__ import annotations

from app.config import get_settings


class TelegramAuthMiddleware:
    def __init__(self) -> None:
        self.settings = get_settings()

    def allowed(self, chat_id: int) -> bool:
        return chat_id in self.settings.TELEGRAM_ALLOWED_CHAT_IDS

    def admin_only(self, chat_id: int) -> bool:
        return chat_id == self.settings.TELEGRAM_ADMIN_CHAT_ID
