/**
 * pandas_ta column-name reference.
 *
 * Search Console shows this site already ranking around position 10 for `BBM_20_2.0`
 * and `MACDS_12_26_9` — off an incidental code comment in an article about something
 * else. Those searchers hit a KeyError and want one thing: which column does this
 * indicator actually create.
 *
 * Every name below was captured by RUNNING pandas_ta against real OHLCV and recording
 * what it returned (`python -m pipeline.pandas_ta_columns`), not transcribed from
 * documentation — which is the only way to get this right, because the library
 * generates these names and they change between versions.
 */

import type { Metadata } from 'next'
import Link from 'next/link'

export const metadata: Metadata = {
  title: 'pandas_ta Column Names Reference (Measured)',
  description:
    'What columns pandas_ta actually creates — BBL/BBM/BBU, MACD/MACDh/MACDs, STOCHk/STOCHd and 40+ more, captured by running the library. Includes why BBM_20_2.0 raises KeyError on a fresh install.',
  alternates: { canonical: 'https://quantengines.com/pandas-ta-columns' },
}

interface Entry {
  indicator: string
  ok: boolean
  columns?: string[]
  n_columns?: number
  error?: string
}
interface Data {
  pandas_ta_version: string
  python: string
  measured_on: { symbol: string; bars: number; from: string; to: string }
  indicators: Entry[]
  legacy_note: {
    pypi_available_versions: string[]
    claim: string
    verified_how: string
    examples: Array<{ indicator: string; legacy_0_3: string; measured_0_4: string; why: string }>
  }
}

function load(): Data | null {
  try {
    // eslint-disable-next-line @typescript-eslint/no-var-requires
    const d = require('../../../public/data/pandas-ta-columns.json') as Data
    return d?.indicators?.length ? d : null
  } catch {
    return null
  }
}

export default function PandasTaColumnsPage() {
  const data = load()

  return (
    <div className="space-y-8">
      <div>
        <h1 className="text-4xl md:text-5xl font-bold mb-3 gradient-text">
          pandas_ta Column Names
        </h1>
        <p className="text-lg text-slate-400 max-w-3xl">
          Which columns each indicator actually appends to your DataFrame. Captured by
          running the library against real price data, not copied from documentation.
        </p>
      </div>

      {!data ? (
        <div className="glass-card p-8">
          <h2 className="text-2xl font-bold mb-2">Reference data is not available</h2>
          <p className="text-slate-400">
            The measured artefact has not been published. This page will not guess column
            names in its absence — guessing is the problem it exists to solve.
          </p>
        </div>
      ) : (
        <>
          <div className="glass-card p-6 border border-amber-500/30">
            <h2 className="text-xl font-bold mb-2">
              Why <code className="inline-code">BBM_20_2.0</code> raises a KeyError today
            </h2>
            <p className="text-slate-300 mb-3">{data.legacy_note.claim}</p>
            <div className="overflow-x-auto">
              <table className="w-full text-sm">
                <thead>
                  <tr className="text-left text-xs uppercase tracking-wide text-slate-400 border-b border-slate-700">
                    <th className="p-2">Indicator</th>
                    <th className="p-2">Name in 0.3.x tutorials</th>
                    <th className="p-2">Measured in {data.pandas_ta_version}</th>
                  </tr>
                </thead>
                <tbody>
                  {data.legacy_note.examples.map(e => (
                    <tr key={e.indicator} className="border-b border-slate-800/60">
                      <td className="p-2 font-mono">{e.indicator}</td>
                      <td className="p-2 font-mono text-amber-400">{e.legacy_0_3}</td>
                      <td className="p-2 font-mono text-emerald-400">{e.measured_0_4}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
            <p className="text-sm text-slate-400 mt-3">
              {data.legacy_note.examples[0]?.why}. The 0.3.x names are recorded here as they
              appear in tutorials — they could not be re-measured, because that release is no
              longer installable ({data.legacy_note.verified_how}). Only the{' '}
              {data.pandas_ta_version} column is measured.
            </p>
          </div>

          <div className="glass-card p-6">
            <h2 className="text-xl font-bold mb-1">
              Every column, measured on {data.pandas_ta_version}
            </h2>
            <p className="text-sm text-slate-400 mb-4">
              Defaults only — change a parameter and the suffix changes with it. Run{' '}
              <code className="inline-code">df.ta.bbands(length=20)</code> and the column becomes{' '}
              <code className="inline-code">BBM_20_...</code>; the suffix is the parameters.
            </p>
            <div className="overflow-x-auto">
              <table className="w-full text-sm">
                <thead>
                  <tr className="text-left text-xs uppercase tracking-wide text-slate-400 border-b border-slate-700">
                    <th className="p-3">Call</th>
                    <th className="p-3 text-right">Cols</th>
                    <th className="p-3">Columns created</th>
                  </tr>
                </thead>
                <tbody>
                  {data.indicators.map(e => (
                    <tr key={e.indicator} className="border-b border-slate-800/60">
                      <td className="p-3 font-mono whitespace-nowrap">df.ta.{e.indicator}()</td>
                      <td className="p-3 text-right font-mono tabular-nums">
                        {e.ok ? e.n_columns : '—'}
                      </td>
                      <td className="p-3 font-mono text-xs">
                        {e.ok
                          ? (e.columns ?? []).join(', ')
                          : <span className="text-amber-400">{e.error}</span>}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>

          <div className="glass-card p-6 text-sm text-slate-400 max-w-4xl space-y-3">
            <h2 className="text-lg font-bold text-white">How to read a suffix</h2>
            <p>
              pandas_ta names each output <code className="inline-code">NAME_param1_param2...</code>
              using the parameters the call actually ran with — which is why the name changes when
              you change a default, and why hardcoding a column string breaks silently on upgrade.
              The robust pattern is to take the returned frame&apos;s columns rather than typing the
              name: <code className="inline-code">bb = df.ta.bbands(); mid = bb.iloc[:, 1]</code>,
              or <code className="inline-code">bb.filter(like=&apos;BBM&apos;)</code>.
            </p>
            <p className="text-xs pt-2 border-t border-slate-800">
              Measured on {data.measured_on.bars} real {data.measured_on.symbol} bars
              ({data.measured_on.from} to {data.measured_on.to}), pandas_ta{' '}
              {data.pandas_ta_version}, Python {data.python}. Regenerate with{' '}
              <code className="inline-code">python -m pipeline.pandas_ta_columns</code>.
            </p>
          </div>

          <div className="glass-card p-6">
            <h2 className="text-lg font-bold text-white mb-3">Related</h2>
            <div className="flex flex-wrap gap-3">
              <Link href="/scanner" className="px-5 py-3 rounded-lg bg-blue-600 text-white hover:bg-blue-500 transition-colors">
                Seasonality screener
              </Link>
              <Link href="/data-vendors" className="px-5 py-3 rounded-lg bg-slate-800 text-slate-300 hover:text-white hover:bg-slate-700 transition-colors">
                Market data API benchmark
              </Link>
              <Link href="/blog/arima-models" className="px-5 py-3 rounded-lg bg-slate-800 text-slate-300 hover:text-white hover:bg-slate-700 transition-colors">
                statsmodels ARIMA import
              </Link>
            </div>
          </div>
        </>
      )}
    </div>
  )
}
