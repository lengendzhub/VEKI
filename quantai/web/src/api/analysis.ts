// web/src/api/analysis.ts
import { api } from "./client";
import type { BacktestResult } from "../types";

export interface BacktestRequest {
  symbol: string;
  timeframe: string;
  start_date: string;
  end_date: string;
  initial_balance: number;
}

export async function backtest(payload: BacktestRequest): Promise<BacktestResult> {
  const response = await api.post<BacktestResult>("/analysis/backtest", payload);
  return response.data;
}
