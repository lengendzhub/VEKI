# backend/app/services/metrics.py
from __future__ import annotations

from collections import deque
from datetime import UTC, datetime


class MetricsCollector:
    """Simple in-memory metrics collector."""

    def __init__(self) -> None:
        self.started_at = datetime.now(UTC)
        self.trades = deque(maxlen=500)
        self.proposals = deque(maxlen=500)
        self.api_calls = deque(maxlen=2000)
        self.ws_messages = 0
        self.news_blocks = 0
        self.current_regime: dict[str, str] = {}
        self.proposals_approved_today = 0
        self.active_positions = 0
        self.model_version = "untrained"
        self.kill_switch_active = False
        self.data_quality_issues_today = 0

    def record_trade(self, won: bool, latency_ms: float) -> None:
        self.trades.append((datetime.now(UTC), won, latency_ms))

    def record_proposal(self, confidence: float) -> None:
        self.proposals.append((datetime.now(UTC), confidence))

    def record_ws_message(self) -> None:
        self.ws_messages += 1

    def record_api_call(self, endpoint: str, latency_ms: float, status: int) -> None:
        self.api_calls.append((datetime.now(UTC), endpoint, latency_ms, status))

    def set_current_regime(self, symbol: str, regime: str) -> None:
        self.current_regime[symbol] = regime

    def increment_news_block(self) -> None:
        self.news_blocks += 1

    def get_snapshot(self) -> dict:
        now = datetime.now(UTC)
        hour_ago = now.timestamp() - 3600
        hour_trades = [t for t in self.trades if t[0].timestamp() >= hour_ago]
        recent20 = list(self.trades)[-20:]
        win_rate = (sum(1 for _, won, _ in recent20 if won) / len(recent20) * 100) if recent20 else 0.0
        avg_latency = (sum(lat for _, _, lat in self.trades) / len(self.trades)) if self.trades else 0.0

        return {
            "trades_per_hour": float(len(hour_trades)),
            "win_rate_live": round(win_rate, 2),
            "avg_latency_ms": round(avg_latency, 2),
            "active_positions": int(self.active_positions),
            "proposals_generated_today": int(len(self.proposals)),
            "proposals_approved_today": int(self.proposals_approved_today),
            "current_regime": dict(self.current_regime),
            "news_blocks_today": int(self.news_blocks),
            "ws_connections_active": int(self.ws_messages),
            "model_version": self.model_version,
            "kill_switch_active": self.kill_switch_active,
            "uptime_seconds": float((now - self.started_at).total_seconds()),
            "data_quality_issues_today": int(self.data_quality_issues_today),
        }


metrics_collector = MetricsCollector()
