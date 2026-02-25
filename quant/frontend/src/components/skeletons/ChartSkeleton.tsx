/**
 * Chart Loading Skeleton
 *
 * Shown while chart components are lazy-loading.
 * Matches the terminal/BigCharts visual style.
 */

'use client'

export function ChartSkeleton() {
  return (
    <div className="h-full w-full bg-[hsl(220,55%,6%)] rounded border border-[hsl(215,40%,18%)] p-4 animate-pulse">
      {/* Chart Header */}
      <div className="flex items-center justify-between mb-4">
        <div className="h-4 w-32 bg-[hsl(215,40%,16%)] rounded" />
        <div className="flex gap-2">
          <div className="h-6 w-12 bg-[hsl(215,40%,16%)] rounded" />
          <div className="h-6 w-12 bg-[hsl(215,40%,16%)] rounded" />
        </div>
      </div>

      {/* Chart Area */}
      <div className="relative h-[calc(100%-3rem)]">
        {/* Y-Axis Labels */}
        <div className="absolute left-0 top-0 bottom-0 w-12 flex flex-col justify-between py-2">
          <div className="h-3 w-10 bg-[hsl(215,40%,16%)] rounded" />
          <div className="h-3 w-10 bg-[hsl(215,40%,16%)] rounded" />
          <div className="h-3 w-10 bg-[hsl(215,40%,16%)] rounded" />
          <div className="h-3 w-10 bg-[hsl(215,40%,16%)] rounded" />
          <div className="h-3 w-10 bg-[hsl(215,40%,16%)] rounded" />
        </div>

        {/* Chart Grid */}
        <div className="absolute left-14 right-0 top-0 bottom-8 flex flex-col justify-between">
          <div className="h-px bg-[hsl(215,40%,12%)]" />
          <div className="h-px bg-[hsl(215,40%,12%)]" />
          <div className="h-px bg-[hsl(215,40%,12%)]" />
          <div className="h-px bg-[hsl(215,40%,12%)]" />
          <div className="h-px bg-[hsl(215,40%,12%)]" />
        </div>

        {/* Chart Bars/Lines */}
        <div className="absolute left-14 right-0 bottom-8 h-40 flex items-end justify-around gap-1">
          {[...Array(12)].map((_, i) => (
            <div
              key={i}
              className="flex-1 bg-gradient-to-t from-[hsl(215,40%,20%)] to-[hsl(215,40%,16%)] rounded-t"
              style={{ height: `${Math.random() * 60 + 40}%` }}
            />
          ))}
        </div>

        {/* X-Axis Labels */}
        <div className="absolute left-14 right-0 bottom-0 h-6 flex justify-between items-center">
          {[...Array(6)].map((_, i) => (
            <div key={i} className="h-3 w-8 bg-[hsl(215,40%,16%)] rounded" />
          ))}
        </div>
      </div>
    </div>
  )
}
