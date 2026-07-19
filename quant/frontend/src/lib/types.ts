/**
 * Shared domain types. Intentionally permissive (index signatures) so consumers
 * compile regardless of exact backend payload shape.
 */

export interface MarketQuote {
  symbol: string;
  price: number;
  change?: number;
  changePercent?: number;
  [key: string]: unknown;
}

export interface MarketStatus {
  isOpen: boolean;
  session?: string;
  nextOpen?: string;
  nextClose?: string;
  [key: string]: unknown;
}

export interface Politician {
  id: string;
  name: string;
  party?: string;
  chamber?: string;
  state?: string;
  tradeCount?: number;
  [key: string]: unknown;
}

export interface DashboardStats {
  totalPoliticians?: number;
  totalTrades?: number;
  totalVolume?: number;
  [key: string]: unknown;
}

export interface CorrelationPair {
  a: string;
  b: string;
  correlation: number;
  [key: string]: unknown;
}

export interface CriticalAnomaly {
  id: string;
  severity?: string;
  description?: string;
  [key: string]: unknown;
}

export interface CycleInfo {
  period?: number;
  strength?: number;
  [key: string]: unknown;
}

export interface Discovery {
  id: string;
  title?: string;
  description?: string;
  createdAt?: string;
  [key: string]: unknown;
}

export interface Experiment {
  id: string;
  name?: string;
  status?: string;
  [key: string]: unknown;
}

export interface PatternMatch {
  id: string;
  score?: number;
  [key: string]: unknown;
}

export interface RegimeInfo {
  regime?: string;
  confidence?: number;
  [key: string]: unknown;
}
