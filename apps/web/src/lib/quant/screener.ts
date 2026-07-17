// Screener ratios — client-side port of the verified Python module.

export function roic(ebit: number, taxRate: number, investedCapital: number): number | null {
  if (investedCapital <= 0) return null;
  return (ebit * (1 - taxRate)) / investedCapital;
}

export function fcfGrowth(series: number[]): number | null {
  if (series.length < 2 || series[0] <= 0) return null;
  const periods = series.length - 1;
  const ratio = series[series.length - 1] / series[0];
  if (ratio <= 0) return null;
  return Math.pow(ratio, 1 / periods) - 1;
}

export function evToEbit(marketCap: number, totalDebt: number, cash: number, ebit: number): number | null {
  if (ebit <= 0) return null;
  return (marketCap + totalDebt - cash) / ebit;
}

export function priceToFcf(marketCap: number, fcf: number): number | null {
  if (fcf <= 0) return null;
  return marketCap / fcf;
}

export interface Criterion { metric: string; op: ">=" | "<=" | ">" | "<" | "=="; value: number; }

export function passes(v: number | null, c: Criterion): boolean {
  if (v === null || v === undefined) return false;
  switch (c.op) {
    case ">=": return v >= c.value;
    case "<=": return v <= c.value;
    case ">": return v > c.value;
    case "<": return v < c.value;
    case "==": return v === c.value;
  }
}
