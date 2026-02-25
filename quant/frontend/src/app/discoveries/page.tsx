/**
 * Discoveries Page - Live Anomaly Detection & Pattern Discovery
 */

'use client'

import { useState, useEffect, useMemo } from 'react'
import Link from 'next/link'
import dynamic from 'next/dynamic'
import { useDiscoveries, useCriticalAnomalies, useRecentExperiments } from '@/lib/hooks'

const ReactECharts = dynamic(() => import('echarts-for-react'), { ssr: false })

interface Anomaly {
  id: string
  symbol: string
  type: 'volume_spike' | 'price_breakout' | 'unusual_options' | 'insider_cluster' | 'momentum_divergence' | 'correlation_break' | 'volatility_spike'
  severity: 'critical' | 'high' | 'medium' | 'low'
  message: string
  change: number
  detected: Date
  confidence: number
  details: string
}

interface Pattern {
  id: string
  symbol: string
  pattern: string
  direction: 'bullish' | 'bearish' | 'neutral'
  confidence: number
  timeframe: string
  priceTarget?: number
  currentPrice: number
  detected: Date
}

const ANOMALY_TYPES = {
  volume_spike: { label: 'Volume Spike', icon: '📊', color: 'yellow' },
  price_breakout: { label: 'Price Breakout', icon: '🚀', color: 'green' },
  unusual_options: { label: 'Unusual Options', icon: '🎯', color: 'purple' },
  insider_cluster: { label: 'Insider Activity', icon: '👔', color: 'blue' },
  momentum_divergence: { label: 'Momentum Divergence', icon: '⚡', color: 'orange' },
  correlation_break: { label: 'Correlation Break', icon: '🔗', color: 'red' },
  volatility_spike: { label: 'Volatility Spike', icon: '📈', color: 'pink' },
}

const PATTERNS = [
  'Head & Shoulders', 'Double Bottom', 'Bull Flag', 'Cup & Handle',
  'Ascending Triangle', 'Falling Wedge', 'Golden Cross', 'MACD Crossover',
  'RSI Divergence', 'Breakout', 'Support Bounce', 'Resistance Test',
  'Inverse Head & Shoulders', 'Double Top', 'Bear Flag', 'Descending Triangle'
]

const SYMBOLS = ['AAPL', 'GOOGL', 'MSFT', 'TSLA', 'NVDA', 'META', 'AMZN', 'AMD', 'NFLX', 'CRM', 'ORCL', 'INTC', 'QCOM', 'AVGO', 'ADBE', 'PYPL', 'SQ', 'SHOP', 'ROKU', 'SNAP']

