/**
 * React Query hooks for Quant Analytics Platform
 * Provides data fetching with caching, loading states, and error handling
 */

import { useQuery, UseQueryOptions } from '@tanstack/react-query'
import { api, APIError } from './api-client'
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
  Discovery,
  Experiment,
  CriticalAnomaly,
  MarketQuote,
  HistoricalDataResponse,
  CompanyInfo,
  MarketStatus,
  StockPrediction,
  CycleAnalysis,
  DiscoverySummary,
} from './types'

export function usePoliticians(minTrades: number = 10) {
  return useQuery<Politician[], APIError>({
    queryKey: ['politicians', minTrades],
    queryFn: () => api.politicians.list(minTrades),
    staleTime: 1000 * 60 * 5, // 5 minutes
  })
}

export function usePolitician(id: string | null) {
  return useQuery<Politician, APIError>({
    queryKey: ['politician', id],
    queryFn: () => api.politicians.get(id!),
    enabled: !!id,
  })
}

export function useTrades(politicianId: string | null, limit: number = 100) {
  return useQuery<Trade[], APIError>({
    queryKey: ['trades', politicianId, limit],
    queryFn: () => api.trades.list(politicianId!, limit),
    enabled: !!politicianId,
  })
}

export function useFourierAnalysis(
  politicianId: string | null,
  params?: { min_strength?: number; min_confidence?: number; include_forecast?: boolean }
) {
  return useQuery<FourierAnalysis, APIError>({
    queryKey: ['fourier', politicianId, params],
    queryFn: () => api.patterns.fourier(politicianId!, params),
    enabled: !!politicianId,
    staleTime: 1000 * 60 * 10, // 10 minutes
  })
}

export function useRegimeAnalysis(politicianId: string | null, nStates: number = 4) {
  return useQuery<RegimeAnalysis, APIError>({
    queryKey: ['regime', politicianId, nStates],
    queryFn: () => api.patterns.regime(politicianId!, nStates),
    enabled: !!politicianId,
    staleTime: 1000 * 60 * 10,
  })
}

export function useDTWAnalysis(
  politicianId: string | null,
  params?: { window_size?: number; top_k?: number; similarity_threshold?: number }
) {
  return useQuery<DTWAnalysis, APIError>({
    queryKey: ['dtw', politicianId, params],
    queryFn: () => api.patterns.dtw(politicianId!, params),
    enabled: !!politicianId,
    staleTime: 1000 * 60 * 10,
  })
}

export function useEnsemblePrediction(politicianId: string | null) {
  return useQuery<EnsemblePrediction, APIError>({
    queryKey: ['ensemble', politicianId],
    queryFn: () => api.analytics.ensemble(politicianId!),
    enabled: !!politicianId,
    staleTime: 1000 * 60 * 15, // 15 minutes for expensive operation
    retry: 1, // Retry once on failure
  })
}

export function useCorrelationAnalysis(politicianIds: string[]) {
  return useQuery<CorrelationPair[], APIError>({
    queryKey: ['correlation', politicianIds.sort()],
    queryFn: () => api.analytics.correlation(politicianIds),
    enabled: politicianIds.length >= 2,
    staleTime: 1000 * 60 * 10,
  })
}

export function useNetworkAnalysis(params?: { min_trades?: number; min_correlation?: number }) {
  return useQuery<NetworkAnalysis, APIError>({
    queryKey: ['network', params],
    queryFn: () => api.analytics.network(params),
    staleTime: 1000 * 60 * 15,
    retry: 1,
  })
}

export function useInsights(politicianId: string | null, confidenceThreshold: number = 0.7) {
  return useQuery<ComprehensiveInsights, APIError>({
    queryKey: ['insights', politicianId, confidenceThreshold],
    queryFn: () => api.analytics.insights(politicianId!, confidenceThreshold),
    enabled: !!politicianId,
    staleTime: 1000 * 60 * 15,
    retry: 1,
  })
}

export function useAnomalies(politicianId: string | null, anomalyThreshold: number = 0.7) {
  return useQuery<AnomalyDetection, APIError>({
    queryKey: ['anomalies', politicianId, anomalyThreshold],
    queryFn: () => api.analytics.anomalies(politicianId!, anomalyThreshold),
    enabled: !!politicianId,
    staleTime: 1000 * 60 * 15,
  })
}

export function useHealth() {
  return useQuery({
    queryKey: ['health'],
    queryFn: () => api.health(),
    refetchInterval: 30000, // Check every 30 seconds
  })
}

// Discovery hooks - connected to backend API
export function useDiscoveries(params?: { timeRange?: string; minStrength?: number }) {
  return useQuery<Discovery[], APIError>({
    queryKey: ['discoveries', params],
    queryFn: () => api.discoveries.list(params),
    staleTime: 1000 * 60 * 5, // 5 minutes
  })
}

