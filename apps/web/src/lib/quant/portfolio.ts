// Portfolio risk metrics — client-side port of the verified Python module.

const TRADING_DAYS = 252;

export function dailyReturns(adjCloses: number[]): number[] {
  if (adjCloses.length < 2) return [];
  const out: number[] = [];
  for (let i = 1; i < adjCloses.length; i++) out.push(adjCloses[i] / adjCloses[i - 1] - 1);
  return out;
}

function mean(xs: number[]): number {
  return xs.reduce((s, x) => s + x, 0) / xs.length;
}

export function annualizedVolatility(returns: number[]): number {
  const n = returns.length;
  if (n < 2) return 0;
  const mu = mean(returns);
  const varr = returns.reduce((s, r) => s + (r - mu) ** 2, 0) / (n - 1);
  return Math.sqrt(varr) * Math.sqrt(TRADING_DAYS);
}

export function beta(assetReturns: number[], benchmarkReturns: number[]): number {
  const n = Math.min(assetReturns.length, benchmarkReturns.length);
  if (n < 2) return 0;
  const a = assetReturns.slice(-n);
  const b = benchmarkReturns.slice(-n);
  const ma = mean(a), mb = mean(b);
  let cov = 0, varB = 0;
  for (let i = 0; i < n; i++) {
    cov += (a[i] - ma) * (b[i] - mb);
    varB += (b[i] - mb) ** 2;
  }
  cov /= n - 1; varB /= n - 1;
  return varB === 0 ? 0 : cov / varB;
}

export function portfolioBeta(weights: number[], betas: number[]): number {
  return weights.reduce((s, w, i) => s + w * betas[i], 0);
}

export function herfindahl(weights: number[]): number {
  return weights.reduce((s, w) => s + w * w, 0);
}

export function sectorExposure(weights: number[], sectors: string[]): Record<string, number> {
  const out: Record<string, number> = {};
  weights.forEach((w, i) => { out[sectors[i]] = (out[sectors[i]] ?? 0) + w; });
  return out;
}
