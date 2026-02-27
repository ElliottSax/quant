/**
 * Backtest Results History Page
 * View, sort, filter, and compare past backtest results
 */

'use client'

import { useState, useEffect } from 'react'
import Link from 'next/link'
import { getBacktestResults, deleteBacktestResult, type BacktestResultRecord } from '@/lib/backtest-storage'

type SortKey = 'createdAt' | 'totalReturn' | 'sharpeRatio' | 'winRate'

export default function BacktestResultsPage() {
  const [results, setResults] = useState<BacktestResultRecord[]>([])
  const [sortBy, setSortBy] = useState<SortKey>('createdAt')
  const [filterStrategy, setFilterStrategy] = useState('')
  const [compareIds, setCompareIds] = useState<Set<string>>(new Set())

  useEffect(() => {
    setResults(getBacktestResults())
  }, [])

  const toggleCompare = (id: string) => {
    setCompareIds(prev => {
      const next = new Set(prev)
      if (next.has(id)) next.delete(id)
      else if (next.size < 4) next.add(id)
      return next
    })
  }

  const handleDelete = (id: string) => {
    deleteBacktestResult(id)
    setResults(getBacktestResults())
    setCompareIds(prev => { const n = new Set(prev); n.delete(id); return n })
  }

  const strategies = Array.from(new Set(results.map(r => r.strategyLabel)))

  const filteredResults = results
    .filter(r => !filterStrategy || r.strategyLabel === filterStrategy)
    .sort((a, b) => {
      switch (sortBy) {
        case 'totalReturn': return b.totalReturn - a.totalReturn
        case 'sharpeRatio': return b.sharpeRatio - a.sharpeRatio
        case 'winRate': return b.winRate - a.winRate
        default: return new Date(b.createdAt).getTime() - new Date(a.createdAt).getTime()
      }
    })

  return (
    <div className="space-y-8">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-4xl font-bold mb-2 gradient-text">Backtest History</h1>
          <p className="text-muted-foreground text-lg">{results.length} saved results</p>
        </div>
        <div className="flex gap-3">
          <Link href="/backtesting" className="px-4 py-2 text-sm font-medium rounded-lg bg-blue-600 text-white hover:bg-blue-500 transition-colors">
            Run New Backtest
          </Link>
          {compareIds.size >= 2 && (
            <Link
              href={`/backtesting/compare?ids=${Array.from(compareIds).join(',')}`}
              className="px-4 py-2 text-sm font-medium rounded-lg bg-purple-600 text-white hover:bg-purple-500 transition-colors"
            >
              Compare ({compareIds.size})
            </Link>
          )}
        </div>
      </div>

      {results.length === 0 ? (
        <div className="glass-strong rounded-xl p-16 text-center">
          <div className="text-6xl mb-4">📊</div>
          <h3 className="text-2xl font-bold mb-2">No Backtests Yet</h3>
          <p className="text-muted-foreground mb-6">Run your first backtest to see results here.</p>
          <div className="flex gap-4 justify-center">
            <Link href="/backtesting" className="px-6 py-3 rounded-lg bg-blue-600 text-white hover:bg-blue-500 transition-colors">
              Run Backtest
            </Link>
            <Link href="/strategies" className="px-6 py-3 rounded-lg bg-slate-800 text-slate-300 hover:text-white hover:bg-slate-700 transition-colors">
              Browse Strategies
            </Link>
          </div>
        </div>
      ) : (
        <>
          {/* Controls */}
          <div className="flex flex-wrap gap-4">
            <div className="flex items-center gap-2">
              <span className="text-xs text-muted-foreground">Sort:</span>
              {([['createdAt', 'Date'], ['totalReturn', 'Return'], ['sharpeRatio', 'Sharpe'], ['winRate', 'Win Rate']] as [SortKey, string][]).map(([key, label]) => (
                <button
                  key={key}
                  onClick={() => setSortBy(key)}
                  className={`px-3 py-1 text-xs rounded ${sortBy === key ? 'bg-blue-600 text-white' : 'bg-slate-800 text-slate-400 hover:text-white'}`}
                >
                  {label}
                </button>
              ))}
            </div>
            {strategies.length > 1 && (
              <div className="flex items-center gap-2">
                <span className="text-xs text-muted-foreground">Filter:</span>
                <select
                  value={filterStrategy}
                  onChange={(e) => setFilterStrategy(e.target.value)}
                  className="input-field text-xs py-1 px-2"
                >
                  <option value="">All Strategies</option>
                  {strategies.map(s => <option key={s} value={s}>{s}</option>)}
                </select>
              </div>
            )}
            {compareIds.size > 0 && (
              <button onClick={() => setCompareIds(new Set())} className="text-xs text-muted-foreground hover:text-white">
                Clear selection
              </button>
            )}
          </div>

          {/* Results Table */}
          <div className="glass-strong rounded-xl overflow-hidden">
            <table className="w-full">
              <thead>
                <tr className="border-b border-slate-700">
                  <th className="px-4 py-3 text-left text-xs font-semibold text-muted-foreground w-10">
                    <span className="sr-only">Compare</span>
                  </th>
                  <th className="px-4 py-3 text-left text-xs font-semibold text-muted-foreground">Strategy</th>
                  <th className="px-4 py-3 text-left text-xs font-semibold text-muted-foreground">Symbol</th>
                  <th className="px-4 py-3 text-right text-xs font-semibold text-muted-foreground">Return</th>
                  <th className="px-4 py-3 text-right text-xs font-semibold text-muted-foreground">Sharpe</th>
                  <th className="px-4 py-3 text-right text-xs font-semibold text-muted-foreground">Win Rate</th>
                  <th className="px-4 py-3 text-right text-xs font-semibold text-muted-foreground">Drawdown</th>
                  <th className="px-4 py-3 text-left text-xs font-semibold text-muted-foreground">Date Range</th>
                  <th className="px-4 py-3 text-right text-xs font-semibold text-muted-foreground">Saved</th>
                  <th className="px-4 py-3 w-10"></th>
                </tr>
              </thead>
              <tbody>
                {filteredResults.map((r) => (
                  <tr key={r.id} className="border-b border-slate-800 hover:bg-slate-800/30 transition-colors">
                    <td className="px-4 py-3">
                      <input
                        type="checkbox"
                        checked={compareIds.has(r.id)}
                        onChange={() => toggleCompare(r.id)}
                        className="rounded border-slate-600"
                        disabled={!compareIds.has(r.id) && compareIds.size >= 4}
                      />
                    </td>
                    <td className="px-4 py-3">
                      <Link href={`/backtesting/results/${r.id}`} className="text-sm font-medium text-white hover:text-blue-400 transition-colors">
                        {r.strategyLabel}
                      </Link>
                    </td>
                    <td className="px-4 py-3 font-mono text-sm text-slate-300">{r.symbol}</td>
                    <td className={`px-4 py-3 text-right text-sm font-bold ${r.totalReturn >= 0 ? 'text-green-400' : 'text-red-400'}`}>
                      {r.totalReturn >= 0 ? '+' : ''}{r.totalReturn.toFixed(2)}%
                    </td>
                    <td className="px-4 py-3 text-right text-sm font-bold text-blue-400">{r.sharpeRatio.toFixed(2)}</td>
                    <td className="px-4 py-3 text-right text-sm text-purple-400">{r.winRate.toFixed(1)}%</td>
                    <td className="px-4 py-3 text-right text-sm text-red-400">{r.maxDrawdown.toFixed(1)}%</td>
                    <td className="px-4 py-3 text-sm text-muted-foreground">
                      {r.startDate} → {r.endDate}
                    </td>
                    <td className="px-4 py-3 text-right text-xs text-muted-foreground">
                      {new Date(r.createdAt).toLocaleDateString()}
                    </td>
                    <td className="px-4 py-3">
                      <button onClick={() => handleDelete(r.id)} className="text-xs text-red-400/50 hover:text-red-400" title="Delete">
                        ×
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </>
      )}
    </div>
  )
}
