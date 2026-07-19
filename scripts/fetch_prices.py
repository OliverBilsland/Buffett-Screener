#!/usr/bin/env python3
"""Fetch real daily price history from Tiingo -> apps/web/public/prices.json

This restores real market data to the Portfolio module. It follows the same
offline-compute pattern as the Buffett screener: fetch once locally, ship a
static file, no backend or database needed at runtime.

USAGE (from the repo root, on a network that isn't blocking outbound calls):

    set PRICE_API_KEY=your_tiingo_token         (Windows CMD)
    $env:PRICE_API_KEY="your_tiingo_token"      (PowerShell)
    python scripts/fetch_prices.py

Optional: pass tickers to fetch instead of the default list:
    python scripts/fetch_prices.py AAPL MSFT NVDA

By default it fetches SPY (the benchmark, required for beta) plus a starter set.
Add whatever you actually hold. Tiingo's free tier covers ~50 symbols/hour, so
keep the list modest or run it in batches.

Output shape (what the web app expects):
    {
      "benchmark": "SPY",
      "as_of": "2026-07-18",
      "sectors": {"AAPL": "Tech", ...},
      "series":  {"AAPL": [adj_close, adj_close, ...], ...}   # oldest -> newest
    }
"""
from __future__ import annotations

import json
import os
import sys
import time
from datetime import date, timedelta
from pathlib import Path
from urllib.request import urlopen, Request
from urllib.error import HTTPError, URLError

# SPY must stay first — it's the benchmark beta is measured against.
DEFAULT_TICKERS = ["SPY", "AAPL", "MSFT", "JPM", "XOM", "UNH", "NVDA", "HNRG"]

# Rough sector labels for the exposure chart. Unknown tickers fall back to
# "Unknown", which the UI handles.
SECTORS = {
    "SPY": "Index", "AAPL": "Tech", "MSFT": "Tech", "NVDA": "Tech",
    "JPM": "Financials", "XOM": "Energy", "UNH": "Healthcare",
    "HNRG": "Energy",
}

LOOKBACK_DAYS = 730          # ~2 years of history
OUT_PATH = Path(__file__).resolve().parent.parent / "apps" / "web" / "public" / "prices.json"
TIINGO_URL = "https://api.tiingo.com/tiingo/daily/{t}/prices?startDate={s}&endDate={e}&token={k}"


def fetch(ticker: str, token: str, start: date, end: date) -> list[float]:
    """Return the adjusted-close series for one ticker, oldest first."""
    url = TIINGO_URL.format(t=ticker.lower(), s=start.isoformat(), e=end.isoformat(), k=token)
    req = Request(url, headers={"Content-Type": "application/json"})
    with urlopen(req, timeout=30) as resp:
        rows = json.loads(resp.read().decode())
    # adjClose (not close) — split/dividend adjusted, required for correct returns.
    bars = [(r["date"], float(r["adjClose"])) for r in rows if r.get("adjClose") is not None]
    bars.sort(key=lambda b: b[0])
    return [p for _, p in bars]


def main() -> None:
    token = os.environ.get("PRICE_API_KEY")
    if not token:
        print("PRICE_API_KEY not set. Get a free token at tiingo.com and set it:", file=sys.stderr)
        print('  PowerShell:  $env:PRICE_API_KEY="your_token"', file=sys.stderr)
        sys.exit(1)

    tickers = [t.upper() for t in sys.argv[1:]] or DEFAULT_TICKERS
    if "SPY" not in tickers:
        print("note: adding SPY — it's the benchmark beta is measured against.")
        tickers = ["SPY"] + tickers

    end = date.today()
    start = end - timedelta(days=LOOKBACK_DAYS)

    series: dict[str, list[float]] = {}
    failed: list[str] = []

    for i, t in enumerate(tickers):
        try:
            s = fetch(t, token, start, end)
            if len(s) < 2:
                print(f"  {t}: no usable data returned")
                failed.append(t)
                continue
            series[t] = s
            print(f"  {t}: {len(s)} daily bars")
        except HTTPError as e:
            body = e.read()[:120].decode(errors="replace")
            print(f"  {t}: HTTP {e.code} — {body}", file=sys.stderr)
            failed.append(t)
        except (URLError, TimeoutError) as e:
            print(f"  {t}: network error — {e}", file=sys.stderr)
            failed.append(t)
        # Be polite to the free tier.
        if i < len(tickers) - 1:
            time.sleep(0.4)

    if "SPY" not in series:
        print("\nSPY failed to load — beta can't be computed without a benchmark.", file=sys.stderr)
        print("Fix the SPY fetch before continuing.", file=sys.stderr)
        sys.exit(1)

    out = {
        "benchmark": "SPY",
        "as_of": end.isoformat(),
        "sectors": {t: SECTORS.get(t, "Unknown") for t in series},
        "series": series,
    }
    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(OUT_PATH, "w", encoding="utf-8") as f:
        json.dump(out, f, separators=(",", ":"))

    kb = OUT_PATH.stat().st_size / 1024
    print(f"\nWrote {OUT_PATH} ({kb:.0f} KB, {len(series)} tickers)")
    if failed:
        print(f"Failed: {', '.join(failed)}")
    print("Next: git add . && git commit -m 'refresh prices' && git push")


if __name__ == "__main__":
    main()
