/**
 * Market Dashboard — real quotes and indicators only.
 *
 * This page shipped with a full set of synthetic fallbacks: a hardcoded index
 * table (S&P 5667.56, NASDAQ 17889.23, DOW 42340.78) and Math.sin-generated
 * fear/greed, VIX and yield-curve series, rendered whenever a fetch failed under
 * the message "Market data unavailable - showing cached data". Nothing was ever
 * cached — a failed request was being presented to the reader as market data.
 *
 * Every panel below now renders only values returned by a live source, and says
 * plainly when a source is unavailable. Never reintroduce a fallback series
 * here: an absent panel is honest, an invented one is not.
 */

'use client'

import { useState, useEffect, useCallback, useMemo } from 'react'
import { useQuery } from '@tanstack/react-query'
import {
  LineChart, Line, AreaChart, Area, XAxis, YAxis, CartesianGrid,
  Tooltip, ResponsiveContainer,
} from 'recharts'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { api } from '@/lib/api-client'
import type { MarketQuote, MarketStatus } from '@/lib/types'

// ---------------------------------------------------------------------------
// Types
// ---------------------------------------------------------------------------

interface IndexQuote {
  symbol: string
  name: string
  price: number
  change: number | null
  change_percent: number | null
}

interface FearGreedEntry {
  value: string
  value_classification: string
  timestamp: string
}

interface FredObservation {
  date: string
  value: string
}

/**
 * FRED requires a registered key. Without one the series cannot be fetched, and
 * the two FRED-backed panels are omitted rather than filled with a stand-in.
 */
const FRED_API_KEY = process.env.NEXT_PUBLIC_FRED_API_KEY ?? ''

// ---------------------------------------------------------------------------
// Helpers
// ---------------------------------------------------------------------------

/** Narrow an index-signature field to a finite number, or null if it is not one. */
function toNum(value: unknown): number | null {
  const n = typeof value === 'string' ? Number(value) : value
  return typeof n === 'number' && Number.isFinite(n) ? n : null
}

function fearGreedColor(value: number): string {
  if (value <= 25) return '#ef4444'   // extreme fear - red
  if (value <= 45) return '#f97316'   // fear - orange
  if (value <= 55) return '#eab308'   // neutral - yellow
  if (value <= 75) return '#84cc16'   // greed - lime
  return '#22c55e'                     // extreme greed - green
}

function fearGreedLabel(value: number): string {
  if (value <= 25) return 'Extreme Fear'
  if (value <= 45) return 'Fear'
  if (value <= 55) return 'Neutral'
  if (value <= 75) return 'Greed'
  return 'Extreme Greed'
}

/** Compute time until next US market open/close (ET).  Approximate. */
function getMarketCountdown(isOpen: boolean): string {
  const now = new Date()
  const et = new Date(now.toLocaleString('en-US', { timeZone: 'America/New_York' }))
  const hours = et.getHours()
  const minutes = et.getMinutes()
  const day = et.getDay()

  if (isOpen) {
    // Market closes at 16:00 ET
    const minsLeft = (16 - hours) * 60 - minutes
    if (minsLeft <= 0) return 'Closing soon'
    const h = Math.floor(minsLeft / 60)
    const m = minsLeft % 60
    return `${h}h ${m}m until close`
  }

  // Market opens at 9:30 ET on weekdays
  let daysUntilOpen = 0
  if (day === 0) { daysUntilOpen = 1 }
  else if (day === 6) { daysUntilOpen = 2 }
  else if (hours >= 16) { daysUntilOpen = day === 5 ? 3 : 1 }
  else if (hours < 9 || (hours === 9 && minutes < 30)) { daysUntilOpen = 0 }
  else { daysUntilOpen = 1 }

  const minsUntil = daysUntilOpen > 0
    ? daysUntilOpen * 24 * 60 - (hours * 60 + minutes) + 9 * 60 + 30
    : (9 * 60 + 30) - (hours * 60 + minutes)

  if (minsUntil <= 0) return 'Opens soon'
  const h = Math.floor(minsUntil / 60)
  const m = minsUntil % 60
  if (h >= 24) {
    const d = Math.floor(h / 24)
    return `${d}d ${h % 24}h until open`
  }
  return `${h}h ${m}m until open`
}

