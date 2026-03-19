# backend/app/telegram/formatters/messages.py
from __future__ import annotations


def escape_md(text: str) -> str:
    special = r"_*[]()~`>#+-=|{}.!"
    out = text
    for char in special:
        out = out.replace(char, f"\\{char}")
    return out


def format_metrics(snapshot: dict) -> str:
    return (
        "📊 *Live Metrics*\n"
        "━━━━━━━━━━━━━━━━━━━━━\n"
        f"Trades/hr:    {snapshot.get('trades_per_hour', 0)}\n"
        f"Win Rate:     {snapshot.get('win_rate_live', 0)}%\n"
        f"Avg Latency:  {snapshot.get('avg_latency_ms', 0)}ms\n"
        f"Active Pos:   {snapshot.get('active_positions', 0)}\n"
        f"Model:        {escape_md(str(snapshot.get('model_version', 'n/a')))}\n"
        "━━━━━━━━━━━━━━━━━━━━━"
    )
