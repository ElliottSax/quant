'use client'

import { useMemo, useState } from 'react'
import {
  ComposedChart,
  Line,
  Area,
  ReferenceLine,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
} from 'recharts'
import { computeMultiLegPayoff, type Leg, type LegPosition } from './multiLegPayoff'
import type { OptionType } from '../../options/blackScholes'

// Multi-leg options payoff-at-expiration diagram. Every number is closed-form
// arithmetic over the strikes/premiums/quantities entered below — there is
// no options chain or live quote behind this page.

function fmtUSD(n: number, dp = 0): string {
  if (!Number.isFinite(n)) return '—'
  return n.toLocaleString('en-US', { style: 'currency', currency: 'USD', minimumFractionDigits: dp, maximumFractionDigits: dp })
}

let nextLegId = 1
function newLeg(overrides: Partial<Leg> = {}): Leg {
  return {
    id: `leg${nextLegId++}`,
    type: overrides.type ?? 'call',
    position: overrides.position ?? 'long',
    strike: overrides.strike ?? 100,
    premium: overrides.premium ?? 5,
    quantity: overrides.quantity ?? 1,
  }
}

type Preset = { name: string; build: () => Leg[] }

const PRESETS: Preset[] = [
  { name: 'Long call', build: () => [newLeg({ type: 'call', position: 'long', strike: 100, premium: 5 })] },
  { name: 'Long put', build: () => [newLeg({ type: 'put', position: 'long', strike: 100, premium: 4 })] },
  {
    name: 'Bull call spread',
    build: () => [
      newLeg({ type: 'call', position: 'long', strike: 100, premium: 5 }),
      newLeg({ type: 'call', position: 'short', strike: 110, premium: 2 }),
    ],
  },
  {
    name: 'Bear put spread',
    build: () => [
      newLeg({ type: 'put', position: 'long', strike: 100, premium: 5 }),
      newLeg({ type: 'put', position: 'short', strike: 90, premium: 2 }),
    ],
  },
  {
    name: 'Long straddle',
    build: () => [
      newLeg({ type: 'call', position: 'long', strike: 100, premium: 5 }),
      newLeg({ type: 'put', position: 'long', strike: 100, premium: 4 }),
    ],
  },
  {
    name: 'Long strangle',
    build: () => [
      newLeg({ type: 'call', position: 'long', strike: 105, premium: 3 }),
      newLeg({ type: 'put', position: 'long', strike: 95, premium: 3 }),
    ],
  },
  {
    name: 'Iron condor',
    build: () => [
      newLeg({ type: 'put', position: 'long', strike: 90, premium: 1 }),
      newLeg({ type: 'put', position: 'short', strike: 95, premium: 3 }),
      newLeg({ type: 'call', position: 'short', strike: 105, premium: 3 }),
      newLeg({ type: 'call', position: 'long', strike: 110, premium: 1 }),
    ],
  },
]

