'use client'

/**
 * Charts — the interactive half.
 *
 * Every price, overlay and statistic on this page comes from public/data/prices.json,
 * fetched at runtime (the file is ~370 KB and stays out of the bundle). There is no
 * fallback series: if the artefact does not load, or the requested symbol is not in it,
 * the page says so and draws nothing. The page previously generated a random walk when
 * the API returned nothing and labelled it in 11px grey; that is what this replaces.
 *
 * The bars are adjusted end-of-day closes, not a live feed. Nothing here is a signal or
 * a recommendation.
 */

import { useCallback, useEffect, useMemo, useState } from 'react'
import Link from 'next/link'
import { useSearchParams } from 'next/navigation'
import { PriceChart, type Overlay } from './PriceChart'
import { bollinger, ema, sma } from './indicators'
import { fetchArtefact, type Bar, type PriceArtefact } from './artefact'
import { RANGES, rangeAvailability, windowStartIndex, type RangeKey } from './range'

type IndicatorKey = 'sma20' | 'sma50' | 'ema20' | 'bb20'

const INDICATORS: { key: IndicatorKey; label: string; period: number; color: string }[] = [
  { key: 'sma20', label: 'SMA 20', period: 20, color: '#fbbf24' },
  { key: 'sma50', label: 'SMA 50', period: 50, color: '#38bdf8' },
  { key: 'ema20', label: 'EMA 20', period: 20, color: '#a78bfa' },
  { key: 'bb20', label: 'Bollinger 20 · 2σ', period: 20, color: '#94a3b8' },
]

function fmtMoney(v: number): string {
  return v.toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 })
}

function fmtVolume(v: number): string {
  if (v >= 1e9) return `${(v / 1e9).toFixed(2)}B`
  if (v >= 1e6) return `${(v / 1e6).toFixed(2)}M`
  if (v >= 1e3) return `${(v / 1e3).toFixed(1)}K`
  return v.toFixed(0)
}

function fmtGeneratedAt(raw: string): string {
  if (!raw) return 'an unrecorded time'
  const t = new Date(raw)
  if (Number.isNaN(t.getTime())) return raw
  return `${t.toISOString().slice(0, 10)} ${t.toISOString().slice(11, 16)} UTC`
}

function StatTile({
  label,
  value,
  sub,
  tone = 'text-white',
}: {
  label: string
  value: string
  sub?: string
  tone?: string
}) {
  return (
    <div className="terminal-panel p-4">
      <p className="text-[11px] text-slate-400 uppercase tracking-wider mb-1">{label}</p>
      <p className={`text-lg font-bold font-mono ${tone}`}>{value}</p>
      {sub && <p className="text-[11px] text-slate-400 mt-1">{sub}</p>}
    </div>
  )
}

