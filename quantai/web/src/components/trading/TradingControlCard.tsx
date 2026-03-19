import { useState } from "react";

import { GlassCard } from "../ui/GlassCard";

export function TradingControlCard() {
  const [enabled, setEnabled] = useState(false);
  const [killSwitch, setKillSwitch] = useState(false);

  return (
    <GlassCard>
      <h3 style={{ marginTop: 0 }}>Trading Controls</h3>
      <p style={{ color: "var(--muted)", marginTop: 0 }}>Execution mode and safety constraints for live orders.</p>
      <div style={{ display: "grid", gap: 8 }}>
        <label style={{ display: "flex", justifyContent: "space-between", gap: 12 }}>
          <span>Enable live execution</span>
          <input type="checkbox" checked={enabled} onChange={(e) => setEnabled(e.target.checked)} />
        </label>
        <label style={{ display: "flex", justifyContent: "space-between", gap: 12 }}>
          <span>Kill switch</span>
          <input type="checkbox" checked={killSwitch} onChange={(e) => setKillSwitch(e.target.checked)} />
        </label>
      </div>
      <p style={{ color: killSwitch ? "#fca5a5" : "#86efac", marginBottom: 0 }}>
        {killSwitch ? "All new orders are blocked." : enabled ? "Trading enabled with risk gates." : "Dry mode only."}
      </p>
    </GlassCard>
  );
}
