/**
 * Discoveries Page - Shows patterns found by background discovery service
 */

'use client'

import { useState } from 'react'
import { useDiscoveries, useCriticalAnomalies, useRecentExperiments } from '@/lib/hooks'
import { DiscoveryFeed } from '@/components/discoveries/DiscoveryFeed'
import { AnomalyAlerts } from '@/components/discoveries/AnomalyAlerts'
import { ExperimentResults } from '@/components/discoveries/ExperimentResults'
import { DiscoveryStats } from '@/components/discoveries/DiscoveryStats'
import Link from 'next/link'

export default function DiscoveriesPage() {
  const [timeRange, setTimeRange] = useState('24h')
  const [minStrength, setMinStrength] = useState(0.8)

  const { data: discoveries, isLoading: discoveriesLoading } = useDiscoveries({
    timeRange,
    minStrength,
  })

  const { data: anomalies, isLoading: anomaliesLoading } = useCriticalAnomalies({
    minSeverity: 0.8,
  })

  const { data: experiments } = useRecentExperiments()

  if (discoveriesLoading || anomaliesLoading) {
    return <LoadingSpinner />
  }

  return (
    <div className="space-y-8">
      {/* Header */}
      <div>
        <h1 className="text-3xl font-bold">Pattern Discoveries</h1>
        <p className="text-muted-foreground mt-2">
          Hidden patterns found by our AI that continuously analyzes all Congressional trading
        </p>
      </div>

      {/* Critical Alerts Banner */}
      {anomalies && anomalies.length > 0 && (
        <div className="bg-red-500/10 border border-red-500/50 rounded-lg p-6">
          <div className="flex items-center gap-3 mb-4">
            <div className="w-3 h-3 bg-red-500 rounded-full animate-pulse" />
            <h2 className="text-xl font-bold text-red-500">
              {anomalies.length} Critical Anomalies Detected
            </h2>
          </div>
          <AnomalyAlerts anomalies={anomalies} />
        </div>
      )}

      {/* Stats Overview */}
      <DiscoveryStats
        totalDiscoveries={discoveries?.length || 0}
        criticalAnomalies={anomalies?.length || 0}
        newExperiments={experiments?.filter(e => e.deployment_ready).length || 0}
      />

      {/* Filters */}
      <div className="flex items-center gap-4">
        <select
          value={timeRange}
          onChange={(e) => setTimeRange(e.target.value)}
          className="px-4 py-2 bg-card border border-border rounded-lg"
        >
          <option value="24h">Last 24 Hours</option>
          <option value="7d">Last 7 Days</option>
          <option value="30d">Last 30 Days</option>
          <option value="all">All Time</option>
        </select>

        <div className="flex items-center gap-2">
          <label className="text-sm text-muted-foreground">Min Strength:</label>
          <input
            type="range"
            min="0"
            max="1"
            step="0.1"
            value={minStrength}
            onChange={(e) => setMinStrength(parseFloat(e.target.value))}
            className="w-32"
          />
          <span className="text-sm font-medium">{(minStrength * 100).toFixed(0)}%</span>
        </div>
      </div>

      {/* Discovery Feed */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Main Feed */}
        <div className="lg:col-span-2">
          <DiscoveryFeed discoveries={discoveries} />
        </div>

        {/* Sidebar */}
        <div className="space-y-6">
          {/* Experiment Results */}
          <div className="bg-card border border-border rounded-lg p-6">
            <h3 className="text-lg font-semibold mb-4">New Models Tested</h3>
            <ExperimentResults experiments={experiments} />
          </div>

          {/* Quick Actions */}
          <div className="bg-card border border-border rounded-lg p-6">
            <h3 className="text-lg font-semibold mb-4">Explore</h3>
            <div className="space-y-3">
              <Link
                href="/discoveries/anomalies"
                className="block p-3 rounded-lg hover:bg-muted/50 transition-colors"
              >
                <div className="font-medium">All Anomalies</div>
                <div className="text-sm text-muted-foreground">
                  View all detected anomalies
                </div>
              </Link>
              <Link
                href="/discoveries/patterns"
                className="block p-3 rounded-lg hover:bg-muted/50 transition-colors"
              >
                <div className="font-medium">Pattern Library</div>
                <div className="text-sm text-muted-foreground">
                  Browse all discovered patterns
                </div>
              </Link>
              <Link
                href="/discoveries/experiments"
                className="block p-3 rounded-lg hover:bg-muted/50 transition-colors"
              >
                <div className="font-medium">Model Lab</div>
                <div className="text-sm text-muted-foreground">
                  See experimental model results
                </div>
              </Link>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}

function LoadingSpinner() {
  return (
    <div className="flex items-center justify-center min-h-[400px]">
      <div className="text-center">
        <div className="inline-block h-8 w-8 animate-spin rounded-full border-4 border-solid border-current border-r-transparent" />
        <p className="mt-4 text-muted-foreground">Loading discoveries...</p>
      </div>
    </div>
  )
}
