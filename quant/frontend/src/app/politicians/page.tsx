/**
 * Politicians List Page - Congressional Trading Tracker
 * Connected to real backend API
 */

'use client'

import Link from 'next/link'
import { useState, useMemo } from 'react'
import { usePoliticians } from '@/lib/hooks'
import dynamic from 'next/dynamic'

const ReactECharts = dynamic(() => import('echarts-for-react'), { ssr: false })

export default function PoliticiansPage() {
  const { data: politicians, isLoading, error } = usePoliticians(1)
  const [search, setSearch] = useState('')
  const [partyFilter, setPartyFilter] = useState<string>('all')
  const [chamberFilter, setChamberFilter] = useState<string>('all')
  const [sortBy, setSortBy] = useState<'name' | 'party' | 'state'>('name')

  const filtered = useMemo(() => {
    if (!politicians) return []

    let result = politicians.filter(p => {
      const matchesSearch = p.name.toLowerCase().includes(search.toLowerCase()) ||
                           (p.state?.toLowerCase() || '').includes(search.toLowerCase())
      const matchesParty = partyFilter === 'all' ||
                          (partyFilter === 'D' && p.party === 'Democratic') ||
                          (partyFilter === 'R' && p.party === 'Republican') ||
                          (partyFilter === 'I' && p.party === 'Independent')
      const matchesChamber = chamberFilter === 'all' || p.chamber?.toLowerCase() === chamberFilter.toLowerCase()
      return matchesSearch && matchesParty && matchesChamber
    })

    // Sort
    result.sort((a, b) => {
      if (sortBy === 'name') return a.name.localeCompare(b.name)
      if (sortBy === 'party') return (a.party || '').localeCompare(b.party || '')
      if (sortBy === 'state') return (a.state || '').localeCompare(b.state || '')
      return 0
    })

    return result
  }, [politicians, search, partyFilter, chamberFilter, sortBy])

  // Party distribution chart
  const partyChartOptions = useMemo(() => {
    if (!politicians) return {}

    const dems = politicians.filter(p => p.party === 'Democratic').length
    const reps = politicians.filter(p => p.party === 'Republican').length
    const ind = politicians.filter(p => p.party === 'Independent').length

    return {
      backgroundColor: 'transparent',
      tooltip: {
        trigger: 'item',
        backgroundColor: 'hsl(220, 55%, 8%)',
        borderColor: 'hsl(215, 40%, 20%)',
        textStyle: { color: '#fff', fontFamily: 'monospace', fontSize: 11 },
      },
      series: [{
        type: 'pie',
        radius: ['45%', '70%'],
        center: ['50%', '50%'],
        avoidLabelOverlap: true,
        itemStyle: { borderRadius: 4, borderColor: 'hsl(220, 60%, 4%)', borderWidth: 2 },
        label: { show: false },
        emphasis: {
          label: { show: true, fontSize: 12, fontWeight: 'bold', color: '#fff' },
        },
        data: [
          { value: dems, name: 'Democratic', itemStyle: { color: 'hsl(210, 100%, 56%)' } },
          { value: reps, name: 'Republican', itemStyle: { color: 'hsl(0, 72%, 55%)' } },
          { value: ind, name: 'Independent', itemStyle: { color: 'hsl(215, 20%, 55%)' } },
        ].filter(d => d.value > 0),
      }],
    }
  }, [politicians])

  // Chamber distribution chart
  const chamberChartOptions = useMemo(() => {
    if (!politicians) return {}

    const house = politicians.filter(p => p.chamber === 'house').length
    const senate = politicians.filter(p => p.chamber === 'senate').length

    return {
      backgroundColor: 'transparent',
      tooltip: {
        trigger: 'item',
        backgroundColor: 'hsl(220, 55%, 8%)',
        borderColor: 'hsl(215, 40%, 20%)',
        textStyle: { color: '#fff', fontFamily: 'monospace', fontSize: 11 },
      },
      series: [{
        type: 'pie',
        radius: ['45%', '70%'],
        center: ['50%', '50%'],
        itemStyle: { borderRadius: 4, borderColor: 'hsl(220, 60%, 4%)', borderWidth: 2 },
        label: { show: false },
        emphasis: {
          label: { show: true, fontSize: 12, fontWeight: 'bold', color: '#fff' },
        },
        data: [
          { value: house, name: 'House', itemStyle: { color: 'hsl(45, 96%, 58%)' } },
          { value: senate, name: 'Senate', itemStyle: { color: 'hsl(142, 71%, 55%)' } },
        ],
      }],
    }
  }, [politicians])

  if (isLoading) {
    return (
      <div className="flex items-center justify-center min-h-[400px]">
        <div className="text-center">
          <div className="inline-block h-12 w-12 animate-spin rounded-full border-2 border-[hsl(215,40%,20%)] border-t-[hsl(45,96%,58%)]" />
          <p className="mt-4 text-sm font-mono text-[hsl(215,20%,55%)]">LOADING POLITICIANS...</p>
        </div>
      </div>
    )
  }

  if (error) {
    return (
      <div className="flex items-center justify-center min-h-[400px]">
        <div className="text-center">
          <p className="text-[hsl(0,72%,55%)] font-mono">ERROR LOADING DATA</p>
          <p className="text-sm text-[hsl(215,20%,55%)] mt-2">{error.message}</p>
          <p className="text-xs text-[hsl(215,20%,45%)] mt-4">Make sure the backend is running at localhost:8000</p>
        </div>
      </div>
    )
  }

  const totalPoliticians = politicians?.length || 0
  const democrats = politicians?.filter(p => p.party === 'Democratic').length || 0
  const republicans = politicians?.filter(p => p.party === 'Republican').length || 0

  return (
    <div className="space-y-4">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-xl font-bold text-[hsl(45,96%,58%)] uppercase tracking-wider">
            Congressional Traders
          </h1>
          <p className="text-xs text-[hsl(215,20%,55%)] font-mono">
            {totalPoliticians} Politicians Tracked
          </p>
        </div>
        <div className="flex items-center gap-2">
          <span className="px-2 py-1 rounded bg-[hsl(210,100%,56%)]/10 border border-[hsl(210,100%,56%)]/30 text-[hsl(210,100%,56%)] text-xs font-mono">
            D: {democrats}
          </span>
          <span className="px-2 py-1 rounded bg-[hsl(0,72%,55%)]/10 border border-[hsl(0,72%,55%)]/30 text-[hsl(0,72%,55%)] text-xs font-mono">
            R: {republicans}
          </span>
        </div>
      </div>

      {/* Stats Row */}
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-3">
        <div className="terminal-panel p-3">
          <span className="text-[10px] text-[hsl(45,96%,58%)] font-semibold">TOTAL TRACKED</span>
          <p className="text-2xl font-bold font-mono text-white">{totalPoliticians}</p>
        </div>
        <div className="terminal-panel p-3">
          <span className="text-[10px] text-[hsl(210,100%,56%)] font-semibold">HOUSE</span>
          <p className="text-2xl font-bold font-mono text-white">
            {politicians?.filter(p => p.chamber === 'house').length || 0}
          </p>
        </div>
        <div className="terminal-panel p-3">
          <span className="text-[10px] text-[hsl(142,71%,55%)] font-semibold">SENATE</span>
          <p className="text-2xl font-bold font-mono text-white">
            {politicians?.filter(p => p.chamber === 'senate').length || 0}
          </p>
        </div>
        <div className="terminal-panel p-3">
          <span className="text-[10px] text-[hsl(270,70%,60%)] font-semibold">DATA SOURCE</span>
          <p className="text-sm font-mono text-[hsl(142,71%,55%)]">LIVE API</p>
        </div>
      </div>

      {/* Charts Row */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-3">
        <div className="terminal-panel">
          <div className="terminal-panel-header">
            <span>Party Distribution</span>
          </div>
          <div className="p-3 bg-[hsl(220,60%,4%)]">
            <div className="h-[180px]">
              <ReactECharts option={partyChartOptions} style={{ height: '100%', width: '100%' }} />
            </div>
            <div className="flex justify-center gap-4 mt-2 pt-2 border-t border-[hsl(215,40%,14%)]">
              <span className="flex items-center gap-1.5 text-xs font-mono">
                <span className="w-2 h-2 rounded-sm bg-[hsl(210,100%,56%)]"></span>
                <span className="text-[hsl(215,20%,70%)]">DEM</span>
              </span>
              <span className="flex items-center gap-1.5 text-xs font-mono">
                <span className="w-2 h-2 rounded-sm bg-[hsl(0,72%,55%)]"></span>
                <span className="text-[hsl(215,20%,70%)]">REP</span>
              </span>
              <span className="flex items-center gap-1.5 text-xs font-mono">
                <span className="w-2 h-2 rounded-sm bg-[hsl(215,20%,55%)]"></span>
                <span className="text-[hsl(215,20%,70%)]">IND</span>
              </span>
            </div>
          </div>
        </div>
        <div className="terminal-panel">
          <div className="terminal-panel-header">
            <span>Chamber Distribution</span>
          </div>
          <div className="p-3 bg-[hsl(220,60%,4%)]">
            <div className="h-[180px]">
              <ReactECharts option={chamberChartOptions} style={{ height: '100%', width: '100%' }} />
            </div>
            <div className="flex justify-center gap-4 mt-2 pt-2 border-t border-[hsl(215,40%,14%)]">
              <span className="flex items-center gap-1.5 text-xs font-mono">
                <span className="w-2 h-2 rounded-sm bg-[hsl(45,96%,58%)]"></span>
                <span className="text-[hsl(215,20%,70%)]">HOUSE</span>
              </span>
              <span className="flex items-center gap-1.5 text-xs font-mono">
                <span className="w-2 h-2 rounded-sm bg-[hsl(142,71%,55%)]"></span>
                <span className="text-[hsl(215,20%,70%)]">SENATE</span>
              </span>
            </div>
          </div>
        </div>
      </div>

      {/* Filters */}
      <div className="terminal-panel">
        <div className="terminal-panel-header">
          <span>Filters & Search</span>
        </div>
        <div className="p-3 bg-[hsl(220,60%,4%)]">
          <div className="flex flex-wrap gap-3">
            <input
              type="text"
              placeholder="Search by name or state..."
              value={search}
              onChange={e => setSearch(e.target.value)}
              className="flex-1 min-w-[200px] px-3 py-2 rounded bg-[hsl(215,50%,10%)] border border-[hsl(215,40%,18%)] text-white text-sm font-mono placeholder-[hsl(215,20%,40%)] focus:border-[hsl(45,96%,58%)] focus:outline-none"
            />
            <select
              value={partyFilter}
              onChange={e => setPartyFilter(e.target.value)}
              className="px-3 py-2 rounded bg-[hsl(215,50%,10%)] border border-[hsl(215,40%,18%)] text-white text-sm font-mono focus:border-[hsl(45,96%,58%)] focus:outline-none"
            >
              <option value="all">All Parties</option>
              <option value="D">Democratic</option>
              <option value="R">Republican</option>
              <option value="I">Independent</option>
            </select>
            <select
              value={chamberFilter}
              onChange={e => setChamberFilter(e.target.value)}
              className="px-3 py-2 rounded bg-[hsl(215,50%,10%)] border border-[hsl(215,40%,18%)] text-white text-sm font-mono focus:border-[hsl(45,96%,58%)] focus:outline-none"
            >
              <option value="all">All Chambers</option>
              <option value="house">House</option>
              <option value="senate">Senate</option>
            </select>
            <select
              value={sortBy}
              onChange={e => setSortBy(e.target.value as any)}
              className="px-3 py-2 rounded bg-[hsl(215,50%,10%)] border border-[hsl(215,40%,18%)] text-white text-sm font-mono focus:border-[hsl(45,96%,58%)] focus:outline-none"
            >
              <option value="name">Sort by Name</option>
              <option value="party">Sort by Party</option>
              <option value="state">Sort by State</option>
            </select>
          </div>
        </div>
      </div>

      {/* Politicians Table */}
      <div className="terminal-panel">
        <div className="terminal-panel-header">
          <span>Politicians ({filtered.length})</span>
        </div>
        <div className="bg-[hsl(220,60%,4%)] overflow-x-auto">
          <table className="w-full text-xs font-mono">
            <thead>
              <tr className="bg-[hsl(215,50%,10%)]">
                <th className="px-4 py-3 text-left text-[10px] text-[hsl(45,96%,58%)] font-semibold uppercase">Name</th>
                <th className="px-4 py-3 text-left text-[10px] text-[hsl(45,96%,58%)] font-semibold uppercase">Party</th>
                <th className="px-4 py-3 text-left text-[10px] text-[hsl(45,96%,58%)] font-semibold uppercase">Chamber</th>
                <th className="px-4 py-3 text-left text-[10px] text-[hsl(45,96%,58%)] font-semibold uppercase">State</th>
                <th className="px-4 py-3 text-right text-[10px] text-[hsl(45,96%,58%)] font-semibold uppercase">Actions</th>
              </tr>
            </thead>
            <tbody>
              {filtered.map((pol, idx) => (
                <tr
                  key={pol.id}
                  className={`border-b border-[hsl(215,40%,12%)] hover:bg-[hsl(215,50%,12%)] transition-colors ${
                    idx % 2 === 0 ? 'bg-[hsl(220,55%,5%)]' : ''
                  }`}
                >
                  <td className="px-4 py-3">
                    <Link
                      href={`/charts?symbol=AAPL`}
                      className="text-white hover:text-[hsl(45,96%,58%)] transition-colors font-medium"
                    >
                      {pol.name}
                    </Link>
                  </td>
                  <td className="px-4 py-3">
                    <span className={`px-2 py-0.5 rounded text-[10px] font-bold ${
                      pol.party === 'Democratic'
                        ? 'bg-[hsl(210,100%,56%)]/20 text-[hsl(210,100%,56%)]'
                        : pol.party === 'Republican'
                        ? 'bg-[hsl(0,72%,55%)]/20 text-[hsl(0,72%,55%)]'
                        : 'bg-[hsl(215,20%,55%)]/20 text-[hsl(215,20%,55%)]'
                    }`}>
                      {pol.party?.charAt(0) || '?'}
                    </span>
                  </td>
                  <td className="px-4 py-3">
                    <span className={`text-[10px] uppercase ${
                      pol.chamber === 'house' ? 'text-[hsl(45,96%,58%)]' : 'text-[hsl(142,71%,55%)]'
                    }`}>
                      {pol.chamber}
                    </span>
                  </td>
                  <td className="px-4 py-3 text-[hsl(215,20%,70%)]">{pol.state || '-'}</td>
                  <td className="px-4 py-3 text-right">
                    <Link
                      href={`/charts?politician=${pol.id}`}
                      className="px-2 py-1 rounded bg-[hsl(210,100%,56%)]/10 border border-[hsl(210,100%,56%)]/30 text-[hsl(210,100%,56%)] text-[10px] hover:bg-[hsl(210,100%,56%)]/20 transition-colors"
                    >
                      VIEW TRADES
                    </Link>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>

          {filtered.length === 0 && (
            <div className="p-8 text-center">
              <p className="text-[hsl(215,20%,55%)] font-mono">No politicians match your filters</p>
            </div>
          )}
        </div>
      </div>
    </div>
  )
}
