#!/usr/bin/env python3
"""Fetch the Market Climate inputs automatically (no API keys).

Replaces the hand-typed numbers in publish.bat / the workflow. Sources:

  10-year Treasury yield   FRED DGS10 (CSV, no key)
  3-month T-bill yield     FRED DTB3
  Buffett Indicator        Wilshire 5000 full-cap index level (Yahoo ^W5000,
                           ~$1B per point) / latest nominal GDP (FRED GDP),
                           in percent. Same approximation the FRED-based
                           Buffett Indicator charts use.
  Shiller CAPE             multpl.com (scraped; fragile, so falls back)
  S&P 500 drawdown         Yahoo ^GSPC close vs 52-week high, positive %
  Forward P/E              No free source. Taken from MARKET_FORWARD_PE
                           (env / repo variable) else a dated default below.

Every value falls back to the matching env var, then to the default, so a
dead source never blocks the run. Prints a shell-friendly summary and writes
the values to $GITHUB_OUTPUT when running in Actions.

Usage:  python scripts/fetch_market_inputs.py          (prints JSON)
"""
from __future__ import annotations

import io
import json
import os
import re
import sys
from datetime import date

import requests

# Updated by hand when it drifts materially. Checked 2026-10-16 (ycharts,
# S&P 500 forward P/E 21.1 as of 2026-09-30).
DEFAULTS = {
    "forward_pe": 21.1,
    "cape": None,
    "buffett_indicator_gdp": None,
    "treasury_10y": None,
    "tbill_3m": None,
    "sp500_drawdown": None,
}
ENV_OVERRIDES = {
    "forward_pe": "MARKET_FORWARD_PE",
    "cape": "MARKET_CAPE",
    "buffett_indicator_gdp": "BUFFETT_INDICATOR_GDP",
    "treasury_10y": "TREASURY_10Y",
    "tbill_3m": "TBILL_3M",
    "sp500_drawdown": "SP500_DRAWDOWN",
}
UA = {"User-Agent": "Mozilla/5.0 (BuffettScreener market-inputs; bilsland@bc.edu)"}


def _fred_latest(series: str) -> tuple[float, str]:
    url = f"https://fred.stlouisfed.org/graph/fredgraph.csv?id={series}"
    text = requests.get(url, timeout=30, headers=UA).text
    rows = [ln.split(",") for ln in text.strip().splitlines()[1:]]
    rows = [(d, v) for d, v in rows if v not in (".", "")]
    d, v = rows[-1]
    return float(v), d


def _yahoo_close_and_high(ticker: str) -> tuple[float, float, str]:
    import yfinance as yf
    h = yf.Ticker(ticker).history(period="1y")
    close = float(h["Close"].iloc[-1])
    high = float(h["Close"].max())
    return close, high, str(h.index[-1].date())


def _multpl(page: str) -> float:
    html = requests.get(f"https://www.multpl.com/{page}", timeout=30, headers=UA).text
    m = re.search(r'id="current".*?(\d+\.\d+)', html, re.S)
    if not m:
        raise ValueError("multpl layout changed")
    return float(m.group(1))


def main() -> int:
    out, notes = {}, {}

    def attempt(key, fn):
        try:
            val, note = fn()
            out[key] = round(val, 2)
            notes[key] = note
        except Exception as e:  # noqa: BLE001
            notes[key] = f"fetch failed ({e.__class__.__name__}); using fallback"

    attempt("treasury_10y", lambda: _fred_latest("DGS10"))
    attempt("tbill_3m", lambda: _fred_latest("DTB3"))
    attempt("cape", lambda: (_multpl("shiller-pe"), "multpl.com"))

    def _buffett():
        w5000, _, wdate = _yahoo_close_and_high("^W5000")
        gdp, gdate = _fred_latest("GDP")          # $bn, SAAR
        return 100.0 * w5000 / gdp, f"W5000 {w5000:,.0f} ({wdate}) / GDP {gdp:,.0f}bn ({gdate})"
    attempt("buffett_indicator_gdp", _buffett)

    def _drawdown():
        close, high, d = _yahoo_close_and_high("^GSPC")
        return 100.0 * (high - close) / high, f"S&P {close:,.0f} vs 52w high {high:,.0f} ({d})"
    attempt("sp500_drawdown", _drawdown)

    # Apply env overrides (repo variables win over fetched values when set),
    # then defaults for anything still missing.
    for key, env in ENV_OVERRIDES.items():
        v = os.environ.get(env, "").strip()
        if v:
            out[key] = float(v)
            notes[key] = f"override from ${env}"
        elif key not in out and DEFAULTS[key] is not None:
            out[key] = DEFAULTS[key]
            notes[key] = "default"

    print(json.dumps({"as_of": date.today().isoformat(), "values": out, "notes": notes}, indent=2))

    gh = os.environ.get("GITHUB_OUTPUT")
    if gh:
        with open(gh, "a") as fh:
            for k, v in out.items():
                fh.write(f"{k}={v}\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
