"use client";

import { PieChart, Pie, Cell, ResponsiveContainer, Legend, Tooltip } from 'recharts';

interface PortfolioChartProps {
  weights: Record<string, number>;
}

const COLORS = ['#3b82f6', '#8b5cf6', '#ec4899', '#f59e0b', '#10b981', '#06b6d4', '#6366f1'];

export function PortfolioChart({ weights }: PortfolioChartProps) {
  const data = Object.entries(weights).map(([symbol, weight]) => ({
    name: symbol,
    value: weight * 100
  }));

  return (
    <div className="w-full h-96 bg-white dark:bg-slate-800 rounded-lg p-4 shadow-lg">
      <h3 className="text-lg font-semibold mb-4 text-gray-900 dark:text-white">
        Portfolio Allocation
      </h3>
      <ResponsiveContainer width="100%" height="100%">
        <PieChart>
          <Pie
            data={data}
            cx="50%"
            cy="50%"
            labelLine={false}
            label={({ name, value }) => `${name}: ${value.toFixed(1)}%`}
            outerRadius={120}
            fill="#8884d8"
            dataKey="value"
          >
            {data.map((entry, index) => (
              <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
            ))}
          </Pie>
          <Tooltip
            formatter={(value: number) => `${value.toFixed(2)}%`}
            contentStyle={{
              backgroundColor: '#1e293b',
              border: '1px solid #475569',
              borderRadius: '8px'
            }}
          />
          <Legend />
        </PieChart>
      </ResponsiveContainer>
    </div>
  );
}
