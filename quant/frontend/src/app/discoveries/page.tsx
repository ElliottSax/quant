/**
 * Discoveries — in development.
 *
 * This page previously presented "Live Anomaly Detection": a stream of anomalies,
 * patterns, price targets and confidence scores generated entirely by Math.random
 * on a setInterval, with no detector behind any of it. It has been replaced by an
 * honest placeholder and excluded from search indexing until a real detector,
 * running on the licensed EOD store and publishing its own error bars, exists.
 *
 * The prior implementation is preserved in git history. Do not restore it.
 */

import Link from 'next/link'
import type { Metadata } from 'next'

export const metadata: Metadata = {
  title: 'Discoveries — In Development | QuantEngines',
  description:
    'The anomaly and pattern discovery tool is being rebuilt on licensed end-of-day data with published methodology. It is not available yet.',
  robots: { index: false, follow: true },
}

export default function DiscoveriesPage() {
  return (
    <main className="container mx-auto px-4 py-16 max-w-3xl">
      <p className="text-xs font-mono uppercase tracking-widest text-muted-foreground mb-3">
        In development
      </p>
      <h1 className="text-3xl md:text-4xl font-bold mb-5">
        Pattern discovery is being rebuilt
      </h1>

      <div className="space-y-4 text-muted-foreground">
        <p>
          This page used to display a live-looking feed of market anomalies and pattern
          detections. There was no detector behind it — the entries, their confidence
          scores and their price targets were generated at random in the browser. We
          removed it rather than leave it up.
        </p>
        <p>
          The replacement runs on licensed end-of-day data with a published methodology:
          every claim will arrive with its sample size, its corrected statistics, and the
          years it failed. If a pattern does not clear the bar, this page will say so
          rather than invent something more exciting.
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
    </main>
  )
}
