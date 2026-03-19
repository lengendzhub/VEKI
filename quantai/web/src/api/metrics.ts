// web/src/api/metrics.ts
import { api } from "./client";
import type { MetricsSnapshot } from "../types";

export async function fetchMetrics(internalKey: string): Promise<MetricsSnapshot> {
  const response = await api.get<MetricsSnapshot>("/metrics", { headers: { "X-Internal-Key": internalKey } });
  return response.data;
}
