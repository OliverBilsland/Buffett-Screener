#!/usr/bin/env node
/**
 * refresh-data.js — copy the Buffett screener's outputs into the web app.
 *
 * After a screener run:
 *     npm run refresh-data
 *     git add . && git commit -m "refresh data" && git push
 *
 * Copies three files (the third is optional):
 *   index.html                -> public/buffett.html          (the dashboard)
 *   screener_data.json        -> public/screener_data.json    (slim index, ~1.3MB)
 *   screener_financials.json  -> public/screener_financials.json (history, ~10MB)
 *
 * Prices come from a separate script (scripts/fetch_prices.py) since they're
 * pulled from Tiingo, not the screener.
 *
 * SOURCE FOLDER: defaults to the repo root (one level above this script's
 * parent), which is where the screener writes. Override with BUFFETT_OUTPUT_DIR.
 */
const fs = require("fs");
const path = require("path");

const REPO_ROOT = path.join(__dirname, "..");
const SRC_DIR = process.env.BUFFETT_OUTPUT_DIR || REPO_ROOT;
const PUBLIC_DIR = path.join(REPO_ROOT, "apps", "web", "public");

const FILES = [
  { from: "index.html", to: "buffett.html", required: true },
  { from: "screener_data.json", to: "screener_data.json", required: true },
  { from: "screener_financials.json", to: "screener_financials.json", required: false },
];

console.log(`source: ${SRC_DIR}`);
console.log(`target: ${PUBLIC_DIR}\n`);

if (!fs.existsSync(PUBLIC_DIR)) {
  fs.mkdirSync(PUBLIC_DIR, { recursive: true });
}

let hardFail = false;
for (const f of FILES) {
  const src = path.join(SRC_DIR, f.from);
  const dst = path.join(PUBLIC_DIR, f.to);
  if (!fs.existsSync(src)) {
    if (f.required) {
      console.error(`  MISSING (required): ${f.from}`);
      hardFail = true;
    } else {
      console.log(`  skipped (not found): ${f.from}`);
    }
    continue;
  }
  fs.copyFileSync(src, dst);
  const mb = fs.statSync(dst).size / 1024 / 1024;
  console.log(`  ${f.from} -> public/${f.to}  (${mb.toFixed(2)} MB)`);
}

if (hardFail) {
  console.error(`\nSome required files were missing in:\n  ${SRC_DIR}`);
  console.error("Run the screener first, or set BUFFETT_OUTPUT_DIR to its output folder.");
  process.exit(1);
}

// Warn if prices.json is stale or missing — the portfolio module needs it.
const pricesPath = path.join(PUBLIC_DIR, "prices.json");
if (!fs.existsSync(pricesPath)) {
  console.log("\nNote: public/prices.json not found. Portfolio risk needs it.");
  console.log("  Run: python scripts/fetch_prices.py  (needs PRICE_API_KEY)");
} else {
  try {
    const p = JSON.parse(fs.readFileSync(pricesPath, "utf8"));
    if (p.as_of) {
      const days = Math.round((Date.now() - new Date(p.as_of).getTime()) / 86400000);
      if (days > 14) {
        console.log(`\nNote: prices.json is ${days} days old.`);
        console.log("  Refresh with: python scripts/fetch_prices.py");
      }
    }
  } catch { /* ignore */ }
}

console.log("\nDone. Next: git add . && git commit -m 'refresh data' && git push");
