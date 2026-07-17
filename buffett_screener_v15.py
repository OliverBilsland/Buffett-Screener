"""
Buffett Screener v15
-------------------
New in v15 (Buffett-style MARKET VALUATION OVERLAY — additive, non-destructive):
  - A market-wide regime module sits BESIDE the company score. It never
    changes final_score and never turns a great business into a bad one; it
    only says whether the market is offering good, fair, or poor odds and how
    much extra margin of safety to demand. This is NOT a timing model — it
    never says "sell everything".
  - MarketContext dataclass + analyze_market_context(): Buffett Indicator
    (GNP-preferred, GDP fallback), interest-rate gravity (10y / 3m T-bill vs
    market earnings yield), corporate-profit-share warning + optional forward-
    EPS haircut, forward-P/E empirical-return buckets, CAPE secondary overlay,
    and a drawdown / PANIC_OPPORTUNITY overlay. All thresholds labelled
    heuristic.
  - Regimes: FAT_PITCH / NORMAL / ELEVATED / EXPENSIVE / VERY_EXPENSIVE /
    PLAYING_WITH_FIRE / PANIC_OPPORTUNITY / MIXED_OR_INCOMPLETE_DATA, each with
    a suggested margin-of-safety add-on.
  - CLI: --market-forward-pe --market-cape --buffett-indicator-gnp
    --buffett-indicator-gdp --treasury-10y --tbill-3m --corporate-profit-share
    --sp500-drawdown --market-adjust-scores --no-market-overlay. No live data
    required; all inputs are manual and optional. Missing inputs =>
    MIXED_OR_INCOMPLETE_DATA, never a crash.
  - market_adjusted_score (only with --market-adjust-scores): a MILD overlay,
    max(0, final_score - penalty + panic_bonus). Penalty is reduced 25-50% for
    ATTRACTIVE + high-owner-earnings-yield names, never reduced for names that
    are already VERY EXPENSIVE on their own. Never touches reliability/data
    grades. final_score is left completely unchanged.
  - Market climate printed once at the top of the console run; market fields
    added to summary CSV, detailed CSV, and the dashboard (new "Market Climate"
    card + per-stock market rows). --no-market-overlay preserves exact v14
    behaviour.
  - Tests: tests_buffett_market_overlay.py (offline, hard-coded contexts).

(v14 notes)
-------------------
New in v14 (post-474-name-run calibration):
  - Special-industry valuation labels name the right module ("See insurance
    valuation", not "see bank valuation" on an insurer).
  - Insurance module deepened to 9 checks (combined-ratio proxy, expense
    ratio, underwriting profitability, cycle-peak test, equity/assets,
    dilution discipline) — 100/100 insurers should now be rare; 10-K scan
    adds reserve-development and catastrophe language caps.
  - Tier 1 split into 1A (normal compounders), 1B (capped/cyclical but
    high quality), 1C (strong special models).
  - "BEST NORMAL-COMPANY RESEARCH CANDIDATES" bucket: excludes financials,
    biotech, commodity, and heavy cyclicals by default.
  - concentration_review flag for semis, healthcare platforms, apparel/
    footwear: customer-concentration diligence pinned to the top of the
    manual-review list (CRUS/DOCS/DECK pattern).
  - Readable console summary: only names within reach of investable
    (>=80 or Tier 1/2) are printed; the rest are counted and left to the
    CSV/dashboard. Dilution hard-gate logic UNCHANGED from v12.

(v13 notes)
-------------------
New in v13:
  - HTML DASHBOARD: every run now also writes buffett_dashboard_TIMESTAMP.html
    — a single self-contained file (no server, no internet, works from
    Downloads). Tier filters, live search, sortable columns, expandable
    per-stock detail cards with caps/gates/warnings/manual-review, and the
    share-count reconciliation. Drop the file on GitHub Pages / Netlify and
    it IS a website. --no-dashboard to skip.

(v12 notes)
-------------------
New in v12 (surgical: share-count reliability & dilution-gate precision):
  - The dilution HARD GATE now requires EVIDENCE. Split-adjusted share CAGR
    > 5%/yr alone is not enough: the cash-flow statement must corroborate
    (issuance proceeds, or economically massive SBC). Extreme "dilution"
    (>15%/yr) needs extreme evidence (issuance > 15% of mcap or SBC > 15%
    of revenue).
  - Buyback contradiction: if the company is a NET REPURCHASER while the
    share series shows growth, the series is a DATA ARTIFACT — suppressed,
    capped 85, "verify manually". (Fixes GGG: 3.4% gross buyback yield with
    a claimed 62.8%/yr dilution is a data error, not economics.)
  - dilution_evidence_level (none/weak/moderate/strong) and
    dilution_hard_gate_allowed on every stock, plus a full share-count
    reconciliation table (begin/end shares raw & adjusted, buybacks,
    issuance, SBC) in debug output and CSV.
  - Console summary gains a "SHARE-COUNT ARTIFACTS TO VERIFY" section.
  - No other scoring changes: v11 interpretation is untouched.

(v11 notes)
-------------------
New in v11 (calibration pass — interpretation, not stricter math):
  - Verdict ladder: 85-89.9 = QUALITY COMPOUNDER WATCHLIST (FDS at 88.5 is
    no longer lumped with 70-point names); 80-84.9 = QUALITY BUT CAPPED.
  - research_queue Tiers 1-5 and valuation_label (ATTRACTIVE/FAIR/EXPENSIVE/
    VERY EXPENSIVE/NOT MEANINGFUL FOR INDUSTRY) as separate fields.
  - Concerns now print FAILURE wording ("Gross margin below 40%"), never the
    raw positive rule label ("Gross margin > 40%").
  - Share-count corroboration: extreme adjusted share CAGR (>15%/yr) must be
    supported by issuance cash / SBC; otherwise it is a DATA ARTIFACT —
    suppressed + capped 85, never a hard gate (fixes GGG/TSCO false rejects).
  - Valuation NEVER hard-rejects: the reverse-DCF gate is now a cap; great-
    but-expensive names land in QUALITY BUT EXPENSIVE / "GREAT BUSINESS,
    BAD PRICE", not REJECT (fixes KO/COST).
  - Negative equity classified by CAUSE (buybacks / operating losses / debt /
    unknown): buyback-driven negative equity with strong coverage and FCF
    caps at 80 instead of 75, and the debt-funded-buyback hard gate only
    fires when interest coverage is actually weak (fixes AZO/ORLY).
  - Final console summary: Tier-1 research names, capped-quality,
    special models, expensive-quality, rejects, and data-artifact warnings.

(v10 notes)
-------------------
New in v10 (precision, not more rules):
  - Row-criticality classification (critical / important / noncritical).
    Reconciliation consequences now match the row: a Net PPE mismatch on a
    capital-light business warns and suppresses the one affected rule — it
    no longer blanket-caps the company at 75.
  - Resolved stock splits vanish: high-confidence split adjustment removes
    the dilution gate entirely (no "suppressed gate", no artifact cap).
    Only UNRESOLVED suspected splits still cap at 85.
  - Bank valuation done properly: generic FCF/OE/DCF/EV valuation caps are
    suppressed for financials and replaced with P/B, P/TBV, P/E, ROA, ROE,
    and normalized (5yr-median) earnings yield, shown separately.
  - Console output distinguishes: missing data (?), industry-irrelevant (—),
    data artifact (!), and economic failure (x). Data warnings and economic
    concerns are separate sections.
  - model_reliability_grade A-F on every stock: how much you can trust the
    score itself, independent of how good the business looks.

(v9 notes)
-------------------
HONESTY NOTES (read first):
  * NOT investment advice. Scores are for idea generation only.
  * Manual 10-K review is ALWAYS required before any decision.
  * Free data (Yahoo/EDGAR/Stooq) has gaps, lags, and label quirks.
  * The 10-K scan is best-effort regex, not comprehension.
  * Owner earnings and DCF values are estimates, not truths.
  * Special industries need custom analysis; the modules are proxies.
  * No model can judge moat durability, management, or disruption.

New in v9 (conservative but never stupid):
  - STOCK SPLITS FIXED: share counts split-adjusted before any dilution
    rule, cap, or hard gate; raw-vs-adjusted CAGRs both reported; suspected
    unadjustable splits become an 85-cap warning, never a rejection.
  - Buyback quality: gross/net buyback yield, effectiveness per dollar,
    SBC leakage, debt-funded severity, capital-allocation letter grade.
  - TenKScanner: patent MATERIALITY tiers (boilerplate/moderate/material/
    critical) — boilerplate patent language never caps; supplier & product
    concentration; going-concern, material-weakness, restatement, auditor-
    change, litigation, restructuring, impairment flags.
  - EDGAR/Yahoo reconciliation: >20% mismatch warns, >50% marks the row
    unreliable and SUPPRESSES any hard gate built on it (cap 85 + verify).
  - Graded scoring: 23 key metrics scored on curves (no 3.9%-fails/4.1%-
    passes cliffs); final raw = 40% binary rules + 60% graded.
  - Special industries: economically-invalid generic rules EXCLUDED for
    financials (not failed, not missing); blended score = 70% module + 30%
    generic when module confidence >= 70; specials never plain COMPOUNDER
    unless --allow-special-compounders.
  - Valuation V2: normalized mid-cycle FCF, base/bear conservative DCF,
    margin-of-safety caps, valuation-percentile caps.
  - Confidence V2: 9-component breakdown (rules, history, source,
    reconciliation, industry, scan, per-share, valuation, module).
  - Moat proxy sub-scores with explicit "manual review always required".
  - Outputs: summary + detailed + per-rule AUDIT CSVs (timestamped);
    --calibration-demo runs a 36-name benchmark with expectations.

(v8 notes)
-------------------
New in v8 (false-positive control):
  - Data-quality caps: low confidence, short history (<5yr/<7yr), synthetic
    data, or unknown sector all cap the score. Missing data now HURTS.
  - Strict verdict bands: 90+ only for COMPOUNDER; 80-89 can only be
    QUALITY BUT CAPPED / EXPENSIVE / WATCHLIST; specials never compounders.
  - Conservative owner earnings: min(classic OE, FCF); per-share OE;
    reverse DCF and OE yields use the LOWER estimate.
  - Valuation vs own history: yearly P/E from Stooq prices + merged
    statements; >1.5x own median caps 85, >2x caps 80.
  - --scan-10k: regex-scans the latest 10-K for customer concentration
    (largest customer %, >=10% customers), single-product and patent-cliff
    language; caps applied per findings. Best-effort text mining.
  - 8 industry modules: banks, insurers, asset mgrs/cap mkts, software,
    retail/apparel, healthcare/CRO, commodity, industrials/cyclicals.
    Any module >=70/100 relaxes an industry cap to 90 (never ELITE).
  - manual_review_required field on every stock, in console and CSV.
  - Companion pytest suite: tests_buffett_v8.py (offline fixtures).

(v7 notes)
-------------------
New in v7:
  - SEC EDGAR integration (free, official): pulls up to ~10 years of annual
    10-K fundamentals from data.sec.gov and merges them into the statement
    tables. Every "every year" / CAGR / volatility / worst-decline rule now
    runs over a real cycle instead of Yahoo's ~4 years. Falls back silently
    to Yahoo-only if EDGAR is unavailable. --no-edgar to disable.
  - Industry sub-modules: banks, insurers, and software get their own
    checklists (ROA, efficiency ratio, deposit growth, equity/assets;
    premium growth, loss ratio, BVPS compounding; SBC discipline, deferred
    revenue, R&D intensity, gross margin). A special-model stock whose
    module scores >= 70/100 has its cap relaxed from 75-80 to 90 (still
    never ELITE). Module sub-score shown in debug and exported to CSV.
  - history_years column: how many years of statements actually backed
    the analysis for each ticker.
New in v6 (major expansion toward the full professional spec):
  - 80 rules across 12 weighted categories (added Working Capital Quality
    and Cyclicality/Downside Risk; expanded every other category)
  - Owner earnings engine: maintenance-capex estimate, OE yield, OE margin
  - Reverse DCF: implied growth rate from current price; gate if extreme
  - Negative shareholders' equity detection (cap 75 + flag; ROE never
    silently skipped again)
  - Expanded hard gates: persistent negative CFO, cumulative OE negative,
    debt-funded buybacks while leverage rises, reverse-DCF > 20%
  - Expanded industry caps: BPO/IT services, personal services/tax prep,
    CROs, healthcare services, hotels/casinos, utilities, specialty finance
  - Data-confidence score (0-100, % of rules evaluable)
  - Much stricter ELITE: requires no caps of ANY kind, no gates, full data
    on balance sheet & returns, confidence >= 90
  - Key strengths / key concerns summary per stock
  - Enriched CSVs: EV, OE yield, FCF yield, ROIC, ND/EBITDA, coverage,
    FCF conversion, revenue/FCF/share CAGRs, positive FCF/EBIT year counts

HONESTY NOTE: free Yahoo data = ~4 years of statements. All "10-year"
tests in the spec run over the full available history instead. Customer/
product concentration, restatements, retention, and peer medians are not
in free data — those stay manual (10-K) and ELITE is deliberately hard
to reach without them.

40 financial tests -> 10 weighted category scores -> hard fails -> score
caps -> industry overrides -> final Buffett-style verdict.

Design goal (per Buffett's actual framework): KILL FALSE POSITIVES.
A stock cannot score high just by passing many rules; leverage, dilution,
weak cash conversion, peak-cycle margins, accounting quality, and
industry type all cap the score.

HONESTY NOTE: free Yahoo data = ~4 years of statements, no peer medians,
no customer-concentration or retention data, no restatement flags.
Those tests (and DCF/moat judgment) must stay manual via the 10-K.
This model implements every test that IS computable from free data,
including Piotroski F-score, Altman Z-score, and accrual quality.

Verdict tiers:
  ELITE COMPOUNDER CANDIDATE  (95-100, no caps, valuation+leverage+accounting pass)
  COMPOUNDER CANDIDATE        (90-94)
  QUALITY BUT CAPPED          (80-89, a risk cap limited the score)
  QUALITY BUT EXPENSIVE       (80+ on quality, weak valuation category)
  SPECIAL MODEL REQUIRED      (banks/insurers/asset mgrs/REITs/biotech)
  WATCHLIST ONLY              (60-79)
  REJECT                      (<60 or hard gate)

Usage:
    pip install yfinance pandas lxml requests
    python buffett_screener.py --too-small-for-buffett --top 15
    python buffett_screener.py --sector Energy --top 15
    python buffett_screener.py --tickers KO AAPL --debug
    python buffett_screener.py --tickers DECK FDS CRUS --debug --sleep 2 --no-cache

Educational tool only. Not financial advice.
"""

import argparse
import io
import os
import pickle
import sys
import time
import math
from datetime import datetime
from pathlib import Path
from dataclasses import dataclass, field, asdict

# Force UTF-8 console output. On Windows the default console encoding (cp1252)
# cannot print characters like em-dashes or math symbols and will crash a run
# at print time. Reconfiguring stdout/stderr to UTF-8 (with backslash-escape
# fallback) makes every print safe regardless of the OS console codepage.
for _stream in (sys.stdout, sys.stderr):
    try:
        _stream.reconfigure(encoding="utf-8", errors="backslashreplace")
    except Exception:
        pass

import requests
import pandas as pd

try:
    import yfinance as yf
except ImportError:
    sys.exit("Run: pip install yfinance pandas lxml requests")

# ============================================================================
# v15 MARKET VALUATION OVERLAY (Buffett-style, additive & non-destructive)
# ----------------------------------------------------------------------------
# This module analyses the *market climate*, not any single company. It never
# alters final_score. It only expresses whether the broad market is offering
# good, fair, or poor odds, and how much extra margin of safety a Buffett-style
# investor should demand. It is NOT a timing model and never says "sell".
# All thresholds below are explicitly HEURISTIC — Buffett himself said his
# ratio has limitations. Treat every number as a guide, not a truth.
# ============================================================================


@dataclass
class MarketContext:
    """Manual (or optionally fetched) snapshot of broad-market valuation.

    Every field is optional. Missing fields never crash the screener; they
    simply reduce how much the overlay can say (=> MIXED_OR_INCOMPLETE_DATA).
    """
    sp500_forward_pe: float = None
    market_cape: float = None
    buffett_indicator_gnp: float = None      # total US equity mkt value / GNP, in %
    buffett_indicator_gdp: float = None      # fallback: / GDP, in %
    treasury_10y: float = None               # 10-year Treasury yield, in %
    tbill_3m: float = None                   # 3-month T-bill yield, in %
    corporate_profit_share_pct: float = None # corp profits / GDP (or GDI), in %
    sp500_drawdown_from_high_pct: float = None  # positive number, e.g. 22 = -22%
    data_source_notes: str = ""
    market_data_reliability: str = "manual-input"


# --- Heuristic bucket tables (all labelled heuristic, not precise) ----------

def _buffett_indicator_bucket(pct):
    """Buffett Indicator regime from market-cap/GNP(or GDP), in percent."""
    if pct is None:
        return None
    if pct <= 80:
        return "FAT_PITCH"
    if pct <= 110:
        return "NORMAL"
    if pct <= 135:
        return "ELEVATED"
    if pct <= 170:
        return "EXPENSIVE"
    if pct <= 200:
        return "VERY_EXPENSIVE"
    return "PLAYING_WITH_FIRE"


def _forward_pe_bucket(fpe):
    """Empirical forward-P/E bucket. Around 22-24x, expected 10yr S&P returns
    are flagged roughly flat / low-single-digit — NOT predicted precisely."""
    if fpe is None:
        return None
    if fpe < 14:
        return "attractive"
    if fpe < 18:
        return "normal/fair"
    if fpe < 20:
        return "elevated"
    if fpe < 22:
        return "expensive"
    if fpe < 24:
        return "flat-return-zone"
    return "extreme-low-return-zone"


def _cape_bucket(cape):
    """Shiller CAPE — SECONDARY confirmation only. Not Buffett's own indicator."""
    if cape is None:
        return None
    if cape < 15:
        return "attractive"
    if cape < 25:
        return "normal/elevated"
    if cape < 35:
        return "expensive"
    return "historically-stretched"


# Ordering of regimes from cheapest to most expensive, used to blend signals.
_REGIME_ORDER = [
    "FAT_PITCH", "NORMAL", "ELEVATED", "EXPENSIVE",
    "VERY_EXPENSIVE", "PLAYING_WITH_FIRE",
]

# Suggested margin-of-safety add-on by regime (percentage points).
_MOS_ADDON = {
    "FAT_PITCH": -5,           # range -5% to 0%
    "NORMAL": 0,
    "ELEVATED": 5,
    "EXPENSIVE": 10,
    "VERY_EXPENSIVE": 15,
    "PLAYING_WITH_FIRE": 20,
    "PANIC_OPPORTUNITY": -8,   # range -5% to -10%, only if no longer expensive
    "MIXED_OR_INCOMPLETE_DATA": 0,
}

# Score penalty by regime for market_adjusted_score (mild overlay).
_MARKET_PENALTY = {
    "FAT_PITCH": 0,
    "NORMAL": 0,
    "ELEVATED": 2,
    "EXPENSIVE": 4,
    "VERY_EXPENSIVE": 7,
    "PLAYING_WITH_FIRE": 10,
    "PANIC_OPPORTUNITY": 0,
    "MIXED_OR_INCOMPLETE_DATA": 0,
}


def _forward_pe_regime(bucket):
    """Map the forward-P/E bucket onto the shared regime scale."""
    return {
        "attractive": "FAT_PITCH",
        "normal/fair": "NORMAL",
        "elevated": "ELEVATED",
        "expensive": "EXPENSIVE",
        "flat-return-zone": "VERY_EXPENSIVE",
        "extreme-low-return-zone": "PLAYING_WITH_FIRE",
    }.get(bucket)


def _cape_regime(bucket):
    return {
        "attractive": "FAT_PITCH",
        "normal/elevated": "ELEVATED",
        "expensive": "EXPENSIVE",
        "historically-stretched": "VERY_EXPENSIVE",
    }.get(bucket)


def analyze_market_context(ctx: MarketContext) -> dict:
    """Turn a MarketContext into a market-regime read-out.

    Returns a dict with the regime, a 0-100 market score (higher = better odds
    for the buyer), individual metric buckets, interest-rate-gravity read,
    profit-share warning, suggested MOS add-on, a plain-English positioning
    sentence, and reliability. Never raises on missing data.
    """
    notes = []
    reliability = ctx.market_data_reliability or "manual-input"

    # --- individual metric buckets ---
    bi_pct = ctx.buffett_indicator_gnp
    bi_source = "GNP"
    if bi_pct is None:
        bi_pct = ctx.buffett_indicator_gdp
        bi_source = "GDP"
    bi_bucket = _buffett_indicator_bucket(bi_pct)
    if bi_bucket:
        notes.append(f"Buffett Indicator ({bi_source}) {bi_pct:.0f}% "
                     f"=> {bi_bucket} (heuristic).")

    fpe_bucket = _forward_pe_bucket(ctx.sp500_forward_pe)
    if fpe_bucket:
        note = f"S&P 500 forward P/E {ctx.sp500_forward_pe:.1f}x => {fpe_bucket}."
        if fpe_bucket in ("flat-return-zone", "extreme-low-return-zone"):
            note += (" Expected 10yr annualized returns roughly flat / low-"
                     "single-digit — flagged, not precisely predicted.")
        notes.append(note)

    cape_bucket = _cape_bucket(ctx.market_cape)
    if cape_bucket:
        notes.append(f"CAPE {ctx.market_cape:.0f} => {cape_bucket} "
                     f"(secondary confirmation only).")

    # --- interest-rate gravity ---
    market_ey = None
    spread_10y = None
    spread_tbill = None
    ir_label = None
    if ctx.sp500_forward_pe and ctx.sp500_forward_pe > 0:
        market_ey = 1.0 / ctx.sp500_forward_pe
    if market_ey is not None and ctx.treasury_10y is not None:
        spread_10y = market_ey - ctx.treasury_10y / 100.0
    if market_ey is not None and ctx.tbill_3m is not None:
        spread_tbill = market_ey - ctx.tbill_3m / 100.0

    if spread_10y is not None:
        if spread_10y <= 0:
            ir_label = "bonds win: equity earnings yield below the 10y"
            notes.append("Equity earnings yield is at or below the 10-year "
                         "Treasury — bond gravity is strong; demand more MOS.")
        elif spread_10y < 0.01:
            ir_label = "narrow equity premium over bonds"
            notes.append("Thin equity-risk premium over the 10-year; raise "
                         "required margin of safety.")
        else:
            ir_label = "healthy equity premium over bonds"
    if spread_tbill is not None and market_ey is not None:
        if spread_tbill <= 0.005:
            notes.append("Cash / T-bills are competitive with the market "
                         "earnings yield — cash has optionality.")
            if ir_label:
                ir_label += "; cash has optionality"
            else:
                ir_label = "cash has optionality"

    # --- corporate profit share ---
    profit_warning = False
    eps_haircut = "none"
    ps = ctx.corporate_profit_share_pct
    if ps is not None:
        # Historical US corp-profits/GDP has typically sat ~8-10%; >~11-12% is
        # top-decile territory. Heuristic bands, not a precise z-score.
        if ps >= 13:
            profit_warning = True
            eps_haircut = "15%"
            notes.append(f"Corporate profit share {ps:.1f}% is EXTREME — "
                         f"haircut forward-EPS optimism ~15% (market context "
                         f"only, not applied to company financials).")
        elif ps >= 12:
            profit_warning = True
            eps_haircut = "10%"
            notes.append(f"Corporate profit share {ps:.1f}% is very elevated "
                         f"— haircut forward EPS ~10% (market context only).")
        elif ps >= 11:
            profit_warning = True
            eps_haircut = "5%"
            notes.append(f"Corporate profit share {ps:.1f}% is elevated — "
                         f"haircut forward EPS ~5% (market context only).")

    # --- blend regime from available expensive-ness signals ---
    regime_signals = [r for r in (
        bi_bucket,
        _forward_pe_regime(fpe_bucket),
        _cape_regime(cape_bucket),
    ) if r]

    have_any = bool(regime_signals) or ir_label is not None or profit_warning

    if not regime_signals:
        regime = "MIXED_OR_INCOMPLETE_DATA"
        if not have_any:
            notes.append("No market valuation inputs supplied — overlay is "
                         "informational only (MIXED_OR_INCOMPLETE_DATA).")
        else:
            notes.append("Insufficient valuation inputs for a firm regime; "
                         "returning MIXED_OR_INCOMPLETE_DATA.")
    else:
        # Take the most expensive signal (conservative / Buffett-cautious),
        # but require Buffett Indicator OR forward P/E to anchor an extreme.
        idx = max(_REGIME_ORDER.index(r) for r in regime_signals)
        regime = _REGIME_ORDER[idx]

    # --- drawdown / panic overlay ---
    dd = ctx.sp500_drawdown_from_high_pct
    still_expensive = regime in ("VERY_EXPENSIVE", "PLAYING_WITH_FIRE")
    if dd is not None and regime != "MIXED_OR_INCOMPLETE_DATA":
        if dd >= 30 and not still_expensive:
            notes.append(f"Drawdown {dd:.0f}% with valuations no longer "
                         f"extreme => dislocation candidate environment.")
            regime = "PANIC_OPPORTUNITY"
        elif dd > 20 and not still_expensive:
            notes.append(f"Drawdown {dd:.0f}% and valuation metrics improved "
                         f"=> panic opportunity; MOS requirement eased slightly.")
            regime = "PANIC_OPPORTUNITY"
        elif dd > 20 and still_expensive:
            notes.append(f"Drawdown {dd:.0f}% but valuation remains extreme — "
                         f"keep caution, not a dislocation buy yet.")

    # --- suggested MOS add-on ---
    mos_addon = _MOS_ADDON.get(regime, 0)
    # Bond gravity nudges the MOS requirement up even within a regime.
    if spread_10y is not None and spread_10y <= 0 and regime not in (
            "PANIC_OPPORTUNITY", "MIXED_OR_INCOMPLETE_DATA"):
        mos_addon += 3
        notes.append("Bond gravity add-on: +3% MOS (equity yield <= 10y).")

    # --- 0-100 market score (buyer's odds) ---
    if regime == "MIXED_OR_INCOMPLETE_DATA":
        market_score = None
    else:
        base = {
            "FAT_PITCH": 90, "NORMAL": 72, "ELEVATED": 58,
            "EXPENSIVE": 42, "VERY_EXPENSIVE": 28, "PLAYING_WITH_FIRE": 15,
            "PANIC_OPPORTUNITY": 80,
        }.get(regime, 50)
        if spread_10y is not None and spread_10y <= 0:
            base -= 5
        if profit_warning:
            base -= 4
        market_score = max(0, min(100, base))

    # --- positioning sentence ---
    positioning = {
        "FAT_PITCH": "Broad market is offering good odds — be more aggressive, "
                     "but still demand quality.",
        "NORMAL": "Fair odds — normal margin of safety; pick spots.",
        "ELEVATED": "Slightly poor odds — demand a bit more margin of safety.",
        "EXPENSIVE": "Poor odds — require a larger margin of safety; smaller "
                     "starting positions.",
        "VERY_EXPENSIVE": "Poor odds — insist on a big margin of safety; "
                          "great business is not the same as a good price here.",
        "PLAYING_WITH_FIRE": "Very poor odds broadly — only exceptional "
                             "bargains; keep dry powder, do not chase.",
        "PANIC_OPPORTUNITY": "Dislocation — better odds for the patient buyer "
                             "of quality; size up selectively, not blindly.",
        "MIXED_OR_INCOMPLETE_DATA": "Not enough market data to judge odds — "
                                    "run company analysis on its own merits.",
    }[regime]

    return {
        "market_regime": regime,
        "market_score_0_100": market_score,
        "market_forward_pe": ctx.sp500_forward_pe,
        "market_forward_pe_bucket": fpe_bucket,
        "buffett_indicator_gnp": ctx.buffett_indicator_gnp,
        "buffett_indicator_gdp": ctx.buffett_indicator_gdp,
        "buffett_indicator_bucket": bi_bucket,
        "market_cape": ctx.market_cape,
        "cape_bucket": cape_bucket,
        "treasury_10y": ctx.treasury_10y,
        "tbill_3m": ctx.tbill_3m,
        "market_earnings_yield": market_ey,
        "equity_yield_spread_vs_10y": spread_10y,
        "equity_yield_spread_vs_tbill": spread_tbill,
        "interest_rate_gravity_label": ir_label,
        "corporate_profit_share_pct": ps,
        "profit_share_warning": profit_warning,
        "forward_eps_haircut": eps_haircut,
        "suggested_margin_of_safety_addon_pct": mos_addon,
        "market_positioning": positioning,
        "market_notes": notes,
        "market_data_reliability": reliability,
    }


def market_adjusted_score(final_score, stock_result, market):
    """MILD overlay. Returns max(0, final_score - penalty + panic_bonus).

    - Never changes final_score itself.
    - Penalty reduced 25-50% for ATTRACTIVE + high owner-earnings-yield names.
    - Penalty never reduced for names already VERY EXPENSIVE on their own.
    - Panic environments add a small bonus.
    Data-quality / reliability grades are untouched by design.
    """
    if final_score is None or market is None:
        return final_score
    regime = market["market_regime"]
    penalty = _MARKET_PENALTY.get(regime, 0)

    val_label = (stock_result.get("valuation_label") or "").upper()
    oey = (stock_result.get("key") or {}).get("oe_yield")

    if penalty and "VERY EXPENSIVE" not in val_label:
        if val_label.startswith("ATTRACTIVE"):
            # cheap + high owner-earnings yield => bigger discount on penalty
            if oey is not None and oey >= 0.06:
                penalty *= 0.5
            elif oey is not None and oey >= 0.045:
                penalty *= 0.75
            else:
                penalty *= 0.75

    panic_bonus = 3 if regime == "PANIC_OPPORTUNITY" else 0
    return round(max(0.0, final_score - penalty + panic_bonus), 1)


# ============================================================================
# Data helpers
# ============================================================================

def _safe(v):
    return v if isinstance(v, (int, float)) and not (isinstance(v, float) and math.isnan(v)) else None

def _row(df, *names):
    if df is None or df.empty:
        return None
    for n in names:
        if n in df.index:
            s = df.loc[n].dropna()
            if len(s):
                return [float(x) for x in s.values[::-1]]  # oldest -> newest
    return None


CACHE_DIR = Path(".buffett_cache")
CACHE_MAX_AGE_HOURS = 24
USE_CACHE = True  # overridden by --no-cache


def _cache_path(ticker):
    return CACHE_DIR / f"{ticker.upper().replace('/', '-')}.pkl"


def _load_cache(ticker):
    if not USE_CACHE:
        return None
    p = _cache_path(ticker)
    if not p.exists():
        return None
    age_hours = (time.time() - p.stat().st_mtime) / 3600
    if age_hours > CACHE_MAX_AGE_HOURS:
        return None
    try:
        with open(p, "rb") as f:
            return pickle.load(f)
    except Exception:
        return None


def _save_cache(ticker, payload):
    if not USE_CACHE:
        return
    try:
        CACHE_DIR.mkdir(exist_ok=True)
        with open(_cache_path(ticker), "wb") as f:
            pickle.dump(payload, f)
    except Exception:
        pass  # cache failures should never kill a run


# ============================================================================
# SEC EDGAR: up to ~10 years of annual 10-K fundamentals (free, official)
# ============================================================================

USE_EDGAR = True   # overridden by --no-edgar
# SEC requires a User-Agent identifying you with a contact address; anonymous
# UAs get 403'd. Override with --edgar-contact "Your Name your@email.com".
EDGAR_UA = "BuffettScreener/15.0 personal-research obilsla@example.com"
_EDGAR_WARNED = False

