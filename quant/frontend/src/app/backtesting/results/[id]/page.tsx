/**
 * Backtest Result Detail Page
 * Full visualization of a saved backtest result
 */

'use client'

import { useState, useEffect } from 'react'
import { useParams, useRouter } from 'next/navigation'
import Link from 'next/link'
import { getBacktestResult, deleteBacktestResult, type BacktestResultRecord } from '@/lib/backtest-storage'
import { BacktestResultView } from '@/components/backtesting'

function computeChartData(record: BacktestResultRecord) {
  const result = record.result
  const equityData = result.equity_curve?.map((point: any, i: number) => ({
    day: point.day || i + 1,
    equity: point.equity || point.value || record.initialCapital,
    drawdown: point.drawdown || 0,
    benchmark: record.initialCapital * (1 + 0.10 * (i / (result.equity_curve.length || 252))),
  })) || []

  const trades = result.trades?.map((t: any, i: number) => ({
    day: t.day || i + 1,
    returnPct: t.return_pct || t.returnPct || 0,
    profit: t.profit || 0,
    isWin: t.isWin ?? ((t.return_pct || t.returnPct || t.profit || 0) > 0),
    equity: t.equity || record.initialCapital,
  })) || []

  // Monthly returns
  const monthlyReturns = []
  if (equityData.length >= 12) {
    const dpm = Math.floor(equityData.length / 12)
    for (let m = 0; m < 12; m++) {
      const si = m * dpm
      const ei = Math.min((m + 1) * dpm, equityData.length - 1)
      monthlyReturns.push({
        month: ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'][m],
        return: parseFloat((((equityData[ei].equity - equityData[si].equity) / equityData[si].equity) * 100).toFixed(2)),
      })
    }
  }

  // Trade distribution
  const buckets: Record<string, number> = {}
  for (let i = -15; i <= 25; i += 2) buckets[`${i}%`] = 0
  trades.forEach((t: any) => {
    const b = Math.round(t.returnPct / 2) * 2
    const k = `${Math.max(-15, Math.min(25, b))}%`
    if (buckets[k] !== undefined) buckets[k]++
  })
  const tradeDistribution = Object.entries(buckets).map(([r, c]) => ({ returnRange: r, count: c, value: parseInt(r) }))

  // Rolling metrics
  const rollingMetrics = []
  for (let i = 20; i < equityData.length; i++) {
    const w = equityData.slice(i - 20, i)
    const rets = w.map((d: any, idx: number) => idx > 0 ? (d.equity - w[idx - 1].equity) / w[idx - 1].equity : 0).slice(1)
    const ar = rets.reduce((a: number, b: number) => a + b, 0) / rets.length
    const sd = Math.sqrt(rets.reduce((s: number, r: number) => s + Math.pow(r - ar, 2), 0) / rets.length)
    rollingMetrics.push({
      day: equityData[i].day,
      sharpe: parseFloat((sd > 0 ? (ar * 252) / (sd * Math.sqrt(252)) : 0).toFixed(2)),
      volatility: parseFloat((sd * Math.sqrt(252) * 100).toFixed(2)),
    })
  }

  const metrics = {
    finalEquity: result.final_capital || equityData[equityData.length - 1]?.equity || record.initialCapital,
    totalReturn: record.totalReturn,
    maxDrawdown: record.maxDrawdown,
    sharpeRatio: record.sharpeRatio,
    winRate: record.winRate,
    avgWin: result.avg_win || 0,
    avgLoss: result.avg_loss || 0,
    profitFactor: result.profit_factor || 0,
    totalTrades: result.total_trades || trades.length,
  }

  return { metrics, chartData: { equityData, trades, monthlyReturns, tradeDistribution, rollingMetrics } }
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

  const { metrics, chartData } = computeChartData(record)

  return (
    <div className="space-y-8">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <div className="flex items-center gap-3 mb-2">
            <Link href="/backtesting/results" className="text-sm text-muted-foreground hover:text-white">← Back to History</Link>
          </div>
          <h1 className="text-4xl font-bold mb-2 gradient-text">{record.strategyLabel}</h1>
          <p className="text-muted-foreground text-lg">
            {record.symbol} | {record.startDate} → {record.endDate} | ${record.initialCapital.toLocaleString()} capital
          </p>
          <p className="text-xs text-muted-foreground mt-1">
            Saved {new Date(record.createdAt).toLocaleString()}
          </p>
        </div>
        <div className="flex gap-3">
          <Link
            href={`/backtesting?strategy=${record.strategy}&symbol=${record.symbol}`}
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

      <BacktestResultView
        metrics={metrics}
        data={chartData}
        initialCapital={record.initialCapital}
      />
    </div>
  )
}
