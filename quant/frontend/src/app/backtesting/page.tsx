/**
 * Backtesting Engine Page
 * Visual backtesting with comprehensive performance analytics
 */

'use client'

import { useState, useEffect, Suspense } from 'react'
import { useSearchParams } from 'next/navigation'
import Link from 'next/link'
import { api } from '@/lib/api-client'
import { useBacktestStrategies } from '@/lib/hooks'
import { BacktestResultView } from '@/components/backtesting'
import { BacktestDataNotes, NoTradesPanel } from '@/components/BacktestDataNotes'
import { saveBacktestResult } from '@/lib/backtest-storage'
import { normalizeBacktest, type NormalizedBacktest } from '@/lib/backtest-normalize'
import { getStrategyById } from '@/lib/strategy-definitions'

// Strategy options for the dropdown
const strategyOptions = [
  { value: 'simple_ma_crossover', label: 'Moving Average Crossover', icon: '📈' },
  { value: 'rsi_mean_reversion', label: 'RSI Mean Reversion', icon: '🔄' },
  { value: 'bollinger_breakout', label: 'Bollinger Breakout', icon: '💥' },
  { value: 'momentum', label: 'Momentum Strategy', icon: '🚀' },
  { value: 'mean_reversion_vol', label: 'Volatility Mean Reversion', icon: '📊' },
  { value: 'trend_following', label: 'Trend Following', icon: '📉' },
  // Mapped from strategy-definitions for deep linking
  { value: 'ma_crossover', label: 'MA Crossover', icon: '📈' },
  { value: 'rsi', label: 'RSI Mean Reversion', icon: '🔄' },
  { value: 'macd', label: 'MACD Momentum', icon: '⚡' },
  { value: 'mean_reversion_zscore', label: 'Z-Score Mean Reversion', icon: '🎯' },
  { value: 'triple_ema', label: 'Triple EMA', icon: '📊' },
]

// De-duplicate by value
const uniqueStrategies = strategyOptions.filter(
  (s, i, arr) => arr.findIndex(x => x.value === s.value) === i
)

