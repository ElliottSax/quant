'use client'

import { useMemo, useState } from 'react'
import {
  computeRiskReward,
  validateRiskReward,
  type RiskRewardInputs,
  type RiskRewardResult,
} from './riskReward'

// Closed-form risk/reward arithmetic over user input only. No market data is
// read and none is displayed. Every figure is reproducible by hand from the
// entry, stop, and target entered above it.

function fmtUSD(n: number, dp = 2): string {
  if (!Number.isFinite(n)) return '—'
  return n.toLocaleString('en-US', {
    style: 'currency',
    currency: 'USD',
    minimumFractionDigits: dp,
    maximumFractionDigits: dp,
  })
}

function fmtNum(n: number, dp = 2): string {
  if (!Number.isFinite(n)) return '—'
  return n.toLocaleString('en-US', { minimumFractionDigits: dp, maximumFractionDigits: dp })
}

/** Empty or non-numeric input yields NaN so validation rejects it explicitly. */
function parseInput(v: string): number {
  if (v.trim() === '') return NaN
  const n = Number(v)
  return Number.isFinite(n) ? n : NaN
}

type Field = {
  key: string
  label: string
  hint: string
  value: string
  set: (v: string) => void
  prefix?: string
  suffix?: string
  step: number
  optional?: boolean
}

