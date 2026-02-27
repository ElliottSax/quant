'use client'

import {
  BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip,
  ResponsiveContainer, Cell,
} from 'recharts'

interface TradeDistributionChartProps {
  tradeDistribution: Array<{ returnRange: string; count: number; value: number }>
}

export function TradeDistributionChart({ tradeDistribution }: TradeDistributionChartProps) {
  return (
    <div className="glass-strong rounded-xl p-6">
      <h2 className="text-2xl font-bold mb-4">Trade Return Distribution</h2>
      <ResponsiveContainer width="100%" height={300}>
        <BarChart data={tradeDistribution}>
          <CartesianGrid strokeDasharray="3 3" stroke="#334155" />
          <XAxis dataKey="returnRange" stroke="#94a3b8" tick={{ fontSize: 12 }} />
          <YAxis stroke="#94a3b8" tick={{ fontSize: 12 }} />
          <Tooltip
            contentStyle={{ backgroundColor: '#1e293b', border: '1px solid #334155', borderRadius: '8px' }}
          />
          <Bar dataKey="count" name="Number of Trades">
            {tradeDistribution.map((entry, index) => (
              <Cell key={`cell-${index}`} fill={entry.value >= 0 ? '#10b981' : '#ef4444'} opacity={0.8} />
            ))}
          </Bar>
        </BarChart>
      </ResponsiveContainer>
    </div>
  )
}
