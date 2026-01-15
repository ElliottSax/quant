/**
 * QuantEngines Home - Live Pattern Detection & Anomaly Dashboard
 * Everything is clickable and leads to detailed views
 */

'use client'

import { useState, useEffect, useMemo } from 'react'
import Link from 'next/link'
import { useRouter } from 'next/navigation'
import dynamic from 'next/dynamic'

const ReactECharts = dynamic(() => import('echarts-for-react'), { ssr: false })

// Simulated live data
interface Anomaly {
  id: string
  symbol: string
  type: 'volume_spike' | 'price_breakout' | 'unusual_options' | 'insider_cluster' | 'momentum_divergence'
  severity: 'critical' | 'high' | 'medium'
  message: string
  change: number
  detected: Date
  confidence: number
}

interface Pattern {
  id: string
  symbol: string
  pattern: string
  direction: 'bullish' | 'bearish' | 'neutral'
  confidence: number
  priceTarget?: number
  currentPrice: number
  timeframe: string
}

interface LiveSignal {
  symbol: string
  action: 'BUY' | 'SELL' | 'HOLD'
  price: number
  confidence: number
  indicators: string[]
}

const ANOMALY_TYPES = {
  volume_spike: { label: 'Volume Spike', icon: '📊', color: 'text-yellow-500' },
  price_breakout: { label: 'Price Breakout', icon: '🚀', color: 'text-green-500' },
  unusual_options: { label: 'Unusual Options', icon: '🎯', color: 'text-purple-500' },
  insider_cluster: { label: 'Insider Activity', icon: '👔', color: 'text-blue-500' },
  momentum_divergence: { label: 'Momentum Divergence', icon: '⚡', color: 'text-orange-500' },
}

const PATTERNS = [
  'Head & Shoulders', 'Double Bottom', 'Bull Flag', 'Cup & Handle',
  'Ascending Triangle', 'Falling Wedge', 'Golden Cross', 'MACD Crossover',
  'RSI Divergence', 'Breakout', 'Support Bounce', 'Resistance Test'
]

const SYMBOLS = ['AAPL', 'GOOGL', 'MSFT', 'TSLA', 'NVDA', 'META', 'AMZN', 'AMD', 'NFLX', 'CRM', 'ORCL', 'INTC', 'QCOM', 'AVGO', 'ADBE']

