import { useState } from "react";

import { readSettings, writeSettings } from "../../utils/storage";
import { GlassCard } from "../ui/GlassCard";

export function SettingsCard() {
  const [settings, setSettings] = useState(readSettings());

  const setNext = (patch: Partial<typeof settings>) => {
    const next = { ...settings, ...patch };
    setSettings(next);
    writeSettings(next);
  };

  return (
    <GlassCard>
      <h3 style={{ marginTop: 0 }}>Settings</h3>
      <div style={{ display: "grid", gap: 8 }}>
        <label style={{ display: "flex", justifyContent: "space-between" }}>
          <span>Auto execute approved trades</span>
          <input
            type="checkbox"
            checked={settings.autoExecute}
            onChange={(e) => setNext({ autoExecute: e.target.checked })}
          />
        </label>
        <label style={{ display: "flex", justifyContent: "space-between" }}>
          <span>Telegram alerts</span>
          <input
            type="checkbox"
            checked={settings.telegramAlerts}
            onChange={(e) => setNext({ telegramAlerts: e.target.checked })}
          />
        </label>
        <label style={{ display: "flex", justifyContent: "space-between" }}>
          <span>Training alerts</span>
          <input
            type="checkbox"
            checked={settings.trainingAlerts}
            onChange={(e) => setNext({ trainingAlerts: e.target.checked })}
          />
        </label>
      </div>
    </GlassCard>
  );
}
