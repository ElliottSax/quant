/**
 * Charts — daily OHLC and volume for the symbols that actually have published history.
 *
 * The page used to call a market-data API that has no historical-price endpoint, and,
 * when nothing came back, drew a random-walk OHLC series labelled "Demo data" in 11px
 * grey while the chart, the stats bar and the percentage change all read as measured
 * prices. It now reads public/data/prices.json — adjusted end-of-day bars written by the
 * compute plane — and shows nothing at all when that file is unavailable.
 *
 * Symbols not in the artefact are never offered, and no view is rendered that is not
 * computed from those bars.
 */

import type { Metadata } from 'next'
import { Suspense } from 'react'
import { ChartsClient } from './ChartsClient'

export const metadata: Metadata = {
  title: 'Charts — Daily OHLC & Volume | QuantEngines',
  description:
    'Candlestick and volume charts built from adjusted end-of-day bars, with moving averages and Bollinger bands computed from the same series. End-of-day, not live.',
}

function ChartsLoadingFallback() {
  return (
    <div className="space-y-6 animate-pulse">
      <div className="glass-card h-32" />
      <div className="terminal-panel h-[620px]" />
    </div>
  )
}

export default function ChartsPage() {
  return (
    <div className="space-y-8">
      <div className="animate-fade-in">
        <h1 className="text-4xl md:text-5xl font-bold mb-3 gradient-text">Charts</h1>
        <p className="text-lg text-slate-400 max-w-3xl">
          Daily open, high, low, close and volume for a fixed universe, drawn from adjusted
          end-of-day bars. Moving averages and Bollinger bands are computed from those same
          closes; no overlay is drawn from a window the history cannot fill. This is
          end-of-day data, not a live quote feed.
        </p>
      </div>

      <Suspense fallback={<ChartsLoadingFallback />}>
        <ChartsClient />
      </Suspense>
    </div>
  )
}
