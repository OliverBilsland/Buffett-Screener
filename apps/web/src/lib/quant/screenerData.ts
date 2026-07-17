// Reads the Buffett screener's handoff file (screener_data.json) and adapts it
// into QuantHub inputs. This is the pipeline seam: screener output -> QuantHub input.
//
// Schema is exactly what the Buffett export produces (confirmed).

export interface ScreenerFinancialYear {
  revenue: number | null;
  free_cash_flow: number | null;
  net_income: number | null;
  total_debt: number | null;
  cash: number | null;
  shares_diluted: number | null;
  roe?: number | null;
  gross_margin?: number | null;
  operating_margin?: number | null;
  capex?: number | null;
}

export interface ScreenerCompany {
  ticker: string;
  company_name: string;
  sector: string;
  market_cap: number | null;
  current_price: number | null;
  final_score: number | null;
  market_adjusted_score: number | null;
  verdict_tier: string | null;
  confidence: string | null;
  latest: {
    revenue: number | null;
    free_cash_flow: number | null;
    total_debt: number | null;
    cash: number | null;
    shares_diluted: number | null;
  };
  financials: Record<string, ScreenerFinancialYear>;
}

// Load the handoff file from /public. Returns [] if not present yet.
export async function loadScreenerData(): Promise<ScreenerCompany[]> {
  try {
    const res = await fetch("/screener_data.json");
    if (!res.ok) return [];
    return (await res.json()) as ScreenerCompany[];
  } catch {
    return [];
  }
}

export function findCompany(data: ScreenerCompany[], ticker: string): ScreenerCompany | undefined {
  return data.find((c) => c.ticker?.toUpperCase() === ticker.toUpperCase());
}

// --- The key integration: derive DCF inputs from a screened company ---
//
// Net debt = total_debt - cash. Base FCF = most recent free_cash_flow.
// Historical FCF growth (if enough years) seeds the growth assumption, so the
// DCF opens pre-filled with the company's ACTUAL numbers rather than blanks.

export interface DCFPrefill {
  baseFcf: number | null;
  netDebt: number | null;
  sharesOutstanding: number | null;
  impliedGrowth: number | null;   // from historical FCF, if computable
  hasData: boolean;
}

export function dcfPrefillFrom(c: ScreenerCompany): DCFPrefill {
  const L = c.latest;
  const baseFcf = L.free_cash_flow;
  const netDebt =
    L.total_debt !== null && L.cash !== null ? L.total_debt - L.cash : null;
  const shares = L.shares_diluted;

  // Historical FCF CAGR across available years (oldest -> newest).
  let impliedGrowth: number | null = null;
  const years = Object.keys(c.financials).sort(); // ascending
  const fcfSeries = years
    .map((y) => c.financials[y].free_cash_flow)
    .filter((v): v is number => v !== null && v > 0);
  if (fcfSeries.length >= 2) {
    const periods = fcfSeries.length - 1;
    const ratio = fcfSeries[fcfSeries.length - 1] / fcfSeries[0];
    if (ratio > 0) {
      const g = Math.pow(ratio, 1 / periods) - 1;
      // clamp to a sane band so a wild historical print doesn't create nonsense
      impliedGrowth = Math.max(-0.10, Math.min(0.30, g));
    }
  }

  return {
    baseFcf,
    netDebt,
    sharesOutstanding: shares,
    impliedGrowth,
    hasData: baseFcf !== null && shares !== null && shares > 0,
  };
}
