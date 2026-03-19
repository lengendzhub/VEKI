import { useSelector } from "react-redux";

import type { RootState } from "../../store";
import { fixed, pct } from "../../utils/format";
import { GlassCard } from "../ui/GlassCard";

export function PerformanceCard() {
  const metrics = useSelector((state: RootState) => state.app.metrics);
  const backtest = useSelector((state: RootState) => state.app.backtest);

  return (
    <GlassCard>
      <h3 style={{ marginTop: 0 }}>Performance</h3>
      <div style={{ display: "grid", gap: 6 }}>
        <div>Live Win Rate: {metrics ? pct(metrics.win_rate_live) : "-"}</div>
        <div>Active Positions: {metrics?.active_positions ?? "-"}</div>
        <div>Backtest Return: {backtest ? pct(backtest.total_return) : "-"}</div>
        <div>Backtest Profit Factor: {backtest ? fixed(backtest.profit_factor, 2) : "-"}</div>
      </div>
    </GlassCard>
  );
}
