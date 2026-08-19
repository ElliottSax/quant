/**
 * Backtest Result Detail Page
 * Full visualization of a saved backtest result
 *
 * Everything on this page is re-derived from the curves the run actually returned and
 * stored. Nothing is filled in: a saved record with no usable equity curve says so, and a
 * record with no completed trades reports that rather than showing zeroed statistics.
 */

'use client'

import { useState, useEffect } from 'react'
import { useParams, useRouter } from 'next/navigation'
import Link from 'next/link'
import { getBacktestResult, deleteBacktestResult, type BacktestResultRecord } from '@/lib/backtest-storage'
import { BacktestResultView } from '@/components/backtesting'
import { BacktestDataNotes, NoTradesPanel } from '@/components/BacktestDataNotes'
import { normalizeBacktest, type NormalizedBacktest } from '@/lib/backtest-normalize'

const isRecord = (v: unknown): v is Record<string, unknown> =>
  typeof v === 'object' && v !== null

const num = (v: unknown): number | null =>
  typeof v === 'number' && Number.isFinite(v) ? v : null

const text = (v: unknown, fallback: string): string =>
  typeof v === 'string' && v.length > 0 ? v : fallback

function normalizeRecord(record: BacktestResultRecord): NormalizedBacktest | null {
  const result = isRecord(record.result) ? record.result : {}
  // Older records were written before the capital was stored alongside them; without it
  // no percentage is computable, and one invented from a default would be arbitrary.
  const initialCapital = num(record.initialCapital) ?? num(result.initial_capital)
  if (initialCapital === null || initialCapital <= 0) return null

  const normalized = normalizeBacktest(
    result.equity_curve,
    result.drawdown_curve,
    result.trades,
    initialCapital
  )
  return normalized.points.length > 0 ? normalized : null
}

export default function BacktestResultDetailPage() {
  const params = useParams()
  const router = useRouter()
  const [record, setRecord] = useState<BacktestResultRecord | null>(null)
  const [notFound, setNotFound] = useState(false)

  useEffect(() => {
    const id = params.id as string
    const found = getBacktestResult(id)
    if (found) setRecord(found)
    else setNotFound(true)
  }, [params.id])

  const handleDelete = () => {
    if (!record) return
    deleteBacktestResult(record.id)
    router.push('/backtesting/results')
  }

  if (notFound) {
    return (
      <div className="space-y-8">
        <div className="glass-strong rounded-xl p-16 text-center">
          <div className="text-6xl mb-4">🔍</div>
          <h3 className="text-2xl font-bold mb-2">Result Not Found</h3>
          <p className="text-muted-foreground mb-6">This backtest result may have been deleted or the link is invalid.</p>
          <Link href="/backtesting/results" className="px-6 py-3 rounded-lg bg-blue-600 text-white hover:bg-blue-500 transition-colors">
            View All Results
          </Link>
        </div>
      </div>
    )
  }

  if (!record) {
    return (
      <div className="flex items-center justify-center py-24">
        <span className="inline-block h-8 w-8 animate-spin rounded-full border-4 border-solid border-blue-500 border-r-transparent" />
      </div>
    )
  }

  const normalized = normalizeRecord(record)
  const initialCapital = num(record.initialCapital) ?? 0
  const symbol = text(record.symbol, 'this symbol')
  const startDate = text(record.startDate, 'the start of the window')
  const endDate = text(record.endDate, 'its end')
  const hasTradeStats = (normalized?.trades.rows.length ?? 0) > 0

  return (
    <div className="space-y-8">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <div className="flex items-center gap-3 mb-2">
            <Link href="/backtesting/results" className="text-sm text-muted-foreground hover:text-white">← Back to History</Link>
          </div>
          <h1 className="text-4xl font-bold mb-2 gradient-text">{text(record.strategyLabel, text(record.name, 'Saved backtest'))}</h1>
          <p className="text-muted-foreground text-lg">
            {symbol} | {startDate} → {endDate}
            {initialCapital > 0 ? ` | $${initialCapital.toLocaleString()} capital` : ''}
          </p>
          <p className="text-xs text-muted-foreground mt-1">
            Saved {new Date(record.createdAt).toLocaleString()}
          </p>
        </div>
        <div className="flex gap-3">
          <Link
            href={`/backtesting?strategy=${text(record.strategy, '')}&symbol=${text(record.symbol, '')}`}
            className="px-4 py-2 text-sm font-medium rounded-lg bg-blue-600 text-white hover:bg-blue-500 transition-colors"
          >
            Run Again
          </Link>
          <button
            onClick={handleDelete}
            className="px-4 py-2 text-sm font-medium rounded-lg bg-red-600/20 text-red-400 hover:bg-red-600/30 transition-colors"
          >
            Delete
          </button>
        </div>
      </div>

      {!normalized ? (
        <div className="glass-strong rounded-xl p-12 text-center border border-amber-500/30">
          <h3 className="text-2xl font-bold mb-3">This saved result cannot be redrawn</h3>
          <p className="text-muted-foreground max-w-xl mx-auto">
            The record holds no equity curve that can be read, so there is nothing measured
            to chart. Charts are not drawn from a placeholder curve. Re-run the backtest to
            produce a result that can be displayed.
          </p>
        </div>
      ) : !hasTradeStats ? (
        <NoTradesPanel
          symbol={symbol}
          startDate={startDate}
          endDate={endDate}
          equityPoints={normalized.points.length}
          executions={normalized.trades.executions}
        />
      ) : (
        <>
          <BacktestDataNotes
            returnUnit={normalized.trades.returnUnit}
            drawdownSource={normalized.drawdownSource}
            executions={normalized.trades.executions}
            realizedTrades={normalized.trades.rows.length}
            hasMonthlyReturns={normalized.chartData.monthlyReturns.length > 0}
            initialCapital={initialCapital}
          />
          <BacktestResultView
            metrics={normalized.metrics}
            data={normalized.chartData}
            initialCapital={initialCapital}
          />
        </>
      )}
    </div>
  )
}
