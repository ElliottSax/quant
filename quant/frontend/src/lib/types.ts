/**
 * Type definitions for Quant Analytics Platform API
 * Auto-generated from backend API schemas
 */

export interface Politician {
  id: string
  name: string
  party: 'Democratic' | 'Republican' | 'Independent' | string
  state: string
  chamber: 'House' | 'Senate' | string
  trade_count?: number
  first_trade?: string
  last_trade?: string
  days_active?: number
}

export interface Trade {
  id: string
  politician_id: string
  transaction_date: string
  ticker: string
  asset_description: string
  asset_type: string
  transaction_type: 'purchase' | 'sale' | string
  amount: string
  amount_min?: number
  amount_max?: number
  disclosure_date: string
}

export interface CycleInfo {
  period_days: number
  strength: number
  confidence: number
  category: string
  frequency: number
}

export interface FourierAnalysis {
  politician_id: string
  politician_name: string
  analysis_date: string
  total_trades: number
  date_range_start: string
  date_range_end: string
  dominant_cycles: CycleInfo[]
  total_cycles_found: number
  forecast_30d?: number[]
  summary: string
}

export interface RegimeInfo {
  regime_id: number
  name: string
  avg_return: number
  volatility: number
  frequency: number
  sample_size: number
}

export interface RegimeAnalysis {
  politician_id: string
  politician_name: string
  analysis_date: string
  current_regime: number
  current_regime_name: string
  regime_confidence: number
  expected_duration_days: number
  regimes: RegimeInfo[]
  transition_probabilities: Record<string, number>
  summary: string
}

export interface PatternMatch {
  match_date: string
  similarity_score: number
  confidence: number
  outcome_30d_trades?: number
  outcome_90d_trades?: number
}

export interface DTWAnalysis {
  politician_id: string
  politician_name: string
  analysis_date: string
  top_matches: PatternMatch[]
  matches_found: number
  prediction?: {
    predicted_return: number
    confidence: number
  }
  summary: string
}

export interface ModelPrediction {
  model_name: 'fourier' | 'hmm' | 'dtw'
  prediction: number
  confidence: number
  supporting_evidence: Record<string, any>
}

export interface EnsemblePrediction {
  politician_id: string
  politician_name: string
  analysis_date: string
  prediction_type: 'trade_increase' | 'trade_decrease' | 'regime_change' | 'cycle_peak' | 'anomaly' | 'insufficient_data'
  predicted_value: number
  confidence: number
  model_agreement: number
  anomaly_score: number
  individual_predictions: ModelPrediction[]
  insights: string[]
  interpretation: string
}

export interface CorrelationPair {
  politician1_id: string
  politician1_name: string
  politician2_id: string
  politician2_name: string
  correlation: number
  p_value: number
  significance: 'significant' | 'not_significant'
  interpretation: string
}

export interface NetworkAnalysis {
  analysis_date: string
  num_politicians: number
  density: number
  clustering_coefficient: number
  average_path_length: number
  central_politicians: Array<{
    politician_id: string
    name: string
    centrality_score: number
  }>
  clusters: Array<{
    cluster_id: number
    politicians: string[]
    avg_correlation: number
  }>
  coordinated_groups: Record<string, Array<[string, string, number]>>
}

export interface Insight {
  type: string
  severity: 'critical' | 'high' | 'medium' | 'low' | 'info'
  title: string
  description: string
  confidence: number
  evidence: Record<string, any>
  recommendations: string[]
  timestamp: string
}

export interface ComprehensiveInsights {
  politician_id: string
  politician_name: string
  analysis_date: string
  executive_summary: string
  total_insights: number
  critical_count: number
  high_priority_count: number
  insights: Insight[]
}

export interface AnomalyDetection {
  politician_id: string
  politician_name: string
  analysis_date: string
  anomaly_detected: boolean
  anomaly_count: number
  ensemble_anomaly_score: number
  anomalies: Insight[]
  requires_investigation: boolean
}