export default function OptionsPayoffBuilder() {
  const [legs, setLegs] = useState<Leg[]>(PRESETS[2].build())

  function updateLeg(id: string, patch: Partial<Leg>) {
    setLegs((ls) => ls.map((l) => (l.id === id ? { ...l, ...patch } : l)))
  }
  function removeLeg(id: string) {
    setLegs((ls) => ls.filter((l) => l.id !== id))
  }
  function addLeg() {
    setLegs((ls) => [...ls, newLeg({ strike: ls[ls.length - 1]?.strike ?? 100 })])
  }

  const result = useMemo(() => {
    if (legs.length === 0) return null
    const strikes = legs.map((l) => l.strike).filter((s) => Number.isFinite(s) && s > 0)
    if (strikes.length === 0) return null
    const minK = Math.min(...strikes)
    const maxK = Math.max(...strikes)
    const pad = Math.max(10, (maxK - minK) * 0.6 || minK * 0.3)
    return computeMultiLegPayoff(legs, [Math.max(0, minK - pad), maxK + pad])
  }, [JSON.stringify(legs)])

  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-sm font-semibold text-[hsl(215,20%,60%)] uppercase tracking-wide mb-2">Strategy presets</h2>
        <div className="flex flex-wrap gap-2">
          {PRESETS.map((p) => (
            <button
              key={p.name}
              type="button"
              onClick={() => setLegs(p.build())}
              className="rounded-md px-3 py-1.5 text-sm font-medium border border-[hsl(215,40%,18%)] text-[hsl(215,20%,70%)] hover:border-indigo-500/50 hover:text-indigo-300 transition-colors"
            >
              {p.name}
            </button>
          ))}
        </div>
      </div>

      <div className="grid gap-6 lg:grid-cols-2">
        {/* Legs editor */}
        <div className="rounded-xl border border-[hsl(215,40%,18%)] bg-[hsl(220,55%,9%)] p-6">
          <h2 className="text-lg font-semibold text-white mb-5">Legs</h2>
          <div className="space-y-3">
            {legs.map((leg) => (
              <div key={leg.id} className="rounded-lg border border-[hsl(215,40%,14%)] p-3">
                <div className="grid grid-cols-2 gap-2 mb-2">
                  <select
                    value={leg.position}
                    onChange={(e) => updateLeg(leg.id, { position: e.target.value as LegPosition })}
                    className="input-field text-sm"
                  >
                    <option value="long">Long (buy)</option>
                    <option value="short">Short (sell)</option>
                  </select>
                  <select
                    value={leg.type}
                    onChange={(e) => updateLeg(leg.id, { type: e.target.value as OptionType })}
                    className="input-field text-sm"
                  >
                    <option value="call">Call</option>
                    <option value="put">Put</option>
                  </select>
                </div>
                <div className="grid grid-cols-3 gap-2">
                  <div>
                    <label className="text-[10px] text-[hsl(215,20%,50%)] uppercase">Strike</label>
                    <input type="number" min={0.01} step={1} value={leg.strike}
                      onChange={(e) => updateLeg(leg.id, { strike: parseFloat(e.target.value) || 0 })}
                      className="input-field text-sm" />
                  </div>
                  <div>
                    <label className="text-[10px] text-[hsl(215,20%,50%)] uppercase">Premium</label>
                    <input type="number" min={0} step={0.05} value={leg.premium}
                      onChange={(e) => updateLeg(leg.id, { premium: parseFloat(e.target.value) || 0 })}
                      className="input-field text-sm" />
                  </div>
                  <div>
                    <label className="text-[10px] text-[hsl(215,20%,50%)] uppercase">Qty</label>
                    <input type="number" min={1} step={1} value={leg.quantity}
                      onChange={(e) => updateLeg(leg.id, { quantity: parseInt(e.target.value) || 1 })}
                      className="input-field text-sm" />
                  </div>
                </div>
                <button type="button" onClick={() => removeLeg(leg.id)} className="mt-2 text-xs text-[hsl(215,20%,50%)] hover:text-red-400">
                  Remove leg
                </button>
              </div>
            ))}
          </div>
          <button
            type="button"
            onClick={addLeg}
            className="mt-3 w-full rounded-lg border border-dashed border-[hsl(215,40%,25%)] py-2 text-sm text-[hsl(215,20%,60%)] hover:border-indigo-500/50 hover:text-indigo-300"
          >
            + Add leg
          </button>
          <p className="mt-3 text-xs text-[hsl(215,20%,45%)]">1 contract = 100 shares. Values are at expiration only — no time value.</p>
        </div>

        {/* Results */}
        <div className="rounded-xl border border-[hsl(215,40%,18%)] bg-[hsl(220,55%,9%)] p-6">
          <h2 className="text-lg font-semibold text-white mb-5">Payoff at expiration</h2>

          {!result ? (
            <div className="rounded-lg border border-amber-500/40 bg-amber-500/10 p-5">
              <p className="text-sm text-amber-200/80">Add at least one leg with a valid strike, premium, and quantity.</p>
            </div>
          ) : (
            <>
              <dl className="space-y-3 mb-5">
                <Stat label="Net premium" value={result.netPremium >= 0 ? `${fmtUSD(result.netPremium)} debit` : `${fmtUSD(-result.netPremium)} credit`} />
                <Stat label="Max profit" value={result.maxProfit === null ? 'Unlimited' : fmtUSD(result.maxProfit)} highlight="good" />
                <Stat label="Max loss" value={result.maxLoss === null ? 'Unlimited' : fmtUSD(Math.abs(result.maxLoss))} highlight="bad" />
                <Stat label="Breakeven(s)" value={result.breakevens.length > 0 ? result.breakevens.map((b) => fmtUSD(b, 2)).join(', ') : '—'} />
              </dl>

              <ResponsiveContainer width="100%" height={260}>
                <ComposedChart data={result.curve} margin={{ top: 8, right: 12, bottom: 20, left: 8 }}>
                  <CartesianGrid strokeDasharray="3 3" stroke="#334155" />
                  <XAxis
                    dataKey="price"
                    type="number"
                    domain={['dataMin', 'dataMax']}
                    stroke="#94a3b8"
                    tick={{ fontSize: 11 }}
                    tickFormatter={(v: number) => v.toFixed(0)}
                    label={{ value: 'Underlying price at expiry', position: 'bottom', fill: '#94a3b8', fontSize: 11 }}
                  />
                  <YAxis stroke="#94a3b8" tick={{ fontSize: 11 }} width={65} tickFormatter={(v: number) => fmtUSD(v)} />
                  <Tooltip
                    contentStyle={{ backgroundColor: '#1e293b', border: '1px solid #334155', borderRadius: '8px' }}
                    labelFormatter={(v: number) => `Price: ${fmtUSD(v, 2)}`}
                    formatter={(value: number) => [fmtUSD(value), 'P/L']}
                  />
                  <ReferenceLine y={0} stroke="#64748b" />
                  {result.breakevens.map((b) => (
                    <ReferenceLine key={b} x={b} stroke="#818cf8" strokeDasharray="3 3" />
                  ))}
                  <defs>
                    <linearGradient id="payoffPos" x1="0" y1="0" x2="0" y2="1">
                      <stop offset="0%" stopColor="#34d399" stopOpacity={0.3} />
                      <stop offset="100%" stopColor="#34d399" stopOpacity={0} />
                    </linearGradient>
                  </defs>
                  <Area type="linear" dataKey="payoff" stroke="#818cf8" strokeWidth={2} fill="url(#payoffPos)" name="payoff" />
                </ComposedChart>
              </ResponsiveContainer>
            </>
          )}
        </div>
      </div>
    </div>
  )
}

function Stat({ label, value, highlight }: { label: string; value: string; highlight?: 'good' | 'bad' }) {
  const color = highlight === 'good' ? 'text-emerald-400' : highlight === 'bad' ? 'text-red-400' : 'text-white'
  return (
    <div className="flex items-start justify-between gap-4 border-b border-[hsl(215,40%,14%)] pb-3">
      <dt className="text-sm text-[hsl(215,20%,60%)]">{label}</dt>
      <dd className={`text-base font-semibold font-mono text-right ${color}`}>{value}</dd>
    </div>
  )
}
