/**
 * QuantEngines Home - Real Quant Discoveries Dashboard
 * Displays ML predictions, regime analysis, and trading patterns from discovery project
 */

'use client'

import { useMemo } from 'react'
import Link from 'next/link'
import dynamic from 'next/dynamic'
import {
  useStockPredictions,
  useDiscoveries,
  useCriticalAnomalies,
  useDiscoveryStatus,
  usePoliticians
} from '@/lib/hooks'

const ReactECharts = dynamic(() => import('echarts-for-react'), { ssr: false })

export default function Home() {
  // Real data from discovery project
  const { data: predictions, isLoading: predictionsLoading } = useStockPredictions({ limit: 20 })
  const { data: discoveries, isLoading: discoveriesLoading } = useDiscoveries({ minStrength: 0.5 })
  const { data: anomalies, isLoading: anomaliesLoading } = useCriticalAnomalies({ minSeverity: 0.5 })
  const { data: discoveryStatus } = useDiscoveryStatus()
  const { data: politicians } = usePoliticians(5)

  // Aggregate stats
  const stats = useMemo(() => {
    const upPredictions = predictions?.filter(p => p.prediction === 'UP').length || 0
    const downPredictions = predictions?.filter(p => p.prediction === 'DOWN').length || 0
    const total = predictions?.length || 0
    const bullishPercent = total > 0 ? Math.round((upPredictions / total) * 100) : 50

    return {
      predictions: total,
      discoveries: discoveries?.length || 0,
      anomalies: anomalies?.length || 0,
      bullishPercent,
      bearishPercent: 100 - bullishPercent
    }
  }, [predictions, discoveries, anomalies])

  // Market sentiment gauge
  const sentimentGauge = useMemo(() => ({
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
      data: [{ value: stats.bullishPercent }]
    }]
  }), [stats.bullishPercent])

  // Prediction distribution chart
  const predictionChart = useMemo(() => {
    if (!predictions?.length) return null

    const regimes = predictions.reduce((acc, p) => {
      const regime = p.regime || 'Unknown'
      acc[regime] = (acc[regime] || 0) + 1
      return acc
    }, {} as Record<string, number>)

    return {
      backgroundColor: 'transparent',
      tooltip: { trigger: 'item' },
      series: [{
        type: 'pie',
        radius: ['45%', '70%'],
        center: ['50%', '50%'],
        itemStyle: { borderRadius: 4, borderColor: '#0a0f1a', borderWidth: 2 },
        label: { show: false },
        data: Object.entries(regimes).map(([name, value]) => ({
          value,
          name,
          itemStyle: {
            color: name === 'High Activity' ? '#22c55e' :
                   name === 'Low Activity' ? '#eab308' :
                   name === 'Medium Activity' ? '#3b82f6' : '#6b7280'
          }
        }))
      }]
    }
  }, [predictions])

  const isLoading = predictionsLoading || discoveriesLoading || anomaliesLoading

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
            <span className="text-[hsl(215,20%,50%)]">
              Discovery: <span className={discoveryStatus?.available ? 'text-green-500' : 'text-red-500'}>
                {discoveryStatus?.available ? 'CONNECTED' : 'OFFLINE'}
              </span>
            </span>
            <span className="text-[hsl(215,20%,50%)]">
              Models: <span className="text-white">{discoveryStatus?.predictions_count || 0}</span>
            </span>
          </div>
        </div>

        <div className="p-6 bg-gradient-to-br from-[hsl(220,60%,4%)] via-[hsl(220,55%,6%)] to-[hsl(220,60%,4%)]">
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
            {/* Main Title */}
            <div className="lg:col-span-2">
              <h1 className="text-3xl md:text-4xl font-bold mb-3">
                <span className="text-[hsl(45,96%,58%)]">Quant</span>{' '}
                <span className="text-white">Discovery Engine</span>
              </h1>
              <p className="text-[hsl(215,20%,60%)] text-sm md:text-base mb-4 max-w-2xl">
                ML-powered analysis of congressional trading patterns. Regime detection, cyclical analysis,
                and ensemble predictions based on politician stock transactions.
              </p>

              {/* Quick Stats */}
              <div className="grid grid-cols-4 gap-3">
                <Link href="/discoveries">
                  <StatBox label="Predictions" value={stats.predictions} color="blue" loading={isLoading} />
                </Link>
                <Link href="/discoveries">
                  <StatBox label="Discoveries" value={stats.discoveries} color="yellow" loading={isLoading} />
                </Link>
                <Link href="/discoveries">
                  <StatBox label="Anomalies" value={stats.anomalies} color="red" loading={isLoading} />
                </Link>
                <Link href="/politicians">
                  <StatBox label="Politicians" value={politicians?.length || 0} color="purple" loading={isLoading} />
                </Link>
              </div>
            </div>

            {/* ML Sentiment Gauge */}
            <div className="flex flex-col items-center justify-center">
              <div className="w-full max-w-[200px] h-[130px]">
                <ReactECharts option={sentimentGauge} style={{ height: '100%', width: '100%' }} />
              </div>
              <p className="text-[10px] text-[hsl(215,20%,50%)] uppercase tracking-wider mt-1">ML Prediction Sentiment</p>
              <div className="flex gap-4 mt-2 text-[10px]">
                <span className="text-green-500">Bullish {stats.bullishPercent}%</span>
                <span className="text-red-500">Bearish {stats.bearishPercent}%</span>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Main Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* ML Predictions */}
        <div className="lg:col-span-2">
          <div className="terminal-panel h-full">
            <div className="terminal-panel-header">
              <div className="flex items-center gap-2">
                <span className="w-1.5 h-1.5 rounded-full bg-blue-500 animate-pulse"></span>
                <span>ML STOCK PREDICTIONS</span>
              </div>
              <Link href="/discoveries" className="text-[10px] text-[hsl(45,96%,58%)]">
                View All →
              </Link>
            </div>
            <div className="p-4 bg-[hsl(220,60%,4%)] max-h-[400px] overflow-y-auto">
              {predictionsLoading ? (
                <LoadingState />
              ) : predictions?.length ? (
                <div className="space-y-2">
                  {predictions.slice(0, 10).map((pred, idx) => (
                    <Link
                      key={pred.ticker}
                      href={`/charts?symbol=${pred.ticker}`}
                      className={`block p-3 rounded border transition-all cursor-pointer ${
                        pred.prediction === 'UP'
                          ? 'bg-green-500/10 border-green-500/30 hover:border-green-500/50'
                          : 'bg-red-500/10 border-red-500/30 hover:border-red-500/50'
                      }`}
                    >
                      <div className="flex items-start justify-between gap-3">
                        <div className="flex items-start gap-3">
                          <span className={`text-2xl ${pred.prediction === 'UP' ? 'text-green-500' : 'text-red-500'}`}>
                            {pred.prediction === 'UP' ? '↑' : '↓'}
                          </span>
                          <div>
                            <div className="flex items-center gap-2 mb-1">
                              <span className="font-bold text-white text-lg">{pred.ticker}</span>
                              <span className={`px-2 py-0.5 rounded text-xs font-bold ${
                                pred.prediction === 'UP'
                                  ? 'bg-green-500/20 text-green-400'
                                  : 'bg-red-500/20 text-red-400'
                              }`}>
                                {pred.prediction}
                              </span>
                              <span className="text-xs text-[hsl(215,20%,50%)]">
                                {Math.round(pred.confidence * 100)}% confidence
                              </span>
                            </div>
                            <div className="flex flex-wrap gap-2 text-[10px]">
                              {pred.regime && (
                                <span className="px-1.5 py-0.5 rounded bg-purple-500/20 text-purple-400">
                                  {pred.regime}
                                </span>
                              )}
                              {pred.signals?.ml && (
                                <span className="text-[hsl(215,20%,50%)]">
                                  RF: {pred.signals.ml.model_scores?.random_forest || 0} |
                                  LR: {pred.signals.ml.model_scores?.logistic || 0} |
                                  GB: {pred.signals.ml.model_scores?.gradient_boost || 0}
                                </span>
                              )}
                            </div>
                            {pred.signals?.regime && (
                              <p className="text-[10px] text-[hsl(215,20%,45%)] mt-1">
                                Regime prob: {Math.round((pred.signals.regime.regime_probability || 0) * 100)}% •
                                Avg trades: {pred.signals.regime.mean_trades?.toFixed(1) || 'N/A'}
                              </p>
                            )}
                          </div>
                        </div>
                        <span className="text-[10px] text-[hsl(215,20%,45%)]">
                          {pred.timestamp ? new Date(pred.timestamp).toLocaleDateString() : ''}
                        </span>
                      </div>
                    </Link>
                  ))}
                </div>
              ) : (
                <EmptyState message="No predictions available" />
              )}
            </div>
          </div>
        </div>

        {/* Right Column */}
        <div className="space-y-6">
          {/* Regime Distribution */}
          <div className="terminal-panel">
            <div className="terminal-panel-header">
              <span>REGIME DISTRIBUTION</span>
            </div>
            <div className="p-4 bg-[hsl(220,60%,4%)]">
              {predictionChart ? (
                <>
                  <div className="h-[150px]">
                    <ReactECharts option={predictionChart} style={{ height: '100%', width: '100%' }} />
                  </div>
                  <div className="grid grid-cols-2 gap-2 mt-3 text-[10px]">
                    <div className="flex items-center gap-2">
                      <span className="w-2 h-2 rounded-full bg-green-500"></span>
                      <span className="text-[hsl(215,20%,60%)]">High Activity</span>
                    </div>
                    <div className="flex items-center gap-2">
                      <span className="w-2 h-2 rounded-full bg-yellow-500"></span>
                      <span className="text-[hsl(215,20%,60%)]">Low Activity</span>
                    </div>
                    <div className="flex items-center gap-2">
                      <span className="w-2 h-2 rounded-full bg-blue-500"></span>
                      <span className="text-[hsl(215,20%,60%)]">Medium Activity</span>
                    </div>
                  </div>
                </>
              ) : (
                <LoadingState small />
              )}
            </div>
          </div>

          {/* Top Discoveries */}
          <div className="terminal-panel">
            <div className="terminal-panel-header">
              <div className="flex items-center gap-2">
                <span className="w-1.5 h-1.5 rounded-full bg-yellow-500 animate-pulse"></span>
                <span>PATTERN DISCOVERIES</span>
              </div>
              <Link href="/discoveries" className="text-[10px] text-[hsl(45,96%,58%)]">View All →</Link>
            </div>
            <div className="p-3 bg-[hsl(220,60%,4%)] max-h-[250px] overflow-y-auto">
              {discoveriesLoading ? (
                <LoadingState small />
              ) : discoveries?.length ? (
                <div className="space-y-2">
                  {discoveries.slice(0, 5).map((discovery) => (
                    <Link
                      key={discovery.id}
                      href="/politicians"
                      className="block p-2 rounded bg-[hsl(215,50%,10%)] border border-[hsl(215,40%,16%)] hover:border-yellow-500/50 transition-all"
                    >
                      <div className="flex items-center justify-between mb-1">
                        <span className="font-semibold text-white text-sm">{discovery.politician_name}</span>
                        <span className="text-[10px] text-green-400">{Math.round(discovery.strength * 100)}%</span>
                      </div>
                      <p className="text-[10px] text-[hsl(45,96%,58%)]">
                        {discovery.pattern_type.replace(/_/g, ' ')}
                      </p>
                    </Link>
                  ))}
                </div>
              ) : (
                <EmptyState message="No discoveries" small />
              )}
            </div>
          </div>
        </div>
      </div>

      {/* Trading Anomalies */}
      {anomalies && anomalies.length > 0 && (
        <div className="terminal-panel border-red-500/30">
          <div className="terminal-panel-header bg-gradient-to-r from-red-500/20 to-transparent">
            <div className="flex items-center gap-2">
              <span className="w-2 h-2 rounded-full bg-red-500 animate-pulse"></span>
              <span className="text-red-400">TRADING ANOMALIES DETECTED</span>
            </div>
            <Link href="/discoveries" className="text-[10px] text-red-400">View All →</Link>
          </div>
          <div className="p-4 bg-[hsl(220,60%,4%)]">
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-3">
              {anomalies.slice(0, 6).map((anomaly) => (
                <div
                  key={anomaly.id}
                  className={`p-3 rounded border ${
                    anomaly.severity >= 0.8
                      ? 'bg-red-500/10 border-red-500/40'
                      : anomaly.severity >= 0.6
                      ? 'bg-orange-500/10 border-orange-500/30'
                      : 'bg-yellow-500/10 border-yellow-500/30'
                  }`}
                >
                  <div className="flex items-center justify-between mb-2">
                    <span className="font-bold text-white">{anomaly.politician_name}</span>
                    <span className={`px-1.5 py-0.5 rounded text-[10px] font-bold ${
                      anomaly.severity >= 0.8 ? 'bg-red-500/20 text-red-400' :
                      anomaly.severity >= 0.6 ? 'bg-orange-500/20 text-orange-400' :
                      'bg-yellow-500/20 text-yellow-400'
                    }`}>
                      {Math.round(anomaly.severity * 100)}%
                    </span>
                  </div>
                  <p className="text-xs text-[hsl(215,20%,60%)]">{anomaly.anomaly_type.replace(/_/g, ' ')}</p>
                </div>
              ))}
            </div>
          </div>
        </div>
      )}

      {/* Congressional Trading Section */}
      <Link href="/politicians" className="block">
        <div className="terminal-panel border-[hsl(210,100%,56%)]/30 hover:border-[hsl(210,100%,56%)]/50 transition-colors cursor-pointer">
          <div className="terminal-panel-header bg-gradient-to-r from-[hsl(210,100%,20%)] to-transparent">
            <div className="flex items-center gap-2">
              <span className="text-lg">🏛️</span>
              <span className="text-[hsl(210,100%,70%)]">CONGRESSIONAL TRADING ANALYSIS</span>
            </div>
            <span className="text-[10px] text-[hsl(142,71%,55%)]">ML-POWERED →</span>
          </div>
          <div className="p-4 bg-[hsl(220,60%,4%)]">
            <p className="text-sm text-[hsl(215,20%,70%)] mb-3">
              Advanced ML analysis of politician trading patterns. Fourier cycle detection, HMM regime analysis,
              DTW pattern matching, and ensemble predictions.
            </p>
            <div className="flex flex-wrap gap-4 text-xs text-[hsl(215,20%,55%)]">
              <span>🔬 Fourier Analysis</span>
              <span>📊 Regime Detection</span>
              <span>🔄 Cyclical Patterns</span>
              <span>🤖 Ensemble ML</span>
            </div>
          </div>
        </div>
      </Link>

      {/* Quick Access */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        <ToolCard title="Discoveries" description="ML pattern discoveries" href="/discoveries" icon="🔬" color="yellow" />
        <ToolCard title="Politicians" description="Congressional trades" href="/politicians" icon="🏛️" color="blue" />
        <ToolCard title="Network" description="Correlation analysis" href="/network" icon="🕸️" color="purple" />
        <ToolCard title="Charts" description="Technical analysis" href="/charts" icon="📊" color="green" />
      </div>

      {/* System Status */}
      <div className="terminal-panel">
        <div className="terminal-panel-header">
          <span>SYSTEM STATUS</span>
        </div>
        <div className="p-3 bg-[hsl(220,60%,4%)] flex flex-wrap items-center justify-between gap-4 text-xs font-mono">
          <div className="flex items-center gap-6 text-[hsl(215,20%,55%)]">
            <span>Discovery: <span className={discoveryStatus?.available ? 'text-green-500' : 'text-red-500'}>
              {discoveryStatus?.available ? 'ONLINE' : 'OFFLINE'}
            </span></span>
            <span>Models: <span className="text-white">{discoveryStatus?.predictions_count || 0}</span></span>
            <span>API: <span className="text-green-500">CONNECTED</span></span>
          </div>
          <span className="text-[hsl(215,20%,45%)]">ML predictions based on congressional trading data</span>
        </div>
      </div>
    </div>
  )
}