# canonical statement row  ->  ordered list of us-gaap XBRL tags to try
EDGAR_INC_TAGS = {
    "Total Revenue": ["Revenues", "RevenueFromContractWithCustomerExcludingAssessedTax",
                      "SalesRevenueNet", "RevenueFromContractWithCustomerIncludingAssessedTax"],
    "Net Income": ["NetIncomeLoss"],
    "Operating Income": ["OperatingIncomeLoss"],
    "EBIT": ["OperatingIncomeLoss"],
    "Gross Profit": ["GrossProfit"],
    "Interest Expense": ["InterestExpense", "InterestExpenseDebt"],
    "Diluted Average Shares": ["WeightedAverageNumberOfDilutedSharesOutstanding"],
    "Basic Average Shares": ["WeightedAverageNumberOfSharesOutstandingBasic"],
    "Selling General And Administration": ["SellingGeneralAndAdministrativeExpense"],
}
EDGAR_BS_TAGS = {
    "Total Assets": ["Assets"],
    "Stockholders Equity": ["StockholdersEquity",
                            "StockholdersEquityIncludingPortionAttributableToNoncontrollingInterest"],
    "Current Assets": ["AssetsCurrent"],
    "Current Liabilities": ["LiabilitiesCurrent"],
    "Retained Earnings": ["RetainedEarningsAccumulatedDeficit"],
    "Goodwill": ["Goodwill"],
    "Inventory": ["InventoryNet"],
    "Accounts Receivable": ["AccountsReceivableNetCurrent", "ReceivablesNetCurrent"],
    "Long Term Debt": ["LongTermDebtNoncurrent", "LongTermDebt"],
    "Net PPE": ["PropertyPlantAndEquipmentNet"],
    "Ordinary Shares Number": ["CommonStockSharesOutstanding"],
    "Total Liabilities Net Minority Interest": ["Liabilities"],
    "Cash And Cash Equivalents": ["CashAndCashEquivalentsAtCarryingValue"],
}
EDGAR_CF_TAGS = {
    "Operating Cash Flow": ["NetCashProvidedByUsedInOperatingActivities",
                            "NetCashProvidedByUsedInOperatingActivitiesContinuingOperations"],
    "Capital Expenditure": ["PaymentsToAcquirePropertyPlantAndEquipment",
                            "PaymentsToAcquireProductiveAssets"],  # negated
    "Depreciation And Amortization": ["DepreciationDepletionAndAmortization",
                                      "DepreciationAndAmortization", "Depreciation"],
    "Cash Dividends Paid": ["PaymentsOfDividendsCommonStock", "PaymentsOfDividends"],  # negated
    "Repurchase Of Capital Stock": ["PaymentsForRepurchaseOfCommonStock"],  # negated
    "Issuance Of Capital Stock": ["ProceedsFromIssuanceOfCommonStock"],
    "Stock Based Compensation": ["ShareBasedCompensation"],
}
EDGAR_NEGATE = {"Capital Expenditure", "Cash Dividends Paid", "Repurchase Of Capital Stock"}

_CIK_MAP = None


def _edgar_get(url):
    resp = requests.get(url, headers={"User-Agent": EDGAR_UA}, timeout=30)
    resp.raise_for_status()
    time.sleep(0.15)  # stay well under SEC's 10 req/s limit
    return resp.json()


def _cik_for(ticker):
    """Ticker -> zero-padded CIK, using SEC's official mapping (cached 7 days)."""
    global _CIK_MAP
    if _CIK_MAP is None:
        p = CACHE_DIR / "edgar_cik_map.pkl"
        fresh = p.exists() and (time.time() - p.stat().st_mtime) / 3600 < 24 * 7
        if fresh:
            try:
                with open(p, "rb") as f:
                    _CIK_MAP = pickle.load(f)
            except Exception:
                _CIK_MAP = None
        if _CIK_MAP is None:
            raw = _edgar_get("https://www.sec.gov/files/company_tickers.json")
            _CIK_MAP = {v["ticker"].upper(): str(v["cik_str"]).zfill(10)
                        for v in raw.values()}
            try:
                CACHE_DIR.mkdir(exist_ok=True)
                with open(p, "wb") as f:
                    pickle.dump(_CIK_MAP, f)
            except Exception:
                pass
    return _CIK_MAP.get(ticker.upper().replace("-", ""))


class EdgarFacts:
    """Annual (10-K) series extractor over SEC companyfacts."""

    def __init__(self, ticker):
        global _EDGAR_WARNED
        self.facts = None
        try:
            cik = _cik_for(ticker)
        except Exception as e:
            if not _EDGAR_WARNED:
                print(f"    !! EDGAR unreachable (ticker map): {type(e).__name__}: {e}")
                print("       10-year history disabled; using Yahoo's ~4 years.")
                _EDGAR_WARNED = True
            return
        if cik is None:
            print(f"    ({ticker}: not in SEC ticker map — EDGAR skipped)")
            return
        try:
            data = _edgar_get(f"https://data.sec.gov/api/xbrl/companyfacts/CIK{cik}.json")
            self.facts = data.get("facts", {}).get("us-gaap", {})
        except Exception as e:
            if not _EDGAR_WARNED:
                print(f"    !! EDGAR fetch failed for {ticker}: {type(e).__name__}: {e}")
                print('       If 403: rerun with --edgar-contact "YourName your@email.com"')
                print("       If timeout/connect: your network blocks sec.gov.")
                _EDGAR_WARNED = True
            self.facts = None

    def series(self, *tags):
        """Annual values as {fiscal_year: value}, latest filing wins per year."""
        if not self.facts:
            return None
        for tag in tags:
            node = self.facts.get(tag)
            if not node:
                continue
            for unit_vals in node.get("units", {}).values():
                by_year = {}
                for item in unit_vals:
                    if item.get("form") != "10-K" or item.get("fp") != "FY":
                        continue
                    fy = item.get("fy")
                    val = item.get("val")
                    if fy is None or val is None:
                        continue
                    # durations: keep only full-year periods (~330+ days)
                    if item.get("start") and item.get("end"):
                        try:
                            days = (pd.Timestamp(item["end"]) - pd.Timestamp(item["start"])).days
                            if days < 330:
                                continue
                        except Exception:
                            pass
                    prev = by_year.get(fy)
                    filed = item.get("filed", "")
                    if prev is None or filed >= prev[1]:
                        by_year[fy] = (float(val), filed)
                if len(by_year) >= 3:
                    return {y: v for y, (v, _) in by_year.items()}
        return None


def _yf_df_to_yearly(df):
    """yfinance statement DataFrame -> {row_label: {year: value}}."""
    out = {}
    if df is None or getattr(df, "empty", True):
        return out
    for label in df.index:
        row = {}
        for col in df.columns:
            try:
                year = pd.Timestamp(col).year
            except Exception:
                continue
            v = df.loc[label, col]
            if pd.notna(v):
                row[year] = float(v)
        if row:
            out[label] = row
    return out


def _merge_statement(yf_df, edgar, tag_map, data=None):
    """Extend yfinance rows with EDGAR history where EDGAR has more years.
    Whole-series replacement (never splice two sources into one row).
    v9: reconciles overlapping years; >20% mismatch -> warning, >50% ->
    row marked unreliable (hard gates depending on it get suppressed)."""
    rows = _yf_df_to_yearly(yf_df)
    prov = {label: "yahoo" for label in rows}
    if edgar is not None and edgar.facts:
        for label, tags in tag_map.items():
            es = edgar.series(*tags)
            if es is None:
                continue
            if label in EDGAR_NEGATE:
                es = {y: -abs(v) for y, v in es.items()}
            yrow = rows.get(label, {})
            # reconciliation on overlapping years before trusting EDGAR
            overlap = sorted(set(es) & set(yrow))
            if overlap and data is not None:
                y = overlap[-1]
                a, b = es[y], yrow[y]
                denom = max(abs(a), abs(b), 1.0)
                mismatch = abs(a - b) / denom
                if mismatch > 0.50:
                    data.unreliable.add(label)
                    data.recon_warnings.append(
                        f"{label}: EDGAR vs Yahoo differ {mismatch*100:.0f}% in {y} "
                        f"— row UNRELIABLE, gates on it suppressed")
                elif mismatch > 0.20:
                    data.recon_warnings.append(
                        f"{label}: EDGAR vs Yahoo differ {mismatch*100:.0f}% in {y} "
                        f"— verify manually")
            if len(es) > len(yrow):
                rows[label] = es
                prov[label] = "edgar"
    # derived rows (EDGAR doesn't report these directly)
    def have(lbl):
        return lbl in rows and len(rows[lbl]) >= 3
    if not have("Free Cash Flow") or (have("Operating Cash Flow")
            and len(rows["Operating Cash Flow"]) > len(rows.get("Free Cash Flow", {}))):
        if have("Operating Cash Flow") and have("Capital Expenditure"):
            common = set(rows["Operating Cash Flow"]) & set(rows["Capital Expenditure"])
            if len(common) >= 3:
                rows["Free Cash Flow"] = {
                    y: rows["Operating Cash Flow"][y] - abs(rows["Capital Expenditure"][y])
                    for y in common}
    if have("Current Assets") and have("Current Liabilities"):
        common = set(rows["Current Assets"]) & set(rows["Current Liabilities"])
        wc = {y: rows["Current Assets"][y] - rows["Current Liabilities"][y] for y in common}
        if len(wc) > len(rows.get("Working Capital", {})):
            rows["Working Capital"] = wc
    if have("Stockholders Equity") and have("Long Term Debt"):
        common = set(rows["Stockholders Equity"]) & set(rows["Long Term Debt"])
        ic = {y: rows["Stockholders Equity"][y] + rows["Long Term Debt"][y] for y in common}
        if len(ic) > len(rows.get("Invested Capital", {})):
            rows["Invested Capital"] = ic
    for lbl in ("Free Cash Flow", "Working Capital", "Invested Capital"):
        if lbl in rows and lbl not in prov:
            prov[lbl] = "derived"
    if data is not None:
        data.provenance.update(prov)
    if not rows:
        return yf_df
    df = pd.DataFrame.from_dict(rows, orient="index")
    return df[sorted(df.columns, reverse=True)]  # newest first, like yfinance


class StatementNormalizer:
    """Named facade over the normalization pipeline (spec section 4):
    merge = StatementNormalizer.merge(...). Provenance, reconciliation
    warnings, and unreliable-row tracking live on the Data object."""
    merge = staticmethod(_merge_statement)


def _fetch_with_retry(fn, what, retries=4, base_wait=5.0):
    """Retry yfinance calls with exponential backoff (handles rate limits).
    Connection failures are NOT retried — they mean Yahoo is unreachable."""
    last_err = None
    for attempt in range(retries):
        try:
            return fn()
        except Exception as e:
            last_err = e
            msg = str(e).lower()
            if _is_connection_error(msg):
                raise
            if "429" in msg or "too many requests" in msg or "rate" in msg:
                wait = base_wait * (2 ** attempt)
                print(f"    rate limited on {what}; waiting {wait:.0f}s "
                      f"(attempt {attempt+1}/{retries})...")
                time.sleep(wait)
            else:
                raise
    raise last_err


_YAHOO_DOWN = False  # set True after first connection failure; skips Yahoo after


def _is_connection_error(msg):
    msg = msg.lower()
    return any(s in msg for s in (
        "failed to connect", "curl: (28)", "curl: (7)", "curl: (6)",
        "connection error", "connectionerror", "max retries",
        "name resolution", "could not connect", "timed out", "timeout"))


def _stooq_price(ticker):
    """Free latest close from stooq.com (no key). Returns float or None."""
    try:
        url = f"https://stooq.com/q/l/?s={ticker.lower()}.us&f=sd2t2ohlcv&h&e=csv"
        resp = requests.get(url, timeout=15)
        lines = resp.text.strip().splitlines()
        if len(lines) < 2:
            return None
        close = lines[1].split(",")[6]
        return float(close) if close not in ("N/D", "") else None
    except Exception:
        return None


def _synthetic_info(ticker, inc, bs_df, cf, price):
    """Rebuild the yfinance 'info' fields the rules need, from statements +
    price alone. Used when Yahoo is unreachable (EDGAR-only mode)."""
    info = {"shortName": ticker.upper(), "sector": "", "industry": "",
            "_synthetic": True}
    sh = _row(inc, "Diluted Average Shares", "Basic Average Shares")
    if sh is None:
        sh = _row(bs_df, "Ordinary Shares Number")
    rev = _row(inc, "Total Revenue")
    ni = _row(inc, "Net Income")
    gp = _row(inc, "Gross Profit")
    ebit = _row(inc, "EBIT", "Operating Income")
    da = _row(cf, "Depreciation And Amortization", "Depreciation Amortization Depletion")
    fcf = _row(cf, "Free Cash Flow")
    cfo = _row(cf, "Operating Cash Flow", "Cash Flow From Continuing Operating Activities")
    se = _row(bs_df, "Stockholders Equity", "Common Stock Equity")
    ta = _row(bs_df, "Total Assets")
    ca = _row(bs_df, "Current Assets")
    cl = _row(bs_df, "Current Liabilities")
    ltd = _row(bs_df, "Long Term Debt")
    cash = _row(bs_df, "Cash And Cash Equivalents")

    mcap = price * sh[-1] if price and sh else None
    debt = ltd[-1] if ltd else 0.0
    cash_v = cash[-1] if cash else 0.0
    ev = mcap + debt - cash_v if mcap is not None else None
    ebitda = (ebit[-1] + (da[-1] if da else 0)) if ebit else None

    info.update({
        "marketCap": mcap, "enterpriseValue": ev, "ebitda": ebitda,
        "totalDebt": debt if ltd else None, "totalCash": cash_v if cash else None,
        "totalRevenue": rev[-1] if rev else None,
        "freeCashflow": fcf[-1] if fcf else None,
        "operatingCashflow": cfo[-1] if cfo else None,
        "netIncomeToCommon": ni[-1] if ni else None,
        "grossMargins": (gp[-1] / rev[-1]) if gp and rev and rev[-1] else None,
        "profitMargins": (ni[-1] / rev[-1]) if ni and rev and rev[-1] else None,
        "returnOnEquity": (ni[-1] / se[-1]) if ni and se and se[-1] > 0 else None,
        "returnOnAssets": (ni[-1] / ta[-1]) if ni and ta and ta[-1] else None,
        "currentRatio": (ca[-1] / cl[-1]) if ca and cl and cl[-1] else None,
        "trailingPE": (mcap / ni[-1]) if mcap and ni and ni[-1] > 0 else None,
        "enterpriseToEbitda": (ev / ebitda) if ev and ebitda and ebitda > 0 else None,
    })
    return {k: v for k, v in info.items() if v is not None or k in
            ("shortName", "sector", "industry")}


class Data:
    def __init__(self, ticker):
        global _YAHOO_DOWN
        self.ticker = ticker
        self.edgar = None
        self.splits = {}          # {year:int -> cumulative-in-year split ratio}
        self.recon_warnings = []  # Yahoo-vs-EDGAR mismatch notes
        self.unreliable = set()   # statement rows too inconsistent for gates
        self.provenance = {}      # row label -> yahoo / edgar / derived
        self.source = "yahoo+edgar"
        cached = _load_cache(ticker)
        if cached is not None and len(cached) == 6:  # v9 cache format
            (self.info, self._inc, self._bs, self._cf,
             edgar_facts, self.splits) = cached
            self.edgar = EdgarFacts.__new__(EdgarFacts)
            self.edgar.facts = edgar_facts
            self.from_cache = True
            self.source = "cache"
            return
        self.from_cache = False
        self.info, self._inc, self._bs, self._cf = {}, None, None, None

        if not _YAHOO_DOWN:
            try:
                t = _fetch_with_retry(lambda: yf.Ticker(ticker), f"{ticker} handle")
                self.info = _fetch_with_retry(lambda: t.info or {}, f"{ticker} info")
                self._inc = _fetch_with_retry(lambda: t.financials, f"{ticker} income stmt")
                self._bs = _fetch_with_retry(lambda: t.balance_sheet, f"{ticker} balance sheet")
                self._cf = _fetch_with_retry(lambda: t.cashflow, f"{ticker} cash flow")
                try:
                    sp = t.splits  # pandas Series: date -> ratio
                    if sp is not None and len(sp):
                        for dt, ratio in sp.items():
                            y = pd.Timestamp(dt).year
                            self.splits[y] = self.splits.get(y, 1.0) * float(ratio)
                except Exception:
                    pass
            except Exception as e:
                if _is_connection_error(str(e)):
                    _YAHOO_DOWN = True
                    print("    !! Yahoo Finance unreachable from this network. "
                          "Switching to EDGAR-only mode (price via Stooq; "
                          "valuation approximate; sector/industry caps unavailable).")
                    self.info = {}
                else:
                    raise

        if USE_EDGAR:
            try:
                self.edgar = EdgarFacts(ticker)
            except Exception:
                self.edgar = None
        self._inc = _merge_statement(self._inc, self.edgar, EDGAR_INC_TAGS, data=self)
        self._bs = _merge_statement(self._bs, self.edgar, EDGAR_BS_TAGS, data=self)
        self._cf = _merge_statement(self._cf, self.edgar, EDGAR_CF_TAGS, data=self)

        if not self.info.get("marketCap"):
            # Yahoo down or empty: rebuild the needed fields from statements
            price = _stooq_price(ticker)
            if price and self.edgar and self.edgar.facts:
                self.info = _synthetic_info(ticker, self._inc, self._bs,
                                            self._cf, price)
                self.source = "edgar+stooq"
            else:
                self.source = "unavailable"

        if self.info and self.info.get("marketCap") is not None:
            _save_cache(ticker, (self.info, self._inc, self._bs, self._cf,
                                 self.edgar.facts if self.edgar else None,
                                 self.splits))

    @property
    def inc(self):
        return self._inc

    @property
    def bs(self):
        return self._bs

    @property
    def cf(self):
        return self._cf

    def g(self, key):
        return _safe(self.info.get(key))


# ============================================================================
# Shared metric computations
# ============================================================================

def _net_debt_ebitda(d):
    debt, cash, ebitda = d.g("totalDebt"), d.g("totalCash"), d.g("ebitda")
    if debt is None or ebitda is None or ebitda <= 0:
        return None
    return (debt - (cash or 0)) / ebitda

def _interest_coverage(d):
    ebit = _row(d.inc, "EBIT", "Operating Income")
    ie = _row(d.inc, "Interest Expense")
    if ebit is None:
        return None
    if ie is None or ie[-1] == 0:
        return float("inf")
    return ebit[-1] / abs(ie[-1])

def _share_cagr(d):
    sh = _row(d.inc, "Diluted Average Shares", "Basic Average Shares")
    if sh is None or len(sh) < 3 or sh[0] <= 0:
        return None
    return (sh[-1] / sh[0]) ** (1 / (len(sh) - 1)) - 1


# ---------------------------------------------------------------------------
# v9 SECTION 1: stock-split adjustment (splits are NOT dilution)
# ---------------------------------------------------------------------------

def get_split_adjustment_factors(fiscal_years, split_events):
    """For each fiscal year, the cumulative factor that restates that year's
    share count in TODAY's share terms: multiply by every split that happened
    AFTER that year. split_events: {year:int -> ratio (e.g. 6.0 for 6:1)}."""
    factors = {}
    for fy in fiscal_years:
        f = 1.0
        for sy, ratio in (split_events or {}).items():
            if sy > fy and ratio and ratio > 0:
                f *= ratio
        factors[fy] = f
    return factors


def split_adjust_share_series(raw_shares_by_year, split_events):
    """{year: raw_shares} -> {year: split-adjusted shares} (today's terms)."""
    if not raw_shares_by_year:
        return raw_shares_by_year
    factors = get_split_adjustment_factors(raw_shares_by_year.keys(), split_events)
    return {y: v * factors[y] for y, v in raw_shares_by_year.items()}


def _looks_like_split_jump(shares_sorted):
    """Heuristic fallback when split data is missing: a >=1.9x single-year
    jump in share count is far more likely a split than real issuance."""
    for a, b in zip(shares_sorted, shares_sorted[1:]):
        if a > 0 and b / a >= 1.9:
            return True
    return False


def dilution_evidence(d):
    """v12: how much cash-flow evidence supports a claim of real dilution?
    Returns dict with level (none/weak/moderate/strong), ratios, and a
    buyback_contradiction flag (net repurchaser can't be a 60%/yr diluter)."""
    iss = _row(d.cf, "Issuance Of Capital Stock", "Common Stock Issuance")
    sbc = _row(d.cf, "Stock Based Compensation")
    buy = _row(d.cf, "Repurchase Of Capital Stock", "Common Stock Payments")
    rev = _row(d.inc, "Total Revenue")
    mc = d.g("marketCap")
    iss_total = sum(abs(x) for x in iss) if iss else 0.0
    buy_total = sum(abs(x) for x in buy) if buy else 0.0
    sbc_total = sum(abs(x) for x in sbc) if sbc else 0.0
    iss_ratio = iss_total / mc if mc and mc > 0 else 0.0
    sbc_ratio = (abs(sbc[-1]) / rev[-1]
                 if sbc and rev and rev[-1] > 0 else 0.0)
    net_buy_yield = ((buy_total - iss_total) / mc) if mc and mc > 0 else None
    contradiction = buy_total > 1.5 * iss_total and buy_total > 0
    if iss_ratio > 0.15 or sbc_ratio > 0.15:
        level = "strong"
    elif (iss_ratio > 0.05 or sbc_ratio > 0.05) and not contradiction:
        level = "moderate"
    elif iss_total > 0 or sbc_total > 0:
        level = "weak"
    else:
        level = "none"
    return {"level": level, "iss_total": iss_total, "buy_total": buy_total,
            "sbc_total": sbc_total, "iss_ratio": iss_ratio,
            "sbc_ratio": sbc_ratio, "net_buyback_yield_window": net_buy_yield,
            "buyback_contradiction": contradiction}


def _both_share_classes_growing(d):
    dil = _yearly(d.inc, "Diluted Average Shares")
    bas = _yearly(d.inc, "Basic Average Shares")
    if not dil or not bas or len(dil) < 3 or len(bas) < 3:
        return False
    def rising(s):
        ys = sorted(s)
        ups = sum(1 for a, b in zip(ys, ys[1:]) if s[b] > s[a])
        return ups >= (len(ys) - 1) * 0.7
    return rising(dil) and rising(bas)


ARTIFACT_MSG = ("DATA ARTIFACT: Share-count series inconsistent with "
                "buyback/issuance data; verify manually")


def share_count_analysis(d):
    """v12: returns raw/adjusted CAGRs plus a full reconciliation:
    begin/end shares (raw & adjusted), evidence level, gate permission,
    reliability, warning."""
    out = {"raw_cagr": None, "adjusted_cagr": None,
           "split_events": dict(getattr(d, "splits", {}) or {}),
           "adjustment_applied": False, "reliability": "high", "warning": None,
           "begin_raw": None, "end_raw": None,
           "begin_adjusted": None, "end_adjusted": None,
           "evidence": None, "dilution_evidence_level": "none",
           "dilution_hard_gate_allowed": False}
    sh = _yearly(d.inc, "Diluted Average Shares", "Basic Average Shares")
    if sh is None or len(sh) < 3:
        out["reliability"] = "low"
        out["warning"] = "share count series too short"
        return out
    years = sorted(sh)
    raw = [sh[y] for y in years]
    out["begin_raw"], out["end_raw"] = raw[0], raw[-1]
    if raw[0] > 0:
        out["raw_cagr"] = (raw[-1] / raw[0]) ** (1 / (len(raw) - 1)) - 1
    if "Diluted Average Shares" in getattr(d, "unreliable", set()) or \
       "Basic Average Shares" in getattr(d, "unreliable", set()):
        out["reliability"] = "low"
        out["warning"] = "share count row failed Yahoo/EDGAR reconciliation"
        out["adjusted_cagr"] = out["raw_cagr"]
        return out
    # split adjustment (in today's share terms)
    if out["split_events"]:
        adj = split_adjust_share_series(sh, out["split_events"])
        a = [adj[y] for y in years]
        out["begin_adjusted"], out["end_adjusted"] = a[0], a[-1]
        if a[0] > 0:
            out["adjusted_cagr"] = (a[-1] / a[0]) ** (1 / (len(a) - 1)) - 1
            out["adjustment_applied"] = True
    else:
        out["begin_adjusted"], out["end_adjusted"] = raw[0], raw[-1]
        out["adjusted_cagr"] = out["raw_cagr"]

    ev = dilution_evidence(d)
    out["evidence"] = ev
    out["dilution_evidence_level"] = ev["level"]
    adj_c = out["adjusted_cagr"]

    if adj_c is not None and adj_c > 0.05:
        # v12 gate permission: evidence must support the dilution claim
        if adj_c > 0.15:
            allowed = ev["level"] == "strong" and not ev["buyback_contradiction"]
        else:
            allowed = (ev["level"] in ("moderate", "strong")
                       and not ev["buyback_contradiction"]) or \
                      (_both_share_classes_growing(d)
                       and not ev["buyback_contradiction"]
                       and ev["level"] != "none")
        if allowed:
            out["dilution_hard_gate_allowed"] = True
        else:
            out["reliability"] = "low"
            out["warning"] = (f"{ARTIFACT_MSG} (claimed "
                              f"{adj_c*100:.0f}%/yr growth; evidence "
                              f"{ev['level']}; net repurchaser: "
                              f"{ev['buyback_contradiction']})")
            out["adjusted_cagr"] = None
        return out

    # no-split-data heuristic (unchanged from v10/v11)
    if (out["raw_cagr"] is not None and out["raw_cagr"] > 0.05
            and not out["split_events"] and _looks_like_split_jump(raw)):
        out["reliability"] = "medium"
        out["warning"] = ("Potential stock-split artifact; verify share count "
                          "manually (>=1.9x single-year jump, no split data)")
        out["adjusted_cagr"] = None
    return out


def _share_cagr_adjusted(d):
    return share_count_analysis(d)["adjusted_cagr"]


# ---------------------------------------------------------------------------
# v9 SECTION 2: buyback quality / shareholder return
# ---------------------------------------------------------------------------

def buyback_analysis(d):
    """Gross/net buyback yields, effectiveness (adjusted share reduction per
    dollar), SBC leakage, and a capital-allocation letter grade."""
    out = {"gross_buyback_yield": None, "net_buyback_yield": None,
           "buyback_effectiveness": None, "sbc_pct_of_buybacks": None,
           "sbc_pct_of_fcf": None, "debt_funded_buyback": None,
           "capital_allocation_grade": None}
    mc = d.g("marketCap")
    buy = _row(d.cf, "Repurchase Of Capital Stock", "Common Stock Payments")
    iss = _row(d.cf, "Issuance Of Capital Stock", "Common Stock Issuance")
    sbc = _row(d.cf, "Stock Based Compensation")
    fcf = _row(d.cf, "Free Cash Flow")
    gross = abs(buy[-1]) if buy else 0.0
    issued = abs(iss[-1]) if iss else 0.0
    if mc and mc > 0:
        out["gross_buyback_yield"] = gross / mc
        out["net_buyback_yield"] = (gross - issued) / mc
    if sbc and gross > 0:
        out["sbc_pct_of_buybacks"] = abs(sbc[-1]) / gross
    if sbc and fcf and fcf[-1] > 0:
        out["sbc_pct_of_fcf"] = abs(sbc[-1]) / fcf[-1]
    sca = share_count_analysis(d)
    adj = sca["adjusted_cagr"]
    if adj is not None and out["gross_buyback_yield"] and out["gross_buyback_yield"] > 0.005:
        # effectiveness: actual adjusted share shrink rate per unit of spend
        out["buyback_effectiveness"] = max(0.0, min(2.0, (-adj) / out["gross_buyback_yield"]))
    out["debt_funded_buyback"] = _debt_funded_buyback(d)
    # letter grade
    pts = 0
    if adj is not None and adj < 0:
        pts += 2
    elif adj is not None and adj < 0.01:
        pts += 1
    if out["buyback_effectiveness"] is not None and out["buyback_effectiveness"] > 0.6:
        pts += 1
    if out["sbc_pct_of_buybacks"] is not None and out["sbc_pct_of_buybacks"] < 0.30:
        pts += 1
    elif out["sbc_pct_of_buybacks"] is None and (sbc is None or not sbc):
        pts += 1
    if not out["debt_funded_buyback"]:
        pts += 1
    out["capital_allocation_grade"] = {5: "A", 4: "B", 3: "C", 2: "D"}.get(pts, "F")
    return out

def _fcf_conversion_ratio(d):
    fcf = _row(d.cf, "Free Cash Flow")
    ni = _row(d.inc, "Net Income")
    if fcf is not None and ni is not None:
        n = min(len(fcf), len(ni))
        tot = sum(ni[-n:])
        if tot > 0:
            return sum(fcf[-n:]) / tot
    f, n2 = d.g("freeCashflow"), d.g("netIncomeToCommon")
    if f is None or n2 is None or n2 <= 0:
        return None
    return f / n2

def _cfo_ni_ratio(d):
    cfo = _row(d.cf, "Operating Cash Flow", "Cash Flow From Continuing Operating Activities")
    ni = _row(d.inc, "Net Income")
    if cfo is not None and ni is not None:
        n = min(len(cfo), len(ni))
        tot = sum(ni[-n:])
        if tot > 0:
            return sum(cfo[-n:]) / tot
    c, n2 = d.g("operatingCashflow"), d.g("netIncomeToCommon")
    if c is None or n2 is None or n2 <= 0:
        return None
    return c / n2

def _nopat_series(d):
    ebit = _row(d.inc, "EBIT", "Operating Income")
    tax = _row(d.inc, "Tax Rate For Calcs")
    if ebit is None:
        return None
    rate = tax[-1] if tax is not None and 0 < tax[-1] < 0.5 else 0.21
    return [e * (1 - rate) for e in ebit]

def _roic_latest(d):
    nopat = _nopat_series(d)
    ic = _row(d.bs, "Invested Capital")
    if nopat is None or ic is None or ic[-1] == 0:
        return None
    return nopat[-1] / ic[-1]

def _op_margins(d):
    ebit = _row(d.inc, "EBIT", "Operating Income")
    rev = _row(d.inc, "Total Revenue")
    if ebit is None or rev is None or len(ebit) != len(rev):
        return None
    m = [e / r for e, r in zip(ebit, rev) if r]
    return m if len(m) >= 3 else None

def _piotroski(d):
    """Best-effort Piotroski F-score, scaled to /9 over available components."""
    pts, avail = 0, 0
    ta = _row(d.bs, "Total Assets")
    ni = _row(d.inc, "Net Income")
    cfo = _row(d.cf, "Operating Cash Flow", "Cash Flow From Continuing Operating Activities")
    rev = _row(d.inc, "Total Revenue")
    gp = _row(d.inc, "Gross Profit")
    ltd = _row(d.bs, "Long Term Debt", "Long Term Debt And Capital Lease Obligation")
    ca = _row(d.bs, "Current Assets")
    cl = _row(d.bs, "Current Liabilities")
    sh = _row(d.inc, "Diluted Average Shares", "Basic Average Shares")

    def two(x):
        return x is not None and len(x) >= 2

    if two(ni) and two(ta):  # ROA > 0 and improving
        avail += 2
        roa1, roa0 = ni[-1] / ta[-1], ni[-2] / ta[-2]
        pts += int(roa1 > 0) + int(roa1 > roa0)
    if cfo is not None and len(cfo) >= 1:  # CFO > 0
        avail += 1
        pts += int(cfo[-1] > 0)
    if cfo is not None and ni is not None:  # CFO > NI (accruals)
        avail += 1
        pts += int(cfo[-1] > ni[-1])
    if two(ltd) and two(ta):  # leverage decreasing
        avail += 1
        pts += int(ltd[-1] / ta[-1] <= ltd[-2] / ta[-2])
    if two(ca) and two(cl) and cl[-1] and cl[-2]:  # current ratio improving
        avail += 1
        pts += int(ca[-1] / cl[-1] >= ca[-2] / cl[-2])
    if two(sh):  # no new shares
        avail += 1
        pts += int(sh[-1] <= sh[-2] * 1.005)
    if two(gp) and two(rev) and rev[-1] and rev[-2]:  # gross margin improving
        avail += 1
        pts += int(gp[-1] / rev[-1] >= gp[-2] / rev[-2])
    if two(rev) and two(ta):  # asset turnover improving
        avail += 1
        pts += int(rev[-1] / ta[-1] >= rev[-2] / ta[-2])
    if avail == 0:
        return None
    return 9 * pts / avail

def _altman_z(d):
    ta = _row(d.bs, "Total Assets")
    ca = _row(d.bs, "Current Assets")
    cl = _row(d.bs, "Current Liabilities")
    re = _row(d.bs, "Retained Earnings")
    ebit = _row(d.inc, "EBIT", "Operating Income")
    rev = _row(d.inc, "Total Revenue")
    tl = _row(d.bs, "Total Liabilities Net Minority Interest", "Total Liabilities")
    mve = d.g("marketCap")
    if not all(x is not None for x in (ta, ebit, rev, tl)) or mve is None or ta[-1] == 0 or tl[-1] == 0:
        return None
    wc = (ca[-1] - cl[-1]) if (ca is not None and cl is not None) else 0.0
    re_v = re[-1] if re is not None else 0.0
    A = ta[-1]
    return (1.2 * wc / A + 1.4 * re_v / A + 3.3 * ebit[-1] / A
            + 0.6 * mve / tl[-1] + 1.0 * rev[-1] / A)

