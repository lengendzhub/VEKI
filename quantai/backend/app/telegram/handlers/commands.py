# backend/app/telegram/handlers/commands.py
from __future__ import annotations

from telegram import Update
from telegram.ext import ContextTypes

from app.telegram.formatters.messages import format_metrics
from app.telegram.keyboards.inline import kill_switch_confirm_keyboard


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    _ = context
    if update.effective_message:
        await update.effective_message.reply_text("QuantAI bot online")


async def killswitch(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    _ = context
    if update.effective_message:
        await update.effective_message.reply_text(
            "⛔ *Emergency Kill Switch*\nThis will close all positions and block new trades.",
            parse_mode="MarkdownV2",
            reply_markup=kill_switch_confirm_keyboard(),
        )


async def metrics(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    snapshot = context.application.bot_data.get("metrics", {})
    if update.effective_message:
        await update.effective_message.reply_text(format_metrics(snapshot), parse_mode="MarkdownV2")
