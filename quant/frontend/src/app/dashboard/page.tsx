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
          <div className="relative">
            <div className="inline-block h-16 w-16 animate-spin rounded-full border-4 border-solid border-primary/20 border-t-primary" />
            <div className="absolute inset-0 h-16 w-16 rounded-full bg-primary/10 blur-xl animate-pulse" />
          </div>
          <p className="mt-6 text-lg font-medium text-muted-foreground animate-pulse">Loading dashboard...</p>
          <p className="mt-2 text-sm text-muted-foreground/60">Fetching latest data</p>
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
      <div className="animate-fade-in">
        <h1 className="text-4xl md:text-5xl font-bold mb-3 bg-clip-text text-transparent bg-gradient-to-r from-foreground to-foreground/70">
          Dashboard
        </h1>
        <p className="text-lg text-muted-foreground">
          Overview of Congressional trading activity and network analytics
        </p>
      </div>

      {/* Key metrics */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 md:gap-6">
        <MetricCard
          title="Total Politicians"
          value={totalPoliticians.toLocaleString()}
          subtitle="With ≥30 trades"
          trend="+5.2%"
          gradient="from-blue-500 to-cyan-500"
          delay={0}
        />
        <MetricCard
          title="Total Trades"
          value={totalTrades.toLocaleString()}
          subtitle="All time"
          trend="+12.3%"
          gradient="from-purple-500 to-pink-500"
          delay={100}
        />
        <MetricCard
          title="Active Last 7 Days"
          value={activePoliticians.toLocaleString()}
          subtitle="Recent traders"
          trend={`${((activePoliticians / totalPoliticians) * 100).toFixed(1)}%`}
          gradient="from-green-500 to-emerald-500"
          delay={200}
        />
        <MetricCard
          title="Network Density"
          value={(network?.density || 0).toFixed(3)}
          subtitle="Correlation strength"
          trend={(network?.clustering_coefficient || 0).toFixed(2)}
          gradient="from-orange-500 to-red-500"
          delay={300}
        />
      </div>

      {/* Network overview and top traders */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 animate-fade-in" style={{ animationDelay: '400ms', animationFillMode: 'backwards' }}>
        {/* Network metrics */}
        <div className="bg-card border border-border rounded-xl p-6 hover:shadow-xl hover:border-primary/30 transition-all duration-300 group">
          <div className="flex items-center justify-between mb-6">
            <h2 className="text-xl font-semibold">Network Analysis</h2>
            <div className="w-10 h-10 rounded-lg bg-gradient-to-br from-blue-500 to-cyan-500 flex items-center justify-center group-hover:scale-110 transition-transform">
              <svg className="w-5 h-5 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 20l-5.447-2.724A1 1 0 013 16.382V5.618a1 1 0 011.447-.894L9 7m0 13l6-3m-6 3V7m6 10l4.553 2.276A1 1 0 0021 18.382V7.618a1 1 0 00-.553-.894L15 4m0 13V4m0 0L9 7" />
              </svg>
            </div>
          </div>
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
        <div className="bg-card border border-border rounded-xl p-6 hover:shadow-xl hover:border-primary/30 transition-all duration-300 group">
          <div className="flex items-center justify-between mb-6">
            <h2 className="text-xl font-semibold">Top Traders</h2>
            <div className="w-10 h-10 rounded-lg bg-gradient-to-br from-purple-500 to-pink-500 flex items-center justify-center group-hover:scale-110 transition-transform">
              <svg className="w-5 h-5 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" />
              </svg>
            </div>
          </div>
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
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4 md:gap-6">
        <Link
          href="/compare"
          className="block p-6 bg-card border border-border rounded-xl hover:border-primary/50 hover:shadow-xl hover:-translate-y-1 transition-all duration-300 group relative overflow-hidden"
        >
          <div className="absolute top-0 right-0 w-32 h-32 bg-gradient-to-br from-blue-500/10 to-cyan-500/10 rounded-full blur-2xl group-hover:scale-150 transition-transform duration-500" />
          <div className="relative">
            <div className="w-12 h-12 rounded-lg bg-gradient-to-br from-blue-500 to-cyan-500 flex items-center justify-center mb-4 group-hover:scale-110 transition-transform">
              <svg className="w-6 h-6 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
              </svg>
            </div>
            <h3 className="text-lg font-semibold mb-2 group-hover:text-primary transition-colors">
              Compare Politicians
            </h3>
            <p className="text-sm text-muted-foreground">
              Side-by-side comparison of trading performance and strategies
            </p>
            <div className="mt-4 text-primary text-sm font-medium flex items-center gap-1 opacity-0 group-hover:opacity-100 transition-opacity">
              Explore <span>→</span>
            </div>
          </div>
        </Link>

        <Link
          href="/network"
          className="block p-6 bg-card border border-border rounded-xl hover:border-primary/50 hover:shadow-xl hover:-translate-y-1 transition-all duration-300 group relative overflow-hidden"
        >
          <div className="absolute top-0 right-0 w-32 h-32 bg-gradient-to-br from-purple-500/10 to-pink-500/10 rounded-full blur-2xl group-hover:scale-150 transition-transform duration-500" />
          <div className="relative">
            <div className="w-12 h-12 rounded-lg bg-gradient-to-br from-purple-500 to-pink-500 flex items-center justify-center mb-4 group-hover:scale-110 transition-transform">
              <svg className="w-6 h-6 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 20l-5.447-2.724A1 1 0 013 16.382V5.618a1 1 0 011.447-.894L9 7m0 13l6-3m-6 3V7m6 10l4.553 2.276A1 1 0 0021 18.382V7.618a1 1 0 00-.553-.894L15 4m0 13V4m0 0L9 7" />
              </svg>
            </div>
            <h3 className="text-lg font-semibold mb-2 group-hover:text-primary transition-colors">
              Network Visualization
            </h3>
            <p className="text-sm text-muted-foreground">
              Interactive network graph showing politician trading correlations
            </p>
            <div className="mt-4 text-primary text-sm font-medium flex items-center gap-1 opacity-0 group-hover:opacity-100 transition-opacity">
              Explore <span>→</span>
            </div>
          </div>
        </Link>

        <Link
          href="/politicians"
          className="block p-6 bg-card border border-border rounded-xl hover:border-primary/50 hover:shadow-xl hover:-translate-y-1 transition-all duration-300 group relative overflow-hidden"
        >
          <div className="absolute top-0 right-0 w-32 h-32 bg-gradient-to-br from-green-500/10 to-emerald-500/10 rounded-full blur-2xl group-hover:scale-150 transition-transform duration-500" />
          <div className="relative">
            <div className="w-12 h-12 rounded-lg bg-gradient-to-br from-green-500 to-emerald-500 flex items-center justify-center mb-4 group-hover:scale-110 transition-transform">
              <svg className="w-6 h-6 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0zm6 3a2 2 0 11-4 0 2 2 0 014 0zM7 10a2 2 0 11-4 0 2 2 0 014 0z" />
              </svg>
            </div>
            <h3 className="text-lg font-semibold mb-2 group-hover:text-primary transition-colors">
              Browse Politicians
            </h3>
            <p className="text-sm text-muted-foreground">
              Search and filter politicians by party, state, and trading activity
            </p>
            <div className="mt-4 text-primary text-sm font-medium flex items-center gap-1 opacity-0 group-hover:opacity-100 transition-opacity">
              Explore <span>→</span>
            </div>
          </div>
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
  gradient?: string
  delay?: number
}

function MetricCard({ title, value, subtitle, trend, gradient, delay = 0 }: MetricCardProps) {
  return (
    <div
      className="relative group bg-card border border-border rounded-xl p-6 hover:shadow-2xl hover:-translate-y-1 hover:border-primary/50 transition-all duration-300 overflow-hidden animate-fade-in"
      style={{
        animationDelay: `${delay}ms`,
        animationFillMode: 'backwards',
      }}
    >
      {/* Gradient background on hover */}
      {gradient && (
        <div className={`absolute inset-0 bg-gradient-to-br ${gradient} opacity-0 group-hover:opacity-5 transition-opacity duration-300`} />
      )}

      {/* Content */}
      <div className="relative">
        <p className="text-sm font-medium text-muted-foreground mb-3">{title}</p>
        <p className="text-4xl font-bold mb-2 bg-clip-text text-transparent bg-gradient-to-br from-foreground to-foreground/70">
          {value}
        </p>
        <div className="flex items-center justify-between">
          <p className="text-xs text-muted-foreground">{subtitle}</p>
          {trend && (
            <span className="inline-flex items-center gap-1 text-xs font-semibold text-green-500 bg-green-500/10 px-2 py-1 rounded-full">
              <svg className="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 7h8m0 0v8m0-8l-8 8-4-4-6 6" />
              </svg>
              {trend}
            </span>
          )}
        </div>
      </div>
    </div>
  )
}
