/**
 * API Client for Quant Analytics Platform
 * Provides typed interfaces to backend endpoints
 */

import {
  Politician,
  Trade,
  FourierAnalysis,
  RegimeAnalysis,
  DTWAnalysis,
  EnsemblePrediction,
  CorrelationPair,
  NetworkAnalysis,
  ComprehensiveInsights,
  AnomalyDetection,
  MarketQuote,
  HistoricalDataResponse,
  CompanyInfo,
  MarketStatus,
  Discovery,
  CriticalAnomaly,
  Experiment,
  StockPrediction,
  CycleAnalysis,
  DiscoverySummary,
} from './types'

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api/v1'

class APIError extends Error {
  constructor(
    message: string,
    public status: number,
    public details?: any
  ) {
    super(message)
    this.name = 'APIError'
  }
}

async function fetchAPI<T>(endpoint: string, options?: RequestInit): Promise<T> {
  const url = `${API_BASE_URL}${endpoint}`

  try {
    const response = await fetch(url, {
      ...options,
      headers: {
        'Content-Type': 'application/json',
        ...options?.headers,
      },
    })

    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}))
      throw new APIError(
        errorData.detail || `API Error: ${response.statusText}`,
        response.status,
        errorData
      )
    }

    return await response.json()
  } catch (error) {
    if (error instanceof APIError) throw error
    throw new APIError(
      error instanceof Error ? error.message : 'Network error',
      0
    )
  }
}

