/**
 * Trading Signals — in development.
 *
 * This page previously presented "AI-powered trading signals": a buy / sell / hold call
 * per watchlist symbol, a confidence gauge, a risk score, a target price, a stop loss, a
 * technical-indicator radar and a written rationale. Every one of those values was
 * produced by Math.random in the browser.
 *
 * It reached for the real generator first, but that path cannot succeed from here:
 * POST /signals/generate is gated behind Depends(get_current_user), and this frontend
 * never sets a bearer token — setAuthToken() is exported and never called, and the login
 * form calls an api.login() that does not exist. So the request 401'd for every visitor
 * and a silent catch substituted invented numbers. Reloading produced a different
 * recommendation for the same symbol at the same instant.
 *
 * No synthetic fallback may be reintroduced here, and no "demo mode" that reads as live.
 * A trading call is the highest-stakes number this site can print; it may only appear as
 * the output of a real generator, on licensed data, carrying its own accuracy record. If
 * the generator cannot be reached, this page says so and shows nothing.
 *
 * The prior implementation is preserved in git history. Do not restore it.
 */

import Link from 'next/link'
import type { Metadata } from 'next'

export const metadata: Metadata = {
  title: 'Trading Signals — In Development | QuantEngines',
  description:
    'The trading signal engine is being rebuilt on licensed market data with a published methodology and track record. It is not available yet.',
  robots: { index: false, follow: true },
}

export default function SignalsPage() {
  return (
    <div className="container mx-auto px-4 py-16 max-w-3xl">
      <p className="text-xs font-mono uppercase tracking-widest text-muted-foreground mb-3">
        In development
      </p>
      <h1 className="text-3xl md:text-4xl font-bold mb-5">
        Trading signals are being rebuilt
      </h1>

      <div className="space-y-4 text-muted-foreground">
        <p>
          This page used to show a live-looking signal for each stock on a watchlist — a
          buy, sell or hold call with a confidence percentage, a risk score, a target
          price, a stop loss and a paragraph of reasoning underneath.
        </p>
        <p>
          None of it was computed. The signal engine sits behind an endpoint this site has
          never been able to call, and the page quietly filled the gap with numbers
          generated at random in your browser. The same stock, refreshed a second later,
          would produce a different call at a different price. We took it down rather than
          leave it up.
        </p>
        <p>
          What replaces it will show the indicator values themselves and the formula behind
          each one, computed on licensed data, alongside a record of how the engine has
          performed — including the stretches where it was wrong. Where it has nothing to
          say about a symbol, the page will say that rather than fill the space.
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
          Backtest a strategy on real history
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
