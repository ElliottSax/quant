'use client'

import { useMemo, useState } from 'react'
import { maxSharpe } from './maxSharpe'

/**
 * Interactive tangency-portfolio solver. Pure arithmetic on the inputs — no market data,
 * so every number on screen can be checked by hand against the formula shown below it.
 */

const NAMES = ['Asset 1', 'Asset 2', 'Asset 3', 'Asset 4', 'Asset 5']
const CARD = 'rounded-xl border border-[hsl(215,40%,18%)] bg-[hsl(220,55%,9%)] p-6'
const CELL =
  'w-full rounded-md border border-[hsl(215,40%,18%)] bg-[hsl(220,55%,7%)] px-2 py-1.5 ' +
  'text-right font-mono text-sm text-slate-200 focus:border-indigo-500 focus:outline-none'

const pct = (x: number, dp = 2) => `${(x * 100).toFixed(dp)}%`

export default function MaxSharpeClient() {
  const [n, setN] = useState(3)
  const [rf, setRf] = useState('2')
  const [mu, setMu] = useState(['10', '12', '8', '9', '7'])
  const [vol, setVol] = useState(['15', '20', '10', '18', '12'])
  const [corr, setCorr] = useState<string[][]>(() =>
    Array.from({ length: 5 }, (_, i) =>
      Array.from({ length: 5 }, (_, j) =>
        i === j ? '1' : i + j === 1 ? '0.3' : i + j === 2 ? '0.1' : '0.2'
      )
    )
  )

  // Correlation matrices are symmetric, so editing one cell edits its mirror.
  const setCorrCell = (i: number, j: number, v: string) =>
    setCorr((prev) => {
      const next = prev.map((r) => [...r])
      next[i][j] = v
      next[j][i] = v
      return next
    })

  const { result, invalid } = useMemo(() => {
    const muV = mu.slice(0, n).map((x) => Number(x) / 100)
    const volV = vol.slice(0, n).map((x) => Number(x) / 100)
    const corrV = corr.slice(0, n).map((r) => r.slice(0, n).map(Number))
    const all = [...muV, ...volV, ...corrV.flat(), Number(rf)]
    if (all.some((v) => !Number.isFinite(v))) {
      return { result: null, invalid: 'Every field needs a number.' }
    }
    if (volV.some((v) => !(v > 0))) {
      return { result: null, invalid: 'Volatilities must be greater than zero.' }
    }
    if (corrV.some((r) => r.some((c) => c < -1 || c > 1))) {
      return { result: null, invalid: 'Correlations must be between −1 and 1.' }
    }
    return { result: maxSharpe({ mu: muV, vol: volV, corr: corrV, rf: Number(rf) / 100 }), invalid: null }
  }, [n, rf, mu, vol, corr])

  return (
    <div className="space-y-6">
      <div className="grid gap-6 lg:grid-cols-2">
        {/* ---------------- Inputs ---------------- */}
        <div className={CARD}>
          <div className="flex items-end justify-between gap-4 mb-5">
            <h2 className="text-lg font-semibold text-white">Assumptions</h2>
            <label className="text-xs">
              <span className="block font-semibold uppercase tracking-wide text-[hsl(215,20%,60%)] mb-1.5">
                Assets
              </span>
              <select
                value={n}
                onChange={(e) => setN(Number(e.target.value))}
                className="rounded-md border border-[hsl(215,40%,18%)] bg-[hsl(220,55%,7%)] px-3 py-1.5 text-sm text-slate-200"
              >
                {[2, 3, 4, 5].map((k) => (
                  <option key={k} value={k}>{k}</option>
                ))}
              </select>
            </label>
          </div>

          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead>
                <tr className="text-xs font-semibold uppercase tracking-wide text-[hsl(215,20%,60%)]">
                  <th className="pb-2 text-left font-semibold">Asset</th>
                  <th className="pb-2 pl-3 text-right font-semibold">Return %</th>
                  <th className="pb-2 pl-3 text-right font-semibold">Volatility %</th>
                </tr>
              </thead>
              <tbody>
                {Array.from({ length: n }, (_, i) => (
                  <tr key={i}>
                    <td className="py-1 pr-3 whitespace-nowrap text-slate-300">{NAMES[i]}</td>
                    <td className="py-1 pl-3 w-28">
                      <input
                        aria-label={`${NAMES[i]} expected return, percent`}
                        value={mu[i]}
                        inputMode="decimal"
                        onChange={(e) => setMu((p) => p.map((v, k) => (k === i ? e.target.value : v)))}
                        className={CELL}
                      />
                    </td>
                    <td className="py-1 pl-3 w-28">
                      <input
                        aria-label={`${NAMES[i]} volatility, percent`}
                        value={vol[i]}
                        inputMode="decimal"
                        onChange={(e) => setVol((p) => p.map((v, k) => (k === i ? e.target.value : v)))}
                        className={CELL}
                      />
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>

          <div className="mt-5 border-t border-[hsl(215,40%,14%)] pt-5">
            <label className="text-xs">
              <span className="block font-semibold uppercase tracking-wide text-[hsl(215,20%,60%)] mb-1.5">
                Risk-free rate %
              </span>
              <input
                value={rf}
                inputMode="decimal"
                onChange={(e) => setRf(e.target.value)}
                className={`${CELL} max-w-[7rem]`}
              />
            </label>
          </div>

          <div className="mt-5 border-t border-[hsl(215,40%,14%)] pt-5">
            <h3 className="text-xs font-semibold uppercase tracking-wide text-[hsl(215,20%,60%)] mb-3">
              Correlation matrix
            </h3>
            <div className="overflow-x-auto">
              <table className="text-sm">
                <tbody>
                  {Array.from({ length: n }, (_, i) => (
                    <tr key={i}>
                      <td className="py-1 pr-3 whitespace-nowrap text-xs text-[hsl(215,20%,55%)]">
                        {NAMES[i]}
                      </td>
                      {Array.from({ length: n }, (_, j) => (
                        <td key={j} className="py-1 pr-2 w-[4.5rem]">
                          <input
                            aria-label={`Correlation between ${NAMES[i]} and ${NAMES[j]}`}
                            value={corr[i][j]}
                            inputMode="decimal"
                            disabled={i === j}
                            onChange={(e) => setCorrCell(i, j, e.target.value)}
                            className={`${CELL} ${i === j ? 'text-[hsl(215,20%,40%)] opacity-60' : ''}`}
                          />
                        </td>
                      ))}
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
            <p className="mt-2 text-xs text-[hsl(215,20%,45%)]">
              Symmetric — editing a cell updates its mirror. The diagonal is fixed at 1.
            </p>
          </div>
        </div>

        {/* ---------------- Results ---------------- */}
        <div className={CARD}>
          <h2 className="text-lg font-semibold text-white mb-5">Tangency portfolio</h2>

          {invalid ? (
            <div className="rounded-lg border border-amber-500/40 bg-amber-500/10 p-5">
              <p className="text-sm font-semibold text-amber-300">Check your inputs</p>
              <p className="mt-1 text-sm text-amber-200/80">{invalid}</p>
            </div>
          ) : !result ? (
            <div className="rounded-lg border border-amber-500/40 bg-amber-500/10 p-5">
              <p className="text-sm font-semibold text-amber-300">No unique solution</p>
              <p className="mt-1 text-sm text-amber-200/80">
                The covariance matrix these inputs describe is singular — usually because two
                assets are perfectly correlated, or because a whole row of the matrix is a
                combination of the others. Infinitely many weight vectors give the same Sharpe
                ratio, so no single answer is shown rather than picking one arbitrarily.
              </p>
            </div>
          ) : (
            <>
              <div className="rounded-lg border border-indigo-500/30 bg-indigo-500/10 p-5 mb-5">
                <div className="text-xs font-semibold uppercase tracking-wide text-indigo-300 mb-1">
                  Sharpe ratio
                </div>
                <div className="font-mono text-4xl font-bold tabular-nums text-white">
                  {result.sharpe.toFixed(4)}
                </div>
                <div className="mt-1 text-xs text-indigo-200/70">
                  ({pct(result.expectedReturn)} − {pct(Number(rf) / 100)}) ÷ {pct(result.volatility)}
                </div>
              </div>

              <table className="w-full text-sm mb-5">
                <thead>
                  <tr className="text-xs font-semibold uppercase tracking-wide text-[hsl(215,20%,60%)] border-b border-[hsl(215,40%,14%)]">
                    <th className="pb-2 text-left font-semibold">Asset</th>
                    <th className="pb-2 text-right font-semibold">Weight</th>
                  </tr>
                </thead>
                <tbody>
                  {result.weights.map((w, i) => (
                    <tr key={i} className="border-b border-[hsl(215,40%,12%)]">
                      <td className="py-2.5 text-slate-300">{NAMES[i]}</td>
                      <td
                        className={`py-2.5 text-right font-mono tabular-nums ${
                          w < 0 ? 'text-amber-400' : 'text-slate-100'
                        }`}
                      >
                        {pct(w)}
                      </td>
                    </tr>
                  ))}
                  <tr>
                    <td className="py-2.5 text-xs uppercase tracking-wide text-[hsl(215,20%,55%)]">
                      Total
                    </td>
                    <td className="py-2.5 text-right font-mono tabular-nums text-[hsl(215,20%,55%)]">
                      100.00%
                    </td>
                  </tr>
                </tbody>
              </table>

              <div className="grid grid-cols-2 gap-3">
                <div className="rounded-lg border border-[hsl(215,40%,14%)] p-4">
                  <div className="font-mono text-xl font-bold tabular-nums text-white">
                    {pct(result.expectedReturn)}
                  </div>
                  <div className="mt-0.5 text-xs text-[hsl(215,20%,55%)]">Expected return</div>
                </div>
                <div className="rounded-lg border border-[hsl(215,40%,14%)] p-4">
                  <div className="font-mono text-xl font-bold tabular-nums text-white">
                    {pct(result.volatility)}
                  </div>
                  <div className="mt-0.5 text-xs text-[hsl(215,20%,55%)]">Volatility</div>
                </div>
              </div>

              {result.hasShorts && (
                <p className="mt-4 rounded-lg border border-amber-500/30 bg-amber-500/5 p-4 text-sm text-amber-200/90">
                  Negative weights are short positions. This closed form has no long-only
                  constraint — clipping the negatives to zero and renormalising gives a different
                  portfolio that is no longer the maximum-Sharpe one. A long-only optimum needs
                  quadratic programming, not this formula.
                </p>
              )}
            </>
          )}
        </div>
      </div>
    </div>
  )
}
