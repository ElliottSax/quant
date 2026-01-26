/**
 * Table Loading Skeleton
 *
 * Shown while table/data grid components are lazy-loading.
 * Matches the terminal/BigCharts visual style.
 */

'use client'

interface TableSkeletonProps {
  rows?: number
  columns?: number
}

export function TableSkeleton({ rows = 10, columns = 5 }: TableSkeletonProps) {
  return (
    <div className="h-full w-full bg-[hsl(220,55%,6%)] rounded border border-[hsl(215,40%,18%)] overflow-hidden">
      {/* Table Header */}
      <div className="bg-[hsl(215,50%,10%)] border-b border-[hsl(215,40%,18%)] px-4 py-3">
        <div className="grid gap-4" style={{ gridTemplateColumns: `repeat(${columns}, 1fr)` }}>
          {[...Array(columns)].map((_, i) => (
            <div key={i} className="h-4 bg-[hsl(215,40%,20%)] rounded animate-pulse" />
          ))}
        </div>
      </div>

      {/* Table Rows */}
      <div className="divide-y divide-[hsl(215,40%,12%)]">
        {[...Array(rows)].map((_, rowIndex) => (
          <div key={rowIndex} className="px-4 py-3 animate-pulse">
            <div className="grid gap-4" style={{ gridTemplateColumns: `repeat(${columns}, 1fr)` }}>
              {[...Array(columns)].map((_, colIndex) => (
                <div
                  key={colIndex}
                  className="h-4 bg-[hsl(215,40%,16%)] rounded"
                  style={{
                    width: `${60 + Math.random() * 40}%`,
                    animationDelay: `${(rowIndex * columns + colIndex) * 50}ms`,
                  }}
                />
              ))}
            </div>
          </div>
        ))}
      </div>
    </div>
  )
}
