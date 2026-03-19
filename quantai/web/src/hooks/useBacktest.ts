// web/src/hooks/useBacktest.ts
import { useState } from "react";
import { backtest, type BacktestRequest } from "../api/analysis";
import { useDispatch } from "react-redux";
import { setBacktest } from "../store";

export function useBacktest() {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const dispatch = useDispatch();

  const runBacktest = async (payload: BacktestRequest) => {
    try {
      setLoading(true);
      setError(null);
      const result = await backtest(payload);
      dispatch(setBacktest(result));
      return result;
    } catch (err) {
      setError(err instanceof Error ? err.message : "Unknown error");
      return null;
    } finally {
      setLoading(false);
    }
  };

  return { runBacktest, loading, error };
}
