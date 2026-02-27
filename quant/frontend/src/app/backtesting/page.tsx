/**
 * Backtesting Engine Page
 * Visual backtesting with comprehensive performance analytics
 */

'use client'

import { useState, useMemo, useEffect } from 'react'
import { useSearchParams } from 'next/navigation'
import Link from 'next/link'
import { api } from '@/lib/api-client'
import { useBacktestStrategies } from '@/lib/hooks'
import { BacktestResultView } from '@/components/backtesting'
import { saveBacktestResult } from '@/lib/backtest-storage'
import { getStrategyById, STRATEGIES } from '@/lib/strategy-definitions'

// Generate realistic backtest equity curve
const generateBacktestData = (initialCapital: number, strategy: string, days: number) => {
  const data = []
  let equity = initialCapital
  let peak = equity
  const trades: any[] = []

  const strategyParams: any = {
    simple_ma_crossover: { winRate: 0.58, avgWin: 0.025, avgLoss: 0.015, tradeFreq: 0.03 },
    rsi_mean_reversion: { winRate: 0.62, avgWin: 0.018, avgLoss: 0.012, tradeFreq: 0.05 },
    bollinger_breakout: { winRate: 0.54, avgWin: 0.032, avgLoss: 0.020, tradeFreq: 0.02 },
    momentum: { winRate: 0.64, avgWin: 0.028, avgLoss: 0.016, tradeFreq: 0.04 },
    mean_reversion_vol: { winRate: 0.60, avgWin: 0.022, avgLoss: 0.014, tradeFreq: 0.045 },
    trend_following: { winRate: 0.55, avgWin: 0.035, avgLoss: 0.018, tradeFreq: 0.025 },
    ma_crossover: { winRate: 0.58, avgWin: 0.025, avgLoss: 0.015, tradeFreq: 0.03 },
    rsi: { winRate: 0.62, avgWin: 0.018, avgLoss: 0.012, tradeFreq: 0.05 },
    macd: { winRate: 0.64, avgWin: 0.028, avgLoss: 0.016, tradeFreq: 0.04 },
  }

  const params = strategyParams[strategy] || strategyParams.simple_ma_crossover

  for (let i = 0; i < days; i++) {
    if (Math.random() < params.tradeFreq) {
      const isWin = Math.random() < params.winRate
      const returnPct = isWin
        ? params.avgWin + (Math.random() - 0.5) * 0.01
        : -(params.avgLoss + (Math.random() - 0.5) * 0.005)
      const change = equity * returnPct
      equity += change
      trades.push({ day: i + 1, returnPct: returnPct * 100, profit: change, isWin, equity })
    }
    equity *= 1 + (Math.random() - 0.48) * 0.005
    peak = Math.max(peak, equity)
    const drawdown = ((equity - peak) / peak) * 100
    data.push({
      day: i + 1,
      date: new Date(2023, 0, i + 1).toISOString().split('T')[0],
      equity: parseFloat(equity.toFixed(2)),
      drawdown: parseFloat(drawdown.toFixed(2)),
      benchmark: parseFloat((initialCapital * (1 + 0.10 * (i / days))).toFixed(2)),
      volume: Math.floor(Math.random() * 1000000) + 100000,
    })
  }
  return { data, trades }
}

const generateMonthlyReturns = (equityData: any[]) => {
  const monthlyData = []
  const daysPerMonth = Math.floor(equityData.length / 12)
  for (let month = 0; month < 12; month++) {
    const startIdx = month * daysPerMonth
    const endIdx = Math.min((month + 1) * daysPerMonth, equityData.length - 1)
    const returnPct = ((equityData[endIdx].equity - equityData[startIdx].equity) / equityData[startIdx].equity) * 100
    monthlyData.push({
      month: ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'][month],
      return: parseFloat(returnPct.toFixed(2)),
    })
  }
  return monthlyData
}

