/**
 * Compare Politicians — in development.
 *
 * This page presented a side-by-side "trading record" for two named members of
 * Congress: average return, win rate, Sharpe ratio, beta, volatility, maximum
 * drawdown, sector allocation, a twelve-month equity curve and a list of dated
 * trades with individual returns. Every one of those numbers came out of a
 * Math.sin(seed) generator in the browser, and they were attached to real people
 * by name — the same defect that removed /leaderboard.
 *
 * There is no data source behind a per-politician performance comparison. The
 * politicians API returns identity only (name, party, chamber, state, trade
 * count); it publishes no returns, no risk metrics and no per-trade P&L, so
 * nothing on this page could be computed rather than invented.
 *
 * A comparison may return only when returns are derived from the filed STOCK Act
 * transactions this site ingests, with the methodology stated on the page. Until
 * then this route stays out of the index. Do not restore the generator.
 */

import Link from 'next/link'
import type { Metadata } from 'next'

export const metadata: Metadata = {
  title: 'Compare Politicians — In Development | QuantEngines',
  description:
    'Side-by-side comparison of congressional trading records is being rebuilt on filed STOCK Act transactions with a stated return methodology. It is not available yet.',
  robots: { index: false, follow: true },
}

export default function ComparePage() {
  return (
    <div className="space-y-8">
      <div className="animate-fade-in">
        <p className="text-xs font-mono uppercase tracking-widest text-muted-foreground mb-3">
          In development
        </p>
        <h1 className="text-4xl md:text-5xl font-bold mb-3 bg-clip-text text-transparent bg-gradient-to-r from-foreground to-foreground/70">
          Compare Politicians
        </h1>
        <p className="text-lg text-muted-foreground">
          Head-to-head comparison of congressional trading records is being rebuilt.
        </p>
      </div>

      <div className="glass-strong rounded-xl p-6 md:p-8 border border-border/50 space-y-4 text-muted-foreground max-w-3xl">
        <p>
          This page used to put two named members of Congress side by side and report
          their average return, win rate, Sharpe ratio, drawdown, sector mix and recent
          trades. None of it was measured. The figures were generated in the browser and
          then attributed to real people, so we removed the page rather than leave it up.
        </p>
        <p>
          The replacement will compute returns from the STOCK Act transactions this site
          already ingests, with the methodology, the reporting lag and the sample size
          stated on the page. Where a filing gives only a value range, the comparison
          will say so instead of picking a number.
        </p>
        <p className="text-sm">
          We compute and display. We never recommend.
        </p>
      </div>

      <div className="flex flex-wrap gap-3">
        <Link
          href="/politicians"
          className="px-5 py-3 rounded-lg bg-blue-600 text-white hover:bg-blue-500 transition-colors"
        >
          Browse politicians
        </Link>
        <Link
          href="/congress-stock-trades"
          className="px-5 py-3 rounded-lg bg-slate-800 text-slate-300 hover:text-white hover:bg-slate-700 transition-colors"
        >
          Congressional trade filings (real data)
        </Link>
      </div>
    </div>
  )
}
