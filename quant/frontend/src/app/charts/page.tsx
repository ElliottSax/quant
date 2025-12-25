/**
 * Advanced Charts & Visualizations Page
 * Professional-grade charting tools with TradingView & ECharts
 */

'use client'

import { useState, useMemo } from 'react'
import dynamic from 'next/dynamic'
import { AdvancedCandlestickChart } from '@/components/charts/AdvancedCandlestickChart'
import { AdvancedHeatmap } from '@/components/charts/AdvancedHeatmap'
import { AdvancedTimeSeriesChart } from '@/components/charts/AdvancedTimeSeriesChart'
import { GaugeChart } from '@/components/charts/GaugeChart'
import { RadarChart } from '@/components/charts/RadarChart'

// Demo data generators
const generateOHLCData = (days: number = 120) => {
  const data = []
  let price = 150
  const startDate = new Date()
  startDate.setDate(startDate.getDate() - days)

  for (let i = 0; i < days; i++) {
    const date = new Date(startDate)
    date.setDate(date.getDate() + i)

    const volatility = 0.02 + Math.random() * 0.02
    const trend = Math.sin(i / 30) * 0.005
    const change = (Math.random() - 0.48 + trend) * price * volatility

    const open = price
    const close = Math.max(1, price + change)
    const high = Math.max(open, close) * (1 + Math.random() * 0.015)
    const low = Math.min(open, close) * (1 - Math.random() * 0.015)
    const volume = Math.floor(1000000 + Math.random() * 8000000)

    data.push({
      timestamp: date.toISOString().split('T')[0],
      open: parseFloat(open.toFixed(2)),
      high: parseFloat(high.toFixed(2)),
      low: parseFloat(low.toFixed(2)),
      close: parseFloat(close.toFixed(2)),
      volume,
    })

    price = close
  }
  return data
}

const generateCorrelationData = () => {
  const symbols = ['AAPL', 'GOOGL', 'MSFT', 'AMZN', 'TSLA', 'NVDA', 'META', 'NFLX', 'AMD', 'CRM']
  const data: { xLabel: string; yLabel: string; value: number }[] = []

  symbols.forEach((symbol1, i) => {
    symbols.forEach((symbol2, j) => {
      let correlation
      if (i === j) {
        correlation = 1.0
      } else if (Math.abs(i - j) === 1) {
        correlation = 0.6 + Math.random() * 0.3
      } else {
        correlation = (Math.random() - 0.3) * 1.2
        correlation = Math.max(-1, Math.min(1, correlation))
      }

      data.push({
        xLabel: symbol1,
        yLabel: symbol2,
        value: parseFloat(correlation.toFixed(4)),
      })
    })
  })

  return data
}

const generateVolatilityData = () => {
  const data = []
  const startDate = new Date()
  startDate.setDate(startDate.getDate() - 252)

  for (let i = 0; i < 252; i++) {
    const date = new Date(startDate)
    date.setDate(date.getDate() + i)

    data.push({
      timestamp: date.toISOString().split('T')[0],
      value: parseFloat((0.15 + Math.sin(i / 20) * 0.1 + Math.random() * 0.05).toFixed(4)) * 100,
    })
  }
  return data
}

const generateDrawdownData = () => {
  const data = []
  let portfolioValue = 100000
  let peak = portfolioValue
  const startDate = new Date()
  startDate.setDate(startDate.getDate() - 252)

  for (let i = 0; i < 252; i++) {
    const date = new Date(startDate)
    date.setDate(date.getDate() + i)

    const dailyReturn = (Math.random() - 0.48) * 0.02
    portfolioValue *= (1 + dailyReturn)
    peak = Math.max(peak, portfolioValue)
    const drawdown = ((portfolioValue - peak) / peak) * 100

    data.push({
      timestamp: date.toISOString().split('T')[0],
      value: parseFloat(drawdown.toFixed(2)),
    })
  }

  return data
}

