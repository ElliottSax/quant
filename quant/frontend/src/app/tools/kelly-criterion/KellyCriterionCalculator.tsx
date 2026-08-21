'use client'

import { useMemo, useState } from 'react'
import {
  ComposedChart,
  Line,
  ReferenceLine,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
} from 'recharts'
import {
  computeKelly,
  validateKelly,
  type KellyInputs,
  type KellyResult,
} from './kellyCriterion'

// Closed-form Kelly-criterion arithmetic over user input only. No market data
// or trade history is read; win probability and win/loss ratio are numbers
// the trader supplies (or estimates from their own trade log elsewhere).
// Everything computes client-side.

function fmtUSD(n: number, dp = 2): string {
  if (!Number.isFinite(n)) return '—'
  return n.toLocaleString('en-US', {
    style: 'currency',
    currency: 'USD',
    minimumFractionDigits: dp,
    maximumFractionDigits: dp,
  })
}

function fmtPct(n: number, dp = 2): string {
  if (!Number.isFinite(n)) return '—'
  return `${n.toLocaleString('en-US', { minimumFractionDigits: dp, maximumFractionDigits: dp })}%`
}

function parseInput(v: string): number {
  if (v.trim() === '') return NaN
  const n = Number(v)
  return Number.isFinite(n) ? n : NaN
}

const PRESETS = [
  { label: 'Full Kelly', value: '100' },
  { label: 'Half Kelly', value: '50' },
  { label: 'Quarter Kelly', value: '25' },
]

