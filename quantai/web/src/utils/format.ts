export function pct(value: number, digits = 2): string {
  return `${(value * 100).toFixed(digits)}%`;
}

export function money(value: number, currency = "USD"): string {
  return new Intl.NumberFormat("en-US", {
    style: "currency",
    currency,
    maximumFractionDigits: 2
  }).format(value);
}

export function fixed(value: number, digits = 4): string {
  return Number.isFinite(value) ? value.toFixed(digits) : "0";
}
