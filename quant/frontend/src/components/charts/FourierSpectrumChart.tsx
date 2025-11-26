/**
 * Fourier Spectrum Chart Component
 * Visualizes frequency domain analysis showing dominant cycles
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
  ReferenceLine,
} from 'recharts'
import { CycleInfo } from '@/lib/types'

interface FourierSpectrumChartProps {
  cycles: CycleInfo[]
  title?: string
  height?: number
}

export function FourierSpectrumChart({
  cycles,
  title = 'Dominant Trading Cycles',
  height = 300,
}: FourierSpectrumChartProps) {
  // Sort cycles by strength
  const sortedCycles = [...cycles].sort((a, b) => b.strength - a.strength)

  // Color mapping by cycle category
  const getCategoryColor = (category: string) => {
    const colors: Record<string, string> = {
      weekly: '#3b82f6',
      biweekly: '#8b5cf6',
      monthly: '#10b981',
      quarterly: '#f59e0b',
      semiannual: '#ef4444',
      annual: '#6366f1',
    }
    return colors[category.toLowerCase()] || '#6b7280'
  }

  const data = sortedCycles.map(cycle => ({
    name: `${cycle.period_days.toFixed(0)} days`,
    strength: cycle.strength,
    confidence: cycle.confidence,
    category: cycle.category,
    period: cycle.period_days,
  }))

  return (
    <div className="w-full">
      {title && <h3 className="text-lg font-semibold mb-4">{title}</h3>}

      <ResponsiveContainer width="100%" height={height}>
        <BarChart
          data={data}
          margin={{ top: 20, right: 30, left: 20, bottom: 60 }}
        >
          <CartesianGrid strokeDasharray="3 3" opacity={0.3} />
          <XAxis
            dataKey="name"
            angle={-45}
            textAnchor="end"
            height={80}
            tick={{ fontSize: 11 }}
            label={{
              value: 'Period (days)',
              position: 'bottom',
              offset: 40,
            }}
          />
          <YAxis
            label={{
              value: 'Strength (Power Spectrum)',
              angle: -90,
              position: 'insideLeft',
            }}
            tick={{ fontSize: 11 }}
          />
          <Tooltip
            content={({ active, payload }) => {
              if (!active || !payload || !payload.length) return null

              const data = payload[0].payload
              return (
                <div className="bg-background border border-border rounded-lg p-3 shadow-lg">
                  <p className="font-semibold text-sm mb-1">{data.category} Cycle</p>
                  <p className="text-xs text-muted-foreground mb-2">
                    Period: {data.period.toFixed(1)} days
                  </p>
                  <div className="space-y-1">
                    <div className="flex justify-between gap-4 text-xs">
                      <span className="text-muted-foreground">Strength:</span>
                      <span className="font-medium">{data.strength.toFixed(4)}</span>
                    </div>
                    <div className="flex justify-between gap-4 text-xs">
                      <span className="text-muted-foreground">Confidence:</span>
                      <span className="font-medium">{(data.confidence * 100).toFixed(1)}%</span>
                    </div>
                  </div>
                </div>
              )
            }}
          />
          <Legend
            content={() => (
              <div className="flex flex-wrap justify-center gap-3 mt-4">
                {Array.from(new Set(sortedCycles.map(c => c.category))).map(cat => (
                  <div key={cat} className="flex items-center gap-2">
                    <div
                      className="w-4 h-4 rounded"
                      style={{ backgroundColor: getCategoryColor(cat) }}
                    />
                    <span className="text-xs capitalize">{cat}</span>
                  </div>
                ))}
              </div>
            )}
          />

          <Bar dataKey="strength" radius={[4, 4, 0, 0]}>
            {data.map((entry, index) => (
              <Cell key={`cell-${index}`} fill={getCategoryColor(entry.category)} />
            ))}
          </Bar>

          {/* Highlight high confidence cycles */}
          {data.filter(d => d.confidence > 0.8).map((entry, idx) => (
            <ReferenceLine
              key={`high-conf-${idx}`}
              y={entry.strength}
              stroke="#22c55e"
              strokeDasharray="3 3"
              strokeWidth={1}
            />
          ))}
        </BarChart>
      </ResponsiveContainer>

      <div className="mt-2 text-xs text-muted-foreground text-center">
        <p>Higher bars indicate stronger cyclical patterns. Green dashed lines mark high-confidence cycles (&gt;80%).</p>
      </div>
    </div>
  )
}
