/**
 * Quant Scanner — seasonality screener.
 *
 * This page previously served 951 lines of hardcoded "signals": pattern names with
 * confidence scores, price targets and stop losses for real tickers, none of which was
 * computed from anything. It was the site's highest-ranked page, which is exactly why
 * it was rebuilt in place rather than taken down — the URL and the screener intent are
 * unchanged, the data behind it is now real.
 *
 * Source: public/data/seasonality.json, written by the compute plane
 * (`python -m pipeline.export_verdicts`) only when the nightly ingest was clean and every
 * tier matches the permanent calibration record. No fallback exists: if the file is
 * missing or malformed the page says so rather than showing anything.
 *
 * Nothing here is a forecast or a recommendation. It reports what 36 years of adjusted
 * end-of-day prices contain, corrected for the number of tests run.
 */

import type { Metadata } from 'next'
import Link from 'next/link'
import { ScannerClient, type Dataset } from './ScannerClient'

export const metadata: Metadata = {
  title: 'Quant Scanner — Seasonality Screener | QuantEngines',
  description:
    'Screen monthly seasonal patterns across a fixed universe: sample sizes, effect sizes with confidence intervals, and multiple-testing-corrected verdicts — including the ones that fail.',
}

function loadDataset(): Dataset | null {
  try {
    // Static artefact, read at build/render time. A parse failure must surface as an
    // honest empty state, never as an invented default.
    // eslint-disable-next-line @typescript-eslint/no-var-requires
    const data = require('../../../public/data/seasonality.json') as Dataset
    if (!data?.cells?.length) return null
    return data
  } catch {
    return null
  }
}

export default function ScannerPage() {
  const data = loadDataset()

  return (
    <div className="space-y-8">
      <div className="animate-fade-in">
        <h1 className="text-4xl md:text-5xl font-bold mb-3 gradient-text">Quant Scanner</h1>
        <p className="text-lg text-slate-400 max-w-3xl">
          Screen monthly seasonal patterns across a fixed universe. Every cell reports its
          sample size, its effect size with a confidence interval, and a verdict corrected
          for the number of tests run — including the patterns that fail.
        </p>
      </div>

      {!data ? (
        <div className="glass-card p-8">
          <h2 className="text-2xl font-bold mb-2">Screener data is not available</h2>
          <p className="text-slate-400 max-w-2xl">
            The seasonality dataset has not been published yet. This page will not display
            placeholder results in its absence — it previously did, and everything it showed
            was invented.
          </p>
          <div className="mt-6 flex flex-wrap gap-3">
            <Link href="/congress-stock-trades" className="px-5 py-3 rounded-lg bg-blue-600 text-white hover:bg-blue-500 transition-colors">
              Congressional trade filings
            </Link>
            <Link href="/backtesting" className="px-5 py-3 rounded-lg bg-slate-800 text-slate-300 hover:text-white hover:bg-slate-700 transition-colors">
              Backtesting
            </Link>
          </div>
        </div>
      ) : (
        <>
          <ScannerClient data={data} />

          <div className="glass-card p-6 space-y-3 text-sm text-slate-400 max-w-4xl">
            <h2 className="text-lg font-bold text-white">How to read this</h2>
            <p>
              <strong className="text-slate-200">Read the q column, not the p column.</strong>{' '}
              A p-value below 0.05 looks convincing on its own, but {data.family_size} tests
              were run together here. The q-value corrects for that. At a false-discovery
              threshold of {(data.fdr_q * 100).toFixed(0)}%, roughly one in ten entries that
              cleared it would still be expected to be a false positive — which is why we
              state the threshold rather than just the winners. See our{' '}
              <Link href="/blog/overfitting-trading-strategies" className="underline hover:text-slate-200">
                guide to multiple-testing correction and the deflated Sharpe ratio
              </Link>{' '}
              for the statistics behind why this matters.
            </p>
            <p>
              <strong className="text-slate-200">Years against</strong> counts the years in
              which that month moved opposite to the overall effect. A pattern with a decent
              average and a third of its years against it is a weaker claim than the average
              alone suggests, so both are shown.
            </p>
            <p>
              A cell needs {data.thresholds.gradeable_n} observations to be graded at all and{' '}
              {data.thresholds.robust_n} to be eligible for <strong>Robust</strong>. Cells
              below the first threshold are reported, never quietly dropped.
            </p>
            <p className="text-xs pt-2 border-t border-slate-800">
              Universe: {data.universe.length} symbols ({data.universe.join(', ')}). Data:{' '}
              {data.provider} adjusted end-of-day, {data.data_start} to {data.data_vintage}.
              Methodology version {data.spec_version}, generated {data.generated_at}. Survivorship
              is not corrected for in this universe; that limitation applies to every figure above.
            </p>
            <p className="text-xs">
              We compute and display. We never recommend. Nothing here is a forecast, and no
              verdict is advice to buy or sell anything — see the{' '}
              <Link href="/disclaimer" className="underline hover:text-slate-200">disclaimer</Link>.
            </p>
          </div>
        </>
      )}
    </div>
  )
}