export default function RiskRewardCalculator() {
  const [entry, setEntry] = useState('100')
  const [stop, setStop] = useState('95')
  const [target, setTarget] = useState('115')
  const [shares, setShares] = useState('')

  const { error, result } = useMemo<{ error: string | null; result: RiskRewardResult | null }>(() => {
    const inputs: RiskRewardInputs = {
      entry: parseInput(entry),
      stop: parseInput(stop),
      target: parseInput(target),
      shares: shares.trim() === '' ? null : parseInput(shares),
    }
    const message = validateRiskReward(inputs)
    if (message !== null) return { error: message, result: null }
    return { error: null, result: computeRiskReward(inputs) }
  }, [entry, stop, target, shares])

  const fields: Field[] = [
    { key: 'entry', label: 'Entry price', hint: 'Price per share at entry', value: entry, set: setEntry, prefix: '$', step: 0.01 },
    { key: 'stop', label: 'Stop-loss price', hint: 'Exit price. Below entry is a long, above entry is a short', value: stop, set: setStop, prefix: '$', step: 0.01 },
    { key: 'target', label: 'Target price', hint: 'Exit price on the winning side of the entry', value: target, set: setTarget, prefix: '$', step: 0.01 },
    { key: 'shares', label: 'Position size (optional)', hint: 'Share count, to convert the per-share figures into dollars', value: shares, set: setShares, suffix: 'sh', step: 1, optional: true },
  ]

  return (
    <div className="grid gap-6 lg:grid-cols-2">
      {/* Inputs */}
      <div className="rounded-xl border border-[hsl(215,40%,18%)] bg-[hsl(220,55%,9%)] p-6">
        <h2 className="text-lg font-semibold text-white mb-5">Trade levels</h2>
        <div className="space-y-4">
          {fields.map((f) => (
            <div key={f.key}>
              <label
                htmlFor={`rr-${f.key}`}
                className="text-xs font-semibold text-[hsl(215,20%,60%)] mb-2 block uppercase tracking-wide"
              >
                {f.label}
              </label>
              <div className="relative">
                {f.prefix && (
                  <span className="absolute left-3 top-1/2 -translate-y-1/2 text-[hsl(215,20%,50%)] text-sm">
                    {f.prefix}
                  </span>
                )}
                <input
                  id={`rr-${f.key}`}
                  type="number"
                  inputMode="decimal"
                  step={f.step}
                  min={0}
                  value={f.value}
                  onChange={(e) => f.set(e.target.value)}
                  placeholder={f.optional ? 'optional' : undefined}
                  className={`input-field ${f.prefix ? 'pl-7' : ''} ${f.suffix ? 'pr-9' : ''}`}
                />
                {f.suffix && (
                  <span className="absolute right-3 top-1/2 -translate-y-1/2 text-[hsl(215,20%,50%)] text-sm">
                    {f.suffix}
                  </span>
                )}
              </div>
              <p className="mt-1 text-xs text-[hsl(215,20%,45%)]">{f.hint}</p>
            </div>
          ))}
        </div>

        <div className="mt-6 border-t border-[hsl(215,40%,14%)] pt-5">
          <h3 className="text-xs font-semibold text-[hsl(215,20%,60%)] uppercase tracking-wide mb-2">
            Formula
          </h3>
          <div className="font-mono text-xs text-slate-300 space-y-1">
            <p>risk = | entry − stop |</p>
            <p>reward = | target − entry |</p>
            <p>R = reward ÷ risk</p>
            <p>breakeven win rate = 1 ÷ (1 + R)</p>
          </div>
        </div>
      </div>

      {/* Results */}
      <div className="rounded-xl border border-[hsl(215,40%,18%)] bg-[hsl(220,55%,9%)] p-6">
        <h2 className="text-lg font-semibold text-white mb-5">Risk / reward</h2>

        {result === null ? (
          <div className="rounded-lg border border-amber-500/40 bg-amber-500/10 p-5">
            <p className="text-sm font-semibold text-amber-300">Check your inputs</p>
            <p className="mt-1 text-sm text-amber-200/80">{error}</p>
          </div>
        ) : (
          <>
            <div className="rounded-lg border border-indigo-500/30 bg-indigo-500/10 p-5 mb-5">
              <div className="text-xs font-semibold text-indigo-300 uppercase tracking-wide mb-1">
                Reward to risk — {result.direction}
              </div>
              <div className="text-4xl font-bold text-white font-mono">
                1 : {fmtNum(result.rrRatio, 2)}
              </div>
              <p className="mt-2 text-xs text-indigo-200/70">
                Risking {fmtUSD(result.risk)} per share to make {fmtUSD(result.reward)} per share.
              </p>
            </div>

            <dl className="space-y-3">
              <Stat label="Risk per share" value={fmtUSD(result.risk)} sub={`${fmtNum(result.lossPct)}% of entry`} tone="loss" />
              <Stat label="Reward per share" value={fmtUSD(result.reward)} sub={`${fmtNum(result.gainPct)}% of entry`} tone="gain" />
              <Stat
                label="Breakeven win rate"
                value={`${fmtNum(result.breakevenWinRate)}%`}
                sub="1 ÷ (1 + R), before costs"
              />
              {result.dollarRisk !== null && result.dollarReward !== null && (
                <>
                  <Stat
                    label="Dollar risk"
                    value={fmtUSD(result.dollarRisk)}
                    sub={`${fmtNum(result.shares ?? 0, 0)} shares × ${fmtUSD(result.risk)}`}
                    tone="loss"
                  />
                  <Stat
                    label="Dollar reward"
                    value={fmtUSD(result.dollarReward)}
                    sub={`${fmtNum(result.shares ?? 0, 0)} shares × ${fmtUSD(result.reward)}`}
                    tone="gain"
                  />
                </>
              )}
            </dl>

            <p className="mt-5 text-xs text-[hsl(215,20%,45%)] leading-relaxed">
              The breakeven win rate is the value of w that solves w × reward = (1 − w) × risk: the
              win percentage at which gains and losses cancel exactly over many trades of this
              shape. It is arithmetic about the levels entered, not an estimate of how often this
              trade would reach the target. Commissions, slippage, and partial fills are not
              included and would raise the win rate required.
            </p>
          </>
        )}
      </div>
    </div>
  )
}

function Stat({
  label,
  value,
  sub,
  tone,
}: {
  label: string
  value: string
  sub?: string
  tone?: 'gain' | 'loss'
}) {
  const color = tone === 'gain' ? 'text-emerald-400' : tone === 'loss' ? 'text-red-400' : 'text-white'
  return (
    <div className="flex items-start justify-between gap-4 border-b border-[hsl(215,40%,14%)] pb-3">
      <dt className="text-sm text-[hsl(215,20%,60%)]">{label}</dt>
      <dd className="text-right">
        <div className={`text-base font-semibold font-mono ${color}`}>{value}</div>
        {sub && <div className="text-xs text-[hsl(215,20%,45%)] font-mono">{sub}</div>}
      </dd>
    </div>
  )
}
