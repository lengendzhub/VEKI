# backend/app/telegram/keyboards/inline.py
from __future__ import annotations

from telegram import InlineKeyboardButton, InlineKeyboardMarkup


def kill_switch_confirm_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        [
            [InlineKeyboardButton("⛔ CONFIRM KILL", callback_data="kill_confirm")],
            [InlineKeyboardButton("❌ Cancel", callback_data="kill_cancel")],
        ]
    )


def kill_switch_reset_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        [
            [InlineKeyboardButton("▶️ Resume Trading", callback_data="kill_reset")],
            [InlineKeyboardButton("📊 Check Status", callback_data="kill_status")],
        ]
    )
