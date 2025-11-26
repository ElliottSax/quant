"use client";

import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer, Area, AreaChart } from 'recharts';

interface EquityPoint {
  timestamp: string;
  equity: number;
}

interface EquityCurveChartProps {
  data: EquityPoint[];
  initialCapital: number;
}

export function EquityCurveChart({ data, initialCapital }: EquityCurveChartProps) {
  const chartData = data.map(point => ({
    date: new Date(point.timestamp).toLocaleDateString(),
    equity: point.equity,
    return: ((point.equity / initialCapital - 1) * 100)
  }));

  return (
    <div className="w-full h-96 bg-white dark:bg-slate-800 rounded-lg p-4 shadow-lg">
      <h3 className="text-lg font-semibold mb-4 text-gray-900 dark:text-white">
        Equity Curve
      </h3>
      <ResponsiveContainer width="100%" height="100%">
        <AreaChart data={chartData}>
          <defs>
            <linearGradient id="colorEquity" x1="0" y1="0" x2="0" y2="1">
              <stop offset="5%" stopColor="#3b82f6" stopOpacity={0.8}/>
              <stop offset="95%" stopColor="#3b82f6" stopOpacity={0}/>
            </linearGradient>
          </defs>
          <CartesianGrid strokeDasharray="3 3" stroke="#444" />
          <XAxis
            dataKey="date"
            stroke="#888"
            tick={{ fill: '#888' }}
          />
          <YAxis
            yAxisId="left"
            stroke="#888"
            tick={{ fill: '#888' }}
            label={{ value: 'Equity ($)', angle: -90, position: 'insideLeft', fill: '#888' }}
          />
          <YAxis
            yAxisId="right"
            orientation="right"
            stroke="#888"
            tick={{ fill: '#888' }}
            label={{ value: 'Return (%)', angle: 90, position: 'insideRight', fill: '#888' }}
          />
          <Tooltip
            contentStyle={{
              backgroundColor: '#1e293b',
              border: '1px solid #475569',
              borderRadius: '8px'
            }}
            formatter={(value: number, name: string) => {
              if (name === 'equity') return `$${value.toLocaleString()}`;
              if (name === 'return') return `${value.toFixed(2)}%`;
              return value;
            }}
          />
          <Legend />
          <Area
            yAxisId="left"
            type="monotone"
            dataKey="equity"
            stroke="#3b82f6"
            fillOpacity={1}
            fill="url(#colorEquity)"
            name="Equity"
          />
          <Line
            yAxisId="right"
            type="monotone"
            dataKey="return"
            stroke="#10b981"
            strokeWidth={2}
            dot={false}
            name="Return %"
          />
        </AreaChart>
      </ResponsiveContainer>
    </div>
  );
}
