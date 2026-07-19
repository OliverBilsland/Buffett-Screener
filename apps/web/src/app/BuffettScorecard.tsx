"use client";

import { useState } from "react";
import { CompanyScoring, ResolvedCategory, ruleTally } from "@/lib/quant/screenerData";

// The Buffett scorecard: every rule that contributed to the company's score,
// grouped by category, with pass/fail/not-applicable status. This is what turns
// a bare score into something you can actually interrogate.

export function BuffettScorecard({ scoring, categories }: { scoring: CompanyScoring; categories: ResolvedCategory[] }) {
  const [openCats, setOpenCats] = useState<Set<string>>(new Set());
  const [filter, setFilter] = useState<"all" | "failed" | "passed">("all");

  const tally = ruleTally(categories);

  const toggle = (cat: string) => {
    const next = new Set(openCats);
    if (next.has(cat)) next.delete(cat);
    else next.add(cat);
    setOpenCats(next);
  };

  const expandAll = () => setOpenCats(new Set(categories.map((c) => c.category)));
  const collapseAll = () => setOpenCats(new Set());

  const visible = (passed: boolean | null) =>
    filter === "all" || (filter === "failed" && passed === false) || (filter === "passed" && passed === true);

  return (
    <div className="scorecard">
      <div className="sc-head">
        <h2>Buffett scorecard</h2>
        <div className="sc-tally">
          <span className="t-pass">{tally.passed} passed</span>
          <span className="t-fail">{tally.failed} failed</span>
          {tally.na > 0 && <span className="t-na">{tally.na} n/a</span>}
        </div>
      </div>

      <div className="sc-summary">
        {scoring.binary_pct !== null && (
          <SummaryStat label="Rule score" value={`${scoring.binary_pct.toFixed(1)}%`} />
        )}
        {scoring.graded_score !== null && (
          <SummaryStat label="Graded score" value={scoring.graded_score.toFixed(1)} />
        )}
        {scoring.final_score !== null && (
          <SummaryStat label="Final" value={scoring.final_score.toFixed(1)} highlight />
        )}
      </div>

      {(scoring.gates.length > 0 || scoring.caps.length > 0) && (
        <div className="sc-limits">
          <div className="sc-limits-title">What limited the score</div>
          <ul>
            {scoring.gates.map((g, i) => (
              <li key={`g${i}`} className="limit-gate">Hard gate: {g}</li>
            ))}
            {scoring.caps.map((c, i) => (
              <li key={`c${i}`}>{c}</li>
            ))}
          </ul>
        </div>
      )}

      <div className="sc-controls">
        <div className="sc-filters">
          {(["all", "failed", "passed"] as const).map((f) => (
            <button key={f} className={filter === f ? "sc-filter on" : "sc-filter"} onClick={() => setFilter(f)}>
              {f === "all" ? "All rules" : f === "failed" ? "Failed only" : "Passed only"}
            </button>
          ))}
        </div>
        <div className="sc-expand">
          <button className="linkish" onClick={expandAll}>Expand all</button>
          <button className="linkish" onClick={collapseAll}>Collapse</button>
        </div>
      </div>

      <div className="sc-cats">
        {categories.map((cat) => {
          const shown = cat.rules.filter((r) => visible(r.passed));
          const catPassed = cat.rules.filter((r) => r.passed === true).length;
          const catTotal = cat.rules.filter((r) => r.passed !== null).length;
          const pct = cat.max_score && cat.max_score > 0 && cat.score !== null
            ? (cat.score / cat.max_score) * 100
            : null;
          const isOpen = openCats.has(cat.category);
          if (shown.length === 0 && filter !== "all") return null;

          return (
            <div key={cat.category} className="sc-cat">
              <button className="sc-cat-head" onClick={() => toggle(cat.category)} aria-expanded={isOpen}>
                <span className="sc-caret">{isOpen ? "▾" : "▸"}</span>
                <span className="sc-cat-name">{cat.category}</span>
                <span className="sc-cat-count">{catPassed}/{catTotal}</span>
                <span className="sc-cat-bar">
                  <span
                    className="sc-cat-fill"
                    style={{
                      width: `${pct ?? 0}%`,
                      background: pct === null ? "var(--line)" : pct >= 75 ? "var(--accent)" : pct >= 40 ? "#d9a441" : "#e2574f",
                    }}
                  />
                </span>
                <span className="sc-cat-pts">
                  {cat.score !== null && cat.max_score !== null
                    ? `${cat.score.toFixed(1)} / ${cat.max_score.toFixed(1)}`
                    : "—"}
                </span>
              </button>

              {isOpen && (
                <ul className="sc-rules">
                  {shown.map((r, i) => (
                    <li key={i} className={r.passed === true ? "r-pass" : r.passed === false ? "r-fail" : "r-na"}>
                      <span className="r-mark">
                        {r.passed === true ? "✓" : r.passed === false ? "✕" : "–"}
                      </span>
                      <span className="r-name">{r.rule}</span>
                      {r.note && <span className="r-note">{r.note}</span>}
                    </li>
                  ))}
                </ul>
              )}
            </div>
          );
        })}
      </div>

      {scoring.graded_metrics.length > 0 && (
        <div className="sc-graded">
          <div className="sc-graded-title">Graded metrics</div>
          <div className="sc-graded-grid">
            {scoring.graded_metrics.map((g, i) => (
              <div key={i} className="graded-item">
                <span className="g-name">{g.metric}</span>
                <span className="g-val">{g.value !== null ? formatMetric(g.value) : "—"}</span>
                <span className="g-score">{g.score !== null ? g.score.toFixed(0) : "—"}</span>
              </div>
            ))}
          </div>
        </div>
      )}

      {(scoring.strengths.length > 0 || scoring.concerns.length > 0) && (
        <div className="sc-sc">
          {scoring.strengths.length > 0 && (
            <div className="sc-col">
              <div className="sc-col-title strong">Strengths</div>
              <ul>{scoring.strengths.map((s, i) => <li key={i}>{s}</li>)}</ul>
            </div>
          )}
          {scoring.concerns.length > 0 && (
            <div className="sc-col">
              <div className="sc-col-title weak">Concerns</div>
              <ul>{scoring.concerns.map((c, i) => <li key={i}>{c}</li>)}</ul>
            </div>
          )}
        </div>
      )}
    </div>
  );
}

function SummaryStat({ label, value, highlight }: { label: string; value: string; highlight?: boolean }) {
  return (
    <div className={highlight ? "sc-stat hl" : "sc-stat"}>
      <span className="sc-stat-label">{label}</span>
      <span className="sc-stat-value">{value}</span>
    </div>
  );
}

function formatMetric(v: number): string {
  if (Math.abs(v) < 1 && v !== 0) return `${(v * 100).toFixed(1)}%`;
  if (Math.abs(v) >= 1e9) return `${(v / 1e9).toFixed(1)}B`;
  if (Math.abs(v) >= 1e6) return `${(v / 1e6).toFixed(0)}M`;
  return v.toFixed(2);
}
