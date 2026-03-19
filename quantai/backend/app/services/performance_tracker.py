# backend/app/services/performance_tracker.py
from __future__ import annotations

from app.services.metrics import metrics_collector


class PerformanceTracker:
    def record_trade_close(self, pnl: float, latency_ms: float) -> None:
        metrics_collector.record_trade(won=pnl >= 0, latency_ms=latency_ms)

    def snapshot(self) -> dict:
        return metrics_collector.get_snapshot()
