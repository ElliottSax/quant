/**
 * Market-data vendor bench.
 *
 * Reads public/data/vendor-bench.json, produced by `python -m pipeline.bench`, which
 * probes each vendor through the same adapter interface the production pipeline uses.
 * Every figure on this page is what a request actually returned. Nothing is copied
 * from a vendor's documentation, and nothing is scored into a ranking — the numbers
 * are reported and the reader draws the conclusion.
 *
 * No fallback: if the artefact is missing the page says so rather than showing
 * anything. That rule is the whole point of the page.
 */

import type { Metadata } from 'next'
import Link from 'next/link'

export const metadata: Metadata = {
  title: 'Market Data API Benchmark — Measured, Not Quoted | QuantEngines',
  description:
    'We requested the same data from each market-data provider and recorded what came back: real history depth, coverage gaps by asset class, split-adjustment correctness, and freshness. Reproducible, timestamped, no marketing copy.',
  alternates: { canonical: 'https://quantengines.com/data-vendors' },
}

interface CoverageRow { symbol: string; class: string; ok: boolean; rows?: number; reason?: string; error?: string }
interface Result {
  provider: string
  available: boolean
  error?: string
  probes: {
    history?: { ok: boolean; rows?: number; earliest_returned?: string; latest_returned?: string; span_years?: number; requested_from?: string; error?: string }
    coverage?: CoverageRow[]
    coverage_summary?: { ok: number; total: number; entitlement_blocked: number }
    adjustment?: { ok: boolean; worst_daily_move_pct?: number | null; adjusted?: boolean; corporate_action?: string; error?: string }
    freshness?: { latest_bar: string; days_behind_today: number }
  }
}
interface Bench {
  generated_at: string
  method: string
  probes: { history: { symbol: string; requested_from: string }; adjustment: { symbol: string; corporate_action: string } }
  results: Result[]
}

function load(): Bench | null {
  try {
    // eslint-disable-next-line @typescript-eslint/no-var-requires
    const d = require('../../../public/data/vendor-bench.json') as Bench
    return d?.results?.length ? d : null
  } catch {
    return null
  }
}

const NAMES: Record<string, string> = {
  fmp: 'Financial Modeling Prep',
  yfinance: 'Yahoo Finance (yfinance)',
}

