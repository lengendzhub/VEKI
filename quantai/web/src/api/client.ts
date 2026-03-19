// web/src/api/client.ts
import axios from "axios";
import { getToken } from "../utils/storage";

export const api = axios.create({
  baseURL: "/api/v1",
  timeout: 30000
});

api.interceptors.request.use((config) => {
  const token = getToken();
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});
