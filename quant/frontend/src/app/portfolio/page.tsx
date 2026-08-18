/**
 * Portfolio Analyzer — in development.
 *
 * This page previously presented a full portfolio analysis suite: headline
 * performance figures, an asset allocation, a sector exposure comparison, a
 * correlation matrix, an efficient frontier, a Monte Carlo projection and
 * VaR/CVaR/beta series. None of it described a portfolio. There was no holdings
 * store, no quote feed and no optimiser behind the page — every number was either
 * hardcoded or drawn from a random-number generator in the browser on each render.
 *
 * It has been replaced by an honest placeholder and excluded from search indexing
 * until real holdings can be priced against real quotes. No synthetic fallback may
 * be reintroduced here: a portfolio page that invents its own valuations is worse
 * than no portfolio page, because its numbers are indistinguishable from measured
 * ones and a reader has no way to tell.
 *
 * The prior implementation is preserved in git history. Do not restore it.
 */

import Link from 'next/link'
import type { Metadata } from 'next'

export const metadata: Metadata = {
  title: 'Portfolio Analyzer — In Development | QuantEngines',
  description:
    'The portfolio analyzer is being rebuilt on user-entered holdings priced against real market quotes. It is not available yet.',
  robots: { index: false, follow: true },
}

export default function PortfolioPage() {
  return (
    <main className="container mx-auto px-4 py-16 max-w-3xl">
      <p className="text-xs font-mono uppercase tracking-widest text-muted-foreground mb-3">
        In development
      </p>
      <h1 className="text-3xl md:text-4xl font-bold mb-5">
        Portfolio analysis is being rebuilt
      </h1>

      <div className="space-y-4 text-muted-foreground">
        <p>
          This page used to show a complete portfolio analysis: a total return, a
          Sharpe ratio, a maximum drawdown, an asset allocation, a correlation
          matrix, an efficient frontier, a Monte Carlo projection and rolling
          value-at-risk. None of it was measured. There were no holdings behind the
          page and no price feed attached to it — the figures were hardcoded, and the
          charts were redrawn from random numbers every time the page loaded. We
          removed the whole thing rather than leave it up.
        </p>
        <p>
          The replacement starts from holdings you enter yourself. Those are your
          data, and they stay yours. Everything derived from them — position values,
          returns, exposure, risk — has to come from real quotes, so when we cannot
          price a holding the page will say it cannot price that holding rather than
          fill the gap with a plausible number.
        </p>
        <p>
          Optimisation output follows the same rule. An efficient frontier is only
          worth drawing once it is estimated from real return histories and shipped
          with the estimation error that comes with it.
        </p>
        <p className="text-sm">
          We compute and display. We never recommend.
        </p>
      </div>

      <div className="flex flex-wrap gap-3 mt-10">
        <Link
          href="/backtesting"
          className="px-5 py-3 rounded-lg bg-blue-600 text-white hover:bg-blue-500 transition-colors"
        >
          Backtesting (real price history)
        </Link>
        <Link
          href="/congress-stock-trades"
          className="px-5 py-3 rounded-lg bg-slate-800 text-slate-300 hover:text-white hover:bg-slate-700 transition-colors"
        >
          Congressional trade filings
        </Link>
        <Link
          href="/charts"
          className="px-5 py-3 rounded-lg bg-slate-800 text-slate-300 hover:text-white hover:bg-slate-700 transition-colors"
        >
          Charts
        </Link>
      </div>
    </main>
  )
}
