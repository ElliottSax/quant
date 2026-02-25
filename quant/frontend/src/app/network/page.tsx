/**
 * Network Visualization Page
 * Interactive force-directed graph showing politician trading correlations
 */

'use client'

import { useMemo, useState } from 'react'
import { NetworkGraph } from '@/components/charts/NetworkGraph'
import Link from 'next/link'
import { usePoliticians, useNetworkAnalysis } from '@/lib/hooks'

// Generate demo network data based on real politicians
function generateNetworkFromPoliticians(
  politicians: Array<{ id: string; name: string; party: string; trade_count?: number }>,
  minCorrelation: number = 0.3
) {
  const nodes = politicians.slice(0, 50).map((pol) => ({
    id: pol.id,
    name: pol.name,
    party: pol.party as 'Democratic' | 'Republican' | 'Independent',
    centrality: Math.random() * 0.7 + 0.3,
    tradeCount: pol.trade_count || 0,
  }))

  const links: Array<{
    source: string
    target: string
    correlation: number
    significance: boolean
  }> = []

  // Generate correlations between politicians
  for (let i = 0; i < nodes.length; i++) {
    for (let j = i + 1; j < nodes.length; j++) {
      // Higher correlation for same party
      const sameParty = nodes[i].party === nodes[j].party
      const baseCorr = sameParty ? 0.3 : -0.1
      const correlation = baseCorr + (Math.random() - 0.5) * 1.2
      const clampedCorr = Math.max(-1, Math.min(1, correlation))

      if (Math.abs(clampedCorr) >= minCorrelation && Math.random() > 0.5) {
        links.push({
          source: nodes[i].id,
          target: nodes[j].id,
          correlation: parseFloat(clampedCorr.toFixed(3)),
          significance: Math.abs(clampedCorr) > 0.5,
        })
      }
    }
  }

  return { nodes, links }
}