def _accrual_ratio(d):
    ni = _row(d.inc, "Net Income")
    cfo = _row(d.cf, "Operating Cash Flow", "Cash Flow From Continuing Operating Activities")
    ta = _row(d.bs, "Total Assets")
    if ni is None or cfo is None or ta is None or ta[-1] == 0:
        return None
    return (ni[-1] - cfo[-1]) / ta[-1]

def _margin_peak_ratio(d):
    """Current operating margin vs multi-year average (peak-cycle detector)."""
    m = _op_margins(d)
    if m is None:
        return None
    avg = sum(m) / len(m)
    if avg <= 0:
        return None
    return m[-1] / avg


# ---------------------------------------------------------------------------
# v6 metric helpers
# ---------------------------------------------------------------------------

def _cagr(series, min_len=3):
    if series is None or len(series) < min_len or series[0] <= 0 or series[-1] <= 0:
        return None
    return (series[-1] / series[0]) ** (1 / (len(series) - 1)) - 1


def _volatility(series):
    """Coefficient of variation of a series (std/|mean|)."""
    if series is None or len(series) < 3:
        return None
    mean = sum(series) / len(series)
    if mean == 0:
        return None
    var = sum((x - mean) ** 2 for x in series) / len(series)
    return math.sqrt(var) / abs(mean)


def _worst_decline(series):
    """Worst year-over-year % change (most negative)."""
    if series is None or len(series) < 3:
        return None
    changes = [(b - a) / abs(a) for a, b in zip(series, series[1:]) if a]
    return min(changes) if changes else None


def _shareholders_equity(d):
    se = _row(d.bs, "Stockholders Equity", "Common Stock Equity",
              "Total Equity Gross Minority Interest")
    return se[-1] if se is not None else None


def _negative_equity(d):
    se = _shareholders_equity(d)
    return None if se is None else se < 0


