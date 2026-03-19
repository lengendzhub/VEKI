import { GlassCard } from "../ui/GlassCard";

const trades = [
  { id: "t1", symbol: "EURUSD", side: "LONG", status: "OPEN", pnl: 43.2 },
  { id: "t2", symbol: "XAUUSD", side: "SHORT", status: "OPEN", pnl: -12.8 }
];

export function TradesCard() {
  return (
    <GlassCard>
      <h3 style={{ marginTop: 0 }}>Trades</h3>
      <table style={{ width: "100%", borderCollapse: "collapse" }}>
        <thead>
          <tr style={{ color: "var(--muted)", textAlign: "left" }}>
            <th>Symbol</th>
            <th>Side</th>
            <th>Status</th>
            <th>PnL</th>
          </tr>
        </thead>
        <tbody>
          {trades.map((t) => (
            <tr key={t.id}>
              <td>{t.symbol}</td>
              <td>{t.side}</td>
              <td>{t.status}</td>
              <td style={{ color: t.pnl >= 0 ? "#86efac" : "#fca5a5" }}>{t.pnl.toFixed(1)}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </GlassCard>
  );
}
