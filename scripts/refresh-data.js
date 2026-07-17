#!/usr/bin/env node
/**
 * refresh-data.js — one-command data refresh for the investor platform.
 *
 * Copies the two files your Buffett screener generates into apps/web/public/,
 * so refreshing the live site is: run screener -> `npm run refresh-data` -> push.
 *
 * SET THIS ONCE: the path to the folder where your screener writes its outputs.
 * Either edit BUFFETT_OUTPUT_DIR below, or set the env var BUFFETT_OUTPUT_DIR.
 */
const fs = require("fs");
const path = require("path");

// >>> EDIT THIS to your screener's output folder (where index.html + screener_data.json land) <<<
const BUFFETT_OUTPUT_DIR =
  process.env.BUFFETT_OUTPUT_DIR ||
  "C:\\Users\\obilsla\\OneDrive - FTI Consulting\\Desktop\\buffett-repo";

const PUBLIC_DIR = path.join(__dirname, "..", "apps", "web", "public");

const FILES = [
  { from: "index.html", to: "buffett.html" },          // dashboard -> served at /buffett.html
  { from: "screener_data.json", to: "screener_data.json" }, // handoff -> QuantHub reads this
];

let ok = true;
for (const f of FILES) {
  const src = path.join(BUFFETT_OUTPUT_DIR, f.from);
  const dst = path.join(PUBLIC_DIR, f.to);
  if (!fs.existsSync(src)) {
    console.error(`  MISSING: ${src}`);
    console.error(`  -> Check BUFFETT_OUTPUT_DIR in scripts/refresh-data.js`);
    ok = false;
    continue;
  }
  fs.copyFileSync(src, dst);
  const kb = (fs.statSync(dst).size / 1024).toFixed(0);
  console.log(`  copied ${f.from} -> public/${f.to} (${kb} KB)`);
}

if (ok) {
  console.log("\nData refreshed. Next: git add . && git commit -m 'refresh data' && git push");
} else {
  console.error("\nSome files were missing — see above. Nothing was pushed.");
  process.exit(1);
}
