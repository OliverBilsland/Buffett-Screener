"use client";

import { useState } from "react";
import { Leg, strategyPayoff, breakevens } from "@/lib/quant/options";

// Project 2 — Options Strategy Builder, client-side. Payoff and breakevens
// computed in the browser from the verified options module.

const PRESETS: Record<string, Leg[]> = {
  "Bull call spread": [
    { kind: "call", direction: "long", strike: 100, premium: 5 },
    { kind: "call", direction: "short", strike: 110, premium: 2 },
  ],
  "Long straddle": [
    { kind: "call", direction: "long", strike: 100, premium: 5 },
    { kind: "put", direction: "long", strike: 100, premium: 5 },
  ],
  "Covered call": [{ kind: "call", direction: "short", strike: 110, premium: 3 }],
};

export default function OptionsPage() {
  const [legs, setLegs] = useState<Leg[]>(PRESETS["Bull call spread"]);

  const spotMin = 80, spotMax = 130, steps = 100;
  const step = (spotMax - spotMin) / steps;
  const spots = Array.from({ length: steps + 1 }, (_, i) => spotMin + i * step);
  const payoff = strategyPayoff(legs, spots);
  const bes = breakevens(legs, spotMin, spotMax, Math.max(step, 0.01));

  const update = (i: number, patch: Partial<Leg>) => {
    const n = [...legs]; n[i] = { ...n[i], ...patch }; setLegs(n);
  };

  return (
    <div>
      <h1>Options strategy builder</h1>
      <p className="muted">Build a multi-leg position and see its profit and loss at expiry.</p>

      <div className="preset-row">
        {Object.keys(PRESETS).map((name) => (
          <button key={name} className="ghost" onClick={() => setLegs(PRESETS[name])}>{name}</button>
        ))}
      </div>

      {legs.map((leg, i) => (
        <div key={i} className="trade-row">
          <select value={leg.direction} onChange={(e) => update(i, { direction: e.target.value as "long" | "short" })}>
            <option value="long">long</option><option value="short">short</option>
          </select>
          <select value={leg.kind} onChange={(e) => update(i, { kind: e.target.value as "call" | "put" })}>
            <option value="call">call</option><option value="put">put</option>
          </select>
          <label className="inline-field">strike<input type="number" value={leg.strike} onChange={(e) => update(i, { strike: +e.target.value })} style={{ width: 80 }} /></label>
          <label className="inline-field">premium<input type="number" value={leg.premium} onChange={(e) => update(i, { premium: +e.target.value })} style={{ width: 80 }} /></label>
          <button className="icon-btn" aria-label="Remove leg" onClick={() => setLegs(legs.filter((_, j) => j !== i))}>✕</button>
        </div>
      ))}
      <button className="ghost" onClick={() => setLegs([...legs, { kind: "call", direction: "long", strike: 100, premium: 5 }])}>+ Add leg</button>

      <div className="result-grid" style={{ gridTemplateColumns: "1fr" }}>
        <div className="metric">
          <div className="metric-label">Breakeven price(s)</div>
          <div className="metric-value" style={{ fontSize: 18 }}>
            {bes.length ? bes.map((b) => `$${b.toFixed(2)}`).join(", ") : "none in range"}
          </div>
        </div>
      </div>

      <PayoffChart spots={spots} payoff={payoff} />
    </div>
  );
}

function PayoffChart({ spots, payoff }: { spots: number[]; payoff: number[] }) {
  const w = 600, h = 220, pad = 30;
  const minP = Math.min(...payoff), maxP = Math.max(...payoff);
  const x = (i: number) => pad + (i / (spots.length - 1)) * (w - 2 * pad);
  const y = (p: number) => h - pad - ((p - minP) / (maxP - minP || 1)) * (h - 2 * pad);
  const path = payoff.map((p, i) => `${i === 0 ? "M" : "L"} ${x(i).toFixed(1)} ${y(p).toFixed(1)}`).join(" ");
  return (
    <svg viewBox={`0 0 ${w} ${h}`} width="100%" role="img" aria-label="Option payoff at expiry" style={{ marginTop: 20 }}>
      <line x1={pad} y1={y(0)} x2={w - pad} y2={y(0)} stroke="var(--line)" strokeDasharray="4 4" />
      <path d={path} fill="none" stroke="var(--accent)" strokeWidth="2" />
      <text x={pad} y={h - 6} fontSize="11" fill="var(--muted)">${spots[0].toFixed(0)}</text>
      <text x={w - pad - 24} y={h - 6} fontSize="11" fill="var(--muted)">${spots[spots.length - 1].toFixed(0)}</text>
    </svg>
  );
}
