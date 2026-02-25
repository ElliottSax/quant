/**
 * Quick Ticker Lookup Widget
 * Instant value - lookup any stock ticker
 */

'use client'

import { useState } from 'react'

export function QuickTickerLookup() {
  const [ticker, setTicker] = useState('')
  const [loading, setLoading] = useState(false)
  const [result, setResult] = useState<any>(null)

  const handleLookup = async () => {
    if (!ticker) return

    setLoading(true)
    // Simulate API call with demo data
    setTimeout(() => {
      setResult({
        symbol: ticker.toUpperCase(),
        name: 'Example Corp',
        price: 156.78,
        change: 2.34,
        changePercent: 1.52,
        volume: 45234567,
        marketCap: '2.3T',
        pe: 28.4,
        dividend: 0.88,
        signals: {
          rsi: 67.8,
          macd: 'Bullish',
          trend: 'Uptrend',
          support: 152.30,
          resistance: 161.50,
        },
        politicianActivity: Math.random() > 0.5 ? {
          recentTrades: 12,
          buyVolume: 8,
          sellVolume: 4,
          trending: true,
        } : null,
      })
      setLoading(false)
    }, 800)
  }

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter') {
      handleLookup()
    }
  }

  return (
    <div className="glass-strong rounded-xl border border-border/50 p-6">
      <div className="flex items-center gap-2 mb-4">
        <div className="w-10 h-10 rounded-lg bg-gradient-to-br from-blue-500 to-cyan-500 flex items-center justify-center">
          <svg className="w-5 h-5 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
          </svg>
        </div>
        <h3 className="text-lg font-bold">Quick Stock Lookup</h3>
      </div>

      <div className="flex gap-2 mb-4">
        <input
          type="text"
          value={ticker}
          onChange={(e) => setTicker(e.target.value.toUpperCase())}
          onKeyPress={handleKeyPress}
          placeholder="Enter ticker (e.g., AAPL)"
          className="input-field flex-1 uppercase"
          maxLength={5}
        />
        <button
          onClick={handleLookup}
          disabled={!ticker || loading}
          className="btn-primary !px-6 disabled:opacity-50"
        >
          {loading ? (
            <div className="h-5 w-5 animate-spin rounded-full border-2 border-solid border-current border-r-transparent" />
          ) : (
            'Lookup'
          )}
        </button>
      </div>

      {result && (
        <div className="space-y-4 animate-fade-in">
          {/* Price Header */}
          <div className="border-b border-border/50 pb-4">
            <div className="flex items-center justify-between mb-2">
              <div>
                <h4 className="text-2xl font-bold">{result.symbol}</h4>
                <p className="text-sm text-muted-foreground">{result.name}</p>
              </div>
              <div className="text-right">
                <p className="text-3xl font-bold">${result.price}</p>
                <p className={`text-sm font-semibold ${result.change >= 0 ? 'text-green-500' : 'text-red-500'}`}>
                  {result.change >= 0 ? '+' : ''}{result.change} ({result.changePercent >= 0 ? '+' : ''}{result.changePercent}%)
                </p>
              </div>
            </div>
          </div>

          {/* Key Metrics */}
          <div className="grid grid-cols-2 gap-3">
            <MetricBox label="Market Cap" value={result.marketCap} />
            <MetricBox label="Volume" value={result.volume.toLocaleString()} />
            <MetricBox label="P/E Ratio" value={result.pe} />
            <MetricBox label="Dividend" value={`${result.dividend}%`} />
          </div>

          {/* Technical Signals */}
          <div className="bg-primary/5 border border-primary/10 rounded-lg p-4">
            <p className="text-xs font-semibold text-muted-foreground mb-3">TECHNICAL SIGNALS</p>
            <div className="grid grid-cols-2 gap-2 text-sm">
              <div className="flex justify-between">
                <span className="text-muted-foreground">RSI:</span>
                <span className="font-semibold">{result.signals.rsi}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-muted-foreground">MACD:</span>
                <span className="font-semibold text-green-500">{result.signals.macd}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-muted-foreground">Trend:</span>
                <span className="font-semibold text-green-500">{result.signals.trend}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-muted-foreground">Support:</span>
                <span className="font-semibold">${result.signals.support}</span>
              </div>
            </div>
          </div>

          {/* Politician Activity Alert */}
          {result.politicianActivity && (
            <div className="bg-orange-500/10 border border-orange-500/20 rounded-lg p-4">
              <div className="flex items-center gap-2 mb-2">
                <svg className="w-5 h-5 text-orange-500" fill="currentColor" viewBox="0 0 20 20">
                  <path fillRule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7-4a1 1 0 11-2 0 1 1 0 012 0zM9 9a1 1 0 000 2v3a1 1 0 001 1h1a1 1 0 100-2v-3a1 1 0 00-1-1H9z" clipRule="evenodd" />
                </svg>
                <p className="font-bold text-orange-500 text-sm">Congressional Activity Detected</p>
              </div>
              <p className="text-sm mb-2">
                <span className="font-semibold">{result.politicianActivity.recentTrades} politicians</span> traded this stock recently
              </p>
              <div className="flex gap-4 text-xs">
                <span className="text-green-500 font-semibold">{result.politicianActivity.buyVolume} Buys</span>
                <span className="text-red-500 font-semibold">{result.politicianActivity.sellVolume} Sells</span>
              </div>
            </div>
          )}

          {/* CTAs */}
          <div className="flex gap-2 pt-2">
            <button className="btn-primary flex-1 !py-2 text-sm">
              View Full Analysis
            </button>
            <button className="btn-secondary flex-1 !py-2 text-sm">
              Add to Watchlist
            </button>
          </div>
        </div>
      )}

      {!result && !loading && (
        <div className="text-center py-8 text-muted-foreground text-sm">
          Enter any stock ticker to see instant analysis
        </div>
      )}
    </div>
  )
}

function MetricBox({ label, value }: { label: string; value: string | number }) {
  return (
    <div className="bg-muted/30 rounded-lg p-3">
      <p className="text-xs text-muted-foreground mb-1">{label}</p>
      <p className="font-bold">{value}</p>
    </div>
  )
}
