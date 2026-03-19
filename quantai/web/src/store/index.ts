// web/src/store/index.ts
import { configureStore, createSlice, PayloadAction } from "@reduxjs/toolkit";
import type { BacktestResult, MetricsSnapshot, Proposal } from "../types";
import trainingReducer from "./trainingSlice";

interface AppState {
  proposal: Proposal | null;
  backtest: BacktestResult | null;
  metrics: MetricsSnapshot | null;
}

const initialState: AppState = {
  proposal: null,
  backtest: null,
  metrics: null
};

const appSlice = createSlice({
  name: "app",
  initialState,
  reducers: {
    setProposal(state, action: PayloadAction<Proposal | null>) {
      state.proposal = action.payload;
    },
    setBacktest(state, action: PayloadAction<BacktestResult | null>) {
      state.backtest = action.payload;
    },
    setMetrics(state, action: PayloadAction<MetricsSnapshot | null>) {
      state.metrics = action.payload;
    }
  }
});

export const { setProposal, setBacktest, setMetrics } = appSlice.actions;

export const store = configureStore({
  reducer: {
    app: appSlice.reducer,
    training: trainingReducer
  }
});

export type RootState = ReturnType<typeof store.getState>;
export type AppDispatch = typeof store.dispatch;
