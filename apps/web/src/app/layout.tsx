import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "Investor Platform",
  description: "Buffett-style quality screening feeding DCF valuation and portfolio risk analytics",
};

const NAV = [
  { href: "/", label: "Home" },
  { href: "/buffett.html", label: "Buffett Screener", external: true },
  { href: "/screener", label: "Quant Screener" },
  { href: "/valuation", label: "DCF Valuation" },
  { href: "/valuation/options", label: "Options" },
  { href: "/portfolio", label: "Portfolio Risk" },
  { href: "/research", label: "Research" },
  { href: "/journal", label: "Journal" },
];

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body>
        <header className="topbar">
          <a href="/" className="brand">◪ INVESTOR PLATFORM</a>
          <nav className="topnav">
            {NAV.slice(1).map((n) =>
              n.external ? (
                <a key={n.href} href={n.href} className="topnav-item">{n.label}</a>
              ) : (
                <a key={n.href} href={n.href} className="topnav-item">{n.label}</a>
              )
            )}
          </nav>
        </header>
        <main className="page">{children}</main>
      </body>
    </html>
  );
}
