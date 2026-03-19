# backend/app/services/risk_manager.py
from __future__ import annotations

from datetime import UTC, datetime

from app.config import get_settings


class RiskManager:
    def __init__(self) -> None:
        self.settings = get_settings()

    def check_daily_drawdown(self, start_balance: float, current_balance: float) -> bool:
        if start_balance <= 0:
            return False
        dd = max(0.0, (start_balance - current_balance) / start_balance)
        return dd <= self.settings.MAX_DAILY_DD

    def check_correlation(self, symbol: str, open_positions: list[dict]) -> bool:
        usd_long = {"EURUSD", "GBPUSD", "AUDUSD", "NZDUSD"}
        usd_inverse = {"USDJPY", "USDCHF"}
        positive_count = sum(1 for p in open_positions if p.get("symbol") in usd_long)
        inverse_count = sum(1 for p in open_positions if p.get("symbol") in usd_inverse)

        if symbol in usd_long and positive_count >= 2:
            return False
        if symbol in usd_inverse and inverse_count >= 1 and positive_count > 0:
            return False
        return True

    def calculate_position_scaling(self, account_balance: float, streak: int) -> float:
        _ = account_balance
        base = self.settings.MAX_RISK_PCT
        if streak <= -3:
            return base * 0.5
        if streak >= 3:
            return min(base * 1.25, base * 1.5)
        return base

    def get_session_risk_multiplier(self, current_utc: datetime | None = None) -> float:
        now = current_utc or datetime.now(UTC)
        h = now.hour
        if 2 <= h <= 5 or 8 <= h <= 11:
            return 1.0
        if 20 <= h <= 23:
            return 0.7
        return 0.4

    def calculate_dynamic_risk(self, base_risk: float, balance: float, streak: int, session_multiplier: float, start_balance: float = 100000.0) -> float:
        risk = base_risk
        drawdown = max(0.0, (start_balance - balance) / start_balance)

        if drawdown > 0.04:
            risk *= 0.25
        elif drawdown > 0.03:
            risk *= 0.5

        if streak >= 5:
            risk *= 1.25

        risk *= session_multiplier
        hard_cap = self.settings.MAX_RISK_PCT * 1.5
        return min(risk, hard_cap)
