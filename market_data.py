"""market_data.py — key-free, cloud-safe market snapshot and industry classification.

Why this exists
---------------
The screener's fundamentals come from SEC EDGAR, an official API that allows
automated access. Its price, market cap, and sector data used to come from
Yahoo Finance via `yfinance`, which is a scraper of a consumer website. Yahoo
blocks datacenter IPs (GitHub Actions included), so a scheduled run could never
complete. This module replaces that dependency with two official sources:

  * Nasdaq's exchange screener feed: one request returns every US-listed
    common stock (NYSE, Nasdaq, NYSE American) with last price, market cap,
    sector and industry. ~7,000 rows, ~2 MB, ~4 seconds.
  * SEC EDGAR submissions: each filer's SIC code, used to sharpen the
    industry classification where the exchange's taxonomy is coarse.

Both are mapped onto the Yahoo/Morningstar-style sector and industry strings
the rule engine was calibrated against ("Banks - Regional", "Insurance -
Property & Casualty", "Software - Application", ...), so every keyword rule,
special model, and risk cap fires exactly as before.

Public surface
--------------
    load_snapshot(cache_dir, max_age_hours) -> dict[ticker] -> row
    classify(nasdaq_sector, nasdaq_industry, sic=None) -> (sector, industry)
    sic_for(cik, cache_dir, ua, max_age_hours) -> (sic:int|None, desc:str)
"""
from __future__ import annotations

import json
import pickle
import time
from pathlib import Path

import requests

NASDAQ_SCREENER_URL = (
    "https://api.nasdaq.com/api/screener/stocks"
    "?tableonly=true&limit=25&offset=0&download=true"
)
_NASDAQ_HEADERS = {
    "User-Agent": ("Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
                   "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0 Safari/537.36"),
    "Accept": "application/json, text/plain, */*",
    "Accept-Language": "en-US,en;q=0.9",
    "Referer": "https://www.nasdaq.com/market-activity/stocks/screener",
}


# ----------------------------------------------------------------------------
# Snapshot
# ----------------------------------------------------------------------------

def _num(s):
    try:
        s = str(s).replace("$", "").replace(",", "").strip()
        return float(s) if s not in ("", "NA", "N/A") else None
    except Exception:
        return None


def load_snapshot(cache_dir: Path | str = ".buffett_cache",
                  max_age_hours: float = 24, quiet: bool = False) -> dict:
    """{TICKER: {price, mcap, name, sector, industry, country, ipo_year}}.

    Disk-cached. Returns {} (never raises) if the feed is unreachable, so the
    caller can fall back to per-ticker lookups.
    """
    cache_dir = Path(cache_dir)
    p = cache_dir / "nasdaq_snapshot.pkl"
    if p.exists() and (time.time() - p.stat().st_mtime) / 3600 < max_age_hours:
        try:
            return pickle.loads(p.read_bytes())
        except Exception:
            pass
    try:
        resp = requests.get(NASDAQ_SCREENER_URL, headers=_NASDAQ_HEADERS, timeout=60)
        resp.raise_for_status()
        rows = resp.json()["data"]["rows"]
    except Exception as e:  # noqa: BLE001
        if not quiet:
            print(f"  !! Nasdaq screener feed unavailable ({type(e).__name__}: {e}); "
                  "falling back to per-ticker lookups.")
        return {}
    out = {}
    for r in rows:
        tk = str(r.get("symbol", "")).strip().upper().replace("/", "-").replace("^", "-")
        if not tk:
            continue
        out[tk] = {
            "price": _num(r.get("lastsale")),
            "mcap": _num(r.get("marketCap")),
            "name": (r.get("name") or "").strip(),
            "sector": (r.get("sector") or "").strip(),
            "industry": (r.get("industry") or "").strip(),
            "country": (r.get("country") or "").strip(),
            "ipo_year": _num(r.get("ipoyear")),
        }
    try:
        cache_dir.mkdir(exist_ok=True)
        p.write_bytes(pickle.dumps(out))
    except Exception:
        pass
    if not quiet:
        print(f"  Exchange snapshot: {len(out):,} US listings with price, cap, "
              f"sector, industry (Nasdaq screener feed).")
    return out


