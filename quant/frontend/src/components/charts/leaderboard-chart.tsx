/**
 * Leaderboard Chart Component
 * Displays top politicians by trade count
 */

'use client';

import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer, Cell } from 'recharts';
import { LeaderboardEntry } from '@/lib/api-client';

interface LeaderboardChartProps {
  data: LeaderboardEntry[];
  showTop?: number;
}

const PARTY_COLORS: Record<string, string> = {
  'Democrat': '#3b82f6',
  'Republican': '#ef4444',
  'Independent': '#8b5cf6',
  'default': '#6b7280',
};

export function LeaderboardChart({ data, showTop = 10 }: LeaderboardChartProps) {
  // Take only top N politicians
  const chartData = data.slice(0, showTop).map((entry) => ({
    name: entry.name.split(' ').slice(-1)[0], // Last name only for chart
    fullName: entry.name,
    trades: entry.trade_count,
    party: entry.party || 'Unknown',
    chamber: entry.chamber,
  }));

  if (chartData.length === 0) {
    return (
      <div className="flex items-center justify-center h-64 text-gray-500">
        No data available
      </div>
    );
  }

  return (
    <div className="w-full h-64">
      <ResponsiveContainer width="100%" height="100%">
        <BarChart
          data={chartData}
          margin={{ top: 20, right: 30, left: 20, bottom: 5 }}
        >
          <CartesianGrid strokeDasharray="3 3" />
          <XAxis dataKey="name" />
          <YAxis />
          <Tooltip
            content={({ active, payload }) => {
              if (active && payload && payload.length) {
                const data = payload[0].payload;
                return (
                  <div className="bg-white p-3 border border-gray-200 rounded shadow-lg">
                    <p className="font-semibold">{data.fullName}</p>
                    <p className="text-sm text-gray-600">
                      {data.party} • {data.chamber}
                    </p>
                    <p className="text-sm mt-1">
                      <span className="font-medium">{data.trades}</span> trades
                    </p>
                  </div>
                );
              }
              return null;
            }}
          />
          <Legend />
          <Bar dataKey="trades" name="Trade Count">
            {chartData.map((entry, index) => (
              <Cell
                key={`cell-${index}`}
                fill={PARTY_COLORS[entry.party] || PARTY_COLORS.default}
              />
            ))}
          </Bar>
        </BarChart>
      </ResponsiveContainer>
    </div>
  );
}