// ---------------------------------------------------------------------------
// Data Fetchers — every one of these rejects on failure. A rejected query gives
// the panel below an unavailable state; it must never resolve to stand-in data.
// ---------------------------------------------------------------------------

async function fetchFearGreed(): Promise<FearGreedEntry[]> {
  const res = await fetch('https://api.alternative.me/fng/?limit=30')
  if (!res.ok) throw new Error('Fear & Greed request failed')
  const json = await res.json()
  const data = json?.data
  return Array.isArray(data) ? (data as FearGreedEntry[]) : []
}

async function fetchFredSeries(seriesId: string): Promise<FredObservation[]> {
  const url = `https://api.stlouisfed.org/fred/series/observations?series_id=${seriesId}` +
    `&api_key=${FRED_API_KEY}&file_type=json&sort_order=desc&limit=30`
  const res = await fetch(url)
  if (!res.ok) throw new Error(`FRED request failed for ${seriesId}`)
  const json = await res.json()
  const obs: FredObservation[] = (json?.observations || []).filter(
    (o: FredObservation) => o.value !== '.'
  )
  return obs.reverse()
}

async function fetchMarketStatus(): Promise<MarketStatus> {
  return api.marketData.marketStatus()
}

async function fetchIndices(): Promise<IndexQuote[]> {
  const symbols = ['^GSPC', '^IXIC', '^DJI']
  const names: Record<string, string> = { '^GSPC': 'S&P 500', '^IXIC': 'NASDAQ', '^DJI': 'DOW 30' }
  const result = await api.marketData.quotes(symbols)

  // Symbols the feed did not return are dropped, not back-filled.
  return symbols.flatMap((sym) => {
    const q = result.quotes?.[sym]
    const price = toNum(q?.price)
    if (price === null) return []
    return [{
      symbol: sym,
      name: names[sym],
      price,
      change: toNum(q?.change),
      change_percent: toNum(q?.change_percent ?? q?.changePercent),
    }]
  })
}

async function fetchStockQuote(symbol: string): Promise<MarketQuote> {
  return api.marketData.quote(symbol)
}

// ---------------------------------------------------------------------------
// Sub-Components
// ---------------------------------------------------------------------------

function Unavailable({ children }: { children: React.ReactNode }) {
  return (
    <div className="text-center py-8 text-[hsl(215,20%,45%)] text-sm">
      {children}
    </div>
  )
}

function FearGreedGauge({ value }: { value: number }) {
  const color = fearGreedColor(value)
  const label = fearGreedLabel(value)
  // SVG semicircle gauge
  const angle = (value / 100) * 180 // 0=left, 180=right
  const rad = (angle * Math.PI) / 180
  const needleX = 100 + 70 * Math.cos(Math.PI - rad)
  const needleY = 100 - 70 * Math.sin(Math.PI - rad)

  return (
    <div className="flex flex-col items-center">
      <svg viewBox="0 0 200 120" className="w-64 h-32">
        {/* Background arc segments */}
        <path d="M 20 100 A 80 80 0 0 1 60 34" stroke="#ef4444" strokeWidth="12" fill="none" strokeLinecap="round" />
        <path d="M 60 34 A 80 80 0 0 1 100 20" stroke="#f97316" strokeWidth="12" fill="none" strokeLinecap="round" />
        <path d="M 100 20 A 80 80 0 0 1 140 34" stroke="#eab308" strokeWidth="12" fill="none" strokeLinecap="round" />
        <path d="M 140 34 A 80 80 0 0 1 160 55" stroke="#84cc16" strokeWidth="12" fill="none" strokeLinecap="round" />
        <path d="M 160 55 A 80 80 0 0 1 180 100" stroke="#22c55e" strokeWidth="12" fill="none" strokeLinecap="round" />
        {/* Needle */}
        <line x1="100" y1="100" x2={needleX} y2={needleY} stroke={color} strokeWidth="3" strokeLinecap="round" />
        <circle cx="100" cy="100" r="5" fill={color} />
      </svg>
      <span className="text-4xl font-bold mt-2" style={{ color }}>{value}</span>
      <span className="text-sm font-medium mt-1" style={{ color }}>{label}</span>
    </div>
  )
}