function StatBox({ label, value, color, loading }: { label: string; value: number; color: string; loading?: boolean }) {
  const colors: Record<string, string> = {
    yellow: 'bg-yellow-500/10 border-yellow-500/30 text-yellow-500 hover:bg-yellow-500/20',
    blue: 'bg-blue-500/10 border-blue-500/30 text-blue-500 hover:bg-blue-500/20',
    green: 'bg-green-500/10 border-green-500/30 text-green-500 hover:bg-green-500/20',
    red: 'bg-red-500/10 border-red-500/30 text-red-500 hover:bg-red-500/20',
    purple: 'bg-purple-500/10 border-purple-500/30 text-purple-500 hover:bg-purple-500/20',
  }

  return (
    <div className={`p-3 rounded border transition-all cursor-pointer ${colors[color]}`}>
      {loading ? (
        <div className="h-8 w-12 bg-current/20 rounded animate-pulse"></div>
      ) : (
        <p className="text-2xl font-bold font-mono">{value}</p>
      )}
      <p className="text-[10px] uppercase tracking-wider opacity-70">{label}</p>
    </div>
  )
}

function ToolCard({ title, description, href, icon, color }: {
  title: string; description: string; href: string; icon: string; color: string
}) {
  const colors: Record<string, string> = {
    blue: 'hover:border-blue-500/50 hover:bg-blue-500/5',
    green: 'hover:border-green-500/50 hover:bg-green-500/5',
    yellow: 'hover:border-yellow-500/50 hover:bg-yellow-500/5',
    purple: 'hover:border-purple-500/50 hover:bg-purple-500/5',
  }

  return (
    <Link href={href} className={`terminal-panel p-4 transition-all cursor-pointer ${colors[color]} group`}>
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

function LoadingState({ small }: { small?: boolean }) {
  return (
    <div className={`flex items-center justify-center ${small ? 'h-24' : 'h-48'}`}>
      <div className="animate-spin w-6 h-6 border-2 border-blue-500 border-t-transparent rounded-full"></div>
    </div>
  )
}

function EmptyState({ message, small }: { message: string; small?: boolean }) {
  return (
    <div className={`flex items-center justify-center text-[hsl(215,20%,50%)] ${small ? 'h-24' : 'h-48'}`}>
      {message}
    </div>
  )
}
