// Discounted Cash Flow valuation — client-side port of the verified Python module.
// Same two-stage logic, same guards. Runs entirely in the browser (no backend).

export interface DCFAssumptions {
  baseFcf: number;
  growthRates: number[];   // one per explicit year
  terminalGrowth: number;
  discountRate: number;    // WACC
  netDebt: number;
  sharesOutstanding: number;
}

export interface DCFResult {
  projectedFcf: number[];
  discountedFcf: number[];
  terminalValue: number;
  pvTerminalValue: number;
  enterpriseValue: number;
  equityValue: number;
  fairValuePerShare: number;
}

export class DCFError extends Error {}

export function valueDCF(a: DCFAssumptions): DCFResult {
  if (a.discountRate <= a.terminalGrowth) {
    throw new DCFError("discount rate must exceed terminal growth for a finite terminal value");
  }
  if (a.sharesOutstanding <= 0) throw new DCFError("shares outstanding must be positive");
  if (a.growthRates.length === 0) throw new DCFError("at least one growth rate required");

  const projected: number[] = [];
  let fcf = a.baseFcf;
  for (const g of a.growthRates) {
    fcf = fcf * (1 + g);
    projected.push(fcf);
  }

  const discounted = projected.map(
    (cf, t) => cf / Math.pow(1 + a.discountRate, t + 1)
  );

  const n = projected.length;
  const finalFcf = projected[n - 1];
  const terminalValue =
    (finalFcf * (1 + a.terminalGrowth)) / (a.discountRate - a.terminalGrowth);
  const pvTerminal = terminalValue / Math.pow(1 + a.discountRate, n);

  const enterpriseValue = discounted.reduce((s, x) => s + x, 0) + pvTerminal;
  const equityValue = enterpriseValue - a.netDebt;
  const fairValue = equityValue / a.sharesOutstanding;

  return {
    projectedFcf: projected,
    discountedFcf: discounted,
    terminalValue,
    pvTerminalValue: pvTerminal,
    enterpriseValue,
    equityValue,
    fairValuePerShare: fairValue,
  };
}
