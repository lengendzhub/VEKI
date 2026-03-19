// web/src/components/dashboard/BacktestPanel.tsx
import { useState } from "react";
import { motion } from "framer-motion";
import { useBacktest } from "../../hooks/useBacktest";
import { GlassCard } from "../ui/GlassCard";

export function BacktestPanel() {
  const { runBacktest, loading, error } = useBacktest();
  const [symbol, setSymbol] = useState("EURUSD");
  const [timeframe, setTimeframe] = useState("M5");

  return (
    <GlassCard>
      <h3 style={{ marginTop: 0 }}>Backtest Launcher</h3>
      <div style={{ display: "grid", gap: 8, gridTemplateColumns: "1fr 1fr auto" }}>
        <input value={symbol} onChange={(e) => setSymbol(e.target.value.toUpperCase())} />
        <input value={timeframe} onChange={(e) => setTimeframe(e.target.value.toUpperCase())} />
        <button
          onClick={() => runBacktest({ symbol, timeframe, start_date: new Date(Date.now() - 86400000 * 7).toISOString(), end_date: new Date().toISOString(), initial_balance: 100000 })}
          disabled={loading}
        >
          {loading ? "Running..." : "Run Simulation"}
        </button>
      </div>
      {error && <p style={{ color: "#fca5a5" }}>{error}</p>}
      <motion.div initial={{ opacity: 0, x: 24 }} animate={{ opacity: 1, x: 0 }}>
        <small style={{ color: "var(--muted)" }}>Uses the same backend AI pipeline as live mode.</small>
      </motion.div>
    </GlassCard>
  );
}
