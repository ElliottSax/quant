/**
 * Correlation Heatmap Component
 * Visualizes correlation matrices between politicians
 */

'use client'

import { CorrelationPair } from '@/lib/types'

interface CorrelationHeatmapProps {
  correlations: CorrelationPair[]
  title?: string
}

export function CorrelationHeatmap({ correlations, title }: CorrelationHeatmapProps) {
  // Build unique list of politicians
  const politicians = Array.from(
    new Set(
      correlations.flatMap(c => [
        { id: c.politician1_id, name: c.politician1_name },
        { id: c.politician2_id, name: c.politician2_name },
      ])
    )
  )

  // Build correlation matrix
  const matrix: number[][] = []
  for (let i = 0; i < politicians.length; i++) {
    matrix[i] = []
    for (let j = 0; j < politicians.length; j++) {
      if (i === j) {
        matrix[i][j] = 1.0
      } else {
        const corr = correlations.find(
          c =>
            (c.politician1_id === politicians[i].id && c.politician2_id === politicians[j].id) ||
            (c.politician2_id === politicians[i].id && c.politician1_id === politicians[j].id)
        )
        matrix[i][j] = corr?.correlation || 0
      }
    }
  }

  // Get color for correlation value (-1 to 1)
  const getColor = (value: number) => {
    // Red (negative) to White (zero) to Blue (positive)
    if (value < 0) {
      const intensity = Math.abs(value) * 255
      return `rgb(${intensity}, 0, 0)`
    } else {
      const intensity = value * 255
      return `rgb(0, 0, ${intensity})`
    }
  }

  const cellSize = Math.max(40, Math.min(80, 600 / politicians.length))

  return (
    <div className="w-full overflow-x-auto">
      {title && <h3 className="text-lg font-semibold mb-4">{title}</h3>}

      <div className="inline-block min-w-full">
        <svg
          width={politicians.length * cellSize + 150}
          height={politicians.length * cellSize + 100}
          className="mx-auto"
        >
          {/* Column labels */}
          {politicians.map((pol, i) => (
            <text
              key={`col-${i}`}
              x={i * cellSize + cellSize / 2 + 100}
              y={cellSize - 10}
              fontSize="10"
              textAnchor="end"
              transform={`rotate(-45, ${i * cellSize + cellSize / 2 + 100}, ${cellSize - 10})`}
              className="fill-current text-foreground"
            >
              {pol.name.split(' ').slice(-1)[0]}
            </text>
          ))}

          {/* Heatmap cells */}
          {matrix.map((row, i) =>
            row.map((value, j) => (
              <g key={`cell-${i}-${j}`}>
                <rect
                  x={j * cellSize + 100}
                  y={i * cellSize + cellSize}
                  width={cellSize - 2}
                  height={cellSize - 2}
                  fill={getColor(value)}
                  stroke="#333"
                  strokeWidth="1"
                  className="transition-opacity hover:opacity-75 cursor-pointer"
                >
                  <title>
                    {politicians[i].name} ↔ {politicians[j].name}: {value.toFixed(3)}
                  </title>
                </rect>
                {Math.abs(value) > 0.5 && (
                  <text
                    x={j * cellSize + cellSize / 2 + 100}
                    y={i * cellSize + cellSize / 2 + cellSize}
                    fontSize="10"
                    textAnchor="middle"
                    dominantBaseline="middle"
                    className="fill-white font-semibold pointer-events-none"
                  >
                    {value.toFixed(2)}
                  </text>
                )}
              </g>
            ))
          )}

          {/* Row labels */}
          {politicians.map((pol, i) => (
            <text
              key={`row-${i}`}
              x={90}
              y={i * cellSize + cellSize / 2 + cellSize}
              fontSize="10"
              textAnchor="end"
              dominantBaseline="middle"
              className="fill-current text-foreground"
            >
              {pol.name.split(' ').slice(-1)[0]}
            </text>
          ))}

          {/* Color scale legend */}
          <g transform={`translate(${politicians.length * cellSize + 120}, ${cellSize})`}>
            <text x="0" y="-10" fontSize="11" fontWeight="bold" className="fill-current">
              Correlation
            </text>
            {Array.from({ length: 21 }, (_, i) => {
              const value = (i - 10) / 10
              return (
                <g key={i}>
                  <rect
                    x="0"
                    y={i * 10}
                    width="20"
                    height="10"
                    fill={getColor(value)}
                    stroke="#333"
                    strokeWidth="0.5"
                  />
                  {i % 5 === 0 && (
                    <text
                      x="25"
                      y={i * 10 + 7}
                      fontSize="9"
                      className="fill-current"
                    >
                      {value.toFixed(1)}
                    </text>
                  )}
                </g>
              )
            })}
          </g>
        </svg>
      </div>

      <div className="mt-4 text-sm text-muted-foreground text-center">
        <p>Hover over cells to see exact correlation values</p>
      </div>
    </div>
  )
}
