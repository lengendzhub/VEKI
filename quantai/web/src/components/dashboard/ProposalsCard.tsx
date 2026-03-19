import { useDispatch, useSelector } from "react-redux";

import { setProposal } from "../../store";
import type { RootState } from "../../store";
import type { Proposal } from "../../types";
import { GlassCard } from "../ui/GlassCard";

const sample: Proposal[] = [
  {
    id: "p1",
    symbol: "EURUSD",
    timeframe: "M5",
    direction: "long",
    confidence: 0.74,
    entry_price: 1.0842,
    stop_loss: 1.0818,
    take_profit: 1.0896,
    regime: "trend",
    explanation: "Momentum aligned with macro flow"
  },
  {
    id: "p2",
    symbol: "XAUUSD",
    timeframe: "M5",
    direction: "short",
    confidence: 0.68,
    entry_price: 3207,
    stop_loss: 3221,
    take_profit: 3180,
    regime: "volatile",
    explanation: "Failed breakout with rising realized volatility"
  }
];

export function ProposalsCard() {
  const dispatch = useDispatch();
  const current = useSelector((state: RootState) => state.app.proposal);

  return (
    <GlassCard>
      <h3 style={{ marginTop: 0 }}>Proposals</h3>
      <div style={{ display: "grid", gap: 8 }}>
        {sample.map((p) => (
          <button key={p.id} onClick={() => dispatch(setProposal(p))} style={{ textAlign: "left" }}>
            {p.symbol} {p.direction.toUpperCase()} · {(p.confidence * 100).toFixed(1)}%
          </button>
        ))}
      </div>
      {current && (
        <p style={{ marginBottom: 0, color: "var(--muted)" }}>
          Selected: {current.symbol} {current.direction.toUpperCase()} @ {current.entry_price}
        </p>
      )}
    </GlassCard>
  );
}
