'use client'

import {
  ScatterChart, Scatter, XAxis, YAxis, ZAxis, CartesianGrid,
  Tooltip, Legend, ResponsiveContainer, ReferenceLine,
} from 'recharts'

interface TradeData {
  day: number
  returnPct: number
  profit: number
  isWin: boolean
}

interface TradeScatterPlotProps {
  trades: TradeData[]
}

export function TradeScatterPlot({ trades }: TradeScatterPlotProps) {
  return (
    <div className="glass-strong rounded-xl p-6">
      <h2 className="text-2xl font-bold mb-4">Trade Analysis</h2>
      <ResponsiveContainer width="100%" height={350}>
        <ScatterChart>
          <CartesianGrid strokeDasharray="3 3" stroke="#334155" />
          <XAxis dataKey="day" name="Trading Day" stroke="#94a3b8" tick={{ fontSize: 12 }} />
          <YAxis
            dataKey="returnPct" name="Return %"
            stroke="#94a3b8" tick={{ fontSize: 12 }}
            tickFormatter={(value) => `${value.toFixed(1)}%`}
          />
          <ZAxis dataKey="profit" range={[50, 400]} name="Profit" />
          <Tooltip
            cursor={{ strokeDasharray: '3 3' }}
            contentStyle={{ backgroundColor: '#1e293b', border: '1px solid #334155', borderRadius: '8px' }}
            formatter={(value: any, name: string) => {
              if (name === 'Return %') return `${value.toFixed(2)}%`
              if (name === 'Profit') return `$${value.toLocaleString(undefined, { maximumFractionDigits: 0 })}`
              return value
            }}
          />
          <Legend />
          <Scatter name="Winning Trades" data={trades.filter(t => t.isWin)} fill="#10b981" />
          <Scatter name="Losing Trades" data={trades.filter(t => !t.isWin)} fill="#ef4444" />
          <ReferenceLine y={0} stroke="#6b7280" />
        </ScatterChart>
      </ResponsiveContainer>
    </div>
  )
}
