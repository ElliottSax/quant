/**
 * Dashboard Page
 * Overview of platform metrics, top traders, and recent activity
 */

'use client'

import { usePoliticians, useNetworkAnalysis } from '@/lib/hooks'
import { AnomalyScoreGauge } from '@/components/charts/AnomalyScoreGauge'
import Link from 'next/link'

export default function DashboardPage() {
  const { data: politicians, isLoading: politiciansLoading } = usePoliticians(30)
  const { data: network, isLoading: networkLoading } = useNetworkAnalysis({
    min_trades: 50,
    min_correlation: 0.5,
  })

  if (politiciansLoading || networkLoading) {
    return (
      <div className="flex items-center justify-center min-h-[400px]">
        <div className="text-center">
          <div className="inline-block h-8 w-8 animate-spin rounded-full border-4 border-solid border-current border-r-transparent motion-reduce:animate-[spin_1.5s_linear_infinite]" />
          <p className="mt-4 text-muted-foreground">Loading dashboard...</p>
        </div>
      </div>
    )
  }

  const totalPoliticians = politicians?.length || 0
  const totalTrades = politicians?.reduce((sum, p) => sum + (p.trade_count || 0), 0) || 0
  const activePoliticians = politicians?.filter(p => {
    if (!p.last_trade) return false
    const lastTradeDate = new Date(p.last_trade)
    const daysSinceLastTrade = (Date.now() - lastTradeDate.getTime()) / (1000 * 60 * 60 * 24)
    return daysSinceLastTrade <= 7
  }).length || 0

  const topTraders = [...(politicians || [])]
    .sort((a, b) => (b.trade_count || 0) - (a.trade_count || 0))
    .slice(0, 10)

  return (
    <div className="space-y-8">
      {/* Page header */}
      <div>
        <h1 className="text-3xl font-bold">Dashboard</h1>
        <p className="text-muted-foreground mt-2">
          Overview of Congressional trading activity and network analytics
        </p>
      </div>

      {/* Key metrics */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        <MetricCard
          title="Total Politicians"
          value={totalPoliticians.toLocaleString()}
          subtitle="With ≥30 trades"
          trend="+5.2%"
        />
        <MetricCard
          title="Total Trades"
          value={totalTrades.toLocaleString()}
          subtitle="All time"
          trend="+12.3%"
        />
        <MetricCard
          title="Active Last 7 Days"
          value={activePoliticians.toLocaleString()}
          subtitle="Recent traders"
          trend={`${((activePoliticians / totalPoliticians) * 100).toFixed(1)}%`}
        />
        <MetricCard
          title="Network Density"
          value={(network?.density || 0).toFixed(3)}
          subtitle="Correlation strength"
          trend={(network?.clustering_coefficient || 0).toFixed(2)}
        />
      </div>

      {/* Network overview and top traders */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Network metrics */}
        <div className="bg-card border border-border rounded-lg p-6">
          <h2 className="text-xl font-semibold mb-4">Network Analysis</h2>
          {network ? (
            <div className="space-y-4">
              <div>
                <div className="flex justify-between items-baseline mb-2">
                  <span className="text-sm text-muted-foreground">Politicians in Network</span>
                  <span className="text-2xl font-bold">{network.num_politicians}</span>
                </div>
                <div className="w-full h-2 bg-muted rounded-full overflow-hidden">
                  <div
                    className="h-full bg-primary rounded-full transition-all"
                    style={{ width: `${(network.num_politicians / totalPoliticians) * 100}%` }}
                  />
                </div>
              </div>

              <div>
                <div className="flex justify-between items-baseline mb-2">
                  <span className="text-sm text-muted-foreground">Clustering Coefficient</span>
                  <span className="text-2xl font-bold">
                    {network.clustering_coefficient.toFixed(3)}
                  </span>
                </div>
                <div className="w-full h-2 bg-muted rounded-full overflow-hidden">
                  <div
                    className="h-full bg-green-500 rounded-full transition-all"
                    style={{ width: `${network.clustering_coefficient * 100}%` }}
                  />
                </div>
              </div>

              <div>
                <div className="flex justify-between items-baseline mb-2">
                  <span className="text-sm text-muted-foreground">Avg Path Length</span>
                  <span className="text-2xl font-bold">
                    {network.average_path_length.toFixed(2)}
                  </span>
                </div>
                <p className="text-xs text-muted-foreground mt-2">
                  Average steps between any two politicians in the network
                </p>
              </div>

              <div className="pt-4">
                <Link
                  href="/network"
                  className="inline-flex items-center text-sm text-primary hover:underline"
                >
                  View Network Visualization →
                </Link>
              </div>
            </div>
          ) : (
            <p className="text-muted-foreground">No network data available</p>
          )}
        </div>

        {/* Top traders */}
        <div className="bg-card border border-border rounded-lg p-6">
          <h2 className="text-xl font-semibold mb-4">Top Traders</h2>
          <div className="space-y-3">
            {topTraders.map((pol, idx) => (
              <Link
                key={pol.id}
                href={`/politicians/${pol.id}`}
                className="flex items-center justify-between p-3 rounded-lg hover:bg-muted/50 transition-colors group"
              >
                <div className="flex items-center gap-3">
                  <div className="flex items-center justify-center w-8 h-8 rounded-full bg-primary/10 text-primary font-semibold text-sm">
                    {idx + 1}
                  </div>
                  <div>
                    <p className="font-medium group-hover:text-primary transition-colors">
                      {pol.name}
                    </p>
                    <p className="text-xs text-muted-foreground">
                      {pol.party} • {pol.state}
                    </p>
                  </div>
                </div>
                <div className="text-right">
                  <p className="font-semibold">{pol.trade_count?.toLocaleString()}</p>
                  <p className="text-xs text-muted-foreground">trades</p>
                </div>
              </Link>
            ))}
          </div>

          <div className="mt-4 pt-4 border-t border-border">
            <Link
              href="/politicians"
              className="inline-flex items-center text-sm text-primary hover:underline"
            >
              View All Politicians →
            </Link>
          </div>
        </div>
      </div>

      {/* Central politicians */}
      {network && network.central_politicians.length > 0 && (
        <div className="bg-card border border-border rounded-lg p-6">
          <h2 className="text-xl font-semibold mb-4">Most Central Politicians</h2>
          <p className="text-sm text-muted-foreground mb-4">
            Politicians with the highest network centrality scores (most interconnected)
          </p>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {network.central_politicians.slice(0, 6).map((central, idx) => (
              <Link
                key={central.politician_id}
                href={`/politicians/${central.politician_id}`}
                className="flex items-center gap-3 p-4 rounded-lg bg-muted/30 hover:bg-muted/50 transition-colors group"
              >
                <div className="flex-1">
                  <p className="font-medium group-hover:text-primary transition-colors">
                    {central.name}
                  </p>
                  <div className="mt-2">
                    <div className="flex items-center justify-between text-xs text-muted-foreground mb-1">
                      <span>Centrality</span>
                      <span className="font-medium">{central.centrality_score.toFixed(3)}</span>
                    </div>
                    <div className="w-full h-1.5 bg-muted rounded-full overflow-hidden">
                      <div
                        className="h-full bg-primary rounded-full transition-all"
                        style={{
                          width: `${(central.centrality_score / Math.max(...network.central_politicians.map(c => c.centrality_score))) * 100}%`,
                        }}
                      />
                    </div>
                  </div>
                </div>
              </Link>
            ))}
          </div>
        </div>
      )}

      {/* Quick actions */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <Link
          href="/analytics"
          className="block p-6 bg-card border border-border rounded-lg hover:border-primary/50 transition-colors group"
        >
          <h3 className="text-lg font-semibold mb-2 group-hover:text-primary transition-colors">
            Advanced Analytics
          </h3>
          <p className="text-sm text-muted-foreground">
            Ensemble predictions, correlations, and automated insights
          </p>
        </Link>

        <Link
          href="/network"
          className="block p-6 bg-card border border-border rounded-lg hover:border-primary/50 transition-colors group"
        >
          <h3 className="text-lg font-semibold mb-2 group-hover:text-primary transition-colors">
            Network Visualization
          </h3>
          <p className="text-sm text-muted-foreground">
            Interactive network graph showing politician trading correlations
          </p>
        </Link>

        <Link
          href="/politicians"
          className="block p-6 bg-card border border-border rounded-lg hover:border-primary/50 transition-colors group"
        >
          <h3 className="text-lg font-semibold mb-2 group-hover:text-primary transition-colors">
            Browse Politicians
          </h3>
          <p className="text-sm text-muted-foreground">
            Search and filter politicians by party, state, and trading activity
          </p>
        </Link>
      </div>
    </div>
  )
}

interface MetricCardProps {
  title: string
  value: string
  subtitle: string
  trend?: string
}

function MetricCard({ title, value, subtitle, trend }: MetricCardProps) {
  return (
    <div className="bg-card border border-border rounded-lg p-6">
      <p className="text-sm text-muted-foreground mb-2">{title}</p>
      <p className="text-3xl font-bold mb-1">{value}</p>
      <div className="flex items-center justify-between">
        <p className="text-xs text-muted-foreground">{subtitle}</p>
        {trend && (
          <span className="text-xs text-green-500 font-medium">{trend}</span>
        )}
      </div>
    </div>
  )
}
