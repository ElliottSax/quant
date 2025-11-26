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
          <div className="inline-block h-8 w-8 animate-spin rounded-full border-4 border-solid border-current border-r-transparent" />
          <p className="mt-4 text-muted-foreground">Loading politicians...</p>
        </div>
      </div>
    )
  }

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold">Politicians</h1>
        <p className="text-muted-foreground mt-2">
          Browse and analyze trading activity by politician
        </p>
      </div>

      {/* Filters */}
      <div className="bg-card border border-border rounded-lg p-4">
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
          <div className="md:col-span-2">
            <label className="block text-sm font-medium mb-2">Search</label>
            <input
              type="text"
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              placeholder="Search by name or state..."
              className="w-full px-3 py-2 bg-background border border-border rounded-md focus:outline-none focus:ring-2 focus:ring-primary"
            />
          </div>

          <div>
            <label className="block text-sm font-medium mb-2">Party</label>
            <select
              value={partyFilter}
              onChange={(e) => setPartyFilter(e.target.value)}
              className="w-full px-3 py-2 bg-background border border-border rounded-md focus:outline-none focus:ring-2 focus:ring-primary"
            >
              <option value="all">All Parties</option>
              {parties.map(party => (
                <option key={party} value={party}>{party}</option>
              ))}
            </select>
          </div>

          <div>
            <label className="block text-sm font-medium mb-2">Chamber</label>
            <select
              value={chamberFilter}
              onChange={(e) => setChamberFilter(e.target.value)}
              className="w-full px-3 py-2 bg-background border border-border rounded-md focus:outline-none focus:ring-2 focus:ring-primary"
            >
              <option value="all">All Chambers</option>
              {chambers.map(chamber => (
                <option key={chamber} value={chamber}>{chamber}</option>
              ))}
            </select>
          </div>
        </div>

        <div className="mt-4 flex items-center justify-between text-sm text-muted-foreground">
          <p>Showing {filtered.length} of {politicians?.length || 0} politicians</p>
          <button
            onClick={() => {
              setSearch('')
              setPartyFilter('all')
              setChamberFilter('all')
            }}
            className="text-primary hover:underline"
          >
            Clear filters
          </button>
        </div>
      </div>

      {/* Politicians table */}
      <div className="bg-card border border-border rounded-lg overflow-hidden">
        <div className="overflow-x-auto">
          <table className="w-full">
            <thead className="bg-muted/50 border-b border-border">
              <tr>
                <th className="px-6 py-3 text-left text-xs font-medium uppercase tracking-wider">
                  Name
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium uppercase tracking-wider">
                  Party
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium uppercase tracking-wider">
                  State
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium uppercase tracking-wider">
                  Chamber
                </th>
                <th className="px-6 py-3 text-right text-xs font-medium uppercase tracking-wider">
                  Trades
                </th>
                <th className="px-6 py-3 text-right text-xs font-medium uppercase tracking-wider">
                  Days Active
                </th>
                <th className="px-6 py-3 text-right text-xs font-medium uppercase tracking-wider">
                  Actions
                </th>
              </tr>
            </thead>
            <tbody className="divide-y divide-border">
              {filtered.map((pol) => (
                <tr key={pol.id} className="hover:bg-muted/30 transition-colors">
                  <td className="px-6 py-4 whitespace-nowrap">
                    <Link
                      href={`/politicians/${pol.id}`}
                      className="font-medium hover:text-primary transition-colors"
                    >
                      {pol.name}
                    </Link>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <span className={`inline-flex px-2 py-1 text-xs font-semibold rounded-full ${
                      pol.party === 'Democratic'
                        ? 'bg-blue-500/10 text-blue-500'
                        : pol.party === 'Republican'
                        ? 'bg-red-500/10 text-red-500'
                        : 'bg-gray-500/10 text-gray-500'
                    }`}>
                      {pol.party}
                    </span>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm">
                    {pol.state}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm">
                    {pol.chamber}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-right text-sm font-medium">
                    {pol.trade_count?.toLocaleString() || 0}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-right text-sm">
                    {pol.days_active || 'N/A'}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-right text-sm">
                    <Link
                      href={`/politicians/${pol.id}`}
                      className="text-primary hover:underline"
                    >
                      View Details →
                    </Link>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>

        {filtered.length === 0 && (
          <div className="text-center py-12">
            <p className="text-muted-foreground">No politicians found matching your filters</p>
          </div>
        )}
      </div>
    </div>
  )
}