export function ChartsClient() {
  const searchParams = useSearchParams()
  const requested = searchParams.get('symbol')?.toUpperCase() ?? null

  const [artefact, setArtefact] = useState<PriceArtefact | null>(null)
  const [status, setStatus] = useState<'loading' | 'ready' | 'error'>('loading')
  const [attempt, setAttempt] = useState(0)

  const [symbol, setSymbol] = useState<string | null>(null)
  const [range, setRange] = useState<RangeKey>('1Y')
  const [active, setActive] = useState<Record<IndicatorKey, boolean>>({
    sma20: true,
    sma50: false,
    ema20: false,
    bb20: false,
  })

  useEffect(() => {
    const controller = new AbortController()
    let live = true
    setStatus('loading')

    fetchArtefact(controller.signal)
      .then((data) => {
        if (!live) return
        if (!data) {
          setArtefact(null)
          setStatus('error')
          return
        }
        setArtefact(data)
        setStatus('ready')
        setSymbol((current) => {
          if (current && data.symbols.includes(current)) return current
          if (requested && data.symbols.includes(requested)) return requested
          return data.symbols[0]
        })
      })
      .catch(() => {
        if (!live || controller.signal.aborted) return
        setArtefact(null)
        setStatus('error')
      })

    return () => {
      live = false
      controller.abort()
    }
  }, [attempt, requested])

  const retry = useCallback(() => setAttempt((n) => n + 1), [])

  const bars: Bar[] = useMemo(() => {
    if (!artefact || !symbol) return []
    return artefact.series[symbol] ?? []
  }, [artefact, symbol])

  const firstDate = bars.length ? bars[0][0] : null
  const lastDate = bars.length ? bars[bars.length - 1][0] : null

  // A range is offered only when the history actually spans it. Showing "3Y" over two
  // years of bars would misdescribe the window the viewer is looking at.
  const availability = useMemo(
    () => rangeAvailability(firstDate, lastDate),
    [firstDate, lastDate],
  )

  const effectiveRange: RangeKey = availability[range] ? range : 'ALL'

  const startIndex = useMemo(
    () => windowStartIndex(bars.map((b) => b[0]), effectiveRange),
    [bars, effectiveRange],
  )

  const visible = useMemo(() => bars.slice(startIndex), [bars, startIndex])

  // Overlays are computed across the whole history and then sliced to the visible window,
  // so a 50-day average inside a one-month view rests on the 50 real closes before it.
  const overlays: Overlay[] = useMemo(() => {
    if (!bars.length) return []
    const closes = bars.map((b) => b[4])
    const out: Overlay[] = []

    if (active.sma20) {
      const v = sma(closes, 20)
      if (v) out.push({ name: 'SMA 20', color: '#fbbf24', values: v.slice(startIndex) })
    }
    if (active.sma50) {
      const v = sma(closes, 50)
      if (v) out.push({ name: 'SMA 50', color: '#38bdf8', values: v.slice(startIndex) })
    }
    if (active.ema20) {
      const v = ema(closes, 20)
      if (v) out.push({ name: 'EMA 20', color: '#a78bfa', values: v.slice(startIndex) })
    }
    if (active.bb20) {
      const b = bollinger(closes, 20, 2)
      if (b) {
        out.push({ name: 'BB upper', color: '#94a3b8', values: b.upper.slice(startIndex), dashed: true })
        out.push({ name: 'BB lower', color: '#94a3b8', values: b.lower.slice(startIndex), dashed: true })
      }
    }
    return out
  }, [active, bars, startIndex])

  const rangeStats = useMemo(() => {
    if (!visible.length) return null
    let high = visible[0][2]
    let low = visible[0][3]
    let volume = 0
    for (const b of visible) {
      if (b[2] > high) high = b[2]
      if (b[3] < low) low = b[3]
      volume += b[5]
    }
    const firstClose = visible[0][4]
    const lastClose = visible[visible.length - 1][4]
    return {
      high,
      low,
      avgVolume: volume / visible.length,
      returnPct: firstClose === 0 ? null : ((lastClose - firstClose) / firstClose) * 100,
      from: visible[0][0],
      to: visible[visible.length - 1][0],
    }
  }, [visible])

  const quote = symbol && artefact ? (artefact.latest[symbol] ?? null) : null
  const lastBar = bars.length ? bars[bars.length - 1] : null

  if (status === 'loading') {
    return (
      <div className="glass-card p-16 text-center">
        <div className="w-6 h-6 mx-auto mb-4 border-2 border-amber-500/30 border-t-amber-400 rounded-full animate-spin" />
        <p className="text-slate-400">Loading the end-of-day price artefact…</p>
      </div>
    )
  }

  if (status === 'error' || !artefact || !symbol) {
    return (
      <div className="glass-card p-10 border border-red-500/30">
        <h2 className="text-2xl font-bold mb-2">Price history is not available</h2>
        <p className="text-slate-400 max-w-2xl">
          The price artefact (<code className="text-slate-300">/data/prices.json</code>) did not
          load, or did not parse into a usable series. No chart is shown because there are no
          prices to chart — this page will not draw a simulated series in place of missing data.
        </p>
        <div className="mt-6 flex flex-wrap gap-3">
          <button onClick={retry} className="btn-primary">
            Try again
          </button>
          <Link href="/scanner" className="btn-secondary">
            Seasonality screener
          </Link>
        </div>
      </div>
    )
  }

  const requestedMissing = requested !== null && !artefact.symbols.includes(requested)

  return (
    <div className="space-y-6">
      {requestedMissing && (
        <div className="glass-card p-5 border border-amber-500/30">
          <h2 className="font-bold mb-1">{requested} is not in this dataset</h2>
          <p className="text-sm text-slate-400">
            The published price artefact covers {artefact.symbols.length} symbols and no others.
            Rather than show you an empty or invented chart for {requested}, the page is showing{' '}
            {symbol}. Pick any covered symbol below.
          </p>
        </div>
      )}

      {/* Controls */}
      <div className="glass-card p-5 space-y-5">
        <div>
          <label className="block text-[11px] font-semibold text-slate-400 uppercase tracking-wider mb-2">
            Symbol — {artefact.symbols.length} covered by the artefact
          </label>
          <div className="flex flex-wrap gap-2">
            {artefact.symbols.map((s) => (
              <button
                key={s}
                onClick={() => setSymbol(s)}
                className={`px-3 py-1.5 rounded text-sm font-mono font-medium transition-colors ${
                  s === symbol
                    ? 'bg-[hsl(45,96%,58%)] text-[hsl(220,60%,8%)]'
                    : 'bg-slate-800/50 text-slate-400 hover:bg-slate-700/50 hover:text-white'
                }`}
              >
                {s}
              </button>
            ))}
          </div>
        </div>

        <div className="flex flex-col md:flex-row md:items-end gap-5">
          <div>
            <label className="block text-[11px] font-semibold text-slate-400 uppercase tracking-wider mb-2">
              Range
            </label>
            <div className="flex gap-2">
              {RANGES.map((r) => {
                const usable = availability[r.key]
                return (
                  <button
                    key={r.key}
                    onClick={() => usable && setRange(r.key)}
                    disabled={!usable}
                    title={
                      usable
                        ? undefined
                        : `The history for ${symbol} starts ${firstDate ?? 'unknown'} and does not span ${r.label}`
                    }
                    className={`px-3 py-1.5 rounded text-sm font-medium transition-colors ${
                      r.key === effectiveRange
                        ? 'bg-[hsl(45,96%,58%)] text-[hsl(220,60%,8%)]'
                        : usable
                          ? 'bg-slate-800/50 text-slate-400 hover:bg-slate-700/50 hover:text-white'
                          : 'bg-slate-900/40 text-slate-600 cursor-not-allowed line-through'
                    }`}
                  >
                    {r.label}
                  </button>
                )
              })}
            </div>
          </div>

          <div className="flex-1">
            <label className="block text-[11px] font-semibold text-slate-400 uppercase tracking-wider mb-2">
              Overlays — computed from these closes
            </label>
            <div className="flex flex-wrap gap-2">
              {INDICATORS.map((ind) => {
                const usable = bars.length >= ind.period
                const on = active[ind.key] && usable
                return (
                  <button
                    key={ind.key}
                    onClick={() => usable && setActive((p) => ({ ...p, [ind.key]: !p[ind.key] }))}
                    disabled={!usable}
                    title={
                      usable
                        ? undefined
                        : `${symbol} has ${bars.length} bars; a ${ind.period}-bar window cannot be computed`
                    }
                    className={`px-3 py-1.5 rounded text-sm font-medium border transition-colors flex items-center gap-2 ${
                      on
                        ? 'bg-slate-800 text-white border-slate-600'
                        : usable
                          ? 'bg-slate-900/40 text-slate-400 border-slate-800 hover:text-slate-300'
                          : 'bg-slate-900/40 text-slate-700 border-slate-800 cursor-not-allowed'
                    }`}
                  >
                    <span
                      className="w-2 h-2 rounded-full"
                      style={{ backgroundColor: on ? ind.color : '#334155' }}
                    />
                    {ind.label}
                  </button>
                )
              })}
            </div>
          </div>
        </div>
      </div>

      {/* Chart */}
      {visible.length ? (
        <div className="terminal-panel overflow-hidden">
          <div className="terminal-panel-header">
            <span>
              {symbol} · daily OHLC &amp; volume · {visible.length} bars · {rangeStats?.from} →{' '}
              {rangeStats?.to}
            </span>
            <span className="text-slate-400 normal-case tracking-normal">
              {artefact.adjusted ? 'Adjusted' : 'Unadjusted'} end-of-day
            </span>
          </div>
          <PriceChart symbol={symbol} bars={visible} overlays={overlays} />
        </div>
      ) : (
        <div className="glass-card p-10 border border-red-500/30">
          <h2 className="text-xl font-bold mb-2">No bars for {symbol} in this range</h2>
          <p className="text-slate-400">
            The artefact carries no rows for this selection. Nothing is drawn in their place.
          </p>
        </div>
      )}

      {/* Statistics — all measured, none defaulted */}
      <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-3">
        {quote ? (
          <>
            <StatTile label="Last close" value={`$${fmtMoney(quote.close)}`} sub={quote.day} />
            <StatTile
              label="Change"
              value={`${quote.change >= 0 ? '+' : ''}${fmtMoney(quote.change)}`}
              sub="vs prior close"
              tone={quote.change >= 0 ? 'text-emerald-400' : 'text-red-400'}
            />
            <StatTile
              label="Change %"
              value={`${quote.change_pct >= 0 ? '+' : ''}${quote.change_pct.toFixed(2)}%`}
              sub="vs prior close"
              tone={quote.change_pct >= 0 ? 'text-emerald-400' : 'text-red-400'}
            />
          </>
        ) : lastBar ? (
          <StatTile
            label="Last close"
            value={`$${fmtMoney(lastBar[4])}`}
            sub={`${lastBar[0]} · no change field published`}
          />
        ) : null}

        {rangeStats && (
          <>
            <StatTile
              label={`${effectiveRange === 'ALL' ? 'Full history' : effectiveRange} return`}
              value={
                rangeStats.returnPct === null
                  ? 'not computable'
                  : `${rangeStats.returnPct >= 0 ? '+' : ''}${rangeStats.returnPct.toFixed(2)}%`
              }
              sub={`${rangeStats.from} → ${rangeStats.to}`}
              tone={
                rangeStats.returnPct === null
                  ? 'text-slate-500'
                  : rangeStats.returnPct >= 0
                    ? 'text-emerald-400'
                    : 'text-red-400'
              }
            />
            <StatTile
              label="Range high / low"
              value={`${fmtMoney(rangeStats.high)} / ${fmtMoney(rangeStats.low)}`}
              sub="intraday extremes in window"
            />
            <StatTile
              label="Avg daily volume"
              value={fmtVolume(rangeStats.avgVolume)}
              sub={`mean of ${visible.length} sessions`}
            />
          </>
        )}
      </div>

      {/* Provenance */}
      <div className="glass-card p-6 space-y-3 text-sm text-slate-400 max-w-4xl">
        <h2 className="text-lg font-bold text-white">Where these prices come from</h2>
        <p>
          {artefact.adjusted ? 'Split- and dividend-adjusted' : 'Unadjusted'} end-of-day bars from{' '}
          <strong className="text-slate-200">{artefact.provider.toUpperCase()}</strong>, published
          as a static artefact by the compute plane and generated{' '}
          <strong className="text-slate-200">{fmtGeneratedAt(artefact.generated_at)}</strong>.{' '}
          {symbol} carries {bars.length} sessions{firstDate && lastDate ? `, ${firstDate} to ${lastDate}` : ''}
          {artefact.years !== null ? ` (${artefact.years}-year window)` : ''}.
        </p>
        <p>
          <strong className="text-slate-200">This is not a live feed.</strong> The last candle is
          the most recent completed session in the artefact, not today&apos;s market. Nothing
          updates intraday, and the change figures above are the artefact&apos;s own
          close-to-close numbers.
        </p>
        <p>
          Overlays are computed here from these closes. A window longer than the available history
          is not drawn at all rather than padded, and any bar before an overlay&apos;s window is
          filled shows a gap in the line. Symbols outside the {artefact.symbols.length} listed above
          are not offered, because there is no history for them to draw.
        </p>
        <p className="text-xs pt-2 border-t border-slate-800">
          The correlation matrix, volatility series, drawdown series, risk gauges and technical
          radar that once shared this page were removed: they had no data source and their numbers
          were generated. They return only if they are computed from real history. We compute and
          display; we never recommend — see the{' '}
          <Link href="/disclaimer" className="underline hover:text-slate-200">
            disclaimer
          </Link>
          .
        </p>
      </div>
    </div>
  )
}