# ----------------------------------------------------------------------------
# Fallback cap proxy: SEC public-float frames (one call per quarter, all filers)
# ----------------------------------------------------------------------------

def public_float_by_cik(cache_dir: Path | str, ua: str, max_age_hours: float = 24 * 7,
                        quarters: int = 8) -> dict:
    """{zero-padded CIK: latest reported EntityPublicFloat (USD)}.

    Used only when the exchange snapshot is unavailable. Public float is the
    market value of non-affiliate shares, so it understates market cap for
    insider-heavy companies; callers should widen the lower bound accordingly.
    """
    cache_dir = Path(cache_dir)
    p = cache_dir / "sec_public_float.pkl"
    if p.exists() and (time.time() - p.stat().st_mtime) / 3600 < max_age_hours:
        try:
            return pickle.loads(p.read_bytes())
        except Exception:
            pass
    import datetime as _dt
    today = _dt.date.today()
    periods = []
    y, q = today.year, (today.month - 1) // 3 + 1
    for _ in range(quarters):
        periods.append(f"CY{y}Q{q}I")
        q -= 1
        if q == 0:
            y, q = y - 1, 4
    out = {}
    for per in reversed(periods):   # oldest first so newer overwrite
        try:
            r = requests.get(
                f"https://data.sec.gov/api/xbrl/frames/dei/EntityPublicFloat/USD/{per}.json",
                headers={"User-Agent": ua}, timeout=60)
            if r.status_code != 200:
                continue
            for row in r.json().get("data", []):
                cik = str(row.get("cik", "")).zfill(10)
                val = row.get("val")
                if cik and val is not None:
                    out[cik] = float(val)
            time.sleep(0.15)
        except Exception:
            continue
    try:
        cache_dir.mkdir(exist_ok=True)
        p.write_bytes(pickle.dumps(out))
    except Exception:
        pass
    return out


# ----------------------------------------------------------------------------
# SIC codes from EDGAR submissions
# ----------------------------------------------------------------------------

def sic_for(cik: str, cache_dir: Path | str, ua: str,
            max_age_hours: float = 24 * 30) -> tuple[int | None, str]:
    """(SIC code, SIC description) for a zero-padded CIK, cached 30 days."""
    cache_dir = Path(cache_dir)
    p = cache_dir / f"sic_{cik}.pkl"
    if p.exists() and (time.time() - p.stat().st_mtime) / 3600 < max_age_hours:
        try:
            return pickle.loads(p.read_bytes())
        except Exception:
            pass
    try:
        r = requests.get(f"https://data.sec.gov/submissions/CIK{cik}.json",
                         headers={"User-Agent": ua}, timeout=30)
        r.raise_for_status()
        j = r.json()
        sic = int(j["sic"]) if str(j.get("sic") or "").isdigit() else None
        desc = (j.get("sicDescription") or "").strip()
        time.sleep(0.12)
    except Exception:
        sic, desc = None, ""
    try:
        cache_dir.mkdir(exist_ok=True)
        p.write_bytes(pickle.dumps((sic, desc)))
    except Exception:
        pass
    return sic, desc


# ----------------------------------------------------------------------------
# Classification -> Yahoo/Morningstar-style (sector, industry)
# ----------------------------------------------------------------------------

YAHOO_SECTOR = {
    "finance": "Financial Services",
    "health care": "Healthcare",
    "consumer discretionary": "Consumer Cyclical",
    "consumer staples": "Consumer Defensive",
    "telecommunications": "Communication Services",
    "technology": "Technology",
    "industrials": "Industrials",
    "energy": "Energy",
    "basic materials": "Basic Materials",
    "real estate": "Real Estate",
    "utilities": "Utilities",
    "miscellaneous": "Industrials",
}

