"use client";

import { useState, useEffect } from "react";
import { dailyReturns, annualizedVolatility, beta, portfolioBeta, herfindahl, sectorExposure } from "@/lib/quant/portfolio";

// Project 5 — Portfolio Risk, client-side. Reads a precomputed prices.json from
// /public (adjusted-close series per ticker + sectors). Everything computes in
// the browser. Refresh prices by regenerating prices.json and pushing.

interface PricesFile {
  benchmark: string;
  sectors: Record<string, string>;
  series: Record<string, number[]>;   // ticker -> adjusted closes, oldest first
}

const money = (x: number) => "$" + new Intl.NumberFormat("en-US", { maximumFractionDigits: 0 }).format(Math.round(x));
const SECTOR_COLOR: Record<string, string> = {
  Tech: "#3b6ea5", Financials: "#2f8f6b", Energy: "#b3812f", Healthcare: "#a34d6a",
  Industrials: "#4a7c3f", Index: "#7a7a7a", Unknown: "#7a7a7a",
};

// Default holdings; editable in the UI. Shares are illustrative.
const DEFAULT = [
  { ticker: "AAPL", shares: 50 }, { ticker: "MSFT", shares: 30 },
  { ticker: "JPM", shares: 40 }, { ticker: "XOM", shares: 100 },
  { ticker: "NVDA", shares: 20 },
];

export default function PortfolioPage() {
  const [prices, setPrices] = useState<PricesFile | null>(null);
  const [holdings, setHoldings] = useState(DEFAULT);
  const [loaded, setLoaded] = useState(false);
  const [missing, setMissing] = useState<string[]>([]);

  useEffect(() => {
    fetch("/prices.json")
      .then((r) => (r.ok ? r.json() : null))
      .then((d) => { setPrices(d); setLoaded(true); })
      .catch(() => setLoaded(true));
  }, []);

  let analysis: null | {
    total: number; pBeta: number; hhi: number; eff: number;
    sectors: Record<string, number>;
    positions: { ticker: string; sector: string; price: number; value: number; weight: number; beta: number; vol: number }[];
  } = null;

  if (prices) {
    const benchSeries = prices.series[prices.benchmark] ?? [];
    const benchRets = dailyReturns(benchSeries);
    const miss: string[] = [];
    const rows = holdings
      .filter((h) => h.ticker && h.shares > 0)
      .map((h) => {
        const series = prices.series[h.ticker];
        if (!series || series.length < 2) { miss.push(h.ticker); return null; }
        const price = series[series.length - 1];
        const rets = dailyReturns(series);
        return {
          ticker: h.ticker, sector: prices.sectors[h.ticker] ?? "Unknown",
          price, value: price * h.shares,
          beta: beta(rets, benchRets), vol: annualizedVolatility(rets),
        };
      })
      .filter((x): x is NonNullable<typeof x> => x !== null);

    if (miss.length && JSON.stringify(miss) !== JSON.stringify(missing)) setMissing(miss);

    if (rows.length) {
      const total = rows.reduce((s, r) => s + r.value, 0);
      const weights = rows.map((r) => r.value / total);
      const withW = rows.map((r, i) => ({ ...r, weight: weights[i] }));
      const hhi = herfindahl(weights);
      analysis = {
        total,
        pBeta: portfolioBeta(weights, rows.map((r) => r.beta)),
        hhi, eff: hhi > 0 ? 1 / hhi : 0,
        sectors: sectorExposure(weights, rows.map((r) => r.sector)),
        positions: withW,
      };
    }
  }

  const update = (i: number, patch: Partial<{ ticker: string; shares: number }>) => {
    const n = [...holdings]; n[i] = { ...n[i], ...patch }; setHoldings(n);
  };

  return (
    <div>
      <h1>Portfolio risk dashboard</h1>
      <p className="muted">
        Beta, volatility, and concentration from real price history, measured
        against {prices?.benchmark ?? "the market"}. Effective positions (1/HHI)
        reports true diversification.
      </p>

      {loaded && !prices && (
        <div className="info-box">
          No <code>prices.json</code> yet. Generate it with your price data and place
          it in <code>public/</code>. The math is ready; it just needs the data.
        </div>
      )}

      {holdings.map((h, i) => (
        <div key={i} className="trade-row">
          <input value={h.ticker} onChange={(e) => update(i, { ticker: e.target.value.toUpperCase() })} style={{ width: 90 }} placeholder="Ticker" />
          <input type="number" value={h.shares || ""} onChange={(e) => update(i, { shares: +e.target.value })} style={{ width: 100 }} placeholder="Shares" />
          <button className="icon-btn" aria-label="Remove" onClick={() => setHoldings(holdings.filter((_, j) => j !== i))}>✕</button>
        </div>
      ))}
      <button className="ghost" onClick={() => setHoldings([...holdings, { ticker: "", shares: 0 }])}>+ Add holding</button>

      {missing.length > 0 && (
        <div className="warn-box">No price data for: {missing.join(", ")} — skipped.</div>
      )}

      {analysis && (
        <>
          <div className="result-grid">
            <Metric label="Total value" value={money(analysis.total)} />
            <Metric label="Portfolio beta" value={analysis.pBeta.toFixed(2)} note={analysis.pBeta > 1 ? "more volatile than market" : "less volatile"} />
            <Metric label="Effective positions" value={analysis.eff.toFixed(1)} note={`${analysis.positions.length} names · HHI ${analysis.hhi.toFixed(2)}`} />
          </div>

          <div className="section-label">Sector exposure</div>
          <div className="sector-bars">
            {Object.entries(analysis.sectors).sort((a, b) => b[1] - a[1]).map(([s, w]) => (
              <div key={s} className="sector-row">
                <span className="sector-name">{s}</span>
                <div className="sector-track"><div className="sector-fill" style={{ width: `${(w * 100).toFixed(1)}%`, background: SECTOR_COLOR[s] ?? "#7a7a7a" }} /></div>
                <span className="sector-pct">{Math.round(w * 100)}%</span>
              </div>
            ))}
          </div>

          <div className="section-label">Positions</div>
          <table className="screen-table">
            <thead><tr><th className="left">Ticker</th><th className="left">Sector</th><th>Price</th><th>Value</th><th>Weight</th><th>Beta</th><th>Vol</th></tr></thead>
            <tbody>
              {analysis.positions.map((p) => (
                <tr key={p.ticker}>
                  <td className="left mono bold">{p.ticker}</td>
                  <td className="left dim">{p.sector}</td>
                  <td className="mono">${p.price.toFixed(2)}</td>
                  <td className="mono">{money(p.value)}</td>
                  <td className="mono">{(p.weight * 100).toFixed(1)}%</td>
                  <td className="mono">{p.beta.toFixed(2)}</td>
                  <td className="mono">{Math.round(p.vol * 100)}%</td>
                </tr>
              ))}
            </tbody>
          </table>
        </>
      )}
    </div>
  );
}

function Metric({ label, value, note }: { label: string; value: string; note?: string }) {
  return <div className="metric"><div className="metric-label">{label}</div><div className="metric-value">{value}</div>{note && <div className="metric-note">{note}</div>}</div>;
}
