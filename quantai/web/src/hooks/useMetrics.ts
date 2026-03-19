// web/src/hooks/useMetrics.ts
import { useEffect, useState } from "react";
import { fetchMetrics } from "../api/metrics";
import { useDispatch } from "react-redux";
import { setMetrics } from "../store";

export function useMetrics(pollMs = 5000) {
  const dispatch = useDispatch();
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let active = true;
    const key = import.meta.env.VITE_INTERNAL_API_KEY ?? "internal-dev-key";

    const tick = async () => {
      try {
        setLoading(true);
        const snapshot = await fetchMetrics(key);
        if (active) {
          dispatch(setMetrics(snapshot));
        }
      } catch (err) {
        if (active) {
          setError(err instanceof Error ? err.message : "Unknown metrics error");
        }
      } finally {
        if (active) {
          setLoading(false);
        }
      }
    };

    tick();
    const timer = window.setInterval(tick, pollMs);
    return () => {
      active = false;
      window.clearInterval(timer);
    };
  }, [dispatch, pollMs]);

  return { loading, error };
}