export interface PoliticianStats {
  total_trades: number
  total_volume: number
  avg_trade_size: number
  most_traded_ticker: string
  recent_activity: number
  anomaly_score: number
  risk_level: 'low' | 'medium' | 'high'
}

export interface DashboardMetrics {
  total_politicians: number
  total_trades: number
  recent_trades_7d: number
  high_risk_politicians: number
  anomalies_detected: number
  top_traders: Array<{
    politician: Politician
    stats: PoliticianStats
  }>
}

export interface Discovery {
  id: string
  discovery_date: string
  politician_id: string
  politician_name: string
  pattern_type: string
  strength: number
  confidence: number
  description: string
  parameters: Record<string, any>
  metadata: Record<string, any>
  reviewed: boolean
  deployed: boolean
}

export interface Experiment {
  id: string
  experiment_date: string
  model_name: string
  deployment_ready: boolean
  hyperparameters?: Record<string, any>
  training_metrics?: Record<string, number>
  validation_metrics?: {
    accuracy?: number
    precision?: number
    recall?: number
  }
  test_metrics?: {
    f1_score?: number
  }
  notes?: string
}

export interface CriticalAnomaly {
  id: string
  detection_date: string
  politician_id: string
  politician_name: string
  anomaly_type: string
  severity: number
  description: string
  evidence: Record<string, any>
  investigated: boolean
}

// Market Data Types
export interface MarketQuote {
  symbol: string
  price: number
  bid?: number
  ask?: number
  volume: number
  timestamp: string
  change?: number
  change_percent?: number
  previous_close?: number
}

export interface MarketDataBar {
  timestamp: string
  open: number
  high: number
  low: number
  close: number
  volume: number
  adjusted_close?: number
}

export interface HistoricalDataResponse {
  symbol: string
  interval: string
  start_date: string
  end_date: string
  bars: MarketDataBar[]
  count: number
}

export interface CompanyInfo {
  symbol: string
  name?: string
  sector?: string
  industry?: string
  description?: string
  website?: string
  employees?: number
  market_cap?: number
  pe_ratio?: number
}

export interface MarketStatus {
  is_open: boolean
  market: string
  timestamp: string
  message: string
}

// Discovery Integration Types
export interface StockPrediction {
  ticker: string
  prediction: 'UP' | 'DOWN'
  confidence: number
  signals?: {
    cyclical?: {
      dominant_cycle?: number | null
      cycle_strength?: number | null
      cycles_detected?: any[]
      seasonality?: string | null
      trade_count?: number
    }
    regime?: {
      current_regime?: string
      regime_probability?: number
      n_regimes?: number
      mean_trades?: number
      recent_avg?: number
    }
    pattern?: {
      error?: string
    }
    ml?: {
      prediction?: string
      confidence?: number
      probability_up?: number
      probability_down?: number
      model_scores?: Record<string, number>
    }
  }
  patterns_found?: string[]
  regime?: string
  cycle_info?: Record<string, any>
  ml_scores?: Record<string, number>
  timestamp?: string
  source?: string
}

export interface CycleAnalysis {
  summary: {
    total_trades: number
    total_chunks: number
    successful_chunks: number
    failed_chunks: number
    elapsed_seconds: number
    throughput: number
    workers_used: number
  }
  results: Array<{
    status: string
    worker_id: string
    results: {
      sentiment?: {
        positive: number
        negative: number
        neutral: number
        overall_sentiment: string
      }
      volume?: {
        average_volume: number
        total_volume: number
        max_volume: number
        min_volume: number
      }
      patterns?: {
        pattern: string
        strength: number
        price_range: number
      }
    }
    trades_processed: number
    chunk_id: number
    worker: string
  }>
  filename?: string
  timestamp?: string
}

export interface DiscoverySummary {
  available: boolean
  predictions_count: number
  top_predictions: Array<{
    ticker: string
    prediction: string
    confidence: number
  }>
  latest_analysis_timestamp?: string
  data_path: string
}
