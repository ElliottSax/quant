/**
 * Politician Detail Page
 * Comprehensive analytics and visualizations for a single politician
 */

'use client'

import { use } from 'react'
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
import { AnomalyScoreGauge } from '@/components/charts/AnomalyScoreGauge'
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

  if (polLoading) {
    return (
      <div className="flex items-center justify-center min-h-[400px]">
        <div className="text-center">
          <div className="inline-block h-8 w-8 animate-spin rounded-full border-4 border-solid border-current border-r-transparent" />
          <p className="mt-4 text-muted-foreground">Loading politician data...</p>
        </div>
      </div>
    )
  }

  if (!politician) {
    return (
      <div className="text-center py-12">
        <h2 className="text-2xl font-bold mb-2">Politician Not Found</h2>
        <p className="text-muted-foreground mb-4">
          The politician you're looking for doesn't exist or has insufficient data.
        </p>
        <Link href="/politicians" className="text-primary hover:underline">
          ← Back to Politicians
        </Link>
      </div>
    )
  }

  return (
    <div className="space-y-8">
      {/* Breadcrumb */}
      <div className="text-sm text-muted-foreground">
        <Link href="/politicians" className="hover:text-foreground transition-colors">
          Politicians
        </Link>
        <span className="mx-2">→</span>
        <span>{politician.name}</span>
      </div>

      {/* Header */}
      <div className="flex items-start justify-between">
        <div>
          <h1 className="text-3xl font-bold">{politician.name}</h1>
          <div className="flex items-center gap-4 mt-2 text-sm">
            <span className={`inline-flex px-3 py-1 font-semibold rounded-full ${
              politician.party === 'Democratic'
                ? 'bg-blue-500/10 text-blue-500'
                : politician.party === 'Republican'
                ? 'bg-red-500/10 text-red-500'
                : 'bg-gray-500/10 text-gray-500'
            }`}>
              {politician.party}
            </span>
            <span className="text-muted-foreground">{politician.state}</span>
            <span className="text-muted-foreground">{politician.chamber}</span>
          </div>
        </div>

        {anomalies && (
          <div className="hidden lg:block">
            <AnomalyScoreGauge
              score={anomalies.ensemble_anomaly_score}
              size={150}
            />
          </div>
        )}
      </div>

      {/* Ensemble Prediction */}
      {ensemble && (
        <div className="bg-card border border-border rounded-lg p-6">
          <h2 className="text-xl font-semibold mb-4">Ensemble Prediction</h2>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
            <div>
              <p className="text-sm text-muted-foreground mb-1">Prediction Type</p>
              <p className="text-2xl font-bold capitalize">
                {ensemble.prediction_type.replace('_', ' ')}
              </p>
              <p className="text-xs text-muted-foreground mt-1">
                {ensemble.interpretation}
              </p>
            </div>

            <div>
              <p className="text-sm text-muted-foreground mb-1">Predicted Value</p>
              <p className="text-2xl font-bold">
                {ensemble.predicted_value.toFixed(1)}
              </p>
              <p className="text-xs text-muted-foreground mt-1">
                Trades in next 30 days
              </p>
            </div>

            <div>
              <p className="text-sm text-muted-foreground mb-1">Confidence</p>
              <p className="text-2xl font-bold">
                {(ensemble.confidence * 100).toFixed(1)}%
              </p>
              <div className="w-full h-2 bg-muted rounded-full overflow-hidden mt-2">
                <div
                  className="h-full bg-primary rounded-full transition-all"
                  style={{ width: `${ensemble.confidence * 100}%` }}
                />
              </div>
            </div>

            <div>
              <p className="text-sm text-muted-foreground mb-1">Model Agreement</p>
              <p className="text-2xl font-bold">
                {(ensemble.model_agreement * 100).toFixed(1)}%
              </p>
              <div className="w-full h-2 bg-muted rounded-full overflow-hidden mt-2">
                <div
                  className="h-full bg-green-500 rounded-full transition-all"
                  style={{ width: `${ensemble.model_agreement * 100}%` }}
                />
              </div>
            </div>
          </div>

          {ensemble.insights.length > 0 && (
            <div className="mt-6 space-y-2">
              <p className="text-sm font-medium">Key Insights:</p>
              {ensemble.insights.map((insight, idx) => (
                <div key={idx} className="flex items-start gap-2 text-sm">
                  <span className="text-primary mt-0.5">•</span>
                  <span className="text-muted-foreground">{insight}</span>
                </div>
              ))}
            </div>
          )}
        </div>
      )}

      {/* Fourier Analysis */}
      {fourier && fourier.dominant_cycles.length > 0 && (
        <div className="bg-card border border-border rounded-lg p-6">
          <FourierSpectrumChart cycles={fourier.dominant_cycles} />
          <p className="mt-4 text-sm text-muted-foreground">{fourier.summary}</p>
        </div>
      )}

      {/* Regime Analysis */}
      {regime && (
        <div className="bg-card border border-border rounded-lg p-6">
          <RegimeTransitionChart
            regimes={regime.regimes}
            currentRegime={regime.current_regime}
            transitionProbs={regime.transition_probabilities}
          />
          <p className="mt-4 text-sm text-muted-foreground">{regime.summary}</p>
        </div>
      )}

      {/* DTW Pattern Matching */}
      {dtw && dtw.top_matches.length > 0 && (
        <div className="bg-card border border-border rounded-lg p-6">
          <PatternMatchChart matches={dtw.top_matches} />
          <p className="mt-4 text-sm text-muted-foreground">{dtw.summary}</p>
        </div>
      )}

      {/* Insights */}
      {insights && insights.insights.length > 0 && (
        <div className="bg-card border border-border rounded-lg p-6">
          <h2 className="text-xl font-semibold mb-4">Automated Insights</h2>
          <div className="mb-4 p-4 bg-muted/50 rounded-lg">
            <p className="text-sm font-medium mb-2">Executive Summary</p>
            <p className="text-sm text-muted-foreground">{insights.executive_summary}</p>
          </div>

          <div className="space-y-3">
            {insights.insights.slice(0, 5).map((insight, idx) => (
              <div
                key={idx}
                className={`p-4 rounded-lg border ${
                  insight.severity === 'critical'
                    ? 'border-red-500/50 bg-red-500/5'
                    : insight.severity === 'high'
                    ? 'border-amber-500/50 bg-amber-500/5'
                    : 'border-border bg-muted/20'
                }`}
              >
                <div className="flex items-start justify-between mb-2">
                  <div className="flex items-center gap-2">
                    <span
                      className={`px-2 py-0.5 text-xs font-semibold rounded uppercase ${
                        insight.severity === 'critical'
                          ? 'bg-red-500 text-white'
                          : insight.severity === 'high'
                          ? 'bg-amber-500 text-white'
                          : 'bg-primary text-primary-foreground'
                      }`}
                    >
                      {insight.severity}
                    </span>
                    <span className="text-xs text-muted-foreground uppercase">
                      {insight.type}
                    </span>
                  </div>
                  <span className="text-xs text-muted-foreground">
                    {(insight.confidence * 100).toFixed(0)}% confidence
                  </span>
                </div>
                <p className="font-medium text-sm mb-2">{insight.title}</p>
                <p className="text-sm text-muted-foreground">{insight.description}</p>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Recent Trades */}
      {trades && trades.length > 0 && (
        <div className="bg-card border border-border rounded-lg p-6">
          <h2 className="text-xl font-semibold mb-4">Recent Trades</h2>
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead className="border-b border-border">
                <tr>
                  <th className="px-4 py-3 text-left text-xs font-medium uppercase">Date</th>
                  <th className="px-4 py-3 text-left text-xs font-medium uppercase">Ticker</th>
                  <th className="px-4 py-3 text-left text-xs font-medium uppercase">Type</th>
                  <th className="px-4 py-3 text-left text-xs font-medium uppercase">Amount</th>
                  <th className="px-4 py-3 text-left text-xs font-medium uppercase">Asset</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-border">
                {trades.slice(0, 10).map((trade) => (
                  <tr key={trade.id} className="text-sm">
                    <td className="px-4 py-3">
                      {new Date(trade.transaction_date).toLocaleDateString()}
                    </td>
                    <td className="px-4 py-3 font-mono font-medium">{trade.ticker}</td>
                    <td className="px-4 py-3">
                      <span
                        className={`px-2 py-1 text-xs font-semibold rounded ${
                          trade.transaction_type === 'purchase'
                            ? 'bg-green-500/10 text-green-500'
                            : 'bg-red-500/10 text-red-500'
                        }`}
                      >
                        {trade.transaction_type}
                      </span>
                    </td>
                    <td className="px-4 py-3">{trade.amount}</td>
                    <td className="px-4 py-3 text-muted-foreground text-xs">
                      {trade.asset_description.slice(0, 40)}
                      {trade.asset_description.length > 40 && '...'}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}
    </div>
  )
}