export const api = {
  // Politicians
  politicians: {
    list: (minTrades: number = 10) =>
      fetchAPI<{ politicians: Politician[] }>(`/politicians/`).then(res => res.politicians),

    get: (id: string) =>
      fetchAPI<Politician>(`/politicians/${id}`),
  },

  // Trades
  trades: {
    list: (politicianId: string, limit: number = 100) =>
      fetchAPI<Trade[]>(`/politicians/${politicianId}/trades?limit=${limit}`),
  },

  // Pattern Analysis
  patterns: {
    fourier: (
      politicianId: string,
      params?: { min_strength?: number; min_confidence?: number; include_forecast?: boolean }
    ) => {
      const query = new URLSearchParams()
      if (params?.min_strength) query.append('min_strength', params.min_strength.toString())
      if (params?.min_confidence) query.append('min_confidence', params.min_confidence.toString())
      if (params?.include_forecast !== undefined) query.append('include_forecast', params.include_forecast.toString())

      return fetchAPI<FourierAnalysis>(
        `/patterns/analyze/${politicianId}/fourier?${query.toString()}`
      )
    },

    regime: (politicianId: string, nStates: number = 4) =>
      fetchAPI<RegimeAnalysis>(
        `/patterns/analyze/${politicianId}/regime?n_states=${nStates}`
      ),

    dtw: (
      politicianId: string,
      params?: { window_size?: number; top_k?: number; similarity_threshold?: number }
    ) => {
      const query = new URLSearchParams()
      if (params?.window_size) query.append('window_size', params.window_size.toString())
      if (params?.top_k) query.append('top_k', params.top_k.toString())
      if (params?.similarity_threshold) query.append('similarity_threshold', params.similarity_threshold.toString())

      return fetchAPI<DTWAnalysis>(
        `/patterns/analyze/${politicianId}/dtw?${query.toString()}`
      )
    },
  },

  // Advanced Analytics
  analytics: {
    ensemble: (politicianId: string) =>
      fetchAPI<EnsemblePrediction>(`/analytics/ensemble/${politicianId}`),

    correlation: (politicianIds: string[]) => {
      const query = politicianIds.map(id => `politician_ids=${id}`).join('&')
      return fetchAPI<CorrelationPair[]>(`/analytics/correlation/pairwise?${query}`)
    },

    network: (params?: { min_trades?: number; min_correlation?: number }) => {
      const query = new URLSearchParams()
      if (params?.min_trades) query.append('min_trades', params.min_trades.toString())
      if (params?.min_correlation) query.append('min_correlation', params.min_correlation.toString())

      return fetchAPI<NetworkAnalysis>(`/analytics/network/analysis?${query.toString()}`)
    },

    insights: (politicianId: string, confidenceThreshold: number = 0.7) =>
      fetchAPI<ComprehensiveInsights>(
        `/analytics/insights/${politicianId}?confidence_threshold=${confidenceThreshold}`
      ),

    anomalies: (politicianId: string, anomalyThreshold: number = 0.7) =>
      fetchAPI<AnomalyDetection>(
        `/analytics/anomaly-detection/${politicianId}?anomaly_threshold=${anomalyThreshold}`
      ),
  },

  // Health check
  health: () =>
    fetchAPI<{ status: string; database: string }>('/health'),

  // Discoveries
  discoveries: {
    list: (params?: { timeRange?: string; minStrength?: number }) => {
      const query = new URLSearchParams()
      if (params?.timeRange) query.append('time_range', params.timeRange)
      if (params?.minStrength) query.append('min_strength', params.minStrength.toString())
      return fetchAPI<Discovery[]>(`/discoveries/?${query.toString()}`)
    },

    anomalies: (params?: { minSeverity?: number }) => {
      const query = new URLSearchParams()
      if (params?.minSeverity) query.append('min_severity', params.minSeverity.toString())
      return fetchAPI<CriticalAnomaly[]>(`/discoveries/anomalies?${query.toString()}`)
    },

    experiments: () =>
      fetchAPI<Experiment[]>('/discoveries/experiments'),
  },

  // Market Data (public endpoints - no auth required)
  marketData: {
    quote: (symbol: string) =>
      fetchAPI<MarketQuote>(`/market-data/public/quote/${symbol}`),

    quotes: (symbols: string[]) => {
      const query = symbols.map(s => `symbols=${s}`).join('&')
      return fetchAPI<{ quotes: Record<string, MarketQuote>; count: number; timestamp: string }>(
        `/market-data/public/quotes?${query}`
      )
    },

    historical: (
      symbol: string,
      startDate: Date,
      endDate?: Date,
      interval: string = '1d'
    ) => {
      const query = new URLSearchParams()
      query.append('start_date', startDate.toISOString())
      if (endDate) query.append('end_date', endDate.toISOString())
      query.append('interval', interval)

      return fetchAPI<HistoricalDataResponse>(
        `/market-data/public/historical/${symbol}?${query.toString()}`
      )
    },

    company: (symbol: string) =>
      fetchAPI<CompanyInfo>(`/market-data/public/company/${symbol}`),

    marketStatus: () =>
      fetchAPI<MarketStatus>('/market-data/public/market-status'),
  },

  // Discovery Integration (pulls from discovery project)
  discovery: {
    status: () =>
      fetchAPI<DiscoverySummary>('/discovery/status'),

    predictions: (params?: { limit?: number; minConfidence?: number; predictionType?: 'UP' | 'DOWN' }) => {
      const query = new URLSearchParams()
      if (params?.limit) query.append('limit', params.limit.toString())
      if (params?.minConfidence) query.append('min_confidence', params.minConfidence.toString())
      if (params?.predictionType) query.append('prediction_type', params.predictionType)
      return fetchAPI<StockPrediction[]>(`/discovery/predictions?${query.toString()}`)
    },

    prediction: (ticker: string) =>
      fetchAPI<StockPrediction>(`/discovery/predictions/${ticker}`),

    multiHorizon: () =>
      fetchAPI<{ data: Record<string, any> }>('/discovery/predictions/multi-horizon'),

    cycleAnalysis: (limit: number = 10) =>
      fetchAPI<CycleAnalysis[]>(`/discovery/analysis/cycles?limit=${limit}`),

    analytics: () =>
      fetchAPI<{ analytics: any[]; timestamp: string }>('/discovery/analytics'),

    trades: (params?: { limit?: number; ticker?: string; politician?: string }) => {
      const query = new URLSearchParams()
      if (params?.limit) query.append('limit', params.limit.toString())
      if (params?.ticker) query.append('ticker', params.ticker)
      if (params?.politician) query.append('politician', params.politician)
      return fetchAPI<{ trades: any[]; count: number; timestamp: string }>(`/discovery/trades?${query.toString()}`)
    },

    alerts: (limit: number = 20) =>
      fetchAPI<{ alerts: any[]; count: number; timestamp: string }>(`/discovery/alerts?limit=${limit}`),
  },
}

export { APIError }
