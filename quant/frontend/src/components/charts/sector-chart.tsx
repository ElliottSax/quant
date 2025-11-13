/**
 * Sector/Ticker Chart Component
 * Displays top traded tickers with buy/sell distribution
 */

'use client';

import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';
import { TickerStat } from '@/lib/api-client';

interface SectorChartProps {
  data: TickerStat[];
  showTop?: number;
}

export function SectorChart({ data, showTop = 10 }: SectorChartProps) {
  // Take only top N tickers
  const chartData = data.slice(0, showTop).map((ticker) => ({
    ticker: ticker.ticker,
    buys: ticker.buy_count,
    sells: ticker.sell_count,
    total: ticker.trade_count,
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
          <XAxis dataKey="ticker" />
          <YAxis />
          <Tooltip />
          <Legend />
          <Bar dataKey="buys" fill="#10b981" name="Buys" />
          <Bar dataKey="sells" fill="#ef4444" name="Sells" />
        </BarChart>
      </ResponsiveContainer>
    </div>
  );
}
