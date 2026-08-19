'use client'

import { useMemo, useState } from 'react'
import {
  ComposedChart,
  Line,
  Area,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
  ReferenceLine,
} from 'recharts'
import {
  blackScholes,
  breakEvenAtExpiry,
  isInTheMoney,
  validateInputs,
  type BlackScholesInputs,
  type OptionType,
} from './blackScholes'

// Every number on this page is closed-form Black-Scholes arithmetic over the
// inputs in the form above it. There is no options data feed behind this page,
// so it must never display a chain, a quote, or an implied volatility as if it
// were observed from the market.

const DAYS_PER_YEAR = 365

function fmt(n: number, dp: number): string {
  if (!Number.isFinite(n)) return '—'
  return n.toLocaleString('en-US', { minimumFractionDigits: dp, maximumFractionDigits: dp })
}

function fmtUSD(n: number, dp = 2): string {
  if (!Number.isFinite(n)) return '—'
  return n.toLocaleString('en-US', {
    style: 'currency',
    currency: 'USD',
    minimumFractionDigits: dp,
    maximumFractionDigits: dp,
  })
}

/** Empty or non-numeric input yields NaN, which validation rejects downstream. */
function parseInput(v: string): number {
  if (v.trim() === '') return NaN
  const n = Number(v)
  return Number.isFinite(n) ? n : NaN
}

type NumField = {
  key: string
  label: string
  unit: string
  value: string
  set: (v: string) => void
  step: number
  hint: string
}

