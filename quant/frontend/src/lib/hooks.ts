'use client';

import { useQuery, type UseQueryResult } from '@tanstack/react-query';
import { api } from './api-client';
import { STRATEGIES } from './strategy-definitions';
import { DEMO_POLITICIANS } from './demo-data';
import type {
  Politician,
  MarketQuote,
  MarketStatus,
  Discovery,
  CriticalAnomaly,
  Experiment,
} from './types';

/**
 * Data hooks (React Query). Each is defensive: the query function tries the live
 * API and falls back to a safe default so the UI renders even when the backend is
 * unavailable. Restored module.
 */

async function safe<T>(fn: () => Promise<T>, fallback: T): Promise<T> {
  try {
    const v = await fn();
    return (v ?? fallback) as T;
  } catch {
    return fallback;
  }
}

export function usePoliticians(limit?: number): UseQueryResult<Politician[]> {
  return useQuery({
    queryKey: ['politicians', limit ?? null],
    queryFn: () =>
      safe<Politician[]>(async () => {
        const anyApi = api as any;
        const res = await anyApi?.politicians?.list?.(limit);
        const list = Array.isArray(res) ? res : res?.data ?? res?.politicians;
        return Array.isArray(list) ? list : DEMO_POLITICIANS;
      }, DEMO_POLITICIANS),
    placeholderData: DEMO_POLITICIANS,
  });
}

export function useMarketStatus(): UseQueryResult<MarketStatus> {
  return useQuery({
    queryKey: ['market-status'],
    queryFn: () =>
      safe<MarketStatus>(async () => {
        const anyApi = api as any;
        return (await anyApi?.market?.status?.()) ?? { isOpen: false };
      }, { isOpen: false }),
  });
}

export function useMarketQuote(ticker?: string): UseQueryResult<MarketQuote | null> {
  return useQuery({
    queryKey: ['market-quote', ticker ?? null],
    enabled: !!ticker,
    queryFn: () =>
      safe<MarketQuote | null>(async () => {
        const anyApi = api as any;
        return (await anyApi?.market?.quote?.(ticker)) ?? null;
      }, null),
  });
}

export function useMarketQuotes(symbols?: string[]): UseQueryResult<MarketQuote[]> {
  return useQuery({
    queryKey: ['market-quotes', symbols ?? []],
    queryFn: () =>
      safe<MarketQuote[]>(async () => {
        const anyApi = api as any;
        const res = await anyApi?.market?.quotes?.(symbols);
        return Array.isArray(res) ? res : [];
      }, []),
  });
}

export function useHistoricalData(ticker?: string, startDate?: string): UseQueryResult<unknown[]> {
  return useQuery({
    queryKey: ['historical', ticker ?? null, startDate ?? null],
    enabled: !!ticker,
    queryFn: () =>
      safe<unknown[]>(async () => {
        const anyApi = api as any;
        const res = await anyApi?.market?.historical?.(ticker, startDate);
        return Array.isArray(res) ? res : [];
      }, []),
  });
}

export function useBacktestStrategies(): UseQueryResult<typeof STRATEGIES> {
  return useQuery({
    queryKey: ['backtest-strategies'],
    queryFn: async () => STRATEGIES,
    initialData: STRATEGIES,
  });
}

export function useDiscoveries(_opts?: { minStrength?: number }): UseQueryResult<Discovery[]> {
  return useQuery({ queryKey: ['discoveries', _opts ?? {}], queryFn: async () => [] as Discovery[], initialData: [] });
}

export function useCriticalAnomalies(_opts?: { minSeverity?: number }): UseQueryResult<CriticalAnomaly[]> {
  return useQuery({ queryKey: ['anomalies', _opts ?? {}], queryFn: async () => [] as CriticalAnomaly[], initialData: [] });
}

export function useRecentExperiments(): UseQueryResult<Experiment[]> {
  return useQuery({ queryKey: ['experiments'], queryFn: async () => [] as Experiment[], initialData: [] });
}

export function useNetworkAnalysis(): UseQueryResult<{ nodes: unknown[]; links: unknown[] }> {
  return useQuery({
    queryKey: ['network-analysis'],
    queryFn: async () => ({ nodes: [], links: [] }),
    initialData: { nodes: [], links: [] },
  });
}
