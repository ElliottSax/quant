/**
 * Shared domain types.
 */

export interface MarketQuote {
  symbol: string;
  price: number;
  change?: number;
  changePercent?: number;
  [key: string]: unknown;
  previous_close?: number;
  volume?: number;
  bid?: number;
  ask?: number;
  timestamp?: string;
}

export interface MarketStatus {
  isOpen: boolean;
  session?: string;
  nextOpen?: string;
  nextClose?: string;
  [key: string]: unknown;
  volume?: number;
  is_open?: boolean;
  market?: string;
}

export interface Politician {
  id: string;
  name: string;
  party?: string;
  chamber?: string;
  state?: string;
  tradeCount?: number;
  [key: string]: unknown;
  trade_count?: number;
  last_trade?: any;
}

export interface Trade {
  id: string;
  politician_id: string;
  ticker: string;
  amount: string;
  type: string;
  date: string;
  [key: string]: unknown;
}

export interface FourierAnalysis {
  model_name: string;
  prediction: number;
  confidence: number;
  supporting_evidence: Record<string, any>;
  [key: string]: unknown;
}

export interface RegimeAnalysis {
  regime: string;
  confidence: number;
  [key: string]: unknown;
}

export interface DTWAnalysis {
  match_id: string;
  similarity: number;
  [key: string]: unknown;
}

export interface EnsemblePrediction {
  politician_id: string;
  politician_name: string;
  prediction_type: string;
  predicted_value: number;
  confidence: number;
  model_agreement: number;
  [key: string]: unknown;
}

export interface CorrelationPair {
  a: string;
  b: string;
  correlation: number;
  [key: string]: unknown;
  politician1_id?: string;
  politician1_name?: string;
  politician2_id?: string;
  politician2_name?: string;
}

export interface NetworkAnalysis {
  num_politicians: number;
  density: number;
  clustering_coefficient: number;
  [key: string]: unknown;
}

export interface ComprehensiveInsights {
  insights: string[];
  severity: string;
  [key: string]: unknown;
}

export interface AnomalyDetection {
  anomaly_score: number;
  is_anomaly: boolean;
  [key: string]: unknown;
}

export interface HistoricalDataResponse {
  data: any[];
  [key: string]: unknown;
}

export interface CompanyInfo {
  name: string;
  sector: string;
  industry: string;
  [key: string]: unknown;
}

export interface StockPrediction {
  ticker: string;
  prediction: number;
  [key: string]: unknown;
}

export interface CycleInfo {
  period: number;
  strength: number;
  period_days: number;
  confidence: number;
  category: string;
  [key: string]: unknown;
}

export interface RegimeInfo {
  regime: string;
  confidence: number;
  frequency: number;
  [key: string]: unknown;
}

export interface PatternMatch {
  id: string;
  score: number;
  similarity_score: number;
  confidence: number;
  match_date?: string;
  outcome_30d_trades?: number;
  outcome_90d_trades?: number;
  [key: string]: unknown;
}

export interface CycleAnalysis {
  period: number;
  strength: number;
  period_days: number;
  confidence: number;
  category: string;
  [key: string]: unknown;
}

export interface DiscoverySummary {
  active_discoveries: number;
  [key: string]: unknown;
}

export interface SignalGenerateRequest {
  symbol: string;
}

export interface SignalResponse {
  signal: string;
}

export interface TradingSignal {
  symbol: string;
  signal: string;
  [key: string]: unknown;
}

export interface BacktestRequest {
  symbol: string;
  start_date: string;
  end_date: string;
  strategy: string;
  initial_capital: number;
  commission?: number;
  slippage?: number;
  strategies?: string[];
}

export interface BacktestResult {
  sharpeRatio?: number;
  winRate?: number;
  maxDrawdown?: number;
  initialCapital?: number;
  [key: string]: unknown;
  equity_curve?: any;
  trades?: any[];
}

export interface StrategyInfo {
  id: string;
  name: string;
  [key: string]: unknown;
}

export interface DashboardStats {
  totalPoliticians?: number;
  totalTrades?: number;
  totalVolume?: number;
  [key: string]: unknown;
}

export interface LeaderboardResponse {
  rankings: any[];
  [key: string]: unknown;
}

export interface SectorStats {
  sector: string;
  volume: number;
  [key: string]: unknown;
}

export interface Discovery {
  id: string;
  title?: string;
  description?: string;
  strength: number;
  confidence: number;
  [key: string]: unknown;
  pattern_type?: string;
  discovery_date?: string;
  deployed?: boolean;
  politician_id?: string;
  politician_name?: string;
  parameters?: Record<string, any>;
}

export interface CriticalAnomaly {
  id: string;
  severity: any;
  [key: string]: unknown;
  anomaly_type?: string;
  politician_id?: string;
  politician_name?: string;
  description?: string;
  evidence?: Record<string, any>;
  detection_date?: string;
}

export interface Experiment {
  id: string;
  name?: string;
  status?: string;
  accuracy?: number;
  [key: string]: unknown;
  model_name?: string;
  deployment_ready?: boolean;
  validation_metrics?: Record<string, any>;
}
