import { createSlice, PayloadAction } from "@reduxjs/toolkit";

import type { TrainingPoint, TrainingStatePayload } from "../types";

interface TrainingSliceState {
  state: TrainingStatePayload;
  history: TrainingPoint[];
}

const initialState: TrainingSliceState = {
  state: {
    stage: "idle",
    epoch: 0,
    total_epochs: 0,
    loss: 0,
    val_loss: 0,
    accuracy: 0,
    f1_score: 0,
    status: "idle",
    health: "unknown",
    overfitting: false,
    error: null,
    updated_at: new Date().toISOString(),
    history_points: 0
  },
  history: []
};

const maxHistory = 200;

const trainingSlice = createSlice({
  name: "training",
  initialState,
  reducers: {
    setTrainingState(state, action: PayloadAction<TrainingStatePayload>) {
      state.state = action.payload;
      if (action.payload.status === "training") {
        const p: TrainingPoint = {
          stage: action.payload.stage,
          epoch: action.payload.epoch,
          total_epochs: action.payload.total_epochs,
          loss: action.payload.loss,
          val_loss: action.payload.val_loss,
          accuracy: action.payload.accuracy,
          f1_score: action.payload.f1_score,
          status: action.payload.status,
          updated_at: action.payload.updated_at
        };
        state.history.push(p);
        if (state.history.length > maxHistory) {
          state.history = state.history.slice(state.history.length - maxHistory);
        }
      }
    },
    setTrainingHistory(state, action: PayloadAction<TrainingPoint[]>) {
      state.history = action.payload.slice(-maxHistory);
    },
    resetTrainingState(state) {
      state.state = initialState.state;
      state.history = [];
    }
  }
});

export const { setTrainingState, setTrainingHistory, resetTrainingState } = trainingSlice.actions;
export default trainingSlice.reducer;