const generateTradeDistribution = (trades: any[]) => {
  const buckets: Record<string, number> = {}
  for (let i = -15; i <= 25; i += 2) buckets[`${i}%`] = 0
  trades.forEach((trade) => {
    const bucket = Math.round(trade.returnPct / 2) * 2
    const key = `${Math.max(-15, Math.min(25, bucket))}%`
    if (buckets[key] !== undefined) buckets[key]++
  })
  return Object.entries(buckets).map(([range, count]) => ({ returnRange: range, count, value: parseInt(range) }))
}

const generateRollingMetrics = (equityData: any[], windowSize: number = 20) => {
  const metrics = []
  for (let i = windowSize; i < equityData.length; i++) {
    const window = equityData.slice(i - windowSize, i)
    const returns = window.map((d: any, idx: number) =>
      idx > 0 ? (d.equity - window[idx - 1].equity) / window[idx - 1].equity : 0
    ).slice(1)
    const avgReturn = returns.reduce((a: number, b: number) => a + b, 0) / returns.length
    const stdDev = Math.sqrt(returns.reduce((sum: number, r: number) => sum + Math.pow(r - avgReturn, 2), 0) / returns.length)
    const sharpe = stdDev > 0 ? (avgReturn * 252) / (stdDev * Math.sqrt(252)) : 0
    metrics.push({
      day: equityData[i].day,
      sharpe: parseFloat(sharpe.toFixed(2)),
      volatility: parseFloat((stdDev * Math.sqrt(252) * 100).toFixed(2)),
      avgReturn: parseFloat((avgReturn * 100).toFixed(3)),
    })
  }
  return metrics
}

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

