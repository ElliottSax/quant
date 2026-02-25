"use client";

import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';

interface PriceData {
  timestamp: string;
  open: number;
  high: number;
  low: number;
  close: number;
  volume: number;
}

interface PriceChartProps {
  data: PriceData[];
  symbol: string;
}

export function PriceChart({ data, symbol }: PriceChartProps) {
  const chartData = data.map(bar => ({
    date: new Date(bar.timestamp).toLocaleDateString(),
    price: bar.close,
    high: bar.high,
    low: bar.low
  }));

  return (
    <div className="w-full h-96 bg-white dark:bg-slate-800 rounded-lg p-4 shadow-lg">
      <h3 className="text-lg font-semibold mb-4 text-gray-900 dark:text-white">
        {symbol} Price Chart
      </h3>
      <ResponsiveContainer width="100%" height="100%">
        <LineChart data={chartData}>
          <CartesianGrid strokeDasharray="3 3" stroke="#444" />
          <XAxis
            dataKey="date"
            stroke="#888"
            tick={{ fill: '#888' }}
          />
          <YAxis
            stroke="#888"
            tick={{ fill: '#888' }}
            domain={['auto', 'auto']}
          />
          <Tooltip
            contentStyle={{
              backgroundColor: '#1e293b',
              border: '1px solid #475569',
              borderRadius: '8px'
            }}
            labelStyle={{ color: '#f1f5f9' }}
          />
          <Legend />
          <Line
            type="monotone"
            dataKey="price"
            stroke="#3b82f6"
            strokeWidth={2}
            dot={false}
            name="Close Price"
          />
        </LineChart>
      </ResponsiveContainer>
    </div>
  );
}