def _maintenance_capex(d):
    """Conservative estimate: max(D&A, median capex/revenue x current revenue)."""
    da = _row(d.cf, "Depreciation And Amortization", "Depreciation Amortization Depletion")
    capex = _row(d.cf, "Capital Expenditure")
    rev = _row(d.inc, "Total Revenue")
    est = []
    if da is not None:
        est.append(abs(da[-1]))
    if capex is not None and rev is not None and rev[-1] > 0:
        n = min(len(capex), len(rev))
        ratios = sorted(abs(c) / r for c, r in zip(capex[-n:], rev[-n:]) if r > 0)
        if ratios:
            est.append(ratios[len(ratios) // 2] * rev[-1])
    return max(est) if est else None


def _owner_earnings(d):
    """OE = NI + D&A - maintenance capex (Buffett 1986 letter, simplified)."""
    ni = _row(d.inc, "Net Income")
    da = _row(d.cf, "Depreciation And Amortization", "Depreciation Amortization Depletion")
    mc = _maintenance_capex(d)
    if ni is None or mc is None:
        return None
    return ni[-1] + (da[-1] if da is not None else 0.0) - mc


def _owner_earnings_conservative(d):
    """v8: the LOWER of classic owner earnings and latest FCF. If the two
    estimates disagree, trust the smaller one — precision bias kills."""
    oe = _owner_earnings(d)
    fcf = _row(d.cf, "Free Cash Flow")
    ests = [x for x in (oe, fcf[-1] if fcf else None) if x is not None]
    return min(ests) if ests else None


def _oe_per_share(d):
    oe = _owner_earnings_conservative(d)
    sh = _row(d.inc, "Diluted Average Shares", "Basic Average Shares")
    if oe is None or sh is None or sh[-1] <= 0:
        return None
    return oe / sh[-1]


def _owner_earnings_yield(d):
    oe, ev = _owner_earnings_conservative(d), d.g("enterpriseValue")
    if oe is None or ev is None or ev <= 0:
        return None
    return oe / ev


def _cumulative_fcf(d):
    fcf = _row(d.cf, "Free Cash Flow")
    return sum(fcf) if fcf is not None and len(fcf) >= 3 else None


def _bvps_series(d):
    se = _row(d.bs, "Stockholders Equity", "Common Stock Equity")
    sh = _row(d.bs, "Ordinary Shares Number", "Share Issued")
    if se is None or sh is None:
        return None
    n = min(len(se), len(sh))
    vals = [e / s for e, s in zip(se[-n:], sh[-n:]) if s > 0]
    return vals if len(vals) >= 3 else None


def _receivable_days(d):
    ar = _row(d.bs, "Accounts Receivable", "Receivables")
    rev = _row(d.inc, "Total Revenue")
    if ar is None or rev is None:
        return None
    n = min(len(ar), len(rev))
    days = [365 * a / r for a, r in zip(ar[-n:], rev[-n:]) if r > 0]
    return days if len(days) >= 3 else None


def _inventory_vs_sales(d):
    inv = _row(d.bs, "Inventory")
    rev = _row(d.inc, "Total Revenue")
    if inv is None or rev is None or len(inv) < 3:
        return None
    n = min(len(inv), len(rev))
    if inv[-n] <= 0 or rev[-n] <= 0:
        return None
    return (inv[-1] / inv[-n] - 1) - (rev[-1] / rev[-n] - 1)  # inv growth minus rev growth


def _cfo_ebitda(d):
    cfo = _row(d.cf, "Operating Cash Flow", "Cash Flow From Continuing Operating Activities")
    ebitda = d.g("ebitda")
    if cfo is None or ebitda is None or ebitda <= 0:
        return None
    return cfo[-1] / ebitda


def _intangibles_ratio(d):
    ta = _row(d.bs, "Total Assets")
    gw = _row(d.bs, "Goodwill And Other Intangible Assets")
    if gw is None:
        g1 = _row(d.bs, "Goodwill")
        g2 = _row(d.bs, "Other Intangible Assets")
        if g1 is None and g2 is None:
            return 0.0 if ta is not None else None
        gw = [(a or 0) + (b or 0) for a, b in
              zip(g1 or [0] * len(g2), g2 or [0] * len(g1))]
    if ta is None or ta[-1] <= 0:
        return None
    return gw[-1] / ta[-1]


def _goodwill_growth(d):
    gw = _row(d.bs, "Goodwill")
    if gw is None or len(gw) < 3 or gw[0] <= 0:
        return None
    return gw[-1] / gw[0] - 1


def _debt_funded_buyback(d):
    """True = buying back stock while total debt rose materially."""
    buy = _row(d.cf, "Repurchase Of Capital Stock", "Common Stock Payments")
    debt = _row(d.bs, "Total Debt")
    if debt is None:
        ltd = _row(d.bs, "Long Term Debt")
        cd = _row(d.bs, "Current Debt")
        if ltd is None:
            return None
        n = min(len(ltd), len(cd)) if cd is not None else len(ltd)
        debt = [(ltd[-n:][i] or 0) + ((cd[-n:][i] or 0) if cd is not None else 0)
                for i in range(n)]
    if buy is None or len(debt) < 3:
        return None
    bought = abs(buy[-1]) > 0
    debt_up = debt[0] > 0 and (debt[-1] / debt[0] - 1) > 0.20
    return bought and debt_up


def _reverse_dcf_implied_growth(d, discount=0.10, terminal=0.025, years=10):
    """Binary-search the growth rate that makes a 10yr DCF of owner earnings
    equal the current enterprise value. High implied growth = priced for
    perfection."""
    oe, ev = _owner_earnings_conservative(d), d.g("enterpriseValue")
    if oe is None or oe <= 0 or ev is None or ev <= 0:
        return None

    def dcf_value(g):
        pv, cash = 0.0, oe
        for t in range(1, years + 1):
            cash *= (1 + g)
            pv += cash / (1 + discount) ** t
        tv = cash * (1 + terminal) / (discount - terminal)
        return pv + tv / (1 + discount) ** years

    lo, hi = -0.20, 0.60
    if dcf_value(hi) < ev:
        return hi  # even 60% growth doesn't justify the price
    if dcf_value(lo) > ev:
        return lo
    for _ in range(60):
        mid = (lo + hi) / 2
        if dcf_value(mid) < ev:
            lo = mid
        else:
            hi = mid
    return (lo + hi) / 2


def _pos_year_counts(d):
    fcf = _row(d.cf, "Free Cash Flow")
    ebit = _row(d.inc, "EBIT", "Operating Income")
    fp = f"{sum(1 for x in fcf if x > 0)}/{len(fcf)}" if fcf is not None else ""
    ep = f"{sum(1 for x in ebit if x > 0)}/{len(ebit)}" if ebit is not None else ""
    return fp, ep


# ============================================================================
# THE 40 RULES (10 weighted categories; weights normalized to 100)
# ============================================================================

def rule(fn):
    def wrapped(d):
        try:
            r = fn(d)
            return None if r is None else bool(r)
        except Exception:
            return None
    return wrapped

@rule
def r_ni_pos(d):
    v = _row(d.inc, "Net Income")
    return None if v is None or len(v) < 3 else all(x > 0 for x in v)

@rule
def r_ebit_pos(d):
    v = _row(d.inc, "EBIT", "Operating Income")
    return None if v is None or len(v) < 3 else all(x > 0 for x in v)

@rule
def r_fcf_pos(d):
    v = _row(d.cf, "Free Cash Flow")
    return None if v is None or len(v) < 3 else all(x > 0 for x in v)

@rule
def r_rev_consistency(d):
    rev = _row(d.inc, "Total Revenue")
    if rev is None or len(rev) < 3:
        return None
    ups = sum(1 for a, b in zip(rev, rev[1:]) if b > a)
    return ups >= (len(rev) - 1) * 0.6

@rule
def r_gross_margin(d):
    v = d.g("grossMargins")
    return None if v is None else v > 0.40

@rule
def r_op_margin_stable(d):
    m = _op_margins(d)
    return None if m is None else m[-1] >= m[0] - 0.02

@rule
def r_net_margin(d):
    v = d.g("profitMargins")
    return None if v is None else v > 0.15

@rule
def r_fcf_margin(d):
    fcf, rev = d.g("freeCashflow"), d.g("totalRevenue")
    if fcf is None or rev is None or rev <= 0:
        return None
    return fcf / rev > 0.10

@rule
def r_roe(d):
    v = d.g("returnOnEquity")
    return None if v is None else v > 0.15

@rule
def r_roic(d):
    v = _roic_latest(d)
    return None if v is None else v > 0.12

@rule
def r_roa(d):
    v = d.g("returnOnAssets")
    return None if v is None else v > 0.07

@rule
def r_incremental_roic(d):
    nopat = _nopat_series(d)
    ic = _row(d.bs, "Invested Capital")
    if nopat is None or ic is None or len(nopat) < 3 or len(ic) < 3:
        return None
    d_ic = ic[-1] - ic[0]
    d_np = nopat[-1] - nopat[0]
    if d_ic <= 0:
        return d_np >= 0  # shrinking capital while holding profit = fine
    return d_np / d_ic > 0.12

@rule
def r_fcf_conversion(d):
    v = _fcf_conversion_ratio(d)
    return None if v is None else v > 0.80

@rule
def r_cfo_vs_ni(d):
    v = _cfo_ni_ratio(d)
    return None if v is None else v > 1.0

@rule
def r_owner_earnings_pos(d):
    ni = _row(d.inc, "Net Income")
    da = _row(d.cf, "Depreciation And Amortization", "Depreciation Amortization Depletion")
    capex = _row(d.cf, "Capital Expenditure")
    if ni is None or capex is None:
        return None
    da_v = da[-1] if da is not None else 0.0
    return ni[-1] + da_v - abs(capex[-1]) > 0

@rule
def r_fcf_after_dividends(d):
    fcf = _row(d.cf, "Free Cash Flow")
    div = _row(d.cf, "Cash Dividends Paid", "Common Stock Dividend Paid")
    if fcf is None:
        return None
    div_v = abs(div[-1]) if div is not None else 0.0
    return fcf[-1] - div_v > 0

@rule
def r_capex_rev(d):
    capex = _row(d.cf, "Capital Expenditure")
    rev = _row(d.inc, "Total Revenue")
    if capex is None or rev is None or rev[-1] <= 0:
        return None
    return abs(capex[-1]) / rev[-1] < 0.10

@rule
def r_capex_cfo(d):
    capex = _row(d.cf, "Capital Expenditure")
    cfo = _row(d.cf, "Operating Cash Flow", "Cash Flow From Continuing Operating Activities")
    if capex is None or cfo is None or cfo[-1] <= 0:
        return None
    return abs(capex[-1]) / cfo[-1] < 0.50

@rule
def r_capex_da(d):
    capex = _row(d.cf, "Capital Expenditure")
    da = _row(d.cf, "Depreciation And Amortization", "Depreciation Amortization Depletion")
    if capex is None or da is None or da[-1] <= 0:
        return None
    return abs(capex[-1]) / da[-1] < 1.5

@rule
def r_nwc_stable(d):
    ca = _row(d.bs, "Current Assets")
    cl = _row(d.bs, "Current Liabilities")
    rev = _row(d.inc, "Total Revenue")
    if ca is None or cl is None or rev is None or len(ca) < 3:
        return None
    n = min(len(ca), len(cl), len(rev))
    nwc = [a - l for a, l in zip(ca[-n:], cl[-n:])]
    if rev[-n] <= 0 or rev[-1] <= 0:
        return None
    return nwc[-1] / rev[-1] <= nwc[0] / rev[-n] + 0.05

@rule
def r_net_debt(d):
    v = _net_debt_ebitda(d)
    return None if v is None else v < 2.0

@rule
def r_coverage(d):
    v = _interest_coverage(d)
    return None if v is None else v > 6.0

@rule
def r_current_ratio(d):
    v = d.g("currentRatio")
    return None if v is None else v > 1.2

@rule
def r_altman(d):
    v = _altman_z(d)
    return None if v is None else v > 3.0

@rule
def r_accruals(d):
    v = _accrual_ratio(d)
    return None if v is None else v < 0.05

@rule
def r_piotroski(d):
    v = _piotroski(d)
    return None if v is None else v >= 6.0

@rule
def r_goodwill(d):
    gw = _row(d.bs, "Goodwill", "Goodwill And Other Intangible Assets")
    ta = _row(d.bs, "Total Assets")
    if ta is None or ta[-1] <= 0:
        return None
    if gw is None:
        return True
    return gw[-1] / ta[-1] < 0.30

@rule
def r_tax_normal(d):
    tax = _row(d.inc, "Tax Rate For Calcs")
    if tax is None:
        return None
    return 0.08 < tax[-1] < 0.40

@rule
def r_share_count(d):
    v = _share_cagr_adjusted(d)  # v9: split-adjusted
    return None if v is None else v < 0.02

@rule
def r_sbc(d):
    sbc = _row(d.cf, "Stock Based Compensation")
    rev = _row(d.inc, "Total Revenue")
    if rev is None or rev[-1] <= 0:
        return None
    if sbc is None:
        return True
    return abs(sbc[-1]) / rev[-1] < 0.05

@rule
def r_div_payout(d):
    div = _row(d.cf, "Cash Dividends Paid", "Common Stock Dividend Paid")
    fcf = _row(d.cf, "Free Cash Flow")
    if fcf is None or fcf[-1] <= 0:
        return None
    if div is None:
        return True
    return abs(div[-1]) / fcf[-1] < 0.60

@rule
def r_shareholder_yield(d):
    div = _row(d.cf, "Cash Dividends Paid", "Common Stock Dividend Paid")
    buy = _row(d.cf, "Repurchase Of Capital Stock", "Common Stock Payments")
    iss = _row(d.cf, "Issuance Of Capital Stock", "Common Stock Issuance")
    mc = d.g("marketCap")
    if mc is None or mc <= 0:
        return None
    total = 0.0
    if div is not None:
        total += abs(div[-1])
    if buy is not None:
        total += abs(buy[-1])
    if iss is not None:
        total -= abs(iss[-1])
    return total / mc > 0

@rule
def r_gm_stable(d):
    gp = _row(d.inc, "Gross Profit")
    rev = _row(d.inc, "Total Revenue")
    if gp is None or rev is None or len(gp) < 3 or len(gp) != len(rev):
        return None
    gm = [g / r for g, r in zip(gp, rev) if r]
    return gm[-1] >= gm[0] - 0.03

@rule
def r_roic_persistent(d):
    nopat = _nopat_series(d)
    ic = _row(d.bs, "Invested Capital")
    if nopat is None or ic is None:
        return None
    n = min(len(nopat), len(ic))
    if n < 3:
        return None
    roics = [np / c for np, c in zip(nopat[-n:], ic[-n:]) if c]
    return all(r > 0.10 for r in roics)

@rule
def r_rev_growing(d):
    rev = _row(d.inc, "Total Revenue")
    return None if rev is None or len(rev) < 3 else rev[-1] > rev[0]

@rule
def r_not_peak_margin(d):
    v = _margin_peak_ratio(d)
    return None if v is None else v < 1.35

@rule
def r_fcf_yield(d):
    fcf, ev = d.g("freeCashflow"), d.g("enterpriseValue")
    if fcf is None or ev is None or ev <= 0:
        return None
    return fcf / ev > 0.04

@rule
def r_ev_ebitda(d):
    v = d.g("enterpriseToEbitda")
    return None if v is None else 0 < v < 15

@rule
def r_earnings_yield(d):
    ebit = _row(d.inc, "EBIT", "Operating Income")
    ev = d.g("enterpriseValue")
    if ebit is None or ev is None or ev <= 0:
        return None
    return ebit[-1] / ev > 0.05

@rule
def r_peg(d):
    peg = d.g("trailingPegRatio") or d.g("pegRatio")
    if peg is None:
        return None
    return 0 < peg < 2.0


# ---------------------------------------------------------------------------
# v6 additional rules
# ---------------------------------------------------------------------------

# -- Earning power --
@rule
def r_rev_cagr(d):
    v = _cagr(_row(d.inc, "Total Revenue"))
    return None if v is None else v > 0.03

@rule
def r_fcf_cagr_pos(d):
    v = _cagr(_row(d.cf, "Free Cash Flow"))
    return None if v is None else v > 0

@rule
def r_worst_rev_decline(d):
    v = _worst_decline(_row(d.inc, "Total Revenue"))
    return None if v is None else v > -0.10

# -- Profitability --
@rule
def r_ebitda_margin(d):
    ebitda, rev = d.g("ebitda"), d.g("totalRevenue")
    if ebitda is None or rev is None or rev <= 0:
        return None
    return ebitda / rev > 0.20

@rule
def r_margin_volatility(d):
    m = _op_margins(d)
    if m is None:
        return None
    v = _volatility(m)
    return None if v is None else v < 0.25

@rule
def r_sga_discipline(d):
    sga = _row(d.inc, "Selling General And Administration",
               "Selling General And Administrative")
    rev = _row(d.inc, "Total Revenue")
    if sga is None or rev is None or len(sga) < 3:
        return None
    n = min(len(sga), len(rev))
    r0, r1 = sga[-n] / rev[-n], sga[-1] / rev[-1]
    return r1 <= r0 + 0.02  # SG&A/revenue not creeping up

# -- Returns on capital --
@rule
def r_positive_equity(d):
    v = _negative_equity(d)
    return None if v is None else not v

@rule
def r_median_roic(d):
    nopat = _nopat_series(d)
    ic = _row(d.bs, "Invested Capital")
    if nopat is None or ic is None:
        return None
    n = min(len(nopat), len(ic))
    if n < 3:
        return None
    roics = sorted(np / c for np, c in zip(nopat[-n:], ic[-n:]) if c > 0)
    if not roics:
        return None
    return roics[len(roics) // 2] > 0.12

@rule
def r_roic_not_declining(d):
    nopat = _nopat_series(d)
    ic = _row(d.bs, "Invested Capital")
    if nopat is None or ic is None:
        return None
    n = min(len(nopat), len(ic))
    if n < 3:
        return None
    roics = [np / c for np, c in zip(nopat[-n:], ic[-n:]) if c > 0]
    if len(roics) < 3:
        return None
    return roics[-1] >= roics[0] - 0.03

# -- Owner earnings --
@rule
def r_oe_yield(d):
    v = _owner_earnings_yield(d)
    return None if v is None else v > 0.045

@rule
def r_cumulative_fcf(d):
    v = _cumulative_fcf(d)
    return None if v is None else v > 0

@rule
def r_fcf_per_share_growing(d):
    fcf = _row(d.cf, "Free Cash Flow")
    sh = _row(d.inc, "Diluted Average Shares", "Basic Average Shares")
    if fcf is None or sh is None:
        return None
    n = min(len(fcf), len(sh))
    if n < 3 or sh[-n] <= 0 or sh[-1] <= 0:
        return None
    return fcf[-1] / sh[-1] > fcf[-n] / sh[-n]

# -- Capital intensity --
@rule
def r_ppe_revenue(d):
    ppe = _row(d.bs, "Net PPE")
    rev = _row(d.inc, "Total Revenue")
    if ppe is None or rev is None or rev[-1] <= 0:
        return None
    return ppe[-1] / rev[-1] < 0.50

@rule
def r_sales_to_capital(d):
    rev = _row(d.inc, "Total Revenue")
    ic = _row(d.bs, "Invested Capital")
    if rev is None or ic is None or ic[-1] <= 0:
        return None
    return rev[-1] / ic[-1] > 0.8

# -- Balance sheet --
@rule
def r_cash_vs_debt(d):
    cash, debt = d.g("totalCash"), d.g("totalDebt")
    if cash is None or debt is None:
        return None
    return debt == 0 or cash / debt > 0.5

@rule
def r_debt_equity(d):
    se = _shareholders_equity(d)
    debt = d.g("totalDebt")
    if se is None or debt is None:
        return None
    if se <= 0:
        return False  # negative equity always fails this
    return debt / se < 1.0

@rule
def r_equity_positive_bs(d):
    v = _negative_equity(d)
    return None if v is None else not v

# -- Working capital quality --
@rule
def r_dso_stable(d):
    days = _receivable_days(d)
    if days is None:
        return None
    return days[-1] <= days[0] * 1.20

@rule
def r_inventory_discipline(d):
    v = _inventory_vs_sales(d)
    if v is None:
        return True  # no inventory (services/software) = pass
    return v < 0.15

@rule
def r_receivables_vs_revenue(d):
    ar = _row(d.bs, "Accounts Receivable", "Receivables")
    rev = _row(d.inc, "Total Revenue")
    if ar is None or rev is None or len(ar) < 3:
        return None
    n = min(len(ar), len(rev))
    if ar[-n] <= 0 or rev[-n] <= 0:
        return None
    return (ar[-1] / ar[-n] - 1) <= (rev[-1] / rev[-n] - 1) + 0.25

@rule
def r_cfo_ebitda(d):
    v = _cfo_ebitda(d)
    return None if v is None else v > 0.60

@rule
def r_nwc_not_ballooning(d):
    wc = _row(d.bs, "Working Capital")
    rev = _row(d.inc, "Total Revenue")
    if wc is None or rev is None or len(wc) < 3:
        return None
    n = min(len(wc), len(rev))
    if rev[-n] <= 0 or rev[-1] <= 0:
        return None
    return wc[-1] / rev[-1] <= wc[-n] / rev[-n] + 0.10

# -- Accounting quality --
@rule
def r_intangibles(d):
    v = _intangibles_ratio(d)
    return None if v is None else v < 0.50

@rule
def r_da_capex_match(d):
    capex = _row(d.cf, "Capital Expenditure")
    da = _row(d.cf, "Depreciation And Amortization", "Depreciation Amortization Depletion")
    if capex is None or da is None or abs(capex[-1]) == 0:
        return None
    ratio = da[-1] / abs(capex[-1])
    return 0.4 < ratio < 2.5  # D&A wildly out of line with capex = red flag

@rule
def r_acquisition_dependence(d):
    v = _goodwill_growth(d)
    if v is None:
        return True  # no goodwill history = not a serial acquirer
    return v < 0.50  # goodwill grew >50% over window = acquisition-driven

@rule
def r_no_heavy_issuance(d):
    iss = _row(d.cf, "Issuance Of Capital Stock", "Common Stock Issuance")
    fcf = _row(d.cf, "Free Cash Flow")
    if iss is None:
        return True
    if fcf is None or fcf[-1] <= 0:
        return abs(iss[-1]) == 0
    return abs(iss[-1]) / fcf[-1] < 0.10

# -- Capital allocation --
@rule
def r_sbc_fcf(d):
    sbc = _row(d.cf, "Stock Based Compensation")
    fcf = _row(d.cf, "Free Cash Flow")
    if fcf is None or fcf[-1] <= 0:
        return None
    if sbc is None:
        return True
    return abs(sbc[-1]) / fcf[-1] < 0.20

@rule
def r_no_debt_funded_buybacks(d):
    v = _debt_funded_buyback(d)
    return None if v is None else not v

@rule
def r_bvps_growing(d):
    bvps = _bvps_series(d)
    if bvps is None:
        # heavy buyback companies can shrink book; give credit if shareholder
        # yield rule handles it — treat as not evaluable
        return None
    div = _row(d.cf, "Cash Dividends Paid", "Common Stock Dividend Paid")
    pays_out = div is not None and abs(div[-1]) > 0
    return bvps[-1] > bvps[0] or pays_out

# -- Moat proxies --
@rule
def r_gm_persistent_high(d):
    gp = _row(d.inc, "Gross Profit")
    rev = _row(d.inc, "Total Revenue")
    if gp is None or rev is None or len(gp) < 3 or len(gp) != len(rev):
        return None
    gm = [g / r for g, r in zip(gp, rev) if r]
    return all(m > 0.35 for m in gm)

@rule
def r_margin_stability(d):
    m = _op_margins(d)
    if m is None:
        return None
    v = _volatility(m)
    return None if v is None else v < 0.15

# -- Cyclicality / downside risk --
@rule
def r_worst_ebit_decline(d):
    v = _worst_decline(_row(d.inc, "EBIT", "Operating Income"))
    return None if v is None else v > -0.20

@rule
def r_worst_fcf_decline(d):
    v = _worst_decline(_row(d.cf, "Free Cash Flow"))
    return None if v is None else v > -0.30

@rule
def r_rev_volatility(d):
    v = _volatility(_row(d.inc, "Total Revenue"))
    return None if v is None else v < 0.15

@rule
def r_margin_vs_history(d):
    v = _margin_peak_ratio(d)
    return None if v is None else v < 1.25

@rule
def r_ebit_volatility(d):
    v = _volatility(_row(d.inc, "EBIT", "Operating Income"))
    return None if v is None else v < 0.30

# -- Valuation --
@rule
def r_oe_yield_val(d):
    v = _owner_earnings_yield(d)
    return None if v is None else v > 0.04

@rule
def r_ev_ebit(d):
    ebit = _row(d.inc, "EBIT", "Operating Income")
    ev = d.g("enterpriseValue")
    if ebit is None or ebit[-1] <= 0 or ev is None or ev <= 0:
        return None
    return ev / ebit[-1] < 20

@rule
def r_reverse_dcf(d):
    v = _reverse_dcf_implied_growth(d)
    return None if v is None else v < 0.15  # price implies <15%/yr OE growth

@rule
def r_pe_sane(d):
    pe = d.g("trailingPE")
    return None if pe is None else 0 < pe < 30



# ============================================================================
# v9 SECTION 5: graded scoring (no more cliff effects)
# ============================================================================

def _lerp(v, x0, x1, y0, y1):
    if x1 == x0:
        return y1
    t = max(0.0, min(1.0, (v - x0) / (x1 - x0)))
    return y0 + t * (y1 - y0)


def score_threshold_high(value, poor, good, excellent):
    """Higher is better. poor->0, good->70, excellent->100."""
    if value is None:
        return None
    if value <= poor:
        return 0.0
    if value >= excellent:
        return 100.0
    if value <= good:
        return _lerp(value, poor, good, 0, 70)
    return _lerp(value, good, excellent, 70, 100)


def score_threshold_low(value, excellent, good, poor):
    """Lower is better. excellent->100, good->70, poor->0."""
    if value is None:
        return None
    if value <= excellent:
        return 100.0
    if value >= poor:
        return 0.0
    if value <= good:
        return _lerp(value, excellent, good, 100, 70)
    return _lerp(value, good, poor, 70, 0)


def score_range(value, ideal_low, ideal_high, fail_low, fail_high):
    """Best inside [ideal_low, ideal_high]; 0 outside [fail_low, fail_high]."""
    if value is None:
        return None
    if ideal_low <= value <= ideal_high:
        return 100.0
    if value < ideal_low:
        return _lerp(value, fail_low, ideal_low, 0, 100)
    return _lerp(value, ideal_high, fail_high, 100, 0)


def score_stability(volatility, excellent, good, poor):
    return score_threshold_low(volatility, excellent, good, poor)


def score_cagr(value, poor, good, excellent):
    return score_threshold_high(value, poor, good, excellent)


FIN_INVALID_GRADED = {"FCF conversion", "CFO/NI", "OE yield", "FCF yield",
                      "EV/EBIT", "EV/EBITDA", "Net debt/EBITDA",
                      "Interest coverage", "Altman Z", "FCF CAGR",
                      "Gross margin", "Rev DCF implied growth"}


def graded_metric_scores(d, is_fin=False):
    """Graded 0-100 for the key economic metrics. For financials, invalid
    generic metrics are excluded and P/B, P/TBV, ROA are graded instead.
    Returns (overall_graded, {metric: (value, score)})."""
    m = _op_margins(d)
    vol_m = _volatility(m) if m else None
    gp, rev = _row(d.inc, "Gross Profit"), _row(d.inc, "Total Revenue")
    gm = gp[-1] / rev[-1] if gp and rev and rev[-1] else d.g("grossMargins")
    om = m[-1] if m else None
    ebit = _row(d.inc, "EBIT", "Operating Income")
    ev = d.g("enterpriseValue")
    ev_ebit = ev / ebit[-1] if ev and ebit and ebit[-1] > 0 else None
    ic = _interest_coverage(d)
    if ic == float("inf"):
        ic = 100.0
    sbc = _row(d.cf, "Stock Based Compensation")
    fcf = _row(d.cf, "Free Cash Flow")
    sbc_fcf = abs(sbc[-1]) / fcf[-1] if sbc and fcf and fcf[-1] > 0 else (
        0.0 if fcf and fcf[-1] > 0 else None)
    fcf_i = d.g("freeCashflow")
    fcf_yld = fcf_i / ev if fcf_i and ev and ev > 0 else None
    pvh = _pe_vs_history(d)
    val_hist_ratio = pvh[0] if pvh else None
    adj_cagr = _share_cagr_adjusted(d)

    table = {
        "ROIC":            (_roic_latest(d),        score_threshold_high(_roic_latest(d), 0.06, 0.12, 0.25)),
        "ROE":             (d.g("returnOnEquity"),  score_threshold_high(d.g("returnOnEquity"), 0.08, 0.15, 0.30)),
        "ROA":             (d.g("returnOnAssets"),  score_threshold_high(d.g("returnOnAssets"), 0.03, 0.07, 0.15)),
        "FCF conversion":  (_fcf_conversion_ratio(d), score_threshold_high(_fcf_conversion_ratio(d), 0.5, 0.8, 1.1)),
        "CFO/NI":          (_cfo_ni_ratio(d),       score_threshold_high(_cfo_ni_ratio(d), 0.7, 1.0, 1.3)),
        "Gross margin":    (gm,                     score_threshold_high(gm, 0.25, 0.40, 0.60)),
        "Operating margin": (om,                    score_threshold_high(om, 0.08, 0.15, 0.30)),
        "Margin stability": (vol_m,                 score_stability(vol_m, 0.05, 0.15, 0.35)),
        "Revenue CAGR":    (_cagr(rev),             score_cagr(_cagr(rev), 0.0, 0.05, 0.12)),
        "FCF CAGR":        (_cagr(fcf),             score_cagr(_cagr(fcf), 0.0, 0.06, 0.15)),
        "OE yield":        (_owner_earnings_yield(d), score_threshold_high(_owner_earnings_yield(d), 0.02, 0.045, 0.08)),
        "FCF yield":       (fcf_yld,                score_threshold_high(fcf_yld, 0.02, 0.04, 0.08)),
        "EV/EBIT":         (ev_ebit,                score_threshold_low(ev_ebit, 10, 18, 30)),
        "EV/EBITDA":       (d.g("enterpriseToEbitda"), score_threshold_low(d.g("enterpriseToEbitda"), 8, 14, 25)),
        "Net debt/EBITDA": (_net_debt_ebitda(d),    score_threshold_low(_net_debt_ebitda(d), 0.0, 1.5, 4.0)),
        "Interest coverage": (ic,                   score_threshold_high(ic, 3, 8, 20)),
        "SBC/FCF":         (sbc_fcf,                score_threshold_low(sbc_fcf, 0.05, 0.15, 0.40)),
        "Share CAGR (adj)": (adj_cagr,              score_threshold_low(adj_cagr, -0.02, 0.01, 0.05)),
        "Accrual ratio":   (_accrual_ratio(d),      score_threshold_low(_accrual_ratio(d), 0.0, 0.05, 0.15)),
        "Piotroski":       (_piotroski(d),          score_threshold_high(_piotroski(d), 3, 6, 8)),
        "Altman Z":        (_altman_z(d),           score_threshold_high(_altman_z(d), 1.8, 3.0, 6.0)),
        "Val vs own history": (val_hist_ratio,      score_threshold_low(val_hist_ratio, 0.8, 1.2, 2.2)),
        "Rev DCF implied growth": (_reverse_dcf_implied_growth(d),
                                   score_threshold_low(_reverse_dcf_implied_growth(d), 0.02, 0.08, 0.18)),
    }
    if is_fin:
        for k in FIN_INVALID_GRADED:
            table.pop(k, None)
        bv = bank_valuation(d)
        table["P/B (bank)"] = (bv["p_b"], score_threshold_low(bv["p_b"], 0.8, 1.5, 3.0))
        table["P/TBV (bank)"] = (bv["p_tbv"], score_threshold_low(bv["p_tbv"], 1.0, 1.8, 3.5))
        table["ROA (bank)"] = (bv["roa"], score_threshold_high(bv["roa"], 0.005, 0.010, 0.018))
        table["Normalized earnings yield (bank)"] = (
            bv["normalized_earnings_yield"],
            score_threshold_high(bv["normalized_earnings_yield"], 0.04, 0.07, 0.12))
    scores = [s for _, s in table.values() if s is not None]
    overall = round(sum(scores) / len(scores), 1) if scores else None
    return overall, table


CATEGORIES = [
    ("1. Consistent earning power", 10, [
        ("Net income positive every year",        r_ni_pos),
        ("Operating income positive every year",  r_ebit_pos),
        ("Free cash flow positive every year",    r_fcf_pos),
        ("Revenue up in most years",              r_rev_consistency),
        ("Revenue CAGR > 3%",                     r_rev_cagr),
        ("FCF CAGR positive",                     r_fcf_cagr_pos),
        ("Worst revenue decline > -10%",          r_worst_rev_decline)]),
    ("2. Profitability & margins", 8, [
        ("Gross margin > 40%",                    r_gross_margin),
        ("Operating margin stable/rising",        r_op_margin_stable),
        ("Net margin > 15%",                      r_net_margin),
        ("FCF margin > 10%",                      r_fcf_margin),
        ("EBITDA margin > 20%",                   r_ebitda_margin),
        ("Operating margin volatility low",       r_margin_volatility),
        ("SG&A / revenue not creeping up",        r_sga_discipline)]),
    ("3. Returns on capital", 14, [
        ("ROE > 15%",                             r_roe),
        ("Positive shareholders' equity",         r_positive_equity),
        ("ROIC > 12%",                            r_roic),
        ("ROA > 7%",                              r_roa),
        ("Incremental ROIC > 12%",                r_incremental_roic),
        ("Median ROIC > 12%",                     r_median_roic),
        ("ROIC not declining",                    r_roic_not_declining)]),
    ("4. Owner earnings / cash conversion", 14, [
        ("FCF / net income > 80%",                r_fcf_conversion),
        ("CFO / net income > 1.0",                r_cfo_vs_ni),
        ("Owner earnings positive",               r_owner_earnings_pos),
        ("Owner earnings yield > 4.5%",           r_oe_yield),
        ("FCF covers dividends",                  r_fcf_after_dividends),
        ("Cumulative FCF positive (all years)",   r_cumulative_fcf),
        ("FCF per share growing",                 r_fcf_per_share_growing)]),
    ("5. Capital intensity", 8, [
        ("Capex < 10% of revenue",                r_capex_rev),
        ("Capex < 50% of operating cash flow",    r_capex_cfo),
        ("Capex < 1.5x D&A",                      r_capex_da),
        ("Working capital not consuming cash",    r_nwc_stable),
        ("Net PP&E < 50% of revenue",             r_ppe_revenue),
        ("Sales / invested capital > 0.8x",       r_sales_to_capital)]),
    ("6. Balance sheet strength", 10, [
        ("Net debt / EBITDA < 2.0x",              r_net_debt),
        ("Interest coverage > 6x",                r_coverage),
        ("Current ratio > 1.2",                   r_current_ratio),
        ("Altman Z-score > 3.0",                  r_altman),
        ("Cash > 50% of total debt",              r_cash_vs_debt),
        ("Debt / equity < 1.0",                   r_debt_equity),
        ("Shareholders' equity positive",         r_equity_positive_bs)]),
    ("7. Working capital quality", 5, [
        ("Receivable days not rising >20%",       r_dso_stable),
        ("Inventory growth <= sales growth",      r_inventory_discipline),
        ("Receivables tracking revenue",          r_receivables_vs_revenue),
        ("CFO / EBITDA > 60%",                    r_cfo_ebitda),
        ("NWC / revenue not ballooning",          r_nwc_not_ballooning)]),
    ("8. Accounting quality", 10, [
        ("Accrual ratio low (NI ~ cash)",         r_accruals),
        ("Piotroski F-score >= 6",                r_piotroski),
        ("Goodwill < 30% of assets",              r_goodwill),
        ("Goodwill+intangibles < 50% of assets",  r_intangibles),
        ("D&A consistent with capex",             r_da_capex_match),
        ("Not acquisition-dependent",             r_acquisition_dependence),
        ("No heavy share issuance",               r_no_heavy_issuance),
        ("Effective tax rate normal",             r_tax_normal)]),
    ("9. Capital allocation", 9, [
        ("Share count flat/shrinking (<2%/yr)",   r_share_count),
        ("Stock comp < 5% of revenue",            r_sbc),
        ("Stock comp < 20% of FCF",               r_sbc_fcf),
        ("Dividends < 60% of FCF",                r_div_payout),
        ("Positive shareholder yield",            r_shareholder_yield),
        ("No debt-funded buybacks",               r_no_debt_funded_buybacks),
        ("Book value/share growing or payout",    r_bvps_growing)]),
    ("10. Moat proxies", 10, [
        ("Gross margin not eroding",              r_gm_stable),
        ("Gross margin > 35% every year",         r_gm_persistent_high),
        ("ROIC > 10% every year",                 r_roic_persistent),
        ("Revenue growing",                       r_rev_growing),
        ("Operating margin very stable",          r_margin_stability),
        ("Margins not at unusual cyclical peak",  r_not_peak_margin)]),
    ("11. Cyclicality / downside risk", 5, [
        ("Worst EBIT decline > -20%",             r_worst_ebit_decline),
        ("Worst FCF decline > -30%",              r_worst_fcf_decline),
        ("Revenue volatility low",                r_rev_volatility),
        ("EBIT volatility moderate",              r_ebit_volatility),
        ("Margins near historical norm",          r_margin_vs_history)]),
    ("12. Valuation / margin of safety", 12, [
        ("FCF yield > 4% of enterprise value",    r_fcf_yield),
        ("Owner earnings yield > 4%",             r_oe_yield_val),
        ("EV / EBITDA < 15",                      r_ev_ebitda),
        ("EV / EBIT < 20",                        r_ev_ebit),
        ("Earnings yield (EBIT/EV) > 5%",         r_earnings_yield),
        ("Reverse DCF implied growth < 15%",      r_reverse_dcf),
        ("P/E < 30",                              r_pe_sane),
        ("PEG < 2.0",                             r_peg)]),
]
TOTAL_WEIGHT = sum(w for _, w, _ in CATEGORIES)  # 115 -> normalized to 100
N_RULES = sum(len(rules) for _, _, rules in CATEGORIES)  # 80

# ============================================================================
# Hard gates, caps, industry overrides
# ============================================================================

SPECIAL_MODEL_KEYWORDS = [
    ("bank", 80), ("insurance", 80), ("asset management", 80),
    ("capital markets", 80), ("reit", 75), ("mortgage", 75),
    ("credit services", 80), ("specialty finance", 80),
    ("financial conglomerates", 80),
    ("biotechnology", 75), ("drug manufacturers - specialty", 75),
    ("utilities", 80), ("utility", 80),
]
RISK_CAP_KEYWORDS = [
    # retail / consumer discretionary
    ("footwear", 85), ("apparel", 85), ("luxury", 85),
    ("specialty retail", 85), ("beauty", 85), ("personal products", 85),
    ("department store", 85), ("discount store", 85),
    # cyclicals / commodities
    ("semiconductor", 85), ("auto parts", 85), ("auto manufacturer", 85),
    ("homebuild", 85), ("oil & gas", 80), ("oil, gas", 80), ("steel", 80),
    ("aluminum", 80), ("copper", 80), ("mining", 80), ("chemicals", 85),
    ("paper", 85), ("lumber", 85), ("agricultural inputs", 85),
    # travel / leisure
    ("gambling", 85), ("resorts", 85), ("casinos", 85), ("airlines", 75),
    ("hotel", 85), ("cruise", 80), ("lodging", 85), ("restaurants", 85),
    # people businesses / outsourcing / special underwriting
    ("consulting", 85), ("staffing", 85), ("outsourcing", 85),
    ("information technology services", 85), ("bpo", 85),
    ("personal services", 85), ("tax", 85),
    ("education", 80), ("healthcare services", 85),
    ("medical care facilities", 85), ("diagnostics & research", 85),
    ("advertising", 85), ("publishing", 85), ("broadcasting", 85),
]

# ============================================================================
# v8: Historical valuation context (Stooq yearly prices + merged statements)
# ============================================================================

def _yearly(df, *names):
    """Row as {year:int -> value} from merged statement frames."""
    if df is None or getattr(df, "empty", True):
        return None
    for n in names:
        if n in df.index:
            out = {}
            for col in df.columns:
                try:
                    y = int(col) if not hasattr(col, "year") else col.year
                except Exception:
                    continue
                v = df.loc[n, col]
                if pd.notna(v):
                    out[y] = float(v)
            if out:
                return out
    return None


def _stooq_yearly_closes(ticker):
    """Yearly closes {year: close} from Stooq (free). Disk-cached 24h."""
    p = CACHE_DIR / f"px_{ticker.upper()}.pkl"
    if USE_CACHE and p.exists() and (time.time() - p.stat().st_mtime) / 3600 < 24:
        try:
            with open(p, "rb") as f:
                return pickle.load(f)
        except Exception:
            pass
    out = None
    try:
        url = f"https://stooq.com/q/d/l/?s={ticker.lower()}.us&i=y"
        lines = requests.get(url, timeout=15).text.strip().splitlines()
        if len(lines) > 2 and lines[0].lower().startswith("date"):
            out = {}
            for ln in lines[1:]:
                parts = ln.split(",")
                if len(parts) >= 5:
                    out[int(parts[0][:4])] = float(parts[4])
    except Exception:
        out = None
    if out:
        try:
            CACHE_DIR.mkdir(exist_ok=True)
            with open(p, "wb") as f:
                pickle.dump(out, f)
        except Exception:
            pass
    return out


def _dcf_value(cash0, growth, years=10, discount=0.10, terminal=0.025):
    if cash0 is None or cash0 <= 0 or discount <= terminal:
        return None
    pv, c = 0.0, cash0
    for t in range(1, years + 1):
        c *= (1 + growth)
        pv += c / (1 + discount) ** t
    tv = c * (1 + terminal) / (discount - terminal)
    return pv + tv / (1 + discount) ** years


def valuation_v2(d):
    """v9 SECTION 8: normalized earnings + conservative base/bear DCF.
    Normalized FCF = median FCF margin x current revenue (mid-cycle proxy).
    DCF is a sanity check, never a price target."""
    out = {"normalized_fcf": None, "normalized_fcf_yield": None,
           "base_dcf_value": None, "bear_dcf_value": None,
           "mos_base": None, "mos_bear": None, "valuation_warning": None}
    rev = _row(d.inc, "Total Revenue")
    fcf = _row(d.cf, "Free Cash Flow")
    ev = d.g("enterpriseValue")
    if rev is None or fcf is None or not ev or ev <= 0:
        return out
    n = min(len(rev), len(fcf))
    margins = sorted(f / r for f, r in zip(fcf[-n:], rev[-n:]) if r > 0)
    if len(margins) < 3:
        return out
    med_margin = margins[len(margins) // 2]
    norm_fcf = med_margin * rev[-1]
    out["normalized_fcf"] = norm_fcf
    out["normalized_fcf_yield"] = norm_fcf / ev if norm_fcf else None
    g_hist = _cagr(rev) or 0.0
    g_base = max(0.0, min(g_hist, 0.08))
    g_bear = max(0.0, g_base - 0.03)
    out["base_dcf_value"] = _dcf_value(norm_fcf, g_base, discount=0.10)
    out["bear_dcf_value"] = _dcf_value(norm_fcf * 0.8, g_bear, discount=0.105)
    if out["base_dcf_value"]:
        out["mos_base"] = out["base_dcf_value"] / ev - 1
    if out["bear_dcf_value"]:
        out["mos_bear"] = out["bear_dcf_value"] / ev - 1
    if out["mos_base"] is not None and out["mos_base"] < 0:
        out["valuation_warning"] = ("price exceeds base-case DCF of normalized "
                                    "owner earnings — no margin of safety")
    return out


# generic rules that are economically meaningless for banks/insurers and
# should be EXCLUDED (not failed, not counted as missing) — spec section 7

# ============================================================================
# v11: concern wording — concerns must read as FAILURES, never as the
# positive rule label (spec item 4)
# ============================================================================

FAIL_TEXT = {
    "Net income positive every year": "Net income was NEGATIVE in at least one year",
    "Operating income positive every year": "Operating income was NEGATIVE in at least one year",
    "Free cash flow positive every year": "Free cash flow was NEGATIVE in at least one year",
    "Revenue up in most years": "Revenue declined in several years",
    "Revenue CAGR > 3%": "Revenue growth below 3%/yr",
    "FCF CAGR positive": "Free cash flow is shrinking over the window",
    "Worst revenue decline > -10%": "Suffered a >10% single-year revenue decline",
    "Gross margin > 40%": "Gross margin below 40% (limited pricing power)",
    "Operating margin stable/rising": "Operating margin is deteriorating",
    "Net margin > 15%": "Net margin below 15%",
    "FCF margin > 10%": "FCF margin below 10%",
    "EBITDA margin > 20%": "EBITDA margin below 20%",
    "Operating margin volatility low": "Operating margins are volatile",
    "SG&A / revenue not creeping up": "SG&A is growing faster than revenue (cost discipline slipping)",
    "ROE > 15%": "ROE below 15%",
    "Positive shareholders' equity": "Shareholders' equity is NEGATIVE",
    "ROIC > 12%": "ROIC below 12%",
    "ROA > 7%": "ROA below 7%",
    "Incremental ROIC > 12%": "New capital is earning below 12% (incremental ROIC weak)",
    "Median ROIC > 12%": "Median ROIC over the window below 12%",
    "ROIC not declining": "ROIC is declining",
    "FCF / net income > 80%": "Less than 80% of earnings convert to free cash",
    "CFO / net income > 1.0": "Operating cash flow runs below reported earnings",
    "Owner earnings positive": "Owner earnings are negative",
    "Owner earnings yield > 4.5%": "Owner-earnings yield below 4.5% (price rich vs cash generation)",
    "FCF covers dividends": "Dividends exceed free cash flow",
    "Cumulative FCF positive (all years)": "Cumulative FCF over the window is negative",
    "FCF per share growing": "FCF per share is not growing",
    "Capex < 10% of revenue": "Capex consumes over 10% of revenue (capital heavy)",
    "Capex < 50% of operating cash flow": "Capex consumes over half of operating cash flow",
    "Capex < 1.5x D&A": "Capex far exceeds depreciation (heavy reinvestment need)",
    "Working capital not consuming cash": "Working capital is consuming cash as it grows",
    "Net PP&E < 50% of revenue": "Asset-heavy: net PP&E exceeds 50% of revenue",
    "Sales / invested capital > 0.8x": "Low capital turnover (<0.8x sales per $ invested)",
    "Net debt / EBITDA < 2.0x": "Net debt above 2x EBITDA",
    "Interest coverage > 6x": "Interest coverage below 6x",
    "Current ratio > 1.2": "Current ratio below 1.2 (thin short-term liquidity)",
    "Altman Z-score > 3.0": "Altman Z-score below 3 (elevated distress odds)",
    "Cash > 50% of total debt": "Cash covers less than half of total debt",
    "Debt / equity < 1.0": "Debt exceeds shareholders' equity",
    "Shareholders' equity positive": "Shareholders' equity is NEGATIVE",
    "Receivable days not rising >20%": "Customers are paying materially slower (DSO up >20%)",
    "Inventory growth <= sales growth": "Inventory growing faster than sales (markdown risk)",
    "Receivables tracking revenue": "Receivables growing much faster than revenue",
    "CFO / EBITDA > 60%": "Under 60% of EBITDA becomes operating cash",
    "NWC / revenue not ballooning": "Working capital intensity is rising",
    "Accrual ratio low (NI ~ cash)": "High accruals: earnings outrun cash",
    "Piotroski F-score >= 6": "Weak Piotroski F-score (<6/9)",
    "Goodwill < 30% of assets": "Goodwill exceeds 30% of assets (acquisition-built)",
    "Goodwill+intangibles < 50% of assets": "Over half the balance sheet is goodwill/intangibles",
    "D&A consistent with capex": "D&A and capex are far out of line (depreciation games or capex cliff)",
    "Not acquisition-dependent": "Growth appears acquisition-dependent (goodwill ballooning)",
    "No heavy share issuance": "Heavy share issuance",
    "Effective tax rate normal": "Abnormal effective tax rate (unsustainable earnings boost?)",
    "Share count flat/shrinking (<2%/yr)": "Share count rising >2%/yr (dilution)",
    "Stock comp < 5% of revenue": "Stock comp exceeds 5% of revenue",
    "Stock comp < 20% of FCF": "Stock comp eats over 20% of free cash flow",
    "Dividends < 60% of FCF": "Dividend payout above 60% of FCF (little retained for growth)",
    "Positive shareholder yield": "Net negative shareholder yield (issuing more than returning)",
    "No debt-funded buybacks": "Buying back stock with borrowed money",
    "Book value/share growing or payout": "Book value per share shrinking without offsetting payout",
    "Gross margin not eroding": "Gross margin is eroding",
    "Gross margin > 35% every year": "Gross margin dipped below 35% in the window",
    "ROIC > 10% every year": "ROIC fell below 10% in at least one year",
    "Revenue growing": "Revenue is not growing",
    "Operating margin very stable": "Operating margins swing widely",
    "Margins not at unusual cyclical peak": "Current margins look like a cyclical peak",
    "Worst EBIT decline > -20%": "EBIT fell over 20% in a single year (downturn fragility)",
    "Worst FCF decline > -30%": "FCF fell over 30% in a single year",
    "Revenue volatility low": "Revenue is volatile",
    "EBIT volatility moderate": "EBIT is highly volatile",
    "Margins near historical norm": "Margins far above their own history (peak risk)",
    "FCF yield > 4% of enterprise value": "FCF yield below 4% (price rich vs cash)",
    "Owner earnings yield > 4%": "Owner-earnings yield below 4%",
    "EV / EBITDA < 15": "EV/EBITDA above 15x",
    "EV / EBIT < 20": "EV/EBIT above 20x",
    "Earnings yield (EBIT/EV) > 5%": "Earnings yield below 5%",
    "Reverse DCF implied growth < 15%": "Price implies over 15%/yr owner-earnings growth",
    "P/E < 30": "P/E above 30x",
    "PEG < 2.0": "PEG above 2 (paying up for growth)",
}


def fail_concern(rule_name):
    return FAIL_TEXT.get(rule_name, f"Fails: {rule_name}")


# ============================================================================
# v10 SECTION: row criticality — reconciliation consequences match the row
# ============================================================================

CRITICAL_ROWS = {
    "Total Revenue", "Net Income", "Operating Income", "EBIT",
    "Operating Cash Flow", "Free Cash Flow", "Long Term Debt", "Total Debt",
    "Cash And Cash Equivalents", "Diluted Average Shares",
    "Basic Average Shares", "Stockholders Equity",
}
# revenue/earnings/cash-generation rows: worst tier inside critical
CORE_ECONOMIC_ROWS = {"Total Revenue", "Net Income", "Operating Income",
                      "EBIT", "Operating Cash Flow", "Free Cash Flow"}
IMPORTANT_ROWS = {
    "Capital Expenditure", "Depreciation And Amortization", "Interest Expense",
    "Current Assets", "Current Liabilities", "Goodwill",
    "Accounts Receivable", "Inventory",
}
# everything else (Net PPE, SG&A, Retained Earnings, intangibles, ...) is
# noncritical: warning only.

# rules whose ONLY inputs are important/noncritical rows — if that row fails
# reconciliation, suppress the rule (excluded, labeled DATA?) instead of
# scoring it on bad data
RULE_ROW_DEPS = {
    "Net PP&E < 50% of revenue": {"Net PPE"},
    "SG&A / revenue not creeping up": {"Selling General And Administration"},
    "Capex < 10% of revenue": {"Capital Expenditure"},
    "Capex < 50% of operating cash flow": {"Capital Expenditure"},
    "Capex < 1.5x D&A": {"Capital Expenditure", "Depreciation And Amortization"},
    "D&A consistent with capex": {"Capital Expenditure", "Depreciation And Amortization"},
    "Receivable days not rising >20%": {"Accounts Receivable"},
    "Receivables tracking revenue": {"Accounts Receivable"},
    "Inventory growth <= sales growth": {"Inventory"},
    "Goodwill < 30% of assets": {"Goodwill"},
    "Goodwill+intangibles < 50% of assets": {"Goodwill"},
    "Current ratio > 1.2": {"Current Assets", "Current Liabilities"},
    "Interest coverage > 6x": {"Interest Expense"},
}


def row_criticality(label):
    if label in CRITICAL_ROWS:
        return "critical"
    if label in IMPORTANT_ROWS:
        return "important"
    return "noncritical"


def reconciliation_caps(unreliable):
    """v10: tiered caps by criticality. Returns (caps, warnings)."""
    caps, warnings = [], []
    crit = {r for r in unreliable if row_criticality(r) == "critical"}
    imp = {r for r in unreliable if row_criticality(r) == "important"}
    nonc = {r for r in unreliable if row_criticality(r) == "noncritical"}
    if crit & CORE_ECONOMIC_ROWS:
        caps.append((75, "CRITICAL economic rows failed reconciliation: "
                         + ", ".join(sorted(crit & CORE_ECONOMIC_ROWS))))
    elif crit:
        caps.append((85, "Critical balance-sheet rows failed reconciliation: "
                         + ", ".join(sorted(crit))))
    for r in sorted(imp):
        warnings.append(f"{r} unreliable — dependent rule(s) suppressed, "
                        f"confidence reduced")
    if len(nonc) >= 3:
        caps.append((90, f"{len(nonc)} noncritical rows failed reconciliation "
                         f"({', '.join(sorted(nonc))})"))
    else:
        for r in sorted(nonc):
            warnings.append(f"{r} unreliable — noncritical, warning only")
    return caps, warnings


SUPPRESS_FOR_FINANCIALS = {
    "FCF yield > 4% of enterprise value", "Owner earnings yield > 4%",
    "Owner earnings yield > 4.5%", "EV / EBITDA < 15", "EV / EBIT < 20",
    "Current ratio > 1.2", "Altman Z-score > 3.0",
    "Capex < 50% of operating cash flow", "Capex < 10% of revenue",
    "Capex < 1.5x D&A", "Net debt / EBITDA < 2.0x", "Interest coverage > 6x",
    "FCF / net income > 80%", "CFO / net income > 1.0",
    "Free cash flow positive every year", "FCF CAGR positive",
    "FCF margin > 10%", "EBITDA margin > 20%", "Owner earnings positive",
    "Cumulative FCF positive (all years)", "FCF per share growing",
    "FCF covers dividends", "Gross margin > 40%", "Gross margin > 35% every year",
    "Worst FCF decline > -30%", "CFO / EBITDA > 60%",
}


def _pe_vs_history(d):
    """(current_PE / median_historical_PE, percentile, n_years) or None.
    Historical PE per year = yearly close x diluted shares / net income."""
    px = _stooq_yearly_closes(d.ticker)
    ni = _yearly(d.inc, "Net Income")
    sh = _yearly(d.inc, "Diluted Average Shares", "Basic Average Shares")
    if not px or not ni or not sh:
        return None
    hist = []
    for y in sorted(set(px) & set(ni) & set(sh)):
        if ni[y] > 0 and sh[y] > 0:
            hist.append(px[y] * sh[y] / ni[y])
    if len(hist) < 4:
        return None
    cur = d.g("trailingPE")
    if cur is None:
        mcap, ni_l = d.g("marketCap"), _row(d.inc, "Net Income")
        if mcap and ni_l and ni_l[-1] > 0:
            cur = mcap / ni_l[-1]
    if cur is None or cur <= 0:
        return None
    med = sorted(hist)[len(hist) // 2]
    pct = 100 * sum(1 for h in hist if h < cur) / len(hist)
    return (cur / med if med > 0 else None, pct, len(hist))


# ============================================================================
# v8: 10-K text extraction — customer / product concentration (best-effort)
# ============================================================================

SCAN_10K = False              # --scan-10k
EXPORT_AUDIT = True           # --export-audit / off unless debug for universe runs
ALLOW_SPECIAL_COMPOUNDERS = False  # --allow-special-compounders

CALIBRATION_TICKERS = ["FDS", "BR", "JKHY", "ALLE", "AOS", "GGG", "MSA", "PTC",
                       "QLYS", "HRB", "DOCS", "EXLS", "DECK", "LULU", "ULTA",
                       "GDDY", "MLI", "COKE", "MEDP", "KNSL", "JPM", "CRUS",
                       "DPZ", "KO", "AAPL", "MSFT", "SPGI", "MCO", "V", "MA",
                       "COST", "ORLY", "AZO", "NVR", "WING", "TSCO"]
CALIBRATION_NOTES = {
    "FDS": "expect COMPOUNDER if valuation reasonable and EDGAR history loads",
    "DECK": "must NOT hard-reject on split dilution; footwear cap expected",
    "JPM": "expect SPECIAL MODEL; generic vs bank scores separated",
    "CRUS": "expect customer-concentration cap if Apple dependence detected",
    "KNSL": "expect SPECIAL MODEL (insurance), never plain COMPOUNDER",
    "HRB": "personal-services cap; check negative-equity handling",
    "AAPL": "quality mega-cap; likely QUALITY BUT EXPENSIVE at rich multiples",
    "MSFT": "quality mega-cap; valuation percentile likely high",
    "NVR": "homebuilder cap expected despite excellent economics",
    "AZO": "negative equity from buybacks — capped, not ELITE",
    "MEDP": "CRO/healthcare special handling",
    "MLI": "commodity module; margin-peak sensitivity",
}


class TenKScanner:
    """v9 SECTION 3: structured, materiality-aware 10-K text scan.
    Best-effort regex over the latest 10-K primary document. A None/False
    field means 'not detected', NOT 'not present'. Disk-cached 7 days."""

    IP_HEAVY = ("biotech", "pharma", "drug", "medical device", "medtech",
                "semiconductor", "licensing", "software")

    CUSTOMER_PATS = (
        r"(?:largest|one|a single) customer[^.]{0,160}?(\d{1,2}(?:\.\d)?)\s?%",
        r"customer (?:accounted for|represented) (?:approximately |about )?"
        r"(\d{1,2}(?:\.\d)?)\s?% of (?:our |total |net |consolidated )?(?:revenue|sales)",
        r"(\d{1,2}(?:\.\d)?)\s?% of (?:our |total |net )?(?:revenue|net sales|sales)"
        r"[^.]{0,60}?(?:one|a single|largest) customer",
    )

    def __init__(self, ticker, industry=""):
        self.ticker = ticker
        self.industry = (industry or "").lower()

    def scan(self):
        import re as _re
        f = {"scanned": False, "filing_url": None,
             "largest_customer_pct": None, "customer_excerpt": None,
             "major_customer_10pct": False, "no_customer_over_10pct": False,
             "supplier_concentration": False, "supplier_excerpt": None,
             "product_concentration": False, "product_excerpt": None,
             "patent_language_found": False, "patent_materiality": "none",
             "patent_cap_applied": False,
             "litigation_risk": False, "regulatory_risk": False,
             "going_concern": False, "material_weakness": False,
             "restatement": False, "auditor_change": False,
             "restructuring_language": False, "impairment_language": False,
             "single_product_risk": False, "patent_cliff_risk": False,
             "warnings": []}
        try:
            cik = _cik_for(self.ticker)
            if cik is None:
                return f
            subs = _edgar_get(f"https://data.sec.gov/submissions/CIK{cik}.json")
            recent = subs.get("filings", {}).get("recent", {})
            forms = recent.get("form", [])
            idx = next((i for i, x in enumerate(forms) if x == "10-K"), None)
            if idx is None:
                return f
            acc = recent["accessionNumber"][idx].replace("-", "")
            doc = recent["primaryDocument"][idx]
            url = f"https://www.sec.gov/Archives/edgar/data/{int(cik)}/{acc}/{doc}"
            html = requests.get(url, headers={"User-Agent": EDGAR_UA}, timeout=60).text
            time.sleep(0.15)
            txt = _re.sub(r"<[^>]+>", " ", html)
            txt = _re.sub(r"\s+", " ", txt).lower()[:2_500_000]
            f["scanned"] = True
            f["filing_url"] = url
            self._scan_text(txt, f)
        except Exception as e:
            f["warnings"].append(f"10-K fetch/scan failed: {type(e).__name__}")
        return f

    def _scan_text(self, txt, f):
        import re as _re

        def excerpt(m, span=120):
            s = max(0, m.start() - 40)
            return txt[s:m.end() + span].strip()[:220]

        # --- customer concentration ---
        if _re.search(r"no (?:single |one |individual )?customer (?:accounted for|"
                      r"represented) (?:more than |over |in excess of )?10", txt):
            f["no_customer_over_10pct"] = True
        pcts = []
        for pat in self.CUSTOMER_PATS:
            for m in _re.finditer(pat, txt):
                try:
                    v = float(m.group(1))
                    if 0 < v < 100:
                        pcts.append((v, excerpt(m)))
                except Exception:
                    continue
        if pcts:
            v, ex = max(pcts, key=lambda t: t[0])
            f["largest_customer_pct"] = v
            f["customer_excerpt"] = ex
        if _re.search(r"customers? (?:that |each |individually )?"
                      r"(?:accounted for|represented) (?:more than |at least |over )?10\s?%", txt):
            f["major_customer_10pct"] = True

        # --- supplier concentration ---
        m = _re.search(r"(?:single|sole) (?:supplier|source)[^.]{0,160}", txt) or \
            _re.search(r"depend(?:ent)? (?:up)?on (?:one|a single|a limited number of) "
                       r"suppliers?[^.]{0,160}", txt)
        if m:
            f["supplier_concentration"] = True
            f["supplier_excerpt"] = excerpt(m)

        # --- product concentration ---
        m = _re.search(r"substantially all of our (?:revenue|net sales|sales)[^.]{0,120}|"
                       r"(?:majority|substantial portion) of our (?:revenue|net sales)"
                       r"[^.]{0,80}?(?:single|one|principal|primary) (?:product|brand)|"
                       r"depend[s]? (?:substantially |primarily )?on (?:a single|one) product"
                       r"[^.]{0,120}", txt)
        if m:
            f["product_concentration"] = True
            f["single_product_risk"] = True
            f["product_excerpt"] = excerpt(m)

        # --- patent language with MATERIALITY (v9 fix: no boilerplate caps) ---
        if _re.search(r"patent", txt):
            f["patent_language_found"] = True
            material_phrases = _re.search(
                r"patents?[^.]{0,120}(?:are material to|material to our|essential to our|"
                r"critical to our) (?:business|revenue|operations)|"
                r"depend[s]? (?:substantially |materially |primarily )?(?:up)?on "
                r"(?:our |certain )?patents|exclusive license[^.]{0,80}(?:material|principal|primary)", txt)
            cliff = _re.search(r"(?:principal|primary|key|core) product[^.]{0,120}patent"
                               r"[^.]{0,80}expir|patents?[^.]{0,60}expir[^.]{0,60}"
                               r"(?:principal|primary|largest|core) product", txt)
            ip_heavy = any(k in self.industry for k in self.IP_HEAVY)
            if cliff and ip_heavy:
                f["patent_materiality"] = "critical"
                f["patent_cliff_risk"] = True
            elif cliff or (material_phrases and ip_heavy):
                f["patent_materiality"] = "material"
                f["patent_cliff_risk"] = bool(cliff)
            elif material_phrases:
                f["patent_materiality"] = "moderate"
            else:
                f["patent_materiality"] = "boilerplate"
                f["warnings"].append("Patent language found but appears "
                                     "boilerplate for this industry — no cap applied")

        # --- red flags ---
        f["going_concern"] = bool(_re.search(r"substantial doubt[^.]{0,60}going concern", txt))
        f["material_weakness"] = bool(_re.search(r"material weakness in (?:our )?internal control", txt))
        f["restatement"] = bool(_re.search(r"restat(?:ed|ement) (?:of )?(?:our |the )?"
                                           r"(?:previously issued )?(?:consolidated )?financial statements", txt))
        f["auditor_change"] = bool(_re.search(r"(?:dismissed|change[d]? (?:in|of)) "
                                              r"(?:our )?independent (?:registered public )?account", txt))
        f["litigation_risk"] = bool(_re.search(r"material adverse effect[^.]{0,80}litigation|"
                                               r"litigation[^.]{0,80}material adverse", txt))
        f["regulatory_risk"] = bool(_re.search(r"regulatory[^.]{0,60}material adverse|"
                                               r"material adverse[^.]{0,60}regulat", txt))
        f["reserve_development_adverse"] = bool(_re.search(
            r"(?:adverse|unfavorable) (?:prior[- ]year )?(?:loss )?reserve development", txt))
        f["catastrophe_exposure"] = bool(_re.search(
            r"catastroph(?:e|ic) (?:losses|events|exposure)", txt))
        f["restructuring_language"] = bool(_re.search(r"restructuring (?:charges|plan|costs)", txt))
        f["impairment_language"] = bool(_re.search(r"impairment charge", txt))


def _tenk_flags(ticker, industry=""):
    """Cached wrapper around TenKScanner (7-day disk cache)."""
    p = CACHE_DIR / f"tenk9_{ticker.upper()}.pkl"
    if USE_CACHE and p.exists() and (time.time() - p.stat().st_mtime) / 3600 < 24 * 7:
        try:
            with open(p, "rb") as fh:
                return pickle.load(fh)
        except Exception:
            pass
    flags = TenKScanner(ticker, industry).scan()
    try:
        CACHE_DIR.mkdir(exist_ok=True)
        with open(p, "wb") as fh:
            pickle.dump(flags, fh)
    except Exception:
        pass
    return flags


def _eseries_list(d, *tags):
    """EDGAR series as oldest->newest list, or None."""
    if d.edgar is None:
        return None
    s = d.edgar.series(*tags)
    if s is None:
        return None
    return [s[y] for y in sorted(s)]


def _module_score(checks):
    """checks: list of (name, bool|None). Returns (pct|None, details, confidence).
    confidence = % of module checks that were evaluable."""
    evaluable = [(n, v) for n, v in checks if v is not None]
    conf = round(100 * len(evaluable) / len(checks), 0) if checks else 0
    if len(evaluable) < 3:
        return None, checks, conf
    pct = round(100 * sum(1 for _, v in evaluable if v) / len(evaluable), 0)
    return pct, checks, conf


def bank_module(d):
    ni = _row(d.inc, "Net Income")
    ta = _row(d.bs, "Total Assets")
    se = _row(d.bs, "Stockholders Equity", "Common Stock Equity")
    nii = _eseries_list(d, "InterestIncomeExpenseNet",
                        "InterestIncomeExpenseAfterProvisionForLoanLoss")
    deposits = _eseries_list(d, "Deposits")
    nonint_exp = _eseries_list(d, "NoninterestExpense")
    nonint_inc = _eseries_list(d, "NoninterestIncome")
    checks = []
    roa = ni[-1] / ta[-1] if ni and ta and ta[-1] else None
    checks.append(("ROA > 1.0%", None if roa is None else roa > 0.010))
    roe = d.g("returnOnEquity")
    checks.append(("ROE > 10%", None if roe is None else roe > 0.10))
    eq_assets = se[-1] / ta[-1] if se and ta and ta[-1] else None
    checks.append(("Equity / assets > 8%", None if eq_assets is None else eq_assets > 0.08))
    checks.append(("Net interest income growing",
                   None if nii is None or len(nii) < 3 else nii[-1] > nii[0]))
    checks.append(("Deposits growing",
                   None if deposits is None or len(deposits) < 3 else deposits[-1] > deposits[0]))
    eff = None
    if nonint_exp and nii:
        rev_base = nii[-1] + (nonint_inc[-1] if nonint_inc else 0)
        if rev_base > 0:
            eff = nonint_exp[-1] / rev_base
    checks.append(("Efficiency ratio < 60%", None if eff is None else eff < 0.60))
    checks.append(("Net income positive every year",
                   None if ni is None or len(ni) < 3 else all(x > 0 for x in ni)))
    return _module_score(checks)


def insurance_module(d):
    """v14: 9 checks. Approximations from free data — combined ratio uses
    SG&A as the expense-ratio proxy; cycle test uses NI/premium vs history."""
    prem = _eseries_list(d, "PremiumsEarnedNet")
    claims = _eseries_list(d, "PolicyholderBenefitsAndClaimsIncurredNet",
                           "IncurredClaimsPropertyCasualtyAndLiability")
    sga = _row(d.inc, "Selling General And Administration",
               "Selling General And Administrative")
    bvps = _bvps_series(d)
    ni = _row(d.inc, "Net Income")
    se = _shareholders_equity(d)
    ta = _row(d.bs, "Total Assets")
    roe = d.g("returnOnEquity")
    sc = _share_cagr_adjusted(d)

    loss = claims[-1] / prem[-1] if prem and claims and prem[-1] > 0 else None
    exp = abs(sga[-1]) / prem[-1] if prem and sga and prem[-1] > 0 else None
    combined = (loss + exp) if loss is not None and exp is not None else None

    # underwriting cycle peak: current NI/premium vs window average
    cycle = None
    if ni is not None and prem is not None:
        n = min(len(ni), len(prem))
        margins = [a / b for a, b in zip(ni[-n:], prem[-n:]) if b > 0]
        if len(margins) >= 3 and sum(margins) != 0:
            avg = sum(margins) / len(margins)
            if avg > 0:
                cycle = margins[-1] / avg

    checks = [
        ("Premiums earned growing",
         None if prem is None or len(prem) < 3 else prem[-1] > prem[0]),
        ("Loss ratio < 70%", None if loss is None else loss < 0.70),
        ("Expense ratio (SG&A proxy) < 30%", None if exp is None else exp < 0.30),
        ("Combined ratio proxy < 100% (underwriting profit)",
         None if combined is None else combined < 1.00),
        ("Combined ratio proxy < 95% (real discipline)",
         None if combined is None else combined < 0.95),
        ("Underwriting margins not at cycle peak",
         None if cycle is None else cycle < 1.30),
        ("Book value / share compounding > 5%/yr",
         None if bvps is None else (_cagr(bvps) or 0) > 0.05),
        ("ROE > 10% without excess leverage",
         None if roe is None or se is None or ta is None or not ta[-1]
         else (roe > 0.10 and se / ta[-1] > 0.15)),
        ("No dilution (share discipline)",
         None if sc is None else sc < 0.02),
    ]
    return _module_score(checks)


def software_module(d):
    rev = _row(d.inc, "Total Revenue")
    sbc = _row(d.cf, "Stock Based Compensation")
    fcf = _row(d.cf, "Free Cash Flow")
    gm = d.g("grossMargins")
    rd = _eseries_list(d, "ResearchAndDevelopmentExpense")
    defrev = _eseries_list(d, "ContractWithCustomerLiabilityCurrent",
                           "ContractWithCustomerLiability", "DeferredRevenueCurrent")
    checks = []
    checks.append(("Revenue CAGR > 10%", None if rev is None else (_cagr(rev) or 0) > 0.10))
    checks.append(("Gross margin > 65%", None if gm is None else gm > 0.65))
    sbc_fcf = abs(sbc[-1]) / fcf[-1] if sbc and fcf and fcf[-1] > 0 else None
    checks.append(("SBC < 30% of FCF", None if sbc_fcf is None else sbc_fcf < 0.30))
    fcf_margin = fcf[-1] / rev[-1] if fcf and rev and rev[-1] > 0 else None
    checks.append(("FCF margin > 15%", None if fcf_margin is None else fcf_margin > 0.15))
    checks.append(("Deferred revenue growing (bookings health)",
                   None if defrev is None or len(defrev) < 3 else defrev[-1] > defrev[0]))
    rd_ratio = rd[-1] / rev[-1] if rd and rev and rev[-1] > 0 else None
    checks.append(("R&D 8-30% of revenue (investing, not starving)",
                   None if rd_ratio is None else 0.08 < rd_ratio < 0.30))
    return _module_score(checks)


def asset_manager_module(d):
    rev = _row(d.inc, "Total Revenue")
    m = _op_margins(d)
    roe = d.g("returnOnEquity")
    checks = [
        ("Revenue growing (proxy for AUM/flows)",
         None if rev is None or len(rev) < 3 else rev[-1] > rev[0]),
        ("Operating margin > 25%", None if m is None else m[-1] > 0.25),
        ("Operating margin stable", None if m is None else (_volatility(m) or 1) < 0.20),
        ("ROE > 12%", None if roe is None else roe > 0.12),
        ("No heavy dilution", None if _share_cagr(d) is None else _share_cagr(d) < 0.02),
    ]
    return _module_score(checks)


def retail_module(d):
    inv_v_sales = _inventory_vs_sales(d)
    gp = _row(d.inc, "Gross Profit")
    rev = _row(d.inc, "Total Revenue")
    gm = None
    if gp and rev and len(gp) == len(rev):
        gm = [g / r for g, r in zip(gp, rev) if r]
    mp = _margin_peak_ratio(d)
    checks = [
        ("Inventory growth <= sales growth (markdown risk)",
         None if inv_v_sales is None else inv_v_sales < 0.10),
        ("Gross margin stable (pricing power)",
         None if gm is None or len(gm) < 3 else gm[-1] >= gm[0] - 0.02),
        ("Margins not at cyclical/fashion peak", None if mp is None else mp < 1.25),
        ("Revenue growing through the window",
         None if rev is None or len(rev) < 3 else rev[-1] > rev[0]),
        ("FCF positive every year",
         (lambda f: None if f is None or len(f) < 3 else all(x > 0 for x in f))
         (_row(d.cf, "Free Cash Flow"))),
    ]
    return _module_score(checks)


def industrial_cyclical_module(d):
    mp = _margin_peak_ratio(d)
    ebit_wd = _worst_decline(_row(d.inc, "EBIT", "Operating Income"))
    nd = _net_debt_ebitda(d)
    roic = _roic_latest(d)
    checks = [
        ("Margins near mid-cycle (not peak)", None if mp is None else mp < 1.20),
        ("Worst EBIT drawdown > -30% (downturn resilience)",
         None if ebit_wd is None else ebit_wd > -0.30),
        ("Net debt / EBITDA < 1.5x (cycle buffer)", None if nd is None else nd < 1.5),
        ("Mid-cycle ROIC > 12%", None if roic is None else roic > 0.12),
        ("FCF positive through window",
         (lambda f: None if f is None or len(f) < 3 else all(x > 0 for x in f))
         (_row(d.cf, "Free Cash Flow"))),
    ]
    return _module_score(checks)


def healthcare_services_module(d):
    """CROs / healthcare services: reimbursement + client concentration risk."""
    rev = _row(d.inc, "Total Revenue")
    m = _op_margins(d)
    sc = _share_cagr(d)
    roic = _roic_latest(d)
    checks = [
        ("Revenue growing", None if rev is None or len(rev) < 3 else rev[-1] > rev[0]),
        ("Operating margin > 12%", None if m is None else m[-1] > 0.12),
        ("Margin stable (reimbursement pressure)",
         None if m is None else (_volatility(m) or 1) < 0.25),
        ("ROIC > 12%", None if roic is None else roic > 0.12),
        ("No heavy dilution (roll-up risk)", None if sc is None else sc < 0.02),
    ]
    return _module_score(checks)


def commodity_module(d):
    mp = _margin_peak_ratio(d)
    nd = _net_debt_ebitda(d)
    fcf = _row(d.cf, "Free Cash Flow")
    checks = [
        ("Margins NOT at commodity-price peak", None if mp is None else mp < 1.15),
        ("Net debt / EBITDA < 1.0x (price-crash buffer)",
         None if nd is None else nd < 1.0),
        ("FCF positive in every year of window",
         None if fcf is None or len(fcf) < 3 else all(x > 0 for x in fcf)),
        ("Low-cost proxy: FCF margin > 10% at current prices",
         (lambda f, r: None if f is None or r is None or r[-1] <= 0
          else f[-1] / r[-1] > 0.10)(fcf, _row(d.inc, "Total Revenue"))),
    ]
    return _module_score(checks)


def run_industry_module(d):
    """Returns (module_name, score, details, confidence) or (None,)*4."""
    text = f"{d.info.get('sector','')} {d.info.get('industry','')}".lower()
    if "bank" in text:
        return ("BANK",) + bank_module(d)
    if "insurance" in text:
        return ("INSURANCE",) + insurance_module(d)
    if "asset management" in text or "capital markets" in text:
        return ("ASSET MGR / CAP MKTS",) + asset_manager_module(d)
    if "software" in text:
        return ("SOFTWARE",) + software_module(d)
    if any(k in text for k in ("retail", "apparel", "footwear", "luxury",
                               "department store", "beauty")):
        return ("RETAIL/APPAREL",) + retail_module(d)
    if any(k in text for k in ("diagnostics & research", "healthcare services",
                               "medical care facilities", "drug manufacturers")):
        return ("HEALTHCARE/CRO",) + healthcare_services_module(d)
    if any(k in text for k in ("oil", "mining", "steel", "aluminum", "copper",
                               "chemicals", "paper", "lumber", "agricultural inputs")):
        return ("COMMODITY",) + commodity_module(d)
    ind_only = (d.info.get("industry") or "").lower()
    if any(k in ind_only for k in ("industrial", "machinery", "auto parts",
                                   "building products", "aerospace",
                                   "engineering", "construction", "farm")):
        return ("INDUSTRIAL/CYCLICAL",) + industrial_cyclical_module(d)
    return None, None, None, 0


def industry_caps(d):
    text = f"{d.info.get('sector','')} {d.info.get('industry','')}".lower()
    if "financial data" in text or "stock exchanges" in text:
        return None, [], False
    caps, reasons, special = [], [], False
    for kw, cap in SPECIAL_MODEL_KEYWORDS:
        if kw in text:
            caps.append(cap)
            reasons.append(f"{kw}: needs industry-specific model")
            special = True
    for kw, cap in RISK_CAP_KEYWORDS:
        if kw in text:
            caps.append(cap)
            reasons.append(f"{kw}: cyclical/brand/concentration/regulatory risk")
    return (min(caps) if caps else None), reasons, special


def financial_caps(d, checks):
    caps = []
    is_fin = _is_financial(d)
    nd = _net_debt_ebitda(d)
    if nd is not None and not is_fin:
        if nd > 3.0:
            caps.append((75, f"Net debt/EBITDA {nd:.1f}x > 3x"))
        elif nd > 2.0:
            caps.append((90, f"Net debt/EBITDA {nd:.1f}x > 2x"))
    sca_cap = share_count_analysis(d)
    sc = sca_cap["adjusted_cagr"]
    if sc is not None and sc > 0.02:
        caps.append((75, f"Dilution {sc*100:.1f}%/yr (split-adjusted)"))
    elif sca_cap["warning"] and "split artifact" in (sca_cap["warning"] or ""):
        caps.append((85, sca_cap["warning"]))
    conv = _fcf_conversion_ratio(d)
    if conv is not None and conv < 0.70 and not is_fin:
        caps.append((75, f"FCF conversion {conv*100:.0f}% < 70%"))
    gp = _row(d.inc, "Gross Profit")
    rev = _row(d.inc, "Total Revenue")
    if gp is not None and rev is not None and len(gp) >= 3 and len(gp) == len(rev):
        gm = [g / r for g, r in zip(gp, rev) if r]
        if gm and gm[-1] < gm[0] - 0.03:
            caps.append((75, f"Gross margin down {100*(gm[0]-gm[-1]):.1f}pp"))
    ar = _row(d.bs, "Accounts Receivable", "Receivables")
    if ar is not None and rev is not None and len(ar) >= 3 and len(rev) >= 3:
        n = min(len(ar), len(rev))
        if ar[-n] > 0 and rev[-n] > 0 and (ar[-1]/ar[-n] - 1) > (rev[-1]/rev[-n] - 1) + 0.25:
            caps.append((80, "Receivables growing much faster than revenue"))
    dfb_c = _debt_funded_buyback(d)
    nd_c = _net_debt_ebitda(d)
    ic_c = _interest_coverage(d)
    if dfb_c and nd_c is not None and nd_c > 2.5 and ic_c is not None and ic_c >= 6:
        caps.append((80, f"Aggressive debt-funded buybacks (ND/EBITDA {nd_c:.1f}x) — "
                         f"coverage {ic_c:.0f}x keeps it survivable, but verify"))
    acc = _accrual_ratio(d)
    if acc is not None and acc > 0.10:
        caps.append((75, f"High accruals ({acc*100:.0f}% of assets)"))
    pio = _piotroski(d)
    if pio is not None and pio <= 4 and not is_fin:
        caps.append((75, f"Piotroski F-score {pio:.0f}/9"))
    mp = _margin_peak_ratio(d)
    if mp is not None and mp > 1.4:
        caps.append((85, f"Margins {mp:.1f}x their multi-year average (peak-cycle risk)"))
    z = _altman_z(d)
    if z is not None and z < 1.8 and not is_fin:
        caps.append((65, f"Altman Z {z:.1f} (distress zone)"))
    if _negative_equity(d):
        cause = negative_equity_cause(d)
        ic_ne = _interest_coverage(d)
        fcf_ne = _row(d.cf, "Free Cash Flow")
        strong = ((ic_ne is not None and ic_ne >= 6)
                  and fcf_ne is not None and fcf_ne[-1] > 0)
        if cause == "buybacks" and strong:
            caps.append((80, "NEGATIVE equity from sustained buybacks (AZO/ORLY "
                             "pattern) — coverage & FCF strong; returns metrics "
                             "still unreliable"))
        elif cause == "operating_losses":
            caps.append((65, "NEGATIVE equity from accumulated operating losses"))
        else:
            caps.append((75, f"NEGATIVE shareholders' equity (cause: {cause or 'unknown'}; "
                             "returns metrics unreliable)"))
    rg = _reverse_dcf_implied_growth(d)
    if rg is not None and rg > 0.20 and not is_fin:
        caps.append((75, f"Reverse DCF implies {rg*100:.0f}%/yr owner-earnings growth "
                         f"(VERY EXPENSIVE — valuation concern, not a business flaw)"))
    elif rg is not None and rg > 0.15 and not is_fin:
        caps.append((90, f"Reverse DCF implies {rg*100:.0f}%/yr owner-earnings growth "
                         f"(priced for perfection)"))
    return caps


def negative_equity_cause(d):
    """buybacks / operating_losses / debt / unknown."""
    if not _negative_equity(d):
        return None
    ni = _row(d.inc, "Net Income")
    buy = _row(d.cf, "Repurchase Of Capital Stock", "Common Stock Payments")
    re_ = _row(d.bs, "Retained Earnings")
    se = _shareholders_equity(d)
    if ni is not None and len(ni) >= 3 and sum(1 for x in ni if x < 0) >= len(ni) / 2:
        return "operating_losses"
    cum_buy = sum(abs(x) for x in buy) if buy else 0.0
    if cum_buy > abs(se or 0) and (re_ is None or re_[-1] > 0 or
                                   (ni is not None and all(x > 0 for x in ni))):
        return "buybacks"
    nd = _net_debt_ebitda(d)
    if nd is not None and nd > 3:
        return "debt"
    return "unknown"


CONCENTRATION_REVIEW_KEYWORDS = (
    "semiconductor", "apparel", "footwear", "luxury",
    "health information", "healthcare plans", "medical devices",
    "diagnostics", "medical care", "drug manufacturers",
)


def needs_concentration_review(d, module_name=None):
    text = f"{d.info.get('sector','')} {d.info.get('industry','')}".lower()
    return (any(k in text for k in CONCENTRATION_REVIEW_KEYWORDS)
            or module_name in ("HEALTHCARE/CRO",))


def bank_valuation(d):
    """v10: valuation metrics that actually mean something for a bank."""
    out = {"p_b": None, "p_tbv": None, "p_e": None, "roa": None, "roe": None,
           "normalized_earnings_yield": None}
    mc = d.g("marketCap")
    se = _shareholders_equity(d)
    gw = _row(d.bs, "Goodwill")
    ni = _row(d.inc, "Net Income")
    ta = _row(d.bs, "Total Assets")
    if mc and se and se > 0:
        out["p_b"] = mc / se
        tbv = se - (gw[-1] if gw else 0)
        if tbv > 0:
            out["p_tbv"] = mc / tbv
    if mc and ni and ni[-1] > 0:
        out["p_e"] = mc / ni[-1]
    if ni and ta and ta[-1]:
        out["roa"] = ni[-1] / ta[-1]
    out["roe"] = d.g("returnOnEquity")
    if mc and ni and len(ni) >= 4:
        med_ni = sorted(ni)[len(ni) // 2]  # credit-cycle-adjusted proxy
        if med_ni > 0:
            out["normalized_earnings_yield"] = med_ni / mc
    return out


def _is_financial(d):
    text = f"{d.info.get('sector','')} {d.info.get('industry','')}".lower()
    return any(k in text for k in ("bank", "insurance", "capital markets",
                                   "credit services", "asset management",
                                   "financial conglomerates"))


def hard_gates(d, is_fin=False):
    """v9: returns (gates, suppressed). Gates fire only on RELIABLE economic
    problems. Data artifacts (unreliable rows, split artifacts) are moved to
    the suppressed list and become caps+warnings instead of rejections.
    is_fin=True: FCF/CFO/EBITDA/interest-coverage gates skipped for banks &
    insurers (deposits/float distort operating cash flow)."""
    gates, suppressed = [], []
    unrel = getattr(d, "unreliable", set())

    def add(msg, needs_rows=()):
        if any(r in unrel for r in needs_rows):
            suppressed.append(f"{msg} [SUPPRESSED: source row failed "
                              f"Yahoo/EDGAR reconciliation — verify manually]")
        else:
            gates.append(msg)

    if not is_fin:
        fcf = _row(d.cf, "Free Cash Flow")
        if fcf is not None and fcf[-1] < 0:
            add("Latest-year FCF negative", ("Free Cash Flow", "Operating Cash Flow"))
        if fcf is not None and len(fcf) >= 3:
            neg = sum(1 for x in fcf if x < 0)
            if neg / len(fcf) > 0.40:
                add(f"FCF negative in {neg}/{len(fcf)} years",
                    ("Free Cash Flow", "Operating Cash Flow"))
        ebit = _row(d.inc, "EBIT", "Operating Income")
        if ebit is not None and len(ebit) >= 3:
            neg = sum(1 for x in ebit if x < 0)
            if neg / len(ebit) > 0.30:
                add(f"EBIT negative in {neg}/{len(ebit)} years", ("Operating Income",))
        cfo = _row(d.cf, "Operating Cash Flow", "Cash Flow From Continuing Operating Activities")
        if cfo is not None and len(cfo) >= 3 and all(x < 0 for x in cfo[-2:]):
            add("Operating cash flow negative two years running", ("Operating Cash Flow",))
        nd = _net_debt_ebitda(d)
        if nd is not None and nd > 4.0:
            add("Net debt / EBITDA > 4x")
        ic = _interest_coverage(d)
        if ic is not None and ic < 3.0:
            add("Interest coverage < 3x", ("Operating Income", "Interest Expense"))
        cn = _cfo_ni_ratio(d)
        if cn is not None and cn < 0.70:
            add("CFO / net income < 0.7 (earnings not converting to cash)",
                ("Operating Cash Flow", "Net Income"))
        oe = _owner_earnings(d)
        fcf2 = _row(d.cf, "Free Cash Flow")
        if oe is not None and oe < 0 and (fcf2 is None or sum(fcf2) < 0):
            add("No positive owner earnings", ("Net Income", "Free Cash Flow"))
        dfb = _debt_funded_buyback(d)
        ic_g = _interest_coverage(d)
        if dfb and nd is not None and nd > 2.5 and (ic_g is None or ic_g < 6):
            add("Debt-funded buybacks with elevated leverage AND weak coverage")
    sca_g = share_count_analysis(d)
    adj = sca_g["adjusted_cagr"]
    if sca_g["dilution_hard_gate_allowed"] and adj is not None and adj > 0.05:
        gates.append(f"Dilution > 5%/yr (split-adjusted {adj*100:.1f}%/yr, "
                     f"evidence: {sca_g['dilution_evidence_level']})")
    elif (sca_g["raw_cagr"] is not None and sca_g["raw_cagr"] > 0.05
          and adj is not None and adj <= 0.05
          and sca_g["adjustment_applied"]
          and sca_g["reliability"] == "high"):
        pass  # resolved split: nothing to report
    elif sca_g["warning"] and "ARTIFACT" in sca_g["warning"].upper():
        suppressed.append(f"Dilution gate suppressed: {sca_g['warning']}")
    elif (sca_g["raw_cagr"] is not None and sca_g["raw_cagr"] > 0.05
          and (adj is None or adj <= 0.05)):
        suppressed.append(f"Dilution gate suppressed: raw share CAGR "
                          f"{sca_g['raw_cagr']*100:.1f}%/yr from "
                          f"UNRESOLVED suspected split artifact — verify manually")
    # v11: valuation NEVER hard-rejects — extreme reverse-DCF moved to caps
    return gates, suppressed


# ============================================================================
# Universe scraping
# ============================================================================

def get_universe(which="both"):
    urls = {
        "sp500": "https://en.wikipedia.org/wiki/List_of_S%26P_500_companies",
        "sp400": "https://en.wikipedia.org/wiki/List_of_S%26P_400_companies",
    }
    picks = ["sp500", "sp400"] if which == "both" else [which]
    tickers = []
    for key in picks:
        html = requests.get(urls[key], headers={"User-Agent": "Mozilla/5.0"}, timeout=30).text
        for tbl in pd.read_html(io.StringIO(html)):
            col = next((c for c in tbl.columns if str(c).lower() in ("symbol", "ticker symbol", "ticker")), None)
            if col is not None:
                tickers += [str(s).replace(".", "-").strip() for s in tbl[col].tolist()]
                break
    seen, out = set(), []
    for tk in tickers:
        if tk and tk not in seen:
            seen.add(tk)
            out.append(tk)
    return out


def get_full_us_universe(exchanges=("Nasdaq", "NYSE", "NYSE American")):
    """Fetch the full list of US-listed tickers from the SEC's own free file.

    Uses company_tickers_exchange.json (no key, no auth). Returns every common
    ticker on a major exchange, which is the real investable universe (~6,000)
    minus OTC/pink-sheet shells. This replaces the S&P-index scrape when the
    user wants the widest possible selection. Cached for 24h like everything
    else. Falls back to the S&P universe if the SEC file can't be reached.
    """
    cache = CACHE_DIR / "sec_universe.pkl"
    if USE_CACHE and cache.exists() and (time.time() - cache.stat().st_mtime) / 3600 < 24:
        try:
            return pickle.loads(cache.read_bytes())
        except Exception:
            pass
    url = "https://www.sec.gov/files/company_tickers_exchange.json"
    try:
        raw = requests.get(url, headers={"User-Agent": EDGAR_UA}, timeout=30).json()
    except Exception as e:
        print(f"  SEC universe fetch failed ({e}); falling back to S&P 500+400.")
        return get_universe("both")
    # Format: {"fields": ["cik","name","ticker","exchange"], "data": [[...], ...]}
    fields = [f.lower() for f in raw.get("fields", [])]
    try:
        ti = fields.index("ticker")
        xi = fields.index("exchange")
    except ValueError:
        print("  SEC universe format unexpected; falling back to S&P 500+400.")
        return get_universe("both")
    want = {e.lower() for e in exchanges}
    # Only exclude clearly-hyphenated non-common-stock instruments (warrants,
    # units, rights, preferred classes: e.g. BAC-PB, DSX-WT, F-PC). We do NOT
    # guess from trailing letters, because real companies end in W/U/R (LOW,
    # GWW, WWW). The bulk of remaining junk (ETFs, baby bonds, crypto funds)
    # has no SEC company mapping and is skipped at scoring time automatically.
    seen, out = set(), []
    for row in raw.get("data", []):
        tk = str(row[ti]).replace(".", "-").strip().upper()
        exch = str(row[xi] or "").lower()
        if not tk or tk in seen:
            continue
        if want and exch and exch not in want:
            continue
        # drop anything with a hyphen suffix (preferred/warrant/unit/right class)
        if "-" in tk:
            continue
        seen.add(tk)
        out.append(tk)
    if not out:
        return get_universe("both")
    try:
        CACHE_DIR.mkdir(exist_ok=True)
        cache.write_bytes(pickle.dumps(out))
    except Exception:
        pass
    return out


def quick_market_cap(ticker):
    """Cheap market-cap probe used to pre-filter BEFORE the expensive EDGAR
    score. Uses yfinance fast_info, which is a light quote call (no 10-year
    financial pull). Returns cap in dollars, or None if unavailable.

    This is the single change that makes a full-universe run feasible: it lets
    us discard the thousands of names outside the Buffett cap band without ever
    paying for their full financial history.
    """
    cache = CACHE_DIR / f"cap_{ticker.upper().replace('/', '-')}.pkl"
    if USE_CACHE and cache.exists() and (time.time() - cache.stat().st_mtime) / 3600 < 24:
        try:
            return pickle.loads(cache.read_bytes())
        except Exception:
            pass
    cap = None
    try:
        fi = yf.Ticker(ticker).fast_info
        cap = fi.get("market_cap") if hasattr(fi, "get") else getattr(fi, "market_cap", None)
    except Exception:
        cap = None
    try:
        CACHE_DIR.mkdir(exist_ok=True)
        cache.write_bytes(pickle.dumps(cap))
    except Exception:
        pass
    return cap


# ============================================================================
# Scoring
# ============================================================================

def _build_financial_history(d):
    """Year-keyed statement history for the QuantHub JSON export (additive)."""
    fh = {}
    def add(name, yd):
        if yd:
            for y, v in yd.items():
                fh.setdefault(int(y), {})[name] = v
    add("revenue",          _yearly(d.inc, "Total Revenue"))
    add("net_income",       _yearly(d.inc, "Net Income"))
    add("gross_profit",     _yearly(d.inc, "Gross Profit"))
    add("operating_income", _yearly(d.inc, "Operating Income"))
    add("shares_diluted",   _yearly(d.inc, "Diluted Average Shares",
                                    "Basic Average Shares"))
    add("free_cash_flow",   _yearly(d.cf, "Free Cash Flow"))
    add("capex",            _yearly(d.cf, "Capital Expenditure"))
    add("total_debt",       _yearly(d.bs, "Total Debt"))
    add("cash",             _yearly(d.bs, "Cash And Cash Equivalents"))
    add("equity",           _yearly(d.bs, "Stockholders Equity",
                                    "Common Stock Equity"))
    return fh


def score_stock(ticker, sector=None):
    d = Data(ticker)
    if not d.info or (d.g("marketCap") is None):
        return None
    if sector and sector.lower() not in str(d.info.get("sector", "")).lower():
        return "SECTOR_SKIP"

    checks, cat_scores, total = {}, [], 0.0
    val_pts, val_weight = 0.0, 12
    acct_ok = True
    bs_fail = False
    critical_missing = 0
    is_fin = _is_financial(d)
    suppressed_generic = []
    data_suppressed_rules = []
    applicable_weight = 0.0
    for cat_name, weight, rules in CATEGORIES:
        per_rule = weight / len(rules)
        earned, applicable, detail = 0.0, 0.0, []
        n_suppressed = 0
        for rule_name, fn in rules:
            if is_fin and rule_name in SUPPRESS_FOR_FINANCIALS:
                detail.append((rule_name, "N/A"))
                suppressed_generic.append(rule_name)
                n_suppressed += 1
                continue
            deps = RULE_ROW_DEPS.get(rule_name)
            if deps and deps & getattr(d, "unreliable", set()):
                detail.append((rule_name, "DATA?"))
                data_suppressed_rules.append(rule_name)
                n_suppressed += 1
                continue
            r = fn(d)
            checks[rule_name] = r
            detail.append((rule_name, r))
            if r is not None:
                applicable += per_rule
                if r:
                    earned += per_rule
            elif cat_name.startswith(("3.", "6.")):
                critical_missing += 1  # missing data in returns/balance sheet
        cat_weight_eff = weight * (len(rules) - n_suppressed) / len(rules)
        cat_pts = cat_weight_eff * (earned / applicable) if applicable else 0.0
        if cat_name.startswith("12."):
            val_pts = cat_pts
            val_weight = max(cat_weight_eff, 0.001)
        if cat_name.startswith("8.") and applicable and (earned / applicable) < 0.5:
            acct_ok = False
        if cat_name.startswith("6.") and applicable and (earned / applicable) < 0.75:
            bs_fail = True  # more than ~2 balance-sheet rules failed
        cat_scores.append((cat_name, cat_pts, cat_weight_eff, detail))
        total += cat_pts
        applicable_weight += cat_weight_eff

    binary_pct = round(100 * total / applicable_weight, 1) if applicable_weight else 0.0
    graded, graded_table = graded_metric_scores(d, is_fin=is_fin)
    # v9 SECTION 5: final raw score leans on graded scores (no cliff effects)
    if graded is not None:
        raw = round(0.4 * binary_pct + 0.6 * graded, 1)
    else:
        raw = binary_pct
    generic_score = raw

    passed = sum(1 for v in checks.values() if v is True)
    scored = sum(1 for v in checks.values() if v is not None)
    missing = [name for name, v in checks.items() if v is None]
    rule_conf = round(100 * scored / len(checks), 0) if checks else 0
    rev_series = _row(d.inc, "Total Revenue")
    history_years = len(rev_series) if rev_series else 0

    ind_cap, ind_reasons, special = industry_caps(d)
    module_name, module_score, module_detail, module_conf = run_industry_module(d)
    # v9 SECTION 7: blended special score
    blended = None
    if special:
        if module_score is not None and module_conf >= 70:
            blended = round(0.7 * module_score + 0.3 * generic_score, 1)
            raw = blended
        else:
            ind_reasons.append("special model has insufficient data "
                               f"(module confidence {module_conf:.0f}% < 70)")
            ind_cap = min(ind_cap or 75, 75)
    if (module_score is not None and module_score >= 70 and ind_cap is not None):
        ind_cap = max(ind_cap, 90)
        ind_reasons.append(f"{module_name} module passed ({module_score:.0f}/100): "
                           f"cap relaxed to {ind_cap}")
    fin = financial_caps(d, checks)
    all_caps = ([(ind_cap, "; ".join(ind_reasons))] if ind_cap is not None else []) + fin

    # --- v9 SECTION 10: multi-component confidence ---
    sca = share_count_analysis(d)
    tenk = _tenk_flags(ticker, d.info.get("industry", "")) if SCAN_10K else {"scanned": False}
    pvh = _pe_vs_history(d)
    conf_parts = {
        "rules_evaluable": rule_conf,
        "history": min(100, 30 + history_years * 8),
        "source": 100 if getattr(d, "source", "") in ("yahoo+edgar", "cache") else 70,
        "reconciliation": max(40, 100 - sum(
            {"critical": 20, "important": 8, "noncritical": 3}[row_criticality(r)]
            for r in getattr(d, "unreliable", set()))
            - 3 * max(0, len(getattr(d, "recon_warnings", []))
                      - len(getattr(d, "unreliable", set())))),
        "industry_classification": 100 if d.info.get("sector") or d.info.get("industry") else 40,
        "tenk_scan": 100 if tenk.get("scanned") else (80 if not SCAN_10K else 50),
        "per_share": {"high": 100, "medium": 70, "low": 50}[sca["reliability"]],
        "valuation_history": 100 if pvh else 70,
        "module": module_conf if special else 100,
    }
    confidence = round(sum(conf_parts.values()) / len(conf_parts), 0)

    # --- data-quality caps (missing/unreliable data must hurt) ---
    if confidence < 60:
        all_caps.append((65, f"Overall confidence {confidence:.0f}% < 60%"))
    elif confidence < 70:
        all_caps.append((75, f"Overall confidence {confidence:.0f}% < 70%"))
    elif confidence < 80:
        all_caps.append((85, f"Overall confidence {confidence:.0f}% < 80%"))
    elif confidence < 90:
        all_caps.append((90, f"Overall confidence {confidence:.0f}% < 90%"))
    if history_years < 5:
        all_caps.append((75, f"Only {history_years} years of history (<5)"))
    elif history_years < 7:
        all_caps.append((85, f"Only {history_years} years of history (<7); "
                             f"cycle behavior unproven"))
    if getattr(d, "source", "") == "edgar+stooq":
        all_caps.append((85, "Synthetic valuation data (Yahoo unavailable)"))
    if not d.info.get("sector") and not d.info.get("industry"):
        all_caps.append((85, "Unknown sector/industry: risk caps could not be applied"))
    recon_caps, recon_row_warnings = reconciliation_caps(getattr(d, "unreliable", set()))
    all_caps.extend(recon_caps)
    if sca["warning"] and ("split artifact" in sca["warning"]
                           or "DATA ARTIFACT" in sca["warning"]):
        all_caps.append((85, sca["warning"]))

    # --- valuation vs own history (P/E is valid for banks too) ---
    if pvh is not None and pvh[0] is not None:
        ratio, pctile, n = pvh
        if ratio > 2.0:
            all_caps.append((80, f"P/E {ratio:.1f}x its {n}-yr median "
                                 f"({pctile:.0f}th percentile of own history)"))
        elif ratio > 1.5:
            all_caps.append((85, f"P/E {ratio:.1f}x its {n}-yr median "
                                 f"({pctile:.0f}th percentile of own history)"))

    # --- v9 SECTION 8: valuation V2 caps (v10: suppressed for financials —
    #     FCF/OE/DCF math is meaningless for banks; bank_valuation replaces it) ---
    v2 = valuation_v2(d) if not is_fin else {
        "normalized_fcf": None, "normalized_fcf_yield": None,
        "base_dcf_value": None, "bear_dcf_value": None,
        "mos_base": None, "mos_bear": None, "valuation_warning": None}
    bank_val = bank_valuation(d) if is_fin else None
    rg_now = _reverse_dcf_implied_growth(d) if not is_fin else None
    if pvh and pvh[1] is not None and not is_fin:
        oe_y = _owner_earnings_yield(d)
        if pvh[1] > 90 and rg_now is not None and rg_now > 0.12:
            all_caps.append((80, f"Valuation {pvh[1]:.0f}th pctile of own history AND "
                                 f"reverse DCF implies {rg_now*100:.0f}%/yr"))
        elif pvh[1] > 80 and oe_y is not None and oe_y < 0.04:
            all_caps.append((85, f"Valuation {pvh[1]:.0f}th pctile with OE yield "
                                 f"{oe_y*100:.1f}% < 4%"))
    if v2["normalized_fcf_yield"] is not None and v2["normalized_fcf_yield"] < 0.03:
        all_caps.append((80, f"Normalized (mid-cycle) FCF yield "
                             f"{v2['normalized_fcf_yield']*100:.1f}% < 3%"))
    if v2["mos_base"] is not None and v2["mos_base"] < 0:
        all_caps.append((85, "No margin of safety vs base-case DCF of "
                             "normalized owner earnings"))
    if v2["mos_bear"] is not None and v2["mos_bear"] < -0.40:
        all_caps.append((80, f"Bear-case DCF implies {abs(v2['mos_bear'])*100:.0f}% downside"))

    # --- v9 SECTION 3: scanner findings with materiality tiers ---
    if tenk.get("scanned"):
        pct = tenk.get("largest_customer_pct")
        if pct is not None and pct >= 70:
            all_caps.append((65, f"10-K: largest customer ~{pct:.0f}% of revenue (EXTREME)"))
        elif pct is not None and pct >= 40:
            all_caps.append((75, f"10-K: largest customer ~{pct:.0f}% of revenue"))
        elif pct is not None and pct >= 20:
            all_caps.append((90, f"10-K: largest customer ~{pct:.0f}% of revenue"))
        elif tenk.get("major_customer_10pct") and not tenk.get("no_customer_over_10pct"):
            all_caps.append((90, "10-K: customer(s) >=10% of revenue disclosed"))
        if tenk.get("single_product_risk"):
            all_caps.append((85, "10-K: single-product / concentrated revenue language"))
        # patent materiality tiers (boilerplate = warning only, NO cap)
        pm = tenk.get("patent_materiality", "none")
        if pm == "critical":
            all_caps.append((70, "10-K: CRITICAL patent-cliff exposure"))
            tenk["patent_cap_applied"] = True
        elif pm == "material":
            all_caps.append((80, "10-K: patents material to revenue"))
            tenk["patent_cap_applied"] = True
        elif pm == "moderate":
            all_caps.append((90, "10-K: moderate patent dependence"))
            tenk["patent_cap_applied"] = True
        if tenk.get("going_concern"):
            all_caps.append((50, "10-K: GOING CONCERN doubt"))
        if tenk.get("material_weakness") and tenk.get("restatement"):
            all_caps.append((60, "10-K: material weakness + restatement"))
        if tenk.get("supplier_concentration"):
            all_caps.append((90, "10-K: single/sole supplier dependence"))
        if is_fin and tenk.get("reserve_development_adverse"):
            all_caps.append((85, "10-K: adverse reserve development language"))
        if is_fin and tenk.get("catastrophe_exposure") and module_name == "INSURANCE":
            all_caps.append((90, "10-K: material catastrophe exposure language"))

    # Global cap: nothing above 95 unless valuation, leverage, accounting all pass
    nd = _net_debt_ebitda(d)
    lev_ok = nd is None or nd < 2.0 or is_fin
    val_ok = val_pts >= val_weight * 0.5 or (is_fin and special)
    if not (val_ok and lev_ok and acct_ok):
        all_caps.append((95, "95 cap: valuation, leverage, or accounting not all clean"))

    cap_reasons = [f"capped at {c}: {why}" for c, why in all_caps]
    final = min([raw] + [c for c, _ in all_caps]) if all_caps else raw
    # Universal ceiling (spec): quantitative data alone never proves moat,
    # concentration, or management quality — those need the 10-K.
    if final > 95.0:
        final = 95.0
        cap_reasons.append("capped at 95: qualitative factors (moat, customer "
                           "concentration, management) require manual 10-K validation")

    gates, suppressed_gates = hard_gates(d, is_fin=is_fin)
    if suppressed_gates:
        all_caps.append((85, f"{len(suppressed_gates)} hard gate(s) suppressed as "
                             f"data artifacts — manual verification required"))
        cap_reasons = [f"capped at {c}: {why}" for c, why in all_caps]
        final = min([final] + [c for c, _ in all_caps])

    # --- STRICT ELITE: no caps of ANY kind, no gates, clean critical data ---
    elite_ok = (not all_caps and not gates and not suppressed_gates and not special
                and critical_missing == 0 and not bs_fail
                and confidence >= 90 and val_ok and lev_ok and acct_ok
                and getattr(d, "source", "") != "edgar+stooq"
                and (tenk.get("scanned") or not SCAN_10K))

    # --- v8 item 2: strict verdict bands ---
    # 90+ = COMPOUNDER only; 80-89 = QUALITY BUT CAPPED / QUALITY BUT
    # EXPENSIVE / WATCHLIST; special models can never be normal compounders.
    hard_risk_caps = [c for c, _ in all_caps if c <= 90]
    if gates:
        verdict = "REJECT (hard gate)"
    elif special and raw >= 60:
        if ALLOW_SPECIAL_COMPOUNDERS and blended is not None and final >= 90:
            verdict = f"COMPOUNDER CANDIDATE (SPECIAL — {module_name} blended {blended:.0f})"
        elif module_score is not None:
            verdict = (f"SPECIAL MODEL ({module_name} {module_score:.0f}/100, "
                       f"blended {blended:.0f})" if blended is not None
                       else f"SPECIAL MODEL ({module_name} sub-score {module_score:.0f}/100)")
        else:
            verdict = "SPECIAL MODEL REQUIRED"
    elif final >= 95 and elite_ok:
        verdict = "ELITE COMPOUNDER CANDIDATE"
    elif final >= 90 and not hard_risk_caps:
        verdict = "COMPOUNDER CANDIDATE"
    elif final >= 90:  # 90+ held back by a risk cap (DECK pattern)
        verdict = "HIGH QUALITY · WATCH PRICE"
    elif final >= 85:  # v11: FDS at 88.5 is not a 70-point watchlist name
        if not val_ok:
            verdict = "QUALITY BUT EXPENSIVE"
        elif hard_risk_caps:
            verdict = "HIGH QUALITY · WATCH PRICE"
        else:
            verdict = "QUALITY COMPOUNDER WATCHLIST"
    elif final >= 80:
        verdict = "QUALITY BUT EXPENSIVE" if not val_ok else "HIGH QUALITY · WATCH PRICE"
    elif final >= 70:
        if not val_ok and (graded or 0) >= 75:
            verdict = "WATCHLIST: GREAT BUSINESS, BAD PRICE"
        else:
            verdict = "WATCHLIST ONLY"
    elif final >= 60:
        verdict = "REJECT / WATCH ONLY"
    else:
        verdict = "REJECT"

    # --- key metrics for output ---
    fcf_i, ev_i = d.g("freeCashflow"), d.g("enterpriseValue")
    fcf_yield = fcf_i / ev_i if fcf_i and ev_i and ev_i > 0 else None
    key = {
        "ev": ev_i,
        "fcf_yield": fcf_yield,
        "oe_yield": _owner_earnings_yield(d),
        "oe_conservative": _owner_earnings_conservative(d),
        "oe_per_share": _oe_per_share(d),
        "roic": _roic_latest(d),
        "nd_ebitda": _net_debt_ebitda(d),
        "interest_cov": _interest_coverage(d),
        "fcf_conv": _fcf_conversion_ratio(d),
        "rev_cagr": _cagr(_row(d.inc, "Total Revenue")),
        "fcf_cagr": _cagr(_row(d.cf, "Free Cash Flow")),
        "share_cagr": _share_cagr(d),
        "implied_growth": _reverse_dcf_implied_growth(d),
        "pe_vs_hist": pvh,
    }
    key["pos_fcf_years"], key["pos_ebit_years"] = _pos_year_counts(d)
    key["raw_share_cagr"] = sca["raw_cagr"]
    key["adj_share_cagr"] = sca["adjusted_cagr"]
    key["valuation_percentile"] = pvh[1] if pvh else None
    key["mos_base"] = v2["mos_base"]
    key["mos_bear"] = v2["mos_bear"]
    key["normalized_fcf_yield"] = v2["normalized_fcf_yield"]
    bba = buyback_analysis(d)

    # --- v9 SECTION 6: moat sub-scores (proxies only; never sufficient) ---
    gp_m, rev_m = _row(d.inc, "Gross Profit"), _row(d.inc, "Total Revenue")
    gm_series = ([g / r for g, r in zip(gp_m, rev_m) if r]
                 if gp_m and rev_m and len(gp_m) == len(rev_m) else None)
    moat_subs = {
        "return_durability": score_threshold_high(_roic_latest(d), 0.08, 0.15, 0.30),
        "pricing_power": (score_stability(_volatility(gm_series), 0.03, 0.08, 0.20)
                          if gm_series else None),
        "capital_light": score_threshold_high(
            (d.g("freeCashflow") or 0) / rev_m[-1] if rev_m and rev_m[-1] else None,
            0.05, 0.12, 0.25),
        "scale_or_leverage": graded_table.get("Operating margin", (None, None))[1],
        "stickiness": (100.0 if tenk.get("no_customer_over_10pct")
                       else (30.0 if tenk.get("largest_customer_pct") else None)),
    }
    moat_avail = [v for v in moat_subs.values() if v is not None]
    moat_score = round(sum(moat_avail) / len(moat_avail), 0) if moat_avail else None
    moat_guess = max((k for k, v in moat_subs.items() if v is not None),
                     key=lambda k: moat_subs[k], default=None)

    # --- v8 item 10: explicit manual-review checklist ---
    manual_items = ["moat type & durability (proxies are NOT proof)",
                    "management quality & incentives",
                    "buyback price discipline", "regulatory/litigation exposure",
                    "your own conservative DCF"]
    conc_flag = needs_concentration_review(d, module_name)
    if conc_flag:
        manual_items.insert(0, "CUSTOMER CONCENTRATION diligence — this industry "
                               "pattern (semis/healthcare/apparel) frequently hides "
                               "one dominant customer or channel; read the 10-K "
                               "concentration section FIRST")
    if tenk.get("supplier_concentration"):
        manual_items.insert(0, "supplier concentration (10-K flagged sole/single supplier)")
    if tenk.get("product_concentration"):
        manual_items.insert(0, "product concentration (10-K flagged)")
    if tenk.get("scanned"):
        pct = tenk.get("largest_customer_pct")
        if tenk.get("no_customer_over_10pct"):
            conc = "10-K scan: no customer >10% (verify in filing)"
        elif pct is not None:
            conc = f"10-K scan: largest customer ~{pct:.0f}% — read the concentration section"
        else:
            conc = "customer/product concentration (scan found no clear disclosure)"
    else:
        conc = "customer/product concentration (NOT scanned; use --scan-10k)"
    manual_items.insert(0, conc)
    manual_review_required = "YES — " + "; ".join(manual_items)

    # --- strengths & concerns ---
    def _coverage(detail):
        ev = sum(1 for _, v in detail if v is not None and v != "N/A")
        tot = sum(1 for _, v in detail if v != "N/A")
        return ev / tot if tot else 0
    strengths = [f"{name.split('. ', 1)[-1]} ({pts:.0f}/{w:.0f})"
                 for name, pts, w, det in cat_scores
                 if w and pts / w >= 0.95 and _coverage(det) >= 0.6][:4]
    failed = [name for name, v in checks.items() if v is False]
    concerns = [fail_concern(n) for n in failed[:4]]
    for c, why in all_caps[:2]:
        concerns.append(f"CAP {c}: {why}")
    if final >= 95 and not elite_ok:
        concerns.append("Scored 95+ but failed the ELITE checklist "
                        "(caps/missing data/balance sheet)")

    # --- v11: valuation label ---
    if is_fin or (special and module_name):
        _t = f"{d.info.get('sector','')} {d.info.get('industry','')}".lower()
        if "insurance" in _t:
            valuation_label = "See insurance valuation"
        elif "bank" in _t:
            valuation_label = "See bank valuation"
        elif "asset management" in _t or "capital markets" in _t:
            valuation_label = "See asset manager valuation"
        elif is_fin:
            valuation_label = "See bank valuation"
        else:
            valuation_label = "See special-industry valuation"
    if not is_fin and not (special and module_name):
        _pctile = pvh[1] if pvh else None
        if rg_now is not None and rg_now > 0.15 or (v2["mos_bear"] is not None
                                                    and v2["mos_bear"] < -0.40):
            valuation_label = "VERY EXPENSIVE"
        elif ((rg_now is not None and rg_now > 0.10)
              or (_pctile is not None and _pctile > 80)
              or (v2["mos_base"] is not None and v2["mos_base"] < 0)):
            valuation_label = "EXPENSIVE"
        elif ((rg_now is not None and rg_now < 0.06)
              and (_pctile is None or _pctile < 60)):
            valuation_label = "ATTRACTIVE"
        elif rg_now is not None or _pctile is not None:
            valuation_label = "FAIR"
        else:
            valuation_label = "UNKNOWN"

    # --- v10: model reliability grade (trust in the SCORE, not the business) ---
    unrel = getattr(d, "unreliable", set())
    crit_unrel = any(row_criticality(r) == "critical" for r in unrel)
    unresolved_split = bool(sca["warning"] and "split artifact" in sca["warning"])
    if (confidence >= 90 and history_years >= 8 and not unrel
            and not unresolved_split and len(getattr(d, "recon_warnings", [])) <= 1):
        reliability_grade = "A"
    elif confidence >= 80 and not crit_unrel and not unresolved_split:
        reliability_grade = "B"
    elif confidence >= 70 and not crit_unrel:
        reliability_grade = "C"
    elif confidence >= 60:
        reliability_grade = "D"
    else:
        reliability_grade = "F"

    # --- v11: research queue tier ---
    _cyc_mod = module_name in ("RETAIL/APPAREL", "INDUSTRIAL/CYCLICAL",
                               "COMMODITY", "HEALTHCARE/CRO")
    if gates:
        research_queue = "Tier 5: Avoid / Reject"
    elif special:
        if (blended is not None and blended >= 85
                and reliability_grade in ("A", "B")):
            research_queue = "Tier 1C: Special-model research"
        else:
            research_queue = "Tier 3: Special Model"
    elif final >= 85 and valuation_label in ("ATTRACTIVE", "FAIR", "UNKNOWN") \
            and reliability_grade in ("A", "B"):
        if hard_risk_caps or _cyc_mod:
            research_queue = "Tier 1B: Capped/cyclical high-quality research"
        else:
            research_queue = "Tier 1A: Normal compounder research"
    elif final >= 80 or verdict in ("QUALITY BUT EXPENSIVE",
                                    "WATCHLIST: GREAT BUSINESS, BAD PRICE"):
        research_queue = "Tier 2: Quality but Capped / Wait for Price"
    elif final >= 70:
        research_queue = "Tier 4: Watchlist Only"
    else:
        research_queue = "Tier 5: Avoid / Reject"

    return {
        "ticker": ticker.upper(),
        "name": d.info.get("shortName", ticker.upper()),
        "sector": d.info.get("sector", ""),
        "industry": d.info.get("industry", ""),
        "mcap": d.g("marketCap"),
        "history_years": history_years,
        "source": getattr(d, "source", "yahoo+edgar"),
        "module_name": module_name,
        "module_score": module_score,
        "module_detail": module_detail,
        "tenk": tenk,
        "manual_review_required": manual_review_required,
        "generic_score": generic_score,
        "blended_score": blended,
        "binary_pct": binary_pct,
        "graded_score": graded,
        "graded_table": graded_table,
        "module_confidence": module_conf,
        "confidence_breakdown": conf_parts,
        "recon_warnings": list(getattr(d, "recon_warnings", [])),
        "unreliable_rows": sorted(getattr(d, "unreliable", set())),
        "suppressed_gates": suppressed_gates,
        "suppressed_generic_rules": suppressed_generic,
        "split_analysis": sca,
        "buybacks": bba,
        "moat_score": moat_score,
        "moat_subs": moat_subs,
        "moat_type_guess": moat_guess,
        "valuation_v2": v2,
        "bank_valuation": bank_val,
        "model_reliability_grade": reliability_grade,
        "valuation_label": valuation_label,
        "research_queue": research_queue,
        "negative_equity_cause": negative_equity_cause(d),
        "concentration_review_needed": conc_flag,
        "data_warnings": (recon_row_warnings
                          + list(getattr(d, "recon_warnings", []))
                          + ([sca["warning"]] if sca["warning"] else [])),
        "data_suppressed_rules": data_suppressed_rules,
        "raw": raw,
        "score": round(final, 1),
        "passed": passed,
        "scored": scored,
        "confidence": confidence,
        "verdict": verdict,
        "gates": gates,
        "caps": cap_reasons,
        "cats": cat_scores,
        "missing": missing,
        "checks": checks,
        "key": key,
        "strengths": strengths,
        "concerns": concerns,
        "from_cache": getattr(d, "from_cache", False),
        "current_price": d.g("currentPrice") or d.g("regularMarketPrice"),
        "financial_history": _build_financial_history(d),
    }


def _fmt_pct(v):
    return f"{v*100:.1f}%" if v is not None else "?"

def _fmt_x(v):
    if v is None:
        return "?"
    return "inf" if v == float("inf") else f"{v:.1f}x"

def print_report(r):
    mc = f"${r['mcap']/1e9:.1f}B" if r["mcap"] else "?"
    print(f"\n{'='*64}\n{r['ticker']} — {r['name']}  ({r['industry']}, {mc})")
    raw_note = f" (raw {r['raw']})" if r["score"] != r["raw"] else ""
    print(f"SCORE: {r['score']}/100{raw_note}   RULES PASSED: {r['passed']}/{r['scored']}"
          f"   DATA CONFIDENCE: {r['confidence']:.0f}%   HISTORY: {r['history_years']}yr"
          f"   RELIABILITY: {r['model_reliability_grade']}   [{r['source']}]")
    if r["source"] == "edgar+stooq":
        print("  NOTE: Yahoo unavailable — market cap/EV rebuilt from SEC filings + "
              "Stooq price. Valuation approximate; industry caps NOT applied "
              "(sector unknown). Verify before trusting high scores.")
    print(f"VERDICT: {r['verdict']}   VALUATION: {r['valuation_label']}   "
          f"{r['research_queue']}")
    gs = r.get("generic_score")
    print(f"SCORES: binary {r['binary_pct']} | graded {r['graded_score']} | "
          f"generic {gs}" + (f" | blended(special) {r['blended_score']}"
                             if r.get("blended_score") is not None else ""))
    sa = r["split_analysis"]
    if sa["split_events"] or sa["warning"] or (sa.get("raw_cagr") or 0) > 0.05:
        ev = sa.get("evidence") or {}
        def _sh(v):
            return f"{v/1e6:.1f}M" if v else "?"
        def _d(v):
            return f"${v/1e9:.2f}B" if v else "$0"
        print(f"  SHARE-COUNT RECONCILIATION:")
        print(f"     raw shares {_sh(sa['begin_raw'])} -> {_sh(sa['end_raw'])} "
              f"(CAGR {_fmt_pct(sa['raw_cagr'])}) | split-adjusted "
              f"{_sh(sa['begin_adjusted'])} -> {_sh(sa['end_adjusted'])} "
              f"(CAGR {_fmt_pct(sa['adjusted_cagr'])})")
        print(f"     splits: {sa['split_events'] or 'none'}")
        print(f"     buybacks {_d(ev.get('buy_total'))} | issuance "
              f"{_d(ev.get('iss_total'))} | SBC {_d(ev.get('sbc_total'))} | "
              f"evidence: {sa['dilution_evidence_level']} | "
              f"gate allowed: {sa['dilution_hard_gate_allowed']}")
        if sa["warning"]:
            print(f"     !! {sa['warning']}")
    for w in r["recon_warnings"][:4]:
        print(f"  ~ RECON: {w}")
    for sg in r["suppressed_gates"]:
        print(f"  ~ SUPPRESSED GATE: {sg}")
    if r.get("bank_valuation"):
        bv = r["bank_valuation"]
        def _f(v, pct=False):
            if v is None: return "?"
            return f"{v*100:.1f}%" if pct else f"{v:.2f}x"
        print(f"  BANK VALUATION: P/B {_f(bv['p_b'])} | P/TBV {_f(bv['p_tbv'])} | "
              f"P/E {_f(bv['p_e'])} | ROA {_f(bv['roa'], True)} | "
              f"ROE {_f(bv['roe'], True)} | NormEarnYld {_f(bv['normalized_earnings_yield'], True)}")
    if r.get("data_warnings"):
        print(f"  DATA WARNINGS (not economic problems):")
        for w in r["data_warnings"][:5]:
            print(f"     ~ {w}")
    if r.get("moat_score") is not None:
        print(f"  MOAT PROXY: {r['moat_score']:.0f}/100 (best evidence: "
              f"{r['moat_type_guess']}) — manual moat review ALWAYS required")
    if r["module_name"]:
        ms = f"{r['module_score']:.0f}/100" if r["module_score"] is not None else "insufficient data"
        print(f"  INDUSTRY MODULE [{r['module_name']}]: {ms}")
        for name, ok in (r["module_detail"] or []):
            mark = "✓" if ok else ("✗" if ok is False else "? no data")
            print(f"     [{mark}] {name}")
    k = r["key"]
    print(f"KEY: FCF yld {_fmt_pct(k['fcf_yield'])} | OE yld {_fmt_pct(k['oe_yield'])} | "
          f"ROIC {_fmt_pct(k['roic'])} | ND/EBITDA {_fmt_x(k['nd_ebitda'])} | "
          f"Cov {_fmt_x(k['interest_cov'])} | RevCAGR {_fmt_pct(k['rev_cagr'])} | "
          f"ShCAGR(adj) {_fmt_pct(k['adj_share_cagr'])} | "
          f"RevDCF implies {_fmt_pct(k['implied_growth'])}/yr | "
          f"ValPctile {k['valuation_percentile'] if k['valuation_percentile'] is not None else '?'} | "
          f"MoS(base) {_fmt_pct(k['mos_base'])}")
    for g in r["gates"]:
        print(f"  !! HARD GATE: {g}")
    for c in r["caps"]:
        print(f"  ~ CAP: {c}")
    if r["strengths"]:
        print(f"  + STRENGTHS: {'; '.join(r['strengths'])}")
    if r["concerns"]:
        print(f"  - CONCERNS (economic): {'; '.join(r['concerns'])}")
    for cat_name, pts, weight, detail in r["cats"]:
        print(f"  {cat_name}  [{pts:.1f}/{weight}]")
        for rule_name, ok in detail:
            if ok == "N/A":
                mark = "— n/a for this industry"
            elif ok == "DATA?":
                mark = "! suppressed: source data failed reconciliation"
            elif ok is None:
                mark = "? no data"
            elif ok:
                mark = "✓"
            else:
                mark = "✗"
            print(f"     [{mark}] {rule_name}")
    if r["missing"]:
        print(f"  MISSING DATA ({len(r['missing'])} rules not evaluable): "
              + ", ".join(r["missing"]))
    if r.get("from_cache"):
        print("  (data served from local cache)")
    print(f"  MANUAL REVIEW REQUIRED: {r['manual_review_required']}")


# ============================================================================
# v13: self-contained HTML dashboard export
# ============================================================================

# ============================================================
# JSON EXPORT FOR QUANTHUB (additive only)
# ============================================================
import json
import math

def _num(x):
    try:
        if x is None:
            return None
        v = float(x)
        if math.isnan(v) or math.isinf(v):
            return None
        return int(v) if v == int(v) and abs(v) < 1e15 else v
    except (TypeError, ValueError):
        return None

def export_screener_json(results, path="screener_data.json"):
    out = []
    for r in results:
        fh = r.get("financial_history") or {}
        fin = {}
        for yr in sorted(fh.keys(), reverse=True):
            row = fh[yr]
            fin[str(yr)] = {
                "revenue":          _num(row.get("revenue")),
                "free_cash_flow":   _num(row.get("free_cash_flow")),
                "net_income":       _num(row.get("net_income")),
                "total_debt":       _num(row.get("total_debt")),
                "cash":             _num(row.get("cash")),
                "shares_diluted":   _num(row.get("shares_diluted")),
                "gross_profit":     _num(row.get("gross_profit")),
                "operating_income": _num(row.get("operating_income")),
                "capex":            _num(row.get("capex")),
                "equity":           _num(row.get("equity")),
            }
        latest_yr = next(iter(fin), None)
        latest_src = fin.get(latest_yr, {})
        latest = {k: latest_src.get(k) for k in
                  ("revenue", "free_cash_flow", "total_debt", "cash", "shares_diluted")}
        out.append({
            "ticker":                r.get("ticker"),
            "company_name":          r.get("name"),
            "sector":                r.get("sector"),
            "market_cap":            _num(r.get("mcap")),
            "current_price":         _num(r.get("current_price")),
            "final_score":           _num(r.get("score")),
            "market_adjusted_score": _num(r.get("market_adjusted_score")),
            "verdict_tier":          r.get("verdict"),
            "confidence":            _num(r.get("confidence")),
            "latest":                latest,
            "financials":            fin,
        })
    with open(path, "w", encoding="utf-8") as f:
        json.dump(out, f, indent=2)
    print(f"[export] wrote {len(out)} companies -> {path}")


def _dash_payload(results):
    """Serialize results to the compact JSON the dashboard needs.

    Returns (rows_json, market_json). market_json is the shared market-climate
    object (or 'null' when the overlay is off).
    """
    import json
    def num(v):
        if v is None:
            return None
        if isinstance(v, float) and (math.isnan(v) or math.isinf(v)):
            return None
        return v

    rows = []
    for r in results:
        k = r["key"]
        sa = r["split_analysis"]
        rows.append({
            "t": r["ticker"], "n": r["name"], "sec": r["sector"],
            "ind": r["industry"], "mc": num(r["mcap"]),
            "s": num(r["score"]), "raw": num(r["raw"]),
            "v": r["verdict"], "q": r["research_queue"],
            "vl": r["valuation_label"], "rg": r["model_reliability_grade"],
            "cf": num(r["confidence"]), "hy": r["history_years"],
            "src": r["source"], "mod": r["module_name"] or "",
            "mods": num(r["module_score"]),
            "fcfy": num(k["fcf_yield"]), "oey": num(k["oe_yield"]),
            "roic": num(k["roic"]), "nde": num(k["nd_ebitda"]),
            "rcagr": num(k["rev_cagr"]), "shcagr": num(k["adj_share_cagr"]),
            "ig": num(k["implied_growth"]), "vp": num(k["valuation_percentile"]),
            "grade_ca": r["buybacks"]["capital_allocation_grade"],
            "strengths": r["strengths"], "concerns": r["concerns"],
            "caps": r["caps"], "gates": r["gates"],
            "supp": r["suppressed_gates"], "dw": r.get("data_warnings", [])[:6],
            "manual": r["manual_review_required"],
            "mas": num(r.get("market_adjusted_score")),
            "mreg": (r.get("market") or {}).get("market_regime"),
            "shrec": {"br": num(sa["begin_raw"]), "er": num(sa["end_raw"]),
                      "ba": num(sa["begin_adjusted"]), "ea": num(sa["end_adjusted"]),
                      "ev": sa["dilution_evidence_level"],
                      "warn": sa["warning"] or ""},
        })
    # Shared market-climate object (same for all rows); pull from first result.
    mkt = None
    for r in results:
        if r.get("market"):
            m = r["market"]
            mkt = {
                "regime": m.get("market_regime"),
                "score": num(m.get("market_score_0_100")),
                "fpe": num(m.get("market_forward_pe")),
                "fpeb": m.get("market_forward_pe_bucket"),
                "bi_gnp": num(m.get("buffett_indicator_gnp")),
                "bi_gdp": num(m.get("buffett_indicator_gdp")),
                "bib": m.get("buffett_indicator_bucket"),
                "cape": num(m.get("market_cape")),
                "capeb": m.get("cape_bucket"),
                "t10": num(m.get("treasury_10y")),
                "t3m": num(m.get("tbill_3m")),
                "sp10": num(m.get("equity_yield_spread_vs_10y")),
                "ir": m.get("interest_rate_gravity_label"),
                "ps": num(m.get("corporate_profit_share_pct")),
                "psw": m.get("profit_share_warning"),
                "mos": m.get("suggested_margin_of_safety_addon_pct"),
                "pos": m.get("market_positioning"),
                "rel": m.get("market_data_reliability"),
                "adj": any(r.get("market_adjusted_score") is not None
                           for r in results),
            }
            break
    return json.dumps(rows), json.dumps(mkt)


DASHBOARD_TEMPLATE = r"""<!DOCTYPE html>
<html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Buffett Quality Screener</title>
<style>
:root{
  --bg:#0A0F14; --bg2:#0F1620; --panel:#131E29; --panel2:#182634;
  --line:#223243; --line2:#2C4155;
  --ink:#EAF1F7; --dim:#8DA2B6; --faint:#5B7088;
  --brass:#D9B45F; --brass-dim:#7d6636; --brass-glow:rgba(217,180,95,.14);
  --teal:#54D6B4; --teal-dim:#276657;
  --coral:#EB8368; --coral-dim:#7a4436;
  --amber:#E4B84F; --violet:#9E8FE6;
  --mono:'SFMono-Regular',ui-monospace,'JetBrains Mono','Cascadia Code',Menlo,Consolas,monospace;
  --sans:'Inter',-apple-system,BlinkMacSystemFont,'Segoe UI',Roboto,sans-serif;
}
*{box-sizing:border-box;margin:0;padding:0}
html{scroll-behavior:smooth}
body{background:var(--bg);color:var(--ink);font-family:var(--sans);font-size:14px;
  line-height:1.5;-webkit-font-smoothing:antialiased;
  background-image:radial-gradient(1100px 520px at 82% -8%,rgba(217,180,95,.05),transparent),
    radial-gradient(820px 460px at -8% 8%,rgba(84,214,180,.045),transparent);
  background-attachment:fixed}
@media (prefers-reduced-motion:reduce){*{animation:none!important;transition:none!important}}
.wrap{max-width:1240px;margin:0 auto;padding:0 20px}

/* masthead */
.mast{padding:30px 0 0;display:flex;align-items:center;justify-content:space-between;gap:20px;flex-wrap:wrap}
.mast h1{font-size:20px;font-weight:700;letter-spacing:-.02em;display:flex;align-items:center;gap:11px}
.mast h1 .dot{width:9px;height:9px;border-radius:50%;background:var(--brass);box-shadow:0 0 0 4px var(--brass-glow)}
.mast .disc{font-family:var(--mono);font-size:10px;color:var(--faint);text-align:right;line-height:1.6;letter-spacing:.02em}

/* tab bar */
.tabbar{display:flex;gap:4px;margin:22px 0 0;border-bottom:1px solid var(--line)}
.tab{background:none;border:none;color:var(--dim);font-family:var(--sans);font-size:14.5px;font-weight:600;
  padding:12px 20px;cursor:pointer;position:relative;transition:color .15s;letter-spacing:-.01em}
.tab:hover{color:var(--ink)}
.tab.on{color:var(--brass)}
.tab.on::after{content:"";position:absolute;left:16px;right:16px;bottom:-1px;height:2px;background:var(--brass);border-radius:2px}
.tab .cnt{font-family:var(--mono);font-size:11px;color:var(--faint);margin-left:7px;font-weight:400}
.view{display:none}.view.on{display:block}

/* ============ STOCKS TAB ============ */
.controls{position:sticky;top:0;z-index:20;background:rgba(10,15,20,.9);backdrop-filter:blur(12px);
  border-bottom:1px solid var(--line);margin:0 -20px;padding:13px 20px}
.controls .inner{max-width:1240px;margin:0 auto;display:flex;gap:11px;align-items:center;flex-wrap:wrap}
#q{flex:1;min-width:180px;background:var(--panel);border:1px solid var(--line2);color:var(--ink);
  padding:9px 14px;border-radius:9px;font-size:13.5px;font-family:var(--sans);transition:border-color .15s,box-shadow .15s}
#q::placeholder{color:var(--faint)}
#q:focus{outline:none;border-color:var(--brass-dim);box-shadow:0 0 0 3px var(--brass-glow)}
.seg{display:flex;background:var(--panel);border:1px solid var(--line2);border-radius:9px;overflow:hidden}
.seg button{background:none;border:none;color:var(--dim);font-family:var(--mono);font-size:11px;
  letter-spacing:.02em;padding:8px 12px;cursor:pointer;transition:.15s;white-space:nowrap}
.seg button:hover{color:var(--ink)}
.seg button.on{background:var(--brass);color:#12100a;font-weight:600}
.qtoggle{display:flex;align-items:center;gap:8px;background:var(--panel);border:1px solid var(--line2);
  border-radius:9px;padding:8px 13px;cursor:pointer;user-select:none;transition:.15s}
.qtoggle:hover{border-color:var(--brass-dim)}
.qtoggle.on{border-color:var(--brass);background:var(--brass-glow)}
.qtoggle .sw{width:30px;height:16px;border-radius:9px;background:var(--line2);position:relative;transition:.15s;flex-shrink:0}
.qtoggle.on .sw{background:var(--brass)}
.qtoggle .sw::after{content:"";position:absolute;top:2px;left:2px;width:12px;height:12px;border-radius:50%;
  background:var(--ink);transition:.15s}
.qtoggle.on .sw::after{left:16px;background:#12100a}
.qtoggle span{font-family:var(--mono);font-size:11px;color:var(--dim)}
.qtoggle.on span{color:var(--brass)}
.shown{font-family:var(--mono);font-size:11px;color:var(--faint);white-space:nowrap;margin-left:auto}
.shown b{color:var(--brass)}

.tiers{display:flex;gap:8px;flex-wrap:wrap;margin:16px 0 4px}
.chip{background:var(--panel);border:1px solid var(--line);border-radius:20px;padding:6px 13px;cursor:pointer;
  display:flex;align-items:center;gap:8px;transition:.15s;user-select:none}
.chip:hover{border-color:var(--line2);transform:translateY(-1px)}
.chip .cn{font-size:12px;color:var(--dim)}
.chip .cc{font-family:var(--mono);font-size:11px;color:var(--faint);background:var(--bg);padding:1px 7px;border-radius:9px}
.chip.on{background:var(--brass);border-color:var(--brass)}
.chip.on .cn{color:#12100a;font-weight:600}.chip.on .cc{color:#12100a;background:rgba(0,0,0,.15)}
.chip .swatch{width:7px;height:7px;border-radius:50%}
.t1 .swatch{background:var(--teal)}.t2 .swatch{background:var(--brass)}
.t3 .swatch{background:var(--violet)}.t4 .swatch{background:var(--amber)}.t5 .swatch{background:var(--coral)}

.list{margin:14px 0 44px;display:grid;gap:9px}
.card{background:linear-gradient(180deg,var(--panel),var(--bg2));border:1px solid var(--line);border-radius:13px;
  overflow:hidden;transition:border-color .15s,box-shadow .15s}
.card:hover{border-color:var(--line2);box-shadow:0 8px 30px -14px rgba(0,0,0,.7)}
.card.opened{border-color:var(--brass-dim)}
.head{display:grid;grid-template-columns:48px 1fr auto;gap:16px;align-items:center;padding:15px 18px;cursor:pointer}
.rank{font-family:var(--mono);font-size:19px;color:var(--faint);font-weight:600;text-align:center}
.idy{min-width:0}
.idy .tk{font-family:var(--mono);font-weight:700;font-size:17px;color:var(--ink)}
.idy .co{color:var(--dim);font-size:12.5px;margin-top:1px;white-space:nowrap;overflow:hidden;text-overflow:ellipsis;max-width:44ch}
.idy .meta{display:flex;gap:7px;flex-wrap:wrap;margin-top:7px}
.tag{font-family:var(--mono);font-size:10px;letter-spacing:.02em;padding:2px 8px;border-radius:6px;
  border:1px solid var(--line2);color:var(--dim);background:var(--bg)}
.tag.verdict{border-color:var(--v-b,var(--line2));color:var(--v-c,var(--dim));background:var(--v-bg,var(--bg))}
.tag.val{border-color:var(--vl-b,var(--line2));color:var(--vl-c,var(--dim))}
.tag.rel{color:var(--faint)}
.scores{display:flex;align-items:center;gap:15px}
.scols{display:flex;flex-direction:column;align-items:flex-end;gap:3px;min-width:112px}
.masrow{display:flex;align-items:baseline;gap:7px}
.masrow .big{font-family:var(--mono);font-size:27px;font-weight:700;line-height:1}
.masrow .of{font-family:var(--mono);font-size:11px;color:var(--faint)}
.qrow{font-family:var(--mono);font-size:10.5px;color:var(--faint);display:flex;align-items:center;gap:5px}
.qrow .delta{padding:0 5px;border-radius:5px;font-weight:600}
.delta.dn{color:var(--coral);background:rgba(235,131,104,.1)}
.delta.up{color:var(--teal);background:rgba(84,214,180,.1)}
.delta.flat{color:var(--faint)}
.qmode .masrow .big{color:var(--teal)}
.gauge{width:62px;height:62px;position:relative;flex-shrink:0}
.gauge svg{transform:rotate(-90deg)}
.gauge .gt{position:absolute;inset:0;display:flex;align-items:center;justify-content:center;font-family:var(--mono);font-size:11px;color:var(--dim);font-weight:600}
.s-hi{color:var(--brass)}.s-mid{color:var(--teal)}.s-lo{color:var(--dim)}

.detail{border-top:1px solid var(--line);padding:18px;display:none;
  background:radial-gradient(560px 200px at 100% 0,rgba(158,143,230,.05),transparent)}
.card.opened .detail{display:block}
.cols{display:grid;grid-template-columns:1.15fr 1fr 1fr;gap:20px}
.blk h4{font-family:var(--mono);font-size:10px;letter-spacing:.08em;text-transform:uppercase;color:var(--faint);
  margin-bottom:9px;padding-bottom:6px;border-bottom:1px solid var(--line)}
.kv div{display:flex;justify-content:space-between;gap:12px;padding:4px 0;border-bottom:1px dotted var(--line);font-size:12.5px}
.kv span:first-child{color:var(--dim)}.kv span:last-child{font-family:var(--mono);color:var(--ink)}
.kv .hl span:last-child{color:var(--brass);font-weight:600}
.blk ul{list-style:none;display:flex;flex-direction:column;gap:5px}
.blk li{font-size:12px;line-height:1.45;padding-left:16px;position:relative;color:var(--dim)}
.blk li::before{content:"";position:absolute;left:2px;top:7px;width:5px;height:5px;border-radius:1px;background:var(--faint)}
.blk li.g{color:#c2ede0}.blk li.g::before{background:var(--teal)}
.blk li.b{color:#f2c6b9}.blk li.b::before{background:var(--coral)}
.manual{margin-top:16px;padding:11px 14px;background:var(--bg);border:1px solid var(--line);border-left:3px solid var(--amber);
  border-radius:8px;font-size:12px;color:var(--dim);line-height:1.5}
.manual b{color:var(--amber);font-family:var(--mono);font-size:10px;letter-spacing:.06em;text-transform:uppercase;display:block;margin-bottom:3px}
.empty{text-align:center;padding:60px 20px;color:var(--dim)}.empty b{color:var(--ink);display:block;margin-bottom:6px}

/* ============ MARKET TAB ============ */
.mkt{padding:22px 0 50px}
.mkt-hero{display:grid;grid-template-columns:280px 1fr;gap:28px;align-items:center;
  background:linear-gradient(180deg,var(--panel),var(--bg2));border:1px solid var(--line);border-radius:18px;
  padding:28px 30px;position:relative;overflow:hidden}
.mkt-hero::before{content:"";position:absolute;inset:0 auto 0 0;width:4px;background:var(--regcol,var(--brass))}
.dial{position:relative;width:250px;height:250px;margin:0 auto}
.dial .lbl{position:absolute;inset:0;display:flex;flex-direction:column;align-items:center;justify-content:center;text-align:center}
.dial .lbl .rname{font-family:var(--mono);font-size:15px;font-weight:700;letter-spacing:.03em;color:var(--regcol,var(--brass));margin-bottom:4px}
.dial .lbl .rscore{font-family:var(--mono);font-size:46px;font-weight:700;line-height:1;color:var(--ink)}
.dial .lbl .rcap{font-family:var(--mono);font-size:10px;letter-spacing:.1em;text-transform:uppercase;color:var(--faint);margin-top:6px}
.mkt-hero .say h2{font-size:15px;font-weight:600;color:var(--faint);letter-spacing:.06em;text-transform:uppercase;font-family:var(--mono);margin-bottom:10px}
.mkt-hero .say .pos{font-size:19px;line-height:1.5;color:var(--ink);font-weight:500;max-width:52ch}
.mkt-hero .say .mos{margin-top:16px;display:inline-flex;align-items:center;gap:10px;font-family:var(--mono);font-size:13px;
  color:var(--brass);border:1px solid var(--brass-dim);background:var(--brass-glow);padding:7px 14px;border-radius:9px}

.mkt-grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(340px,1fr));gap:16px;margin-top:20px}
.rule{background:linear-gradient(180deg,var(--panel),var(--bg2));border:1px solid var(--line);border-radius:14px;overflow:hidden}
.rule .rh{padding:16px 18px 14px;display:flex;justify-content:space-between;align-items:flex-start;gap:14px}
.rule .rt{font-size:14px;font-weight:600;color:var(--ink)}
.rule .rsub{font-family:var(--mono);font-size:10.5px;color:var(--faint);margin-top:3px;letter-spacing:.02em}
.rule .rval{text-align:right;flex-shrink:0}
.rule .rval .v{font-family:var(--mono);font-size:22px;font-weight:700;line-height:1}
.rule .rval .b{font-family:var(--mono);font-size:9.5px;letter-spacing:.04em;text-transform:uppercase;margin-top:4px}
/* horizontal band meter */
.band{margin:0 18px;height:34px;border-radius:8px;position:relative;overflow:hidden;
  background:linear-gradient(90deg,var(--teal-dim),#3a5f2e 30%,var(--brass-dim) 60%,var(--coral-dim));border:1px solid var(--line)}
.band .zones{position:absolute;inset:0;display:flex}
.band .zone{flex:1;border-right:1px solid rgba(0,0,0,.25)}
.band .needle{position:absolute;top:-3px;bottom:-3px;width:3px;background:var(--ink);box-shadow:0 0 8px rgba(255,255,255,.5);border-radius:2px;transition:left .5s}
.band .needle::after{content:"";position:absolute;top:-5px;left:50%;transform:translateX(-50%);
  border-left:5px solid transparent;border-right:5px solid transparent;border-top:6px solid var(--ink)}
.bandscale{display:flex;justify-content:space-between;margin:6px 18px 0;font-family:var(--mono);font-size:9px;color:var(--faint)}
.rule .learn{margin:14px 18px 0;border-top:1px solid var(--line);padding-top:0}
.rule .learn summary{list-style:none;cursor:pointer;padding:12px 0;font-family:var(--mono);font-size:11px;
  color:var(--brass);display:flex;align-items:center;gap:7px;user-select:none}
.rule .learn summary::-webkit-details-marker{display:none}
.rule .learn summary::before{content:"+";display:inline-block;width:14px;height:14px;line-height:13px;text-align:center;
  border:1px solid var(--brass-dim);border-radius:4px;font-size:12px}
.rule .learn[open] summary::before{content:"\2212"}
.rule .learn .body{font-size:12.5px;line-height:1.6;color:var(--dim);padding-bottom:16px;max-width:60ch}
.rule .learn .body b{color:var(--ink)}
.mkt-note{margin-top:22px;font-family:var(--mono);font-size:10.5px;color:var(--faint);line-height:1.7;
  border-top:1px solid var(--line);padding-top:16px}
.mkt-empty{text-align:center;padding:70px 20px;color:var(--dim)}
.mkt-empty b{color:var(--ink);display:block;margin-bottom:8px;font-size:16px}

.foot{border-top:1px solid var(--line);margin-top:24px;padding:22px 0 44px;font-family:var(--mono);font-size:10.5px;color:var(--faint);line-height:1.7}
.foot b{color:var(--dim)}

@media (max-width:860px){
  .cols{grid-template-columns:1fr}
  .mkt-hero{grid-template-columns:1fr;gap:18px}
  .dial{width:210px;height:210px}
  .head{grid-template-columns:40px 1fr;gap:12px}
  .scores{grid-column:1/-1;justify-content:flex-end;margin-top:6px;padding-top:12px;border-top:1px solid var(--line)}
  .mast .disc{text-align:left}
}
</style></head>
<body>
<div class="wrap">
<header class="mast">
  <h1><span class="dot"></span>Buffett Quality Screener</h1>
  <div class="disc">EDUCATIONAL RESEARCH — NOT INVESTMENT ADVICE<br>verify before acting</div>
</header>

<nav class="tabbar">
  <button class="tab on" data-v="stocks">Stocks<span class="cnt" id="tabcnt">0</span></button>
  <button class="tab" data-v="market">Market Climate</button>
</nav>

<!-- STOCKS VIEW -->
<section class="view on" id="view-stocks">
  <div class="controls"><div class="inner">
    <input id="q" placeholder="Search ticker, company, or industry…" autocomplete="off">
    <div class="seg" id="sortseg">
      <button data-k="mas" class="on">Score</button>
      <button data-k="oey">OE yield</button>
      <button data-k="roic">ROIC</button>
      <button data-k="mc">Size</button>
    </div>
    <div class="qtoggle" id="qtoggle" title="Rank by business quality only, ignoring price and market">
      <span class="sw"></span><span>Quality only</span>
    </div>
    <span class="shown"><b id="nshow">0</b> shown</span>
  </div></div>
  <div class="tiers" id="tiers"></div>
  <div class="list" id="list"></div>
</section>

<!-- MARKET VIEW -->
<section class="view" id="view-market">
  <div class="mkt" id="mkt"></div>
</section>

<footer class="foot">
  <b>Method:</b> 80 rules across 12 categories · 10-year SEC EDGAR history reconciled with Yahoo Finance · valuation caps scores, never gates.<br>
  <b>Score</b> = quality blended with market climate · <b>Quality only</b> = the business on its own merits, price ignored.
</footer>
</div>

<script>
const DATA=__DATA__;
const MARKET=__MARKET__;
const TLABEL={"Tier 1A":"Normal compounders","Tier 1B":"Capped/cyclical quality","Tier 1C":"Special-model research","Tier 1":"Research first","Tier 2":"Capped / wait for price","Tier 3":"Special model","Tier 4":"Watchlist","Tier 5":"Avoid / reject"};
const REGCOL={FAT_PITCH:"#54D6B4",PANIC_OPPORTUNITY:"#54D6B4",NORMAL:"#54D6B4",ELEVATED:"#E4B84F",EXPENSIVE:"#EB8368",VERY_EXPENSIVE:"#EB8368",PLAYING_WITH_FIRE:"#EB8368",MIXED_OR_INCOMPLETE_DATA:"#8DA2B6"};
const TIERS=[...new Set(DATA.map(r=>r.q.split(":")[0]))].sort();
let tierOn=null, query="", sortK="mas", qualityOnly=false, open=null;

const pct=v=>v==null?"—":(v*100).toFixed(1)+"%";
const x=v=>v==null?"—":v.toFixed(1)+"x";
const bn=v=>v==null?"—":v>=1e9?"$"+(v/1e9).toFixed(1)+"B":"$"+(v/1e6).toFixed(0)+"M";
const tierOf=r=>r.q.split(":")[0];
const sCls=v=>v==null?"s-lo":v>=85?"s-hi":v>=70?"s-mid":"s-lo";
// headline: market-adjusted normally, pure quality in "quality only" mode
const headScore=r=>qualityOnly?r.s:(r.mas!=null?r.mas:r.s);

/* ---- tabs ---- */
document.querySelectorAll(".tab").forEach(t=>t.onclick=()=>{
  document.querySelectorAll(".tab").forEach(x=>x.classList.remove("on"));
  document.querySelectorAll(".view").forEach(x=>x.classList.remove("on"));
  t.classList.add("on");
  document.getElementById("view-"+t.dataset.v).classList.add("on");
  if(t.dataset.v==="market") renderMarket();
});

/* ---- tier chips ---- */
function tierClass(t){return "t"+(t.includes("1")?1:t.includes("2")?2:t.includes("3")?3:t.includes("5")?5:4);}
function renderTiers(){
  const el=document.getElementById("tiers");el.innerHTML="";
  const all=document.createElement("div");
  all.className="chip"+(tierOn===null?" on":"");
  all.innerHTML=`<span class="cn">All tiers</span><span class="cc">${DATA.length}</span>`;
  all.onclick=()=>{tierOn=null;renderList();};el.appendChild(all);
  TIERS.forEach(t=>{
    const n=DATA.filter(r=>tierOf(r)===t).length;
    const d=document.createElement("div");
    d.className="chip "+tierClass(t)+(tierOn===t?" on":"");
    d.innerHTML=`<span class="swatch"></span><span class="cn">${TLABEL[t]||t}</span><span class="cc">${n}</span>`;
    d.onclick=()=>{tierOn=tierOn===t?null:t;renderList();};
    el.appendChild(d);
  });
}

function rows(){
  let rs=DATA.filter(r=>!tierOn||tierOf(r)===tierOn);
  if(query){const s=query.toLowerCase();
    rs=rs.filter(r=>(r.t+" "+r.n+" "+r.ind+" "+r.sec).toLowerCase().includes(s));}
  rs.sort((a,b)=>{
    const k=sortK==="mas"?null:sortK;
    const av=k?a[k]:headScore(a), bv=k?b[k]:headScore(b);
    if(av==null)return 1; if(bv==null)return -1; return bv-av;});
  return rs;
}

function verdictStyle(v){
  if(v.includes("REJECT")||v.includes("hard gate"))return["var(--coral-dim)","var(--coral)","rgba(235,131,104,.07)"];
  if(v.includes("COMPOUNDER")&&!v.includes("WATCHLIST"))return["var(--brass-dim)","var(--brass)","var(--brass-glow)"];
  if(v.includes("SPECIAL"))return["var(--violet)","var(--violet)","rgba(158,143,230,.08)"];
  if(v.includes("EXPENSIVE"))return["var(--amber)","var(--amber)","rgba(228,184,79,.07)"];
  if(v.includes("WATCH PRICE")||v.includes("WATCHLIST"))return["var(--teal-dim)","var(--teal)","rgba(84,214,180,.06)"];
  return["var(--line2)","var(--dim)","var(--bg)"];
}
function valStyle(vl){
  if(vl.startsWith("VERY"))return["var(--coral-dim)","var(--coral)"];
  if(vl==="EXPENSIVE")return["var(--amber)","var(--amber)"];
  if(vl==="ATTRACTIVE")return["var(--teal-dim)","var(--teal)"];
  return["var(--line2)","var(--dim)"];
}
function gauge(v){
  const s=Math.max(0,Math.min(100,v||0)),r=25,c=2*Math.PI*r,off=c*(1-s/100);
  const col=s>=85?"var(--brass)":s>=70?"var(--teal)":"var(--faint)";
  return `<div class="gauge"><svg width="62" height="62" viewBox="0 0 62 62">
    <circle cx="31" cy="31" r="${r}" fill="none" stroke="var(--line)" stroke-width="5"/>
    <circle cx="31" cy="31" r="${r}" fill="none" stroke="${col}" stroke-width="5" stroke-linecap="round"
      stroke-dasharray="${c.toFixed(1)}" stroke-dashoffset="${off.toFixed(1)}"/>
  </svg><div class="gt">${v==null?"—":v.toFixed(0)}</div></div>`;
}

function detail(r){
  const li=(a,c)=>a&&a.length?a.map(t=>`<li class="${c}">${t}</li>`).join(""):'<li>none</li>';
  const masLine=(MARKET&&r.mas!=null)
    ? `<div class="hl"><span>Market-adjusted score</span><span>${r.mas.toFixed(1)}</span></div>
       <div><span>Business quality (base)</span><span>${r.s==null?"—":r.s.toFixed(1)}</span></div>`
    : `<div class="hl"><span>Business quality</span><span>${r.s==null?"—":r.s.toFixed(1)}</span></div>`;
  return `<div class="detail">
    <div class="cols">
      <div class="blk kv"><h4>Ledger</h4>
        ${masLine}
        <div><span>Market cap</span><span>${bn(r.mc)}</span></div>
        <div><span>FCF yield</span><span>${pct(r.fcfy)}</span></div>
        <div><span>Owner-earnings yield</span><span>${pct(r.oey)}</span></div>
        <div><span>ROIC</span><span>${pct(r.roic)}</span></div>
        <div><span>Net debt / EBITDA</span><span>${x(r.nde)}</span></div>
        <div><span>Revenue CAGR</span><span>${pct(r.rcagr)}</span></div>
        <div><span>Price implies growth</span><span>${pct(r.ig)}/yr</span></div>
        <div><span>Data confidence</span><span>${r.cf}% · ${r.rg}</span></div>
        <div><span>History</span><span>${r.hy}yr · ${r.src}</span></div>
      </div>
      <div class="blk"><h4>Strengths</h4><ul>${li(r.strengths,"g")}</ul>
        <h4 style="margin-top:14px">Economic concerns</h4><ul>${li(r.concerns,"b")}</ul></div>
      <div class="blk"><h4>Why capped</h4><ul>${li(r.gates.map(g=>"Hard gate: "+g),"b")}${li(r.caps,"")}</ul></div>
    </div>
    ${r.manual&&r.manual!=="NO"?`<div class="manual"><b>Manual review needed</b>${r.manual.replace("YES — ","")}</div>`:""}
  </div>`;
}

function card(r,rank){
  const hs=headScore(r),[vb,vc,vbg]=verdictStyle(r.v),[vlb,vlc]=valStyle(r.vl);
  const vshort=r.v.replace(/ \(.*/,""),vlshort=r.vl.split(" (")[0];
  let deltaHtml="";
  if(!qualityOnly&&MARKET&&r.mas!=null&&r.s!=null){
    const d=r.mas-r.s,cls=d<-.05?"dn":d>.05?"up":"flat";
    const txt=d<-.05?`▼ ${Math.abs(d).toFixed(1)} market`:d>.05?`▲ ${d.toFixed(1)} market`:"market-neutral";
    deltaHtml=`<span class="qrow">quality ${r.s.toFixed(1)} <span class="delta ${cls}">${txt}</span></span>`;
  } else if(qualityOnly){
    deltaHtml=`<span class="qrow">business quality</span>`;
  }
  return `<div class="card${open===r.t?' opened':''}${qualityOnly?' qmode':''}" data-t="${r.t}">
    <div class="head" data-t="${r.t}">
      <div class="rank">${rank}</div>
      <div class="idy">
        <span class="tk">${r.t}</span><div class="co">${r.n}</div>
        <div class="meta">
          <span class="tag verdict" style="--v-b:${vb};--v-c:${vc};--v-bg:${vbg}">${vshort}</span>
          <span class="tag val" style="--vl-b:${vlb};--vl-c:${vlc}">${vlshort}</span>
          <span class="tag rel">${r.rg} · ${r.hy}yr</span>
        </div>
      </div>
      <div class="scores">
        <div class="scols">
          <div class="masrow"><span class="big ${sCls(hs)}">${hs==null?"—":hs.toFixed(1)}</span><span class="of">/100</span></div>
          ${deltaHtml}
        </div>
        ${gauge(hs)}
      </div>
    </div>
    ${detail(r)}
  </div>`;
}

function renderList(){
  renderTiers();
  const rs=rows();
  document.getElementById("nshow").textContent=rs.length;
  document.getElementById("tabcnt").textContent=DATA.length;
  const list=document.getElementById("list");
  if(!rs.length){list.innerHTML=`<div class="empty"><b>No matches</b>Clear the search or pick All tiers.</div>`;return;}
  list.innerHTML=rs.map((r,i)=>card(r,i+1)).join("");
  list.querySelectorAll(".head").forEach(h=>h.onclick=()=>{const t=h.dataset.t;open=open===t?null:t;renderList();});
}

document.getElementById("q").addEventListener("input",e=>{query=e.target.value;renderList();});
document.querySelectorAll("#sortseg button").forEach(b=>b.onclick=()=>{
  document.querySelectorAll("#sortseg button").forEach(x=>x.classList.remove("on"));
  b.classList.add("on");sortK=b.dataset.k;renderList();});
document.getElementById("qtoggle").onclick=function(){
  qualityOnly=!qualityOnly;this.classList.toggle("on",qualityOnly);
  // in quality-only mode, the Score sort means pure quality
  renderList();};

/* ============ MARKET TAB RENDER ============ */
function bandMeter(pos,zones){
  // pos: 0..1 needle position; zones: array of labels for scale ends
  const p=Math.max(0,Math.min(1,pos))*100;
  const z=zones.map(()=>`<div class="zone"></div>`).join("");
  return `<div class="band"><div class="zones">${z}</div><div class="needle" style="left:${p}%"></div></div>`;
}
function renderMarket(){
  const el=document.getElementById("mkt");
  if(!MARKET){el.innerHTML=`<div class="mkt-empty"><b>No market data for this run</b>Pass market inputs (forward P/E, Buffett Indicator, Treasury) to populate the climate view.</div>`;return;}
  const M=MARKET,col=REGCOL[M.regime]||"var(--brass)";
  const regName=M.regime.replace(/_/g," ");
  // dial ring
  const s=M.score!=null?M.score:50,r=112,c=2*Math.PI*r,off=c*(1-s/100);
  const dial=`<div class="dial"><svg width="250" height="250" viewBox="0 0 250 250" style="transform:rotate(-90deg)">
    <circle cx="125" cy="125" r="${r}" fill="none" stroke="var(--line)" stroke-width="10"/>
    <circle cx="125" cy="125" r="${r}" fill="none" stroke="${col}" stroke-width="10" stroke-linecap="round"
      stroke-dasharray="${c.toFixed(1)}" stroke-dashoffset="${off.toFixed(1)}"/></svg>
    <div class="lbl"><div class="rname" style="color:${col}">${regName}</div>
      <div class="rscore">${M.score!=null?M.score:"—"}</div>
      <div class="rcap">buyer's odds / 100</div></div></div>`;

  // rule cards
  const rules=[];
  // 1. Buffett Indicator
  const bi=M.bi_gnp!=null?M.bi_gnp:M.bi_gdp, biSrc=M.bi_gnp!=null?"GNP":"GDP";
  if(bi!=null){
    const pos=(bi-60)/(220-60); // 60%..220% scale
    const bc=bi<=110?"var(--teal)":bi<=170?"var(--amber)":"var(--coral)";
    rules.push(`<div class="rule">
      <div class="rh"><div><div class="rt">Buffett Indicator</div><div class="rsub">total US market value / ${biSrc}</div></div>
        <div class="rval"><div class="v" style="color:${bc}">${bi.toFixed(0)}%</div><div class="b" style="color:${bc}">${(M.bib||"").replace(/_/g," ")}</div></div></div>
      ${bandMeter(pos,[1,2,3,4])}
      <div class="bandscale"><span>60% cheap</span><span>110% fair</span><span>170% rich</span><span>220%+</span></div>
      <details class="learn"><summary>What Buffett means by this</summary><div class="body">
        Buffett called the ratio of total US stock-market value to the nation's output <b>"probably the best single measure of where valuations stand at any given moment."</b> Near or below 100% has historically meant stocks were reasonably priced; well above it means buyers are paying a lot for each dollar of national output. He also stressed it's a rough guide, not a precise timer.
      </div></details></div>`);
  }
  // 2. Forward P/E
  if(M.fpe!=null){
    const pos=(M.fpe-10)/(26-10);
    const fc=M.fpe<18?"var(--teal)":M.fpe<22?"var(--amber)":"var(--coral)";
    rules.push(`<div class="rule">
      <div class="rh"><div><div class="rt">S&amp;P 500 Forward P/E</div><div class="rsub">price paid per dollar of expected earnings</div></div>
        <div class="rval"><div class="v" style="color:${fc}">${M.fpe.toFixed(1)}x</div><div class="b" style="color:${fc}">${(M.fpeb||"").replace(/-/g," ")}</div></div></div>
      ${bandMeter(pos,[1,2,3,4])}
      <div class="bandscale"><span>10x cheap</span><span>18x fair</span><span>22x rich</span><span>26x+</span></div>
      <details class="learn"><summary>Why the price you pay matters</summary><div class="body">
        Buffett's core rule is that <b>the price you pay determines your return.</b> A high forward P/E means the market is pricing in years of strong growth already — leaving little margin for error. History suggests that buying broadly at 22–24x earnings has tended to produce roughly flat-to-low returns over the following decade. This is a tendency, not a prediction.
      </div></details></div>`);
  }
  // 3. Interest-rate gravity
  if(M.t10!=null){
    const pos=Math.max(0,Math.min(1,(M.t10-1)/(7-1)));
    const spread=M.sp10!=null?(M.sp10*100):null;
    const gc=spread!=null?(spread<=0?"var(--coral)":spread<1?"var(--amber)":"var(--teal)"):"var(--dim)";
    rules.push(`<div class="rule">
      <div class="rh"><div><div class="rt">Interest-Rate Gravity</div><div class="rsub">10-year Treasury vs. stock earnings yield</div></div>
        <div class="rval"><div class="v" style="color:${gc}">${M.t10.toFixed(2)}%</div><div class="b" style="color:${gc}">${spread!=null?(spread>=0?"+":"")+spread.toFixed(1)+"% premium":"10-yr yield"}</div></div></div>
      ${bandMeter(pos,[1,2,3,4])}
      <div class="bandscale"><span>1%</span><span>3%</span><span>5%</span><span>7%</span></div>
      <details class="learn"><summary>Buffett on interest rates</summary><div class="body">
        Buffett described interest rates as <b>"gravity" for asset prices</b> — when rates are high, every dollar of future company earnings is worth less today, and safe bonds compete with stocks. A thin or negative gap between the market's earnings yield and the 10-year Treasury means stocks offer little extra reward for their extra risk, so a patient buyer should demand a larger margin of safety.
      </div></details></div>`);
  }
  // 4. CAPE (if present)
  if(M.cape!=null){
    const pos=(M.cape-10)/(40-10);
    const cc=M.cape<25?"var(--teal)":M.cape<35?"var(--amber)":"var(--coral)";
    rules.push(`<div class="rule">
      <div class="rh"><div><div class="rt">Shiller CAPE</div><div class="rsub">price vs. 10-year average earnings</div></div>
        <div class="rval"><div class="v" style="color:${cc}">${M.cape.toFixed(0)}</div><div class="b" style="color:${cc}">${(M.capeb||"").replace(/-/g," ")}</div></div></div>
      ${bandMeter(pos,[1,2,3])}
      <div class="bandscale"><span>10 cheap</span><span>25 elevated</span><span>40 stretched</span></div>
      <details class="learn"><summary>Secondary confirmation</summary><div class="body">
        CAPE smooths earnings over ten years to strip out the business cycle. It's a <b>secondary check</b> here, not Buffett's own indicator — but a very high CAPE alongside a high Buffett Indicator reinforces the read that broad returns from here are likely muted.
      </div></details></div>`);
  }

  el.innerHTML=`
    <div class="mkt-hero" style="--regcol:${col}">
      ${dial}
      <div class="say">
        <h2>The market is offering</h2>
        <div class="pos">${M.pos||""}</div>
        ${M.mos!=null?`<div class="mos">Demand ${M.mos>=0?"an extra ":""}${M.mos>=0?"+":""}${M.mos}% margin of safety in this climate</div>`:""}
      </div>
    </div>
    <div class="mkt-grid">${rules.join("")}</div>
    <div class="mkt-note">These thresholds are heuristics, in Buffett's own spirit — guides to whether the odds are good, fair, or poor, never a signal to buy or sell everything. The company quality scores on the Stocks tab are never altered by this climate read; it only shifts how much margin of safety to demand.</div>`;
}

renderList();
</script></body></html>"""


def export_dashboard(results, filename, stamp):
    rows_json, market_json = _dash_payload(results)
    html = (DASHBOARD_TEMPLATE
            .replace("__DATA__", rows_json)
            .replace("__MARKET__", market_json)
            .replace("__STAMP__", stamp)
            .replace("__COUNT__", str(len(results))))
    with open(filename, "w", encoding="utf-8") as f:
        f.write(html)
    return filename


def main():
    global USE_CACHE, USE_EDGAR
    ap = argparse.ArgumentParser()
    ap.add_argument("--tickers", nargs="*")
    ap.add_argument("--no-edgar", action="store_true",
                    help="Skip SEC EDGAR history (Yahoo ~4yrs only)")
    ap.add_argument("--edgar-contact", type=str, default=None,
                    help='SEC requires identification, e.g. "Jane Doe jane@x.com"')
    ap.add_argument("--calibration-demo", action="store_true",
                    help="Run the 36-ticker calibration set with notes")
    ap.add_argument("--export-audit", action="store_true", default=None,
                    help="Force per-rule audit CSV (default: on for <=40 tickers)")
    ap.add_argument("--allow-special-compounders", action="store_true",
                    help="Let banks/insurers with strong blended scores be "
                         "labeled COMPOUNDER (SPECIAL). Default off.")
    ap.add_argument("--min-confidence", type=float, default=None,
                    help="Drop results below this overall confidence")
    ap.add_argument("--min-history-years", type=int, default=None,
                    help="Drop results with fewer statement years than this")
    ap.add_argument("--max-workers", type=int, default=1,
                    help="Reserved; kept at 1 to respect rate limits")
    ap.add_argument("--suppress-special-generic", action="store_true", default=True,
                    help="(default on) exclude economically-invalid generic rules "
                         "for banks/insurers instead of failing them")
    ap.add_argument("--no-dashboard", action="store_true",
                    help="Skip the self-contained HTML dashboard export")
    ap.add_argument("--publish", action="store_true",
                    help="Also write the dashboard as index.html in the current "
                         "folder, so a GitHub repo can be published with just "
                         "'git add -A && git commit && git push' — no renaming.")
    ap.add_argument("--scan-10k", action="store_true",
                    help="Scan latest 10-K text for customer/product concentration "
                         "(1-3MB fetch per ticker; best for shortlists, not full universe)")
    ap.add_argument("--universe", choices=["sp500", "sp400", "both", "full"],
                    default="both",
                    help="Ticker set. 'full' = every US-listed common stock on "
                         "a major exchange via SEC (~6,000). Pair with "
                         "--too-small-for-buffett or --cap-min/--cap-max to keep "
                         "it feasible.")
    ap.add_argument("--too-small-for-buffett", action="store_true",
                    help="Only $300M-$20B market caps")
    ap.add_argument("--cap-min", type=float, default=None,
                    help="Minimum market cap in $ (e.g. 3e8). Cheap pre-filter "
                         "applied BEFORE the expensive score.")
    ap.add_argument("--cap-max", type=float, default=None,
                    help="Maximum market cap in $ (e.g. 2e10).")
    ap.add_argument("--resume", action="store_true",
                    help="Resume a large run: reuse already-scored results from "
                         "the run manifest and skip finished tickers. Lets a "
                         "multi-hour full-universe scan survive interruption.")
    ap.add_argument("--sector", type=str, default=None,
                    help="e.g. Energy, Technology, Healthcare, Industrials")
    ap.add_argument("--limit", type=int, default=None)
    ap.add_argument("--top", type=int, default=20)
    ap.add_argument("--debug", action="store_true",
                    help="Print full breakdown (gates, caps, categories, missing data) per ticker")
    ap.add_argument("--sleep", type=float, default=1.0,
                    help="Seconds to wait between tickers (default 1.0; raise if rate limited)")
    ap.add_argument("--no-cache", action="store_true",
                    help="Bypass the 24h local data cache and force fresh fetches")
    # --- v15 market valuation overlay (all optional; manual inputs) ---
    mkt = ap.add_argument_group("market overlay (v15)")
    mkt.add_argument("--market-forward-pe", type=float, default=None,
                     help="S&P 500 forward P/E (primary market-valuation input)")
    mkt.add_argument("--market-cape", type=float, default=None,
                     help="Shiller CAPE (secondary confirmation only)")
    mkt.add_argument("--buffett-indicator-gnp", type=float, default=None,
                     help="Total US equity market value / GNP, in %% (preferred)")
    mkt.add_argument("--buffett-indicator-gdp", type=float, default=None,
                     help="Fallback: total US equity market value / GDP, in %%")
    mkt.add_argument("--treasury-10y", type=float, default=None,
                     help="10-year Treasury yield, in %% (e.g. 4.3)")
    mkt.add_argument("--tbill-3m", type=float, default=None,
                     help="3-month T-bill yield, in %% (e.g. 5.2)")
    mkt.add_argument("--corporate-profit-share", type=float, default=None,
                     help="Corporate profits / GDP (or GDI), in %% (e.g. 11.5)")
    mkt.add_argument("--sp500-drawdown", type=float, default=None,
                     help="S&P 500 drawdown from high, positive %% (e.g. 22)")
    mkt.add_argument("--market-adjust-scores", action="store_true",
                     help="Also compute market_adjusted_score (final_score is "
                          "always left unchanged)")
    mkt.add_argument("--no-market-overlay", action="store_true",
                     help="Disable the v15 market overlay entirely (exact v14 "
                          "behaviour)")
    args = ap.parse_args()
    USE_CACHE = not args.no_cache
    USE_EDGAR = not args.no_edgar
    if args.edgar_contact:
        globals()["EDGAR_UA"] = f"BuffettScreener/15.0 {args.edgar_contact}"
    globals()["SCAN_10K"] = args.scan_10k
    globals()["ALLOW_SPECIAL_COMPOUNDERS"] = args.allow_special_compounders
    if args.calibration_demo:
        args.tickers = CALIBRATION_TICKERS
        print(f"CALIBRATION DEMO: {len(CALIBRATION_TICKERS)} tickers with expectations")

    if args.tickers:
        tickers = args.tickers
    else:
        if args.universe == "full":
            print("Fetching full US universe from SEC...")
            tickers = get_full_us_universe()
        else:
            print("Scraping universe...")
            tickers = get_universe(args.universe)
        print(f"Universe: {len(tickers)} tickers")
    if args.limit:
        tickers = tickers[:args.limit]

    # Resolve the cap band once. --too-small-for-buffett is shorthand for the
    # Buffett $300M-$20B thesis; explicit --cap-min/--cap-max override it.
    cap_min = args.cap_min
    cap_max = args.cap_max
    if args.too_small_for_buffett:
        if cap_min is None:
            cap_min = 3e8
        if cap_max is None:
            cap_max = 2e10
    cap_band_on = cap_min is not None or cap_max is not None

    # Cheap market-cap PRE-FILTER: for large runs, probe cap with a light quote
    # call and drop out-of-band names BEFORE paying for the full EDGAR history.
    # Only worth it when the list is big; for short lists it just adds calls.
    if cap_band_on and len(tickers) > 120:
        lo = cap_min if cap_min is not None else 0
        hi = cap_max if cap_max is not None else float("inf")
        print(f"Pre-filtering {len(tickers)} tickers to cap band "
              f"[{lo:,.0f} - {hi:,.0f}] (cheap probe)...")
        kept, dropped, unknown = [], 0, 0
        for j, tk in enumerate(tickers, 1):
            cap = quick_market_cap(tk)
            if cap is None:
                unknown += 1
                kept.append(tk)  # keep unknowns; the full score decides
            elif lo <= cap <= hi:
                kept.append(tk)
            else:
                dropped += 1
            if j % 250 == 0:
                print(f"  probed {j}/{len(tickers)} — kept {len(kept)}, "
                      f"dropped {dropped}")
        print(f"Pre-filter kept {len(kept)} "
              f"(dropped {dropped} out-of-band, {unknown} unknown kept).")
        tickers = kept

    globals()["EXPORT_AUDIT"] = (args.export_audit if args.export_audit is not None
                                 else len(tickers) <= 40)

    # ---- checkpoint / resume manifest ----
    # Each scored result is written to a manifest immediately, so a crash or
    # Ctrl-C during a multi-hour run costs nothing: --resume reloads finished
    # work and skips those tickers.
    manifest_path = CACHE_DIR / "run_manifest.pkl"
    results = []
    done = set()
    if args.resume and manifest_path.exists():
        try:
            saved = pickle.loads(manifest_path.read_bytes())
            results = saved.get("results", [])
            done = {r["ticker"] for r in results}
            print(f"Resuming: {len(done)} tickers already scored, skipping them.")
        except Exception as e:
            print(f"  Could not read manifest ({e}); starting fresh.")

    def _persist():
        try:
            CACHE_DIR.mkdir(exist_ok=True)
            manifest_path.write_bytes(pickle.dumps({"results": results}))
        except Exception:
            pass

    for i, tk in enumerate(tickers, 1):
        if tk in done:
            continue
        try:
            r = score_stock(tk, sector=args.sector)
        except Exception as e:
            print(f"[{i}/{len(tickers)}] {tk}: error ({e})")
            continue
        if r is None:
            print(f"[{i}/{len(tickers)}] {tk}: no data")
            continue
        if r == "SECTOR_SKIP":
            print(f"[{i}/{len(tickers)}] {tk}: skipped (not {args.sector})")
            continue
        if cap_band_on and r["mcap"] and not (
                (cap_min is None or r["mcap"] >= cap_min) and
                (cap_max is None or r["mcap"] <= cap_max)):
            print(f"[{i}/{len(tickers)}] {tk}: skipped (outside cap band)")
            continue
        if args.min_confidence is not None and r["confidence"] < args.min_confidence:
            print(f"[{i}/{len(tickers)}] {tk}: dropped (confidence "
                  f"{r['confidence']:.0f}% < {args.min_confidence})")
            continue
        if args.min_history_years is not None and r["history_years"] < args.min_history_years:
            print(f"[{i}/{len(tickers)}] {tk}: dropped ({r['history_years']}yr history)")
            continue
        results.append(r)
        cache_note = " [cache]" if r.get("from_cache") else ""
        print(f"[{i}/{len(tickers)}] {tk}: {r['score']}/100  {r['verdict']}{cache_note}")
        if args.debug:
            print_report(r)
        if i % 25 == 0:
            _persist()  # checkpoint periodically
        if not r.get("from_cache"):
            time.sleep(args.sleep)
    _persist()  # final checkpoint

    results.sort(key=lambda x: -x["score"])

    # ------------------------------------------------------------------
    # v15 MARKET OVERLAY: computed once from CLI inputs, attached to every
    # result. It NEVER changes final_score. market_adjusted_score is only
    # computed when --market-adjust-scores is passed.
    # ------------------------------------------------------------------
    market = None
    market_overlay_on = not args.no_market_overlay
    any_market_input = any(v is not None for v in (
        args.market_forward_pe, args.market_cape, args.buffett_indicator_gnp,
        args.buffett_indicator_gdp, args.treasury_10y, args.tbill_3m,
        args.corporate_profit_share, args.sp500_drawdown))

    if market_overlay_on and any_market_input:
        ctx = MarketContext(
            sp500_forward_pe=args.market_forward_pe,
            market_cape=args.market_cape,
            buffett_indicator_gnp=args.buffett_indicator_gnp,
            buffett_indicator_gdp=args.buffett_indicator_gdp,
            treasury_10y=args.treasury_10y,
            tbill_3m=args.tbill_3m,
            corporate_profit_share_pct=args.corporate_profit_share,
            sp500_drawdown_from_high_pct=args.sp500_drawdown,
            data_source_notes="manual CLI inputs",
            market_data_reliability="manual-input",
        )
        market = analyze_market_context(ctx)

        # Attach to every result (final_score untouched throughout).
        # v15.1: the market-adjusted score is now computed BY DEFAULT whenever
        # the overlay has data, because a real investment decision must weigh
        # market climate. --market-adjust-scores is kept for back-compat but is
        # no longer required. final_score remains sacrosanct and separate.
        for r in results:
            r["market"] = market
            r["market_adjusted_score"] = market_adjusted_score(
                r["score"], r, market)

        # Re-rank by the market-adjusted (blended) score so the headline order
        # reflects both business quality AND market odds. Ties fall back to the
        # pure quality score.
        results.sort(key=lambda r: (
            -(r.get("market_adjusted_score")
              if r.get("market_adjusted_score") is not None else r["score"]),
            -r["score"]))

        # Console climate banner, printed once at the top.
        print(f"\n{'='*72}")
        print(f"MARKET CLIMATE: {market['market_regime']}")
        if market["market_forward_pe"] is not None:
            print(f"  Forward P/E:        {market['market_forward_pe']:.1f}x "
                  f"({market['market_forward_pe_bucket']})")
        bi = market["buffett_indicator_gnp"]
        bi_src = "GNP"
        if bi is None:
            bi = market["buffett_indicator_gdp"]; bi_src = "GDP"
        if bi is not None:
            print(f"  Buffett Indicator:  {bi:.0f}% ({bi_src}) "
                  f"[{market['buffett_indicator_bucket']}]")
        if market["treasury_10y"] is not None:
            print(f"  10-year Treasury:   {market['treasury_10y']:.2f}%")
        if market["market_score_0_100"] is not None:
            print(f"  Market score:       {market['market_score_0_100']}/100 "
                  f"(buyer's odds)")
        print(f"  Profit-share warn:  "
              f"{'yes' if market['profit_share_warning'] else 'no'}")
        print(f"  Required MOS add-on: "
              f"{market['suggested_margin_of_safety_addon_pct']:+d}%")
        print(f"  {market['market_positioning']}")
        print("  (market-adjusted score is the headline rank; "
              "final_score preserved separately)")
        print(f"{'='*72}")
    else:
        for r in results:
            r["market"] = None
            r["market_adjusted_score"] = None

    if not args.debug:
        for r in results[:args.top]:
            print_report(r)

    # ------------------------------------------------------------------
    # v14 readable summary: only names within reach of investable are
    # printed. Everything else lives in the CSVs and the dashboard.
    # ------------------------------------------------------------------
    def q(r):
        return r["research_queue"]

    investable = [r for r in results
                  if r["score"] is not None and r["score"] >= 80
                  and not r["gates"]
                  or q(r).startswith(("Tier 1", "Tier 2"))]
    omitted = len(results) - len(investable)

    print(f"\n{'='*72}\n--- RANKING (investable candidates only; "
          f"{omitted} weaker names in CSV/dashboard) ---")
    print(f"  {'SCORE':>6}  {'TICKER':<6} {'REL':<3} {'VERDICT':<38} VALUATION")
    for r in investable:
        print(f"  {r['score']:>6}  {r['ticker']:<6} {r['model_reliability_grade']:<3} "
              f"{r['verdict'][:38]:<38} {r['valuation_label']}")

    print(f"\n{'='*72}\n--- RESEARCH SUMMARY ---")
    t1a = [r for r in results if q(r).startswith("Tier 1A")]
    t1b = [r for r in results if q(r).startswith("Tier 1B")]
    t1c = [r for r in results if q(r).startswith("Tier 1C")]
    t2 = [r for r in results if q(r).startswith("Tier 2")]

    print(f"\nBEST NORMAL-COMPANY RESEARCH CANDIDATES ({len(t1a)}):")
    if t1a:
        for r in t1a[:12]:
            conc = "  [check concentration]" if r.get("concentration_review_needed") else ""
            print(f"   {r['ticker']:<6} {r['score']:>5}  {r['valuation_label']:<10} "
                  f"OEyld {_fmt_pct(r['key']['oe_yield'])}  ROIC {_fmt_pct(r['key']['roic'])}{conc}")
    else:
        print("   none this run — see Tier 1B/2 or wait for better prices")
    if t1b:
        print(f"\nCAPPED / CYCLICAL BUT HIGH-QUALITY ({len(t1b)}): " + ", ".join(
            f"{r['ticker']} {r['score']}" for r in t1b[:12]))
    if t1c:
        print(f"\nSTRONG SPECIAL MODELS ({len(t1c)}): " + ", ".join(
            f"{r['ticker']} {r['score']} ({r['module_name']} {r['module_score']:.0f})"
            for r in t1c[:10]))
    if t2:
        print(f"\nQUALITY, WAIT FOR PRICE ({len(t2)}): " + ", ".join(
            f"{r['ticker']} {r['score']}" for r in t2[:12]))
    exp = [r for r in results if "EXPENSIVE" in r["valuation_label"]
           and (r["graded_score"] or 0) >= 70 and not r["gates"]]
    if exp:
        print(f"\nGREAT BUSINESS, BAD PRICE ({len(exp)}): " + ", ".join(
            f"{r['ticker']} (implies {_fmt_pct(r['key']['implied_growth'])}/yr)"
            for r in exp[:10]))
    conc_names = [r for r in investable if r.get("concentration_review_needed")]
    if conc_names:
        print(f"\nCONCENTRATION REVIEW NEEDED ({len(conc_names)}): " + ", ".join(
            r["ticker"] for r in conc_names))
    share_art = [r for r in results
                 if any("Dilution gate suppressed" in s for s in r["suppressed_gates"])
                 or "ARTIFACT" in (r["split_analysis"]["warning"] or "").upper()]
    if share_art:
        print(f"\nSHARE-COUNT ARTIFACTS TO VERIFY ({len(share_art)}): " + ", ".join(
            f"{r['ticker']} (raw {_fmt_pct(r['split_analysis']['raw_cagr'])})"
            for r in share_art))
    n_reject = sum(1 for r in results if q(r).startswith("Tier 5"))
    n_watch = sum(1 for r in results if q(r).startswith(("Tier 3", "Tier 4")))
    print(f"\nNot shown: {n_watch} watchlist/special names, {n_reject} avoid/reject "
          f"— full detail in the CSVs and dashboard.")

    stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    summary_file = f"buffett_summary_v15_{stamp}.csv"
    detailed_file = f"buffett_detailed_v15_{stamp}.csv"
    audit_file = f"buffett_audit_v15_{stamp}.csv"

    pd.DataFrame([{
        "ticker": r["ticker"], "name": r["name"], "sector": r["sector"],
        "industry": r["industry"], "market_cap": r["mcap"],
        "enterprise_value": r["key"]["ev"],
        "raw_score": r["raw"], "final_score": r["score"],
        "market_regime": (r.get("market") or {}).get("market_regime"),
        "market_score_0_100": (r.get("market") or {}).get("market_score_0_100"),
        "market_adjusted_score": r.get("market_adjusted_score"),
        "market_forward_pe": (r.get("market") or {}).get("market_forward_pe"),
        "market_forward_pe_bucket": (r.get("market") or {}).get("market_forward_pe_bucket"),
        "buffett_indicator_gnp": (r.get("market") or {}).get("buffett_indicator_gnp"),
        "buffett_indicator_gdp": (r.get("market") or {}).get("buffett_indicator_gdp"),
        "buffett_indicator_bucket": (r.get("market") or {}).get("buffett_indicator_bucket"),
        "market_cape": (r.get("market") or {}).get("market_cape"),
        "cape_bucket": (r.get("market") or {}).get("cape_bucket"),
        "treasury_10y": (r.get("market") or {}).get("treasury_10y"),
        "tbill_3m": (r.get("market") or {}).get("tbill_3m"),
        "equity_yield_spread_vs_10y": (r.get("market") or {}).get("equity_yield_spread_vs_10y"),
        "corporate_profit_share_pct": (r.get("market") or {}).get("corporate_profit_share_pct"),
        "profit_share_warning": (r.get("market") or {}).get("profit_share_warning"),
        "suggested_margin_of_safety_addon_pct": (r.get("market") or {}).get("suggested_margin_of_safety_addon_pct"),
        "market_positioning": (r.get("market") or {}).get("market_positioning"),
        "market_data_reliability": (r.get("market") or {}).get("market_data_reliability"),
        "rules_passed": r["passed"], "rules_scored": r["scored"],
        "data_confidence_pct": r["confidence"],
        "history_years": r["history_years"],
        "industry_module": r["module_name"] or "",
        "module_score": r["module_score"],
        "verdict": r["verdict"],
        "fcf_yield": r["key"]["fcf_yield"],
        "owner_earnings_yield": r["key"]["oe_yield"],
        "roic": r["key"]["roic"],
        "net_debt_ebitda": r["key"]["nd_ebitda"],
        "interest_coverage": (None if r["key"]["interest_cov"] == float("inf")
                              else r["key"]["interest_cov"]),
        "fcf_conversion": r["key"]["fcf_conv"],
        "revenue_cagr": r["key"]["rev_cagr"],
        "fcf_cagr": r["key"]["fcf_cagr"],
        "share_count_cagr": r["key"]["share_cagr"],
        "reverse_dcf_implied_growth": r["key"]["implied_growth"],
        "positive_fcf_years": r["key"]["pos_fcf_years"],
        "positive_ebit_years": r["key"]["pos_ebit_years"],
        "oe_conservative": r["key"]["oe_conservative"],
        "oe_per_share": r["key"]["oe_per_share"],
        "pe_vs_own_history": (r["key"]["pe_vs_hist"][0]
                              if r["key"]["pe_vs_hist"] else None),
        "largest_customer_pct": r["tenk"].get("largest_customer_pct"),
        "tenk_scanned": r["tenk"].get("scanned", False),
        "manual_review_required": r["manual_review_required"],
        "generic_score": r["generic_score"],
        "graded_score": r["graded_score"],
        "blended_special_score": r["blended_score"],
        "module_confidence": r["module_confidence"],
        "raw_share_cagr": r["key"]["raw_share_cagr"],
        "split_adjusted_share_cagr": r["key"]["adj_share_cagr"],
        "split_events": str(r["split_analysis"]["split_events"] or ""),
        "split_adjustment_applied": r["split_analysis"]["adjustment_applied"],
        "share_count_warning": r["split_analysis"]["warning"] or "",
        "begin_shares_raw": r["split_analysis"]["begin_raw"],
        "end_shares_raw": r["split_analysis"]["end_raw"],
        "begin_shares_adjusted": r["split_analysis"]["begin_adjusted"],
        "end_shares_adjusted": r["split_analysis"]["end_adjusted"],
        "window_gross_buybacks": (r["split_analysis"].get("evidence") or {}).get("buy_total"),
        "window_issuance_proceeds": (r["split_analysis"].get("evidence") or {}).get("iss_total"),
        "window_sbc_total": (r["split_analysis"].get("evidence") or {}).get("sbc_total"),
        "dilution_evidence_level": r["split_analysis"]["dilution_evidence_level"],
        "dilution_hard_gate_allowed": r["split_analysis"]["dilution_hard_gate_allowed"],
        "valuation_percentile": r["key"]["valuation_percentile"],
        "mos_base": r["key"]["mos_base"],
        "mos_bear": r["key"]["mos_bear"],
        "normalized_fcf_yield": r["key"]["normalized_fcf_yield"],
        "gross_buyback_yield": r["buybacks"]["gross_buyback_yield"],
        "net_buyback_yield": r["buybacks"]["net_buyback_yield"],
        "buyback_effectiveness": r["buybacks"]["buyback_effectiveness"],
        "capital_allocation_grade": r["buybacks"]["capital_allocation_grade"],
        "moat_proxy_score": r["moat_score"],
        "suppressed_hard_gates": " | ".join(r["suppressed_gates"]),
        "recon_warnings": " | ".join(r["recon_warnings"]),
        "unreliable_rows": "; ".join(r["unreliable_rows"]),
        "model_reliability_grade": r["model_reliability_grade"],
        "valuation_label": r["valuation_label"],
        "research_queue": r["research_queue"],
        "negative_equity_cause": r.get("negative_equity_cause") or "",
        "concentration_review_needed": r.get("concentration_review_needed", False),
        "bank_p_tbv": (r["bank_valuation"] or {}).get("p_tbv"),
        "bank_normalized_earnings_yield": (r["bank_valuation"] or {}).get("normalized_earnings_yield"),
        "data_warnings": " | ".join(r.get("data_warnings", [])[:6]),
        "calibration_notes": CALIBRATION_NOTES.get(r["ticker"], ""),
        "key_strengths": "; ".join(r["strengths"]),
        "key_concerns": "; ".join(r["concerns"]),
        "caps": " | ".join(r["caps"]),
        "gates_failed": "; ".join(r["gates"]),
        "missing_data": "; ".join(r["missing"]),
    } for r in results]).to_csv(summary_file, index=False)

    detailed_rows = []
    for r in results:
        row = {
            "ticker": r["ticker"], "name": r["name"], "sector": r["sector"],
            "industry": r["industry"], "market_cap": r["mcap"],
            "raw_score": r["raw"], "final_score": r["score"],
            "market_regime": (r.get("market") or {}).get("market_regime"),
            "market_adjusted_score": r.get("market_adjusted_score"),
            "suggested_margin_of_safety_addon_pct": (r.get("market") or {}).get("suggested_margin_of_safety_addon_pct"),
            "verdict": r["verdict"],
            "gates_failed": "; ".join(r["gates"]),
            "caps": " | ".join(r["caps"]),
            "missing_data": "; ".join(r["missing"]),
            "n_missing": len(r["missing"]),
        }
        for cat_name, pts, weight, _detail in r["cats"]:
            row[f"cat_{cat_name.split('.')[0]}_{cat_name.split(' ', 1)[-1][:20]}"] = round(pts, 2)
        for rule_name, ok in r["checks"].items():
            row[f"rule_{rule_name[:40]}"] = "" if ok is None else ("PASS" if ok else "FAIL")
        detailed_rows.append(row)
    pd.DataFrame(detailed_rows).to_csv(detailed_file, index=False)

    if EXPORT_AUDIT:
        audit_rows = []
        for r in results:
            for cat_name, _pts, _w, detail in r["cats"]:
                for rule_name, ok in detail:
                    audit_rows.append({
                        "ticker": r["ticker"], "kind": "rule",
                        "category": cat_name, "name": rule_name,
                        "value": "", "threshold": "(in rule name)",
                        "pass_fail": ("N/A" if ok == "N/A" else
                                      "" if ok is None else
                                      "PASS" if ok else "FAIL"),
                        "score": "", "data_source": r["source"],
                        "reliability": r["confidence"],
                        "warning": ("suppressed for financials" if ok == "N/A"
                                    else "no data" if ok is None else ""),
                    })
            for mname, (val, sc) in (r.get("graded_table") or {}).items():
                audit_rows.append({
                    "ticker": r["ticker"], "kind": "graded_metric",
                    "category": "graded", "name": mname,
                    "value": val, "threshold": "(graded curve)",
                    "pass_fail": "", "score": sc,
                    "data_source": r["source"], "reliability": r["confidence"],
                    "warning": "" if val is not None else "no data",
                })
        pd.DataFrame(audit_rows).to_csv(audit_file, index=False)

    dash_note = ""
    export_screener_json(results, "screener_data.json")
    if not args.no_dashboard and results:
        dash_file = f"buffett_dashboard_{stamp}.html"
        export_dashboard(results, dash_file, stamp)
        dash_note = f", {dash_file}"
        if args.publish:
            export_dashboard(results, "index.html", stamp)
            dash_note += ", index.html"
    files = (f"{summary_file}, {detailed_file}"
             + (f", {audit_file}" if EXPORT_AUDIT else "") + dash_note)
    print(f"\nSaved {files} ({len(results)} stocks).")
    if dash_note:
        print(f"Open the dashboard: double-click {dash_file} (works offline; "
              f"upload the same file to GitHub Pages to make it a website).")
        if args.publish:
            print("Published index.html — now run:  git add -A && "
                  "git commit -m \"update dashboard\" && git push")
    print("Educational tool only — not financial advice.")


if __name__ == "__main__":
    main()

