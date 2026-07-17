"use client";

import { useState } from "react";
import { callAnthropic, AnthropicError, SummaryKind } from "@/lib/quant/anthropic";
import { ApiKeyField } from "../ApiKeyField";

// Projects 1, 3, 7 — AI Research Hub, bring-your-own-key.
// The user's key is held in memory here only; see anthropic.ts for the call.

type Mode = Extract<SummaryKind, "bull_bear" | "filing" | "news_digest">;
const MODES: { id: Mode; label: string; hint: string }[] = [
  { id: "bull_bear", label: "Stock research", hint: "Bull and bear case from financials, filings, and news" },
  { id: "filing", label: "SEC filing", hint: "Risks, opportunities, and insights from a 10-K or 10-Q" },
  { id: "news_digest", label: "News digest", hint: "Market-moving events with sentiment" },
];

export default function ResearchPage() {
  const [apiKey, setApiKey] = useState("");
  const [mode, setMode] = useState<Mode>("bull_bear");
  const [text, setText] = useState("");
  const [result, setResult] = useState<Record<string, unknown> | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  const run = async () => {
    setLoading(true); setError(null); setResult(null);
    try {
      setResult(await callAnthropic(apiKey, mode, text));
    } catch (e) {
      setError(e instanceof AnthropicError ? e.message : "Something went wrong.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div>
      <h1>AI research hub</h1>
      <p className="muted">
        Analyze a stock, a filing, or the news. Optional — bring your own Anthropic
        key; the four core modules need no key at all.
      </p>

      <ApiKeyField value={apiKey} onChange={setApiKey} />

      <div className="mode-tabs">
        {MODES.map((m) => (
          <button key={m.id} className={m.id === mode ? "mode-tab active" : "mode-tab"}
            onClick={() => { setMode(m.id); setResult(null); setError(null); }}>
            {m.label}
          </button>
        ))}
      </div>
      <p className="muted small">{MODES.find((m) => m.id === mode)?.hint}</p>

      <textarea rows={8} value={text} onChange={(e) => setText(e.target.value)}
        placeholder={mode === "filing" ? "Paste 10-K / 10-Q text…" : mode === "news_digest" ? "Paste headlines and articles…" : "Paste financials, filing excerpts, and news…"} />

      <button onClick={run} disabled={loading}>{loading ? "Analyzing…" : "Analyze"}</button>

      {error && <div className="error-box">{error}</div>}
      {result && <ResultView result={result} />}
    </div>
  );
}

function ResultView({ result }: { result: Record<string, unknown> }) {
  return (
    <div className="research-output">
      {Object.entries(result).map(([key, value]) => (
        <div key={key} className="research-section">
          <div className="research-key">{key.replace(/_/g, " ")}</div>
          <div className="research-value">
            {Array.isArray(value) ? (
              <ul>{value.map((item, i) => <li key={i}>{typeof item === "object" ? JSON.stringify(item) : String(item)}</li>)}</ul>
            ) : String(value)}
          </div>
        </div>
      ))}
    </div>
  );
}