const CHART_TYPES = [
  { id: 'candlestick', label: 'Candlestick', icon: '📊', description: 'TradingView-style OHLC with indicators' },
  { id: 'correlation', label: 'Correlation', icon: '🔥', description: 'Interactive correlation heatmap' },
  { id: 'volatility', label: 'Volatility', icon: '📈', description: 'Historical volatility analysis' },
  { id: 'drawdown', label: 'Drawdown', icon: '📉', description: 'Portfolio drawdown tracking' },
  { id: 'metrics', label: 'Metrics', icon: '⏱️', description: 'Risk gauges and radar analysis' },
] as const

type ChartType = typeof CHART_TYPES[number]['id']

const STOCK_PRESETS = [
  { symbol: 'AAPL', name: 'Apple Inc.' },
  { symbol: 'GOOGL', name: 'Alphabet Inc.' },
  { symbol: 'MSFT', name: 'Microsoft Corp.' },
  { symbol: 'TSLA', name: 'Tesla Inc.' },
  { symbol: 'NVDA', name: 'NVIDIA Corp.' },
  { symbol: 'AMZN', name: 'Amazon.com Inc.' },
]

export default function ChartsPage() {
  const [selectedChart, setSelectedChart] = useState<ChartType>('candlestick')
  const [ticker, setTicker] = useState('AAPL')
  const [showIndicators, setShowIndicators] = useState({
    volume: true,
    sma: true,
    rsi: false,
    bollinger: false,
  })

  // Generate data
  const ohlcData = useMemo(() => generateOHLCData(150), [])
  const correlationData = useMemo(() => generateCorrelationData(), [])
  const volatilityData = useMemo(() => generateVolatilityData(), [])
  const drawdownData = useMemo(() => generateDrawdownData(), [])

  const radarData = useMemo(() => [
    { name: 'Momentum', value: 75, max: 100 },
    { name: 'Volatility', value: 45, max: 100 },
    { name: 'Volume', value: 82, max: 100 },
    { name: 'Trend', value: 68, max: 100 },
    { name: 'Support', value: 55, max: 100 },
    { name: 'Resistance', value: 62, max: 100 },
  ], [])

  const currentChartInfo = CHART_TYPES.find(c => c.id === selectedChart)

  return (
    <div className="space-y-8">
      {/* Header */}
      <div className="animate-fade-in">
        <h1 className="text-4xl md:text-5xl font-bold mb-3 gradient-text">
          Advanced Charts
        </h1>
        <p className="text-lg text-slate-400 max-w-2xl">
          Professional-grade visualization tools powered by TradingView Lightweight Charts
          and Apache ECharts. Interactive, responsive, and built for serious analysis.
        </p>
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

          {/* Chart Type Selector */}
          <div className="flex-1">
            <label className="block text-xs font-semibold text-slate-500 uppercase tracking-wider mb-2">
              Chart Type
            </label>
            <div className="flex flex-wrap gap-2">
              {CHART_TYPES.map((chart) => (
                <button
                  key={chart.id}
                  onClick={() => setSelectedChart(chart.id)}
                  className={`group relative px-4 py-2.5 rounded-xl text-sm font-medium transition-all ${
                    selectedChart === chart.id
                      ? 'bg-gradient-to-r from-indigo-500 to-purple-600 text-white shadow-lg shadow-indigo-500/25'
                      : 'bg-slate-800/50 text-slate-300 hover:bg-slate-700/50 border border-slate-700/50'
                  }`}
                >
                  <span className="flex items-center gap-2">
                    <span className="text-base">{chart.icon}</span>
                    <span>{chart.label}</span>
                  </span>
                </button>
              ))}
            </div>
          </div>
        </div>

        {/* Chart Description */}
        <div className="mt-4 pt-4 border-t border-slate-700/50">
          <p className="text-sm text-slate-400">
            <span className="text-indigo-400 font-medium">{currentChartInfo?.icon} {currentChartInfo?.label}:</span>{' '}
            {currentChartInfo?.description}
          </p>
        </div>

        {/* Indicator Toggles (for candlestick) */}
        {selectedChart === 'candlestick' && (
          <div className="mt-4 pt-4 border-t border-slate-700/50">
            <label className="block text-xs font-semibold text-slate-500 uppercase tracking-wider mb-3">
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
        )}
      </div>

      {/* Chart Display */}
      <div className="animate-slide-up" style={{ animationDelay: '100ms' }}>
        {selectedChart === 'candlestick' && (
          <AdvancedCandlestickChart
            data={ohlcData}
            symbol={ticker}
            height={600}
            showVolume={showIndicators.volume}
            showSMA={showIndicators.sma}
            showRSI={showIndicators.rsi}
            showBollingerBands={showIndicators.bollinger}
          />
        )}

        {selectedChart === 'correlation' && (
          <AdvancedHeatmap
            data={correlationData}
            title="Stock Correlation Matrix"
            height={500}
          />
        )}

        {selectedChart === 'volatility' && (
          <AdvancedTimeSeriesChart
            data={volatilityData}
            title="Historical Volatility (Annualized)"
            seriesName="Volatility %"
            yAxisLabel="Volatility"
            color="#f59e0b"
            height={450}
            showDataZoom={true}
          />
        )}

        {selectedChart === 'drawdown' && (
          <AdvancedTimeSeriesChart
            data={drawdownData}
            title="Portfolio Drawdown Analysis"
            seriesName="Drawdown %"
            yAxisLabel="Drawdown"
            color="#ef4444"
            height={450}
            showDataZoom={true}
          />
        )}

        {selectedChart === 'metrics' && (
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            <div className="space-y-6">
              <GaugeChart
                value={67}
                title="Risk Score"
                subtitle="Portfolio risk assessment based on current holdings"
                size="lg"
                thresholds={{ low: 25, medium: 50, high: 75 }}
              />
              <GaugeChart
                value={42}
                title="Volatility Index"
                subtitle="30-day rolling volatility percentile"
                size="lg"
                colors={{
                  low: '#22c55e',
                  medium: '#f59e0b',
                  high: '#f97316',
                  critical: '#ef4444',
                }}
              />
            </div>
            <RadarChart
              data={radarData}
              title="Technical Analysis Profile"
              height={450}
              colors={['#6366f1', '#22c55e']}
            />
          </div>
        )}
      </div>

      {/* Stats Bar */}
      {selectedChart === 'candlestick' && ohlcData.length > 0 && (
        <div className="grid grid-cols-2 md:grid-cols-4 lg:grid-cols-6 gap-4 animate-fade-in" style={{ animationDelay: '200ms' }}>
          {[
            { label: 'Open', value: `$${ohlcData[ohlcData.length - 1].open.toFixed(2)}`, color: 'text-slate-300' },
            { label: 'High', value: `$${ohlcData[ohlcData.length - 1].high.toFixed(2)}`, color: 'text-emerald-400' },
            { label: 'Low', value: `$${ohlcData[ohlcData.length - 1].low.toFixed(2)}`, color: 'text-red-400' },
            { label: 'Close', value: `$${ohlcData[ohlcData.length - 1].close.toFixed(2)}`, color: 'text-white' },
            { label: 'Volume', value: (ohlcData[ohlcData.length - 1].volume / 1000000).toFixed(2) + 'M', color: 'text-cyan-400' },
            {
              label: 'Change',
              value: `${((ohlcData[ohlcData.length - 1].close - ohlcData[0].close) / ohlcData[0].close * 100).toFixed(2)}%`,
              color: ohlcData[ohlcData.length - 1].close >= ohlcData[0].close ? 'text-emerald-400' : 'text-red-400'
            },
          ].map((stat) => (
            <div key={stat.label} className="glass-card p-4 text-center">
              <p className="text-xs text-slate-500 uppercase tracking-wider mb-1">{stat.label}</p>
              <p className={`text-lg font-bold ${stat.color}`}>{stat.value}</p>
            </div>
          ))}
        </div>
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