function MarketStatusBar({ status }: { status: MarketStatus }) {
  const isOpen = typeof status.is_open === 'boolean' ? status.is_open : Boolean(status.isOpen)
  const marketName = typeof status.market === 'string' ? status.market : 'US Equity'
  const countdown = getMarketCountdown(isOpen)

  return (
    <div className={`flex flex-wrap items-center justify-between gap-4 px-6 py-3 rounded-lg border ${
      isOpen
        ? 'border-green-500/30 bg-green-500/5'
        : 'border-red-500/30 bg-red-500/5'
    }`}>
      <div className="flex items-center gap-3">
        <span className={`inline-block w-3 h-3 rounded-full ${isOpen ? 'bg-green-500 animate-pulse' : 'bg-red-500'}`} />
        <span className="text-white font-semibold">
          {marketName} Market {isOpen ? 'Open' : 'Closed'}
        </span>
        <Badge className={isOpen ? 'bg-green-600 text-white' : 'bg-red-600 text-white'}>
          {isOpen ? 'TRADING' : 'CLOSED'}
        </Badge>
      </div>
      <span className="text-[hsl(215,20%,60%)] text-sm">{countdown}</span>
    </div>
  )
}

/** Shown when the session endpoint is unreachable. Neither "open" nor "closed"
 *  may be asserted from a failed request. */
function MarketStatusUnknownBar() {
  return (
    <div className="flex flex-wrap items-center gap-3 px-6 py-3 rounded-lg border border-[hsl(215,40%,18%)] bg-[hsl(220,55%,7%)]">
      <span className="inline-block w-3 h-3 rounded-full bg-[hsl(215,20%,35%)]" />
      <span className="text-[hsl(215,20%,60%)] text-sm">
        Session status unavailable — the market-status service did not respond.
      </span>
    </div>
  )
}

function IndexCard({ quote }: { quote: IndexQuote }) {
  const positive = (quote.change ?? 0) >= 0
  return (
    <Card className="border-[hsl(215,40%,18%)] bg-[hsl(220,55%,7%)]">
      <CardHeader className="pb-2">
        <CardTitle className="text-[hsl(215,20%,60%)] text-sm font-medium">{quote.name}</CardTitle>
      </CardHeader>
      <CardContent>
        <div className="text-2xl font-bold text-white">{quote.price.toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 })}</div>
        {quote.change === null && quote.change_percent === null ? (
          <div className="mt-1 text-sm text-[hsl(215,20%,45%)]">Change not reported</div>
        ) : (
          <div className={`flex items-center gap-2 mt-1 text-sm font-medium ${positive ? 'text-green-400' : 'text-red-400'}`}>
            {quote.change !== null && <span>{positive ? '+' : ''}{quote.change.toFixed(2)}</span>}
            {quote.change_percent !== null && (
              <span>({quote.change_percent >= 0 ? '+' : ''}{quote.change_percent.toFixed(2)}%)</span>
            )}
          </div>
        )}
      </CardContent>
    </Card>
  )
}

// ---------------------------------------------------------------------------
// Custom tooltip for recharts (dark theme)
// ---------------------------------------------------------------------------

function DarkTooltip({ active, payload, label }: any) {
  if (!active || !payload?.length) return null
  return (
    <div className="bg-[hsl(220,55%,10%)] border border-[hsl(215,40%,20%)] rounded px-3 py-2 text-xs shadow-lg">
      <p className="text-[hsl(215,20%,60%)] mb-1">{label}</p>
      {payload.map((entry: any, i: number) => (
        <p key={i} style={{ color: entry.color }} className="font-semibold">
          {entry.name}: {typeof entry.value === 'number' ? entry.value.toFixed(2) : entry.value}
        </p>
      ))}
    </div>
  )
}

// ---------------------------------------------------------------------------
// Main Page Component
// ---------------------------------------------------------------------------

