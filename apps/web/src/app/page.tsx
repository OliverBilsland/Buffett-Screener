export default function Home() {
  return (
    <div className="home">
      <div className="hero">
        <div className="hero-eyebrow">EQUITY RESEARCH PIPELINE</div>
        <h1 className="hero-title">Screen for quality. Value the winners. Manage the risk.</h1>
        <p className="hero-sub">
          A Buffett-style screener scores companies across 80 rules, then hands the
          survivors to a valuation and risk engine — DCF, options, and portfolio
          analytics — all running in your browser.
        </p>
      </div>

      <div className="pipeline">
        <a href="/buffett" className="stage">
          <div className="stage-num">01</div>
          <div className="stage-name">Buffett Screener</div>
          <div className="stage-desc">
            80 quality rules across 12 categories. Verdict tiers, confidence caps,
            and a market-regime overlay surface durable compounders.
          </div>
          <div className="stage-cta">Open dashboard →</div>
        </a>

        <div className="arrow" aria-hidden="true">→</div>

        <a href="/valuation" className="stage">
          <div className="stage-num">02</div>
          <div className="stage-name">DCF Valuation</div>
          <div className="stage-desc">
            Two-stage discounted cash flow. Screened companies pre-fill with their
            real financials — base FCF, net debt, and historical growth.
          </div>
          <div className="stage-cta">Value a company →</div>
        </a>

        <div className="arrow" aria-hidden="true">→</div>

        <a href="/portfolio" className="stage">
          <div className="stage-num">03</div>
          <div className="stage-name">Portfolio Risk</div>
          <div className="stage-desc">
            Beta, volatility, concentration, and sector exposure — measured against
            the market, with true diversification via effective positions.
          </div>
          <div className="stage-cta">Analyze risk →</div>
        </a>
      </div>

      <div className="secondary-links">
        <a href="/screener" className="mini-link">
          <span className="mini-name">Quant Screener</span>
          <span className="mini-desc">Filter on ROIC, FCF growth, and valuation multiples</span>
        </a>
        <a href="/valuation/options" className="mini-link">
          <span className="mini-name">Options Builder</span>
          <span className="mini-desc">Multi-leg payoff diagrams and Black-Scholes pricing</span>
        </a>
        <a href="/research" className="mini-link">
          <span className="mini-name">AI Research</span>
          <span className="mini-desc">Bull/bear cases and filing analysis — bring your own key</span>
        </a>
        <a href="/journal" className="mini-link">
          <span className="mini-name">Trading Journal</span>
          <span className="mini-desc">AI feedback on execution and psychology — bring your own key</span>
        </a>
      </div>

      <div className="note">
        The four core modules (screener, DCF, portfolio, options) run entirely
        client-side and need no keys. The AI modules are optional and use your own
        Anthropic key, which stays in your browser and is never stored. All
        calculations are unit-tested against reference values (DCF hand
        calculations, Black-Scholes textbook prices, portfolio metrics).
      </div>
    </div>
  );
}