export default function OptionsCalculator() {
  const [spot, setSpot] = useState('100')
  const [strike, setStrike] = useState('100')
  const [days, setDays] = useState('30')
  const [vol, setVol] = useState('25')
  const [rate, setRate] = useState('5')
  const [type, setType] = useState<OptionType>('call')

  const model = useMemo(() => {
    const S = parseInput(spot)
    const K = parseInput(strike)
    const D = parseInput(days)
    const volPct = parseInput(vol)
    const ratePct = parseInput(rate)

    const inputs: BlackScholesInputs = {
      S,
      K,
      T: D / DAYS_PER_YEAR,
      r: ratePct / 100,
      sigma: volPct / 100,
      type,
    }

    const error = validateInputs(inputs)
    const result = error === null ? blackScholes(inputs) : null
    return { inputs, error, result, S, K, D }
  }, [spot, strike, days, vol, rate, type])

  const { inputs, error, result, S, K } = model

  // Payoff and value curves are only meaningful once the model has a price.
  const curves = useMemo(() => {
    if (!result) return []
    const lo = Math.max(0.01, Math.min(S, K) * 0.5)
    // The lower bound is clamped, so the upper bound is forced above it to keep
    // the sweep ascending when both spot and strike are very small.
    const hi = Math.max(Math.max(S, K) * 1.5, lo * 1.5)
    const steps = 80
    const stride = (hi - lo) / steps
    const rows: { price: number; payoff: number; value: number }[] = []

    for (let n = 0; n <= steps; n++) {
      const p = lo + n * stride
      const intrinsic = type === 'call' ? Math.max(0, p - K) : Math.max(0, K - p)
      const now = blackScholes({ ...inputs, S: p })
      rows.push({
        price: Number(p.toFixed(2)),
        // P/L at expiry for one long contract, per share: intrinsic - premium.
        payoff: intrinsic - result.price,
        // P/L today if spot moved to p with time and volatility unchanged.
        value: now ? now.price - result.price : 0,
      })
    }
    return rows
  }, [result, inputs, S, K, type])

  // Greeks as a function of remaining life, holding every other input fixed.
  const decay = useMemo(() => {
    if (!result) return []
    const rows: { days: number; delta: number; gamma: number; theta: number }[] = []
    for (let d = 1; d <= 180; d += 2) {
      const r = blackScholes({ ...inputs, T: d / DAYS_PER_YEAR })
      if (r) rows.push({ days: d, delta: r.delta, gamma: r.gamma, theta: r.thetaPerDay })
    }
    return rows
  }, [result, inputs])

  const fields: NumField[] = [
    { key: 'spot', label: 'Spot price', unit: '$', value: spot, set: setSpot, step: 0.01, hint: 'Current price of the underlying' },
    { key: 'strike', label: 'Strike price', unit: '$', value: strike, set: setStrike, step: 0.01, hint: 'Exercise price of the option' },
    { key: 'days', label: 'Days to expiry', unit: 'days', value: days, set: setDays, step: 1, hint: 'Calendar days, converted to years as days ÷ 365' },
    { key: 'vol', label: 'Volatility', unit: '% p.a.', value: vol, set: setVol, step: 0.1, hint: 'Annualised volatility you want to price at' },
    { key: 'rate', label: 'Risk-free rate', unit: '% p.a.', value: rate, set: setRate, step: 0.1, hint: 'Continuously compounded annual rate' },
  ]

  return (
    <div className="space-y-8">
      {/* Inputs */}
      <div className="glass-strong rounded-xl p-6">
        <h2 className="text-xl font-bold mb-1">Option parameters</h2>
        <p className="text-sm text-muted-foreground mb-5">
          Values you supply. Nothing here is fetched from a market data source.
        </p>
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-6 gap-4">
          {fields.map((f) => (
            <div key={f.key}>
              <label
                htmlFor={`opt-${f.key}`}
                className="text-xs font-semibold text-muted-foreground mb-2 flex items-baseline justify-between gap-2 uppercase tracking-wide"
              >
                <span>{f.label}</span>
                <span className="normal-case text-[hsl(215,20%,45%)] font-normal">{f.unit}</span>
              </label>
              <input
                id={`opt-${f.key}`}
                type="number"
                inputMode="decimal"
                value={f.value}
                onChange={(e) => f.set(e.target.value)}
                className="input-field"
                step={f.step}
              />
              <p className="mt-1 text-[11px] leading-snug text-[hsl(215,20%,45%)]">{f.hint}</p>
            </div>
          ))}

          <div>
            <label
              htmlFor="opt-type"
              className="text-xs font-semibold text-muted-foreground mb-2 flex items-baseline justify-between gap-2 uppercase tracking-wide"
            >
              <span>Option type</span>
            </label>
            <select
              id="opt-type"
              value={type}
              onChange={(e) => setType(e.target.value as OptionType)}
              className="input-field"
            >
              <option value="call">Call</option>
              <option value="put">Put</option>
            </select>
            <p className="mt-1 text-[11px] leading-snug text-[hsl(215,20%,45%)]">European exercise, no dividends</p>
          </div>
        </div>

        {error !== null && (
          <div className="mt-5 rounded-lg border border-amber-500/40 bg-amber-500/10 px-4 py-3">
            <p className="text-sm font-semibold text-amber-300">Cannot price with these inputs</p>
            <p className="text-sm text-amber-200/80 mt-0.5">{error}</p>
          </div>
        )}
      </div>

      {result === null ? (
        <div className="glass-strong rounded-xl p-8 text-center">
          <p className="text-muted-foreground">
            Enter a spot price, strike, expiry, and volatility above to price the option.
          </p>
        </div>
      ) : (
        <>
          {/* Price and Greeks */}
          <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-4">
            <Metric
              label="Theoretical value"
              value={fmtUSD(result.price, 4)}
              sub={`${fmtUSD(result.price * 100, 2)} per 100-share contract`}
              accent="text-emerald-400"
            />
            <Metric
              label="Delta (Δ)"
              value={fmt(result.delta, 4)}
              sub="Value change per $1 of spot"
              accent="text-blue-400"
            />
            <Metric
              label="Gamma (Γ)"
              value={fmt(result.gamma, 4)}
              sub="Delta change per $1 of spot"
              accent="text-purple-400"
            />
            <Metric
              label="Vega (ν)"
              value={fmt(result.vegaPerPoint, 4)}
              sub="Per +1 point of volatility"
              accent="text-cyan-400"
            />
            <Metric
              label="Theta (Θ)"
              value={fmt(result.thetaPerDay, 4)}
              sub="Per calendar day elapsed"
              accent="text-red-400"
            />
            <Metric
              label="Rho (ρ)"
              value={fmt(result.rhoPerPoint, 4)}
              sub="Per +1 point of interest rate"
              accent="text-orange-400"
            />
          </div>

          {/* Decomposition and expiry arithmetic */}
          <div className="glass-strong rounded-xl p-6">
            <h2 className="text-xl font-bold mb-1">Value breakdown</h2>
            <p className="text-sm text-muted-foreground mb-5">
              Per share, for one long {type} bought at the theoretical value above and held to expiry.
            </p>
            <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
              <Cell
                label="Intrinsic value"
                value={fmtUSD(result.intrinsic, 4)}
                sub={type === 'call' ? 'max(spot − strike, 0)' : 'max(strike − spot, 0)'}
              />
              <Cell
                label="Time value"
                value={fmtUSD(result.timeValue, 4)}
                sub="theoretical value − intrinsic"
              />
              <Cell
                label="Break-even at expiry"
                value={fmtUSD(breakEvenAtExpiry(K, result.price, type), 4)}
                sub={type === 'call' ? 'strike + premium' : 'strike − premium'}
              />
              <Cell
                label="Moneyness"
                value={S === K ? 'At the money' : isInTheMoney(S, K, type) ? 'In the money' : 'Out of the money'}
                sub={`spot ${fmtUSD(S)} vs strike ${fmtUSD(K)}`}
              />
              <Cell
                label="Max loss (long)"
                value={fmtUSD(result.price, 4)}
                sub="Premium paid, if it expires worthless"
              />
              <Cell
                label="Max gain (long)"
                value={
                  type === 'call'
                    ? 'Unbounded'
                    : fmtUSD(Math.max(0, K - result.price), 4)
                }
                sub={type === 'call' ? 'Payoff rises with spot without limit' : 'strike − premium, reached if spot goes to 0'}
              />
              <Cell label="d₁" value={fmt(result.d1, 4)} sub="Black-Scholes intermediate term" />
              <Cell label="d₂" value={fmt(result.d2, 4)} sub="d₁ − σ√T" />
            </div>
          </div>

          {/* Payoff */}
          <div className="glass-strong rounded-xl p-6">
            <h2 className="text-xl font-bold mb-1">Profit and loss vs spot price</h2>
            <p className="text-sm text-muted-foreground mb-5">
              One long {type}, per share. <span className="text-slate-300">At expiry</span> is
              intrinsic value minus the premium. <span className="text-slate-300">Today</span> is
              the Black-Scholes value at that spot minus the premium, holding days to expiry,
              volatility, and rate at the values entered above.
            </p>
            <ResponsiveContainer width="100%" height={380}>
              <ComposedChart data={curves} margin={{ top: 8, right: 16, bottom: 24, left: 8 }}>
                <CartesianGrid strokeDasharray="3 3" stroke="#334155" />
                <XAxis
                  dataKey="price"
                  type="number"
                  domain={['dataMin', 'dataMax']}
                  stroke="#94a3b8"
                  tick={{ fontSize: 12 }}
                  label={{ value: 'Spot price ($)', position: 'bottom', fill: '#94a3b8' }}
                />
                <YAxis
                  stroke="#94a3b8"
                  tick={{ fontSize: 12 }}
                  label={{ value: 'P/L per share ($)', angle: -90, position: 'insideLeft', fill: '#94a3b8' }}
                />
                <Tooltip
                  contentStyle={{ backgroundColor: '#1e293b', border: '1px solid #334155', borderRadius: '8px' }}
                  labelFormatter={(v) => `Spot $${v}`}
                  formatter={(value: number | string) =>
                    typeof value === 'number' ? fmtUSD(value) : String(value)
                  }
                />
                <Legend verticalAlign="top" height={30} />
                <ReferenceLine y={0} stroke="#6b7280" strokeDasharray="3 3" />
                <ReferenceLine x={Number(K.toFixed(2))} stroke="#f59e0b" strokeDasharray="3 3" label={{ value: 'Strike', fill: '#f59e0b', fontSize: 11 }} />
                <Area
                  type="monotone"
                  dataKey="payoff"
                  stroke="#10b981"
                  fill="#10b981"
                  fillOpacity={0.2}
                  name="P/L at expiry"
                />
                <Line
                  type="monotone"
                  dataKey="value"
                  stroke="#60a5fa"
                  strokeWidth={2}
                  dot={false}
                  name="P/L today"
                />
              </ComposedChart>
            </ResponsiveContainer>
          </div>

          {/* Greeks vs remaining life */}
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            <GreekChart
              title="Delta vs days to expiry"
              caption="Black-Scholes delta recomputed at each expiry, with spot, strike, volatility, and rate unchanged."
              data={decay}
              dataKey="delta"
              color="#3b82f6"
              currentDays={model.D}
            />
            <GreekChart
              title="Gamma vs days to expiry"
              caption="Black-Scholes gamma recomputed at each expiry, with spot, strike, volatility, and rate unchanged."
              data={decay}
              dataKey="gamma"
              color="#8b5cf6"
              currentDays={model.D}
            />
          </div>

          {/* Formula */}
          <div className="glass-strong rounded-xl p-6">
            <h2 className="text-xl font-bold mb-4">The formula used</h2>
            <div className="font-mono text-sm text-slate-300 space-y-1.5 overflow-x-auto">
              <p>d₁ = [ ln(S / K) + (r + σ² / 2) · T ] / (σ · √T)</p>
              <p>d₂ = d₁ − σ · √T</p>
              <p>Call = S · N(d₁) − K · e^(−rT) · N(d₂)</p>
              <p>Put&nbsp; = K · e^(−rT) · N(−d₂) − S · N(−d₁)</p>
              <p className="pt-2">Δ = N(d₁) for a call, N(d₁) − 1 for a put</p>
              <p>Γ = φ(d₁) / (S · σ · √T)</p>
              <p>ν = S · φ(d₁) · √T&nbsp;&nbsp;(shown ÷ 100, per 1 volatility point)</p>
              <p>Θ = −S · φ(d₁) · σ / (2√T) ∓ r · K · e^(−rT) · N(±d₂)&nbsp;&nbsp;(shown ÷ 365, per day)</p>
              <p>ρ = ± K · T · e^(−rT) · N(±d₂)&nbsp;&nbsp;(shown ÷ 100, per 1 rate point)</p>
            </div>
            <p className="mt-4 text-sm text-muted-foreground leading-relaxed">
              S is spot, K is strike, T is time to expiry in years (days ÷ 365), r is the
              continuously compounded risk-free rate, σ is annualised volatility, N is the standard
              normal cumulative distribution function and φ its density. The upper sign applies to
              calls, the lower to puts.
            </p>
            <p className="mt-3 text-sm text-muted-foreground leading-relaxed">
              At S = 100, K = 100, r = 5%, σ = 20%, T = 1 year this returns a call value of
              $10.4506 and a put value of $5.5735, the standard published reference values for
              those inputs. Call and put outputs satisfy put-call parity,
              C − P = S − K·e^(−rT), to floating-point precision.
            </p>
            <p className="mt-3 text-sm text-muted-foreground leading-relaxed">
              This is the European, no-dividend Black-Scholes model. It assumes constant volatility
              and interest rates and no early exercise, so it will not match the traded price of an
              American option, an option on a dividend-paying underlying, or any option whose market
              volatility differs from the figure entered above. All figures are per share; a
              standard US equity contract covers 100 shares.
            </p>
          </div>
        </>
      )}
    </div>
  )
}