export function useCriticalAnomalies(params?: { minSeverity?: number }) {
  return useQuery<CriticalAnomaly[], APIError>({
    queryKey: ['critical-anomalies', params],
    queryFn: () => api.discoveries.anomalies(params),
    staleTime: 1000 * 60 * 5,
  })
}

export function useRecentExperiments() {
  return useQuery<Experiment[], APIError>({
    queryKey: ['recent-experiments'],
    queryFn: () => api.discoveries.experiments(),
    staleTime: 1000 * 60 * 10, // 10 minutes
  })
}

// Market Data Hooks
export function useMarketQuote(symbol: string | null) {
  return useQuery<MarketQuote, APIError>({
    queryKey: ['market-quote', symbol],
    queryFn: () => api.marketData.quote(symbol!),
    enabled: !!symbol,
    staleTime: 1000 * 30, // 30 seconds
    refetchInterval: 1000 * 60, // Refresh every minute
  })
}

export function useMarketQuotes(symbols: string[]) {
  return useQuery<{ quotes: Record<string, MarketQuote>; count: number; timestamp: string }, APIError>({
    queryKey: ['market-quotes', symbols.sort()],
    queryFn: () => api.marketData.quotes(symbols),
    enabled: symbols.length > 0,
    staleTime: 1000 * 30,
    refetchInterval: 1000 * 60,
  })
}

export function useHistoricalData(
  symbol: string | null,
  startDate: Date,
  endDate?: Date,
  interval: string = '1d'
) {
  return useQuery<HistoricalDataResponse, APIError>({
    queryKey: ['historical-data', symbol, startDate.toISOString(), endDate?.toISOString(), interval],
    queryFn: () => api.marketData.historical(symbol!, startDate, endDate, interval),
    enabled: !!symbol,
    staleTime: 1000 * 60 * 5, // 5 minutes
  })
}

export function useCompanyInfo(symbol: string | null) {
  return useQuery<CompanyInfo, APIError>({
    queryKey: ['company-info', symbol],
    queryFn: () => api.marketData.company(symbol!),
    enabled: !!symbol,
    staleTime: 1000 * 60 * 60, // 1 hour - company info doesn't change often
  })
}

export function useMarketStatus() {
  return useQuery<MarketStatus, APIError>({
    queryKey: ['market-status'],
    queryFn: () => api.marketData.marketStatus(),
    staleTime: 1000 * 60, // 1 minute
    refetchInterval: 1000 * 60, // Refresh every minute
  })
}

// Discovery Integration Hooks
export function useDiscoveryStatus() {
  return useQuery<DiscoverySummary, APIError>({
    queryKey: ['discovery-status'],
    queryFn: () => api.discovery.status(),
    staleTime: 1000 * 60 * 5, // 5 minutes
  })
}

export function useStockPredictions(params?: { limit?: number; minConfidence?: number; predictionType?: 'UP' | 'DOWN' }) {
  return useQuery<StockPrediction[], APIError>({
    queryKey: ['stock-predictions', params],
    queryFn: () => api.discovery.predictions(params),
    staleTime: 1000 * 60 * 5, // 5 minutes
  })
}

export function useStockPrediction(ticker: string | null) {
  return useQuery<StockPrediction, APIError>({
    queryKey: ['stock-prediction', ticker],
    queryFn: () => api.discovery.prediction(ticker!),
    enabled: !!ticker,
    staleTime: 1000 * 60 * 5,
  })
}

export function useCycleAnalysis(limit: number = 10) {
  return useQuery<CycleAnalysis[], APIError>({
    queryKey: ['cycle-analysis', limit],
    queryFn: () => api.discovery.cycleAnalysis(limit),
    staleTime: 1000 * 60 * 10, // 10 minutes
  })
}

export function useDiscoveryAnalytics() {
  return useQuery({
    queryKey: ['discovery-analytics'],
    queryFn: () => api.discovery.analytics(),
    staleTime: 1000 * 60 * 10,
  })
}

export function useDiscoveryTrades(params?: { limit?: number; ticker?: string; politician?: string }) {
  return useQuery({
    queryKey: ['discovery-trades', params],
    queryFn: () => api.discovery.trades(params),
    staleTime: 1000 * 60 * 5,
  })
}

export function useDiscoveryAlerts(limit: number = 20) {
  return useQuery({
    queryKey: ['discovery-alerts', limit],
    queryFn: () => api.discovery.alerts(limit),
    staleTime: 1000 * 60 * 2, // 2 minutes for alerts
    refetchInterval: 1000 * 60 * 2, // Auto-refresh every 2 minutes
  })
}
