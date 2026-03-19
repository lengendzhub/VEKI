// web/src/App.tsx
import { useSelector } from "react-redux";
import type { RootState } from "./store";
import { PriceChartCard } from "./components/chart/PriceChartCard";
import { AuthCard } from "./components/dashboard/AuthCard";
import { BacktestPanel } from "./components/dashboard/BacktestPanel";
import { PerformanceCard } from "./components/dashboard/PerformanceCard";
import { ProposalsCard } from "./components/dashboard/ProposalsCard";
import { SettingsCard } from "./components/dashboard/SettingsCard";
import { TrainingMonitor } from "./components/dashboard/TrainingMonitor";
import { TradesCard } from "./components/dashboard/TradesCard";
import { SectionGrid } from "./components/layout/SectionGrid";
import { TradingControlCard } from "./components/trading/TradingControlCard";
import { GlassCard } from "./components/ui/GlassCard";
import { useMetrics } from "./hooks/useMetrics";
import { useTrainingStream } from "./hooks/useTrainingStream";

export default function App() {
  const { loading, error } = useMetrics();
  useTrainingStream();
  const metrics = useSelector((state: RootState) => state.app.metrics);
  const backtest = useSelector((state: RootState) => state.app.backtest);

  return (
    <main style={{ padding: "1.25rem", display: "grid", gap: "1rem", maxWidth: 1200, margin: "0 auto" }}>
      <GlassCard>
        <h1 style={{ margin: 0 }}>QuantAI Trading System</h1>
        <p style={{ marginBottom: 0, color: "var(--muted)" }}>AI intraday scalping dashboard with backtesting and risk controls.</p>
      </GlassCard>

      <GlassCard>
        <h3 style={{ marginTop: 0 }}>Live Metrics</h3>
        {loading && <p>Loading metrics...</p>}
        {error && <p style={{ color: "#fca5a5" }}>{error}</p>}
        {!loading && !error && (
          <SectionGrid columns="repeat(auto-fit, minmax(160px, 1fr))">
            <div className="liquid-glass" style={{ padding: ".75rem" }}>
              <small style={{ color: "var(--muted)" }}>Trades/Hour</small>
              <div>{metrics?.trades_per_hour ?? "-"}</div>
            </div>
            <div className="liquid-glass" style={{ padding: ".75rem" }}>
              <small style={{ color: "var(--muted)" }}>Live Win Rate</small>
              <div>{metrics ? `${(metrics.win_rate_live * 100).toFixed(1)}%` : "-"}</div>
            </div>
            <div className="liquid-glass" style={{ padding: ".75rem" }}>
              <small style={{ color: "var(--muted)" }}>Latency</small>
              <div>{metrics?.avg_latency_ms ?? "-"} ms</div>
            </div>
            <div className="liquid-glass" style={{ padding: ".75rem" }}>
              <small style={{ color: "var(--muted)" }}>Model</small>
              <div>{metrics?.model_version ?? "-"}</div>
            </div>
          </SectionGrid>
        )}
      </GlassCard>

      <SectionGrid>
        <AuthCard />
        <ProposalsCard />
        <TradesCard />
        <PerformanceCard />
        <SettingsCard />
        <TradingControlCard />
      </SectionGrid>

      <PriceChartCard />
      <BacktestPanel />

      {backtest && (
        <GlassCard>
          <h3 style={{ marginTop: 0 }}>Backtest Result</h3>
          <p style={{ marginBottom: 0, color: "var(--muted)" }}>
            {backtest.symbol} {backtest.timeframe} · Return {(backtest.total_return * 100).toFixed(2)}% · PF {backtest.profit_factor.toFixed(2)} · Win Rate {(backtest.win_rate * 100).toFixed(2)}%
          </p>
        </GlassCard>
      )}

      <TrainingMonitor />
    </main>
  );
}
