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
      { href: '/options', name: 'Options Calculator', desc: 'Price options and analyze the Greeks.' },
      { href: '/signals', name: 'Trade Signals', desc: 'Data-driven signals surfaced from market and trade data.' },
      { href: '/charts', name: 'Advanced Charts', desc: 'Interactive price charts with technical overlays.' },
      { href: '/market-dashboard', name: 'Market Dashboard', desc: 'Free live market data at a glance.' },
    ],
  },
  {
    title: 'Risk Management Calculators',
    blurb: 'Size trades and check the math before you commit capital.',
    tools: [
      { href: '/tools/position-size', name: 'Position Size Calculator', desc: 'Find how many shares to buy from your account size, risk per trade, entry, and stop-loss.' },
      { href: '/tools/risk-reward', name: 'Risk/Reward Ratio Calculator', desc: 'Get the R:R ratio, percentage gain/loss, and breakeven win rate of any trade.' },
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
