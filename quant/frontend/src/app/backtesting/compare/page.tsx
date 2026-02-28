/**
 * Backtest Compare Page
 * Side-by-side comparison of 2-4 backtest results with overlay charts
 */

'use client'

import { useState, useEffect, useMemo, Suspense } from 'react'
import { useSearchParams } from 'next/navigation'
import Link from 'next/link'
import dynamic from 'next/dynamic'
import { getBacktestResult, type BacktestResultRecord } from '@/lib/backtest-storage'

const ReactECharts = dynamic(() => import('echarts-for-react'), { ssr: false })

const COLORS = ['#10b981', '#3b82f6', '#f59e0b', '#ef4444']

function computeEquityData(record: BacktestResultRecord) {
  const result = record.result
  return result.equity_curve?.map((point: any, i: number) => ({
    day: point.day || i + 1,
    equity: point.equity || point.value || record.initialCapital,
  })) || []
}

function BacktestComparePageContent() {
  const searchParams = useSearchParams()
  const [records, setRecords] = useState<BacktestResultRecord[]>([])

  useEffect(() => {
    const idsParam = searchParams.get('ids')
    if (!idsParam) return
    const ids = idsParam.split(',')
    const found = ids.map(id => getBacktestResult(id)).filter(Boolean) as BacktestResultRecord[]
    setRecords(found)
  }, [searchParams])

  const overlayChartOption = useMemo(() => {
    if (records.length === 0) return {}

    const series = records.map((record, idx) => {
      const equityData = computeEquityData(record)
      // Normalize to percentage return
      const initial = equityData[0]?.equity || record.initialCapital
      return {
        name: `${record.strategyLabel} (${record.symbol})`,
        type: 'line',
        data: equityData.map((d: any) => [d.day, ((d.equity - initial) / initial * 100)]),
        smooth: true,
        lineStyle: { color: COLORS[idx], width: 2 },
        symbol: 'none',
      }
    })

    return {
      backgroundColor: 'transparent',
      tooltip: {
        trigger: 'axis',
        backgroundColor: 'rgba(30, 41, 59, 0.95)',
        borderColor: '#334155',
        textStyle: { color: '#e2e8f0' },
      },
      legend: {
        data: series.map(s => s.name),
        textStyle: { color: '#94a3b8' },
        top: 10,
      },
      grid: { left: '3%', right: '4%', bottom: '15%', top: '15%', containLabel: true },
      xAxis: {
        type: 'value', name: 'Trading Days', nameLocation: 'middle', nameGap: 30,
        axisLine: { lineStyle: { color: '#475569' } },
        axisLabel: { color: '#94a3b8' },
        splitLine: { lineStyle: { color: '#334155', type: 'dashed' } },
      },
      yAxis: {
        type: 'value', name: 'Return %', nameLocation: 'middle', nameGap: 50,
        axisLine: { lineStyle: { color: '#475569' } },
        axisLabel: { color: '#94a3b8', formatter: (v: number) => `${v.toFixed(1)}%` },
        splitLine: { lineStyle: { color: '#334155', type: 'dashed' } },
      },
      dataZoom: [
        { type: 'inside', start: 0, end: 100 },
        {
          type: 'slider', start: 0, end: 100, height: 20, bottom: 5,
          borderColor: '#475569', backgroundColor: 'rgba(71, 85, 105, 0.3)',
          fillerColor: 'rgba(59, 130, 246, 0.3)', handleStyle: { color: '#3b82f6' },
          textStyle: { color: '#94a3b8' },
        },
      ],
      series,
    }
  }, [records])

  // Find best/worst for each metric
  const metrics = ['totalReturn', 'sharpeRatio', 'winRate', 'maxDrawdown'] as const
  const bestIdx = (metric: typeof metrics[number]) => {
    if (records.length === 0) return -1
    if (metric === 'maxDrawdown') return records.reduce((best, r, i) => r[metric] > records[best][metric] ? i : best, 0)
    return records.reduce((best, r, i) => r[metric] > records[best][metric] ? i : best, 0)
  }

  if (records.length === 0) {
    return (
      <div className="space-y-8">
        <div className="glass-strong rounded-xl p-16 text-center">
          <div className="text-6xl mb-4">📊</div>
          <h3 className="text-2xl font-bold mb-2">No Results to Compare</h3>
          <p className="text-muted-foreground mb-6">
            Select 2-4 results from the history page to compare them side-by-side.
          </p>
          <Link href="/backtesting/results" className="px-6 py-3 rounded-lg bg-blue-600 text-white hover:bg-blue-500 transition-colors">
            Go to History
          </Link>
        </div>
      </div>
    )
  }

  return (
    <div className="space-y-8">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <div className="flex items-center gap-3 mb-2">
            <Link href="/backtesting/results" className="text-sm text-muted-foreground hover:text-white">← Back to History</Link>
          </div>
          <h1 className="text-4xl font-bold mb-2 gradient-text">Strategy Comparison</h1>
          <p className="text-muted-foreground text-lg">Comparing {records.length} strategies</p>
        </div>
      </div>

      {/* Legend chips */}
      <div className="flex flex-wrap gap-3">
        {records.map((r, idx) => (
          <div key={r.id} className="flex items-center gap-2 px-3 py-1.5 rounded-lg bg-slate-800 border border-slate-700">
            <div className="w-3 h-3 rounded-full" style={{ backgroundColor: COLORS[idx] }} />
            <span className="text-sm font-medium text-white">{r.strategyLabel}</span>
            <span className="text-xs text-muted-foreground">({r.symbol})</span>
          </div>
        ))}
      </div>

      {/* Overlay Equity Chart */}
      <div className="glass-strong rounded-xl p-6">
        <h2 className="text-2xl font-bold mb-4">Equity Curves (Normalized)</h2>
        <div className="h-[450px]">
          <ReactECharts option={overlayChartOption} style={{ height: '100%', width: '100%' }} opts={{ renderer: 'canvas' }} />
        </div>
      </div>

      {/* Comparison Table */}
      <div className="glass-strong rounded-xl overflow-hidden">
        <table className="w-full">
          <thead>
            <tr className="border-b border-slate-700">
              <th className="px-6 py-4 text-left text-xs font-semibold text-muted-foreground">Metric</th>
              {records.map((r, idx) => (
                <th key={r.id} className="px-6 py-4 text-right text-xs font-semibold" style={{ color: COLORS[idx] }}>
                  {r.strategyLabel}
                </th>
              ))}
            </tr>
          </thead>
          <tbody>
            <tr className="border-b border-slate-800">
              <td className="px-6 py-3 text-sm text-muted-foreground">Symbol</td>
              {records.map(r => <td key={r.id} className="px-6 py-3 text-right text-sm font-mono">{r.symbol}</td>)}
            </tr>
            <tr className="border-b border-slate-800">
              <td className="px-6 py-3 text-sm text-muted-foreground">Total Return</td>
              {records.map((r, idx) => (
                <td key={r.id} className={`px-6 py-3 text-right text-sm font-bold ${r.totalReturn >= 0 ? 'text-green-400' : 'text-red-400'} ${idx === bestIdx('totalReturn') ? 'bg-green-500/10' : ''}`}>
                  {r.totalReturn >= 0 ? '+' : ''}{r.totalReturn.toFixed(2)}%
                </td>
              ))}
            </tr>
            <tr className="border-b border-slate-800">
              <td className="px-6 py-3 text-sm text-muted-foreground">Sharpe Ratio</td>
              {records.map((r, idx) => (
                <td key={r.id} className={`px-6 py-3 text-right text-sm font-bold text-blue-400 ${idx === bestIdx('sharpeRatio') ? 'bg-blue-500/10' : ''}`}>
                  {r.sharpeRatio.toFixed(2)}
                </td>
              ))}
            </tr>
            <tr className="border-b border-slate-800">
              <td className="px-6 py-3 text-sm text-muted-foreground">Win Rate</td>
              {records.map((r, idx) => (
                <td key={r.id} className={`px-6 py-3 text-right text-sm font-bold text-purple-400 ${idx === bestIdx('winRate') ? 'bg-purple-500/10' : ''}`}>
                  {r.winRate.toFixed(1)}%
                </td>
              ))}
            </tr>
            <tr className="border-b border-slate-800">
              <td className="px-6 py-3 text-sm text-muted-foreground">Max Drawdown</td>
              {records.map((r, idx) => (
                <td key={r.id} className={`px-6 py-3 text-right text-sm font-bold text-red-400 ${idx === bestIdx('maxDrawdown') ? 'bg-green-500/10' : ''}`}>
                  {r.maxDrawdown.toFixed(2)}%
                </td>
              ))}
            </tr>
            <tr className="border-b border-slate-800">
              <td className="px-6 py-3 text-sm text-muted-foreground">Date Range</td>
              {records.map(r => <td key={r.id} className="px-6 py-3 text-right text-sm text-muted-foreground">{r.startDate} → {r.endDate}</td>)}
            </tr>
            <tr className="border-b border-slate-800">
              <td className="px-6 py-3 text-sm text-muted-foreground">Initial Capital</td>
              {records.map(r => <td key={r.id} className="px-6 py-3 text-right text-sm">${r.initialCapital.toLocaleString()}</td>)}
            </tr>
            <tr>
              <td className="px-6 py-3 text-sm text-muted-foreground">Actions</td>
              {records.map(r => (
                <td key={r.id} className="px-6 py-3 text-right">
                  <Link href={`/backtesting/results/${r.id}`} className="text-xs text-blue-400 hover:text-blue-300">
                    View Details →
                  </Link>
                </td>
              ))}
            </tr>
          </tbody>
        </table>
      </div>
    </div>
  )
}

export default function BacktestComparePage() {
  return (
    <Suspense fallback={<div className="text-center py-16 text-muted-foreground">Loading...</div>}>
      <BacktestComparePageContent />
    </Suspense>
  )
}
