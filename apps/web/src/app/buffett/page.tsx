"use client";

import { useState, useEffect } from "react";
import { loadScreenerData, ScreenerCompany } from "@/lib/quant/screenerData";

// The Buffett screener dashboard, wrapped INSIDE the platform so the nav stays.
// The raw dashboard renders in an iframe; above it, a summary bar and a
// "send to valuation" search so you can jump straight from a screened name
// into the DCF. This is the screener -> quant handoff.

export default function BuffettPage() {
  const [data, setData] = useState<ScreenerCompany[]>([]);
  const [query, setQuery] = useState("");

  useEffect(() => { loadScreenerData().then(setData); }, []);

  const matches = query.trim()
    ? data
        .filter(
          (c) =>
            c.ticker?.toUpperCase().includes(query.toUpperCase()) ||
            c.company_name?.toUpperCase().includes(query.toUpperCase())
        )
        .slice(0, 8)
    : [];

  // Top names by score, as quick jump-off points.
  const top = [...data]
    .filter((c) => c.final_score !== null)
    .sort((a, b) => (b.final_score ?? 0) - (a.final_score ?? 0))
    .slice(0, 6);

  return (
    <div>
      <h1>Buffett screener</h1>
      <p className="muted">
        {data.length > 0
          ? `${data.length} companies scored across 80 rules in 12 categories. Pick any name to value it.`
          : "Quality scoring across 80 rules in 12 categories."}
      </p>

      <div className="handoff-bar">
        <div className="handoff-label">Send a company to DCF valuation</div>
        <input
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          placeholder="Search ticker or company…"
          className="handoff-search"
        />
        {matches.length > 0 && (
          <div className="handoff-results">
            {matches.map((c) => (
              <a key={c.ticker} href={`/valuation?ticker=${c.ticker}`} className="handoff-hit">
                <span className="hh-ticker">{c.ticker}</span>
                <span className="hh-name">{c.company_name}</span>
                <span className="hh-score">{c.final_score ?? "—"}</span>
                <span className="hh-price">
                  {c.current_price != null ? `$${c.current_price.toFixed(2)}` : ""}
                </span>
                <span className="hh-go">value →</span>
              </a>
            ))}
          </div>
        )}

        {top.length > 0 && !query && (
          <div className="top-chips">
            <span className="chips-label">Top scored:</span>
            {top.map((c) => (
              <a key={c.ticker} href={`/valuation?ticker=${c.ticker}`} className="chip">
                {c.ticker} <span className="chip-score">{c.final_score}</span>
              </a>
            ))}
          </div>
        )}
      </div>

      <div className="dash-frame-wrap">
        <iframe
          src="/buffett.html"
          title="Buffett screener dashboard"
          className="dash-frame"
        />
      </div>
      <div className="frame-note">
        <a href="/buffett.html" target="_blank" rel="noreferrer">
          Open the dashboard full-screen ↗
        </a>
      </div>
    </div>
  );
}
