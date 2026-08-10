'use client'

import { useState, useMemo } from 'react'

// Self-contained risk/reward calculator. All math is client-side and instant.

function fmtUSD(n: number): string {
  if (!isFinite(n)) return '—'
  return n.toLocaleString('en-US', { style: 'currency', currency: 'USD', maximumFractionDigits: 2 })
}

function fmtNum(n: number, dp = 2): string {
  if (!isFinite(n)) return '—'
  return n.toLocaleString('en-US', { minimumFractionDigits: dp, maximumFractionDigits: dp })
}

type Field = {
  label: string
  hint: string
  value: string
  set: (v: string) => void
  prefix?: string
  suffix?: string
}

export default function RiskRewardCalculator() {
  const [entry, setEntry] = useState('100')
  const [stop, setStop] = useState('95')
  const [target, setTarget] = useState('115')
  const [shares, setShares] = useState('')

  const r = useMemo(() => {
    const entryPrice = parseFloat(entry) || 0
    const stopPrice = parseFloat(stop) || 0
    const targetPrice = parseFloat(target) || 0
    const size = parseFloat(shares) || 0

    const risk = Math.abs(entryPrice - stopPrice)
    const reward = Math.abs(targetPrice - entryPrice)
    const rrRatio = risk > 0 ? reward / risk : 0
    const pctGain = entryPrice > 0 ? ((targetPrice - entryPrice) / entryPrice) * 100 : 0
    const pctLoss = entryPrice > 0 ? ((stopPrice - entryPrice) / entryPrice) * 100 : 0
    const breakevenWinRate = (1 / (1 + rrRatio)) * 100

    const hasSize = size > 0
    const dollarRisk = hasSize ? risk * size : 0
    const dollarReward = hasSize ? reward * size : 0

    return { risk, reward, rrRatio, pctGain, pctLoss, breakevenWinRate, hasSize, dollarRisk, dollarReward }
  }, [entry, stop, target, shares])

  const fields: Field[] = [
    { label: 'Entry price', hint: 'Price you plan to buy at', value: entry, set: setEntry, prefix: '$' },
    { label: 'Stop-loss price', hint: 'Price you will exit at a loss', value: stop, set: setStop, prefix: '$' },
    { label: 'Target price', hint: 'Price you plan to take profit', value: target, set: setTarget, prefix: '$' },
    { label: 'Position size (optional)', hint: 'Number of shares, for dollar figures', value: shares, set: setShares, suffix: 'sh' },
  ]

  return (
    <div className="grid gap-6 lg:grid-cols-2">
      {/* Inputs */}
      <div className="rounded-xl border border-[hsl(215,40%,18%)] bg-[hsl(220,55%,9%)] p-6">
        <h2 className="text-lg font-semibold text-white mb-5">Trade levels</h2>
        <div className="space-y-4">
          {fields.map((f) => (
            <div key={f.label}>
              <label className="text-xs font-semibold text-[hsl(215,20%,60%)] mb-2 block uppercase tracking-wide">
                {f.label}
              </label>
              <div className="relative">
                {f.prefix && (
                  <span className="absolute left-3 top-1/2 -translate-y-1/2 text-[hsl(215,20%,50%)] text-sm">
                    {f.prefix}
                  </span>
                )}
                <input
                  type="number"
                  inputMode="decimal"
                  value={f.value}
                  onChange={(e) => f.set(e.target.value)}
                  placeholder={f.suffix === 'sh' ? 'optional' : undefined}
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
      </div>

      {/* Results */}
      <div className="rounded-xl border border-[hsl(215,40%,18%)] bg-[hsl(220,55%,9%)] p-6">
        <h2 className="text-lg font-semibold text-white mb-5">Risk / reward</h2>

        <div className="rounded-lg border border-indigo-500/30 bg-indigo-500/10 p-5 mb-5">
          <div className="text-xs font-semibold text-indigo-300 uppercase tracking-wide mb-1">Risk / reward ratio</div>
          <div className="text-4xl font-bold text-white font-mono">
            {r.rrRatio > 0 ? `1 : ${fmtNum(r.rrRatio, 1)}` : '—'}
          </div>
          {r.risk <= 0 && (
            <p className="mt-2 text-xs text-amber-400">Entry and stop-loss must differ to compute a ratio.</p>
          )}
        </div>

        <dl className="space-y-3">
          <Stat label="Risk per share" value={fmtUSD(r.risk)} tone="loss" />
          <Stat label="Reward per share" value={fmtUSD(r.reward)} tone="gain" />
          <Stat label="Potential gain" value={`${fmtNum(r.pctGain)}%`} tone="gain" />
          <Stat label="Potential loss" value={`${fmtNum(r.pctLoss)}%`} tone="loss" />
          <Stat label="Breakeven win rate" value={`${fmtNum(r.breakevenWinRate)}%`} sub="Win rate needed to break even" />
          {r.hasSize && (
            <>
              <Stat label="Dollar risk" value={fmtUSD(r.dollarRisk)} tone="loss" />
              <Stat label="Dollar reward" value={fmtUSD(r.dollarReward)} tone="gain" />
            </>
          )}
        </dl>

        <p className="mt-5 text-xs text-[hsl(215,20%,45%)] leading-relaxed">
          A higher reward-to-risk ratio lets you be profitable while winning fewer than half your
          trades. The breakeven win rate is the win percentage at which wins and losses cancel out.
        </p>
      </div>
    </div>
  )
}

function Stat({ label, value, sub, tone }: { label: string; value: string; sub?: string; tone?: 'gain' | 'loss' }) {
  const color = tone === 'gain' ? 'text-emerald-400' : tone === 'loss' ? 'text-red-400' : 'text-white'
  return (
    <div className="flex items-center justify-between border-b border-[hsl(215,40%,14%)] pb-3">
      <dt className="text-sm text-[hsl(215,20%,60%)]">{label}</dt>
      <dd className="text-right">
        <div className={`text-base font-semibold font-mono ${color}`}>{value}</div>
        {sub && <div className="text-xs text-[hsl(215,20%,45%)]">{sub}</div>}
      </dd>
    </div>
  )
}