export default function Home() {
  const router = useRouter()
  const [anomalies, setAnomalies] = useState<Anomaly[]>([])
  const [patterns, setPatterns] = useState<Pattern[]>([])
  const [signals, setSignals] = useState<LiveSignal[]>([])
  const [marketPulse, setMarketPulse] = useState({ bullish: 52, bearish: 31, neutral: 17 })
  const [scanCount, setScanCount] = useState(0)
  const [lastUpdate, setLastUpdate] = useState(new Date())

  // Generate initial data and simulate live updates
  useEffect(() => {
    // Initial data
    generateAnomalies(5)
    generatePatterns(8)
    generateSignals(6)

    // Simulate live updates
    const anomalyInterval = setInterval(() => {
      if (Math.random() > 0.6) {
        generateAnomalies(1, true)
      }
      setScanCount(prev => prev + Math.floor(Math.random() * 50) + 10)
      setLastUpdate(new Date())
    }, 3000)

    const patternInterval = setInterval(() => {
      if (Math.random() > 0.7) {
        generatePatterns(1, true)
      }
    }, 5000)

    const signalInterval = setInterval(() => {
      generateSignals(1, true)
      setMarketPulse({
        bullish: 45 + Math.floor(Math.random() * 15),
        bearish: 25 + Math.floor(Math.random() * 15),
        neutral: 10 + Math.floor(Math.random() * 15),
      })
    }, 4000)

    return () => {
      clearInterval(anomalyInterval)
      clearInterval(patternInterval)
      clearInterval(signalInterval)
    }
  }, [])

  const generateAnomalies = (count: number, prepend = false) => {
    const types = Object.keys(ANOMALY_TYPES) as Anomaly['type'][]
    const severities: Anomaly['severity'][] = ['critical', 'high', 'medium']

    const newAnomalies: Anomaly[] = Array.from({ length: count }, (_, i) => {
      const type = types[Math.floor(Math.random() * types.length)]
      const symbol = SYMBOLS[Math.floor(Math.random() * SYMBOLS.length)]
      const severity = severities[Math.floor(Math.random() * severities.length)]
      const change = (Math.random() - 0.3) * 20

      const messages: Record<Anomaly['type'], string[]> = {
        volume_spike: [`${symbol} volume 340% above average`, `Unusual accumulation in ${symbol}`, `${symbol} block trade detected`],
        price_breakout: [`${symbol} breaking 52-week high`, `${symbol} gap up on heavy volume`, `${symbol} clearing major resistance`],
        unusual_options: [`Large ${symbol} call sweep detected`, `${symbol} unusual put activity`, `${symbol} options flow bullish`],
        insider_cluster: [`Multiple ${symbol} insider buys`, `${symbol} CEO purchase filed`, `${symbol} director buying`],
        momentum_divergence: [`${symbol} RSI divergence forming`, `${symbol} MACD histogram divergence`, `${symbol} momentum shift detected`],
      }

      return {
        id: `${Date.now()}-${i}`,
        symbol,
        type,
        severity,
        message: messages[type][Math.floor(Math.random() * messages[type].length)],
        change,
        detected: new Date(),
        confidence: 0.7 + Math.random() * 0.25,
      }
    })

    setAnomalies(prev => prepend
      ? [...newAnomalies, ...prev].slice(0, 12)
      : [...newAnomalies, ...prev].slice(0, 12)
    )
  }

  const generatePatterns = (count: number, prepend = false) => {
    const newPatterns: Pattern[] = Array.from({ length: count }, (_, i) => {
      const symbol = SYMBOLS[Math.floor(Math.random() * SYMBOLS.length)]
      const currentPrice = 50 + Math.random() * 400
      const direction = Math.random() > 0.5 ? 'bullish' : Math.random() > 0.3 ? 'bearish' : 'neutral'

      return {
        id: `${Date.now()}-${i}`,
        symbol,
        pattern: PATTERNS[Math.floor(Math.random() * PATTERNS.length)],
        direction,
        confidence: 0.65 + Math.random() * 0.3,
        priceTarget: direction === 'bullish' ? currentPrice * (1.05 + Math.random() * 0.15) :
                     direction === 'bearish' ? currentPrice * (0.85 + Math.random() * 0.1) : undefined,
        currentPrice,
        timeframe: ['1H', '4H', '1D', '1W'][Math.floor(Math.random() * 4)],
      }
    })

    setPatterns(prev => prepend
      ? [...newPatterns, ...prev].slice(0, 10)
      : [...newPatterns, ...prev].slice(0, 10)
    )
  }

  const generateSignals = (count: number, prepend = false) => {
    const newSignals: LiveSignal[] = Array.from({ length: count }, () => {
      const actions: LiveSignal['action'][] = ['BUY', 'SELL', 'HOLD']
      return {
        symbol: SYMBOLS[Math.floor(Math.random() * SYMBOLS.length)],
        action: actions[Math.floor(Math.random() * actions.length)],
        price: 50 + Math.random() * 400,
        confidence: 0.6 + Math.random() * 0.35,
        indicators: ['RSI', 'MACD', 'BB', 'SMA', 'Volume'].slice(0, 2 + Math.floor(Math.random() * 3)),
      }
    })

    setSignals(prev => prepend
      ? [...newSignals, ...prev].slice(0, 8)
      : [...newSignals, ...prev].slice(0, 8)
    )
  }

  // Market pulse gauge - clickable
  const pulseGaugeOptions = useMemo(() => ({
    backgroundColor: 'transparent',
    series: [{
      type: 'gauge',
      startAngle: 180,
      endAngle: 0,
      min: 0,
      max: 100,
      splitNumber: 10,
      radius: '100%',
      center: ['50%', '75%'],
      axisLine: {
        lineStyle: {
          width: 20,
          color: [
            [0.3, '#ef4444'],
            [0.5, '#eab308'],
            [0.7, '#22c55e'],
            [1, '#10b981']
          ]
        }
      },
      pointer: {
        icon: 'path://M12.8,0.7l12,40.1H0.7L12.8,0.7z',
        length: '55%',
        width: 10,
        offsetCenter: [0, '-15%'],
        itemStyle: { color: '#d4af37' }
      },
      axisTick: { show: false },
      splitLine: { show: false },
      axisLabel: { show: false },
      detail: {
        fontSize: 32,
        offsetCenter: [0, '5%'],
        formatter: '{value}%',
        color: '#d4af37',
        fontWeight: 'bold',
        fontFamily: 'JetBrains Mono, monospace',
      },
      data: [{ value: marketPulse.bullish }]
    }]
  }), [marketPulse])

  // Anomaly distribution chart
  const anomalyDistOptions = useMemo(() => {
    const typeCounts = anomalies.reduce((acc, a) => {
      acc[a.type] = (acc[a.type] || 0) + 1
      return acc
    }, {} as Record<string, number>)

    return {
      backgroundColor: 'transparent',
      tooltip: { trigger: 'item', backgroundColor: 'rgba(0,0,0,0.9)', textStyle: { color: '#fff' } },
      series: [{
        type: 'pie',
        radius: ['45%', '70%'],
        center: ['50%', '50%'],
        avoidLabelOverlap: true,
        itemStyle: { borderRadius: 4, borderColor: '#0a0f1a', borderWidth: 2 },
        label: { show: false },
        data: Object.entries(typeCounts).map(([type, count]) => ({
          value: count,
          name: ANOMALY_TYPES[type as keyof typeof ANOMALY_TYPES]?.label || type,
          itemStyle: {
            color: type === 'volume_spike' ? '#eab308' :
                   type === 'price_breakout' ? '#22c55e' :
                   type === 'unusual_options' ? '#a855f7' :
                   type === 'insider_cluster' ? '#3b82f6' : '#f97316'
          }
        }))
      }]
    }
  }, [anomalies])

  const criticalCount = anomalies.filter(a => a.severity === 'critical').length

  return (
    <div className="space-y-6">
      {/* Hero Header */}
      <div className="terminal-panel overflow-hidden">
        <div className="terminal-panel-header">
          <div className="flex items-center gap-3">
            <span className="relative flex h-2.5 w-2.5">
              <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-green-400 opacity-75"></span>
              <span className="relative inline-flex rounded-full h-2.5 w-2.5 bg-green-500"></span>
            </span>
            <span>QUANTENGINES TERMINAL</span>
          </div>
          <div className="flex items-center gap-4 text-[10px] font-mono">
            <span className="text-[hsl(215,20%,50%)]">Scanned: <span className="text-white">{scanCount.toLocaleString()}</span></span>
            <span className="text-[hsl(215,20%,50%)]">Updated: <span className="text-[hsl(142,71%,55%)]">{lastUpdate.toLocaleTimeString()}</span></span>
          </div>
        </div>

        <div className="p-6 bg-gradient-to-br from-[hsl(220,60%,4%)] via-[hsl(220,55%,6%)] to-[hsl(220,60%,4%)]">
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
            {/* Main Title */}
            <div className="lg:col-span-2">
              <h1 className="text-3xl md:text-4xl font-bold mb-3">
                <span className="text-[hsl(45,96%,58%)]">Real-Time</span>{' '}
                <span className="text-white">Pattern Detection</span>
              </h1>
              <p className="text-[hsl(215,20%,60%)] text-sm md:text-base mb-4 max-w-2xl">
                AI-powered market scanning detecting anomalies, chart patterns, and trading signals across 10,000+ securities in real-time.
              </p>

              {/* Quick Stats - All Clickable */}
              <div className="grid grid-cols-4 gap-3">
                <Link href="/discoveries">
                  <StatBox label="Anomalies" value={anomalies.length} color="yellow" />
                </Link>
                <Link href="/charts">
                  <StatBox label="Patterns" value={patterns.length} color="blue" />
                </Link>
                <Link href="/signals">
                  <StatBox label="Signals" value={signals.length} color="green" />
                </Link>
                <Link href="/discoveries">
                  <StatBox label="Critical" value={criticalCount} color="red" pulse={criticalCount > 0} />
                </Link>
              </div>
            </div>

            {/* Market Pulse Gauge - Clickable */}
            <Link href="/scanner" className="flex flex-col items-center justify-center cursor-pointer hover:opacity-90 transition-opacity">
              <div className="w-full max-w-[200px] h-[130px]">
                <ReactECharts option={pulseGaugeOptions} style={{ height: '100%', width: '100%' }} />
              </div>
              <p className="text-[10px] text-[hsl(215,20%,50%)] uppercase tracking-wider mt-1">Market Sentiment</p>
              <div className="flex gap-4 mt-2 text-[10px]">
                <span className="text-green-500">Bullish {marketPulse.bullish}%</span>
                <span className="text-red-500">Bearish {marketPulse.bearish}%</span>
              </div>
              <p className="text-[10px] text-[hsl(45,96%,58%)] mt-1">Click to view Scanner →</p>
            </Link>
          </div>
        </div>
      </div>

      {/* Critical Alerts Banner - Clickable */}
      {criticalCount > 0 && (
        <Link href="/discoveries" className="block">
          <div className="terminal-panel border-red-500/50 hover:border-red-500/70 transition-colors cursor-pointer">
            <div className="terminal-panel-header bg-gradient-to-r from-red-500/20 to-transparent">
              <div className="flex items-center gap-2">
                <span className="w-2 h-2 rounded-full bg-red-500 animate-pulse"></span>
                <span className="text-red-500">{criticalCount} CRITICAL ALERT{criticalCount > 1 ? 'S' : ''}</span>
              </div>
              <span className="text-[10px] text-red-400 hover:text-red-300">View All Anomalies →</span>
            </div>
            <div className="p-3 bg-red-500/5">
              <div className="flex gap-4 overflow-x-auto pb-1">
                {anomalies.filter(a => a.severity === 'critical').slice(0, 3).map(anomaly => (
                  <div key={anomaly.id} className="flex-shrink-0 px-3 py-2 rounded bg-red-500/10 border border-red-500/30">
                    <div className="flex items-center gap-2">
                      <span className="text-lg">{ANOMALY_TYPES[anomaly.type].icon}</span>
                      <span className="font-bold text-white">{anomaly.symbol}</span>
                      <span className={`text-sm ${anomaly.change >= 0 ? 'text-green-500' : 'text-red-500'}`}>
                        {anomaly.change >= 0 ? '+' : ''}{anomaly.change.toFixed(1)}%
                      </span>
                    </div>
                    <p className="text-xs text-[hsl(215,20%,60%)] mt-1">{anomaly.message}</p>
                  </div>
                ))}
              </div>
            </div>
          </div>
        </Link>
      )}

      {/* Main Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Live Anomaly Feed */}
        <div className="lg:col-span-2">
          <div className="terminal-panel h-full">
            <div className="terminal-panel-header">
              <div className="flex items-center gap-2">
                <span className="w-1.5 h-1.5 rounded-full bg-yellow-500 animate-pulse"></span>
                <span>LIVE ANOMALY DETECTION</span>
              </div>
              <Link href="/discoveries" className="text-[10px] text-[hsl(45,96%,58%)] hover:text-[hsl(45,96%,70%)]">
                Full Dashboard →
              </Link>
            </div>
            <div className="p-4 bg-[hsl(220,60%,4%)] max-h-[400px] overflow-y-auto">
              <div className="space-y-2">
                {anomalies.map((anomaly, idx) => (
                  <Link
                    key={anomaly.id}
                    href={`/charts?symbol=${anomaly.symbol}`}
                    className={`block p-3 rounded border transition-all cursor-pointer ${
                      anomaly.severity === 'critical'
                        ? 'bg-red-500/10 border-red-500/40 hover:border-red-500/60 hover:bg-red-500/15'
                        : anomaly.severity === 'high'
                        ? 'bg-orange-500/10 border-orange-500/30 hover:border-orange-500/50 hover:bg-orange-500/15'
                        : 'bg-[hsl(215,50%,10%)] border-[hsl(215,40%,16%)] hover:border-[hsl(215,40%,25%)] hover:bg-[hsl(215,50%,12%)]'
                    } ${idx === 0 ? 'animate-slide-in' : ''}`}
                  >
                    <div className="flex items-start justify-between gap-3">
                      <div className="flex items-start gap-3">
                        <span className="text-xl">{ANOMALY_TYPES[anomaly.type].icon}</span>
                        <div>
                          <div className="flex items-center gap-2 mb-1">
                            <span className="font-bold text-white">{anomaly.symbol}</span>
                            <span className={`px-1.5 py-0.5 rounded text-[10px] font-semibold ${
                              anomaly.severity === 'critical' ? 'bg-red-500/20 text-red-400' :
                              anomaly.severity === 'high' ? 'bg-orange-500/20 text-orange-400' :
                              'bg-yellow-500/20 text-yellow-400'
                            }`}>
                              {anomaly.severity.toUpperCase()}
                            </span>
                            <span className={`text-sm font-mono ${anomaly.change >= 0 ? 'text-green-500' : 'text-red-500'}`}>
                              {anomaly.change >= 0 ? '+' : ''}{anomaly.change.toFixed(2)}%
                            </span>
                          </div>
                          <p className="text-sm text-[hsl(215,20%,70%)]">{anomaly.message}</p>
                          <p className="text-[10px] text-[hsl(215,20%,45%)] mt-1">
                            {ANOMALY_TYPES[anomaly.type].label} • {Math.round(anomaly.confidence * 100)}% confidence • Click to view chart
                          </p>
                        </div>
                      </div>
                      <span className="text-[10px] text-[hsl(215,20%,45%)] whitespace-nowrap">
                        {anomaly.detected.toLocaleTimeString()}
                      </span>
                    </div>
                  </Link>
                ))}
              </div>
            </div>
          </div>
        </div>

        {/* Right Column */}
        <div className="space-y-6">
          {/* Anomaly Distribution - Clickable */}
          <Link href="/discoveries" className="block">
            <div className="terminal-panel hover:border-[hsl(215,40%,25%)] transition-colors cursor-pointer">
              <div className="terminal-panel-header">
                <span>ANOMALY DISTRIBUTION</span>
                <span className="text-[10px] text-[hsl(45,96%,58%)]">View All →</span>
              </div>
              <div className="p-4 bg-[hsl(220,60%,4%)]">
                <div className="h-[150px]">
                  <ReactECharts option={anomalyDistOptions} style={{ height: '100%', width: '100%' }} />
                </div>
                <div className="grid grid-cols-2 gap-2 mt-2">
                  {Object.entries(ANOMALY_TYPES).slice(0, 4).map(([key, { label, icon }]) => (
                    <div key={key} className="flex items-center gap-1.5 text-[10px] text-[hsl(215,20%,60%)]">
                      <span>{icon}</span>
                      <span>{label}</span>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          </Link>

          {/* Live Signals - All Clickable */}
          <div className="terminal-panel">
            <div className="terminal-panel-header">
              <div className="flex items-center gap-2">
                <span className="w-1.5 h-1.5 rounded-full bg-green-500 animate-pulse"></span>
                <span>LIVE SIGNALS</span>
              </div>
              <Link href="/signals" className="text-[10px] text-[hsl(45,96%,58%)]">View All →</Link>
            </div>
            <div className="p-3 bg-[hsl(220,60%,4%)]">
              <div className="space-y-2">
                {signals.slice(0, 5).map((signal, idx) => (
                  <Link
                    key={idx}
                    href={`/signals?symbol=${signal.symbol}`}
                    className="flex items-center justify-between p-2 rounded bg-[hsl(215,50%,10%)] border border-[hsl(215,40%,16%)] hover:border-[hsl(215,40%,25%)] hover:bg-[hsl(215,50%,12%)] transition-all cursor-pointer"
                  >
                    <div className="flex items-center gap-2">
                      <span className={`px-1.5 py-0.5 rounded text-[10px] font-bold ${
                        signal.action === 'BUY' ? 'bg-green-500/20 text-green-400' :
                        signal.action === 'SELL' ? 'bg-red-500/20 text-red-400' :
                        'bg-gray-500/20 text-gray-400'
                      }`}>
                        {signal.action}
                      </span>
                      <span className="font-semibold text-white text-sm">{signal.symbol}</span>
                    </div>
                    <div className="text-right">
                      <p className="text-xs font-mono text-[hsl(215,20%,70%)]">${signal.price.toFixed(2)}</p>
                      <p className="text-[10px] text-[hsl(215,20%,50%)]">{Math.round(signal.confidence * 100)}%</p>
                    </div>
                  </Link>
                ))}
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Pattern Detection - All Clickable */}
      <div className="terminal-panel">
        <div className="terminal-panel-header">
          <div className="flex items-center gap-2">
            <span className="w-1.5 h-1.5 rounded-full bg-blue-500 animate-pulse"></span>
            <span>DETECTED CHART PATTERNS</span>
          </div>
          <Link href="/charts" className="text-[10px] text-[hsl(45,96%,58%)]">Open Charts →</Link>
        </div>
        <div className="p-4 bg-[hsl(220,60%,4%)]">
          <div className="grid grid-cols-2 md:grid-cols-4 lg:grid-cols-5 gap-3">
            {patterns.map((pattern, idx) => (
              <Link
                key={pattern.id}
                href={`/charts?symbol=${pattern.symbol}`}
                className={`block p-3 rounded border transition-all hover:scale-[1.02] cursor-pointer ${
                  pattern.direction === 'bullish'
                    ? 'bg-green-500/5 border-green-500/30 hover:border-green-500/50 hover:bg-green-500/10'
                    : pattern.direction === 'bearish'
                    ? 'bg-red-500/5 border-red-500/30 hover:border-red-500/50 hover:bg-red-500/10'
                    : 'bg-[hsl(215,50%,10%)] border-[hsl(215,40%,16%)] hover:border-[hsl(215,40%,25%)] hover:bg-[hsl(215,50%,12%)]'
                } ${idx === 0 ? 'animate-fade-in' : ''}`}
              >
                <div className="flex items-center justify-between mb-2">
                  <span className="font-bold text-white">{pattern.symbol}</span>
                  <span className={`w-2 h-2 rounded-full ${
                    pattern.direction === 'bullish' ? 'bg-green-500' :
                    pattern.direction === 'bearish' ? 'bg-red-500' : 'bg-gray-500'
                  }`}></span>
                </div>
                <p className="text-xs text-[hsl(45,96%,58%)] font-semibold mb-1">{pattern.pattern}</p>
                <div className="flex items-center justify-between text-[10px]">
                  <span className="text-[hsl(215,20%,50%)]">{pattern.timeframe}</span>
                  <span className={pattern.direction === 'bullish' ? 'text-green-400' : pattern.direction === 'bearish' ? 'text-red-400' : 'text-gray-400'}>
                    {Math.round(pattern.confidence * 100)}%
                  </span>
                </div>
                {pattern.priceTarget && (
                  <p className={`text-[10px] mt-1 ${pattern.direction === 'bullish' ? 'text-green-400' : 'text-red-400'}`}>
                    Target: ${pattern.priceTarget.toFixed(2)}
                  </p>
                )}
              </Link>
            ))}
          </div>
        </div>
      </div>

      {/* Quick Access Tools - All Clickable */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        <ToolCard
          title="Advanced Charts"
          description="Real-time with 50+ indicators"
          href="/charts"
          icon="📊"
          color="blue"
        />
        <ToolCard
          title="Stock Screener"
          description="Filter 10K+ securities"
          href="/scanner"
          icon="🔍"
          color="green"
        />
        <ToolCard
          title="Backtesting"
          description="Test strategies on historical data"
          href="/backtesting"
          icon="⚡"
          color="yellow"
        />
        <ToolCard
          title="Options Flow"
          description="Unusual options activity"
          href="/options"
          icon="🎯"
          color="purple"
        />
      </div>

      {/* Congressional Trading - Prominent & Clickable */}
      <Link href="/politicians" className="block">
        <div className="terminal-panel border-[hsl(210,100%,56%)]/30 hover:border-[hsl(210,100%,56%)]/50 transition-colors cursor-pointer">
          <div className="terminal-panel-header bg-gradient-to-r from-[hsl(210,100%,20%)] to-transparent">
            <div className="flex items-center gap-2">
              <span className="text-lg">🏛️</span>
              <span className="text-[hsl(210,100%,70%)]">CONGRESSIONAL TRADING TRACKER</span>
            </div>
            <span className="text-[10px] text-[hsl(142,71%,55%)]">FREE ACCESS →</span>
          </div>
          <div className="p-4 bg-[hsl(220,60%,4%)]">
            <div className="flex flex-col md:flex-row gap-4 items-start md:items-center justify-between">
              <div>
                <p className="text-sm text-[hsl(215,20%,70%)] mb-2">
                  Track what Congress is buying and selling. Exposed from public STOCK Act filings.
                </p>
                <div className="flex gap-4 text-xs text-[hsl(215,20%,55%)]">
                  <span>👤 535 Politicians</span>
                  <span>📈 15K+ Trades</span>
                  <span>🔄 Daily Updates</span>
                </div>
              </div>
              <div className="flex gap-2">
                <span className="btn-secondary text-sm py-2 pointer-events-none">
                  View Politicians →
                </span>
              </div>
            </div>
          </div>
        </div>
      </Link>

      {/* More Tools Grid - All Clickable */}
      <div className="terminal-panel">
        <div className="terminal-panel-header">
          <span>MORE TOOLS</span>
          <Link href="/tools" className="text-[10px] text-[hsl(45,96%,58%)]">See All →</Link>
        </div>
        <div className="p-4 bg-[hsl(220,60%,4%)]">
          <div className="grid grid-cols-2 md:grid-cols-4 lg:grid-cols-6 gap-3">
            <MiniToolLink href="/portfolio" icon="💼" label="Portfolio" />
            <MiniToolLink href="/compare" icon="⚖️" label="Compare" />
            <MiniToolLink href="/network" icon="🕸️" label="Correlation" />
            <MiniToolLink href="/dashboard" icon="📊" label="Dashboard" />
            <MiniToolLink href="/discoveries" icon="🔬" label="Anomalies" />
            <MiniToolLink href="/resources" icon="📚" label="Learn" />
          </div>
        </div>
      </div>

      {/* Footer Stats */}
      <div className="terminal-panel">
        <div className="terminal-panel-header">
          <span>SYSTEM STATUS</span>
        </div>
        <div className="p-3 bg-[hsl(220,60%,4%)] flex flex-wrap items-center justify-between gap-4 text-xs font-mono">
          <div className="flex items-center gap-6 text-[hsl(215,20%,55%)]">
            <span>Engine: <span className="text-[hsl(142,71%,55%)]">ONLINE</span></span>
            <span>Data Feed: <span className="text-[hsl(142,71%,55%)]">LIVE</span></span>
            <span>Latency: <span className="text-white">12ms</span></span>
          </div>
          <span className="text-[hsl(215,20%,45%)]">For educational purposes only. Not financial advice.</span>
        </div>
      </div>
    </div>
  )
}

function StatBox({ label, value, color, pulse }: { label: string; value: number; color: string; pulse?: boolean }) {
  const colors = {
    yellow: 'bg-yellow-500/10 border-yellow-500/30 text-yellow-500 hover:bg-yellow-500/20 hover:border-yellow-500/50',
    blue: 'bg-blue-500/10 border-blue-500/30 text-blue-500 hover:bg-blue-500/20 hover:border-blue-500/50',
    green: 'bg-green-500/10 border-green-500/30 text-green-500 hover:bg-green-500/20 hover:border-green-500/50',
    red: 'bg-red-500/10 border-red-500/30 text-red-500 hover:bg-red-500/20 hover:border-red-500/50',
  }

  return (
    <div className={`p-3 rounded border transition-all cursor-pointer ${colors[color as keyof typeof colors]} ${pulse ? 'animate-pulse' : ''}`}>
      <p className="text-2xl font-bold font-mono">{value}</p>
      <p className="text-[10px] uppercase tracking-wider opacity-70">{label}</p>
    </div>
  )
}

function ToolCard({ title, description, href, icon, color }: {
  title: string; description: string; href: string; icon: string; color: string
}) {
  const colors = {
    blue: 'hover:border-blue-500/50 hover:bg-blue-500/5',
    green: 'hover:border-green-500/50 hover:bg-green-500/5',
    yellow: 'hover:border-yellow-500/50 hover:bg-yellow-500/5',
    purple: 'hover:border-purple-500/50 hover:bg-purple-500/5',
  }

  return (
    <Link
      href={href}
      className={`terminal-panel p-4 transition-all cursor-pointer ${colors[color as keyof typeof colors]} group`}
    >
      <div className="flex items-start gap-3">
        <span className="text-2xl">{icon}</span>
        <div>
          <h3 className="font-semibold text-white group-hover:text-[hsl(45,96%,58%)] transition-colors">{title}</h3>
          <p className="text-xs text-[hsl(215,20%,55%)]">{description}</p>
        </div>
      </div>
    </Link>
  )
}

function MiniToolLink({ href, icon, label }: { href: string; icon: string; label: string }) {
  return (
    <Link
      href={href}
      className="flex items-center gap-2 p-3 rounded bg-[hsl(215,50%,10%)] border border-[hsl(215,40%,16%)] hover:border-[hsl(45,96%,58%)]/50 hover:bg-[hsl(215,50%,12%)] transition-all cursor-pointer"
    >
      <span className="text-lg">{icon}</span>
      <span className="text-sm font-medium text-white">{label}</span>
    </Link>
  )
}
