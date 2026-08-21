'use client'

import { useMemo, useState } from 'react'
import {
  ComposedChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
} from 'recharts'
import { computeRiskAdjustedReturn, validateReturns, type RiskAdjustedInputs } from './riskAdjustedReturn'

// Sharpe/Sortino/Calmar over a pasted return series only. No market data is
// fetched; everything computes client-side from the numbers you paste in.

function pct(n: number, dp = 2): string {
  if (!Number.isFinite(n)) return '—'
  return `${(n * 100).toFixed(dp)}%`
}
function ratio(n: number | null): string {
  return n === null ? 'undefined (zero volatility)' : n.toFixed(3)
}

const PERIODICITY = [
  { label: 'Daily', value: 252 },
  { label: 'Weekly', value: 52 },
  { label: 'Monthly', value: 12 },
  { label: 'Quarterly', value: 4 },
  { label: 'Annual', value: 1 },
]

const DEFAULT_RETURNS = '2.1, -1.4, 3.0, 0.8, -2.5, 1.9, 2.7, -0.6, 1.1, -3.2, 4.0, 1.5'

export default function RiskAdjustedReturnCalculator() {
  const [returnsText, setReturnsText] = useState(DEFAULT_RETURNS)
  const [riskFreePct, setRiskFreePct] = useState('4')
  const [periodsPerYear, setPeriodsPerYear] = useState(12)

  const parsedReturns = useMemo(
    () =>
      returnsText
        .split(/[,\n]/)
        .map((s) => s.trim())
        .filter((s) => s.length > 0)
        .map((s) => Number(s) / 100),
    [returnsText]
  )

  const { error, result } = useMemo(() => {
    const inputs: RiskAdjustedInputs = {
      returns: parsedReturns,
      riskFreeAnnual: (Number(riskFreePct) || 0) / 100,
      periodsPerYear,
    }
    const message = validateReturns(inputs)
    if (message !== null) return { error: message, result: null }
    return { error: null, result: computeRiskAdjustedReturn(inputs) }
  }, [parsedReturns, riskFreePct, periodsPerYear])

  const chartData = result?.equityCurve.map((v, i) => ({ period: i, equity: v })) ?? []

  return (
    <div className="grid gap-6 lg:grid-cols-2">
      <div className="rounded-xl border border-[hsl(215,40%,18%)] bg-[hsl(220,55%,9%)] p-6">
        <h2 className="text-lg font-semibold text-white mb-5">Return series</h2>
        <label htmlFor="returns" className="text-xs font-semibold text-[hsl(215,20%,60%)] mb-2 block uppercase tracking-wide">
          Periodic returns (%), comma or newline separated
        </label>
        <textarea
          id="returns"
          value={returnsText}
          onChange={(e) => setReturnsText(e.target.value)}
          rows={6}
          className="input-field font-mono text-sm w-full"
        />
        <p className="mt-1 text-xs text-[hsl(215,20%,45%)]">{parsedReturns.length} periods parsed. Paste your own strategy's or backtest's period-over-period returns.</p>

        <div className="mt-5 grid grid-cols-2 gap-4">
          <div>
            <label htmlFor="rf" className="text-xs font-semibold text-[hsl(215,20%,60%)] mb-2 block uppercase tracking-wide">Risk-free rate</label>
            <div className="relative">
              <input id="rf" type="number" step={0.1} value={riskFreePct} onChange={(e) => setRiskFreePct(e.target.value)} className="input-field pr-8" />
              <span className="absolute right-3 top-1/2 -translate-y-1/2 text-[hsl(215,20%,50%)] text-sm">%</span>
            </div>
          </div>
          <div>
            <label htmlFor="ppy" className="text-xs font-semibold text-[hsl(215,20%,60%)] mb-2 block uppercase tracking-wide">Return period</label>
            <select id="ppy" value={periodsPerYear} onChange={(e) => setPeriodsPerYear(Number(e.target.value))} className="input-field">
              {PERIODICITY.map((p) => (
                <option key={p.value} value={p.value}>{p.label}</option>
              ))}
            </select>
          </div>
        </div>

        <div className="mt-6 border-t border-[hsl(215,40%,14%)] pt-5">
          <h3 className="text-xs font-semibold text-[hsl(215,20%,60%)] uppercase tracking-wide mb-2">Method</h3>
          <div className="font-mono text-xs text-slate-300 space-y-1">
            <p>Sharpe = mean(excess) / stdev(excess) × √periods/yr</p>
            <p>Sortino = mean(excess) / downside-dev × √periods/yr</p>
            <p>Calmar = CAGR / max drawdown</p>
            <p>Ulcer Index = √mean(drawdown²) -- Pain Index = mean(|drawdown|)</p>
            <p>PSR = Φ[(SR&minus;SR*)√(n&minus;1) / √(1&minus;skew·SR+((kurt&minus;1)/4)SR²)]</p>
          </div>
        </div>
      </div>

      <div className="rounded-xl border border-[hsl(215,40%,18%)] bg-[hsl(220,55%,9%)] p-6">
        <h2 className="text-lg font-semibold text-white mb-5">Risk-adjusted ratios</h2>

        {error !== null || result === null ? (
          <div className="rounded-lg border border-amber-500/40 bg-amber-500/10 p-5">
            <p className="text-sm font-semibold text-amber-300">Check your inputs</p>
            <p className="mt-1 text-sm text-amber-200/80">{error ?? 'Enter a valid return series.'}</p>
          </div>
        ) : (
          <>
            <dl className="space-y-3 mb-5">
              <Stat label="Sharpe ratio" value={ratio(result.sharpe)} sub="annualized" />
              <Stat label="Sortino ratio" value={ratio(result.sortino)} sub="annualized, downside only" />
              <Stat label="Calmar ratio" value={ratio(result.calmar)} sub="CAGR ÷ max drawdown" />
              <Stat label="Annualized return" value={pct(result.annualizedReturn)} />
              <Stat label="Annualized volatility" value={pct(result.annualizedVolatility)} />
              <Stat label="Max drawdown" value={pct(-result.maxDrawdown)} />
              <Stat label="Ulcer Index" value={result.ulcerIndex.toFixed(2)} sub="RMS of drawdown path" />
              <Stat label="Pain Index" value={result.painIndex.toFixed(2)} sub="mean of drawdown path" />
              <Stat
                label="Probabilistic Sharpe Ratio"
                value={result.probabilisticSharpeRatio === null ? 'undefined (zero volatility)' : pct(result.probabilisticSharpeRatio, 1)}
                sub="confidence true Sharpe > 0"
              />
            </dl>

            <h3 className="text-xs font-semibold text-[hsl(215,20%,60%)] uppercase tracking-wide mb-2">Equity curve (starting at 1.00)</h3>
            <ResponsiveContainer width="100%" height={200}>
              <ComposedChart data={chartData} margin={{ top: 8, right: 12, bottom: 8, left: 8 }}>
                <CartesianGrid strokeDasharray="3 3" stroke="#334155" />
                <XAxis dataKey="period" stroke="#94a3b8" tick={{ fontSize: 11 }} />
                <YAxis stroke="#94a3b8" tick={{ fontSize: 11 }} width={50} domain={['auto', 'auto']} />
                <Tooltip
                  contentStyle={{ backgroundColor: '#1e293b', border: '1px solid #334155', borderRadius: '8px' }}
                  formatter={(value: number) => [value.toFixed(4), 'Equity']}
                />
                <Line type="monotone" dataKey="equity" stroke="#818cf8" strokeWidth={2} dot={false} />
              </ComposedChart>
            </ResponsiveContainer>

            <p className="mt-5 text-xs text-[hsl(215,20%,45%)] leading-relaxed">
              Sample standard deviation (n-1) for Sharpe; downside deviation uses the full period
              count in its denominator, per Sortino &amp; Price (1994) — not just the count of losing
              periods, which some calculators use and which inflates the ratio. A "Sharpe ratio
              calculator" showing a different number than this one on the same data most likely
              differs on exactly one of these two conventions.
            </p>
            <p className="mt-3 text-xs text-[hsl(215,20%,45%)] leading-relaxed">
              The Probabilistic Sharpe Ratio (Bailey &amp; Lopez de Prado, 2012) answers a different
              question than Sharpe itself: given only {result.n} observations and this return series'
              actual skewness ({result.skewness.toFixed(2)}) and kurtosis ({result.kurtosis.toFixed(2)}
              , a normal distribution scores 0 and 3), how confident can you be that the TRUE Sharpe
              ratio is really above zero, rather than this track record just getting lucky? A short or
              fat-tailed track record can post an impressive Sharpe ratio and still score a low PSR —
              most free Sharpe calculators skip this entirely.
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
