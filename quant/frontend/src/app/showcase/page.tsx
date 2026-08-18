/**
 * Visualization showcase — in development.
 *
 * This page previously rendered a gallery of the site's chart components: a candlestick
 * chart labelled AAPL, a "Politician Trading Correlations" heatmap, a force-directed
 * network graph naming twelve sitting members of Congress, a trading-activity time
 * series, risk gauges and dashboard stat tiles ("12,847 trades", "23 anomalies detected",
 * "risk score 67"). It called no API at all — every price, volume, centrality score,
 * correlation and count came from Math.random at render time, and the hardcoded tiles
 * were invented outright.
 *
 * No synthetic fallback may be reintroduced here, including under a "demo data" label. A
 * gallery on this site has to be driven by data the site actually holds: a chart carrying
 * a real ticker or a real person's name is a claim about them, and a fabricated
 * correlation drawn between two named individuals is a claim neither of them earned. The
 * fact that the page exists to demonstrate a component does not change what a reader
 * takes away from it.
 *
 * The prior implementation is preserved in git history. Do not restore it.
 */

import Link from 'next/link'
import type { Metadata } from 'next'

export const metadata: Metadata = {
  title: 'Visualization Showcase — In Development | QuantEngines',
  description:
    'The chart component gallery is being rewired to the real data sources used elsewhere on the site. It is not available yet.',
  robots: { index: false, follow: true },
}

export default function ShowcasePage() {
  return (
    <div className="container mx-auto px-4 py-16 max-w-3xl">
      <p className="text-xs font-mono uppercase tracking-widest text-muted-foreground mb-3">
        In development
      </p>
      <h1 className="text-3xl md:text-4xl font-bold mb-5">
        The chart gallery is being rewired
      </h1>

      <div className="space-y-4 text-muted-foreground">
        <p>
          This page was a showcase of the charting components used across the site —
          candlesticks, a correlation heatmap, a network graph, time series, gauges and a
          draggable dashboard.
        </p>
        <p>
          Every number in it was generated at random when the page loaded. The candlestick
          chart was labelled AAPL but showed a price history that never happened, the
          dashboard tiles reported trade and anomaly counts nobody had counted, and the
          heatmap and network graph drew trading correlations between twelve named members
          of Congress that no analysis had produced. We took it down rather than leave it
          up.
        </p>
        <p>
          The components themselves are sound and are already in use on pages that have
          real data behind them. When the gallery returns it will read from those same
          sources, so that what it demonstrates is the chart rather than the number.
        </p>
        <p className="text-sm">
          We compute and display. We never recommend.
        </p>
      </div>

      <div className="flex flex-wrap gap-3 mt-10">
        <Link
          href="/congress-stock-trades"
          className="px-5 py-3 rounded-lg bg-blue-600 text-white hover:bg-blue-500 transition-colors"
        >
          Congressional trade filings (real data)
        </Link>
        <Link
          href="/backtesting"
          className="px-5 py-3 rounded-lg bg-slate-800 text-slate-300 hover:text-white hover:bg-slate-700 transition-colors"
        >
          Backtesting
        </Link>
      </div>
    </div>
  )
}
