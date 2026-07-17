// Options payoffs + Black-Scholes — client-side port of the verified Python module.

export interface Leg {
  kind: "call" | "put";
  direction: "long" | "short";
  strike: number;
  premium: number;
  quantity?: number;
}

function intrinsic(kind: string, strike: number, spot: number): number {
  if (kind === "call") return Math.max(spot - strike, 0);
  if (kind === "put") return Math.max(strike - spot, 0);
  throw new Error(`unknown option kind: ${kind}`);
}

export function legPayoff(leg: Leg, spot: number): number {
  const q = leg.quantity ?? 1;
  const intr = intrinsic(leg.kind, leg.strike, spot);
  const pnl = leg.direction === "long" ? intr - leg.premium : leg.premium - intr;
  return pnl * q;
}

export function strategyPayoff(legs: Leg[], spots: number[]): number[] {
  return spots.map((s) => legs.reduce((sum, leg) => sum + legPayoff(leg, s), 0));
}

export function breakevens(legs: Leg[], lo: number, hi: number, step = 0.01): number[] {
  const points: number[] = [];
  let prevS = lo;
  let prev = legs.reduce((s, leg) => s + legPayoff(leg, lo), 0);
  let s = lo + step;
  while (s <= hi) {
    const cur = legs.reduce((sum, leg) => sum + legPayoff(leg, s), 0);
    if (prev === 0) points.push(Math.round(prevS * 1e4) / 1e4);
    else if (prev < 0 !== cur < 0) {
      const frac = prev / (prev - cur);
      points.push(Math.round((prevS + frac * step) * 1e4) / 1e4);
    }
    prev = cur; prevS = s; s += step;
  }
  return points;
}

// erf via Abramowitz & Stegun 7.1.26 (max error ~1.5e-7)
function erf(x: number): number {
  const sign = x >= 0 ? 1 : -1;
  x = Math.abs(x);
  const t = 1 / (1 + 0.3275911 * x);
  const y =
    1 -
    ((((1.061405429 * t - 1.453152027) * t + 1.421413741) * t - 0.284496736) * t +
      0.254829592) *
      t *
      Math.exp(-x * x);
  return sign * y;
}

// Normal CDF built from erf: Phi(x) = 0.5 * (1 + erf(x / sqrt(2)))
function normCdf(x: number): number {
  return 0.5 * (1 + erf(x / Math.SQRT2));
}

export function blackScholesPrice(
  kind: "call" | "put", spot: number, strike: number, t: number, r: number, sigma: number
): number {
  if (t <= 0 || sigma <= 0) return intrinsic(kind, strike, spot);
  const d1 = (Math.log(spot / strike) + (r + 0.5 * sigma * sigma) * t) / (sigma * Math.sqrt(t));
  const d2 = d1 - sigma * Math.sqrt(t);
  if (kind === "call") return spot * normCdf(d1) - strike * Math.exp(-r * t) * normCdf(d2);
  return strike * Math.exp(-r * t) * normCdf(-d2) - spot * normCdf(-d1);
}