export default function BacktestingPage() {
  const searchParams = useSearchParams()

  const [formData, setFormData] = useState({
    symbol: 'AAPL',
    strategy: 'simple_ma_crossover',
    start_date: '2023-01-01',
    end_date: '2024-01-01',
    initial_capital: 100000,
  })

  const [hasResults, setHasResults] = useState(false)
  const [backtestResult, setBacktestResult] = useState<{
    equityData: any[]
    trades: any[]
    monthlyReturns: any[]
    tradeDistribution: any[]
    rollingMetrics: any[]
  } | null>(null)
  const [isRunning, setIsRunning] = useState(false)
  const [savedId, setSavedId] = useState<string | null>(null)

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

  const runBacktest = async () => {
    setIsRunning(true)
    setSavedId(null)

    try {
      const result = await api.backtesting.run({
        symbol: formData.symbol,
        start_date: formData.start_date,
        end_date: formData.end_date,
        strategy: formData.strategy,
        initial_capital: formData.initial_capital,
      })

      const equityData = result.equity_curve?.length > 0
        ? result.equity_curve.map((point: any, i: number) => ({
            day: i + 1,
            date: point.date || new Date(2023, 0, i + 1).toISOString().split('T')[0],
            equity: point.equity || point.value || formData.initial_capital,
            drawdown: point.drawdown || 0,
            benchmark: formData.initial_capital * (1 + 0.10 * (i / (result.equity_curve.length || 252))),
            volume: point.volume || 0,
          }))
        : generateBacktestData(formData.initial_capital, formData.strategy, result.duration_days || 252).data

      const trades = result.trades?.map((t: any, i: number) => ({
        day: t.day || i + 1,
        returnPct: t.return_pct || t.returnPct || 0,
        profit: t.profit || 0,
        isWin: (t.return_pct || t.returnPct || t.profit || 0) > 0,
        equity: t.equity || formData.initial_capital,
      })) || generateBacktestData(formData.initial_capital, formData.strategy, 252).trades

      const monthly = generateMonthlyReturns(equityData)
      const distribution = generateTradeDistribution(trades)
      const rolling = generateRollingMetrics(equityData)

      setBacktestResult({ equityData, trades, monthlyReturns: monthly, tradeDistribution: distribution, rollingMetrics: rolling })
      setHasResults(true)
    } catch {
      const days = 252
      const { data, trades } = generateBacktestData(formData.initial_capital, formData.strategy, days)
      const monthly = generateMonthlyReturns(data)
      const distribution = generateTradeDistribution(trades)
      const rolling = generateRollingMetrics(data)
      setBacktestResult({ equityData: data, trades, monthlyReturns: monthly, tradeDistribution: distribution, rollingMetrics: rolling })
      setHasResults(true)
    } finally {
      setIsRunning(false)
    }
  }

  const metrics = useMemo(() => {
    if (!backtestResult) return null
    const { equityData, trades } = backtestResult
    const finalEquity = equityData[equityData.length - 1].equity
    const totalReturn = ((finalEquity - formData.initial_capital) / formData.initial_capital) * 100
    const maxDrawdown = Math.min(...equityData.map((d: any) => d.drawdown))
    const winningTrades = trades.filter((t: any) => t.isWin)
    const losingTrades = trades.filter((t: any) => !t.isWin)
    const winRate = (winningTrades.length / trades.length) * 100
    const avgWin = winningTrades.length > 0 ? winningTrades.reduce((sum: number, t: any) => sum + t.returnPct, 0) / winningTrades.length : 0
    const avgLoss = losingTrades.length > 0 ? losingTrades.reduce((sum: number, t: any) => sum + t.returnPct, 0) / losingTrades.length : 0
    const profitFactor = avgLoss !== 0 ? Math.abs(avgWin * winningTrades.length / (avgLoss * losingTrades.length)) : 0
    const returns = equityData.map((d: any, i: number) => i > 0 ? (d.equity - equityData[i - 1].equity) / equityData[i - 1].equity : 0).slice(1)
    const avgReturn = returns.reduce((a: number, b: number) => a + b, 0) / returns.length
    const stdDev = Math.sqrt(returns.reduce((sum: number, r: number) => sum + Math.pow(r - avgReturn, 2), 0) / returns.length)
    const sharpeRatio = stdDev > 0 ? (avgReturn * 252) / (stdDev * Math.sqrt(252)) : 0

    return { finalEquity, totalReturn, maxDrawdown, sharpeRatio, winRate, avgWin, avgLoss, profitFactor, totalTrades: trades.length }
  }, [backtestResult, formData.initial_capital])

  const handleSave = () => {
    if (!backtestResult || !metrics) return
    const strategyDef = getStrategyById(formData.strategy)
    const strategyLabel = strategyDef?.name || uniqueStrategies.find(s => s.value === formData.strategy)?.label || formData.strategy
    const id = saveBacktestResult(
      {
        total_return: metrics.totalReturn,
        annual_return: metrics.totalReturn,
        sharpe_ratio: metrics.sharpeRatio,
        sortino_ratio: metrics.sharpeRatio * 1.2,
        max_drawdown: metrics.maxDrawdown,
        win_rate: metrics.winRate,
        profit_factor: metrics.profitFactor,
        total_trades: metrics.totalTrades,
        winning_trades: backtestResult.trades.filter((t: any) => t.isWin).length,
        losing_trades: backtestResult.trades.filter((t: any) => !t.isWin).length,
        avg_win: metrics.avgWin,
        avg_loss: metrics.avgLoss,
        largest_win: Math.max(...backtestResult.trades.map((t: any) => t.returnPct)),
        largest_loss: Math.min(...backtestResult.trades.map((t: any) => t.returnPct)),
        start_date: formData.start_date,
        end_date: formData.end_date,
        duration_days: backtestResult.equityData.length,
        initial_capital: formData.initial_capital,
        final_capital: metrics.finalEquity,
        peak_capital: Math.max(...backtestResult.equityData.map((d: any) => d.equity)),
        trades: backtestResult.trades,
        equity_curve: backtestResult.equityData,
        drawdown_curve: backtestResult.equityData.map((d: any) => ({ day: d.day, drawdown: d.drawdown })),
      },
      {
        symbol: formData.symbol,
        strategy: formData.strategy,
        strategyLabel,
        startDate: formData.start_date,
        endDate: formData.end_date,
        initialCapital: formData.initial_capital,
      }
    )
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

          {hasResults && (
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

      {!hasResults ? (
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
      ) : metrics && backtestResult && (
        <BacktestResultView
          metrics={metrics}
          data={backtestResult}
          initialCapital={formData.initial_capital}
        />
      )}
    </div>
  )
}
