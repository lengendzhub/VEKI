const TOKEN_KEY = "quantai_token";
const SETTINGS_KEY = "quantai_settings";

export interface UiSettings {
  autoExecute: boolean;
  telegramAlerts: boolean;
  trainingAlerts: boolean;
}

const defaultSettings: UiSettings = {
  autoExecute: false,
  telegramAlerts: true,
  trainingAlerts: true
};

export function getToken(): string | null {
  return localStorage.getItem(TOKEN_KEY);
}

export function setToken(token: string): void {
  localStorage.setItem(TOKEN_KEY, token);
}

export function clearToken(): void {
  localStorage.removeItem(TOKEN_KEY);
}

export function readSettings(): UiSettings {
  const raw = localStorage.getItem(SETTINGS_KEY);
  if (!raw) {
    return defaultSettings;
  }
  try {
    return { ...defaultSettings, ...(JSON.parse(raw) as Partial<UiSettings>) };
  } catch {
    return defaultSettings;
  }
}

export function writeSettings(next: UiSettings): void {
  localStorage.setItem(SETTINGS_KEY, JSON.stringify(next));
}