# Nasdaq industry (lower-cased, whitespace-normalised) -> (sector or None, industry)
# A sector of None keeps the Nasdaq sector; a string overrides it.
NASDAQ_INDUSTRY = {
    # --- financials ---
    "major banks": ("Financial Services", "Banks - Regional"),
    "commercial banks": ("Financial Services", "Banks - Regional"),
    "banks": ("Financial Services", "Banks - Regional"),
    "savings institutions": ("Financial Services", "Banks - Regional"),
    "property-casualty insurers": ("Financial Services", "Insurance - Property & Casualty"),
    "life insurance": ("Financial Services", "Insurance - Life"),
    "accident &health insurance": ("Financial Services", "Insurance - Life"),
    "specialty insurers": ("Financial Services", "Insurance - Specialty"),
    "investment managers": ("Financial Services", "Asset Management"),
    "investment bankers/brokers/service": ("Financial Services", "Capital Markets"),
    "finance/investors services": ("Financial Services", "Capital Markets"),
    "finance: consumer services": ("Financial Services", "Credit Services"),
    "finance companies": ("Financial Services", "Credit Services"),
    "diversified financial services": ("Financial Services", "Financial Conglomerates"),
    "blank checks": ("Financial Services", "Shell Companies"),
    "trusts except educational religious and charitable": ("Financial Services", "Asset Management"),
    "real estate investment trusts": ("Real Estate", "REIT - Diversified"),
    "real estate": ("Real Estate", "Real Estate Services"),
    "building operators": ("Real Estate", "Real Estate Services"),
    # --- technology ---
    "computer software: prepackaged software": ("Technology", "Software - Application"),
    "computer software: programming data processing": ("Technology", "Software - Infrastructure"),
    "edp services": ("Technology", "Information Technology Services"),
    "semiconductors": ("Technology", "Semiconductors"),
    "computer manufacturing": ("Technology", "Computer Hardware"),
    "computer peripheral equipment": ("Technology", "Computer Hardware"),
    "electronic components": ("Technology", "Electronic Components"),
    "computer communications equipment": ("Technology", "Communication Equipment"),
    "telecommunications equipment": ("Technology", "Communication Equipment"),
    "radio and television broadcasting and communications equipment": ("Technology", "Communication Equipment"),
    "consumer electronics/appliances": ("Technology", "Consumer Electronics"),
    "retail: computer software & peripheral equipment": ("Technology", "Electronics & Computer Distribution"),
    "electronics distribution": ("Technology", "Electronics & Computer Distribution"),
    "office equipment/supplies/services": ("Industrials", "Business Equipment & Supplies"),
    "electrical products": ("Industrials", "Electrical Equipment & Parts"),
    "cable & other pay television services": ("Communication Services", "Telecom Services"),
    # --- energy ---
    "oil & gas production": ("Energy", "Oil & Gas E&P"),
    "integrated oil companies": ("Energy", "Oil & Gas Integrated"),
    "oil refining/marketing": ("Energy", "Oil & Gas Refining & Marketing"),
    "oilfield services/equipment": ("Energy", "Oil & Gas Equipment & Services"),
    "oil and gas field machinery": ("Energy", "Oil & Gas Equipment & Services"),
    "oil/gas transmission": ("Energy", "Oil & Gas Midstream"),
    "coal mining": ("Energy", "Thermal Coal"),
    # --- materials ---
    "precious metals": ("Basic Materials", "Gold"),
    "metal mining": ("Basic Materials", "Other Industrial Metals & Mining"),
    "other metals and minerals": ("Basic Materials", "Other Industrial Metals & Mining"),
    "mining & quarrying of nonmetallic minerals (no fuels)": ("Basic Materials", "Other Industrial Metals & Mining"),
    "steel/iron ore": ("Basic Materials", "Steel"),
    "aluminum": ("Basic Materials", "Aluminum"),
    "major chemicals": ("Basic Materials", "Chemicals"),
    "specialty chemicals": ("Basic Materials", "Specialty Chemicals"),
    "agricultural chemicals": ("Basic Materials", "Agricultural Inputs"),
    "paints/coatings": ("Basic Materials", "Specialty Chemicals"),
    "plastic products": ("Basic Materials", "Specialty Chemicals"),
    "paper": ("Basic Materials", "Paper & Paper Products"),
    "forest products": ("Basic Materials", "Lumber & Wood Production"),
    "building materials": ("Basic Materials", "Building Materials"),
    "containers/packaging": ("Consumer Cyclical", "Packaging & Containers"),
    # --- consumer cyclical ---
    "apparel": ("Consumer Cyclical", "Apparel Manufacturing"),
    "garments and clothing": ("Consumer Cyclical", "Apparel Manufacturing"),
    "textiles": ("Consumer Cyclical", "Textile Manufacturing"),
    "shoe manufacturing": ("Consumer Cyclical", "Footwear & Accessories"),
    "clothing/shoe/accessory stores": ("Consumer Cyclical", "Apparel Retail"),
    "department/specialty retail stores": ("Consumer Cyclical", "Department Stores"),
    "other specialty stores": ("Consumer Cyclical", "Specialty Retail"),
    "catalog/specialty distribution": ("Consumer Cyclical", "Internet Retail"),
    "consumer electronics/video chains": ("Consumer Cyclical", "Specialty Retail"),
    "auto & home supply stores": ("Consumer Cyclical", "Specialty Retail"),
    "retail: building materials": ("Consumer Cyclical", "Home Improvement Retail"),
    "retail-auto dealers and gas stations": ("Consumer Cyclical", "Auto & Truck Dealerships"),
    "home furnishings": ("Consumer Cyclical", "Furnishings, Fixtures & Appliances"),
    "consumer specialties": ("Consumer Cyclical", "Leisure"),
    "recreational games/products/toys": ("Consumer Cyclical", "Leisure"),
    "durable goods": ("Consumer Cyclical", "Furnishings, Fixtures & Appliances"),
    "auto parts:o.e.m.": ("Consumer Cyclical", "Auto Parts"),
    "automotive aftermarket": ("Consumer Cyclical", "Auto Parts"),
    "motor vehicles": ("Consumer Cyclical", "Auto Manufacturers"),
    "auto manufacturing": ("Consumer Cyclical", "Auto Manufacturers"),
    "homebuilding": ("Consumer Cyclical", "Residential Construction"),
    "hotels/resorts": ("Consumer Cyclical", "Lodging"),
    "services-misc. amusement & recreation": ("Consumer Cyclical", "Resorts & Casinos"),
    "restaurants": ("Consumer Cyclical", "Restaurants"),
    "movies/entertainment": ("Communication Services", "Entertainment"),
    "advertising": ("Communication Services", "Advertising Agencies"),
    "broadcasting": ("Communication Services", "Broadcasting"),
    "newspapers/magazines": ("Communication Services", "Publishing"),
    "books": ("Communication Services", "Publishing"),
    "publishing": ("Communication Services", "Publishing"),
    "package goods/cosmetics": ("Consumer Defensive", "Household & Personal Products"),
    "tobacco": ("Consumer Defensive", "Tobacco"),
    "rental/leasing companies": ("Industrials", "Rental & Leasing Services"),
    "misc corporate leasing services": ("Industrials", "Rental & Leasing Services"),
    "other consumer services": ("Consumer Cyclical", "Personal Services"),
    "professional services": ("Industrials", "Consulting Services"),
    "business services": ("Industrials", "Specialty Business Services"),
    "diversified commercial services": ("Industrials", "Specialty Business Services"),
    "tools/hardware": ("Industrials", "Tools & Accessories"),
    "wholesale distributors": ("Industrials", "Industrial Distribution"),
    "professional and commerical equipment": ("Industrials", "Industrial Distribution"),
    "miscellaneous manufacturing industries": ("Industrials", "Specialty Industrial Machinery"),
    "industrial specialties": ("Industrials", "Specialty Industrial Machinery"),
    "multi-sector companies": ("Industrials", "Conglomerates"),
    "miscellaneous": ("Industrials", "Conglomerates"),
    # --- transport ---
    "air freight/delivery services": ("Industrials", "Integrated Freight & Logistics"),
    "integrated freight & logistics": ("Industrials", "Integrated Freight & Logistics"),
    "transportation services": ("Industrials", "Integrated Freight & Logistics"),
    "other transportation": ("Industrials", "Integrated Freight & Logistics"),
    "marine transportation": ("Industrials", "Marine Shipping"),
    "trucking freight/courier services": ("Industrials", "Trucking"),
    "railroads": ("Industrials", "Railroads"),
    # --- industrials ---
    "industrial machinery/components": ("Industrials", "Specialty Industrial Machinery"),
    "construction/ag equipment/trucks": ("Industrials", "Farm & Heavy Construction Machinery"),
    "metal fabrications": ("Industrials", "Metal Fabrication"),
    "fluid controls": ("Industrials", "Specialty Industrial Machinery"),
    "building products": ("Industrials", "Building Products & Equipment"),
    "engineering & construction": ("Industrials", "Engineering & Construction"),
    "general bldg contractors - nonresidential bldgs": ("Industrials", "Engineering & Construction"),
    "water sewer pipeline comm & power line construction": ("Industrials", "Engineering & Construction"),
    "military/government/technical": ("Industrials", "Aerospace & Defense"),
    "aerospace": ("Industrials", "Aerospace & Defense"),
    "ordnance and accessories": ("Industrials", "Aerospace & Defense"),
    "environmental services": ("Industrials", "Waste Management"),
    "pollution control equipment": ("Industrials", "Pollution & Treatment Controls"),
    # --- consumer defensive ---
    "beverages (production/distribution)": ("Consumer Defensive", "Beverages - Non-Alcoholic"),
    "packaged foods": ("Consumer Defensive", "Packaged Foods"),
    "specialty foods": ("Consumer Defensive", "Packaged Foods"),
    "meat/poultry/fish": ("Consumer Defensive", "Farm Products"),
    "farming/seeds/milling": ("Consumer Defensive", "Farm Products"),
    "food chains": ("Consumer Defensive", "Grocery Stores"),
    "food distributors": ("Consumer Defensive", "Food Distribution"),
    "retail-drug stores and proprietary stores": ("Healthcare", "Pharmaceutical Retailers"),
    # --- healthcare ---
    "biotechnology: biological products (no diagnostic substances)": ("Healthcare", "Biotechnology"),
    "biotechnology: pharmaceutical preparations": ("Healthcare", "Drug Manufacturers - Specialty & Generic"),
    "biotechnology: in vitro & in vivo diagnostic substances": ("Healthcare", "Diagnostics & Research"),
    "biotechnology: commercial physical & biological resarch": ("Healthcare", "Diagnostics & Research"),
    "biotechnology: laboratory analytical instruments": ("Healthcare", "Diagnostics & Research"),
    "biotechnology: electromedical & electrotherapeutic apparatus": ("Healthcare", "Medical Devices"),
    "medical/dental instruments": ("Healthcare", "Medical Instruments & Supplies"),
    "medical specialities": ("Healthcare", "Medical Devices"),
    "medical electronics": ("Healthcare", "Medical Devices"),
    "ophthalmic goods": ("Healthcare", "Medical Instruments & Supplies"),
    "precision instruments": ("Healthcare", "Scientific & Technical Instruments"),
    "medical/nursing services": ("Healthcare", "Medical Care Facilities"),
    "hospital/nursing management": ("Healthcare", "Medical Care Facilities"),
    "misc health and biotechnology services": ("Healthcare", "Health Information Services"),
    "managed health care": ("Healthcare", "Healthcare Plans"),
    "other pharmaceuticals": ("Healthcare", "Drug Manufacturers - Specialty & Generic"),
    "pharmaceuticals and biotechnology": ("Healthcare", "Drug Manufacturers - General"),
    "medicinal chemicals and botanical products": ("Healthcare", "Drug Manufacturers - Specialty & Generic"),
    # --- utilities ---
    "electric utilities: central": ("Utilities", "Utilities - Regulated Electric"),
    "power generation": ("Utilities", "Utilities - Independent Power Producers"),
    "natural gas distribution": ("Utilities", "Utilities - Regulated Gas"),
    "water supply": ("Utilities", "Utilities - Regulated Water"),
}

