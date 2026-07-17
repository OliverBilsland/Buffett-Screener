"use client";

import { useState } from "react";
import { callAnthropic, AnthropicError } from "@/lib/quant/anthropic";
import { ApiKeyField } from "../ApiKeyField";

// Project 10 — AI Trading Journal, bring-your-own-key.

interface Trade { ticker: string; side: "buy" | "sell"; quantity: number; price: number; thesis: string; }

export default function JournalPage() {
  const [apiKey, setApiKey] = useState("");
  const [trades, setTrades] = useState<Trade[]>([
    { ticker: "", side: "buy", quantity: 0, price: 0, thesis: "" },
  ]);
  const [result, setResult] = useState<Record<string, unknown> | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  const update = (i: number, patch: Partial<Trade>) => {
    const n = [...trades]; n[i] = { ...n[i], ...patch }; setTrades(n);
  };

  const review = async () => {
    const valid = trades.filter((t) => t.ticker.trim() && t.quantity > 0 && t.price > 0);
    if (!valid.length) { setError("Enter at least one trade with ticker, quantity, and price."); return; }
    const text = valid
      .map((t) => `${t.ticker} ${t.side} ${t.quantity} @ ${t.price}${t.thesis ? ` | thesis: ${t.thesis}` : ""}`)
      .join("\n");
    setLoading(true); setError(null); setResult(null);
    try {
      setResult(await callAnthropic(apiKey, "trade_review", text));
    } catch (e) {
      setError(e instanceof AnthropicError ? e.message : "Something went wrong.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div>
      <h1>AI trading journal</h1>
      <p className="muted">
        Log trades and get feedback on execution, psychology, risk, and recurring
        mistakes. Optional — bring your own Anthropic key.
      </p>

      <ApiKeyField value={apiKey} onChange={setApiKey} />

      {trades.map((t, i) => (
        <div key={i} className="trade-row">
          <input value={t.ticker} onChange={(e) => update(i, { ticker: e.target.value.toUpperCase() })} style={{ width: 90 }} placeholder="Ticker" />
          <select value={t.side} onChange={(e) => update(i, { side: e.target.value as "buy" | "sell" })}>
            <option value="buy">buy</option><option value="sell">sell</option>
          </select>
          <input type="number" value={t.quantity || ""} onChange={(e) => update(i, { quantity: +e.target.value })} style={{ width: 80 }} placeholder="Qty" />
          <input type="number" value={t.price || ""} onChange={(e) => update(i, { price: +e.target.value })} style={{ width: 90 }} placeholder="Price" />
          <input value={t.thesis} onChange={(e) => update(i, { thesis: e.target.value })} style={{ flex: 1, minWidth: 120 }} placeholder="Thesis (optional)" />
        </div>
      ))}

      <div className="journal-actions">
        <button className="ghost" onClick={() => setTrades([...trades, { ticker: "", side: "buy", quantity: 0, price: 0, thesis: "" }])}>+ Add trade</button>
        <button onClick={review} disabled={loading}>{loading ? "Reviewing…" : "Get feedback"}</button>
      </div>

      {error && <div className="error-box">{error}</div>}
      {result && (
        <div className="research-output">
          {Object.entries(result).map(([key, value]) => (
            <div key={key} className="research-section">
              <div className="research-key">{key.replace(/_/g, " ")}</div>
              <div className="research-value">
                {Array.isArray(value) ? <ul>{value.map((it, i) => <li key={i}>{typeof it === "object" ? JSON.stringify(it) : String(it)}</li>)}</ul> : String(value)}
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