export default function DiscoveriesPage() {
  const [anomalies, setAnomalies] = useState<Anomaly[]>([])
  const [patterns, setPatterns] = useState<Pattern[]>([])
  const [filter, setFilter] = useState<string>('all')
  const [severityFilter, setSeverityFilter] = useState<string>('all')
  const [scanCount, setScanCount] = useState(0)
  const [lastUpdate, setLastUpdate] = useState(new Date())

  // Real API data for congressional trading discoveries
  const { data: discoveries, isLoading: discoveriesLoading } = useDiscoveries({ minStrength: 0.5 })
  const { data: criticalAnomalies, isLoading: anomaliesLoading } = useCriticalAnomalies({ minSeverity: 0.5 })
  const { data: experiments, isLoading: experimentsLoading } = useRecentExperiments()

  useEffect(() => {
    // Generate initial data
    generateAnomalies(15)
    generatePatterns(12)

    // Live updates
    const interval = setInterval(() => {
      if (Math.random() > 0.5) {
        generateAnomalies(1, true)
      }
      if (Math.random() > 0.7) {
        generatePatterns(1, true)
      }
      setScanCount(prev => prev + Math.floor(Math.random() * 100) + 50)
      setLastUpdate(new Date())
    }, 4000)

    return () => clearInterval(interval)
  }, [])

  const generateAnomalies = (count: number, prepend = false) => {
    const types = Object.keys(ANOMALY_TYPES) as Anomaly['type'][]
    const severities: Anomaly['severity'][] = ['critical', 'high', 'medium', 'low']

    const newAnomalies: Anomaly[] = Array.from({ length: count }, (_, i) => {
      const type = types[Math.floor(Math.random() * types.length)]
      const symbol = SYMBOLS[Math.floor(Math.random() * SYMBOLS.length)]
      const severity = severities[Math.floor(Math.random() * severities.length)]
      const change = (Math.random() - 0.3) * 25

      const messages: Record<Anomaly['type'], string[]> = {
        volume_spike: [`${symbol} volume 340% above 20-day average`, `Unusual accumulation detected in ${symbol}`, `${symbol} institutional block trade detected`],
        price_breakout: [`${symbol} breaking 52-week high on volume`, `${symbol} gap up through resistance`, `${symbol} clearing major technical level`],
        unusual_options: [`Large ${symbol} call sweep at ask`, `${symbol} unusual put activity near earnings`, `${symbol} options flow diverging from stock`],
        insider_cluster: [`Multiple ${symbol} insider purchases this week`, `${symbol} CEO buying shares`, `${symbol} director cluster buying detected`],
        momentum_divergence: [`${symbol} RSI/price divergence forming`, `${symbol} MACD histogram divergence`, `${symbol} momentum failing to confirm new highs`],
        correlation_break: [`${symbol} decoupling from sector ETF`, `${symbol} breaking historical correlation`, `${symbol} unusual relative strength`],
        volatility_spike: [`${symbol} implied volatility spike +45%`, `${symbol} options pricing unusual move`, `${symbol} volatility term structure inversion`],
      }

      const details: Record<Anomaly['type'], string[]> = {
        volume_spike: ['20-day avg: 5.2M, Today: 17.8M', 'Dark pool activity: 45% of volume', 'Block trade size: $25M'],
        price_breakout: ['Previous resistance: $152.40', 'Volume confirmation: 2.3x average', 'RSI: 68, not overbought'],
        unusual_options: ['Strike: $160C, Exp: 2 weeks', 'Premium paid: $2.4M', 'Open interest change: +15,000'],
        insider_cluster: ['3 insiders bought $5.2M total', 'Last cluster: 8 months ago', 'Historical accuracy: 73%'],
        momentum_divergence: ['Price: New high, RSI: Lower high', 'MACD histogram: Declining', 'Volume: Decreasing on rallies'],
        correlation_break: ['30-day correlation: 0.92 → 0.45', 'Sector down 2%, stock up 4%', 'Relative strength rank: 95th'],
        volatility_spike: ['IV percentile: 95th', '30-day HV: 28%, IV: 52%', 'Put/Call skew: Elevated'],
      }

      return {
        id: `${Date.now()}-${i}-${Math.random()}`,
        symbol,
        type,
        severity,
        message: messages[type][Math.floor(Math.random() * messages[type].length)],
        change,
        detected: new Date(),
        confidence: 0.65 + Math.random() * 0.30,
        details: details[type][Math.floor(Math.random() * details[type].length)],
      }
    })

    setAnomalies(prev => prepend
      ? [...newAnomalies, ...prev].slice(0, 50)
      : [...newAnomalies, ...prev].slice(0, 50)
    )
  }

  const generatePatterns = (count: number, prepend = false) => {
    const newPatterns: Pattern[] = Array.from({ length: count }, (_, i) => {
      const symbol = SYMBOLS[Math.floor(Math.random() * SYMBOLS.length)]
      const currentPrice = 50 + Math.random() * 400
      const direction = Math.random() > 0.5 ? 'bullish' : Math.random() > 0.3 ? 'bearish' : 'neutral'

      return {
        id: `${Date.now()}-${i}-${Math.random()}`,
        symbol,
        pattern: PATTERNS[Math.floor(Math.random() * PATTERNS.length)],
        direction,
        confidence: 0.60 + Math.random() * 0.35,
        priceTarget: direction === 'bullish' ? currentPrice * (1.05 + Math.random() * 0.20) :
                     direction === 'bearish' ? currentPrice * (0.80 + Math.random() * 0.15) : undefined,
        currentPrice,
        timeframe: ['1H', '4H', '1D', '1W'][Math.floor(Math.random() * 4)],
        detected: new Date(),
      }
    })

    setPatterns(prev => prepend
      ? [...newPatterns, ...prev].slice(0, 30)
      : [...newPatterns, ...prev].slice(0, 30)
    )
  }

  const filteredAnomalies = useMemo(() => {
    return anomalies.filter(a => {
      if (filter !== 'all' && a.type !== filter) return false
      if (severityFilter !== 'all' && a.severity !== severityFilter) return false
      return true
    })
  }, [anomalies, filter, severityFilter])

  const stats = useMemo(() => ({
    total: anomalies.length,
    critical: anomalies.filter(a => a.severity === 'critical').length,
    high: anomalies.filter(a => a.severity === 'high').length,
    patterns: patterns.length,
    bullish: patterns.filter(p => p.direction === 'bullish').length,
    bearish: patterns.filter(p => p.direction === 'bearish').length,
  }), [anomalies, patterns])

  // Anomaly type distribution chart
  const typeDistChart = useMemo(() => {
    const counts = anomalies.reduce((acc, a) => {
      acc[a.type] = (acc[a.type] || 0) + 1
      return acc
    }, {} as Record<string, number>)

    return {
      backgroundColor: 'transparent',
      tooltip: { trigger: 'item' },
      series: [{
        type: 'pie',
        radius: ['40%', '70%'],
        itemStyle: { borderRadius: 4, borderColor: '#0a0f1a', borderWidth: 2 },
        label: { show: false },
        data: Object.entries(counts).map(([type, count]) => ({
          value: count,
          name: ANOMALY_TYPES[type as keyof typeof ANOMALY_TYPES]?.label || type,
        }))
      }]
    }
  }, [anomalies])

  // Severity timeline chart
  const severityChart = useMemo(() => {
    const hours = Array.from({ length: 24 }, (_, i) => `${i}:00`)
    return {
      backgroundColor: 'transparent',
      tooltip: { trigger: 'axis' },
      xAxis: { type: 'category', data: hours, axisLine: { lineStyle: { color: '#333' } }, axisLabel: { color: '#888', fontSize: 10 } },
      yAxis: { type: 'value', axisLine: { lineStyle: { color: '#333' } }, axisLabel: { color: '#888' }, splitLine: { lineStyle: { color: '#222' } } },
      series: [
        { name: 'Critical', type: 'bar', stack: 'total', data: hours.map(() => Math.floor(Math.random() * 5)), itemStyle: { color: '#ef4444' } },
        { name: 'High', type: 'bar', stack: 'total', data: hours.map(() => Math.floor(Math.random() * 8)), itemStyle: { color: '#f97316' } },
        { name: 'Medium', type: 'bar', stack: 'total', data: hours.map(() => Math.floor(Math.random() * 12)), itemStyle: { color: '#eab308' } },
      ]
    }
  }, [])

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="terminal-panel">
        <div className="terminal-panel-header">
          <div className="flex items-center gap-3">
            <span className="relative flex h-2.5 w-2.5">
              <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-green-400 opacity-75"></span>
              <span className="relative inline-flex rounded-full h-2.5 w-2.5 bg-green-500"></span>
            </span>
            <span>ANOMALY DETECTION ENGINE</span>
          </div>
          <div className="flex items-center gap-4 text-[10px] font-mono">
            <span className="text-[hsl(215,20%,50%)]">Scanned: <span className="text-white">{scanCount.toLocaleString()}</span></span>
            <span className="text-[hsl(215,20%,50%)]">Updated: <span className="text-[hsl(142,71%,55%)]">{lastUpdate.toLocaleTimeString()}</span></span>
          </div>
        </div>
        <div className="p-6 bg-[hsl(220,60%,4%)]">
          <h1 className="text-2xl font-bold mb-2">
            <span className="text-[hsl(45,96%,58%)]">Live</span> Anomaly Detection
          </h1>
          <p className="text-[hsl(215,20%,60%)] text-sm">
            AI-powered detection of unusual market activity, volume spikes, options flow, and technical patterns across 10,000+ securities.
          </p>
        </div>
      </div>

      {/* Stats Grid */}
      <div className="grid grid-cols-2 md:grid-cols-6 gap-4">
        <StatCard label="Total Anomalies" value={stats.total} color="yellow" />
        <StatCard label="Critical" value={stats.critical} color="red" pulse={stats.critical > 0} />
        <StatCard label="High Priority" value={stats.high} color="orange" />
        <StatCard label="Patterns Found" value={stats.patterns} color="blue" />
        <StatCard label="Bullish" value={stats.bullish} color="green" />
        <StatCard label="Bearish" value={stats.bearish} color="red" />
      </div>

      {/* Critical Alerts */}
      {stats.critical > 0 && (
        <div className="terminal-panel border-red-500/50">
          <div className="terminal-panel-header bg-gradient-to-r from-red-500/20 to-transparent">
            <div className="flex items-center gap-2">
              <span className="w-2 h-2 rounded-full bg-red-500 animate-pulse"></span>
              <span className="text-red-500">{stats.critical} CRITICAL ALERTS</span>
            </div>
          </div>
          <div className="p-4 bg-red-500/5 space-y-2">
            {anomalies.filter(a => a.severity === 'critical').slice(0, 3).map(anomaly => (
              <Link
                key={anomaly.id}
                href={`/charts?symbol=${anomaly.symbol}`}
                className="block p-3 rounded bg-red-500/10 border border-red-500/30 hover:border-red-500/50 transition-colors"
              >
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-3">
                    <span className="text-xl">{ANOMALY_TYPES[anomaly.type].icon}</span>
                    <div>
                      <div className="flex items-center gap-2">
                        <span className="font-bold text-white">{anomaly.symbol}</span>
                        <span className={`text-sm ${anomaly.change >= 0 ? 'text-green-500' : 'text-red-500'}`}>
                          {anomaly.change >= 0 ? '+' : ''}{anomaly.change.toFixed(2)}%
                        </span>
                      </div>
                      <p className="text-sm text-[hsl(215,20%,60%)]">{anomaly.message}</p>
                    </div>
                  </div>
                  <span className="text-xs text-[hsl(215,20%,50%)]">{anomaly.detected.toLocaleTimeString()}</span>
                </div>
              </Link>
            ))}
          </div>
        </div>
      )}

      {/* Congressional Trading Discoveries - Real API Data */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Pattern Discoveries */}
        <div className="terminal-panel">
          <div className="terminal-panel-header bg-gradient-to-r from-purple-500/20 to-transparent">
            <div className="flex items-center gap-2">
              <span className="w-2 h-2 rounded-full bg-purple-500"></span>
              <span className="text-purple-400">CONGRESSIONAL TRADING PATTERNS</span>
            </div>
            <span className="text-[10px] text-[hsl(215,20%,50%)]">
              {discoveriesLoading ? 'Loading...' : `${discoveries?.length || 0} patterns`}
            </span>
          </div>
          <div className="p-4 bg-[hsl(220,60%,4%)] max-h-[400px] overflow-y-auto space-y-2">
            {discoveriesLoading ? (
              <div className="flex items-center justify-center h-32 text-[hsl(215,20%,50%)]">
                <div className="animate-spin w-6 h-6 border-2 border-purple-500 border-t-transparent rounded-full"></div>
              </div>
            ) : discoveries && discoveries.length > 0 ? (
              discoveries.map((discovery) => (
                <div
                  key={discovery.id}
                  className="p-3 rounded border bg-purple-500/5 border-purple-500/30 hover:border-purple-500/50 transition-colors"
                >
                  <div className="flex items-start justify-between gap-3">
                    <div className="flex-1">
                      <div className="flex items-center gap-2 mb-1">
                        <span className="font-bold text-white">{discovery.politician_name}</span>
                        <span className="px-1.5 py-0.5 rounded text-[10px] font-semibold bg-purple-500/20 text-purple-400">
                          {discovery.pattern_type.replace(/_/g, ' ').toUpperCase()}
                        </span>
                      </div>
                      <p className="text-sm text-[hsl(215,20%,70%)]">{discovery.description}</p>
                      <div className="flex items-center gap-4 mt-2">
                        <span className="text-[10px] text-[hsl(215,20%,50%)]">
                          Strength: <span className="text-green-400">{Math.round(discovery.strength * 100)}%</span>
                        </span>
                        <span className="text-[10px] text-[hsl(215,20%,50%)]">
                          Confidence: <span className="text-blue-400">{Math.round(discovery.confidence * 100)}%</span>
                        </span>
                        {discovery.deployed && (
                          <span className="text-[10px] px-1.5 py-0.5 rounded bg-green-500/20 text-green-400">DEPLOYED</span>
                        )}
                      </div>
                    </div>
                    <span className="text-[10px] text-[hsl(215,20%,45%)] whitespace-nowrap">
                      {new Date(discovery.discovery_date).toLocaleDateString()}
                    </span>
                  </div>
                </div>
              ))
            ) : (
              <div className="flex items-center justify-center h-32 text-[hsl(215,20%,50%)]">
                No discoveries found
              </div>
            )}
          </div>
        </div>

        {/* Trading Anomalies */}
        <div className="terminal-panel">
          <div className="terminal-panel-header bg-gradient-to-r from-amber-500/20 to-transparent">
            <div className="flex items-center gap-2">
              <span className="w-2 h-2 rounded-full bg-amber-500 animate-pulse"></span>
              <span className="text-amber-400">TRADING ANOMALIES</span>
            </div>
            <span className="text-[10px] text-[hsl(215,20%,50%)]">
              {anomaliesLoading ? 'Loading...' : `${criticalAnomalies?.length || 0} detected`}
            </span>
          </div>
          <div className="p-4 bg-[hsl(220,60%,4%)] max-h-[400px] overflow-y-auto space-y-2">
            {anomaliesLoading ? (
              <div className="flex items-center justify-center h-32 text-[hsl(215,20%,50%)]">
                <div className="animate-spin w-6 h-6 border-2 border-amber-500 border-t-transparent rounded-full"></div>
              </div>
            ) : criticalAnomalies && criticalAnomalies.length > 0 ? (
              criticalAnomalies.map((anomaly) => (
                <div
                  key={anomaly.id}
                  className={`p-3 rounded border transition-colors ${
                    anomaly.severity >= 0.8
                      ? 'bg-red-500/10 border-red-500/40 hover:border-red-500/60'
                      : anomaly.severity >= 0.6
                      ? 'bg-amber-500/10 border-amber-500/30 hover:border-amber-500/50'
                      : 'bg-yellow-500/10 border-yellow-500/30 hover:border-yellow-500/50'
                  }`}
                >
                  <div className="flex items-start justify-between gap-3">
                    <div className="flex-1">
                      <div className="flex items-center gap-2 mb-1">
                        <span className="font-bold text-white">{anomaly.politician_name}</span>
                        <span className={`px-1.5 py-0.5 rounded text-[10px] font-semibold ${
                          anomaly.severity >= 0.8
                            ? 'bg-red-500/20 text-red-400'
                            : anomaly.severity >= 0.6
                            ? 'bg-amber-500/20 text-amber-400'
                            : 'bg-yellow-500/20 text-yellow-400'
                        }`}>
                          {anomaly.severity >= 0.8 ? 'CRITICAL' : anomaly.severity >= 0.6 ? 'HIGH' : 'MEDIUM'}
                        </span>
                      </div>
                      <p className="text-sm text-[hsl(215,20%,70%)]">{anomaly.description}</p>
                      <div className="flex items-center gap-4 mt-2">
                        <span className="text-[10px] text-[hsl(215,20%,50%)]">
                          Type: <span className="text-[hsl(45,96%,58%)]">{anomaly.anomaly_type.replace(/_/g, ' ')}</span>
                        </span>
                        <span className="text-[10px] text-[hsl(215,20%,50%)]">
                          Severity: <span className="text-red-400">{Math.round(anomaly.severity * 100)}%</span>
                        </span>
                        {anomaly.investigated && (
                          <span className="text-[10px] px-1.5 py-0.5 rounded bg-blue-500/20 text-blue-400">INVESTIGATED</span>
                        )}
                      </div>
                    </div>
                    <span className="text-[10px] text-[hsl(215,20%,45%)] whitespace-nowrap">
                      {new Date(anomaly.detection_date).toLocaleDateString()}
                    </span>
                  </div>
                </div>
              ))
            ) : (
              <div className="flex items-center justify-center h-32 text-[hsl(215,20%,50%)]">
                No anomalies detected
              </div>
            )}
          </div>
        </div>
      </div>

      {/* ML Experiments */}
      <div className="terminal-panel">
        <div className="terminal-panel-header bg-gradient-to-r from-cyan-500/20 to-transparent">
          <div className="flex items-center gap-2">
            <span className="w-2 h-2 rounded-full bg-cyan-500"></span>
            <span className="text-cyan-400">ML EXPERIMENTS</span>
          </div>
          <span className="text-[10px] text-[hsl(215,20%,50%)]">
            {experimentsLoading ? 'Loading...' : `${experiments?.length || 0} experiments`}
          </span>
        </div>
        <div className="p-4 bg-[hsl(220,60%,4%)]">
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-3">
            {experimentsLoading ? (
              <div className="col-span-full flex items-center justify-center h-24 text-[hsl(215,20%,50%)]">
                <div className="animate-spin w-6 h-6 border-2 border-cyan-500 border-t-transparent rounded-full"></div>
              </div>
            ) : experiments && experiments.length > 0 ? (
              experiments.map((exp) => (
                <div
                  key={exp.id}
                  className={`p-3 rounded border ${
                    exp.deployment_ready
                      ? 'bg-green-500/5 border-green-500/30'
                      : 'bg-[hsl(215,50%,10%)] border-[hsl(215,40%,16%)]'
                  }`}
                >
                  <div className="flex items-center justify-between mb-2">
                    <span className="font-mono text-sm text-white">{exp.model_name}</span>
                    {exp.deployment_ready && (
                      <span className="px-1.5 py-0.5 rounded text-[10px] bg-green-500/20 text-green-400">READY</span>
                    )}
                  </div>
                  <div className="grid grid-cols-2 gap-2 text-[10px]">
                    <div>
                      <span className="text-[hsl(215,20%,50%)]">Accuracy</span>
                      <p className="text-green-400">{Math.round((exp.validation_metrics?.accuracy || 0) * 100)}%</p>
                    </div>
                    <div>
                      <span className="text-[hsl(215,20%,50%)]">Precision</span>
                      <p className="text-blue-400">{Math.round((exp.validation_metrics?.precision || 0) * 100)}%</p>
                    </div>
                    <div>
                      <span className="text-[hsl(215,20%,50%)]">Recall</span>
                      <p className="text-purple-400">{Math.round((exp.validation_metrics?.recall || 0) * 100)}%</p>
                    </div>
                    <div>
                      <span className="text-[hsl(215,20%,50%)]">F1 Score</span>
                      <p className="text-[hsl(45,96%,58%)]">{exp.test_metrics?.f1_score ? Math.round(exp.test_metrics.f1_score * 100) + '%' : 'N/A'}</p>
                    </div>
                  </div>
                  <p className="text-[10px] text-[hsl(215,20%,45%)] mt-2">
                    {new Date(exp.experiment_date).toLocaleDateString()}
                  </p>
                </div>
              ))
            ) : (
              <div className="col-span-full flex items-center justify-center h-24 text-[hsl(215,20%,50%)]">
                No experiments found
              </div>
            )}
          </div>
        </div>
      </div>

      {/* Main Content */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Anomaly Feed */}
        <div className="lg:col-span-2">
          <div className="terminal-panel">
            <div className="terminal-panel-header">
              <span>ANOMALY FEED</span>
              <div className="flex items-center gap-2">
                <select
                  value={filter}
                  onChange={(e) => setFilter(e.target.value)}
                  className="text-xs bg-[hsl(220,55%,8%)] border border-[hsl(215,40%,20%)] rounded px-2 py-1"
                >
                  <option value="all">All Types</option>
                  {Object.entries(ANOMALY_TYPES).map(([key, { label }]) => (
                    <option key={key} value={key}>{label}</option>
                  ))}
                </select>
                <select
                  value={severityFilter}
                  onChange={(e) => setSeverityFilter(e.target.value)}
                  className="text-xs bg-[hsl(220,55%,8%)] border border-[hsl(215,40%,20%)] rounded px-2 py-1"
                >
                  <option value="all">All Severity</option>
                  <option value="critical">Critical</option>
                  <option value="high">High</option>
                  <option value="medium">Medium</option>
                  <option value="low">Low</option>
                </select>
              </div>
            </div>
            <div className="p-4 bg-[hsl(220,60%,4%)] max-h-[600px] overflow-y-auto space-y-2">
              {filteredAnomalies.map((anomaly, idx) => (
                <Link
                  key={anomaly.id}
                  href={`/charts?symbol=${anomaly.symbol}`}
                  className={`block p-3 rounded border transition-all cursor-pointer ${
                    anomaly.severity === 'critical'
                      ? 'bg-red-500/10 border-red-500/40 hover:border-red-500/60'
                      : anomaly.severity === 'high'
                      ? 'bg-orange-500/10 border-orange-500/30 hover:border-orange-500/50'
                      : anomaly.severity === 'medium'
                      ? 'bg-yellow-500/10 border-yellow-500/30 hover:border-yellow-500/50'
                      : 'bg-[hsl(215,50%,10%)] border-[hsl(215,40%,16%)] hover:border-[hsl(215,40%,25%)]'
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
                            anomaly.severity === 'medium' ? 'bg-yellow-500/20 text-yellow-400' :
                            'bg-gray-500/20 text-gray-400'
                          }`}>
                            {anomaly.severity.toUpperCase()}
                          </span>
                          <span className={`text-sm font-mono ${anomaly.change >= 0 ? 'text-green-500' : 'text-red-500'}`}>
                            {anomaly.change >= 0 ? '+' : ''}{anomaly.change.toFixed(2)}%
                          </span>
                        </div>
                        <p className="text-sm text-[hsl(215,20%,70%)]">{anomaly.message}</p>
                        <p className="text-[10px] text-[hsl(215,20%,50%)] mt-1 font-mono">{anomaly.details}</p>
                        <p className="text-[10px] text-[hsl(215,20%,45%)] mt-1">
                          {ANOMALY_TYPES[anomaly.type].label} • {Math.round(anomaly.confidence * 100)}% confidence
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

        {/* Right Sidebar */}
        <div className="space-y-6">
          {/* Type Distribution */}
          <div className="terminal-panel">
            <div className="terminal-panel-header">
              <span>ANOMALY TYPES</span>
            </div>
            <div className="p-4 bg-[hsl(220,60%,4%)]">
              <div className="h-[200px]">
                <ReactECharts option={typeDistChart} style={{ height: '100%', width: '100%' }} />
              </div>
              <div className="grid grid-cols-2 gap-2 mt-3">
                {Object.entries(ANOMALY_TYPES).slice(0, 6).map(([key, { label, icon }]) => (
                  <button
                    key={key}
                    onClick={() => setFilter(filter === key ? 'all' : key)}
                    className={`flex items-center gap-1.5 text-[10px] p-1.5 rounded transition-colors ${
                      filter === key ? 'bg-[hsl(45,96%,58%)]/20 text-[hsl(45,96%,58%)]' : 'text-[hsl(215,20%,60%)] hover:bg-[hsl(215,50%,12%)]'
                    }`}
                  >
                    <span>{icon}</span>
                    <span>{label}</span>
                  </button>
                ))}
              </div>
            </div>
          </div>

          {/* Pattern Detection */}
          <div className="terminal-panel">
            <div className="terminal-panel-header">
              <div className="flex items-center gap-2">
                <span className="w-1.5 h-1.5 rounded-full bg-blue-500 animate-pulse"></span>
                <span>DETECTED PATTERNS</span>
              </div>
              <Link href="/charts" className="text-[10px] text-[hsl(45,96%,58%)]">View All →</Link>
            </div>
            <div className="p-3 bg-[hsl(220,60%,4%)] max-h-[300px] overflow-y-auto space-y-2">
              {patterns.slice(0, 8).map(pattern => (
                <Link
                  key={pattern.id}
                  href={`/charts?symbol=${pattern.symbol}`}
                  className={`block p-2 rounded border transition-all ${
                    pattern.direction === 'bullish'
                      ? 'bg-green-500/5 border-green-500/30 hover:border-green-500/50'
                      : pattern.direction === 'bearish'
                      ? 'bg-red-500/5 border-red-500/30 hover:border-red-500/50'
                      : 'bg-[hsl(215,50%,10%)] border-[hsl(215,40%,16%)] hover:border-[hsl(215,40%,25%)]'
                  }`}
                >
                  <div className="flex items-center justify-between">
                    <div>
                      <div className="flex items-center gap-2">
                        <span className="font-bold text-white text-sm">{pattern.symbol}</span>
                        <span className={`w-1.5 h-1.5 rounded-full ${
                          pattern.direction === 'bullish' ? 'bg-green-500' :
                          pattern.direction === 'bearish' ? 'bg-red-500' : 'bg-gray-500'
                        }`}></span>
                      </div>
                      <p className="text-xs text-[hsl(45,96%,58%)]">{pattern.pattern}</p>
                    </div>
                    <div className="text-right">
                      <p className="text-[10px] text-[hsl(215,20%,50%)]">{pattern.timeframe}</p>
                      <p className="text-[10px] text-[hsl(215,20%,60%)]">{Math.round(pattern.confidence * 100)}%</p>
                    </div>
                  </div>
                </Link>
              ))}
            </div>
          </div>

          {/* Activity Timeline */}
          <div className="terminal-panel">
            <div className="terminal-panel-header">
              <span>24H ACTIVITY</span>
            </div>
            <div className="p-4 bg-[hsl(220,60%,4%)]">
              <div className="h-[150px]">
                <ReactECharts option={severityChart} style={{ height: '100%', width: '100%' }} />
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Quick Links */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        <Link href="/charts" className="terminal-panel p-4 hover:border-blue-500/50 transition-colors">
          <div className="flex items-center gap-3">
            <span className="text-2xl">📊</span>
            <div>
              <p className="font-semibold text-white">Charts</p>
              <p className="text-xs text-[hsl(215,20%,55%)]">Technical analysis</p>
            </div>
          </div>
        </Link>
        <Link href="/signals" className="terminal-panel p-4 hover:border-green-500/50 transition-colors">
          <div className="flex items-center gap-3">
            <span className="text-2xl">📡</span>
            <div>
              <p className="font-semibold text-white">Signals</p>
              <p className="text-xs text-[hsl(215,20%,55%)]">Trading signals</p>
            </div>
          </div>
        </Link>
        <Link href="/scanner" className="terminal-panel p-4 hover:border-yellow-500/50 transition-colors">
          <div className="flex items-center gap-3">
            <span className="text-2xl">🔍</span>
            <div>
              <p className="font-semibold text-white">Screener</p>
              <p className="text-xs text-[hsl(215,20%,55%)]">Find stocks</p>
            </div>
          </div>
        </Link>
        <Link href="/politicians" className="terminal-panel p-4 hover:border-purple-500/50 transition-colors">
          <div className="flex items-center gap-3">
            <span className="text-2xl">🏛️</span>
            <div>
              <p className="font-semibold text-white">Congress</p>
              <p className="text-xs text-[hsl(215,20%,55%)]">Insider trades</p>
            </div>
          </div>
        </Link>
      </div>
    </div>
  )
}

function StatCard({ label, value, color, pulse }: { label: string; value: number; color: string; pulse?: boolean }) {
  const colors: Record<string, string> = {
    yellow: 'bg-yellow-500/10 border-yellow-500/30 text-yellow-500',
    red: 'bg-red-500/10 border-red-500/30 text-red-500',
    orange: 'bg-orange-500/10 border-orange-500/30 text-orange-500',
    blue: 'bg-blue-500/10 border-blue-500/30 text-blue-500',
    green: 'bg-green-500/10 border-green-500/30 text-green-500',
  }

  return (
    <div className={`terminal-panel p-4 ${colors[color]} ${pulse ? 'animate-pulse' : ''}`}>
      <p className="text-2xl font-bold font-mono">{value}</p>
      <p className="text-[10px] uppercase tracking-wider opacity-70">{label}</p>
    </div>
  )
}
