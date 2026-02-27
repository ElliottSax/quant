'use client'

import {
  BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip,
  ResponsiveContainer, ReferenceLine, Cell,
} from 'recharts'

interface MonthlyReturnsChartProps {
  monthlyReturns: Array<{ month: string; return: number }>
}

export function MonthlyReturnsChart({ monthlyReturns }: MonthlyReturnsChartProps) {
  return (
    <div className="glass-strong rounded-xl p-6">
      <h2 className="text-2xl font-bold mb-4">Monthly Returns</h2>
      <ResponsiveContainer width="100%" height={300}>
        <BarChart data={monthlyReturns}>
          <CartesianGrid strokeDasharray="3 3" stroke="#334155" />
          <XAxis dataKey="month" stroke="#94a3b8" tick={{ fontSize: 12 }} />
          <YAxis stroke="#94a3b8" tick={{ fontSize: 12 }} tickFormatter={(value) => `${value}%`} />
          <Tooltip
            contentStyle={{ backgroundColor: '#1e293b', border: '1px solid #334155', borderRadius: '8px' }}
            formatter={(value: any) => `${value.toFixed(2)}%`}
          />
          <ReferenceLine y={0} stroke="#6b7280" />
          <Bar dataKey="return" name="Monthly Return %">
            {monthlyReturns.map((entry, index) => (
              <Cell key={`cell-${index}`} fill={entry.return >= 0 ? '#10b981' : '#ef4444'} />
            ))}
          </Bar>
        </BarChart>
      </ResponsiveContainer>
    </div>
  )
}
