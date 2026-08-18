/**
 * Advanced Charts & Visualizations Page
 *
 * Every figure on this page is drawn from bars returned by the market-data API.
 * There is no synthetic fallback and none may be reintroduced: this page used to
 * generate a random-walk OHLC series whenever the API returned nothing, and label
 * it "Demo data" in 11px grey while the chart, the stats bar and the percentage
 * change above it all read as measured prices. A visitor could not tell the two
 * apart. When no bars arrive, the page now says so and shows nothing else.
 *
 * The correlation heatmap, volatility series, drawdown series, risk gauges and
 * technical radar that used to live here were removed for the same reason: none of
 * them had a data source at all. They were random numbers and hardcoded scores.
 * They come back only when they are computed from real history.
 */

'use client'

import { useState, useMemo, useEffect, Suspense } from 'react'
import { useSearchParams } from 'next/navigation'
import { AdvancedCandlestickChart } from '@/components/charts/AdvancedCandlestickChart'
import { useHistoricalData, useMarketQuote, useMarketStatus } from '@/lib/hooks'

interface OhlcBar {
  timestamp: string
  open: number
  high: number
  low: number
  close: number
  volume: number
}

/**
 * Accept only bars that actually carry a date and four finite prices. Anything
 * malformed is dropped rather than defaulted, so a partial response can never be
 * padded out into a complete-looking series.
 */
function toOhlcBars(raw: unknown): OhlcBar[] {
  if (!Array.isArray(raw)) return []

  const bars: OhlcBar[] = []
  for (const item of raw) {
    if (!item || typeof item !== 'object') continue
    const record = item as Record<string, unknown>

    const stamp =
      typeof record.timestamp === 'string'
        ? record.timestamp
        : typeof record.date === 'string'
          ? record.date
          : null
    if (!stamp) continue

    const open = Number(record.open)
    const high = Number(record.high)
    const low = Number(record.low)
    const close = Number(record.close)
    if (![open, high, low, close].every(Number.isFinite)) continue

    const volume = Number(record.volume)

    bars.push({
      timestamp: stamp.split('T')[0],
      open,
      high,
      low,
      close,
      volume: Number.isFinite(volume) ? volume : 0,
    })
  }
  return bars
}

const STOCK_PRESETS = [
  { symbol: 'AAPL', name: 'Apple Inc.' },
  { symbol: 'GOOGL', name: 'Alphabet Inc.' },
  { symbol: 'MSFT', name: 'Microsoft Corp.' },
  { symbol: 'TSLA', name: 'Tesla Inc.' },
  { symbol: 'NVDA', name: 'NVIDIA Corp.' },
  { symbol: 'AMZN', name: 'Amazon.com Inc.' },
]

