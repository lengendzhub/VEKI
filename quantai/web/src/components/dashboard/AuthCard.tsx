import { FormEvent, useMemo, useState } from "react";

import { GlassCard } from "../ui/GlassCard";
import { clearToken, getToken, setToken } from "../../utils/storage";

export function AuthCard() {
  const [email, setEmail] = useState("trader@quantai.dev");
  const [password, setPassword] = useState("");
  const [version, setVersion] = useState(0);
  const token = useMemo(() => getToken(), [version]);

  const signIn = (e: FormEvent) => {
    e.preventDefault();
    if (email.trim().length < 4 || password.length < 6) {
      return;
    }
    setToken(`demo-${Date.now()}`);
    setVersion((v) => v + 1);
  };

  const signOut = () => {
    clearToken();
    setVersion((v) => v + 1);
  };

  return (
    <GlassCard>
      <h3 style={{ marginTop: 0 }}>Auth</h3>
      <form onSubmit={signIn} style={{ display: "grid", gap: 8 }}>
        <input value={email} onChange={(e) => setEmail(e.target.value)} placeholder="Email" />
        <input value={password} onChange={(e) => setPassword(e.target.value)} type="password" placeholder="Password" />
        <div style={{ display: "flex", gap: 8 }}>
          <button type="submit">Sign In</button>
          <button type="button" onClick={signOut}>
            Sign Out
          </button>
        </div>
      </form>
      <small style={{ color: token ? "#86efac" : "var(--muted)" }}>
        {token ? "Authenticated" : "Not authenticated"}
      </small>
    </GlassCard>
  );
}
