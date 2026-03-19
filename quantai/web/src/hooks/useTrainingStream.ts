import { useEffect } from "react";
import { useDispatch } from "react-redux";

import { setTrainingState } from "../store/trainingSlice";
import type { TrainingStatePayload } from "../types";

function wsUrl(): string {
  const protocol = window.location.protocol === "https:" ? "wss:" : "ws:";
  const host = window.location.host;
  return `${protocol}//${host}/ws?user_id=public`;
}

export function useTrainingStream() {
  const dispatch = useDispatch();

  useEffect(() => {
    let socket: WebSocket | null = null;
    let pingTimer: number | null = null;

    const connect = () => {
      socket = new WebSocket(wsUrl());

      socket.onopen = () => {
        if (pingTimer !== null) {
          window.clearInterval(pingTimer);
        }
        pingTimer = window.setInterval(() => {
          if (socket && socket.readyState === WebSocket.OPEN) {
            socket.send(JSON.stringify({ type: "ping" }));
          }
        }, 15000);
      };

      socket.onmessage = (event: MessageEvent<string>) => {
        try {
          const payload = JSON.parse(event.data) as { type?: string; data?: TrainingStatePayload };
          if (payload.type === "training_update" && payload.data) {
            dispatch(setTrainingState(payload.data));
          }
        } catch {
          // Ignore invalid ws payloads.
        }
      };

      socket.onclose = () => {
        if (pingTimer !== null) {
          window.clearInterval(pingTimer);
          pingTimer = null;
        }
        window.setTimeout(connect, 1500);
      };
    };

    connect();

    return () => {
      if (pingTimer !== null) {
        window.clearInterval(pingTimer);
      }
      if (socket && socket.readyState <= WebSocket.OPEN) {
        socket.close();
      }
    };
  }, [dispatch]);
}
