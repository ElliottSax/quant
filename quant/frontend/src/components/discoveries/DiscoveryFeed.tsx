/**
 * Discovery Feed Component - Shows discovered patterns as cards
 */

import { formatDistanceToNow } from 'date-fns'
import Link from 'next/link'

interface Discovery {
  id: string
  discovery_date: string
  politician_id: string
  politician_name: string
  pattern_type: string
  strength: number
  confidence: number
  description: string
  parameters: Record<string, any>
  metadata: Record<string, any>
  reviewed: boolean
  deployed: boolean
}

interface DiscoveryFeedProps {
  discoveries: Discovery[]
}

export function DiscoveryFeed({ discoveries }: DiscoveryFeedProps) {
  if (!discoveries || discoveries.length === 0) {
    return (
      <div className="text-center py-12 bg-card border border-border rounded-lg">
        <p className="text-muted-foreground">No discoveries found in this time range.</p>
        <p className="text-sm text-muted-foreground mt-2">
          Try adjusting the filters or check back later.
        </p>
      </div>
    )
  }

  return (
    <div className="space-y-4">
      {discoveries.map((discovery) => (
        <DiscoveryCard key={discovery.id} discovery={discovery} />
      ))}
    </div>
  )
}

function DiscoveryCard({ discovery }: { discovery: Discovery }) {
  const patternTypeConfig = {
    fourier_cycle: {
      icon: '🔄',
      label: 'Cyclical Pattern',
      color: 'blue',
    },
    regime_transition: {
      icon: '📊',
      label: 'Regime Change',
      color: 'purple',
    },
    correlation: {
      icon: '🔗',
      label: 'Correlation',
      color: 'green',
    },
    leading_indicator: {
      icon: '🎯',
      label: 'Leading Indicator',
      color: 'amber',
    },
    novel_pattern: {
      icon: '✨',
      label: 'Novel Pattern',
      color: 'pink',
    },
  }

  const config = patternTypeConfig[discovery.pattern_type] || {
    icon: '🔍',
    label: discovery.pattern_type,
    color: 'gray',
  }

  const isNew = new Date(discovery.discovery_date) > new Date(Date.now() - 24 * 60 * 60 * 1000)

  return (
    <div className="bg-card border border-border rounded-lg p-6 hover:border-primary/50 transition-all">
      {/* Header */}
      <div className="flex items-start justify-between mb-4">
        <div className="flex items-center gap-3">
          <div className="text-3xl">{config.icon}</div>
          <div>
            <div className="flex items-center gap-2">
              <h3 className="font-semibold">{config.label}</h3>
              {isNew && (
                <span className="px-2 py-0.5 text-xs font-semibold bg-primary text-primary-foreground rounded-full">
                  NEW
                </span>
              )}
              {discovery.deployed && (
                <span className="px-2 py-0.5 text-xs font-semibold bg-green-500/10 text-green-500 rounded-full">
                  DEPLOYED
                </span>
              )}
            </div>
            <Link
              href={`/politicians/${discovery.politician_id}`}
              className="text-sm text-primary hover:underline"
            >
              {discovery.politician_name}
            </Link>
          </div>
        </div>

        <div className="text-right">
          <div className="text-xs text-muted-foreground">
            {formatDistanceToNow(new Date(discovery.discovery_date), { addSuffix: true })}
          </div>
        </div>
      </div>

      {/* Description */}
      <p className="text-sm text-muted-foreground mb-4">{discovery.description}</p>

      {/* Metrics */}
      <div className="grid grid-cols-2 gap-4 mb-4">
        <div>
          <div className="text-xs text-muted-foreground mb-1">Pattern Strength</div>
          <div className="flex items-center gap-2">
            <div className="flex-1 h-2 bg-muted rounded-full overflow-hidden">
              <div
                className="h-full bg-primary rounded-full transition-all"
                style={{ width: `${discovery.strength * 100}%` }}
              />
            </div>
            <span className="text-sm font-semibold">{(discovery.strength * 100).toFixed(0)}%</span>
          </div>
        </div>

        <div>
          <div className="text-xs text-muted-foreground mb-1">Confidence</div>
          <div className="flex items-center gap-2">
            <div className="flex-1 h-2 bg-muted rounded-full overflow-hidden">
              <div
                className="h-full bg-green-500 rounded-full transition-all"
                style={{ width: `${discovery.confidence * 100}%` }}
              />
            </div>
            <span className="text-sm font-semibold">{(discovery.confidence * 100).toFixed(0)}%</span>
          </div>
        </div>
      </div>

      {/* Parameters Used */}
      <details className="text-xs">
        <summary className="cursor-pointer text-muted-foreground hover:text-foreground">
          Discovery Parameters
        </summary>
        <pre className="mt-2 p-3 bg-muted rounded-lg overflow-x-auto">
          {JSON.stringify(discovery.parameters, null, 2)}
        </pre>
      </details>

      {/* Actions */}
      <div className="flex items-center gap-3 mt-4 pt-4 border-t border-border">
        <Link
          href={`/politicians/${discovery.politician_id}`}
          className="text-sm text-primary hover:underline"
        >
          View Politician →
        </Link>
        <Link
          href={`/discoveries/${discovery.id}`}
          className="text-sm text-primary hover:underline"
        >
          Full Analysis →
        </Link>
      </div>
    </div>
  )
}