export default function KellyCriterionCalculator() {
  const [winProbPct, setWinProbPct] = useState('55')
  const [winLossRatio, setWinLossRatio] = useState('1.5')
  const [account, setAccount] = useState('25000')
  const [kellyFractionPct, setKellyFractionPct] = useState('50')

  const { error, result } = useMemo<{ error: string | null; result: KellyResult | null }>(() => {
    const inputs: KellyInputs = {
      winProbPct: parseInput(winProbPct),
      winLossRatio: parseInput(winLossRatio),
      account: parseInput(account),
      kellyFractionPct: parseInput(kellyFractionPct),
    }
    const message = validateKelly(inputs)
    if (message !== null) return { error: message, result: null }
    return { error: null, result: computeKelly(inputs) }
  }, [winProbPct, winLossRatio, account, kellyFractionPct])

  return (
    <div className="grid gap-6 lg:grid-cols-2">
      {/* Inputs */}
      <div className="rounded-xl border border-[hsl(215,40%,18%)] bg-[hsl(220,55%,9%)] p-6">
        <h2 className="text-lg font-semibold text-white mb-5">Trade statistics</h2>
        <div className="space-y-4">
          <div>
            <label htmlFor="kc-winprob" className="text-xs font-semibold text-[hsl(215,20%,60%)] mb-2 block uppercase tracking-wide">
              Win probability
            </label>
            <div className="relative">
              <input
                id="kc-winprob"
                type="number"
                inputMode="decimal"
                step={1}
                min={0}
                max={100}
                value={winProbPct}
                onChange={(e) => setWinProbPct(e.target.value)}
                className="input-field pr-8"
              />
              <span className="absolute right-3 top-1/2 -translate-y-1/2 text-[hsl(215,20%,50%)] text-sm">%</span>
            </div>
            <p className="mt-1 text-xs text-[hsl(215,20%,45%)]">Share of trades that win, from your own trade log — not a guess.</p>
          </div>

          <div>
            <label htmlFor="kc-ratio" className="text-xs font-semibold text-[hsl(215,20%,60%)] mb-2 block uppercase tracking-wide">
              Win/loss ratio
            </label>
            <input
              id="kc-ratio"
              type="number"
              inputMode="decimal"
              step={0.05}
              min={0}
              value={winLossRatio}
              onChange={(e) => setWinLossRatio(e.target.value)}
              className="input-field"
            />
            <p className="mt-1 text-xs text-[hsl(215,20%,45%)]">Average win size ÷ average loss size. 1.5 means wins are 1.5× the size of losses.</p>
          </div>

          <div>
            <label htmlFor="kc-account" className="text-xs font-semibold text-[hsl(215,20%,60%)] mb-2 block uppercase tracking-wide">
              Account size
            </label>
            <div className="relative">
              <span className="absolute left-3 top-1/2 -translate-y-1/2 text-[hsl(215,20%,50%)] text-sm">$</span>
              <input
                id="kc-account"
                type="number"
                inputMode="decimal"
                step={100}
                min={0}
                value={account}
                onChange={(e) => setAccount(e.target.value)}
                className="input-field pl-7"
              />
            </div>
          </div>

          <div>
            <label htmlFor="kc-fraction" className="text-xs font-semibold text-[hsl(215,20%,60%)] mb-2 block uppercase tracking-wide">
              Fraction of full Kelly to stake
            </label>
            <div className="relative">
              <input
                id="kc-fraction"
                type="number"
                inputMode="decimal"
                step={5}
                min={0}
                value={kellyFractionPct}
                onChange={(e) => setKellyFractionPct(e.target.value)}
                className="input-field pr-8"
              />
              <span className="absolute right-3 top-1/2 -translate-y-1/2 text-[hsl(215,20%,50%)] text-sm">%</span>
            </div>
            <div className="mt-2 flex gap-2">
              {PRESETS.map((p) => (
                <button
                  key={p.label}
                  type="button"
                  onClick={() => setKellyFractionPct(p.value)}
                  className={`rounded-md px-2.5 py-1 text-xs font-medium border transition-colors ${
                    kellyFractionPct === p.value
                      ? 'border-indigo-500 bg-indigo-500/15 text-indigo-300'
                      : 'border-[hsl(215,40%,18%)] text-[hsl(215,20%,60%)] hover:border-indigo-500/50'
                  }`}
                >
                  {p.label}
                </button>
              ))}
            </div>
            <p className="mt-1 text-xs text-[hsl(215,20%,45%)]">Most traders who use Kelly stake a fraction of full Kelly to reduce variance — see the chart below for why.</p>
          </div>
        </div>

        <div className="mt-6 border-t border-[hsl(215,40%,14%)] pt-5">
          <h3 className="text-xs font-semibold text-[hsl(215,20%,60%)] uppercase tracking-wide mb-2">Formula</h3>
          <div className="font-mono text-xs text-slate-300 space-y-1">
            <p>f* = W − (1 − W) ÷ R</p>
            <p>staked = f* × fraction</p>
            <p>growth(f) = W·ln(1 + f·R) + (1 − W)·ln(1 − f)</p>
          </div>
        </div>
      </div>

      {/* Results */}
      <div className="rounded-xl border border-[hsl(215,40%,18%)] bg-[hsl(220,55%,9%)] p-6">
        <h2 className="text-lg font-semibold text-white mb-5">Kelly allocation</h2>

        {error !== null || result === null ? (
          <div className="rounded-lg border border-amber-500/40 bg-amber-500/10 p-5">
            <p className="text-sm font-semibold text-amber-300">Check your inputs</p>
            <p className="mt-1 text-sm text-amber-200/80">{error ?? 'Enter valid numbers for every field.'}</p>
          </div>
        ) : !result.hasEdge ? (
          <div className="rounded-lg border border-red-500/40 bg-red-500/10 p-5">
            <div className="text-xs font-semibold text-red-300 uppercase tracking-wide mb-1">
              Full Kelly is negative — {fmtPct(result.fullKellyPct)}
            </div>
            <p className="mt-2 text-sm text-red-200/80 leading-relaxed">
              At this win probability and win/loss ratio, the expected value per dollar staked is{' '}
              {fmtUSD(result.edgePerDollar)}. Kelly sizing only allocates capital when there is a
              positive edge — with these inputs it says to stake nothing. You would need at least a{' '}
              {fmtPct(result.breakEvenWinProbPct)} win rate at this win/loss ratio to break even.
            </p>
          </div>
        ) : (
          <>
            <div className="rounded-lg border border-indigo-500/30 bg-indigo-500/10 p-5 mb-5">
              <div className="text-xs font-semibold text-indigo-300 uppercase tracking-wide mb-1">
                Stake — {fmtPct(result.stakedPct)} of account
              </div>
              <div className="text-4xl font-bold text-white font-mono">{fmtUSD(result.dollarAllocation, 0)}</div>
              <p className="mt-2 text-xs text-indigo-200/70">
                Full Kelly is {fmtPct(result.fullKellyPct)}; you selected {kellyFractionPct}% of it.
              </p>
            </div>

            <dl className="space-y-3">
              <Stat label="Full Kelly fraction" value={fmtPct(result.fullKellyPct)} />
              <Stat label="Edge per dollar staked" value={fmtUSD(result.edgePerDollar)} sub="W×R − (1−W)" />
              <Stat label="Break-even win probability" value={fmtPct(result.breakEvenWinProbPct)} sub="at this win/loss ratio" />
              <Stat label="Expected growth rate per trade" value={fmtPct(result.expectedGrowthPct)} sub="expected log-growth at your staked fraction" />
            </dl>

            <div className="mt-6">
              <h3 className="text-xs font-semibold text-[hsl(215,20%,60%)] uppercase tracking-wide mb-2">
                Expected growth rate vs. stake size
              </h3>
              <ResponsiveContainer width="100%" height={220}>
                <ComposedChart data={result.growthCurve} margin={{ top: 8, right: 12, bottom: 20, left: 8 }}>
                  <CartesianGrid strokeDasharray="3 3" stroke="#334155" />
                  <XAxis
                    dataKey="ofFullKellyPct"
                    type="number"
                    domain={[0, 'dataMax']}
                    stroke="#94a3b8"
                    tick={{ fontSize: 11 }}
                    tickFormatter={(v: number) => `${Math.round(v)}%`}
                    label={{ value: '% of full Kelly staked', position: 'bottom', fill: '#94a3b8', fontSize: 11 }}
                  />
                  <YAxis stroke="#94a3b8" tick={{ fontSize: 11 }} width={55} tickFormatter={(v: number) => `${v.toFixed(1)}%`} />
                  <Tooltip
                    contentStyle={{ backgroundColor: '#1e293b', border: '1px solid #334155', borderRadius: '8px' }}
                    labelFormatter={(v: number) => `${Math.round(v)}% of full Kelly`}
                    formatter={(value: number) => [`${value.toFixed(3)}%`, 'Expected growth/trade']}
                  />
                  <ReferenceLine x={100} stroke="#818cf8" strokeDasharray="3 3" label={{ value: 'Full Kelly', fill: '#818cf8', fontSize: 10, position: 'top' }} />
                  <ReferenceLine x={parseInput(kellyFractionPct)} stroke="#34d399" strokeDasharray="3 3" label={{ value: 'You', fill: '#34d399', fontSize: 10, position: 'insideTopLeft' }} />
                  <Line type="monotone" dataKey="growthPct" stroke="#818cf8" strokeWidth={2} dot={false} name="growthPct" />
                </ComposedChart>
              </ResponsiveContainer>
              <p className="mt-2 text-xs text-[hsl(215,20%,45%)] leading-relaxed">
                Growth peaks exactly at 100% of full Kelly and falls off faster above it than below —
                staking twice full Kelly gives the same expected growth as a much smaller fraction,
                with far more variance along the way. That asymmetry is the standard argument for
                staking a fraction rather than full Kelly.
              </p>
            </div>
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
