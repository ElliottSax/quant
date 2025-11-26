/**
 * Pattern Match Chart Component
 * Visualizes DTW pattern matching results with similarity scores
 */

'use client'

import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  Cell,
  ReferenceLine,
} from 'recharts'
import { PatternMatch } from '@/lib/types'

interface PatternMatchChartProps {
  matches: PatternMatch[]
  title?: string
  height?: number
}

export function PatternMatchChart({
  matches,
  title = 'Historical Pattern Matches',
  height = 300,
}: PatternMatchChartProps) {
  const data = matches.map(match => ({
    date: new Date(match.match_date).toLocaleDateString(),
    similarity: match.similarity_score * 100,
    confidence: match.confidence * 100,
    outcome30d: match.outcome_30d_trades,
    outcome90d: match.outcome_90d_trades,
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
            dataKey="date"
            angle={-45}
            textAnchor="end"
            height={80}
            tick={{ fontSize: 11 }}
            label={{ value: 'Match Date', position: 'bottom', offset: 40 }}
          />
          <YAxis
            domain={[0, 100]}
            label={{ value: 'Similarity Score (%)', angle: -90, position: 'insideLeft' }}
            tick={{ fontSize: 11 }}
          />
          <Tooltip
            content={({ active, payload }) => {
              if (!active || !payload || !payload.length) return null

              const data = payload[0].payload
              return (
                <div className="bg-background border border-border rounded-lg p-3 shadow-lg">
                  <p className="font-semibold text-sm mb-2">{data.date}</p>
                  <div className="space-y-1 text-xs">
                    <div className="flex justify-between gap-4">
                      <span className="text-muted-foreground">Similarity:</span>
                      <span className="font-medium">{data.similarity.toFixed(1)}%</span>
                    </div>
                    <div className="flex justify-between gap-4">
                      <span className="text-muted-foreground">Confidence:</span>
                      <span className="font-medium">{data.confidence.toFixed(1)}%</span>
                    </div>
                    {data.outcome30d !== null && (
                      <div className="flex justify-between gap-4">
                        <span className="text-muted-foreground">30-day outcome:</span>
                        <span className="font-medium">{data.outcome30d.toFixed(1)} trades</span>
                      </div>
                    )}
                    {data.outcome90d !== null && (
                      <div className="flex justify-between gap-4">
                        <span className="text-muted-foreground">90-day outcome:</span>
                        <span className="font-medium">{data.outcome90d.toFixed(1)} trades</span>
                      </div>
                    )}
                  </div>
                </div>
              )
            }}
          />

          <Bar dataKey="similarity" name="Similarity Score" radius={[4, 4, 0, 0]}>
            {data.map((entry, index) => {
              // Color based on similarity score
              let color = '#3b82f6' // Blue for medium
              if (entry.similarity >= 90) color = '#22c55e' // Green for high
              else if (entry.similarity >= 80) color = '#10b981' // Light green
              else if (entry.similarity < 70) color = '#f59e0b' // Orange for low

              return <Cell key={`cell-${index}`} fill={color} />
            })}
          </Bar>

          {/* Reference line for high similarity threshold */}
          <ReferenceLine
            y={85}
            stroke="#22c55e"
            strokeDasharray="3 3"
            label={{
              value: 'High Similarity',
              position: 'right',
              fontSize: 10,
            }}
          />

          {/* Reference line for medium similarity threshold */}
          <ReferenceLine
            y={70}
            stroke="#f59e0b"
            strokeDasharray="3 3"
            label={{
              value: 'Medium Similarity',
              position: 'right',
              fontSize: 10,
            }}
          />
        </BarChart>
      </ResponsiveContainer>

      <div className="mt-4 grid grid-cols-3 gap-3 text-xs text-center">
        <div>
          <div className="w-4 h-4 bg-[#22c55e] rounded mx-auto mb-1" />
          <p className="text-muted-foreground">High (≥90%)</p>
        </div>
        <div>
          <div className="w-4 h-4 bg-[#3b82f6] rounded mx-auto mb-1" />
          <p className="text-muted-foreground">Medium (70-90%)</p>
        </div>
        <div>
          <div className="w-4 h-4 bg-[#f59e0b] rounded mx-auto mb-1" />
          <p className="text-muted-foreground">Low (&lt;70%)</p>
        </div>
      </div>

      <div className="mt-2 text-xs text-muted-foreground text-center">
        <p>Higher similarity scores indicate stronger historical precedent for current trading pattern.</p>
      </div>
    </div>
  )
}
