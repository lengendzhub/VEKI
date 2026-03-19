# backend/app/telegram/handlers/alerts.py
from __future__ import annotations

from telegram.ext import Application


async def send_news_block_alert(app: Application, event_name: str, minutes_remaining: int) -> None:
    _ = event_name, minutes_remaining


async def send_kill_switch_activated(app: Application, reason: str) -> None:
    _ = reason


async def send_regime_change(app: Application, symbol: str, old_regime: str, new_regime: str) -> None:
    _ = symbol, old_regime, new_regime


async def send_high_confidence_alert(app: Application, proposal: dict) -> None:
    _ = proposal


async def send_data_quality_warning(app: Application, symbol: str, issues: list[str]) -> None:
    _ = symbol, issues
