/**
 * Politicians List Page
 * Searchable, filterable list of all politicians with trading data
 */

'use client'

import { usePoliticians } from '@/lib/hooks'
import Link from 'next/link'
import { useState, useMemo } from 'react'

export default function PoliticiansPage() {
  const { data: politicians, isLoading } = usePoliticians(10)
  const [search, setSearch] = useState('')
  const [partyFilter, setPartyFilter] = useState<string>('all')
  const [chamberFilter, setChamberFilter] = useState<string>('all')

  const filtered = useMemo(() => {
    if (!politicians) return []

    return politicians.filter(p => {
      const matchesSearch = p.name.toLowerCase().includes(search.toLowerCase()) ||
                           p.state.toLowerCase().includes(search.toLowerCase())
      const matchesParty = partyFilter === 'all' || p.party === partyFilter
      const matchesChamber = chamberFilter === 'all' || p.chamber === chamberFilter

      return matchesSearch && matchesParty && matchesChamber
    })
  }, [politicians, search, partyFilter, chamberFilter])

  const parties = Array.from(new Set(politicians?.map(p => p.party) || []))
  const chambers = Array.from(new Set(politicians?.map(p => p.chamber) || []))

  if (isLoading) {
    return (
      <div className="flex items-center justify-center min-h-[400px]">
        <div className="text-center">
          <div className="relative">
            <div className="inline-block h-16 w-16 animate-spin rounded-full border-4 border-solid border-primary/20 border-t-primary" />
            <div className="absolute inset-0 h-16 w-16 rounded-full bg-primary/10 blur-xl animate-pulse" />
          </div>
          <p className="mt-6 text-lg font-medium text-muted-foreground animate-pulse">Loading politicians...</p>
          <p className="mt-2 text-sm text-muted-foreground/60">Fetching data</p>
        </div>
      </div>
    )
  }

  return (
    <div className="space-y-8">
      {/* Header */}
      <div className="animate-fade-in">
        <h1 className="text-4xl md:text-5xl font-bold mb-3 bg-clip-text text-transparent bg-gradient-to-r from-foreground to-foreground/70">
          Politicians
        </h1>
        <p className="text-lg text-muted-foreground">
          Browse and analyze trading activity by politician
        </p>
      </div>

      {/* Filters */}
      <div className="glass-strong rounded-xl p-6 border border-border/50 animate-fade-in" style={{ animationDelay: '100ms', animationFillMode: 'backwards' }}>
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
          <div className="md:col-span-2">
            <label className="block text-sm font-semibold mb-2 text-foreground">Search</label>
            <div className="relative">
              <input
                type="text"
                value={search}
                onChange={(e) => setSearch(e.target.value)}
                placeholder="Search by name or state..."
                className="input-field pl-10"
              />
              <svg className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-muted-foreground" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
              </svg>
            </div>
          </div>

          <div>
            <label className="block text-sm font-semibold mb-2 text-foreground">Party</label>
            <select
              value={partyFilter}
              onChange={(e) => setPartyFilter(e.target.value)}
              className="input-field"
            >
              <option value="all">All Parties</option>
              {parties.map(party => (
                <option key={party} value={party}>{party}</option>
              ))}
            </select>
          </div>

          <div>
            <label className="block text-sm font-semibold mb-2 text-foreground">Chamber</label>
            <select
              value={chamberFilter}
              onChange={(e) => setChamberFilter(e.target.value)}
              className="input-field"
            >
              <option value="all">All Chambers</option>
              {chambers.map(chamber => (
                <option key={chamber} value={chamber}>{chamber}</option>
              ))}
            </select>
          </div>
        </div>

        <div className="mt-6 flex items-center justify-between pt-4 border-t border-border/50">
          <p className="text-sm font-medium">
            Showing <span className="text-primary font-bold">{filtered.length}</span> of {politicians?.length || 0} politicians
          </p>
          <button
            onClick={() => {
              setSearch('')
              setPartyFilter('all')
              setChamberFilter('all')
            }}
            className="inline-flex items-center gap-2 px-4 py-2 text-sm font-medium text-primary hover:text-primary/80 hover:bg-primary/10 rounded-lg transition-all"
          >
            <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
            </svg>
            Clear filters
          </button>
        </div>
      </div>

      {/* Politicians table */}
      <div className="bg-card border border-border rounded-xl overflow-hidden shadow-lg animate-fade-in" style={{ animationDelay: '200ms', animationFillMode: 'backwards' }}>
        <div className="overflow-x-auto scrollbar-thin">
          <table className="w-full">
            <thead className="bg-gradient-to-r from-muted/80 to-muted/40 border-b border-border">
              <tr>
                <th className="px-6 py-4 text-left text-xs font-bold uppercase tracking-wider text-foreground">
                  Name
                </th>
                <th className="px-6 py-4 text-left text-xs font-bold uppercase tracking-wider text-foreground">
                  Party
                </th>
                <th className="px-6 py-4 text-left text-xs font-bold uppercase tracking-wider text-foreground">
                  State
                </th>
                <th className="px-6 py-4 text-left text-xs font-bold uppercase tracking-wider text-foreground">
                  Chamber
                </th>
                <th className="px-6 py-4 text-right text-xs font-bold uppercase tracking-wider text-foreground">
                  Trades
                </th>
                <th className="px-6 py-4 text-right text-xs font-bold uppercase tracking-wider text-foreground">
                  Days Active
                </th>
                <th className="px-6 py-4 text-right text-xs font-bold uppercase tracking-wider text-foreground">
                  Actions
                </th>
              </tr>
            </thead>
            <tbody className="divide-y divide-border/50">
              {filtered.map((pol, idx) => (
                <tr
                  key={pol.id}
                  className="hover:bg-primary/5 transition-all duration-200 group animate-fade-in"
                  style={{ animationDelay: `${300 + idx * 30}ms`, animationFillMode: 'backwards' }}
                >
                  <td className="px-6 py-4 whitespace-nowrap">
                    <Link
                      href={`/politicians/${pol.id}`}
                      className="font-semibold text-foreground group-hover:text-primary transition-colors flex items-center gap-2"
                    >
                      {pol.name}
                      <svg className="w-4 h-4 opacity-0 group-hover:opacity-100 transition-opacity" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
                      </svg>
                    </Link>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <span className={`inline-flex items-center gap-1.5 px-3 py-1.5 text-xs font-bold rounded-full border ${
                      pol.party === 'Democratic'
                        ? 'bg-blue-500/10 text-blue-500 border-blue-500/20'
                        : pol.party === 'Republican'
                        ? 'bg-red-500/10 text-red-500 border-red-500/20'
                        : 'bg-gray-500/10 text-gray-500 border-gray-500/20'
                    }`}>
                      <span className="w-1.5 h-1.5 rounded-full bg-current"></span>
                      {pol.party}
                    </span>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm font-medium">
                    {pol.state}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm">
                    <span className="inline-flex items-center px-2.5 py-1 rounded-md bg-muted/50 text-muted-foreground font-medium">
                      {pol.chamber}
                    </span>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-right">
                    <span className="text-sm font-bold text-foreground">
                      {pol.trade_count?.toLocaleString() || 0}
                    </span>
                    <p className="text-xs text-muted-foreground">trades</p>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-right text-sm font-medium text-muted-foreground">
                    {pol.days_active || 'N/A'}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-right">
                    <Link
                      href={`/politicians/${pol.id}`}
                      className="inline-flex items-center gap-1 text-sm font-semibold text-primary hover:text-primary/80 group-hover:gap-2 transition-all"
                    >
                      View Details
                      <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 7l5 5m0 0l-5 5m5-5H6" />
                      </svg>
                    </Link>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>

        {filtered.length === 0 && (
          <div className="text-center py-16">
            <div className="inline-flex items-center justify-center w-16 h-16 rounded-full bg-muted/50 mb-4">
              <svg className="w-8 h-8 text-muted-foreground" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9.172 16.172a4 4 0 015.656 0M9 10h.01M15 10h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
            </div>
            <p className="text-lg font-medium text-muted-foreground mb-1">No politicians found</p>
            <p className="text-sm text-muted-foreground/60">Try adjusting your search filters</p>
          </div>
        )}
      </div>
    </div>
  )
}
