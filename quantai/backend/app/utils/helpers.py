# backend/app/utils/helpers.py
from __future__ import annotations


def format_money(value: float) -> float:
    return round(value, 2)


def format_fx(value: float) -> float:
    return round(value, 5)


def progress_bar(current: int, total: int, width: int = 10) -> str:
    if total <= 0:
        return "░" * width
    ratio = max(0.0, min(1.0, current / total))
    filled = int(ratio * width)
    return "█" * filled + "░" * (width - filled)
