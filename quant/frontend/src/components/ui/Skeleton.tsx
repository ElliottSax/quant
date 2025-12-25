/**
 * Skeleton Loading Component
 * Modern skeleton screens for better loading UX
 */

'use client'

import { cn } from '@/lib/utils'

interface SkeletonProps {
  className?: string
  variant?: 'default' | 'rounded' | 'circle'
  animation?: 'pulse' | 'shimmer' | 'none'
}

export function Skeleton({
  className,
  variant = 'default',
  animation = 'shimmer',
}: SkeletonProps) {
  const variantClasses = {
    default: 'rounded-md',
    rounded: 'rounded-xl',
    circle: 'rounded-full',
  }

  const animationClasses = {
    pulse: 'animate-pulse',
    shimmer: 'animate-shimmer bg-[length:200%_100%] bg-gradient-to-r from-muted via-muted/50 to-muted',
    none: '',
  }

  return (
    <div
      className={cn(
        'bg-muted',
        variantClasses[variant],
        animationClasses[animation],
        className
      )}
    />
  )
}

// Pre-built skeleton components for common use cases

export function SkeletonCard() {
  return (
    <div className="bg-card border border-border rounded-xl p-6 space-y-4">
      <div className="flex items-center gap-4">
        <Skeleton variant="circle" className="w-12 h-12" />
        <div className="flex-1 space-y-2">
          <Skeleton className="h-4 w-3/4" />
          <Skeleton className="h-3 w-1/2" />
        </div>
      </div>
      <Skeleton className="h-32 w-full" variant="rounded" />
      <div className="flex gap-2">
        <Skeleton className="h-8 w-20" variant="rounded" />
        <Skeleton className="h-8 w-20" variant="rounded" />
      </div>
    </div>
  )
}

export function SkeletonTable({ rows = 5 }: { rows?: number }) {
  return (
    <div className="bg-card border border-border rounded-xl overflow-hidden">
      {/* Header */}
      <div className="bg-muted/50 border-b border-border p-4">
        <div className="grid grid-cols-4 gap-4">
          {[1, 2, 3, 4].map((i) => (
            <Skeleton key={i} className="h-4" />
          ))}
        </div>
      </div>

      {/* Rows */}
      <div className="divide-y divide-border">
        {Array.from({ length: rows }).map((_, i) => (
          <div key={i} className="p-4">
            <div className="grid grid-cols-4 gap-4">
              {[1, 2, 3, 4].map((j) => (
                <Skeleton key={j} className="h-4" />
              ))}
            </div>
          </div>
        ))}
      </div>
    </div>
  )
}

export function SkeletonMetrics() {
  return (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
      {[1, 2, 3, 4].map((i) => (
        <div key={i} className="bg-card border border-border rounded-xl p-6 space-y-3">
          <Skeleton className="h-3 w-24" />
          <Skeleton className="h-8 w-32" />
          <Skeleton className="h-2 w-16" />
        </div>
      ))}
    </div>
  )
}

export function SkeletonChart() {
  return (
    <div className="bg-card border border-border rounded-xl p-6">
      <div className="space-y-4">
        <div className="flex items-center justify-between">
          <Skeleton className="h-6 w-32" />
          <Skeleton className="h-8 w-24" variant="rounded" />
        </div>
        <Skeleton className="h-64 w-full" variant="rounded" />
      </div>
    </div>
  )
}

export function SkeletonList({ items = 5 }: { items?: number }) {
  return (
    <div className="space-y-3">
      {Array.from({ length: items }).map((_, i) => (
        <div key={i} className="flex items-center gap-4 bg-card border border-border rounded-lg p-4">
          <Skeleton variant="circle" className="w-10 h-10" />
          <div className="flex-1 space-y-2">
            <Skeleton className="h-4 w-3/4" />
            <Skeleton className="h-3 w-1/2" />
          </div>
          <Skeleton className="h-8 w-24" variant="rounded" />
        </div>
      ))}
    </div>
  )
}
