"use client";

import { useState, useEffect } from "react";
import { roic, fcfGrowth, evToEbit, priceToFcf, passes, Criterion } from "@/lib/quant/screener";
import { loadScreenerData, ScreenerCompany } from "@/lib/quant/screenerData";

// Project 9 — Quant Screener, client-side. Reads the Buffett screener's universe
// and lets you filter it on computed ratios. Each passing ticker links straight
// to its DCF valuation, completing the screen -> value pipeline.

interface Row {
  ticker: string; sector: string;
  roic: number | null; fcfGrowth: number | null; evToEbit: number | null; pfcf: number | null;
}

const META: Record<string, { label: string; pct: boolean }> = {
  roic: { label: "ROIC", pct: true },
  fcfGrowth: { label: "FCF growth", pct: true },
  evToEbit: { label: "EV/EBIT", pct: false },
  pfcf: { label: "P/FCF", pct: false },
};
const OPS: Criterion["op"][] = [">=", "<=", ">", "<"];

function fmt(key: string, v: number | null): string {
  if (v === null) return "—";
  return META[key]?.pct ? `${Math.round(v * 100)}%` : `${v.toFixed(1)}x`;
}

export default function ScreenerPage() {
  const [rows, setRows] = useState<Row[]>([]);
  const [criteria, setCriteria] = useState<Criterion[]>([
    { metric: "roic", op: ">=", value: 0.15 },
  ]);
  const [loaded, setLoaded] = useState(false);

  // Build screenable rows from the Buffett universe by computing ratios from
  // each company's real financials.
  useEffect(() => {
    loadScreenerData().then((data: ScreenerCompany[]) => {
      const built = data.map((c) => {
        const L = c.latest;
        const years = Object.keys(c.financials).sort();
        const fcfSeries = years
          .map((y) => c.financials[y].free_cash_flow)
          .filter((v): v is number => v !== null && v > 0);
        // Approx EBIT via operating income if present in latest year, else null.
        const latestYear = c.financials[years[years.length - 1]] ?? {};
        const ebit = (latestYear as { operating_income?: number | null }).operating_income ?? null;
        return {
          ticker: c.ticker,
          sector: c.sector,
          roic: ebit !== null ? roic(ebit, 0.21, (L.total_debt ?? 0) + ((latestYear as { equity?: number | null }).equity ?? 0)) : null,
          fcfGrowth: fcfGrowth(fcfSeries),
          evToEbit: ebit !== null && c.market_cap !== null ? evToEbit(c.market_cap, L.total_debt ?? 0, L.cash ?? 0, ebit) : null,
          pfcf: c.market_cap !== null && L.free_cash_flow !== null ? priceToFcf(c.market_cap, L.free_cash_flow) : null,
        };
      });
      setRows(built);
      setLoaded(true);
    });
  }, []);

  const passing = rows.filter((r) =>
    criteria.every((c) => passes((r as unknown as Record<string, number | null>)[c.metric], c))
  );

  return (
    <div>
      <h1>Quant screener</h1>
      <p className="muted">
        Filter the screened universe on ROIC, FCF growth, and valuation multiples.
        Click any passing company to value it. Undefined metrics never pass.
      </p>

      {!loaded && (
        <div className="info-box">
          Loading the screened universe. If this stays empty, run{" "}
          <code>npm run refresh-data</code> to populate <code>screener_data.json</code>.
        </div>
      )}

      <div className="filter-stack">
        {criteria.map((c, i) => (
          <div key={i} className="filter-row">
            <select value={c.metric} onChange={(e) => { const n = [...criteria]; n[i] = { ...c, metric: e.target.value }; setCriteria(n); }}>
              {Object.entries(META).map(([k, m]) => <option key={k} value={k}>{m.label}</option>)}
            </select>
            <select value={c.op} onChange={(e) => { const n = [...criteria]; n[i] = { ...c, op: e.target.value as Criterion["op"] }; setCriteria(n); }}>
              {OPS.map((op) => <option key={op} value={op}>{op}</option>)}
            </select>
            <input type="number" step={META[c.metric]?.pct ? 0.01 : 0.5} value={c.value}
              onChange={(e) => { const n = [...criteria]; n[i] = { ...c, value: +e.target.value }; setCriteria(n); }} />
            <button className="icon-btn" aria-label="Remove" onClick={() => setCriteria(criteria.filter((_, j) => j !== i))}>✕</button>
          </div>
        ))}
      </div>
      <button className="ghost" onClick={() => setCriteria([...criteria, { metric: "fcfGrowth", op: ">=", value: 0.1 }])}>+ Add filter</button>

      {loaded && (
        <>
          <p className="screen-summary">{passing.length} of {rows.length} pass</p>
          <table className="screen-table">
            <thead>
              <tr>
                <th className="left">Ticker</th><th className="left">Sector</th>
                <th>ROIC</th><th>FCF growth</th><th>EV/EBIT</th><th>P/FCF</th><th></th>
              </tr>
            </thead>
            <tbody>
              {passing.map((r) => (
                <tr key={r.ticker}>
                  <td className="left mono bold">{r.ticker}</td>
                  <td className="left dim">{r.sector}</td>
                  <td className="mono">{fmt("roic", r.roic)}</td>
                  <td className="mono">{fmt("fcfGrowth", r.fcfGrowth)}</td>
                  <td className="mono">{fmt("evToEbit", r.evToEbit)}</td>
                  <td className="mono">{fmt("pfcf", r.pfcf)}</td>
                  <td><a className="row-link" href={`/valuation?ticker=${r.ticker}`}>value →</a></td>
                </tr>
              ))}
            </tbody>
          </table>
        </>
      )}
    </div>
  );
}
