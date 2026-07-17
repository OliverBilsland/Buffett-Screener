"""
Offline tests for the v15 Buffett-style market valuation overlay.

These tests use hard-coded MarketContext values ONLY. They never touch the
network, never fetch data, and never run the full screener. Run with:

    pytest tests_buffett_market_overlay.py -q

or standalone:

    python tests_buffett_market_overlay.py
"""

import importlib.util
import os

import pytest

# ---------------------------------------------------------------------------
# Import the screener module by file path so the tests work regardless of the
# working directory / file name quirks on Windows (buffett_screener_v15.py,
# "buffett_screener_v15 (1).py", etc.).
# ---------------------------------------------------------------------------
_HERE = os.path.dirname(os.path.abspath(__file__))
_CANDIDATES = [
    os.path.join(_HERE, "buffett_screener_v15.py"),
    "buffett_screener_v15.py",
]
_PATH = next((p for p in _CANDIDATES if os.path.exists(p)), _CANDIDATES[0])
_spec = importlib.util.spec_from_file_location("buffett_screener_v15", _PATH)
bs = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(bs)

MarketContext = bs.MarketContext
analyze_market_context = bs.analyze_market_context
market_adjusted_score = bs.market_adjusted_score


# ---------------------------------------------------------------------------
# A. Forward P/E buckets
# ---------------------------------------------------------------------------
def test_forward_pe_23_is_flat_return_very_expensive():
    m = analyze_market_context(MarketContext(sp500_forward_pe=23))
    assert m["market_forward_pe_bucket"] == "flat-return-zone"
    assert m["market_regime"] == "VERY_EXPENSIVE"


def test_forward_pe_low_is_attractive_fat_pitch():
    m = analyze_market_context(MarketContext(sp500_forward_pe=12))
    assert m["market_forward_pe_bucket"] == "attractive"
    assert m["market_regime"] == "FAT_PITCH"


# ---------------------------------------------------------------------------
# B. Buffett Indicator regimes
# ---------------------------------------------------------------------------
def test_buffett_indicator_75_is_fat_pitch():
    m = analyze_market_context(MarketContext(buffett_indicator_gnp=75))
    assert m["buffett_indicator_bucket"] == "FAT_PITCH"
    assert m["market_regime"] == "FAT_PITCH"


def test_buffett_indicator_205_is_playing_with_fire():
    m = analyze_market_context(MarketContext(buffett_indicator_gnp=205))
    assert m["buffett_indicator_bucket"] == "PLAYING_WITH_FIRE"
    assert m["market_regime"] == "PLAYING_WITH_FIRE"


def test_buffett_indicator_gdp_fallback_used_when_gnp_missing():
    m = analyze_market_context(MarketContext(buffett_indicator_gdp=75))
    assert m["buffett_indicator_bucket"] == "FAT_PITCH"


# ---------------------------------------------------------------------------
# C. Interest-rate gravity raises the MOS add-on
# ---------------------------------------------------------------------------
def test_high_treasury_low_earnings_yield_increases_mos_addon():
    # forward P/E 22 => earnings yield ~4.5%; 10y at 5% => negative spread.
    m = analyze_market_context(MarketContext(sp500_forward_pe=22, treasury_10y=5.0))
    assert m["equity_yield_spread_vs_10y"] is not None
    assert m["equity_yield_spread_vs_10y"] <= 0
    # Base VERY_EXPENSIVE add-on is +15; bond-gravity nudges it higher.
    assert m["suggested_margin_of_safety_addon_pct"] >= 15


def test_cash_optionality_flag_when_tbill_competitive():
    m = analyze_market_context(MarketContext(sp500_forward_pe=20, tbill_3m=6.0))
    assert "optionality" in (m["interest_rate_gravity_label"] or "")


# ---------------------------------------------------------------------------
# D. Corporate profit share warning + haircut
# ---------------------------------------------------------------------------
def test_high_profit_share_creates_warning_and_haircut():
    m = analyze_market_context(MarketContext(corporate_profit_share_pct=13.5))
    assert m["profit_share_warning"] is True
    assert m["forward_eps_haircut"] == "15%"


def test_normal_profit_share_no_warning():
    m = analyze_market_context(MarketContext(corporate_profit_share_pct=9.0))
    assert m["profit_share_warning"] is False
    assert m["forward_eps_haircut"] == "none"


# ---------------------------------------------------------------------------
# E. CAPE overlay (secondary)
# ---------------------------------------------------------------------------
def test_cape_stretched_bucket():
    m = analyze_market_context(MarketContext(market_cape=38))
    assert m["cape_bucket"] == "historically-stretched"


# ---------------------------------------------------------------------------
# F. Drawdown / panic opportunity
# ---------------------------------------------------------------------------
def test_severe_drawdown_with_improved_valuation_is_panic_opportunity():
    # Cheap forward P/E + big drawdown => dislocation candidate.
    m = analyze_market_context(MarketContext(sp500_forward_pe=13,
                                             sp500_drawdown_from_high_pct=35))
    assert m["market_regime"] == "PANIC_OPPORTUNITY"
    assert m["suggested_margin_of_safety_addon_pct"] < 0