function ChartsContent() {
  const searchParams = useSearchParams()
  const symbolFromUrl = searchParams.get('symbol')

  const [ticker, setTicker] = useState(symbolFromUrl?.toUpperCase() || 'AAPL')
  const [showIndicators, setShowIndicators] = useState({
    volume: true,
    sma: true,
    rsi: false,
    bollinger: false,
  })

  // Update ticker when URL param changes
  useEffect(() => {
    if (symbolFromUrl) {
      setTicker(symbolFromUrl.toUpperCase())
    }
  }, [symbolFromUrl])

  // Calculate date range for historical data (1 year)
  const startDate = useMemo(() => {
    const date = new Date()
    date.setFullYear(date.getFullYear() - 1)
    return date.toISOString()
  }, [])

  // Fetch real market data from API
  const {
    data: historicalData,
    isLoading: isLoadingHistorical,
    isError: isHistoricalError,
    refetch: refetchHistorical,
  } = useHistoricalData(ticker, startDate)

  const { data: quoteData, isLoading: isLoadingQuote } = useMarketQuote(ticker)

  const { data: marketStatus } = useMarketStatus()

  const ohlcData = useMemo(() => toOhlcBars(historicalData), [historicalData])

  const quotePrice = typeof quoteData?.price === 'number' ? quoteData.price : null
  const quoteChange = typeof quoteData?.change === 'number' ? quoteData.change : null
  const quoteChangePercent =
    typeof quoteData?.changePercent === 'number' ? quoteData.changePercent : null

  const hasBars = ohlcData.length > 0
  const latest = hasBars ? ohlcData[ohlcData.length - 1] : null
  const first = hasBars ? ohlcData[0] : null

  return (
    <div className="space-y-8">
      {/* Header */}
      <div className="animate-fade-in">
        <div className="flex items-start justify-between">
          <div>
            <h1 className="text-4xl md:text-5xl font-bold mb-3 gradient-text">
              Advanced Charts
            </h1>
            <p className="text-lg text-slate-400 max-w-2xl">
              Professional-grade visualization tools powered by TradingView Lightweight Charts
              and Apache ECharts. Every price and indicator on this page is drawn from
              market data returned by the API — nothing is simulated.
            </p>
          </div>

          {/* Market Status & Real-time Quote */}
          <div className="flex flex-col items-end gap-2">
            {marketStatus && (
              <div className={`flex items-center gap-2 px-3 py-1.5 rounded-lg ${
                marketStatus.isOpen
                  ? 'bg-emerald-500/10 border border-emerald-500/30'
                  : 'bg-slate-700/50 border border-slate-600/30'
              }`}>
                <span className={`w-2 h-2 rounded-full ${
                  marketStatus.isOpen ? 'bg-emerald-400 animate-pulse' : 'bg-slate-500'
                }`} />
                <span className={`text-xs font-medium ${
                  marketStatus.isOpen ? 'text-emerald-400' : 'text-slate-400'
                }`}>
                  {marketStatus.isOpen ? 'MARKET OPEN' : 'MARKET CLOSED'}
                </span>
              </div>
            )}

            {quotePrice !== null && !isLoadingQuote && (
              <div className="text-right">
                <div className="text-2xl font-bold text-white font-mono">
                  ${quotePrice.toFixed(2)}
                </div>
                {quoteChange !== null && (
                  <div className={`text-sm font-medium ${
                    quoteChange >= 0 ? 'text-emerald-400' : 'text-red-400'
                  }`}>
                    {quoteChange >= 0 ? '+' : ''}
                    {quoteChange.toFixed(2)}
                    {quoteChangePercent !== null && ` (${quoteChangePercent.toFixed(2)}%)`}
                  </div>
                )}
              </div>
            )}

            {isLoadingHistorical && (
              <div className="flex items-center gap-2 text-xs text-slate-400">
                <div className="w-3 h-3 border-2 border-indigo-500/30 border-t-indigo-500 rounded-full animate-spin" />
                Loading data...
              </div>
            )}
          </div>
        </div>
      </div>

      {/* Control Panel */}
      <div className="glass-card p-6">
        <div className="flex flex-col lg:flex-row gap-6">
          {/* Stock Selector */}
          <div className="flex-shrink-0">
            <label className="block text-xs font-semibold text-slate-500 uppercase tracking-wider mb-2">
              Symbol
            </label>
            <div className="flex gap-2">
              <input
                type="text"
                value={ticker}
                onChange={(e) => setTicker(e.target.value.toUpperCase())}
                className="input-field w-24 uppercase font-mono text-lg text-center"
                placeholder="AAPL"
                maxLength={5}
              />
              <div className="flex gap-1">
                {STOCK_PRESETS.slice(0, 4).map((stock) => (
                  <button
                    key={stock.symbol}
                    onClick={() => setTicker(stock.symbol)}
                    className={`px-3 py-2 text-xs font-medium rounded-lg transition-all ${
                      ticker === stock.symbol
                        ? 'bg-indigo-500 text-white'
                        : 'bg-slate-800/50 text-slate-400 hover:bg-slate-700/50 hover:text-white'
                    }`}
                    title={stock.name}
                  >
                    {stock.symbol}
                  </button>
                ))}
              </div>
            </div>
          </div>

          {/* Indicator Toggles */}
          <div className="flex-1">
            <label className="block text-xs font-semibold text-slate-500 uppercase tracking-wider mb-2">
              Technical Indicators
            </label>
            <div className="flex flex-wrap gap-3">
              {[
                { key: 'volume', label: 'Volume', color: 'cyan' },
                { key: 'sma', label: 'SMA 20/50', color: 'amber' },
                { key: 'rsi', label: 'RSI (14)', color: 'purple' },
                { key: 'bollinger', label: 'Bollinger Bands', color: 'blue' },
              ].map((indicator) => (
                <button
                  key={indicator.key}
                  onClick={() => setShowIndicators(prev => ({
                    ...prev,
                    [indicator.key]: !prev[indicator.key as keyof typeof prev]
                  }))}
                  className={`px-4 py-2 rounded-lg text-sm font-medium transition-all flex items-center gap-2 ${
                    showIndicators[indicator.key as keyof typeof showIndicators]
                      ? `bg-${indicator.color}-500/20 text-${indicator.color}-400 border border-${indicator.color}-500/30`
                      : 'bg-slate-800/30 text-slate-500 border border-slate-700/30 hover:bg-slate-700/50'
                  }`}
                >
                  <span className={`w-2 h-2 rounded-full ${
                    showIndicators[indicator.key as keyof typeof showIndicators]
                      ? `bg-${indicator.color}-400`
                      : 'bg-slate-600'
                  }`} />
                  {indicator.label}
                </button>
              ))}
            </div>
          </div>
        </div>

        <div className="mt-4 pt-4 border-t border-slate-700/50">
          <p className="text-sm text-slate-400">
            <span className="text-indigo-400 font-medium">📊 Candlestick:</span>{' '}
            One year of daily OHLC bars for the selected symbol, with indicators computed
            from those bars. The correlation, volatility, drawdown and risk-score views
            that used to sit alongside this chart were removed — they had no data source
            behind them, and will return only once they are computed from real history.
          </p>
        </div>
      </div>

      {/* Chart Display */}
      <div className="animate-slide-up" style={{ animationDelay: '100ms' }}>
        {isLoadingHistorical ? (
          <div className="glass-card p-16 text-center">
            <div className="w-6 h-6 mx-auto mb-4 border-2 border-indigo-500/30 border-t-indigo-500 rounded-full animate-spin" />
            <p className="text-slate-400">Loading {ticker} price history…</p>
          </div>
        ) : hasBars ? (
          <AdvancedCandlestickChart
            data={ohlcData}
            symbol={ticker}
            height={600}
            showVolume={showIndicators.volume}
            showSMA={showIndicators.sma}
            showRSI={showIndicators.rsi}
            showBollingerBands={showIndicators.bollinger}
          />
        ) : (
          <div className="glass-card p-12 text-center border border-red-500/30">
            <h3 className="text-2xl font-bold mb-3">
              {ticker} price history did not load
            </h3>
            <p className="text-slate-400 mb-2 max-w-xl mx-auto">
              {isHistoricalError
                ? 'The market-data service returned an error.'
                : `No daily bars came back for ${ticker}. The symbol may not be covered, or the market-data service may be unavailable.`}
            </p>
            <p className="text-sm text-slate-500 mb-6 max-w-xl mx-auto">
              No chart is shown because there are no prices to chart. This page will never
              display a simulated price series in place of missing data.
            </p>
            <button onClick={() => refetchHistorical()} className="btn-primary">
              Try again
            </button>
          </div>
        )}
      </div>

      {/* Stats Bar */}
      {hasBars && latest && first && (
        <>
          <div className="flex items-center gap-2">
            <span className="w-2 h-2 rounded-full bg-emerald-400" />
            <span className="text-xs text-slate-500">
              {ohlcData.length} daily bars from the market-data API
            </span>
          </div>

          <div className="grid grid-cols-2 md:grid-cols-4 lg:grid-cols-6 gap-4 animate-fade-in" style={{ animationDelay: '200ms' }}>
            {[
              { label: 'Open', value: `$${latest.open.toFixed(2)}`, color: 'text-slate-300' },
              { label: 'High', value: `$${latest.high.toFixed(2)}`, color: 'text-emerald-400' },
              { label: 'Low', value: `$${latest.low.toFixed(2)}`, color: 'text-red-400' },
              { label: 'Close', value: `$${latest.close.toFixed(2)}`, color: 'text-white' },
              { label: 'Volume', value: `${(latest.volume / 1000000).toFixed(2)}M`, color: 'text-cyan-400' },
              {
                label: 'Change',
                value: `${((latest.close - first.close) / first.close * 100).toFixed(2)}%`,
                color: latest.close >= first.close ? 'text-emerald-400' : 'text-red-400'
              },
            ].map((stat) => (
              <div key={stat.label} className="glass-card p-4 text-center">
                <p className="text-xs text-slate-500 uppercase tracking-wider mb-1">{stat.label}</p>
                <p className={`text-lg font-bold ${stat.color}`}>{stat.value}</p>
              </div>
            ))}
          </div>
        </>
      )}

      {/* Pro Features CTA */}
      <div className="glass-card p-8 text-center relative overflow-hidden">
        <div className="absolute inset-0 bg-gradient-to-r from-indigo-500/10 via-purple-500/10 to-pink-500/10" />
        <div className="relative">
          <h3 className="text-2xl font-bold mb-3 gradient-text">Unlock Pro Features</h3>
          <p className="text-slate-400 mb-6 max-w-lg mx-auto">
            Get real-time data, custom alerts, advanced indicators, and AI-powered trade signals.
          </p>
          <div className="flex justify-center gap-4">
            <button className="btn-primary">
              Start Free Trial
            </button>
            <button className="btn-secondary">
              Learn More
            </button>
          </div>
        </div>
      </div>
    </div>
  )
}

function ChartsLoadingFallback() {
  return (
    <div className="space-y-8 animate-pulse">
      <div className="h-12 w-64 bg-slate-800/50 rounded-lg" />
      <div className="h-6 w-96 bg-slate-800/30 rounded" />
      <div className="glass-card p-6 h-32" />
      <div className="glass-card h-[600px]" />
    </div>
  )
}

export default function ChartsPage() {
  return (
    <Suspense fallback={<ChartsLoadingFallback />}>
      <ChartsContent />
    </Suspense>
  )
}
