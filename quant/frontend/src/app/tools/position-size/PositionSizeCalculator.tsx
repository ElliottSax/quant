'use client'

import { useState, useMemo } from 'react'

// Self-contained position-size calculator. All math runs client-side; no data
// leaves the browser. Kept deliberately dependency-free so the page stays fast.

function fmtUSD(n: number): string {
  if (!isFinite(n)) return '—'
  return n.toLocaleString('en-US', { style: 'currency', currency: 'USD', maximumFractionDigits: 2 })
}

function fmtNum(n: number, dp = 2): string {
  if (!isFinite(n)) return '—'
  return n.toLocaleString('en-US', { minimumFractionDigits: dp, maximumFractionDigits: dp })
}

type Field = { label: string; hint: string; value: string; set: (v: string) => void; prefix?: string; suffix?: string }

export default function PositionSizeCalculator() {
  const [accountSize, setAccountSize] = useState('25000')
  const [riskPct, setRiskPct] = useState('1')
  const [entry, setEntry] = useState('50')
  const [stop, setStop] = useState('48')

  const r = useMemo(() => {
    const account = parseFloat(accountSize) || 0
    const risk = parseFloat(riskPct) || 0
    const entryPrice = parseFloat(entry) || 0
    const stopPrice = parseFloat(stop) || 0

    const dollarRisk = account * (risk / 100)
    const riskPerShare = Math.abs(entryPrice - stopPrice)
    const shares = riskPerShare > 0 ? Math.floor(dollarRisk / riskPerShare) : 0
    const positionValue = shares * entryPrice
    const positionPctOfAccount = account > 0 ? (positionValue / account) * 100 : 0
    const actualDollarRisk = shares * riskPerShare

    return { account, dollarRisk, riskPerShare, shares, positionValue, positionPctOfAccount, actualDollarRisk }
  }, [accountSize, riskPct, entry, stop])

  const fields: Field[] = [
    { label: 'Account size', hint: 'Total trading capital', value: accountSize, set: setAccountSize, prefix: '$' },
    { label: 'Risk per trade', hint: 'Percent of account to risk', value: riskPct, set: setRiskPct, suffix: '%' },
    { label: 'Entry price', hint: 'Price you plan to buy at', value: entry, set: setEntry, prefix: '$' },
    { label: 'Stop-loss price', hint: 'Price you will exit at a loss', value: stop, set: setStop, prefix: '$' },
  ]

  return (
    <div className="grid gap-6 lg:grid-cols-2">
      {/* Inputs */}
      <div className="rounded-xl border border-[hsl(215,40%,18%)] bg-[hsl(220,55%,9%)] p-6">
        <h2 className="text-lg font-semibold text-white mb-5">Trade details</h2>
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
                  className={`input-field ${f.prefix ? 'pl-7' : ''} ${f.suffix ? 'pr-8' : ''}`}
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
        <h2 className="text-lg font-semibold text-white mb-5">Position size</h2>

        <div className="rounded-lg border border-indigo-500/30 bg-indigo-500/10 p-5 mb-5">
          <div className="text-xs font-semibold text-indigo-300 uppercase tracking-wide mb-1">Shares to buy</div>
          <div className="text-4xl font-bold text-white font-mono">{r.shares.toLocaleString('en-US')}</div>
          {r.riskPerShare <= 0 && (
            <p className="mt-2 text-xs text-amber-400">
              Entry and stop-loss must differ to size a position.
            </p>
          )}
        </div>

        <dl className="space-y-3">
          <Stat label="Total dollar risk" value={fmtUSD(r.actualDollarRisk)} sub={`Target: ${fmtUSD(r.dollarRisk)}`} />
          <Stat label="Risk per share" value={fmtUSD(r.riskPerShare)} />
          <Stat label="Position value" value={fmtUSD(r.positionValue)} />
          <Stat label="Position as % of account" value={`${fmtNum(r.positionPctOfAccount)}%`} />
        </dl>

        <p className="mt-5 text-xs text-[hsl(215,20%,45%)] leading-relaxed">
          Shares are rounded down so your actual risk never exceeds the dollar amount you set.
          This tool does not account for commissions, slippage, or margin.
        </p>
      </div>
    </div>
  )
}

function Stat({ label, value, sub }: { label: string; value: string; sub?: string }) {
  return (
    <div className="flex items-center justify-between border-b border-[hsl(215,40%,14%)] pb-3">
      <dt className="text-sm text-[hsl(215,20%,60%)]">{label}</dt>
      <dd className="text-right">
        <div className="text-base font-semibold text-white font-mono">{value}</div>
        {sub && <div className="text-xs text-[hsl(215,20%,45%)] font-mono">{sub}</div>}
      </dd>
    </div>
  )
}