export default function DataVendorsPage() {
  const bench = load()

  return (
    <div className="space-y-8">
      <div>
        <h1 className="text-4xl md:text-5xl font-bold mb-3 gradient-text">Market Data API Benchmark</h1>
        <p className="text-lg text-slate-400 max-w-3xl">
          We asked each provider for the same data and recorded what came back. Every number
          below is a measurement, not a figure from a pricing page — including the ones that
          are unflattering to a provider we pay for.
        </p>
      </div>

      {!bench ? (
        <div className="glass-card p-8">
          <h2 className="text-2xl font-bold mb-2">Benchmark data is not available</h2>
          <p className="text-slate-400 max-w-2xl">
            The bench artefact has not been published. This page will not show placeholder
            comparisons in its absence.
          </p>
        </div>
      ) : (
        <>
          <div className="glass-card p-6">
            <h2 className="text-xl font-bold mb-4">Results</h2>
            <div className="overflow-x-auto">
              <table className="w-full text-sm">
                <thead>
                  <tr className="text-left text-xs uppercase tracking-wide text-slate-400 border-b border-slate-700">
                    <th className="p-3">Provider</th>
                    <th className="p-3">History returned</th>
                    <th className="p-3 text-right">Rows</th>
                    <th className="p-3 text-right">Coverage</th>
                    <th className="p-3">Split-adjusted</th>
                    <th className="p-3 text-right">Days behind</th>
                  </tr>
                </thead>
                <tbody>
                  {bench.results.map(r => {
                    const h = r.probes.history
                    const c = r.probes.coverage_summary
                    const a = r.probes.adjustment
                    const f = r.probes.freshness
                    return (
                      <tr key={r.provider} className="border-b border-slate-800/60">
                        <td className="p-3 font-semibold">{NAMES[r.provider] ?? r.provider}</td>
                        <td className="p-3 font-mono text-xs">
                          {h?.ok ? `${h.earliest_returned} → ${h.latest_returned} (${h.span_years}y)` : `failed: ${h?.error ?? 'n/a'}`}
                        </td>
                        <td className="p-3 text-right font-mono tabular-nums">{h?.ok ? h.rows : '—'}</td>
                        <td className="p-3 text-right font-mono tabular-nums">
                          {c ? `${c.ok}/${c.total}` : '—'}
                          {c && c.entitlement_blocked > 0 && (
                            <span className="ml-2 text-[10px] text-amber-400 border border-amber-400/40 rounded px-1">
                              {c.entitlement_blocked} blocked
                            </span>
                          )}
                        </td>
                        <td className="p-3">
                          {a?.ok
                            ? (a.adjusted
                                ? <span className="text-emerald-400">yes ({a.worst_daily_move_pct}% worst move)</span>
                                : <span className="text-red-400">no ({a.worst_daily_move_pct}%)</span>)
                            : '—'}
                        </td>
                        <td className="p-3 text-right font-mono tabular-nums">
                          {f ? f.days_behind_today : '—'}
                        </td>
                      </tr>
                    )
                  })}
                </tbody>
              </table>
            </div>
          </div>

          <div className="glass-card p-6">
            <h2 className="text-xl font-bold mb-2">Coverage, symbol by symbol</h2>
            <p className="text-sm text-slate-400 mb-4">
              Entitlement gaps do not announce themselves. A plan can serve equities happily
              and refuse every ETF — which is invisible until the request that needs one fails.
            </p>
            <div className="overflow-x-auto">
              <table className="w-full text-sm">
                <thead>
                  <tr className="text-left text-xs uppercase tracking-wide text-slate-400 border-b border-slate-700">
                    <th className="p-3">Symbol</th>
                    <th className="p-3">Asset class</th>
                    {bench.results.map(r => (
                      <th key={r.provider} className="p-3">{NAMES[r.provider] ?? r.provider}</th>
                    ))}
                  </tr>
                </thead>
                <tbody>
                  {(bench.results[0]?.probes.coverage ?? []).map((row, i) => (
                    <tr key={row.symbol} className="border-b border-slate-800/60">
                      <td className="p-3 font-mono font-semibold">{row.symbol}</td>
                      <td className="p-3 text-slate-400">{row.class}</td>
                      {bench.results.map(r => {
                        const cell = r.probes.coverage?.[i]
                        return (
                          <td key={r.provider} className="p-3">
                            {cell?.ok
                              ? <span className="text-emerald-400">served</span>
                              : <span className="text-amber-400">
                                  {cell?.reason === 'entitlement' ? 'plan does not cover' : 'no data'}
                                </span>}
                          </td>
                        )
                      })}
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>

          <div className="glass-card p-6 space-y-3 text-sm text-slate-400 max-w-4xl">
            <h2 className="text-lg font-bold text-white">Method</h2>
            <p>{bench.method}</p>
            <p>
              <strong className="text-slate-200">History</strong> requests {bench.probes.history.symbol} from{' '}
              {bench.probes.history.requested_from} and records the earliest bar that actually
              arrives. This distinction matters more than it sounds: one provider here returns
              about twenty years to an open-ended request and thirty-three to date-windowed
              ones, because its row cap applies per request rather than per symbol. Catalogue
              depth and delivered depth are not the same number.
            </p>
            <p>
              <strong className="text-slate-200">Split-adjustment</strong> is checked against a
              known corporate action — {bench.probes.adjustment.corporate_action}. An
              unadjusted series turns that month into roughly a −75% move, which would be
              published as a seasonal effect by anything computing monthly returns downstream.
            </p>
            <p>
              <strong className="text-slate-200">No ranking.</strong> There is no score and no
              winner, because the right provider depends on which of these dimensions binds for
              you. A free source with full coverage may still be unusable if you need terms of
              service you can rely on.
            </p>
            <p className="text-xs pt-2 border-t border-slate-800">
              Generated {bench.generated_at} · re-measured on the same nightly schedule as the
              rest of the site · reproducible with <code className="text-slate-300">python -m pipeline.bench</code>
            </p>
          </div>

          <div className="glass-card p-6 text-sm text-slate-400 max-w-4xl">
            <h2 className="text-lg font-bold text-white mb-2">Disclosure</h2>
            <p>
              QuantEngines uses Financial Modeling Prep for its own published statistics, and
              the entitlement gaps shown above are on the tier we actually pay for. Where this
              page carries an affiliate link in future it will be marked as one, and it will
              not change a measurement — see the{' '}
              <Link href="/affiliate-disclosure" className="text-blue-400 hover:text-blue-300 underline">
                affiliate disclosure
              </Link>. Yahoo Finance is included because it is measurable and widely used, not
              as a recommendation: it is an unofficial endpoint with no terms of service for
              programmatic use and no availability guarantee.
            </p>
          </div>
        </>
      )}
    </div>
  )
}