function BacktestingPageContent() {
  const searchParams = useSearchParams()

  const [formData, setFormData] = useState({
    symbol: 'AAPL',
    strategy: 'simple_ma_crossover',
    start_date: '2023-01-01',
    end_date: '2024-01-01',
    initial_capital: 100000,
  })

  const [backtestResult, setBacktestResult] = useState<NormalizedBacktest | null>(null)
  const [isRunning, setIsRunning] = useState(false)
  const [savedId, setSavedId] = useState<string | null>(null)
  const [runError, setRunError] = useState<string | null>(null)

  // Read query params for deep linking from /strategies page
  useEffect(() => {
    const strategyParam = searchParams.get('strategy')
    const symbolParam = searchParams.get('symbol')
    if (strategyParam) {
      // Check if it maps to a known strategy
      const found = uniqueStrategies.find(s => s.value === strategyParam)
      if (found) {
        setFormData(prev => ({ ...prev, strategy: strategyParam }))
      }
    }
    if (symbolParam) {
      setFormData(prev => ({ ...prev, symbol: symbolParam.toUpperCase() }))
    }
  }, [searchParams])

  const { data: apiStrategies } = useBacktestStrategies()

  // A backtest either runs on real returned data or it fails visibly. There is no
  // synthetic fallback: this page used to fabricate an equity curve (with per-strategy
  // win rates baked in, so every run "profited") whenever the API errored or returned
  // an empty curve. Fabricated results are worse than no results.
  const runBacktest = async () => {
    setIsRunning(true)
    setSavedId(null)
    setRunError(null)

    try {
      const result = await api.backtesting.run({
        symbol: formData.symbol,
        start_date: formData.start_date,
        end_date: formData.end_date,
        strategy: formData.strategy,
        initial_capital: formData.initial_capital,
      })

      if (!result.equity_curve?.length) {
        throw new Error(
          `No price history was returned for ${formData.symbol} over ${formData.start_date} to ${formData.end_date}.`
        )
      }

      // The backend sends equity_curve as { timestamp, equity } and ships drawdown
      // separately as drawdown_curve; trades carry `pnl`, never `return_pct`. Mapping is
      // in one place (lib/backtest-normalize) so the two run pages cannot drift apart.
      const normalized = normalizeBacktest(
        result.equity_curve,
        (result as any).drawdown_curve,
        result.trades,
        formData.initial_capital
      )

      if (normalized.points.length < 2) {
        throw new Error(
          `The backtest returned ${normalized.points.length} usable equity point(s) for ` +
            `${formData.symbol}. At least two are needed to measure a return.`
        )
      }

      setBacktestResult(normalized)
    } catch (err) {
      setBacktestResult(null)
      setRunError(
        err instanceof Error && err.message
          ? err.message
          : 'The backtest service could not be reached.'
      )
    } finally {
      setIsRunning(false)
    }
  }

  const hasResults = backtestResult !== null
  // Trade statistics exist only when trades were realised. With none, the metrics object
  // holds zeros that measure nothing, so the page shows the no-trades panel instead.
  const hasTradeStats = (backtestResult?.trades.rows.length ?? 0) > 0
  const metrics = backtestResult?.metrics ?? null

  const handleSave = () => {
    if (!backtestResult || !metrics || !hasTradeStats) return
    const strategyDef = getStrategyById(formData.strategy)
    const strategyLabel = strategyDef?.name || uniqueStrategies.find(s => s.value === formData.strategy)?.label || formData.strategy
    const rows = backtestResult.trades.rows
    // One record: the storage module takes a single object, and the history and compare
    // pages read these flat fields off it.
    const id = saveBacktestResult({
      name: `${strategyLabel} · ${formData.symbol}`,
      symbol: formData.symbol,
      strategy: formData.strategy,
      strategyLabel,
      startDate: formData.start_date,
      endDate: formData.end_date,
      initialCapital: formData.initial_capital,
      totalReturn: metrics.totalReturn,
      sharpeRatio: metrics.sharpeRatio,
      winRate: metrics.winRate,
      maxDrawdown: metrics.maxDrawdown,
      result: {
        total_return: metrics.totalReturn,
        sharpe_ratio: metrics.sharpeRatio,
        sortino_ratio: metrics.sortinoRatio,
        max_drawdown: metrics.maxDrawdown,
        win_rate: metrics.winRate,
        profit_factor: metrics.profitFactor,
        total_trades: metrics.totalTrades,
        executions: backtestResult.trades.executions,
        winning_trades: rows.filter(t => t.isWin).length,
        losing_trades: rows.filter(t => !t.isWin && t.profit < 0).length,
        avg_win: metrics.avgWin,
        avg_loss: metrics.avgLoss,
        largest_win: Math.max(...rows.map(t => t.profit)),
        largest_loss: Math.min(...rows.map(t => t.profit)),
        return_unit: backtestResult.trades.returnUnit,
        drawdown_source: backtestResult.drawdownSource,
        start_date: formData.start_date,
        end_date: formData.end_date,
        duration_days: backtestResult.points.length,
        initial_capital: formData.initial_capital,
        final_capital: metrics.finalEquity,
        peak_capital: Math.max(...backtestResult.points.map(p => p.equity)),
        // Stored the way the API sent them, so reopening a saved run re-derives the same
        // figures instead of reading percentages that were never reported.
        trades: rows.map(t => ({
          timestamp: t.date, side: t.side, quantity: t.quantity, price: t.price, pnl: t.profit,
        })),
        equity_curve: backtestResult.points.map(p => ({ timestamp: p.date, equity: p.equity })),
        drawdown_curve: backtestResult.points.map(p => ({ timestamp: p.date, drawdown: Math.abs(p.drawdown) })),
      },
    })
    setSavedId(id)
  }

  return (
    <div className="space-y-8">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-4xl font-bold mb-2 gradient-text">Backtesting Engine</h1>
          <p className="text-muted-foreground text-lg">
            Test and optimize your trading strategies with historical data
          </p>
        </div>
        <div className="flex gap-3">
          <Link href="/strategies" className="px-4 py-2 text-sm font-medium rounded-lg bg-slate-800 text-slate-300 hover:text-white hover:bg-slate-700 transition-colors">
            Strategy Library
          </Link>
          <Link href="/backtesting/builder" className="px-4 py-2 text-sm font-medium rounded-lg bg-blue-600 text-white hover:bg-blue-500 transition-colors">
            Strategy Builder
          </Link>
          <Link href="/backtesting/results" className="px-4 py-2 text-sm font-medium rounded-lg bg-slate-800 text-slate-300 hover:text-white hover:bg-slate-700 transition-colors">
            History
          </Link>
        </div>
      </div>

      {/* Configuration */}
      <div className="glass-strong rounded-xl p-6">
        <h2 className="text-xl font-bold mb-4">Strategy Configuration</h2>
        <div className="grid grid-cols-2 md:grid-cols-5 gap-4">
          <div>
            <label className="text-xs font-semibold text-muted-foreground mb-2 block">SYMBOL</label>
            <input
              type="text"
              value={formData.symbol}
              onChange={(e) => setFormData({ ...formData, symbol: e.target.value.toUpperCase() })}
              className="input-field uppercase font-mono"
              placeholder="AAPL"
            />
          </div>
          <div>
            <label className="text-xs font-semibold text-muted-foreground mb-2 block">STRATEGY</label>
            <select
              value={formData.strategy}
              onChange={(e) => setFormData({ ...formData, strategy: e.target.value })}
              className="input-field"
            >
              {uniqueStrategies.map((s) => (
                <option key={s.value} value={s.value}>{s.icon} {s.label}</option>
              ))}
            </select>
          </div>
          <div>
            <label className="text-xs font-semibold text-muted-foreground mb-2 block">START DATE</label>
            <input type="date" value={formData.start_date} onChange={(e) => setFormData({ ...formData, start_date: e.target.value })} className="input-field" />
          </div>
          <div>
            <label className="text-xs font-semibold text-muted-foreground mb-2 block">END DATE</label>
            <input type="date" value={formData.end_date} onChange={(e) => setFormData({ ...formData, end_date: e.target.value })} className="input-field" />
          </div>
          <div>
            <label className="text-xs font-semibold text-muted-foreground mb-2 block">CAPITAL ($)</label>
            <input
              type="number" value={formData.initial_capital}
              onChange={(e) => setFormData({ ...formData, initial_capital: Number(e.target.value) })}
              className="input-field" min={1000} step={1000}
            />
          </div>
        </div>

        <div className="flex items-center gap-4 mt-6">
          <button onClick={runBacktest} className="btn-primary" disabled={isRunning}>
            {isRunning ? (
              <>
                <span className="inline-block h-4 w-4 animate-spin rounded-full border-2 border-solid border-current border-r-transparent mr-2" />
                Running Backtest...
              </>
            ) : (
              'Run Backtest'
            )}
          </button>

          {/* Saving stores the run's headline statistics for the history and compare
              tables. A run with no trades has none to store. */}
          {hasResults && hasTradeStats && (
            <>
              <button onClick={handleSave} className="px-4 py-2 text-sm font-medium rounded-lg bg-green-600 text-white hover:bg-green-500 transition-colors">
                {savedId ? 'Saved!' : 'Save Result'}
              </button>
              {savedId && (
                <Link href={`/backtesting/results/${savedId}`} className="text-sm text-blue-400 hover:text-blue-300">
                  View saved result →
                </Link>
              )}
            </>
          )}
        </div>
      </div>

      {runError && !hasResults ? (
        <div className="glass-strong rounded-xl p-12 text-center border border-red-500/30">
          <h3 className="text-2xl font-bold mb-3">This backtest did not run</h3>
          <p className="text-muted-foreground mb-2 max-w-xl mx-auto">{runError}</p>
          <p className="text-sm text-muted-foreground mb-6 max-w-xl mx-auto">
            No results are shown because none were produced. This page will never display
            simulated results in place of a failed run.
          </p>
          <button onClick={runBacktest} className="btn-primary" disabled={isRunning}>
            Try again
          </button>
        </div>
      ) : !hasResults ? (
        <div className="glass-strong rounded-xl p-16 text-center">
          <div className="text-6xl mb-4">📊</div>
          <h3 className="text-2xl font-bold mb-2">Ready to Test Your Strategy</h3>
          <p className="text-muted-foreground mb-6">
            Configure your parameters above and click &quot;Run Backtest&quot; to see comprehensive results
          </p>
          <div className="flex gap-4 justify-center">
            <Link href="/strategies" className="px-6 py-3 rounded-lg bg-slate-800 text-slate-300 hover:text-white hover:bg-slate-700 transition-colors">
              Browse Strategies
            </Link>
            <Link href="/backtesting/builder" className="px-6 py-3 rounded-lg bg-blue-600 text-white hover:bg-blue-500 transition-colors">
              Build Custom Strategy
            </Link>
          </div>
        </div>
      ) : backtestResult && !hasTradeStats ? (
        <NoTradesPanel
          symbol={formData.symbol}
          startDate={formData.start_date}
          endDate={formData.end_date}
          equityPoints={backtestResult.points.length}
          executions={backtestResult.trades.executions}
        />
      ) : metrics && backtestResult && (
        <div className="space-y-8">
          <BacktestDataNotes
            returnUnit={backtestResult.trades.returnUnit}
            drawdownSource={backtestResult.drawdownSource}
            executions={backtestResult.trades.executions}
            realizedTrades={backtestResult.trades.rows.length}
            hasMonthlyReturns={backtestResult.chartData.monthlyReturns.length > 0}
            initialCapital={formData.initial_capital}
          />
          <BacktestResultView
            metrics={metrics}
            data={backtestResult.chartData}
            initialCapital={formData.initial_capital}
          />
        </div>
      )}
    </div>
  )
}

export default function BacktestingPage() {
  return (
    <Suspense fallback={<div className="text-center py-16 text-muted-foreground">Loading...</div>}>
      <BacktestingPageContent />
    </Suspense>
  )
}