# SIC ranges -> (sector, industry). Checked first when a SIC is known, because
# the SEC code is more precise than the exchange's bucket for exactly the
# cases the rule engine cares most about (banks, insurers, REITs, SPACs,
# software, semis, E&P, pharma, staffing, homebuilders, utilities).
SIC_RULES = [
    ((6770, 6770), ("Financial Services", "Shell Companies")),
    ((6020, 6036), ("Financial Services", "Banks - Regional")),
    ((6099, 6099), ("Financial Services", "Credit Services")),
    ((6111, 6163), ("Financial Services", "Credit Services")),
    ((6172, 6172), ("Financial Services", "Credit Services")),
    ((6189, 6189), ("Financial Services", "Mortgage Finance")),
    ((6199, 6199), ("Financial Services", "Capital Markets")),
    ((6200, 6200), ("Financial Services", "Financial Data & Stock Exchanges")),
    ((6211, 6211), ("Financial Services", "Capital Markets")),
    ((7320, 7320), ("Financial Services", "Financial Data & Stock Exchanges")),
    ((6221, 6221), ("Financial Services", "Capital Markets")),
    ((6282, 6282), ("Financial Services", "Asset Management")),
    ((6311, 6311), ("Financial Services", "Insurance - Life")),
    ((6321, 6324), ("Financial Services", "Insurance - Life")),
    ((6331, 6331), ("Financial Services", "Insurance - Property & Casualty")),
    ((6351, 6351), ("Financial Services", "Insurance - Specialty")),
    ((6361, 6361), ("Financial Services", "Insurance - Specialty")),
    ((6399, 6399), ("Financial Services", "Insurance - Diversified")),
    ((6411, 6411), ("Financial Services", "Insurance Brokers")),
    ((6798, 6798), ("Real Estate", "REIT - Diversified")),
    ((6500, 6553), ("Real Estate", "Real Estate Services")),
    # 7370/7371/7373/7374 are generic "computer services" buckets that hold
    # Visa, FactSet and Paychex alike; the exchange's industry is better there.
    ((7372, 7372), ("Technology", "Software - Application")),
    ((3674, 3674), ("Technology", "Semiconductors")),
    ((3559, 3559), ("Technology", "Semiconductor Equipment & Materials")),
    ((1311, 1311), ("Energy", "Oil & Gas E&P")),
    ((1381, 1389), ("Energy", "Oil & Gas Equipment & Services")),
    ((2911, 2911), ("Energy", "Oil & Gas Refining & Marketing")),
    ((4610, 4613), ("Energy", "Oil & Gas Midstream")),
    ((1220, 1221), ("Energy", "Thermal Coal")),
    ((1000, 1099), ("Basic Materials", "Other Industrial Metals & Mining")),
    ((1040, 1044), ("Basic Materials", "Gold")),
    ((3312, 3317), ("Basic Materials", "Steel")),
    ((3334, 3334), ("Basic Materials", "Aluminum")),
    ((2800, 2829), ("Basic Materials", "Chemicals")),
    ((2851, 2899), ("Basic Materials", "Specialty Chemicals")),
    ((2870, 2879), ("Basic Materials", "Agricultural Inputs")),
    ((2600, 2679), ("Basic Materials", "Paper & Paper Products")),
    ((2400, 2452), ("Basic Materials", "Lumber & Wood Production")),
    ((2834, 2834), ("Healthcare", "Drug Manufacturers - Specialty & Generic")),
    ((2835, 2836), ("Healthcare", "Biotechnology")),
    ((8071, 8071), ("Healthcare", "Diagnostics & Research")),
    ((8731, 8731), ("Healthcare", "Diagnostics & Research")),
    ((8000, 8069), ("Healthcare", "Medical Care Facilities")),
    ((8082, 8099), ("Healthcare", "Medical Care Facilities")),
    ((3841, 3845), ("Healthcare", "Medical Devices")),
    ((6324, 6324), ("Healthcare", "Healthcare Plans")),
    ((7361, 7363), ("Industrials", "Staffing & Employment Services")),
    ((8741, 8748), ("Industrials", "Consulting Services")),
    ((8200, 8299), ("Consumer Defensive", "Education & Training Services")),
    ((1520, 1531), ("Consumer Cyclical", "Residential Construction")),
    ((3711, 3711), ("Consumer Cyclical", "Auto Manufacturers")),
    ((3714, 3714), ("Consumer Cyclical", "Auto Parts")),
    ((2300, 2399), ("Consumer Cyclical", "Apparel Manufacturing")),
    ((3140, 3149), ("Consumer Cyclical", "Footwear & Accessories")),
    ((5600, 5699), ("Consumer Cyclical", "Apparel Retail")),
    ((5311, 5311), ("Consumer Cyclical", "Department Stores")),
    ((5331, 5399), ("Consumer Defensive", "Discount Stores")),
    ((5812, 5812), ("Consumer Cyclical", "Restaurants")),
    ((7011, 7011), ("Consumer Cyclical", "Lodging")),
    ((7990, 7999), ("Consumer Cyclical", "Resorts & Casinos")),
    ((4512, 4513), ("Industrials", "Airlines")),
    ((4400, 4412), ("Industrials", "Marine Shipping")),
    ((4911, 4911), ("Utilities", "Utilities - Regulated Electric")),
    ((4920, 4925), ("Utilities", "Utilities - Regulated Gas")),
    ((4931, 4932), ("Utilities", "Utilities - Diversified")),
    ((4941, 4941), ("Utilities", "Utilities - Regulated Water")),
    ((7310, 7319), ("Communication Services", "Advertising Agencies")),
    ((2711, 2741), ("Communication Services", "Publishing")),
    ((4832, 4841), ("Communication Services", "Broadcasting")),
    ((3570, 3579), ("Technology", "Computer Hardware")),
    ((3661, 3669), ("Technology", "Communication Equipment")),
]
# Gold's range sits inside the general mining range; order matters, so make
# the narrower rule win by sorting on span.
SIC_RULES.sort(key=lambda r: r[0][1] - r[0][0])


