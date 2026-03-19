# backend/app/telegram/handlers/account.py
from __future__ import annotations

from telegram import Update
from telegram.ext import ContextTypes


async def account(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    _ = context
    if update.effective_message:
        await update.effective_message.reply_text("Account: mock mode")
