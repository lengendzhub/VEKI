# backend/tests/test_risk_manager.py
from __future__ import annotations

from app.services.risk_manager import RiskManager


def test_position_scaling_losses() -> None:
    rm = RiskManager()
    assert rm.calculate_position_scaling(100000, -3) <= rm.settings.MAX_RISK_PCT


def test_position_scaling_wins_cap() -> None:
    rm = RiskManager()
    assert rm.calculate_position_scaling(100000, 5) <= rm.settings.MAX_RISK_PCT * 1.5


def test_session_multiplier_outside() -> None:
    rm = RiskManager()
    val = rm.get_session_risk_multiplier()
    assert val in {0.4, 0.7, 1.0}
