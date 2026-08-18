/**
 * Network Visualization Page
 * Force-directed graph of congressional trading correlations — measured edges only.
 *
 * Every node position, centrality score and correlation edge on this page was
 * previously invented: the politician list was fetched for real, then run through a
 * generator that assigned each member a random centrality and drew an edge between
 * any two members whose randomly-drawn correlation cleared a threshold. The graph
 * looked like an analysis and was noise, redrawn differently on every visit.
 *
 * The graph now renders only what the network-analysis API returns. When that
 * analysis is unavailable the page says so and draws nothing. A generated graph
 * must never be reintroduced as a fallback: an absent network is honest, an
 * invented one asserts relationships between named people that no one measured.
 */

'use client'

import { useMemo, useState } from 'react'
import { NetworkGraph } from '@/components/charts/NetworkGraph'
import Link from 'next/link'
import { useNetworkAnalysis } from '@/lib/hooks'

interface GraphNode {
  id: string
  name: string
  party: string
  centrality: number
  tradeCount?: number
}

interface GraphLink {
  source: string
  target: string
  correlation: number
  significance: boolean
}

interface GraphCluster {
  cluster_id: string | number
  avg_correlation: number
  politicians: string[]
}

const isRecord = (v: unknown): v is Record<string, unknown> =>
  typeof v === 'object' && v !== null

/**
 * Normalisers, not repairers. An entry missing a measured field is dropped rather
 * than completed with a default, because a defaulted centrality or correlation is
 * a fabricated one.
 */
function toNodes(raw: unknown[]): GraphNode[] {
  return raw.filter(isRecord).reduce<GraphNode[]>((acc, n) => {
    if (typeof n.id !== 'string' || typeof n.centrality !== 'number') return acc
    acc.push({
      id: n.id,
      name: typeof n.name === 'string' ? n.name : n.id,
      party: typeof n.party === 'string' ? n.party : 'Independent',
      centrality: n.centrality,
      tradeCount: typeof n.tradeCount === 'number' ? n.tradeCount : undefined,
    })
    return acc
  }, [])
}

function toLinks(raw: unknown[]): GraphLink[] {
  return raw.filter(isRecord).reduce<GraphLink[]>((acc, l) => {
    if (typeof l.source !== 'string' || typeof l.target !== 'string') return acc
    if (typeof l.correlation !== 'number') return acc
    acc.push({
      source: l.source,
      target: l.target,
      correlation: l.correlation,
      significance: l.significance === true,
    })
    return acc
  }, [])
}

function toClusters(raw: unknown[]): GraphCluster[] {
  return raw.filter(isRecord).reduce<GraphCluster[]>((acc, c) => {
    if (typeof c.avg_correlation !== 'number') return acc
    if (!Array.isArray(c.politicians)) return acc
    acc.push({
      cluster_id: (c.cluster_id as string | number) ?? acc.length + 1,
      avg_correlation: c.avg_correlation,
      politicians: c.politicians.filter((p): p is string => typeof p === 'string'),
    })
    return acc
  }, [])
}

export default function NetworkPage() {
  const { data: networkAnalysis, isLoading, error } = useNetworkAnalysis()

  const [selectedPolitician, setSelectedPolitician] = useState<string | null>(null)
  const [viewMode, setViewMode] = useState<'full' | 'clusters' | 'central'>('full')

  const nodes = useMemo(() => toNodes(networkAnalysis?.nodes ?? []), [networkAnalysis])
  const links = useMemo(() => toLinks(networkAnalysis?.links ?? []), [networkAnalysis])
  const clusters = useMemo(() => toClusters(networkAnalysis?.clusters ?? []), [networkAnalysis])
  const centralPoliticians = networkAnalysis?.central_politicians ?? []

  const hasGraph = nodes.length > 0
  const hasStats = (networkAnalysis?.num_politicians ?? 0) > 0

  const handleNodeClick = (node: { id: string }) => {
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
            Loading correlation analysis...
          </p>
        </div>
      </div>
    )
  }

  if (error) {
    return (
      <div className="flex items-center justify-center min-h-[600px]">
        <div className="text-center glass-card p-10 max-w-lg">
          <div className="text-5xl mb-4">!</div>
          <h2 className="text-xl font-bold text-red-400 mb-2">This analysis did not load</h2>
          <p className="text-slate-400 mb-4">
            {error.message || 'The network analysis service could not be reached.'}
          </p>
          <p className="text-sm text-slate-500">
            No graph is shown because none was produced. This page will never draw a
            simulated network in place of a failed request.
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
          {hasGraph && (
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
          )}
        </div>
      </div>

      {/* Network Stats — shown only when the analysis actually covered a population.
          Zeroed metrics from an empty response are not a result. */}
      {hasStats && networkAnalysis && (
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
        {hasGraph ? (
          <NetworkGraph
            nodes={nodes}
            links={links}
            height={650}
            onNodeClick={handleNodeClick}
            highlightedNode={selectedPolitician}
          />
        ) : (
          <div className="glass-card p-12 text-center">
            <h2 className="text-xl font-bold text-white mb-3">
              The correlation graph is not available yet
            </h2>
            <p className="text-slate-400 max-w-2xl mx-auto mb-3">
              No measured correlations were returned for the current filing set, so there
              is nothing to plot. This page previously filled that gap with a randomly
              generated graph — connections between named members of Congress that had
              never been computed. It no longer does.
            </p>
            <p className="text-sm text-slate-500 max-w-2xl mx-auto mb-8">
              Edges will reappear here when the pairwise correlation analysis runs over the
              disclosed transactions, and only for pairs that clear its significance test.
            </p>
            <div className="flex flex-wrap gap-3 justify-center">
              <Link
                href="/congress-stock-trades"
                className="px-5 py-3 rounded-xl bg-indigo-500 text-white hover:bg-indigo-400 transition-colors"
              >
                Congressional trade filings (real data)
              </Link>
              <Link
                href="/politicians"
                className="px-5 py-3 rounded-xl bg-slate-800/50 text-slate-300 hover:bg-slate-700/50 border border-slate-700/50 transition-colors"
              >
                Browse politicians
              </Link>
            </div>
          </div>
        )}
      </div>

      {/* Central Politicians */}
      {centralPoliticians.length > 0 && (
        <div className="glass-card p-6 animate-fade-in" style={{ animationDelay: '300ms' }}>
          <h2 className="text-xl font-bold text-white mb-4 flex items-center gap-2">
            <span className="text-2xl">⭐</span>
            Most Central Politicians
          </h2>
          <p className="text-sm text-slate-400 mb-6">
            Politicians with the highest centrality scores are most interconnected in the network
          </p>

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {centralPoliticians.slice(0, 6).map((pol, idx) => (
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
                            width: `${(pol.centrality_score / Math.max(...centralPoliticians.map(c => c.centrality_score))) * 100}%`
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
      {clusters.length > 0 && (
        <div className="glass-card p-6 animate-fade-in" style={{ animationDelay: '400ms' }}>
          <h2 className="text-xl font-bold text-white mb-4 flex items-center gap-2">
            <span className="text-2xl">🎯</span>
            Trading Clusters
          </h2>
          <p className="text-sm text-slate-400 mb-6">
            Groups of politicians with highly correlated trading patterns
          </p>

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {clusters.slice(0, 6).map((cluster) => (
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
      {hasGraph && (
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
      )}
    </div>
  )
}