function Metric({
  label,
  value,
  sub,
  accent,
}: {
  label: string
  value: string
  sub: string
  accent: string
}) {
  return (
    <div className="glass-strong rounded-xl p-5">
      <p className="text-xs text-muted-foreground mb-1 uppercase tracking-wide">{label}</p>
      <p className={`text-2xl font-bold font-mono ${accent}`}>{value}</p>
      <p className="text-xs text-[hsl(215,20%,45%)] mt-1 leading-snug">{sub}</p>
    </div>
  )
}

function Cell({ label, value, sub }: { label: string; value: string; sub: string }) {
  return (
    <div className="glass rounded-lg p-4">
      <p className="text-xs text-muted-foreground mb-1">{label}</p>
      <p className="text-lg font-bold font-mono text-slate-100">{value}</p>
      <p className="text-xs text-[hsl(215,20%,45%)] mt-1 leading-snug">{sub}</p>
    </div>
  )
}

function GreekChart({
  title,
  caption,
  data,
  dataKey,
  color,
  currentDays,
}: {
  title: string
  caption: string
  data: { days: number; delta: number; gamma: number; theta: number }[]
  dataKey: 'delta' | 'gamma' | 'theta'
  color: string
  currentDays: number
}) {
  return (
    <div className="glass-strong rounded-xl p-6">
      <h2 className="text-lg font-bold mb-1">{title}</h2>
      <p className="text-sm text-muted-foreground mb-4">{caption}</p>
      <ResponsiveContainer width="100%" height={280}>
        <ComposedChart data={data} margin={{ top: 8, right: 16, bottom: 24, left: 8 }}>
          <CartesianGrid strokeDasharray="3 3" stroke="#334155" />
          <XAxis
            dataKey="days"
            type="number"
            domain={['dataMin', 'dataMax']}
            stroke="#94a3b8"
            tick={{ fontSize: 12 }}
            label={{ value: 'Days to expiry', position: 'bottom', fill: '#94a3b8' }}
          />
          <YAxis stroke="#94a3b8" tick={{ fontSize: 12 }} width={70} />
          <Tooltip
            contentStyle={{ backgroundColor: '#1e293b', border: '1px solid #334155', borderRadius: '8px' }}
            labelFormatter={(v) => `${v} days to expiry`}
            formatter={(value: number | string) =>
              typeof value === 'number' ? value.toFixed(4) : String(value)
            }
          />
          {Number.isFinite(currentDays) && currentDays > 0 && currentDays <= 180 && (
            <ReferenceLine
              x={Math.round(currentDays)}
              stroke="#94a3b8"
              strokeDasharray="3 3"
              label={{ value: 'Entered', fill: '#94a3b8', fontSize: 11 }}
            />
          )}
          <Area type="monotone" dataKey={dataKey} stroke={color} fill={color} fillOpacity={0.25} name={dataKey} />
        </ComposedChart>
      </ResponsiveContainer>
    </div>
  )
}
