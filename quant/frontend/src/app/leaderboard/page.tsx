/**
 * Leaderboard Page
 * Shows top politicians by trade count with charts and table
 */

'use client';

import { useState } from 'react';
import { useLeaderboard, useSectorStats } from '@/hooks/use-stats';
import { LeaderboardChart } from '@/components/charts/leaderboard-chart';
import { SectorChart } from '@/components/charts/sector-chart';
import { LeaderboardTable } from '@/components/politicians/leaderboard-table';

export default function LeaderboardPage() {
  const [period, setPeriod] = useState<'7d' | '30d' | '90d' | '1y' | 'all'>('30d');
  const [chamber, setChamber] = useState<'senate' | 'house' | ''>('');

  const { data: leaderboardData, isLoading: leaderboardLoading } = useLeaderboard({
    period,
    limit: 50,
    chamber: chamber || undefined,
  });

  const { data: sectorData, isLoading: sectorLoading } = useSectorStats({
    period,
  });

  const periodOptions = [
    { value: '7d', label: '7 Days' },
    { value: '30d', label: '30 Days' },
    { value: '90d', label: '90 Days' },
    { value: '1y', label: '1 Year' },
    { value: 'all', label: 'All Time' },
  ];

  const chamberOptions = [
    { value: '', label: 'All' },
    { value: 'senate', label: 'Senate' },
    { value: 'house', label: 'House' },
  ];

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <div className="bg-white border-b border-gray-200">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
          <h1 className="text-3xl font-bold text-gray-900">Trading Leaderboard</h1>
          <p className="mt-2 text-gray-600">
            Politicians ranked by trading activity with statistical rigor
          </p>
        </div>
      </div>

      {/* Filters */}
      <div className="bg-white border-b border-gray-200">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
          <div className="flex flex-wrap gap-4">
            {/* Period Filter */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Time Period
              </label>
              <select
                value={period}
                onChange={(e) => setPeriod(e.target.value as any)}
                className="block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 sm:text-sm px-3 py-2 border"
              >
                {periodOptions.map((option) => (
                  <option key={option.value} value={option.value}>
                    {option.label}
                  </option>
                ))}
              </select>
            </div>

            {/* Chamber Filter */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Chamber
              </label>
              <select
                value={chamber}
                onChange={(e) => setChamber(e.target.value as any)}
                className="block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 sm:text-sm px-3 py-2 border"
              >
                {chamberOptions.map((option) => (
                  <option key={option.value} value={option.value}>
                    {option.label}
                  </option>
                ))}
              </select>
            </div>
          </div>
        </div>
      </div>

      {/* Content */}
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 space-y-8">
        {/* Charts Section */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
          {/* Top Traders Chart */}
          <div className="bg-white rounded-lg shadow p-6">
            <h2 className="text-lg font-semibold text-gray-900 mb-4">
              Top Traders
            </h2>
            {leaderboardLoading ? (
              <div className="h-64 flex items-center justify-center">
                <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-500"></div>
              </div>
            ) : (
              <LeaderboardChart data={leaderboardData?.leaderboard || []} showTop={10} />
            )}
          </div>

          {/* Top Stocks Chart */}
          <div className="bg-white rounded-lg shadow p-6">
            <h2 className="text-lg font-semibold text-gray-900 mb-4">
              Most Traded Stocks
            </h2>
            {sectorLoading ? (
              <div className="h-64 flex items-center justify-center">
                <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-500"></div>
              </div>
            ) : (
              <SectorChart data={sectorData?.tickers || []} showTop={10} />
            )}
          </div>
        </div>

        {/* Leaderboard Table */}
        <div className="bg-white rounded-lg shadow">
          <div className="px-6 py-4 border-b border-gray-200">
            <h2 className="text-lg font-semibold text-gray-900">
              Full Leaderboard
            </h2>
            {leaderboardData && (
              <p className="text-sm text-gray-600 mt-1">
                Showing {leaderboardData.count} politicians
              </p>
            )}
          </div>
          <LeaderboardTable
            data={leaderboardData?.leaderboard || []}
            loading={leaderboardLoading}
          />
        </div>
      </div>
    </div>
  );
}
