/**
 * Regime Transition Chart Component
 * Visualizes HMM trading regime transitions and characteristics
 */

'use client'

import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
  Cell,
  ComposedChart,
  Line,
} from 'recharts'
import { RegimeInfo } from '@/lib/types'

interface RegimeTransitionChartProps {
  regimes: RegimeInfo[]
  currentRegime: number
  transitionProbs?: Record<string, number>
  title?: string
  height?: number
}

export function RegimeTransitionChart({
  regimes,
  currentRegime,
  transitionProbs,
  title = 'Trading Regime Analysis',
  height = 350,
}: RegimeTransitionChartProps) {
  const data = regimes.map((regime, idx) => ({
    name: regime.name,
    avgReturn: regime.avg_return,
    volatility: regime.volatility,
    frequency: regime.frequency * 100, // Convert to percentage
    sampleSize: regime.sample_size,
    isCurrent: idx === currentRegime,
  }))

  // Get color for regime (current vs others)
  const getColor = (isCurrent: boolean, index: number) => {
    if (isCurrent) return '#22c55e' // Green for current
    const colors = ['#3b82f6', '#8b5cf6', '#f59e0b', '#ef4444']
    return colors[index % colors.length]
  }

  return (
    <div className="w-full space-y-6">
      {title && <h3 className="text-lg font-semibold">{title}</h3>}

      {/* Regime characteristics chart */}
      <ResponsiveContainer width="100%" height={height}>
        <ComposedChart
          data={data}
          margin={{ top: 20, right: 20, bottom: 60, left: 20 }}
        >
          <CartesianGrid strokeDasharray="3 3" opacity={0.3} />
          <XAxis
            dataKey="name"
            angle={-45}
            textAnchor="end"
            height={80}
            tick={{ fontSize: 11 }}
          />
          <YAxis
            yAxisId="left"
            label={{
              value: 'Average Return',
              angle: -90,
              position: 'insideLeft',
            }}
            tick={{ fontSize: 11 }}
          />
          <YAxis
            yAxisId="right"
            orientation="right"
            label={{
              value: 'Volatility',
              angle: 90,
              position: 'insideRight',
            }}
            tick={{ fontSize: 11 }}
          />
          <Tooltip
            content={({ active, payload }) => {
              if (!active || !payload || !payload.length) return null

              const data = payload[0].payload
              return (
                <div className="bg-background border border-border rounded-lg p-3 shadow-lg">
                  <p className="font-semibold text-sm mb-2">
                    {data.name}
                    {data.isCurrent && (
                      <span className="ml-2 text-xs bg-green-500 text-white px-2 py-0.5 rounded">
                        Current
                      </span>
                    )}
                  </p>
                  <div className="space-y-1 text-xs">
                    <div className="flex justify-between gap-4">
                      <span className="text-muted-foreground">Avg Return:</span>
                      <span className="font-medium">{data.avgReturn.toFixed(3)}</span>
                    </div>
                    <div className="flex justify-between gap-4">
                      <span className="text-muted-foreground">Volatility:</span>
                      <span className="font-medium">{data.volatility.toFixed(3)}</span>
                    </div>
                    <div className="flex justify-between gap-4">
                      <span className="text-muted-foreground">Frequency:</span>
                      <span className="font-medium">{data.frequency.toFixed(1)}%</span>
                    </div>
                    <div className="flex justify-between gap-4">
                      <span className="text-muted-foreground">Sample Size:</span>
                      <span className="font-medium">{data.sampleSize}</span>
                    </div>
                  </div>
                </div>
              )
            }}
          />
          <Legend />

          <Bar yAxisId="left" dataKey="avgReturn" name="Avg Return" radius={[4, 4, 0, 0]}>
            {data.map((entry, index) => (
              <Cell key={`cell-${index}`} fill={getColor(entry.isCurrent, index)} />
            ))}
          </Bar>

          <Line
            yAxisId="right"
            type="monotone"
            dataKey="volatility"
            stroke="#ef4444"
            strokeWidth={2}
            dot={{ r: 4 }}
            name="Volatility"
          />
        </ComposedChart>
      </ResponsiveContainer>

      {/* Regime frequency distribution */}
      <ResponsiveContainer width="100%" height={150}>
        <BarChart
          data={data}
          margin={{ top: 10, right: 20, bottom: 40, left: 20 }}
          layout="vertical"
        >
          <CartesianGrid strokeDasharray="3 3" opacity={0.3} />
          <XAxis
            type="number"
            domain={[0, 100]}
            label={{ value: 'Time in Regime (%)', position: 'bottom' }}
            tick={{ fontSize: 11 }}
          />
          <YAxis
            type="category"
            dataKey="name"
            tick={{ fontSize: 11 }}
            width={100}
          />
          <Tooltip
            formatter={(value: number) => `${value.toFixed(1)}%`}
          />

          <Bar dataKey="frequency" name="Time in Regime" radius={[0, 4, 4, 0]}>
            {data.map((entry, index) => (
              <Cell key={`cell-${index}`} fill={getColor(entry.isCurrent, index)} />
            ))}
          </Bar>
        </BarChart>
      </ResponsiveContainer>

      {/* Transition probabilities (if available) */}
      {transitionProbs && Object.keys(transitionProbs).length > 0 && (
        <div className="bg-muted/50 rounded-lg p-4">
          <h4 className="text-sm font-semibold mb-3">Regime Transition Probabilities</h4>
          <div className="grid grid-cols-2 gap-3 text-xs">
            {Object.entries(transitionProbs).map(([key, prob]) => (
              <div key={key} className="flex items-center justify-between">
                <span className="text-muted-foreground">{key}:</span>
                <div className="flex items-center gap-2">
                  <div className="w-20 h-2 bg-muted rounded-full overflow-hidden">
                    <div
                      className="h-full bg-primary rounded-full transition-all"
                      style={{ width: `${prob * 100}%` }}
                    />
                  </div>
                  <span className="font-medium w-12 text-right">{(prob * 100).toFixed(1)}%</span>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      <div className="text-xs text-muted-foreground text-center">
        <p>Green highlights the current trading regime. Bar heights show average returns, line shows volatility.</p>
      </div>
    </div>
  )
}