def test_drawdown_but_still_extreme_keeps_caution():
    # Big drawdown but Buffett Indicator still extreme => stays cautious.
    m = analyze_market_context(MarketContext(buffett_indicator_gnp=205,
                                             sp500_drawdown_from_high_pct=25))
    assert m["market_regime"] == "PLAYING_WITH_FIRE"


# ---------------------------------------------------------------------------
# G. Missing data never crashes
# ---------------------------------------------------------------------------
def test_empty_context_returns_mixed_and_does_not_crash():
    m = analyze_market_context(MarketContext())
    assert m["market_regime"] == "MIXED_OR_INCOMPLETE_DATA"
    assert m["market_score_0_100"] is None
    assert m["suggested_margin_of_safety_addon_pct"] == 0


# ---------------------------------------------------------------------------
# H. market_adjusted_score behaviour (final_score never changes)
# ---------------------------------------------------------------------------
def _stock(final=90, val="FAIR", oey=0.03):
    return {"score": final, "valuation_label": val, "key": {"oe_yield": oey}}


def test_final_score_unchanged_when_overlay_active():
    m = analyze_market_context(MarketContext(sp500_forward_pe=23))  # VERY_EXPENSIVE
    stock = _stock(final=90)
    before = stock["score"]
    mas = market_adjusted_score(stock["score"], stock, m)
    # final_score field in the stock dict is untouched
    assert stock["score"] == before == 90
    # market_adjusted_score is a mild, separate number, lower here
    assert mas < 90


def test_market_penalty_applied_in_expensive_regime():
    m = analyze_market_context(MarketContext(sp500_forward_pe=23))  # VERY_EXPENSIVE -> penalty 7
    mas = market_adjusted_score(90, _stock(final=90, val="FAIR"), m)
    assert mas == 83.0


def test_attractive_high_oey_reduces_penalty():
    m = analyze_market_context(MarketContext(sp500_forward_pe=23))  # penalty 7
    # ATTRACTIVE + high owner-earnings yield => penalty halved (7 -> 3.5)
    mas_cheap = market_adjusted_score(90, _stock(90, "ATTRACTIVE", 0.07), m)
    mas_plain = market_adjusted_score(90, _stock(90, "FAIR", 0.03), m)
    assert mas_cheap > mas_plain
    assert mas_cheap == pytest.approx(86.5)


def test_very_expensive_stock_penalty_not_reduced():
    m = analyze_market_context(MarketContext(sp500_forward_pe=23))  # penalty 7
    mas = market_adjusted_score(90, _stock(90, "VERY EXPENSIVE", 0.02), m)
    assert mas == 83.0  # full penalty, no discount


def test_panic_regime_adds_bonus():
    m = analyze_market_context(MarketContext(sp500_forward_pe=13,
                                             sp500_drawdown_from_high_pct=35))
    assert m["market_regime"] == "PANIC_OPPORTUNITY"
    mas = market_adjusted_score(80, _stock(80, "ATTRACTIVE", 0.06), m)
    assert mas >= 80  # no penalty + small panic bonus


# ---------------------------------------------------------------------------
# I. Historical calibration sanity checks
# ---------------------------------------------------------------------------
def test_1999_2000_style_is_extreme_low_return():
    # Dot-com: very high market-cap/GDP + very high forward P/E.
    m = analyze_market_context(MarketContext(buffett_indicator_gnp=145,
                                             sp500_forward_pe=26))
    assert m["market_regime"] in ("VERY_EXPENSIVE", "PLAYING_WITH_FIRE")


def test_2021_style_extreme_marketcap_gdp_is_very_expensive_or_worse():
    m = analyze_market_context(MarketContext(buffett_indicator_gnp=200,
                                             sp500_forward_pe=22))
    assert m["market_regime"] in ("VERY_EXPENSIVE", "PLAYING_WITH_FIRE")


def test_2008_2009_style_dislocation_flagged_when_improved():
    m = analyze_market_context(MarketContext(sp500_forward_pe=11,
                                             buffett_indicator_gnp=60,
                                             sp500_drawdown_from_high_pct=45))
    assert m["market_regime"] == "PANIC_OPPORTUNITY"


def test_1979_style_cheap_stocks_high_bonds_not_treated_as_bad():
    # High bond yields but very cheap equities: regime should still be
    # attractive/fat-pitch on the valuation signal, not a poor-odds label.
    m = analyze_market_context(MarketContext(sp500_forward_pe=8,
                                             buffett_indicator_gnp=45,
                                             treasury_10y=10.0))
    assert m["market_regime"] == "FAT_PITCH"
    # earnings yield 12.5% still beats a 10% bond -> healthy premium
    assert m["equity_yield_spread_vs_10y"] > 0


if __name__ == "__main__":
    import sys
    sys.exit(pytest.main([__file__, "-q"]))
