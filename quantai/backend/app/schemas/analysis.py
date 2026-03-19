# backend/app/schemas/analysis.py
from __future__ import annotations

from datetime import datetime
from enum import Enum

from pydantic import BaseModel, Field


class MarketRegime(str, Enum):
    TREND = "trend"
    RANGE = "range"
    VOLATILE = "volatile"
    LOW_VOLATILITY = "low_volatility"


class ValidationResult(BaseModel):
    is_valid: bool
    issues: list[str]
    missing_pct: float
    repaired_count: int


class ExecutionResult(BaseModel):
    filled_price: float
    slippage: float
    execution_time_ms: float
    order_type: str
    spread_at_execution: float
    partial_tp_levels: list[dict]
    breakeven_moved: bool


class BacktestRequest(BaseModel):
    symbol: str
    timeframe: str
    start_date: datetime
    end_date: datetime
    initial_balance: float = Field(default=100000.0, gt=0)


class BacktestResult(BaseModel):
    symbol: str
    timeframe: str
    start_date: datetime
    end_date: datetime
    initial_balance: float
    final_balance: float
    total_return: float
    win_rate: float
    max_drawdown: float
    profit_factor: float
    sharpe_ratio: float
    total_trades: int
    winning_trades: int
    losing_trades: int
    avg_rr: float
    equity_curve: list[float]
    trade_log: list[dict]
    regime_breakdown: dict
    news_blocked_count: int