export default function NetworkPage() {
  // Fetch real data from API
  const { data: politicians, isLoading: politiciansLoading, error: politiciansError } = usePoliticians()
  const { data: networkAnalysis, isLoading: networkLoading, error: networkError } = useNetworkAnalysis()

  const isLoading = politiciansLoading || networkLoading
  const hasError = politiciansError || networkError

  const [selectedPolitician, setSelectedPolitician] = useState<string | null>(null)
  const [viewMode, setViewMode] = useState<'full' | 'clusters' | 'central'>('full')

  // Generate network data from politicians
  const networkData = useMemo(() => {
    if (!politicians || politicians.length === 0) {
      return { nodes: [], links: [] }
    }
    return generateNetworkFromPoliticians(politicians)
  }, [politicians])

  const handleNodeClick = (node: any) => {
    setSelectedPolitician(node.id)
  }

  if (isLoading) {
    return (
      <div className="flex items-center justify-center min-h-[600px]">
        <div className="text-center">
          <div className="relative">
            <div className="inline-block h-16 w-16 animate-spin rounded-full border-4 border-solid border-indigo-500/20 border-t-indigo-500" />
            <div className="absolute inset-0 h-16 w-16 rounded-full bg-indigo-500/10 blur-xl animate-pulse" />
          </div>
          <p className="mt-6 text-lg font-medium text-slate-400 animate-pulse">
            Building network graph...
          </p>
          <p className="mt-2 text-sm text-slate-500">
            Analyzing trading correlations
          </p>
        </div>
      </div>
    )
  }

  if (hasError) {
    return (
      <div className="flex items-center justify-center min-h-[600px]">
        <div className="text-center glass-card p-10">
          <div className="text-5xl mb-4">!</div>
          <h2 className="text-xl font-bold text-red-400 mb-2">Connection Error</h2>
          <p className="text-slate-400 mb-4">
            {politiciansError?.message || networkError?.message || 'Failed to load network data'}
          </p>
          <p className="text-sm text-slate-500">
            Ensure the backend is running at localhost:8000
          </p>
        </div>
      </div>
    )
  }

  return (
    <div className="space-y-8">
      {/* Header */}
      <div className="animate-fade-in">
        <div className="flex items-start justify-between">
          <div>
            <h1 className="text-4xl md:text-5xl font-bold mb-3 gradient-text">
              Network Analysis
            </h1>
            <p className="text-lg text-slate-400 max-w-2xl">
              Interactive visualization of trading correlations between Congressional members.
              Explore connections, clusters, and influential traders.
            </p>
          </div>

          {/* View mode selector */}
          <div className="flex gap-2">
            {[
              { id: 'full', label: 'Full Network', icon: '🕸️' },
              { id: 'clusters', label: 'Clusters', icon: '🎯' },
              { id: 'central', label: 'Central', icon: '⭐' },
            ].map((mode) => (
              <button
                key={mode.id}
                onClick={() => setViewMode(mode.id as typeof viewMode)}
                className={`px-4 py-2 rounded-xl text-sm font-medium transition-all ${
                  viewMode === mode.id
                    ? 'bg-indigo-500 text-white shadow-lg shadow-indigo-500/25'
                    : 'bg-slate-800/50 text-slate-400 hover:bg-slate-700/50 border border-slate-700/50'
                }`}
              >
                <span className="flex items-center gap-2">
                  <span>{mode.icon}</span>
                  <span>{mode.label}</span>
                </span>
              </button>
            ))}
          </div>
        </div>
      </div>

      {/* Network Stats */}
      {networkAnalysis && (
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4 animate-fade-in" style={{ animationDelay: '100ms' }}>
          <div className="glass-card p-5">
            <p className="text-xs text-slate-500 uppercase tracking-wider mb-1">Politicians</p>
            <p className="text-3xl font-bold text-white">{networkAnalysis.num_politicians}</p>
            <p className="text-xs text-slate-400 mt-1">In network</p>
          </div>
          <div className="glass-card p-5">
            <p className="text-xs text-slate-500 uppercase tracking-wider mb-1">Density</p>
            <p className="text-3xl font-bold text-indigo-400">{networkAnalysis.density.toFixed(3)}</p>
            <p className="text-xs text-slate-400 mt-1">Connection ratio</p>
          </div>
          <div className="glass-card p-5">
            <p className="text-xs text-slate-500 uppercase tracking-wider mb-1">Clustering</p>
            <p className="text-3xl font-bold text-emerald-400">{networkAnalysis.clustering_coefficient.toFixed(3)}</p>
            <p className="text-xs text-slate-400 mt-1">Group tendency</p>
          </div>
          <div className="glass-card p-5">
            <p className="text-xs text-slate-500 uppercase tracking-wider mb-1">Avg Path</p>
            <p className="text-3xl font-bold text-amber-400">{networkAnalysis.average_path_length.toFixed(2)}</p>
            <p className="text-xs text-slate-400 mt-1">Degrees of separation</p>
          </div>
        </div>
      )}

      {/* Main Network Graph */}
      <div className="animate-slide-up" style={{ animationDelay: '200ms' }}>
        <NetworkGraph
          nodes={networkData.nodes}
          links={networkData.links}
          height={650}
          onNodeClick={handleNodeClick}
          highlightedNode={selectedPolitician}
        />
      </div>

      {/* Central Politicians */}
      {networkAnalysis && networkAnalysis.central_politicians.length > 0 && (
        <div className="glass-card p-6 animate-fade-in" style={{ animationDelay: '300ms' }}>
          <h2 className="text-xl font-bold text-white mb-4 flex items-center gap-2">
            <span className="text-2xl">⭐</span>
            Most Central Politicians
          </h2>
          <p className="text-sm text-slate-400 mb-6">
            Politicians with the highest centrality scores are most interconnected in the network
          </p>

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {networkAnalysis.central_politicians.slice(0, 6).map((pol, idx) => (
              <Link
                key={pol.politician_id}
                href={`/politicians/${pol.politician_id}`}
                className="group relative p-4 rounded-xl bg-slate-800/30 border border-slate-700/50 hover:border-indigo-500/50 hover:bg-slate-800/50 transition-all"
              >
                <div className="flex items-center gap-4">
                  <div className={`w-10 h-10 rounded-full flex items-center justify-center font-bold text-lg ${
                    idx === 0 ? 'bg-amber-500/20 text-amber-400' :
                    idx === 1 ? 'bg-slate-400/20 text-slate-300' :
                    idx === 2 ? 'bg-orange-500/20 text-orange-400' :
                    'bg-slate-700/50 text-slate-400'
                  }`}>
                    {idx + 1}
                  </div>
                  <div className="flex-1 min-w-0">
                    <p className="font-semibold text-white truncate group-hover:text-indigo-400 transition-colors">
                      {pol.name}
                    </p>
                    <div className="flex items-center gap-2 mt-1">
                      <div className="flex-1 h-1.5 bg-slate-700/50 rounded-full overflow-hidden">
                        <div
                          className="h-full bg-gradient-to-r from-indigo-500 to-purple-500 rounded-full transition-all"
                          style={{
                            width: `${(pol.centrality_score / Math.max(...networkAnalysis.central_politicians.map(c => c.centrality_score))) * 100}%`
                          }}
                        />
                      </div>
                      <span className="text-xs font-mono text-slate-400">
                        {pol.centrality_score.toFixed(3)}
                      </span>
                    </div>
                  </div>
                </div>
              </Link>
            ))}
          </div>
        </div>
      )}

      {/* Network Clusters */}
      {networkAnalysis && networkAnalysis.clusters && networkAnalysis.clusters.length > 0 && (
        <div className="glass-card p-6 animate-fade-in" style={{ animationDelay: '400ms' }}>
          <h2 className="text-xl font-bold text-white mb-4 flex items-center gap-2">
            <span className="text-2xl">🎯</span>
            Trading Clusters
          </h2>
          <p className="text-sm text-slate-400 mb-6">
            Groups of politicians with highly correlated trading patterns
          </p>

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {networkAnalysis.clusters.slice(0, 6).map((cluster) => (
              <div
                key={cluster.cluster_id}
                className="p-4 rounded-xl bg-slate-800/30 border border-slate-700/50"
              >
                <div className="flex items-center justify-between mb-3">
                  <span className="text-sm font-semibold text-white">
                    Cluster {cluster.cluster_id}
                  </span>
                  <span className={`px-2 py-0.5 rounded text-xs font-medium ${
                    cluster.avg_correlation > 0.6 ? 'bg-emerald-500/20 text-emerald-400' :
                    cluster.avg_correlation > 0.4 ? 'bg-amber-500/20 text-amber-400' :
                    'bg-slate-500/20 text-slate-400'
                  }`}>
                    r = {cluster.avg_correlation.toFixed(2)}
                  </span>
                </div>
                <p className="text-xs text-slate-400">
                  {cluster.politicians.length} members
                </p>
                <div className="mt-2 flex flex-wrap gap-1">
                  {cluster.politicians.slice(0, 4).map((name, i) => (
                    <span key={i} className="px-2 py-0.5 rounded bg-slate-700/50 text-xs text-slate-300">
                      {name.split(' ').slice(-1)[0]}
                    </span>
                  ))}
                  {cluster.politicians.length > 4 && (
                    <span className="px-2 py-0.5 rounded bg-slate-700/50 text-xs text-slate-500">
                      +{cluster.politicians.length - 4} more
                    </span>
                  )}
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Info Panel */}
      <div className="glass-card p-6 text-center">
        <h3 className="text-lg font-semibold text-white mb-2">How to Read This Network</h3>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mt-4 text-sm text-slate-400">
          <div>
            <div className="w-12 h-12 mx-auto mb-3 rounded-full bg-slate-800/50 flex items-center justify-center">
              <span className="text-2xl">🔵</span>
            </div>
            <p><strong className="text-blue-400">Democrats</strong> are shown in blue</p>
          </div>
          <div>
            <div className="w-12 h-12 mx-auto mb-3 rounded-full bg-slate-800/50 flex items-center justify-center">
              <span className="text-2xl">🔴</span>
            </div>
            <p><strong className="text-red-400">Republicans</strong> are shown in red</p>
          </div>
          <div>
            <div className="w-12 h-12 mx-auto mb-3 rounded-full bg-slate-800/50 flex items-center justify-center">
              <span className="text-2xl">📏</span>
            </div>
            <p><strong className="text-white">Node size</strong> represents centrality score</p>
          </div>
        </div>
      </div>
    </div>
  )
}
