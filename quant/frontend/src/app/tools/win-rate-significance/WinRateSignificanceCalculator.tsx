'use client'

import { useMemo, useState } from 'react'
import {
  computeWinRateSignificance,
  validateWinRate,
  type WinRateInputs,
  type WinRateResult,
} from './winRateSignificance'

// Wilson score interval + exact binomial test over user-entered win/loss
// counts only. No trade history is read; everything computes client-side.

function pct(n: number, dp = 1): string {
  if (!Number.isFinite(n)) return '—'
  return `${(n * 100).toFixed(dp)}%`
}

function parseIntInput(v: string): number {
  if (v.trim() === '') return NaN
  const n = Number(v)
  return Number.isFinite(n) ? n : NaN
}

const CONFIDENCE_OPTIONS: WinRateInputs['confidence'][] = [0.9, 0.95, 0.99]

export default function WinRateSignificanceCalculator() {
  const [wins, setWins] = useState('58')
  const [trades, setTrades] = useState('100')
  const [nullRatePct, setNullRatePct] = useState('50')
  const [confidence, setConfidence] = useState<WinRateInputs['confidence']>(0.95)

  const { error, result } = useMemo<{ error: string | null; result: WinRateResult | null }>(() => {
    const inputs: WinRateInputs = {
      wins: parseIntInput(wins),
      trades: parseIntInput(trades),
      nullRate: parseIntInput(nullRatePct) / 100,
      confidence,
    }
    const message = validateWinRate(inputs)
    if (message !== null) return { error: message, result: null }
    return { error: null, result: computeWinRateSignificance(inputs) }
  }, [wins, trades, nullRatePct, confidence])

  return (
    <div className="grid gap-6 lg:grid-cols-2">
      {/* Inputs */}
      <div className="rounded-xl border border-[hsl(215,40%,18%)] bg-[hsl(220,55%,9%)] p-6">
        <h2 className="text-lg font-semibold text-white mb-5">Trade record</h2>
        <div className="space-y-4">
          <div>
            <label htmlFor="wr-wins" className="text-xs font-semibold text-[hsl(215,20%,60%)] mb-2 block uppercase tracking-wide">
              Winning trades
            </label>
            <input id="wr-wins" type="number" inputMode="numeric" step={1} min={0} value={wins}
              onChange={(e) => setWins(e.target.value)} className="input-field" />
          </div>
          <div>
            <label htmlFor="wr-trades" className="text-xs font-semibold text-[hsl(215,20%,60%)] mb-2 block uppercase tracking-wide">
              Total trades
            </label>
            <input id="wr-trades" type="number" inputMode="numeric" step={1} min={1} value={trades}
              onChange={(e) => setTrades(e.target.value)} className="input-field" />
          </div>
          <div>
            <label htmlFor="wr-null" className="text-xs font-semibold text-[hsl(215,20%,60%)] mb-2 block uppercase tracking-wide">
              Baseline to test against
            </label>
            <div className="relative">
              <input id="wr-null" type="number" inputMode="decimal" step={1} min={0} max={100} value={nullRatePct}
                onChange={(e) => setNullRatePct(e.target.value)} className="input-field pr-8" />
              <span className="absolute right-3 top-1/2 -translate-y-1/2 text-[hsl(215,20%,50%)] text-sm">%</span>
            </div>
            <p className="mt-1 text-xs text-[hsl(215,20%,45%)]">
              50% for "is this better than a coin flip?" Use your breakeven win rate (from the risk/reward calculator) to test "is this beating what I need to be profitable?"
            </p>
          </div>
          <div>
            <label className="text-xs font-semibold text-[hsl(215,20%,60%)] mb-2 block uppercase tracking-wide">Confidence level</label>
            <div className="flex gap-2">
              {CONFIDENCE_OPTIONS.map((c) => (
                <button key={c} type="button" onClick={() => setConfidence(c)}
                  className={`rounded-md px-3 py-1.5 text-sm font-medium border transition-colors ${
                    confidence === c ? 'border-indigo-500 bg-indigo-500/15 text-indigo-300' : 'border-[hsl(215,40%,18%)] text-[hsl(215,20%,60%)] hover:border-indigo-500/50'
                  }`}>
                  {c * 100}%
                </button>
              ))}
            </div>
          </div>
        </div>

        <div className="mt-6 border-t border-[hsl(215,40%,14%)] pt-5">
          <h3 className="text-xs font-semibold text-[hsl(215,20%,60%)] uppercase tracking-wide mb-2">Method</h3>
          <div className="font-mono text-xs text-slate-300 space-y-1">
            <p>Wilson score interval (Wilson 1927)</p>
            <p>Exact two-sided binomial test</p>
          </div>
        </div>
      </div>

      {/* Results */}
      <div className="rounded-xl border border-[hsl(215,40%,18%)] bg-[hsl(220,55%,9%)] p-6">
        <h2 className="text-lg font-semibold text-white mb-5">Significance</h2>

        {error !== null || result === null ? (
          <div className="rounded-lg border border-amber-500/40 bg-amber-500/10 p-5">
            <p className="text-sm font-semibold text-amber-300">Check your inputs</p>
            <p className="mt-1 text-sm text-amber-200/80">{error ?? 'Enter valid numbers for every field.'}</p>
          </div>
        ) : (
          <>
            <div className={`rounded-lg border p-5 mb-5 ${result.significant ? 'border-emerald-500/30 bg-emerald-500/10' : 'border-amber-500/30 bg-amber-500/10'}`}>
              <div className={`text-xs font-semibold uppercase tracking-wide mb-1 ${result.significant ? 'text-emerald-300' : 'text-amber-300'}`}>
                {result.significant
                  ? `Distinguishable from ${nullRatePct}% at ${confidence * 100}% confidence`
                  : `Not distinguishable from ${nullRatePct}% at ${confidence * 100}% confidence`}
              </div>
              <div className="text-4xl font-bold text-white font-mono">{pct(result.observedRate)}</div>
              <p className="mt-2 text-xs text-slate-300/80">
                observed win rate over {trades} trades
              </p>
            </div>

            <dl className="space-y-3">
              <Stat label={`${confidence * 100}% confidence interval`} value={`${pct(result.wilsonLower)} – ${pct(result.wilsonUpper)}`} sub="Wilson score interval" />
              <Stat label="Exact two-sided p-value" value={result.pValue < 0.0001 ? '< 0.0001' : result.pValue.toFixed(4)} sub={`vs. ${nullRatePct}% baseline`} />
            </dl>

            <div className="mt-5 rounded-lg border border-[hsl(215,40%,14%)] bg-[hsl(220,55%,7%)] p-4">
              <div className="relative h-2 rounded-full bg-[hsl(215,40%,18%)]">
                <div
                  className="absolute h-2 rounded-full bg-indigo-500"
                  style={{
                    left: `${result.wilsonLower * 100}%`,
                    width: `${Math.max(0.5, (result.wilsonUpper - result.wilsonLower) * 100)}%`,
                  }}
                />
                <div
                  className="absolute top-1/2 h-3 w-0.5 -translate-y-1/2 bg-white"
                  style={{ left: `${result.observedRate * 100}%` }}
                  title="Observed win rate"
                />
                <div
                  className={`absolute top-1/2 h-3 w-0.5 -translate-y-1/2 ${result.significant ? 'bg-red-400' : 'bg-emerald-400'}`}
                  style={{ left: `${Math.min(100, Math.max(0, Number(nullRatePct)))}%` }}
                  title="Baseline"
                />
              </div>
              <div className="mt-2 flex justify-between text-[10px] text-[hsl(215,20%,45%)] font-mono">
                <span>0%</span>
                <span>50%</span>
                <span>100%</span>
              </div>
              <p className="mt-2 text-xs text-[hsl(215,20%,50%)]">
                Blue band = confidence interval · white line = your observed rate · {result.significant ? 'red' : 'green'} line = baseline
              </p>
            </div>

            <p className="mt-5 text-xs text-[hsl(215,20%,45%)] leading-relaxed">
              A "not distinguishable" result does not mean your win rate is 50% — it means this
              sample size can't rule out chance producing a result at least this extreme. More
              trades narrow the interval; the interval width shrinks roughly with the square root
              of the sample size, not linearly.
            </p>
          </>
        )}
      </div>
    </div>
  )
}

function Stat({ label, value, sub }: { label: string; value: string; sub?: string }) {
  return (
    <div className="flex items-start justify-between gap-4 border-b border-[hsl(215,40%,14%)] pb-3">
      <dt className="text-sm text-[hsl(215,20%,60%)]">{label}</dt>
      <dd className="text-right">
        <div className="text-base font-semibold text-white font-mono">{value}</div>
        {sub && <div className="text-xs text-[hsl(215,20%,45%)] font-mono">{sub}</div>}
      </dd>
    </div>
  )
}
