import { Area, AreaChart, CartesianGrid, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts";

import { GlassCard } from "../ui/GlassCard";

const series = [
  { t: "09:00", px: 1.0821 },
  { t: "09:15", px: 1.0829 },
  { t: "09:30", px: 1.0824 },
  { t: "09:45", px: 1.0836 },
  { t: "10:00", px: 1.0842 },
  { t: "10:15", px: 1.0838 },
  { t: "10:30", px: 1.0849 }
];

export function PriceChartCard() {
  return (
    <GlassCard>
      <h3 style={{ marginTop: 0 }}>Chart</h3>
      <div style={{ width: "100%", height: 220 }}>
        <ResponsiveContainer>
          <AreaChart data={series}>
            <CartesianGrid stroke="rgba(148,163,184,0.2)" strokeDasharray="4 4" />
            <XAxis dataKey="t" stroke="#94a3b8" />
            <YAxis stroke="#94a3b8" domain={["dataMin - 0.0008", "dataMax + 0.0008"]} />
            <Tooltip />
            <Area type="monotone" dataKey="px" stroke="#22c55e" fill="rgba(34,197,94,0.2)" strokeWidth={2.5} />
          </AreaChart>
        </ResponsiveContainer>
      </div>
    </GlassCard>
  );
}
