# Buffett Quality Screener

A Python screening engine that scores US-listed companies against a Buffett-style
quality-and-value framework, with full rule-level transparency, and publishes the
results to an interactive two-tab dashboard.

**Live dashboard:** https://oliverbilsland.github.io/Buffett-Screener/

> Educational research tool — **not** investment advice.

---

## The idea

Warren Buffett's investing rules are sound, but Berkshire's size forces it into
mega-caps. That leaves smaller, Buffett-quality companies (roughly $300M–$20B
market cap) as a space an individual investor can actually act on. This tool
automates the tedious part: it pulls a market universe, scores every company
against an explicit rule set, and ranks what survives — so the human can spend
their time on judgment (moat, management, price) instead of data gathering.

## What it does

- **Scans the full US universe** (~7,800 tickers from the SEC's own free file)
  and filters to the Buffett cap band before scoring, so a single run covers
  thousands of real candidates rather than a fixed index list.
- **Scores each company against 80 rules across 12 categories** (earning power,
  returns on capital, owner earnings, balance-sheet strength, accounting
  quality, capital allocation, valuation, and more).
- **Full transparency:** every company shows which rules passed, failed, or
  lacked data — no black box.
- **10-year financial history from SEC EDGAR,** reconciled against Yahoo Finance,
  so the fundamentals are audited rather than trusted blindly.
- **Industry-aware:** dedicated models for insurance, banks, and REITs, plus
  concentration flags for sectors like semiconductors and apparel.
- **Valuation as a cap, not a gate:** a great business at a bad price is flagged
  as exactly that, not silently rejected.
- **Market-climate overlay:** a Buffett-style read of the broad market (Buffett
  Indicator, forward P/E, interest-rate gravity, CAPE) that adjusts the required
  margin of safety without ever altering a company's underlying quality score.
  It answers "are the overall odds good, fair, or poor?" — deliberately **not**
  a market-timing model.

## The dashboard

Two tabs:

- **Stocks** — ranked cards scored by a market-adjusted score, with a **"Quality
  only"** toggle that re-ranks by pure business quality (ignoring price and
  market climate entirely), plus search, sorting, and tier filters. Click any
  card for the full rule-by-rule breakdown.
- **Market Climate** — a visual read of the current market: a regime dial, and
  cards for the Buffett Indicator, forward P/E, interest-rate gravity, and CAPE,
  each with a live value, a band meter showing where the market sits, and a
  click-to-expand explanation of the underlying Buffett rule.

## Running it

Requires Python 3 and: `yfinance pandas lxml requests` (plus `pytest` for tests).

```bash
pip install yfinance pandas lxml requests pytest
```

Full-universe scan in the Buffett cap band, with the market overlay, publishing
`index.html` for the site:

```bash
python buffett_screener_v15.py --universe full --too-small-for-buffett \
    --edgar-contact "you@example.com" \
    --market-forward-pe 22 --buffett-indicator-gnp 200 --treasury-10y 4.5 \
    --publish --resume
```

Score a specific handful of tickers:

```bash
python buffett_screener_v15.py --tickers AZO ORLY KO
```

Useful flags:

| Flag | Purpose |
|------|---------|
| `--universe full` | Every US-listed common stock on a major exchange (via SEC) |
| `--too-small-for-buffett` | Restrict to the $300M-$20B cap band |
| `--cap-min` / `--cap-max` | Custom cap band in dollars |
| `--resume` | Resume a long run; skips already-scored tickers |
| `--publish` | Also write the dashboard as index.html for GitHub Pages |
| `--tickers T1 T2 ...` | Score a specific list instead of the universe |
| `--edgar-contact "Name you@email.com"` | SEC fair-access identification |

Each run writes timestamped CSVs plus a self-contained dashboard HTML. With
`--publish` it also writes `index.html`, so the site can be updated with a plain
`git add -A && git commit && git push`.

## Testing

An offline test suite validates the market-overlay logic (no network calls):

```bash
python -m pytest tests_buffett_market_overlay.py -q
```

## Tech

Python · pandas · yfinance · SEC EDGAR API · lxml/requests · pytest · GitHub Pages

## Disclaimer

This is a personal research and learning project. It is **not** financial advice,
not a recommendation to buy or sell any security, and its outputs should not be
relied on for investment decisions. Data may be incomplete or inaccurate. Do your
own research and consult a licensed professional.