def _norm(s: str) -> str:
    return " ".join((s or "").lower().split())


def classify(nasdaq_sector: str, nasdaq_industry: str,
             sic: int | None = None) -> tuple[str, str]:
    """Return a Yahoo-style (sector, industry). Empty strings if unknown."""
    if sic is not None:
        for (lo, hi), (sec, ind) in SIC_RULES:
            if lo <= sic <= hi:
                return sec, ind
    ind_key = _norm(nasdaq_industry)
    sec_key = _norm(nasdaq_sector)
    hit = NASDAQ_INDUSTRY.get(ind_key)
    if hit:
        sec, ind = hit
        return (sec or YAHOO_SECTOR.get(sec_key, nasdaq_sector or "")), ind
    if ind_key:
        # Unmapped industry: keep the exchange's wording so keyword rules still
        # have something to match on, under a mapped sector.
        return YAHOO_SECTOR.get(sec_key, nasdaq_sector or ""), (nasdaq_industry or "").strip()
    return YAHOO_SECTOR.get(sec_key, ""), ""


if __name__ == "__main__":  # quick manual check
    snap = load_snapshot()
    for t in ("DECK", "GL", "RNR", "FHB", "CRUS", "JPM", "AZO", "FDS", "KNSL", "MEDP"):
        r = snap.get(t, {})
        print(t, r.get("price"), r.get("mcap"), classify(r.get("sector", ""), r.get("industry", "")))
