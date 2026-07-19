// Reads the Buffett screener's handoff files.
//
// TWO FILES (split for performance):
//   screener_data.json        ~1.3 MB — slim index, loaded on every page
//   screener_financials.json  ~10 MB  — year-by-year history, loaded ON DEMAND
//                                       only when valuing a specific company
//
// The split matters: at ~3,166 companies the combined file was ~12 MB, which
// made the screener page slow. Now the list view downloads 1.3 MB and the heavy
// file is fetched only if the user actually opens a valuation.

export interface ScreenerLatest {
  revenue: number | null;
  free_cash_flow: number | null;
  total_debt: number | null;
  cash: number | null;
  shares_diluted: number | null;
  operating_income?: number | null;
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
  confidence: string | number | null;
  latest: ScreenerLatest;
  // Present only in the legacy single-file format; new format omits it.
  financials?: Record<string, FinancialYear>;
}

export interface FinancialYear {
  revenue: number | null;
  free_cash_flow: number | null;
  net_income: number | null;
  total_debt: number | null;
  cash: number | null;
  shares_diluted: number | null;
  gross_profit?: number | null;
  operating_income?: number | null;
  capex?: number | null;
  equity?: number | null;
}

// ticker -> { year -> metrics }
export type FinancialsFile = Record<string, Record<string, FinancialYear>>;

let _indexCache: ScreenerCompany[] | null = null;
let _finCache: FinancialsFile | null = null;

/** Slim index — safe to call on every page. Cached after first load. */
export async function loadScreenerData(): Promise<ScreenerCompany[]> {
  if (_indexCache) return _indexCache;
  try {
    const res = await fetch("/screener_data.json");
    if (!res.ok) return [];
    _indexCache = (await res.json()) as ScreenerCompany[];
    return _indexCache;
  } catch {
    return [];
  }
}

/** Heavy financials file — only call when actually valuing a company. */
export async function loadFinancials(): Promise<FinancialsFile> {
  if (_finCache) return _finCache;
  try {
    const res = await fetch("/screener_financials.json");
    if (!res.ok) return {};
    _finCache = (await res.json()) as FinancialsFile;
    return _finCache;
  } catch {
    return {};
  }
}

export function findCompany(data: ScreenerCompany[], ticker: string): ScreenerCompany | undefined {
  return data.find((c) => c.ticker?.toUpperCase() === ticker.toUpperCase());
}

// --- DCF prefill -----------------------------------------------------------

export interface DCFPrefill {
  baseFcf: number | null;
  netDebt: number | null;
  sharesOutstanding: number | null;
  impliedGrowth: number | null;
  hasData: boolean;
  yearsUsed: number;
}

/**
 * Derive DCF inputs. `history` is optional: without it we still get base FCF,
 * net debt, and shares from `latest`; with it we also compute historical FCF
 * growth to seed the growth assumption.
 */
export function dcfPrefillFrom(
  c: ScreenerCompany,
  history?: Record<string, FinancialYear>
): DCFPrefill {
  const L = c.latest ?? {};
  const baseFcf = L.free_cash_flow ?? null;
  const netDebt =
    L.total_debt !== null && L.total_debt !== undefined &&
    L.cash !== null && L.cash !== undefined
      ? L.total_debt - L.cash
      : null;
  const shares = L.shares_diluted ?? null;

  // Prefer the passed-in history; fall back to inline financials (legacy format).
  const hist = history ?? c.financials;
  let impliedGrowth: number | null = null;
  let yearsUsed = 0;

  if (hist) {
    const years = Object.keys(hist).sort();          // ascending
    const fcfSeries = years
      .map((y) => hist[y]?.free_cash_flow)
      .filter((v): v is number => v !== null && v !== undefined && v > 0);
    yearsUsed = fcfSeries.length;
    if (fcfSeries.length >= 2) {
      const periods = fcfSeries.length - 1;
      const ratio = fcfSeries[fcfSeries.length - 1] / fcfSeries[0];
      if (ratio > 0) {
        const g = Math.pow(ratio, 1 / periods) - 1;
        // Clamp conservatively. Historical growth rarely persists: a company
        // that compounded FCF at 30% will not do so for another five years, and
        // assuming it produces absurd fair values. Cap at 15% and floor at -5%.
        impliedGrowth = Math.max(-0.05, Math.min(0.15, g));
      }
    }
  }

  return {
    baseFcf,
    netDebt,
    sharesOutstanding: shares,
    impliedGrowth,
    hasData: baseFcf !== null && shares !== null && shares > 0,
    yearsUsed,
  };
}


/**
 * Build a fading growth path instead of holding stage-1 growth flat.
 *
 * Holding a high growth rate flat for five years is the single most common way
 * a DCF produces a nonsense number. Real businesses mean-revert, so we fade
 * linearly from the starting rate toward the terminal rate across the horizon.
 */
export function fadingGrowthPath(
  startGrowth: number,
  terminalGrowth: number,
  years = 5
): number[] {
  const path: number[] = [];
  for (let i = 0; i < years; i++) {
    const t = (i + 1) / years;               // 0 -> 1 across the horizon
    path.push(startGrowth + (terminalGrowth - startGrowth) * t);
  }
  return path;
}

/**
 * Whether a standard DCF is an appropriate valuation method for this company.
 *
 * DCF assumes a business generates free cash flow that can be discounted.
 * Banks, insurers, and asset managers don't work that way — their "cash flow"
 * is an artifact of reserve and float accounting, so a DCF on them produces
 * numbers that look precise and are meaningless. The Buffett screener already
 * scores these with dedicated industry models; we defer to it rather than
 * inventing a second answer.
 */
export interface DcfSuitability {
  suitable: boolean;
  reason: string | null;
  modelNote: string | null;   // what the screener used instead, if known
}

const FINANCIAL_SECTORS = ["financial", "financials", "banks", "insurance", "bank"];

export function dcfSuitability(c: ScreenerCompany): DcfSuitability {
  const tier = (c.verdict_tier ?? "").toUpperCase();
  const sector = (c.sector ?? "").toLowerCase();

  // The screener explicitly routed this to an industry model.
  if (tier.includes("SPECIAL MODEL")) {
    const kind =
      tier.includes("BANK") ? "a bank model"
      : tier.includes("INSURANCE") ? "an insurance model"
      : tier.includes("ASSET MGR") || tier.includes("CAP MKTS") ? "an asset-manager model"
      : "an industry-specific model";
    return {
      suitable: false,
      reason:
        "Discounted cash flow doesn't apply cleanly to financials — reserve and " +
        "float accounting means reported free cash flow isn't economically " +
        "comparable to an operating business.",
      modelNote: `The Buffett screener scored this company with ${kind}; trust that score over a DCF here.`,
    };
  }

  // Sector-based catch for financials the screener didn't specially tag.
  if (FINANCIAL_SECTORS.some((f) => sector.includes(f))) {
    return {
      suitable: false,
      reason:
        "This is a financial company. Standard DCF is unreliable for banks, " +
        "insurers, and asset managers because their cash flows reflect reserve " +
        "and float accounting rather than distributable earnings.",
      modelNote: "Treat any fair value below as indicative only.",
    };
  }

  return { suitable: true, reason: null, modelNote: null };
}
