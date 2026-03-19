# backend/app/services/logger.py
from __future__ import annotations

import structlog


structlog.configure(
    processors=[
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.add_log_level,
        structlog.processors.JSONRenderer(),
    ]
)


class QuantLogger:
    """Structured JSON logger wrapper for consistent metadata."""

    def __init__(self) -> None:
        self._logger = structlog.get_logger("quantai")

    def trade_executed(self, trade_id: str, symbol: str, direction: str, entry: float, sl: float, tp: float, lots: float, actor: str) -> None:
        self._logger.info("trade_executed", trade_id=trade_id, symbol=symbol, direction=direction, entry=entry, sl=sl, tp=tp, lots=lots, actor=actor)

    def trade_closed(self, trade_id: str, pnl: float, rr: float, duration_s: float) -> None:
        self._logger.info("trade_closed", trade_id=trade_id, pnl=pnl, rr=rr, duration_s=duration_s)

    def proposal_generated(self, proposal_id: str, symbol: str, confidence: float, regime: str) -> None:
        self._logger.info("proposal_generated", proposal_id=proposal_id, symbol=symbol, confidence=confidence, regime=regime)

    def proposal_rejected(self, proposal_id: str, reason: str) -> None:
        self._logger.warning("proposal_rejected", proposal_id=proposal_id, reason=reason)

    def retrain_started(self, version: str, trigger_reason: str) -> None:
        self._logger.info("retrain_started", version=version, trigger_reason=trigger_reason)

    def retrain_completed(self, version: str, metrics: dict) -> None:
        self._logger.info("retrain_completed", version=version, metrics=metrics)

    def news_block(self, symbol: str, event_name: str, minutes_remaining: int) -> None:
        self._logger.info("news_block", symbol=symbol, event_name=event_name, minutes_remaining=minutes_remaining)

    def kill_switch_activated(self, reason: str, actor: str) -> None:
        self._logger.critical("kill_switch_activated", reason=reason, actor=actor)

    def data_quality_warning(self, symbol: str, timeframe: str, issues: list[str]) -> None:
        self._logger.warning("data_quality_warning", symbol=symbol, timeframe=timeframe, issues=issues)

    def mtf_misalignment(self, symbol: str, direction_4h: str, direction_1h: str, direction_5m: str) -> None:
        self._logger.info("mtf_misalignment", symbol=symbol, direction_4h=direction_4h, direction_1h=direction_1h, direction_5m=direction_5m)

    def error(self, module: str, error_type: str, message: str, traceback_str: str) -> None:
        self._logger.error("module_error", module=module, error_type=error_type, message=message, traceback=traceback_str)


quant_logger = QuantLogger()
