/**
 * Dashboard Loading Skeleton
 *
 * Full-page skeleton for dashboard with multiple panels.
 * Matches the terminal/BigCharts visual style.
 */

'use client'

import { ChartSkeleton } from './ChartSkeleton'
import { TableSkeleton } from './TableSkeleton'

export function DashboardSkeleton() {
  return (
    <div className="min-h-screen bg-[hsl(220,60%,4%)] p-4 space-y-4">
      {/* Header Stats */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        {[...Array(4)].map((_, i) => (
          <div
            key={i}
            className="bg-[hsl(220,55%,6%)] rounded border border-[hsl(215,40%,18%)] p-4 animate-pulse"
          >
            <div className="h-3 w-20 bg-[hsl(215,40%,16%)] rounded mb-3" />
            <div className="h-8 w-32 bg-[hsl(215,40%,20%)] rounded mb-2" />
            <div className="h-3 w-24 bg-[hsl(215,40%,16%)] rounded" />
          </div>
        ))}
      </div>

      {/* Main Charts Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
        <div className="h-[400px]">
          <ChartSkeleton />
        </div>
        <div className="h-[400px]">
          <ChartSkeleton />
        </div>
      </div>

      {/* Data Table */}
      <div className="h-[500px]">
        <TableSkeleton rows={12} columns={6} />
      </div>
    </div>
  )
}
