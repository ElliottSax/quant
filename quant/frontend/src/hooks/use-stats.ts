/**
 * React Query hooks for statistics data
 */

import { useQuery, UseQueryResult } from '@tanstack/react-query';
import { apiClient, LeaderboardEntry, SectorStats, Trade } from '@/lib/api-client';

export interface UseLeaderboardParams {
  period?: '7d' | '30d' | '90d' | '1y' | 'all';
  limit?: number;
  chamber?: 'senate' | 'house';
  party?: string;
}

export interface UseRecentTradesParams {
  limit?: number;
  chamber?: 'senate' | 'house';
  party?: string;
  transaction_type?: 'buy' | 'sell';
}

export interface UseSectorStatsParams {
  period?: '7d' | '30d' | '90d' | '1y' | 'all';
}

/**
 * Hook to fetch leaderboard data
 */
export function useLeaderboard(
  params: UseLeaderboardParams = {}
): UseQueryResult<{ leaderboard: LeaderboardEntry[]; period: string; count: number }> {
  return useQuery({
    queryKey: ['leaderboard', params],
    queryFn: () => apiClient.getLeaderboard(params),
    staleTime: 5 * 60 * 1000, // 5 minutes
    cacheTime: 10 * 60 * 1000, // 10 minutes
  });
}

/**
 * Hook to fetch recent trades
 */
export function useRecentTrades(
  params: UseRecentTradesParams = {}
): UseQueryResult<{ trades: Trade[]; count: number }> {
  return useQuery({
    queryKey: ['recent-trades', params],
    queryFn: () => apiClient.getRecentTrades(params),
    staleTime: 2 * 60 * 1000, // 2 minutes (more fresh for recent data)
    cacheTime: 5 * 60 * 1000, // 5 minutes
  });
}

/**
 * Hook to fetch sector statistics
 */
export function useSectorStats(
  params: UseSectorStatsParams = {}
): UseQueryResult<SectorStats> {
  return useQuery({
    queryKey: ['sector-stats', params],
    queryFn: () => apiClient.getSectorStats(params),
    staleTime: 5 * 60 * 1000, // 5 minutes
    cacheTime: 10 * 60 * 1000, // 10 minutes
  });
}
