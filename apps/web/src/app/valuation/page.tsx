"use client";

import { useState, useEffect, useCallback, Suspense } from "react";
import { useSearchParams } from "next/navigation";
import { valueDCF, DCFError, DCFResult } from "@/lib/quant/dcf";
import { loadScreenerData, loadFinancials, findCompany, dcfPrefillFrom, fadingGrowthPath, dcfSuitability, ScreenerCompany } from "@/lib/quant/screenerData";

// Project 8 — DCF Valuation, client-side. If reached with ?ticker=GGG, it loads
// that company from the Buffett screener's data and pre-fills the model with the
// company's REAL financials. This is the screener -> valuation pipeline seam.

const money = (x: number) =>
  new Intl.NumberFormat("en-US", { maximumFractionDigits: 0 }).format(Math.round(x));

function ValuationInner() {
  const params = useSearchParams();
  const ticker = params.get("ticker");

  const [company, setCompany] = useState<ScreenerCompany | null>(null);
  const [baseFcf, setBaseFcf] = useState(1000);      // in $M
  const [netDebt, setNetDebt] = useState(500);
  const [shares, setShares] = useState(100);
  const [wacc, setWacc] = useState(0.1);
  const [tg, setTg] = useState(0.025);
  const [g1, setG1] = useState(0.12);
  const [prefilled, setPrefilled] = useState(false);

  // If a ticker is passed, pull the company's real numbers and pre-fill.
  const [loadingHistory, setLoadingHistory] = useState(false);
  const [yearsUsed, setYearsUsed] = useState(0);

  useEffect(() => {
    if (!ticker) return;
    setLoadingHistory(true);
    // Slim index first (fast), then the heavy financials file ONLY here.
    Promise.all([loadScreenerData(), loadFinancials()])
      .then(([data, fins]) => {
        const c = findCompany(data, ticker);
        if (!c) return;
        setCompany(c);
        const history = fins[c.ticker] ?? fins[c.ticker?.toUpperCase()];
        const pf = dcfPrefillFrom(c, history);
        if (pf.hasData) {
          // Screener values are absolute dollars; the model works in $M.
          setBaseFcf((pf.baseFcf as number) / 1e6);
          if (pf.netDebt !== null) setNetDebt(pf.netDebt / 1e6);
          if (pf.sharesOutstanding !== null) setShares(pf.sharesOutstanding / 1e6);
          if (pf.impliedGrowth !== null) setG1(pf.impliedGrowth);
          setPrefilled(true);
          setYearsUsed(pf.yearsUsed);
        }
      })
      .finally(() => setLoadingHistory(false));
  }, [ticker]);

  const [result, setResult] = useState<DCFResult | null>(null);
  const [error, setError] = useState<string | null>(null);

  const compute = useCallback(() => {
    try {
      // Growth fades from the stage-1 rate toward terminal across 5 years,
      // rather than holding a high rate flat (which inflates fair value).
      setResult(valueDCF({
        baseFcf, growthRates: fadingGrowthPath(g1, tg, 5),
        terminalGrowth: tg, discountRate: wacc,
        netDebt, sharesOutstanding: shares,
      }));
      setError(null);
    } catch (e) {
      setResult(null);
      setError(e instanceof DCFError ? e.message : "calculation error");
    }
  }, [baseFcf, netDebt, shares, wacc, tg, g1]);

  useEffect(() => { compute(); }, [compute]);

  return (
    <div>
      <h1>Discounted cash flow valuation</h1>

      {company && (
        <div className="prefill-banner">
          Loaded <strong>{company.company_name}</strong> ({company.ticker}) from the
          screener — {company.verdict_tier ?? "screened"}, score {company.final_score ?? "—"}.
          {prefilled
            ? ` Inputs below are the company's real financials${yearsUsed ? `, with growth from ${yearsUsed} years of FCF history` : ""}; adjust as you like.`
            : loadingHistory
            ? " Loading financial history…"
            : " Financial data was incomplete, so defaults are shown."}
          {company.current_price != null && result && (
            <div className="prefill-compare">
              Model fair value <strong>${result.fairValuePerShare.toFixed(2)}</strong> vs.
              market price <strong>${company.current_price.toFixed(2)}</strong>
              {" "}({result.fairValuePerShare > company.current_price ? "model sees upside" : "model sees downside"}).
            </div>
          )}
        </div>
      )}

      {company && !dcfSuitability(company).suitable && (
        <div className="unsuitable-box">
          <div className="unsuitable-title">DCF isn&apos;t the right tool for this company</div>
          <div className="unsuitable-body">{dcfSuitability(company).reason}</div>
          {dcfSuitability(company).modelNote && (
            <div className="unsuitable-note">{dcfSuitability(company).modelNote}</div>
          )}
        </div>
      )}

      <p className="muted">
        A valuation is only as good as its assumptions. Every input is yours to set.
        {" "}Values in millions. Stage-1 growth fades toward the terminal rate over five years.
      </p>

      <div className="grid-3">
        <Field label="Base FCF ($M)"><input type="number" value={baseFcf} onChange={(e) => setBaseFcf(+e.target.value)} /></Field>
        <Field label="Net debt ($M)"><input type="number" value={netDebt} onChange={(e) => setNetDebt(+e.target.value)} /></Field>
        <Field label="Shares (M)"><input type="number" value={shares} onChange={(e) => setShares(+e.target.value)} /></Field>
      </div>

      <Slider label="Discount rate (WACC)" value={wacc} min={0.04} max={0.2} step={0.005} onChange={setWacc} fmt={(v) => `${(v * 100).toFixed(1)}%`} />
      <Slider label="Terminal growth" value={tg} min={0} max={0.05} step={0.001} onChange={setTg} fmt={(v) => `${(v * 100).toFixed(1)}%`} />
      <Slider label="Stage-1 growth (5yr)" value={g1} min={-0.05} max={0.3} step={0.005} onChange={setG1} fmt={(v) => `${(v * 100).toFixed(1)}%`} />

      {error && <div className="error-box">{error}</div>}

      {result && (
        <div className="result-grid">
          <Metric label="Enterprise value" value={`$${money(result.enterpriseValue)}M`} />
          <Metric label="Equity value" value={`$${money(result.equityValue)}M`} />
          <Metric label="Fair value / share" value={`$${result.fairValuePerShare.toFixed(2)}`} highlight />
        </div>
      )}
    </div>
  );
}

export default function ValuationPage() {
  return (
    <Suspense fallback={<div className="muted">Loading…</div>}>
      <ValuationInner />
    </Suspense>
  );
}

function Field({ label, children }: { label: string; children: React.ReactNode }) {
  return <label className="field"><span>{label}</span>{children}</label>;
}
function Slider(props: { label: string; value: number; min: number; max: number; step: number; onChange: (v: number) => void; fmt: (v: number) => string; }) {
  return (
    <div className="slider-row">
      <span className="slider-label">{props.label}</span>
      <input type="range" min={props.min} max={props.max} step={props.step} value={props.value} onChange={(e) => props.onChange(+e.target.value)} />
      <span className="slider-value">{props.fmt(props.value)}</span>
    </div>
  );
}
function Metric({ label, value, highlight }: { label: string; value: string; highlight?: boolean }) {
  return (
    <div className={highlight ? "metric metric-highlight" : "metric"}>
      <div className="metric-label">{label}</div>
      <div className="metric-value">{value}</div>
    </div>
  );
}