export default function MarketDashboardPage() {
  // ---- Queries with 60s auto-refresh ----
  const REFETCH = 60_000

  const { data: marketStatus } = useQuery({
    queryKey: ['market-status'],
    queryFn: fetchMarketStatus,
    refetchInterval: REFETCH,
    staleTime: 30_000,
    retry: 1,
  })

  const { data: indices, isLoading: indicesLoading } = useQuery({
    queryKey: ['market-indices'],
    queryFn: fetchIndices,
    refetchInterval: REFETCH,
    staleTime: 30_000,
    retry: 1,
  })

  const { data: fearGreedData, isLoading: fearGreedLoading } = useQuery({
    queryKey: ['fear-greed'],
    queryFn: fetchFearGreed,
    refetchInterval: REFETCH,
    staleTime: 30_000,
    retry: 1,
  })

  const { data: yieldCurve } = useQuery({
    queryKey: ['fred-yield-curve'],
    queryFn: () => fetchFredSeries('T10Y2Y'),
    enabled: !!FRED_API_KEY,
    refetchInterval: REFETCH,
    staleTime: 30_000,
    retry: 1,
  })

  const { data: vixData } = useQuery({
    queryKey: ['fred-vix'],
    queryFn: () => fetchFredSeries('VIXCLS'),
    enabled: !!FRED_API_KEY,
    refetchInterval: REFETCH,
    staleTime: 30_000,
    retry: 1,
  })

  // ---- Stock Lookup ----
  const [ticker, setTicker] = useState('')
  const [lookupSymbol, setLookupSymbol] = useState<string | null>(null)

  const { data: lookupQuote, isFetching: lookupLoading, error: lookupError } = useQuery({
    queryKey: ['stock-lookup', lookupSymbol],
    queryFn: () => fetchStockQuote(lookupSymbol!),
    enabled: !!lookupSymbol,
    retry: 1,
    staleTime: 30_000,
  })

  const handleLookup = useCallback(() => {
    const sym = ticker.trim().toUpperCase()
    if (sym.length > 0 && sym.length <= 10) {
      setLookupSymbol(sym)
    }
  }, [ticker])

  // ---- Derived data ----
  const currentFearGreed = toNum(fearGreedData?.[0]?.value)

  const fearGreedChartData = useMemo(
    () =>
      (fearGreedData ?? []).slice().reverse().map((d) => ({
        date: new Date(Number(d.timestamp) * 1000).toLocaleDateString('en-US', { month: 'short', day: 'numeric' }),
        value: Number(d.value),
      })),
    [fearGreedData]
  )

  const yieldChartData = useMemo(
    () =>
      (yieldCurve ?? []).map((d) => ({
        date: d.date,
        spread: Number(d.value),
      })),
    [yieldCurve]
  )

  const vixChartData = useMemo(
    () =>
      (vixData ?? []).map((d) => ({
        date: d.date,
        vix: Number(d.value),
      })),
    [vixData]
  )

  const lookupPrice = toNum(lookupQuote?.price)
  const lookupChange = toNum(lookupQuote?.change)
  const lookupChangePercent = toNum(lookupQuote?.change_percent ?? lookupQuote?.changePercent)
  const lookupVolume = toNum(lookupQuote?.volume)
  const lookupBid = toNum(lookupQuote?.bid)
  const lookupAsk = toNum(lookupQuote?.ask)
  const lookupPrevClose = toNum(lookupQuote?.previous_close)
  const lookupTimestamp = typeof lookupQuote?.timestamp === 'string' ? lookupQuote.timestamp : null

  // ---- Last refreshed timer ----
  const [lastRefreshed, setLastRefreshed] = useState(new Date())
  useEffect(() => {
    const id = setInterval(() => setLastRefreshed(new Date()), REFETCH)
    return () => clearInterval(id)
  }, [])

  return (
    <>
      {/* SEO head tags */}
      <title>Market Dashboard | Stock Quotes, Fear &amp; Greed Index, Volatility</title>
      <meta name="description" content="Market dashboard with the Crypto Fear & Greed Index, major index quotes and quick stock lookup, drawn from live sources only. No login required." />
      <meta name="keywords" content="market dashboard, stock quotes, fear and greed index, VIX, yield curve, free market data" />
      <meta property="og:title" content="Market Dashboard | QuantEngines" />
      <meta property="og:description" content="Major indices, Crypto Fear & Greed and quick stock lookup, from live sources only." />

      <div className="space-y-8">
        {/* Header */}
        <div className="flex flex-col md:flex-row md:items-end justify-between gap-4">
          <div>
            <Badge className="bg-[hsl(210,100%,56%)] text-white text-xs mb-3">Free Market Data</Badge>
            <h1 className="text-3xl md:text-4xl font-bold text-white">Market Dashboard</h1>
            <p className="text-[hsl(215,20%,60%)] mt-2">
              Market indicators and economic signals from live sources, re-requested every 60 seconds.
              Panels whose source is unavailable say so rather than show a stand-in.
            </p>
          </div>
          <p className="text-xs text-[hsl(215,20%,50%)] shrink-0">
            Last updated: {lastRefreshed.toLocaleTimeString()}
          </p>
        </div>

        {/* Market Status Bar */}
        {marketStatus ? <MarketStatusBar status={marketStatus} /> : <MarketStatusUnknownBar />}

        {/* Major Indices */}
        <section>
          <h2 className="text-xl font-semibold text-white mb-4">Major Indices</h2>
          {indices && indices.length > 0 ? (
            <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
              {indices.map((q) => (
                <IndexCard key={q.symbol} quote={q} />
              ))}
            </div>
          ) : (
            <Card className="border-[hsl(215,40%,18%)] bg-[hsl(220,55%,7%)]">
              <CardContent className="pt-6">
                <Unavailable>
                  {indicesLoading
                    ? 'Loading index quotes...'
                    : 'Index quotes are unavailable right now. Nothing is shown in their place.'}
                </Unavailable>
              </CardContent>
            </Card>
          )}
        </section>

        {/* Fear & Greed + Quick Lookup row */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {/* Fear & Greed */}
          <Card className="border-[hsl(215,40%,18%)] bg-[hsl(220,55%,7%)]">
            <CardHeader>
              <CardTitle className="text-white">Crypto Fear &amp; Greed Index</CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              {currentFearGreed !== null && fearGreedChartData.length > 0 ? (
                <>
                  <FearGreedGauge value={currentFearGreed} />
                  <div className="h-48">
                    <ResponsiveContainer width="100%" height="100%">
                      <AreaChart data={fearGreedChartData}>
                        <defs>
                          <linearGradient id="fgGrad" x1="0" y1="0" x2="0" y2="1">
                            <stop offset="5%" stopColor={fearGreedColor(currentFearGreed)} stopOpacity={0.3} />
                            <stop offset="95%" stopColor={fearGreedColor(currentFearGreed)} stopOpacity={0} />
                          </linearGradient>
                        </defs>
                        <CartesianGrid strokeDasharray="3 3" stroke="hsl(215,40%,16%)" />
                        <XAxis dataKey="date" tick={{ fill: 'hsl(215,20%,55%)', fontSize: 11 }} tickLine={false} />
                        <YAxis domain={[0, 100]} tick={{ fill: 'hsl(215,20%,55%)', fontSize: 11 }} tickLine={false} />
                        <Tooltip content={<DarkTooltip />} />
                        <Area
                          type="monotone"
                          dataKey="value"
                          name="F&G"
                          stroke={fearGreedColor(currentFearGreed)}
                          fill="url(#fgGrad)"
                          strokeWidth={2}
                        />
                      </AreaChart>
                    </ResponsiveContainer>
                  </div>
                </>
              ) : (
                <Unavailable>
                  {fearGreedLoading
                    ? 'Loading the Fear & Greed Index...'
                    : 'Alternative.me did not return an index reading. No gauge is drawn without one.'}
                </Unavailable>
              )}
            </CardContent>
          </Card>

          {/* Quick Stock Lookup */}
          <Card className="border-[hsl(215,40%,18%)] bg-[hsl(220,55%,7%)]">
            <CardHeader>
              <CardTitle className="text-white">Quick Stock Lookup</CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="flex gap-2">
                <Input
                  value={ticker}
                  onChange={(e) => setTicker(e.target.value.toUpperCase())}
                  onKeyDown={(e) => e.key === 'Enter' && handleLookup()}
                  placeholder="Enter ticker (e.g. AAPL)"
                  className="bg-[hsl(220,55%,10%)] border-[hsl(215,40%,20%)] text-white placeholder:text-[hsl(215,20%,40%)]"
                />
                <Button
                  onClick={handleLookup}
                  disabled={lookupLoading}
                  className="bg-[hsl(45,96%,58%)] text-[hsl(220,60%,8%)] hover:bg-[hsl(45,96%,65%)] font-semibold shrink-0"
                >
                  {lookupLoading ? 'Loading...' : 'Lookup'}
                </Button>
              </div>

              {lookupError && (
                <div className="text-red-400 text-sm p-3 bg-red-500/10 border border-red-500/20 rounded">
                  Could not fetch quote for &quot;{lookupSymbol}&quot;. Check the ticker and try again.
                </div>
              )}

              {lookupQuote && lookupPrice !== null && (
                <div className="p-4 rounded-lg border border-[hsl(215,40%,20%)] bg-[hsl(220,55%,5%)] space-y-3">
                  <div className="flex items-center justify-between">
                    <span className="text-lg font-bold text-white">{lookupQuote.symbol}</span>
                    {lookupTimestamp && (
                      <Badge className="bg-[hsl(215,50%,14%)] text-[hsl(215,20%,70%)]">
                        {new Date(lookupTimestamp).toLocaleTimeString()}
                      </Badge>
                    )}
                  </div>
                  <div className="text-3xl font-bold text-white">
                    ${lookupPrice.toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 })}
                  </div>
                  {lookupChange !== null && (
                    <div className={`text-sm font-medium ${lookupChange >= 0 ? 'text-green-400' : 'text-red-400'}`}>
                      {lookupChange >= 0 ? '+' : ''}
                      {lookupChange.toFixed(2)}
                      {lookupChangePercent !== null && (
                        <> ({lookupChangePercent >= 0 ? '+' : ''}{lookupChangePercent.toFixed(2)}%)</>
                      )}
                    </div>
                  )}
                  <div className="grid grid-cols-3 gap-3 pt-2 border-t border-[hsl(215,40%,16%)]">
                    <div>
                      <p className="text-[hsl(215,20%,50%)] text-xs">Volume</p>
                      <p className="text-white text-sm font-medium">{lookupVolume?.toLocaleString() ?? '-'}</p>
                    </div>
                    {lookupBid !== null && (
                      <div>
                        <p className="text-[hsl(215,20%,50%)] text-xs">Bid</p>
                        <p className="text-white text-sm font-medium">${lookupBid.toFixed(2)}</p>
                      </div>
                    )}
                    {lookupAsk !== null && (
                      <div>
                        <p className="text-[hsl(215,20%,50%)] text-xs">Ask</p>
                        <p className="text-white text-sm font-medium">${lookupAsk.toFixed(2)}</p>
                      </div>
                    )}
                    {lookupPrevClose !== null && (
                      <div>
                        <p className="text-[hsl(215,20%,50%)] text-xs">Prev Close</p>
                        <p className="text-white text-sm font-medium">${lookupPrevClose.toFixed(2)}</p>
                      </div>
                    )}
                  </div>
                </div>
              )}

              {!lookupQuote && !lookupError && (
                <div className="text-center py-8 text-[hsl(215,20%,45%)] text-sm">
                  Type a stock ticker above and press Enter or click Lookup to fetch a quote from the backend API.
                </div>
              )}
            </CardContent>
          </Card>
        </div>

        {/* Yield Curve Spread + VIX Charts — only when a FRED key is configured and
            the series actually came back. */}
        {FRED_API_KEY && (yieldChartData.length > 0 || vixChartData.length > 0) && (
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            {/* Yield Curve Spread */}
            {yieldChartData.length > 0 && (
              <Card className="border-[hsl(215,40%,18%)] bg-[hsl(220,55%,7%)]">
                <CardHeader>
                  <div className="flex items-center justify-between">
                    <CardTitle className="text-white">10Y-2Y Yield Curve Spread</CardTitle>
                    <Badge className={`text-xs ${
                      yieldChartData[yieldChartData.length - 1].spread < 0
                        ? 'bg-red-600 text-white'
                        : 'bg-green-600 text-white'
                    }`}>
                      {yieldChartData[yieldChartData.length - 1].spread < 0 ? 'INVERTED' : 'NORMAL'}
                    </Badge>
                  </div>
                  <p className="text-[hsl(215,20%,50%)] text-xs">
                    An inverted yield curve (negative spread) has historically preceded recessions. Source: FRED
                  </p>
                </CardHeader>
                <CardContent>
                  <div className="h-64">
                    <ResponsiveContainer width="100%" height="100%">
                      <AreaChart data={yieldChartData}>
                        <defs>
                          <linearGradient id="ycGrad" x1="0" y1="0" x2="0" y2="1">
                            <stop offset="5%" stopColor="#3b82f6" stopOpacity={0.3} />
                            <stop offset="95%" stopColor="#3b82f6" stopOpacity={0} />
                          </linearGradient>
                        </defs>
                        <CartesianGrid strokeDasharray="3 3" stroke="hsl(215,40%,16%)" />
                        <XAxis dataKey="date" tick={{ fill: 'hsl(215,20%,55%)', fontSize: 11 }} tickLine={false} />
                        <YAxis tick={{ fill: 'hsl(215,20%,55%)', fontSize: 11 }} tickLine={false} />
                        <Tooltip content={<DarkTooltip />} />
                        {/* Zero reference line */}
                        <Line type="monotone" dataKey={() => 0} stroke="#ef4444" strokeDasharray="4 4" dot={false} name="Zero" />
                        <Area
                          type="monotone"
                          dataKey="spread"
                          name="Spread (%)"
                          stroke="#3b82f6"
                          fill="url(#ycGrad)"
                          strokeWidth={2}
                        />
                      </AreaChart>
                    </ResponsiveContainer>
                  </div>
                </CardContent>
              </Card>
            )}

            {/* VIX Volatility */}
            {vixChartData.length > 0 && (
              <Card className="border-[hsl(215,40%,18%)] bg-[hsl(220,55%,7%)]">
                <CardHeader>
                  <div className="flex items-center justify-between">
                    <CardTitle className="text-white">VIX Volatility Index</CardTitle>
                    <Badge className={`text-xs ${
                      vixChartData[vixChartData.length - 1].vix > 30
                        ? 'bg-red-600 text-white'
                        : vixChartData[vixChartData.length - 1].vix > 20
                          ? 'bg-yellow-600 text-white'
                          : 'bg-green-600 text-white'
                    }`}>
                      {vixChartData[vixChartData.length - 1].vix > 30
                        ? 'HIGH FEAR'
                        : vixChartData[vixChartData.length - 1].vix > 20
                          ? 'ELEVATED'
                          : 'LOW VOL'}
                    </Badge>
                  </div>
                  <p className="text-[hsl(215,20%,50%)] text-xs">
                    The &quot;fear gauge&quot; of the stock market. Values above 30 indicate extreme fear. Source: FRED/CBOE
                  </p>
                </CardHeader>
                <CardContent>
                  <div className="h-64">
                    <ResponsiveContainer width="100%" height="100%">
                      <AreaChart data={vixChartData}>
                        <defs>
                          <linearGradient id="vixGrad" x1="0" y1="0" x2="0" y2="1">
                            <stop offset="5%" stopColor="#f97316" stopOpacity={0.3} />
                            <stop offset="95%" stopColor="#f97316" stopOpacity={0} />
                          </linearGradient>
                        </defs>
                        <CartesianGrid strokeDasharray="3 3" stroke="hsl(215,40%,16%)" />
                        <XAxis dataKey="date" tick={{ fill: 'hsl(215,20%,55%)', fontSize: 11 }} tickLine={false} />
                        <YAxis tick={{ fill: 'hsl(215,20%,55%)', fontSize: 11 }} tickLine={false} />
                        <Tooltip content={<DarkTooltip />} />
                        {/* Warning threshold lines */}
                        <Line type="monotone" dataKey={() => 20} stroke="#eab308" strokeDasharray="4 4" dot={false} name="Caution (20)" />
                        <Line type="monotone" dataKey={() => 30} stroke="#ef4444" strokeDasharray="4 4" dot={false} name="Fear (30)" />
                        <Area
                          type="monotone"
                          dataKey="vix"
                          name="VIX"
                          stroke="#f97316"
                          fill="url(#vixGrad)"
                          strokeWidth={2}
                        />
                      </AreaChart>
                    </ResponsiveContainer>
                  </div>
                </CardContent>
              </Card>
            )}
          </div>
        )}

        {/* Footer disclaimer */}
        <div className="text-center py-6 border-t border-[hsl(215,40%,14%)]">
          <p className="text-xs text-[hsl(215,20%,45%)]">
            Market data provided for informational purposes only. Crypto Fear &amp; Greed from Alternative.me.
            Economic data from FRED (Federal Reserve Bank of St. Louis). Quotes may be delayed. Not financial advice.
          </p>
        </div>
      </div>
    </>
  )
}
