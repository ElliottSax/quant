/**
 * Homepage
 * Shows recent trades and top performers
 */

'use client';

import Link from 'next/link';
import { useRecentTrades, useLeaderboard } from '@/hooks/use-stats';
import { TradeList } from '@/components/trades/trade-list';
import { LeaderboardChart } from '@/components/charts/leaderboard-chart';

export default function Home() {
  const { data: recentTradesData, isLoading: tradesLoading } = useRecentTrades({
    limit: 12,
  });

  const { data: leaderboardData, isLoading: leaderboardLoading } = useLeaderboard({
    period: '30d',
    limit: 10,
  });

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Hero Section */}
      <div className="bg-gradient-to-r from-blue-600 to-blue-800 text-white">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-16">
          <h1 className="text-4xl md:text-5xl font-bold mb-4">
            Quant Analytics Platform
          </h1>
          <p className="text-xl md:text-2xl text-blue-100 mb-8">
            Track government stock trades with statistical rigor
          </p>
          <div className="flex gap-4">
            <Link
              href="/leaderboard"
              className="bg-white text-blue-600 px-6 py-3 rounded-lg font-semibold hover:bg-blue-50 transition-colors"
            >
              View Leaderboard
            </Link>
            <Link
              href="/trades"
              className="bg-blue-700 text-white px-6 py-3 rounded-lg font-semibold hover:bg-blue-600 transition-colors border border-blue-500"
            >
              Browse Trades
            </Link>
          </div>
        </div>
      </div>

      {/* Main Content */}
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12 space-y-12">
        {/* Top Performers Section */}
        <section>
          <div className="flex items-center justify-between mb-6">
            <div>
              <h2 className="text-2xl font-bold text-gray-900">
                Top Performers (30 Days)
              </h2>
              <p className="text-gray-600 mt-1">
                Politicians with the most trading activity
              </p>
            </div>
            <Link
              href="/leaderboard"
              className="text-blue-600 hover:text-blue-700 font-medium"
            >
              View Full Leaderboard →
            </Link>
          </div>
          <div className="bg-white rounded-lg shadow p-6">
            {leaderboardLoading ? (
              <div className="h-64 flex items-center justify-center">
                <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-500"></div>
              </div>
            ) : (
              <LeaderboardChart data={leaderboardData?.leaderboard || []} showTop={10} />
            )}
          </div>
        </section>

        {/* Recent Trades Section */}
        <section>
          <div className="flex items-center justify-between mb-6">
            <div>
              <h2 className="text-2xl font-bold text-gray-900">
                Recent Trades
              </h2>
              <p className="text-gray-600 mt-1">
                Latest disclosed congressional stock transactions
              </p>
            </div>
            <Link
              href="/trades"
              className="text-blue-600 hover:text-blue-700 font-medium"
            >
              View All Trades →
            </Link>
          </div>
          <TradeList
            trades={recentTradesData?.trades || []}
            loading={tradesLoading}
            emptyMessage="No recent trades available"
          />
        </section>

        {/* Info Section */}
        <section className="bg-white rounded-lg shadow p-8">
          <h2 className="text-2xl font-bold text-gray-900 mb-4">
            About This Platform
          </h2>
          <div className="prose prose-blue max-w-none">
            <p className="text-gray-600">
              This platform tracks stock trades made by members of the U.S. Congress,
              providing transparent access to publicly disclosed financial transactions.
              All data is sourced from official congressional disclosure records.
            </p>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mt-6">
              <div className="border-l-4 border-blue-500 pl-4">
                <h3 className="font-semibold text-gray-900 mb-2">
                  Statistical Rigor
                </h3>
                <p className="text-sm text-gray-600">
                  We show the math behind every claim with proper statistical testing
                </p>
              </div>
              <div className="border-l-4 border-green-500 pl-4">
                <h3 className="font-semibold text-gray-900 mb-2">
                  Real-Time Updates
                </h3>
                <p className="text-sm text-gray-600">
                  Automated scraping keeps data fresh and up-to-date
                </p>
              </div>
              <div className="border-l-4 border-purple-500 pl-4">
                <h3 className="font-semibold text-gray-900 mb-2">
                  Full Transparency
                </h3>
                <p className="text-sm text-gray-600">
                  Open methodology with complete data sourcing information
                </p>
              </div>
            </div>
          </div>
        </section>
      </div>
    </div>
  );
}
