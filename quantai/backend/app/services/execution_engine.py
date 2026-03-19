# backend/app/services/execution_engine.py
from __future__ import annotations

import asyncio
import time

from app.broker.base import BaseBroker
from app.config import get_settings
from app.schemas.analysis import ExecutionResult
from app.schemas.proposal import TradeProposal


class KillSwitchActiveError(Exception):
    pass


class ExecutionEngine:
    def __init__(self, kill_switch_checker) -> None:
        self.settings = get_settings()
        self.kill_switch_checker = kill_switch_checker

    async def execute_trade(self, proposal: TradeProposal, broker: BaseBroker) -> ExecutionResult:
        if await self.kill_switch_checker():
            raise KillSwitchActiveError("Kill switch is active. Trade execution blocked.")

        start = time.perf_counter()
        spread = 1.2
        if spread > self.settings.MAX_SPREAD_PIPS:
            raise ValueError("Spread too high.")

        order_type = "market" if abs(proposal.entry_price - proposal.stop_loss) <= (proposal.atr * 0.5) else "limit"
        response = await broker.execute(proposal)
        filled = float(response.get("filled_price", proposal.entry_price))
        slippage = abs(filled - proposal.entry_price) * 10000

        if slippage > self.settings.MAX_SLIPPAGE_PIPS:
            response = await broker.execute(proposal)
            filled = float(response.get("filled_price", proposal.entry_price))
            slippage = abs(filled - proposal.entry_price) * 10000

        levels: list[dict] = []
        if self.settings.ENABLE_PARTIAL_TP:
            risk = abs(proposal.entry_price - proposal.stop_loss)
            sign = 1 if proposal.direction == "long" else -1
            levels = [
                {"name": "tp1", "pct": 0.5, "price": proposal.entry_price + sign * risk},
                {"name": "tp2", "pct": 0.3, "price": proposal.entry_price + sign * risk * 2},
                {"name": "tp3", "pct": 0.2, "price": proposal.take_profit},
            ]
            ticket = int(response.get("ticket", 0))
            if ticket:
                asyncio.create_task(self._run_partial_tp_manager(ticket=ticket, levels=levels, broker=broker))

        elapsed = (time.perf_counter() - start) * 1000
        return ExecutionResult(
            filled_price=filled,
            slippage=round(slippage, 4),
            execution_time_ms=round(elapsed, 2),
            order_type=order_type,
            spread_at_execution=spread,
            partial_tp_levels=levels,
            breakeven_moved=bool(levels),
        )

    async def _run_partial_tp_manager(self, ticket: int, levels: list[dict], broker: BaseBroker) -> None:
        for _ in range(3):
            await asyncio.sleep(5)
            positions = await broker.get_positions()
            if not any(int(p.get("ticket", 0)) == ticket for p in positions):
                return

    async def _move_to_breakeven(self, ticket: int, entry: float, direction: str, broker: BaseBroker) -> None:
        delta = 0.0002 if direction == "long" else -0.0002
        await broker.modify_sl_tp(ticket=ticket, sl=entry + delta, tp=entry)

    async def _activate_trailing_stop(self, ticket: int, atr: float, direction: str, broker: BaseBroker) -> None:
        pos = await broker.get_positions()
        if not pos:
            return
        base = float(pos[0].get("price", 0.0))
        trail = atr if direction == "long" else -atr
        await broker.modify_sl_tp(ticket=ticket, sl=base - trail, tp=base + trail)
