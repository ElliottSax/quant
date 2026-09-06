'use client'

import { useMemo, useState } from 'react'
import {
  ComposedChart,
  Bar,
  ReferenceLine,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
} from 'recharts'
import { computeVar, validateVar, type VarInputs, type VarResult } from './valueAtRisk'

// Parametric and historical VaR/CVaR over a pasted return series and a
// portfolio value only. No market data is fetched; everything computes
// client-side from the numbers you paste in.

function fmtUSD(n: number, dp = 0): string {
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
  return `${(n * 100).toLocaleString('en-US', { minimumFractionDigits: dp, maximumFractionDigits: dp })}%`
}

const CONFIDENCE_OPTIONS: { label: string; value: VarInputs['confidence'] }[] = [
  { label: '90%', value: 0.9 },
  { label: '95%', value: 0.95 },
  { label: '99%', value: 0.99 },
]

const DEFAULT_RETURNS =
  '1.2, -0.8, 0.5, -2.1, 1.8, -0.3, 0.9, -1.4, 2.2, -0.6, 0.4, -3.5, 1.1, -0.9, 0.7, -1.1, 1.6, -0.5, 0.3, -2.8, 1.0, -0.7, 0.6, -1.6, 1.3'

export default function ValueAtRiskCalculator() {
  const [portfolioValue, setPortfolioValue] = useState('100000')
  const [confidence, setConfidence] = useState<VarInputs['confidence']>(0.95)
  const [horizonDays, setHorizonDays] = useState('1')
  const [returnsText, setReturnsText] = useState(DEFAULT_RETURNS)

  const parsedReturns = useMemo(
    () =>
      returnsText
        .split(/[,\n]/)
        .map((s) => s.trim())
        .filter((s) => s.length > 0)
        .map((s) => Number(s) / 100),
    [returnsText]
  )

  const { error, result } = useMemo<{ error: string | null; result: VarResult | null }>(() => {
    const inputs: VarInputs = {
      portfolioValue: Number(portfolioValue),
      confidence,
      horizonDays: Number(horizonDays),
      returns: parsedReturns,
    }
    const message = validateVar(inputs)
    if (message !== null) return { error: message, result: null }
    return { error: null, result: computeVar(inputs) }
  }, [portfolioValue, confidence, horizonDays, parsedReturns])

  const chartData = result
    ? [
        { method: 'Parametric', VaR: result.parametricVaR, CVaR: result.parametricCVaR },
        { method: 'Historical', VaR: result.historicalVaR, CVaR: result.historicalCVaR },
      ]
    : []

  return (
    <div className="grid gap-6 lg:grid-cols-2">
      {/* Inputs */}
      <div className="rounded-xl border border-[hsl(215,40%,18%)] bg-[hsl(220,55%,9%)] p-6">
        <h2 className="text-lg font-semibold text-white mb-5">Portfolio & return series</h2>

        <div className="grid grid-cols-2 gap-4 mb-4">
          <div>
            <label htmlFor="var-value" className="text-xs font-semibold text-[hsl(215,20%,60%)] mb-2 block uppercase tracking-wide">
              Portfolio value
            </label>
            <div className="relative">
              <span className="absolute left-3 top-1/2 -translate-y-1/2 text-[hsl(215,20%,50%)] text-sm">$</span>
              <input
                id="var-value"
                type="number"
                inputMode="decimal"
                step={1000}
                min={0}
                value={portfolioValue}
                onChange={(e) => setPortfolioValue(e.target.value)}
                className="input-field pl-7"
              />
            </div>
          </div>
          <div>
            <label htmlFor="var-horizon" className="text-xs font-semibold text-[hsl(215,20%,60%)] mb-2 block uppercase tracking-wide">
              Horizon (periods)
            </label>
            <input
              id="var-horizon"
              type="number"
              inputMode="numeric"
              step={1}
              min={1}
              value={horizonDays}
              onChange={(e) => setHorizonDays(e.target.value)}
              className="input-field"
            />
          </div>
        </div>

        <div className="mb-4">
          <label className="text-xs font-semibold text-[hsl(215,20%,60%)] mb-2 block uppercase tracking-wide">
            Confidence level
          </label>
          <div className="flex gap-2">
            {CONFIDENCE_OPTIONS.map((c) => (
              <button
                key={c.value}
                type="button"
                onClick={() => setConfidence(c.value)}
                className={`flex-1 rounded-md px-3 py-2 text-sm font-medium border transition-colors ${
                  confidence === c.value
                    ? 'border-indigo-500 bg-indigo-500/15 text-indigo-300'
                    : 'border-[hsl(215,40%,18%)] text-[hsl(215,20%,60%)] hover:border-indigo-500/50'
                }`}
              >
                {c.label}
              </button>
            ))}
          </div>
        </div>

        <label htmlFor="var-returns" className="text-xs font-semibold text-[hsl(215,20%,60%)] mb-2 block uppercase tracking-wide">
          Periodic returns (%), comma or newline separated
        </label>
        <textarea
          id="var-returns"
          value={returnsText}
          onChange={(e) => setReturnsText(e.target.value)}
          rows={6}
          className="input-field font-mono text-sm w-full"
        />
        <p className="mt-1 text-xs text-[hsl(215,20%,45%)]">
          {parsedReturns.length} periods parsed. The horizon above is expressed in the same
          periodicity as these returns (e.g. days, if these are daily returns).
        </p>

        <div className="mt-6 border-t border-[hsl(215,40%,14%)] pt-5">
          <h3 className="text-xs font-semibold text-[hsl(215,20%,60%)] uppercase tracking-wide mb-2">Formulas</h3>
          <div className="font-mono text-xs text-slate-300 space-y-1">
            <p>Parametric VaR = (z·&sigma; &minus; &mu;) · &radic;t · V&#8320;</p>
            <p>Parametric CVaR = (&sigma;·&phi;(z) / (1&minus;c) &minus; &mu;) · &radic;t · V&#8320;</p>
            <p>Historical VaR = &minus;Q<sub>1&minus;c</sub>(returns) · V&#8320;</p>
            <p>Historical CVaR = &minus;mean(returns &le; threshold) · V&#8320;</p>
          </div>
        </div>
      </div>

      {/* Results */}
      <div className="rounded-xl border border-[hsl(215,40%,18%)] bg-[hsl(220,55%,9%)] p-6">
        <h2 className="text-lg font-semibold text-white mb-5">VaR & CVaR estimates</h2>

        {error !== null || result === null ? (
          <div className="rounded-lg border border-amber-500/40 bg-amber-500/10 p-5">
            <p className="text-sm font-semibold text-amber-300">Check your inputs</p>
            <p className="mt-1 text-sm text-amber-200/80">{error ?? 'Enter a valid return series.'}</p>
          </div>
        ) : (
          <>
            <div className="grid grid-cols-2 gap-3 mb-5">
              <div className="rounded-lg border border-indigo-500/30 bg-indigo-500/10 p-4">
                <div className="text-[10px] font-semibold text-indigo-300 uppercase tracking-wide mb-1">Parametric VaR</div>
                <div className="text-2xl font-bold text-white font-mono">{fmtUSD(result.parametricVaR)}</div>
                <div className="mt-1 text-[10px] text-indigo-200/70">CVaR {fmtUSD(result.parametricCVaR)}</div>
              </div>
              <div className="rounded-lg border border-emerald-500/30 bg-emerald-500/10 p-4">
                <div className="text-[10px] font-semibold text-emerald-300 uppercase tracking-wide mb-1">Historical VaR</div>
                <div className="text-2xl font-bold text-white font-mono">{fmtUSD(result.historicalVaR)}</div>
                <div className="mt-1 text-[10px] text-emerald-200/70">CVaR {fmtUSD(result.historicalCVaR)}</div>
              </div>
            </div>

            {result.fatTailGap !== null && result.fatTailGap > 0.2 && (
              <div className="rounded-lg border border-amber-500/40 bg-amber-500/10 p-4 mb-5">
                <p className="text-sm font-semibold text-amber-300">Fat-tail gap detected</p>
                <p className="mt-1 text-xs text-amber-200/80 leading-relaxed">
                  Historical VaR is {fmtPct(result.fatTailGap, 0)} larger than parametric VaR. This
                  gap is itself the finding: the return series has fatter tails than a normal
                  distribution assumes, so the parametric number is understating real risk. Weight
                  the historical estimate more heavily here.
                </p>
              </div>
            )}

            {result.smallSampleWarning && (
              <div className="rounded-lg border border-red-500/40 bg-red-500/10 p-4 mb-5">
                <p className="text-sm font-semibold text-red-300">Small sample ({result.n} periods)</p>
                <p className="mt-1 text-xs text-red-200/80 leading-relaxed">
                  {result.sparseTailWarning
                    ? `At ${((1 - CONFIDENCE_OPTIONS.find((c) => c.value === confidence)!.value) * 100).toFixed(0)}% tail size, only ${result.expectedTailCount.toFixed(2)} observations are expected in the tail — the historical VaR/CVaR below is extrapolated from essentially a single worst observation, not a real percentile.`
                    : 'The historical VaR/CVaR below is estimated from a limited number of tail observations and will be noisy. More data narrows it.'}
                </p>
              </div>
            )}

            <dl className="space-y-3 mb-5">
              <Stat label="Mean return / period" value={fmtPct(result.meanPerPeriod)} />
              <Stat label="Std. dev. / period" value={fmtPct(result.stdevPerPeriod)} />
              <Stat label="z (confidence quantile)" value={result.z.toFixed(4)} />
              <Stat label="Historical threshold return" value={fmtPct(result.historicalThresholdReturn)} sub={`Q at ${((1 - confidence) * 100).toFixed(0)}%`} />
              <Stat label="Expected tail observations" value={result.expectedTailCount.toFixed(2)} sub="n × (1 − c)" />
              <Stat label="Actual tail observations used" value={String(result.actualTailCount)} sub="for historical CVaR" />
            </dl>

            <h3 className="text-xs font-semibold text-[hsl(215,20%,60%)] uppercase tracking-wide mb-2">VaR vs. CVaR by method</h3>
            <ResponsiveContainer width="100%" height={200}>
              <ComposedChart data={chartData} margin={{ top: 8, right: 12, bottom: 8, left: 8 }}>
                <CartesianGrid strokeDasharray="3 3" stroke="#334155" />
                <XAxis dataKey="method" stroke="#94a3b8" tick={{ fontSize: 11 }} />
                <YAxis stroke="#94a3b8" tick={{ fontSize: 11 }} width={70} tickFormatter={(v: number) => fmtUSD(v)} />
                <Tooltip
                  contentStyle={{ backgroundColor: '#1e293b', border: '1px solid #334155', borderRadius: '8px' }}
                  formatter={(value: number, name: string) => [fmtUSD(value), name]}
                />
                <ReferenceLine y={0} stroke="#475569" />
                <Bar dataKey="VaR" fill="#818cf8" radius={[4, 4, 0, 0]} />
                <Bar dataKey="CVaR" fill="#f472b6" radius={[4, 4, 0, 0]} />
              </ComposedChart>
            </ResponsiveContainer>
            <p className="mt-2 text-xs text-[hsl(215,20%,45%)] leading-relaxed">
              CVaR (Expected Shortfall) is always at least as large as VaR — it is the average loss
              in the scenarios where the VaR threshold is already breached, not just the threshold
              itself.
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
