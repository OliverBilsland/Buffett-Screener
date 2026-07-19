"use client";

import { useState, useEffect, useMemo } from "react";
import { fcfGrowth, evToEbit, priceToFcf, passes, Criterion } from "@/lib/quant/screener";
import { loadScreenerData, ScreenerCompany } from "@/lib/quant/screenerData";

// Quant screener over the Buffett universe. Shows price, Buffett score, and
// computed ratios side by side, and links each row into DCF valuation.

interface Row {
  ticker: string; name: string; sector: string;
  price: number | null; marketCap: number | null;
  score: number | null; tier: string | null;
  fcfGrowth: number | null; pfcf: number | null;
  evEbit: number | null; fcfYield: number | null;
}

const META: Record<string, { label: string; fmt: (v: number) => string }> = {
  score:     { label: "Buffett score", fmt: (v) => v.toFixed(0) },
  fcfGrowth: { label: "FCF growth",    fmt: (v) => `${(v * 100).toFixed(0)}%` },
  pfcf:      { label: "P/FCF",         fmt: (v) => `${v.toFixed(1)}x` },
  evEbit:    { label: "EV/EBIT",       fmt: (v) => `${v.toFixed(1)}x` },
  fcfYield:  { label: "FCF yield",     fmt: (v) => `${(v * 100).toFixed(1)}%` },
};
const OPS: Criterion["op"][] = [">=", "<=", ">", "<"];

const fmtCap = (v: number | null) => {
  if (v === null) return "—";
  if (v >= 1e9) return `$${(v / 1e9).toFixed(1)}B`;
  if (v >= 1e6) return `$${(v / 1e6).toFixed(0)}M`;
  return `$${v.toFixed(0)}`;
};

export default function ScreenerPage() {
  const [companies, setCompanies] = useState<ScreenerCompany[]>([]);
  const [loaded, setLoaded] = useState(false);
  const [criteria, setCriteria] = useState<Criterion[]>([{ metric: "score", op: ">=", value: 70 }]);
  const [hideRejects, setHideRejects] = useState(true);
  const [sortKey, setSortKey] = useState<string>("score");

  useEffect(() => { loadScreenerData().then((d) => { setCompanies(d); setLoaded(true); }); }, []);

  const rows: Row[] = useMemo(() => companies.map((c) => {
    const L = c.latest ?? {};
    // operating_income now comes from `latest` (the slim index), so the screener
    // never needs the heavy financials file.
    const ebit = L.operating_income ?? null;
    // FCF growth needs history; only available in the legacy inline format.
    const inline = c.financials;
    const fcfSeries = inline
      ? Object.keys(inline).sort()
          .map((y) => inline[y].free_cash_flow)
          .filter((v): v is number => v !== null && v !== undefined && v > 0)
      : [];
    return {
      ticker: c.ticker, name: c.company_name, sector: c.sector,
      price: c.current_price, marketCap: c.market_cap,
      score: c.final_score, tier: c.verdict_tier,
      fcfGrowth: fcfGrowth(fcfSeries),
      pfcf: c.market_cap !== null && L.free_cash_flow !== null ? priceToFcf(c.market_cap, L.free_cash_flow) : null,
      evEbit: ebit !== null && c.market_cap !== null ? evToEbit(c.market_cap, L.total_debt ?? 0, L.cash ?? 0, ebit) : null,
      fcfYield: c.market_cap !== null && L.free_cash_flow !== null && c.market_cap > 0 ? L.free_cash_flow / c.market_cap : null,
    };
  }), [companies]);

  const filtered = useMemo(() => {
    let out = rows.filter((r) => criteria.every((c) => passes((r as unknown as Record<string, number | null>)[c.metric], c)));
    if (hideRejects) out = out.filter((r) => !(r.tier ?? "").toUpperCase().includes("REJECT"));
    return [...out].sort((a, b) => {
      const av = (a as unknown as Record<string, number | null>)[sortKey];
      const bv = (b as unknown as Record<string, number | null>)[sortKey];
      if (av === null) return 1;
      if (bv === null) return -1;
      return bv - av;
    });
  }, [rows, criteria, hideRejects, sortKey]);

  return (
    <div>
      <h1>Quant screener</h1>
      <p className="muted">
        {loaded
          ? `${companies.length} companies from the Buffett screen. Filter on score, growth, and valuation — then value any name.`
          : "Loading the screened universe…"}
      </p>

      {loaded && companies.length === 0 && (
        <div className="info-box">
          No data loaded. Run <code>npm run refresh-data</code> to copy <code>screener_data.json</code> into <code>public/</code>.
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
            <input type="number" step="any" value={c.value}
              onChange={(e) => { const n = [...criteria]; n[i] = { ...c, value: +e.target.value }; setCriteria(n); }} />
            <button className="icon-btn" aria-label="Remove" onClick={() => setCriteria(criteria.filter((_, j) => j !== i))}>✕</button>
          </div>
        ))}
      </div>

      <div className="screener-controls">
        <button className="ghost" onClick={() => setCriteria([...criteria, { metric: "fcfYield", op: ">=", value: 0.04 }])}>+ Add filter</button>
        <label className="check">
          <input type="checkbox" checked={hideRejects} onChange={(e) => setHideRejects(e.target.checked)} /> Hide rejects
        </label>
        <label className="check">
          Sort by
          <select value={sortKey} onChange={(e) => setSortKey(e.target.value)}>
            {Object.entries(META).map(([k, m]) => <option key={k} value={k}>{m.label}</option>)}
          </select>
        </label>
      </div>

      {loaded && companies.length > 0 && (
        <>
          <p className="screen-summary">{filtered.length} of {rows.length} match</p>
          <div className="table-scroll">
            <table className="screen-table">
              <thead>
                <tr>
                  <th className="left">Ticker</th><th className="left">Company</th>
                  <th>Price</th><th>Mkt cap</th><th>Score</th>
                  <th>FCF gr</th><th>FCF yld</th><th>P/FCF</th><th></th>
                </tr>
              </thead>
              <tbody>
                {filtered.slice(0, 150).map((r) => (
                  <tr key={r.ticker}>
                    <td className="left mono bold">{r.ticker}</td>
                    <td className="left dim truncate" title={r.name}>{r.name}</td>
                    <td className="mono">{r.price !== null ? `$${r.price.toFixed(2)}` : "—"}</td>
                    <td className="mono">{fmtCap(r.marketCap)}</td>
                    <td className="mono score-cell">{r.score !== null ? r.score.toFixed(0) : "—"}</td>
                    <td className="mono">{r.fcfGrowth !== null ? META.fcfGrowth.fmt(r.fcfGrowth) : "—"}</td>
                    <td className="mono">{r.fcfYield !== null ? META.fcfYield.fmt(r.fcfYield) : "—"}</td>
                    <td className="mono">{r.pfcf !== null ? META.pfcf.fmt(r.pfcf) : "—"}</td>
                    <td><a className="row-link" href={`/valuation?ticker=${r.ticker}`}>value →</a></td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
          {filtered.length > 150 && <p className="screen-summary">Showing first 150. Add filters to narrow.</p>}
        </>
      )}
    </div>
  );
}
