import { motion } from "framer-motion";
import { Line, LineChart, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts";
import { useSelector } from "react-redux";

import type { RootState } from "../../store";
import { GlassCard } from "../ui/GlassCard";

function statusColor(status: string): string {
  if (status === "completed") return "#22c55e";
  if (status === "failed") return "#ef4444";
  if (status === "training") return "#60a5fa";
  return "#94a3b8";
}

function healthColor(health: string): string {
  if (health === "good") return "#22c55e";
  if (health === "warning") return "#f59e0b";
  if (health === "bad") return "#ef4444";
  return "#94a3b8";
}

export function TrainingMonitor() {
  const training = useSelector((state: RootState) => state.training.state);
  const history = useSelector((state: RootState) => state.training.history);
  const progress = training.total_epochs > 0 ? Math.min(100, (training.epoch / training.total_epochs) * 100) : 0;

  return (
    <motion.div initial={{ opacity: 0, y: 12 }} animate={{ opacity: 1, y: 0 }} transition={{ duration: 0.35 }}>
      <GlassCard className="liquid-glass-purple">
        <div style={{ display: "flex", justifyContent: "space-between", gap: 8, alignItems: "center", marginBottom: 12 }}>
          <h3 style={{ margin: 0 }}>Live Training Monitor</h3>
          <div style={{ display: "flex", gap: 8, alignItems: "center" }}>
            <span style={{ padding: "4px 8px", borderRadius: 999, background: "rgba(255,255,255,.08)", fontSize: 12 }}>
              Stage: {training.stage.toUpperCase()}
            </span>
            <span style={{ padding: "4px 8px", borderRadius: 999, background: "rgba(255,255,255,.08)", color: statusColor(training.status), fontSize: 12 }}>
              {training.status.toUpperCase()}
            </span>
          </div>
        </div>

        <div style={{ marginBottom: 10 }}>
          <div style={{ display: "flex", justifyContent: "space-between", fontSize: 12, color: "var(--muted)", marginBottom: 6 }}>
            <span>Epoch Progress</span>
            <span>
              {training.epoch}/{training.total_epochs}
            </span>
          </div>
          <div style={{ height: 10, borderRadius: 999, background: "rgba(255,255,255,.08)", overflow: "hidden" }}>
            <motion.div
              style={{ height: "100%", background: "linear-gradient(90deg, #7c3aed, #c084fc)" }}
              initial={{ width: 0 }}
              animate={{ width: `${progress}%` }}
              transition={{ duration: 0.3 }}
            />
          </div>
        </div>

        <div style={{ display: "grid", gap: 8, gridTemplateColumns: "repeat(auto-fit, minmax(150px, 1fr))", marginBottom: 12 }}>
          <div>
            <small style={{ color: "var(--muted)" }}>Loss</small>
            <div>{training.loss.toFixed(5)}</div>
          </div>
          <div>
            <small style={{ color: "var(--muted)" }}>Val Loss</small>
            <div>{training.val_loss.toFixed(5)}</div>
          </div>
          <div>
            <small style={{ color: "var(--muted)" }}>Accuracy</small>
            <div>{(training.accuracy * 100).toFixed(2)}%</div>
          </div>
          <div>
            <small style={{ color: "var(--muted)" }}>F1</small>
            <div>{training.f1_score.toFixed(4)}</div>
          </div>
          <div>
            <small style={{ color: "var(--muted)" }}>Health</small>
            <div style={{ color: healthColor(training.health) }}>{training.health.toUpperCase()}</div>
          </div>
          <div>
            <small style={{ color: "var(--muted)" }}>Overfitting</small>
            <div style={{ color: training.overfitting ? "#f59e0b" : "#22c55e" }}>{training.overfitting ? "DETECTED" : "NO"}</div>
          </div>
        </div>

        <div style={{ width: "100%", height: 220 }}>
          <ResponsiveContainer>
            <LineChart data={history}>
              <XAxis dataKey="epoch" stroke="#94a3b8" />
              <YAxis stroke="#94a3b8" />
              <Tooltip />
              <Line type="monotone" dataKey="loss" stroke="#a78bfa" strokeWidth={2} dot={false} />
              <Line type="monotone" dataKey="val_loss" stroke="#60a5fa" strokeWidth={2} dot={false} />
            </LineChart>
          </ResponsiveContainer>
        </div>

        {training.error && <p style={{ color: "#fca5a5", marginBottom: 0 }}>Error: {training.error}</p>}
      </GlassCard>
    </motion.div>
  );
}
