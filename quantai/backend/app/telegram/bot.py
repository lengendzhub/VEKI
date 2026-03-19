# backend/app/telegram/bot.py
from __future__ import annotations

from telegram.ext import Application, CommandHandler

from app.config import get_settings
from app.telegram.handlers.commands import killswitch, metrics, start


class TelegramBot:
    def __init__(self) -> None:
        settings = get_settings()
        self.app = Application.builder().token(settings.TELEGRAM_BOT_TOKEN).build() if settings.TELEGRAM_BOT_TOKEN else None

    def configure(self) -> None:
        if self.app is None:
            return
        self.app.add_handler(CommandHandler("start", start))
        self.app.add_handler(CommandHandler("killswitch", killswitch))
        self.app.add_handler(CommandHandler("metrics", metrics))

    async def start(self) -> None:
        if self.app is None:
            return
        self.configure()
        await self.app.initialize()
        await self.app.start()

    async def stop(self) -> None:
        if self.app is None:
            return
        await self.app.stop()
        await self.app.shutdown()
