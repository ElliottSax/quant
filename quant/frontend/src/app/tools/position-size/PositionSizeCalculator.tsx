'use client'

import { useMemo, useState } from 'react'
import {
  computePositionSize,
  validatePositionSize,
  type PositionSizeInputs,
  type PositionSizeResult,
} from './positionSize'

// Closed-form position sizing over user input only. No market data is read and
// none is displayed, so every figure here is reproducible by hand from the four
// inputs. All arithmetic runs client-side; nothing leaves the browser.

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
}

export default function PositionSizeCalculator() {
  const [accountSize, setAccountSize] = useState('25000')
  const [riskPct, setRiskPct] = useState('1')
  const [entry, setEntry] = useState('50')
  const [stop, setStop] = useState('48')

  const { error, result } = useMemo<{ error: string | null; result: PositionSizeResult | null }>(() => {
    const inputs: PositionSizeInputs = {
      account: parseInput(accountSize),
      riskPct: parseInput(riskPct),
      entry: parseInput(entry),
      stop: parseInput(stop),
    }
    const message = validatePositionSize(inputs)
    if (message !== null) return { error: message, result: null }
    return { error: null, result: computePositionSize(inputs) }
  }, [accountSize, riskPct, entry, stop])

  const fields: Field[] = [
    { key: 'account', label: 'Account size', hint: 'Total trading capital', value: accountSize, set: setAccountSize, prefix: '$', step: 100 },
    { key: 'risk', label: 'Risk per trade', hint: 'Percent of the account to put at risk', value: riskPct, set: setRiskPct, suffix: '%', step: 0.1 },
    { key: 'entry', label: 'Entry price', hint: 'Price per share at entry', value: entry, set: setEntry, prefix: '$', step: 0.01 },
    { key: 'stop', label: 'Stop-loss price', hint: 'Exit price. Below entry is a long, above entry is a short', value: stop, set: setStop, prefix: '$', step: 0.01 },
  ]

  return (
    <div className="grid gap-6 lg:grid-cols-2">
      {/* Inputs */}
      <div className="rounded-xl border border-[hsl(215,40%,18%)] bg-[hsl(220,55%,9%)] p-6">
        <h2 className="text-lg font-semibold text-white mb-5">Trade details</h2>
        <div className="space-y-4">
          {fields.map((f) => (
            <div key={f.key}>
              <label
                htmlFor={`ps-${f.key}`}
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
                  id={`ps-${f.key}`}
                  type="number"
                  inputMode="decimal"
                  step={f.step}
                  min={0}
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

        <div className="mt-6 border-t border-[hsl(215,40%,14%)] pt-5">
          <h3 className="text-xs font-semibold text-[hsl(215,20%,60%)] uppercase tracking-wide mb-2">
            Formula
          </h3>
          <div className="font-mono text-xs text-slate-300 space-y-1">
            <p>dollar risk = account × (risk % ÷ 100)</p>
            <p>risk per share = | entry − stop |</p>
            <p>shares = floor(dollar risk ÷ risk per share)</p>
            <p>position value = shares × entry</p>
          </div>
        </div>
      </div>

      {/* Results */}
      <div className="rounded-xl border border-[hsl(215,40%,18%)] bg-[hsl(220,55%,9%)] p-6">
        <h2 className="text-lg font-semibold text-white mb-5">Position size</h2>

        {result === null ? (
          <div className="rounded-lg border border-amber-500/40 bg-amber-500/10 p-5">
            <p className="text-sm font-semibold text-amber-300">Check your inputs</p>
            <p className="mt-1 text-sm text-amber-200/80">{error}</p>
          </div>
        ) : (
          <>
            <div className="rounded-lg border border-indigo-500/30 bg-indigo-500/10 p-5 mb-5">
              <div className="text-xs font-semibold text-indigo-300 uppercase tracking-wide mb-1">
                Shares — {result.direction === 'long' ? 'long (stop below entry)' : 'short (stop above entry)'}
              </div>
              <div className="text-4xl font-bold text-white font-mono">
                {result.shares.toLocaleString('en-US')}
              </div>
              {result.shares === 0 && (
                <p className="mt-2 text-xs text-amber-400">
                  Risk per share ({fmtUSD(result.riskPerShare)}) is larger than the dollar risk
                  ({fmtUSD(result.targetDollarRisk)}), so one whole share would already exceed the
                  limit set above.
                </p>
              )}
            </div>

            <dl className="space-y-3">
              <Stat
                label="Dollar risk if stopped"
                value={fmtUSD(result.actualDollarRisk)}
                sub={`${fmtNum(result.actualRiskPctOfAccount)}% of account · limit ${fmtUSD(result.targetDollarRisk)}`}
              />
              <Stat
                label="Risk per share"
                value={fmtUSD(result.riskPerShare)}
                sub={`${fmtNum(result.stopDistancePct)}% from entry`}
              />
              <Stat label="Position value" value={fmtUSD(result.positionValue)} />
              <Stat label="Position as % of account" value={`${fmtNum(result.positionPctOfAccount)}%`} />
            </dl>

            {result.needsMargin && (
              <p className="mt-4 rounded-lg border border-amber-500/30 bg-amber-500/5 px-3 py-2 text-xs text-amber-300/90 leading-relaxed">
                The position value is {fmtNum(result.positionPctOfAccount)}% of the account, so this
                share count is larger than the cash balance entered and would require margin or
                leverage to hold.
              </p>
            )}

            <p className="mt-5 text-xs text-[hsl(215,20%,45%)] leading-relaxed">
              Shares are rounded down, so the dollar risk shown is at or below the limit implied by
              your risk percentage. The figures assume a single fill at the entry price and an exit
              at exactly the stop price; commissions, slippage, gaps, and financing costs are not
              included.
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
