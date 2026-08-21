import type { Metadata } from 'next'
import Link from 'next/link'

// Directory / hub for every working tool on the site. Most of these pages were
// live but orphaned (linked from nowhere, absent from nav), so neither users nor
// Google could find them. This hub gives them a front door and interlinks them.

export const metadata: Metadata = {
  title: 'Free Quant & Congressional Trading Tools | QuantEngines',
  description:
    'Free tools for congressional-trade tracking, backtesting, market scanning, options, and more. No signup required — track politician stock trades, test strategies, and analyze the market.',
  alternates: { canonical: 'https://quantengines.com/tools' },
}

type Tool = { href: string; name: string; desc: string }
type Group = { title: string; blurb: string; tools: Tool[] }

const GROUPS: Group[] = [
  {
    title: 'Congressional Trading',
    blurb: 'Track what members of Congress are buying and selling.',
    tools: [
      { href: '/congress-stock-trades', name: 'Congress Stock Trades', desc: 'Latest real House & Senate trades from official STOCK Act disclosures, updated daily.' },
      { href: '/politicians', name: 'Politician Tracker', desc: 'Browse individual politicians and their full trading records.' },
      { href: '/leaderboard', name: 'Trader Leaderboard', desc: 'Congressional traders ranked by activity and estimated performance.' },
      { href: '/discoveries', name: 'Anomaly Detection', desc: 'Automatically flags unusual, well-timed, or outsized trades.' },
      { href: '/network', name: 'Network Analysis', desc: 'Interactive graph of trading correlations between members.' },
    ],
  },
  {
    title: 'Trading & Market Tools',
    blurb: 'Test ideas and analyze the market — free, no account needed.',
    tools: [
      { href: '/backtesting', name: 'Backtesting Engine', desc: 'Test trading strategies against historical market data.' },
      { href: '/backtesting/builder', name: 'Strategy Builder', desc: 'Create a strategy with a visual, form-based editor — no code.' },
      { href: '/strategies', name: 'Strategy Library', desc: 'Pre-built, ready-to-run strategies like MA crossover and RSI.' },
      { href: '/scanner', name: 'Stock Scanner', desc: 'Scan the market for setups, breakouts, and signals.' },
      { href: '/signals', name: 'Trade Signals', desc: 'Data-driven signals surfaced from market and trade data.' },
      { href: '/charts', name: 'Advanced Charts', desc: 'Interactive price charts with technical overlays.' },
      { href: '/market-dashboard', name: 'Market Dashboard', desc: 'Free live market data at a glance.' },
      { href: '/backtrader-vs-vectorbt', name: 'backtrader vs vectorbt', desc: 'The same strategy through both libraries on the same bars — they agree to the cent, but only after pinning three defaults. With the divergence decomposed.' },
      { href: '/indicator-formulas', name: 'Indicator Formulas (Verified)', desc: 'RSI, ADX, ATR, MACD, Bollinger and Stochastic — each implemented independently and cross-checked against pandas_ta on real bars.' },
      { href: '/statsmodels-imports', name: 'statsmodels Import Reference', desc: 'Which import paths work, measured by executing every statement — including the three that succeed and fail later.' },
      { href: '/cot-report', name: 'COT Report Positioning', desc: 'Speculator and hedger net positioning for 11 futures markets, normalised by open interest and z-scored against up to 21 years of each market’s own history.' },
      { href: '/yield-curve', name: 'Treasury Yield Curve', desc: 'Today’s par curve plus every sustained 10y−2y inversion since 1990 — dates, durations and depths computed from Treasury’s daily series.' },
      { href: '/fundamentals', name: 'Fundamental Screener', desc: 'Accruals, asset growth and net share issuance for 3,000+ US filers, computed straight from SEC XBRL filings and matched to each company’s own fiscal year.' },
    ],
  },
  {
    title: 'Calculators',
    blurb:
      'Closed-form math over the numbers you type in. These use no market data at all, so every figure they show can be checked by hand.',
    tools: [
      { href: '/tools/position-size', name: 'Position Size Calculator', desc: 'Share count implied by your account size, risk per trade, entry, and stop-loss. Handles longs and shorts.' },
      { href: '/tools/kelly-criterion', name: 'Kelly Criterion Calculator', desc: 'Edge-optimal stake from your win rate and win/loss ratio, with a half/quarter-Kelly comparison and growth-rate chart.' },
      { href: '/tools/risk-reward', name: 'Risk/Reward Ratio Calculator', desc: 'Reward-to-risk ratio, each distance as a percentage of entry, and the breakeven win rate the ratio implies.' },
      { href: '/options', name: 'Black-Scholes Options Calculator', desc: 'Theoretical value and all five Greeks for a European call or put, from spot, strike, expiry, volatility, and rate.' },
      { href: '/tools/max-sharpe', name: 'Max Sharpe Ratio Portfolio', desc: 'Tangency portfolio weights from the closed form w ∝ Σ⁻¹(μ − rf·1), for up to five assets, with the derivation and a worked example.' },
    ],
  },
]

export default function ToolsPage() {
  return (
    <div className="container mx-auto px-4 py-12">
      <div className="max-w-3xl mb-12">
        <h1 className="text-4xl md:text-5xl font-bold mb-4 text-white">Free Trading Tools</h1>
        <p className="text-lg text-slate-400">
          Everything QuantEngines offers in one place — congressional-trade tracking,
          backtesting, market scanning, and more. All free, no signup required.
        </p>
      </div>

      <div className="space-y-14">
        {GROUPS.map((group) => (
          <section key={group.title}>
            <div className="mb-5">
              <h2 className="text-2xl font-bold text-white">{group.title}</h2>
              <p className="text-slate-400">{group.blurb}</p>
            </div>
            <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
              {group.tools.map((t) => (
                <Link
                  key={t.href}
                  href={t.href}
                  className="group rounded-xl border border-[hsl(215,40%,18%)] bg-[hsl(220,55%,9%)] p-5 transition-all hover:border-indigo-500/60 hover:bg-[hsl(220,55%,11%)]"
                >
                  <h3 className="text-lg font-semibold text-white group-hover:text-indigo-400 transition-colors">
                    {t.name}
                  </h3>
                  <p className="mt-1.5 text-sm text-slate-400">{t.desc}</p>
                  <span className="mt-3 inline-block text-sm font-medium text-indigo-400">
                    Open tool →
                  </span>
                </Link>
              ))}
            </div>
          </section>
        ))}
      </div>
    </div>
  )
}
