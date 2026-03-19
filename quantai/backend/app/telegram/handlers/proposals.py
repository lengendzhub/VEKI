# backend/app/telegram/handlers/proposals.py
from __future__ import annotations

from telegram import Update
from telegram.ext import ContextTypes


async def approve_proposal(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    _ = context
    if update.effective_message:
        await update.effective_message.reply_text("Proposal approved")


async def reject_proposal(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    _ = context
    if update.effective_message:
        await update.effective_message.reply_text("Proposal rejected")
