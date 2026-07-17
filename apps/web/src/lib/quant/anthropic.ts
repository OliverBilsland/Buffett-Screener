// Bring-your-own-key Anthropic client, called directly from the browser.
//
// SECURITY: the user's key is passed in per-call and held only in React state by
// the calling component. This module never persists it, never logs it, never
// sends it anywhere except Anthropic's API. No localStorage, no cookies.
//
// Uses the documented browser-access header so the call is allowed via CORS.

const ANTHROPIC_URL = "https://api.anthropic.com/v1/messages";
const MODEL = "claude-sonnet-4-6";

export type SummaryKind = "bull_bear" | "filing" | "news_digest" | "trade_review";

const SYSTEM_PROMPTS: Record<SummaryKind, string> = {
  bull_bear:
    'You are an equity analyst. Return ONLY valid JSON with keys: "bull_case" ' +
    '(array of strings), "bear_case" (array of strings), "summary" (string). ' +
    "Ground every point in the supplied text. Do not fabricate numbers. " +
    "This is analysis, not investment advice.",
  filing:
    'You analyze SEC filings. Return ONLY valid JSON with keys: "key_risks" ' +
    '(array), "growth_opportunities" (array), "financial_insights" (array), ' +
    '"summary" (string). Use ONLY information present in the provided text.',
  news_digest:
    'You summarize financial news. Return ONLY valid JSON with keys: ' +
    '"market_moving_events" (array of strings), "overall_sentiment" ' +
    '(one of "bullish","bearish","neutral"), "summary" (string).',
  trade_review:
    'You are a trading coach. Return ONLY valid JSON with keys: ' +
    '"execution_feedback" (array), "psychology_notes" (array), ' +
    '"risk_management" (array), "recurring_mistakes" (array), "summary" (string). ' +
    "Be constructive and honest; do not encourage reckless risk-taking.",
};

export class AnthropicError extends Error {}

export async function callAnthropic(
  apiKey: string,
  kind: SummaryKind,
  userText: string
): Promise<Record<string, unknown>> {
  if (!apiKey.trim()) throw new AnthropicError("Please enter your Anthropic API key.");
  if (!userText.trim()) throw new AnthropicError("Please enter some text to analyze.");

  let res: Response;
  try {
    res = await fetch(ANTHROPIC_URL, {
      method: "POST",
      headers: {
        "content-type": "application/json",
        "x-api-key": apiKey,
        "anthropic-version": "2023-06-01",
        // Required for direct browser calls (CORS). The user's own key is used.
        "anthropic-dangerous-direct-browser-access": "true",
      },
      body: JSON.stringify({
        model: MODEL,
        max_tokens: 2000,
        system: SYSTEM_PROMPTS[kind],
        messages: [{ role: "user", content: userText }],
      }),
    });
  } catch {
    throw new AnthropicError("Network error reaching Anthropic. Check your connection.");
  }

  if (!res.ok) {
    let detail = `Anthropic returned ${res.status}`;
    try {
      const err = await res.json();
      detail = err?.error?.message ?? detail;
    } catch { /* keep default */ }
    if (res.status === 401) detail = "Invalid API key. Check the key and try again.";
    throw new AnthropicError(detail);
  }

  const data = await res.json();
  const text: string = (data.content ?? [])
    .filter((b: { type?: string }) => b.type === "text")
    .map((b: { text?: string }) => b.text ?? "")
    .join("");

  const cleaned = text.trim().replace(/^```json/, "").replace(/^```/, "").replace(/```$/, "").trim();
  try {
    const parsed = JSON.parse(cleaned);
    if (typeof parsed !== "object" || parsed === null) {
      throw new AnthropicError("Model returned an unexpected format.");
    }
    return parsed as Record<string, unknown>;
  } catch {
    throw new AnthropicError("Could not parse the model's response. Try again.");
  }
}
