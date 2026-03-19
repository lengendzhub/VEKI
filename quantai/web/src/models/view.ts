export interface TradeViewModel {
  id: string;
  symbol: string;
  side: "long" | "short";
  entry: number;
  stopLoss: number;
  takeProfit: number;
  status: "open" | "closed";
}

export interface ProposalViewModel {
  id: string;
  symbol: string;
  direction: "long" | "short";
  confidence: number;
  entryPrice: number;
  stopLoss: number;
  takeProfit: number;
}
