/**
 * Politician Detail Page
 * Comprehensive analytics and visualizations for a single politician
 */

'use client'

import { use, useMemo } from 'react'
import {
  usePolitician,
  useTrades,
  useFourierAnalysis,
  useRegimeAnalysis,
  useDTWAnalysis,
  useEnsemblePrediction,
  useInsights,
  useAnomalies,
} from '@/lib/hooks'
import { FourierSpectrumChart } from '@/components/charts/FourierSpectrumChart'
import { RegimeTransitionChart } from '@/components/charts/RegimeTransitionChart'
import { PatternMatchChart } from '@/components/charts/PatternMatchChart'
import { GaugeChart } from '@/components/charts/GaugeChart'
import { RadarChart } from '@/components/charts/RadarChart'
import { AdvancedTimeSeriesChart } from '@/components/charts/AdvancedTimeSeriesChart'
import Link from 'next/link'

export default function PoliticianDetailPage({
  params,
}: {
  params: Promise<{ id: string }>
}) {
  const resolvedParams = use(params)
  const politicianId = resolvedParams.id

  const { data: politician, isLoading: polLoading } = usePolitician(politicianId)
  const { data: trades, isLoading: tradesLoading } = useTrades(politicianId, 50)
  const { data: fourier, isLoading: fourierLoading } = useFourierAnalysis(politicianId, {
    include_forecast: true,
  })
  const { data: regime, isLoading: regimeLoading } = useRegimeAnalysis(politicianId)
  const { data: dtw, isLoading: dtwLoading } = useDTWAnalysis(politicianId)
  const { data: ensemble, isLoading: ensembleLoading } = useEnsemblePrediction(politicianId)
  const { data: insights, isLoading: insightsLoading } = useInsights(politicianId)
  const { data: anomalies, isLoading: anomaliesLoading } = useAnomalies(politicianId)

  // Generate trading activity time series from trades
  const tradingActivityData = useMemo(() => {
    if (!trades || trades.length === 0) return []

    // Group trades by month
    const tradesByMonth: Record<string, number> = {}
    trades.forEach((trade) => {
      const date = new Date(trade.transaction_date)
      const monthKey = `${date.getFullYear()}-${String(date.getMonth() + 1).padStart(2, '0')}-01`
      tradesByMonth[monthKey] = (tradesByMonth[monthKey] || 0) + 1
    })

    return Object.entries(tradesByMonth)
      .map(([timestamp, value]) => ({ timestamp, value }))
      .sort((a, b) => a.timestamp.localeCompare(b.timestamp))
  }, [trades])

  // Generate radar data from ensemble predictions
  const performanceRadarData = useMemo(() => {
    if (!ensemble) {
      return [
        { name: 'Activity', value: 50, max: 100 },
        { name: 'Timing', value: 50, max: 100 },
        { name: 'Consistency', value: 50, max: 100 },
        { name: 'Diversification', value: 50, max: 100 },
        { name: 'Risk Score', value: 50, max: 100 },
      ]
    }

    return [
      { name: 'Activity', value: Math.min(100, (ensemble.predicted_value / 20) * 100), max: 100 },
      { name: 'Confidence', value: ensemble.confidence * 100, max: 100 },
      { name: 'Agreement', value: ensemble.model_agreement * 100, max: 100 },
      { name: 'Signal Strength', value: Math.min(100, Math.abs(ensemble.predicted_value - 10) * 10), max: 100 },
      { name: 'Anomaly Risk', value: anomalies ? anomalies.ensemble_anomaly_score * 100 : 50, max: 100 },
    ]
  }, [ensemble, anomalies])

  if (polLoading) {
    return (
      <div className="flex items-center justify-center min-h-[600px]">
        <div className="text-center">
          <div className="relative">
            <div className="inline-block h-16 w-16 animate-spin rounded-full border-4 border-solid border-indigo-500/20 border-t-indigo-500" />
            <div className="absolute inset-0 h-16 w-16 rounded-full bg-indigo-500/10 blur-xl animate-pulse" />
          </div>
          <p className="mt-6 text-lg font-medium text-slate-400 animate-pulse">
            Loading politician data...
          </p>
        </div>
      </div>
    )
  }

  if (!politician) {
    return (
      <div className="text-center py-20">
        <div className="text-6xl mb-4">🔍</div>
        <h2 className="text-2xl font-bold mb-2 text-white">Politician Not Found</h2>
        <p className="text-slate-400 mb-6">
          The politician you're looking for doesn't exist or has insufficient data.
        </p>
        <Link href="/politicians" className="btn-primary">
          ← Back to Politicians
        </Link>
      </div>
    )
  }

  return (
    <div className="space-y-8">
      {/* Breadcrumb */}
      <div className="text-sm text-slate-400">
        <Link href="/politicians" className="hover:text-white transition-colors">
          Politicians
        </Link>
        <span className="mx-2 text-slate-600">→</span>
        <span className="text-white">{politician.name}</span>
      </div>

      {/* Header */}
      <div className="flex flex-col lg:flex-row gap-6">
        <div className="flex-1">
          <div className="glass-card p-6">
            <div className="flex items-start justify-between">
              <div>
                <h1 className="text-3xl md:text-4xl font-bold text-white mb-3">{politician.name}</h1>
                <div className="flex flex-wrap items-center gap-3">
                  <span className={`px-4 py-1.5 font-semibold rounded-full text-sm ${
                    politician.party === 'Democratic'
                      ? 'bg-blue-500/20 text-blue-400 border border-blue-500/30'
                      : politician.party === 'Republican'
                      ? 'bg-red-500/20 text-red-400 border border-red-500/30'
                      : 'bg-purple-500/20 text-purple-400 border border-purple-500/30'
                  }`}>
                    {politician.party}
                  </span>
                  <span className="text-slate-400">{politician.state}</span>
                  <span className="text-slate-500">•</span>
                  <span className="text-slate-400">{politician.chamber}</span>
                </div>
              </div>
            </div>

            {/* Quick Stats */}
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mt-6 pt-6 border-t border-slate-700/50">
              <div>
                <p className="text-xs text-slate-500 uppercase tracking-wider mb-1">Total Trades</p>
                <p className="text-2xl font-bold text-white">{politician.trade_count?.toLocaleString() || '—'}</p>
              </div>
              <div>
                <p className="text-xs text-slate-500 uppercase tracking-wider mb-1">Days Active</p>
                <p className="text-2xl font-bold text-white">{politician.days_active?.toLocaleString() || '—'}</p>
              </div>
              <div>
                <p className="text-xs text-slate-500 uppercase tracking-wider mb-1">First Trade</p>
                <p className="text-sm font-semibold text-slate-300">
                  {politician.first_trade ? new Date(politician.first_trade).toLocaleDateString() : '—'}
                </p>
              </div>
              <div>
                <p className="text-xs text-slate-500 uppercase tracking-wider mb-1">Last Trade</p>
                <p className="text-sm font-semibold text-slate-300">
                  {politician.last_trade ? new Date(politician.last_trade).toLocaleDateString() : '—'}
                </p>
              </div>
            </div>
          </div>
        </div>

        {/* Anomaly Score Gauge */}
        {anomalies && (
          <div className="w-full lg:w-80">
            <GaugeChart
              value={anomalies.ensemble_anomaly_score * 100}
              title="Anomaly Score"
              subtitle="Unusual trading pattern detection"
              size="md"
              thresholds={{ low: 30, medium: 50, high: 70 }}
            />
          </div>
        )}
      </div>

      {/* Ensemble Prediction & Radar */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {ensemble && (
          <div className="glass-card p-6">
            <h2 className="text-xl font-bold text-white mb-6 flex items-center gap-2">
              <span className="text-2xl">🎯</span>
              Ensemble Prediction
            </h2>

            <div className="grid grid-cols-2 gap-6 mb-6">
              <div className="p-4 rounded-xl bg-slate-800/30 border border-slate-700/50">
                <p className="text-xs text-slate-500 uppercase tracking-wider mb-2">Prediction</p>
                <p className="text-2xl font-bold text-white capitalize">
                  {ensemble.prediction_type.replace('_', ' ')}
                </p>
              </div>
              <div className="p-4 rounded-xl bg-slate-800/30 border border-slate-700/50">
                <p className="text-xs text-slate-500 uppercase tracking-wider mb-2">Expected Trades</p>
                <p className="text-2xl font-bold text-indigo-400">
                  {ensemble.predicted_value.toFixed(1)}
                </p>
                <p className="text-xs text-slate-500">next 30 days</p>
              </div>
            </div>

            <div className="space-y-4">
              <div>
                <div className="flex justify-between text-sm mb-2">
                  <span className="text-slate-400">Confidence</span>
                  <span className="font-semibold text-white">{(ensemble.confidence * 100).toFixed(1)}%</span>
                </div>
                <div className="h-2 bg-slate-800/50 rounded-full overflow-hidden">
                  <div
                    className="h-full bg-gradient-to-r from-indigo-500 to-purple-500 rounded-full transition-all"
                    style={{ width: `${ensemble.confidence * 100}%` }}
                  />
                </div>
              </div>
              <div>
                <div className="flex justify-between text-sm mb-2">
                  <span className="text-slate-400">Model Agreement</span>
                  <span className="font-semibold text-white">{(ensemble.model_agreement * 100).toFixed(1)}%</span>
                </div>
                <div className="h-2 bg-slate-800/50 rounded-full overflow-hidden">
                  <div
                    className="h-full bg-gradient-to-r from-emerald-500 to-green-500 rounded-full transition-all"
                    style={{ width: `${ensemble.model_agreement * 100}%` }}
                  />
                </div>
              </div>
            </div>

            {ensemble.insights.length > 0 && (
              <div className="mt-6 pt-6 border-t border-slate-700/50">
                <p className="text-sm font-semibold text-slate-300 mb-3">Key Insights:</p>
                <div className="space-y-2">
                  {ensemble.insights.slice(0, 3).map((insight, idx) => (
                    <div key={idx} className="flex items-start gap-2 text-sm">
                      <span className="text-indigo-400 mt-0.5">•</span>
                      <span className="text-slate-400">{insight}</span>
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>
        )}

        <RadarChart
          data={performanceRadarData}
          title="Trading Profile Analysis"
          height={350}
          colors={['#6366f1', '#22c55e']}
        />
      </div>

      {/* Trading Activity Timeline */}
      {tradingActivityData.length > 0 && (
        <AdvancedTimeSeriesChart
          data={tradingActivityData}
          title="Monthly Trading Activity"
          seriesName="Trades"
          yAxisLabel="Trade Count"
          color="#6366f1"
          height={350}
          showDataZoom={true}
        />
      )}

      {/* Analysis Charts Row */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Fourier Analysis */}
        {fourier && fourier.dominant_cycles.length > 0 && (
          <div className="glass-card p-6">
            <h2 className="text-lg font-bold text-white mb-4 flex items-center gap-2">
              <span>📊</span> Fourier Cycle Analysis
            </h2>
            <FourierSpectrumChart cycles={fourier.dominant_cycles} />
            <p className="mt-4 text-sm text-slate-400">{fourier.summary}</p>
          </div>
        )}

        {/* Regime Analysis */}
        {regime && (
          <div className="glass-card p-6">
            <h2 className="text-lg font-bold text-white mb-4 flex items-center gap-2">
              <span>🔄</span> Trading Regime Analysis
            </h2>
            <RegimeTransitionChart
              regimes={regime.regimes}
              currentRegime={regime.current_regime}
              transitionProbs={regime.transition_probabilities}
            />
            <p className="mt-4 text-sm text-slate-400">{regime.summary}</p>
          </div>
        )}
      </div>

      {/* DTW Pattern Matching */}
      {dtw && dtw.top_matches.length > 0 && (
        <div className="glass-card p-6">
          <h2 className="text-lg font-bold text-white mb-4 flex items-center gap-2">
            <span>🔍</span> Historical Pattern Matching (DTW)
          </h2>
          <PatternMatchChart matches={dtw.top_matches} />
          <p className="mt-4 text-sm text-slate-400">{dtw.summary}</p>
        </div>
      )}

      {/* Insights */}
      {insights && insights.insights.length > 0 && (
        <div className="glass-card p-6">
          <h2 className="text-xl font-bold text-white mb-6 flex items-center gap-2">
            <span className="text-2xl">💡</span>
            Automated Insights
          </h2>

          <div className="mb-6 p-4 rounded-xl bg-gradient-to-r from-indigo-500/10 to-purple-500/10 border border-indigo-500/20">
            <p className="text-sm font-semibold text-indigo-300 mb-2">Executive Summary</p>
            <p className="text-sm text-slate-300">{insights.executive_summary}</p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {insights.insights.slice(0, 6).map((insight, idx) => (
              <div
                key={idx}
                className={`p-4 rounded-xl border ${
                  insight.severity === 'critical'
                    ? 'border-red-500/30 bg-red-500/5'
                    : insight.severity === 'high'
                    ? 'border-amber-500/30 bg-amber-500/5'
                    : 'border-slate-700/50 bg-slate-800/20'
                }`}
              >
                <div className="flex items-center justify-between mb-2">
                  <span
                    className={`px-2 py-0.5 text-xs font-bold rounded uppercase ${
                      insight.severity === 'critical'
                        ? 'bg-red-500 text-white'
                        : insight.severity === 'high'
                        ? 'bg-amber-500 text-white'
                        : 'bg-indigo-500 text-white'
                    }`}
                  >
                    {insight.severity}
                  </span>
                  <span className="text-xs text-slate-500">
                    {(insight.confidence * 100).toFixed(0)}% confidence
                  </span>
                </div>
                <p className="font-semibold text-sm text-white mb-1">{insight.title}</p>
                <p className="text-xs text-slate-400">{insight.description}</p>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Recent Trades Table */}
      {trades && trades.length > 0 && (
        <div className="glass-card overflow-hidden">
          <div className="p-6 border-b border-slate-700/50">
            <h2 className="text-xl font-bold text-white flex items-center gap-2">
              <span className="text-2xl">📋</span>
              Recent Trades
            </h2>
          </div>
          <div className="overflow-x-auto">
            <table className="table-pro">
              <thead>
                <tr>
                  <th>Date</th>
                  <th>Ticker</th>
                  <th>Type</th>
                  <th>Amount</th>
                  <th>Asset Description</th>
                </tr>
              </thead>
              <tbody>
                {trades.slice(0, 15).map((trade) => (
                  <tr key={trade.id}>
                    <td className="font-mono text-slate-400">
                      {new Date(trade.transaction_date).toLocaleDateString()}
                    </td>
                    <td>
                      <span className="font-mono font-bold text-indigo-400">{trade.ticker}</span>
                    </td>
                    <td>
                      <span
                        className={`px-2 py-1 text-xs font-bold rounded ${
                          trade.transaction_type === 'purchase'
                            ? 'bg-emerald-500/20 text-emerald-400'
                            : 'bg-red-500/20 text-red-400'
                        }`}
                      >
                        {trade.transaction_type.toUpperCase()}
                      </span>
                    </td>
                    <td className="font-semibold">{trade.amount}</td>
                    <td className="text-slate-500 text-xs max-w-xs truncate">
                      {trade.asset_description}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
          {trades.length > 15 && (
            <div className="p-4 text-center border-t border-slate-700/50 bg-slate-800/30">
              <p className="text-sm text-slate-400">
                Showing 15 of {trades.length} trades
              </p>
            </div>
          )}
        </div>
      )}

      {/* Back link */}
      <div className="text-center pt-8">
        <Link href="/politicians" className="btn-secondary">
          ← Back to All Politicians
        </Link>
      </div>
    </div>
  )
}
