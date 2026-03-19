// web/src/types/index.ts
export type MarketRegime = "trend" | "range" | "volatile" | "low_volatility";

export interface Proposal {
  id: string;
  symbol: string;
  timeframe: string;
  direction: "long" | "short";
  confidence: number;
  entry_price: number;
  stop_loss: number;
  take_profit: number;
  regime: MarketRegime;
  explanation: string;
}

export interface BacktestResult {
  symbol: string;
  timeframe: string;
  initial_balance: number;
  final_balance: number;
  total_return: number;
  win_rate: number;
  max_drawdown: number;
  profit_factor: number;
  sharpe_ratio: number;
  total_trades: number;
  winning_trades: number;
  losing_trades: number;
  avg_rr: number;
  equity_curve: number[];
  trade_log: Record<string, unknown>[];
  regime_breakdown: Record<string, number>;
  news_blocked_count: number;
}

export interface MetricsSnapshot {
  trades_per_hour: number;
  win_rate_live: number;
  avg_latency_ms: number;
  active_positions: number;
  proposals_generated_today: number;
  proposals_approved_today: number;
  current_regime: Record<string, string>;
  news_blocks_today: number;
  ws_connections_active: number;
  model_version: string;
  kill_switch_active: boolean;
  uptime_seconds: number;
  data_quality_issues_today: number;
}

export type TrainingStatus = "idle" | "training" | "completed" | "failed";
export type TrainingHealth = "unknown" | "good" | "warning" | "bad";

export interface TrainingPoint {
  stage: string;
  epoch: number;
  total_epochs: number;
  loss: number;
  val_loss: number;
  accuracy: number;
  f1_score: number;
  status: TrainingStatus;
  updated_at: string;
}

export interface TrainingStatePayload {
  stage: string;
  epoch: number;
  total_epochs: number;
  loss: number;
  val_loss: number;
  accuracy: number;
  f1_score: number;
  status: TrainingStatus;
  health: TrainingHealth;
  overfitting: boolean;
  error: string | null;
  updated_at: string;
  history_points: number;
}
