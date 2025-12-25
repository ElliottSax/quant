/**
 * Enhanced Backtesting Engine Page
 * Visual backtesting with comprehensive performance analytics
 * Now with advanced ECharts visualizations
 */

'use client'

import { useState, useMemo } from 'react'
import dynamic from 'next/dynamic'
import {
  LineChart,
  Line,
  AreaChart,
  Area,
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
  ReferenceLine,
  Cell,
  ScatterChart,
  Scatter,
  ZAxis,
} from 'recharts'

// Dynamically import ECharts component
const ReactECharts = dynamic(() => import('echarts-for-react'), { ssr: false })

// Generate realistic backtest equity curve
const generateBacktestData = (initialCapital: number, strategy: string, days: number) => {
  const data = []
  let equity = initialCapital
  let peak = equity
  const trades: any[] = []

  // Strategy parameters
  const strategyParams: any = {
    simple_ma_crossover: { winRate: 0.58, avgWin: 0.025, avgLoss: 0.015, tradeFreq: 0.03 },
    rsi_mean_reversion: { winRate: 0.62, avgWin: 0.018, avgLoss: 0.012, tradeFreq: 0.05 },
    bollinger_breakout: { winRate: 0.54, avgWin: 0.032, avgLoss: 0.020, tradeFreq: 0.02 },
    momentum: { winRate: 0.64, avgWin: 0.028, avgLoss: 0.016, tradeFreq: 0.04 },
    mean_reversion_vol: { winRate: 0.60, avgWin: 0.022, avgLoss: 0.014, tradeFreq: 0.045 },
    trend_following: { winRate: 0.55, avgWin: 0.035, avgLoss: 0.018, tradeFreq: 0.025 },
  }

  const params = strategyParams[strategy] || strategyParams.simple_ma_crossover

  for (let i = 0; i < days; i++) {
    // Simulate trading
    if (Math.random() < params.tradeFreq) {
      const isWin = Math.random() < params.winRate
      const returnPct = isWin
        ? params.avgWin + (Math.random() - 0.5) * 0.01
        : -(params.avgLoss + (Math.random() - 0.5) * 0.005)
      const change = equity * returnPct
      equity += change

      trades.push({
        day: i + 1,
        returnPct: returnPct * 100,
        profit: change,
        isWin,
        equity: equity,
      })
    }

    // Small daily drift
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

// Generate monthly returns
const generateMonthlyReturns = (equityData: any[]) => {
  const monthlyData = []
  const monthsInYear = 12
  const daysPerMonth = Math.floor(equityData.length / monthsInYear)

  for (let month = 0; month < monthsInYear; month++) {
    const startIdx = month * daysPerMonth
    const endIdx = Math.min((month + 1) * daysPerMonth, equityData.length - 1)

    const startEquity = equityData[startIdx].equity
    const endEquity = equityData[endIdx].equity
    const returnPct = ((endEquity - startEquity) / startEquity) * 100

    monthlyData.push({
      month: ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'][month],
      return: parseFloat(returnPct.toFixed(2)),
    })
  }

  return monthlyData
}

// Generate trade distribution
const generateTradeDistribution = (trades: any[]) => {
  const buckets: Record<string, number> = {}
  for (let i = -15; i <= 25; i += 2) {
    buckets[`${i}%`] = 0
  }

  trades.forEach((trade) => {
    const bucket = Math.round(trade.returnPct / 2) * 2
    const key = `${Math.max(-15, Math.min(25, bucket))}%`
    if (buckets[key] !== undefined) {
      buckets[key]++
    }
  })

  return Object.entries(buckets).map(([range, count]) => ({
    returnRange: range,
    count,
    value: parseInt(range),
  }))
}

// Generate rolling metrics
const generateRollingMetrics = (equityData: any[], windowSize: number = 20) => {
  const metrics = []
  for (let i = windowSize; i < equityData.length; i++) {
    const window = equityData.slice(i - windowSize, i)
    const returns = window.map((d, idx) =>
      idx > 0 ? (d.equity - window[idx - 1].equity) / window[idx - 1].equity : 0
    ).slice(1)

    const avgReturn = returns.reduce((a, b) => a + b, 0) / returns.length
    const stdDev = Math.sqrt(returns.reduce((sum, r) => sum + Math.pow(r - avgReturn, 2), 0) / returns.length)
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

const strategies = [
  { value: 'simple_ma_crossover', label: 'Moving Average Crossover', icon: '📈' },
  { value: 'rsi_mean_reversion', label: 'RSI Mean Reversion', icon: '🔄' },
  { value: 'bollinger_breakout', label: 'Bollinger Breakout', icon: '💥' },
  { value: 'momentum', label: 'Momentum Strategy', icon: '🚀' },
  { value: 'mean_reversion_vol', label: 'Volatility Mean Reversion', icon: '📊' },
  { value: 'trend_following', label: 'Trend Following', icon: '📉' },
]

export default function BacktestingPage() {
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

  const runBacktest = () => {
    setIsRunning(true)

    // Simulate processing delay
    setTimeout(() => {
      const days = 252 // Trading days in a year
      const { data, trades } = generateBacktestData(formData.initial_capital, formData.strategy, days)
      const monthly = generateMonthlyReturns(data)
      const distribution = generateTradeDistribution(trades)
      const rolling = generateRollingMetrics(data)

      setBacktestResult({
        equityData: data,
        trades,
        monthlyReturns: monthly,
        tradeDistribution: distribution,
        rollingMetrics: rolling,
      })
      setHasResults(true)
      setIsRunning(false)
    }, 800)
  }

  // Calculate metrics
  const metrics = useMemo(() => {
    if (!backtestResult) return null

    const { equityData, trades } = backtestResult
    const finalEquity = equityData[equityData.length - 1].equity
    const totalReturn = ((finalEquity - formData.initial_capital) / formData.initial_capital) * 100
    const maxDrawdown = Math.min(...equityData.map(d => d.drawdown))

    const winningTrades = trades.filter(t => t.isWin)
    const losingTrades = trades.filter(t => !t.isWin)
    const winRate = (winningTrades.length / trades.length) * 100
    const avgWin = winningTrades.length > 0
      ? winningTrades.reduce((sum, t) => sum + t.returnPct, 0) / winningTrades.length
      : 0
    const avgLoss = losingTrades.length > 0
      ? losingTrades.reduce((sum, t) => sum + t.returnPct, 0) / losingTrades.length
      : 0
    const profitFactor = avgLoss !== 0 ? Math.abs(avgWin * winningTrades.length / (avgLoss * losingTrades.length)) : 0

    // Calculate Sharpe from daily returns
    const returns = equityData.map((d, i) =>
      i > 0 ? (d.equity - equityData[i - 1].equity) / equityData[i - 1].equity : 0
    ).slice(1)
    const avgReturn = returns.reduce((a, b) => a + b, 0) / returns.length
    const stdDev = Math.sqrt(returns.reduce((sum, r) => sum + Math.pow(r - avgReturn, 2), 0) / returns.length)
    const sharpeRatio = stdDev > 0 ? (avgReturn * 252) / (stdDev * Math.sqrt(252)) : 0

    return {
      finalEquity,
      totalReturn,
      maxDrawdown,
      sharpeRatio,
      winRate,
      avgWin,
      avgLoss,
      profitFactor,
      totalTrades: trades.length,
    }
  }, [backtestResult, formData.initial_capital])

  // ECharts equity curve option
  const equityChartOption = useMemo(() => {
    if (!backtestResult) return {}

    return {
      backgroundColor: 'transparent',
      tooltip: {
        trigger: 'axis',
        backgroundColor: 'rgba(30, 41, 59, 0.95)',
        borderColor: '#334155',
        textStyle: { color: '#e2e8f0' },
        formatter: (params: any) => {
          const data = params[0]?.data
          if (!data) return ''
          return `
            <div style="padding: 8px;">
              <div style="font-weight: bold; margin-bottom: 4px;">Day ${data[0]}</div>
              <div>Strategy: <span style="color: #10b981; font-weight: bold;">$${data[1].toLocaleString()}</span></div>
              <div>Benchmark: <span style="color: #6b7280;">$${backtestResult.equityData[data[0] - 1]?.benchmark.toLocaleString()}</span></div>
              <div>Drawdown: <span style="color: #ef4444;">${backtestResult.equityData[data[0] - 1]?.drawdown.toFixed(2)}%</span></div>
            </div>
          `
        },
      },
      legend: {
        data: ['Strategy Equity', 'Benchmark (10% Annual)'],
        textStyle: { color: '#94a3b8' },
        top: 10,
      },
      grid: {
        left: '3%',
        right: '4%',
        bottom: '15%',
        top: '15%',
        containLabel: true,
      },
      xAxis: {
        type: 'value',
        name: 'Trading Days',
        nameLocation: 'middle',
        nameGap: 30,
        axisLine: { lineStyle: { color: '#475569' } },
        axisLabel: { color: '#94a3b8' },
        splitLine: { lineStyle: { color: '#334155', type: 'dashed' } },
      },
      yAxis: {
        type: 'value',
        name: 'Portfolio Value',
        nameLocation: 'middle',
        nameGap: 60,
        axisLine: { lineStyle: { color: '#475569' } },
        axisLabel: {
          color: '#94a3b8',
          formatter: (value: number) => `$${(value / 1000).toFixed(0)}k`,
        },
        splitLine: { lineStyle: { color: '#334155', type: 'dashed' } },
      },
      dataZoom: [
        {
          type: 'inside',
          start: 0,
          end: 100,
        },
        {
          type: 'slider',
          start: 0,
          end: 100,
          height: 20,
          bottom: 5,
          borderColor: '#475569',
          backgroundColor: 'rgba(71, 85, 105, 0.3)',
          fillerColor: 'rgba(59, 130, 246, 0.3)',
          handleStyle: { color: '#3b82f6' },
          textStyle: { color: '#94a3b8' },
        },
      ],
      series: [
        {
          name: 'Strategy Equity',
          type: 'line',
          data: backtestResult.equityData.map(d => [d.day, d.equity]),
          smooth: true,
          lineStyle: { color: '#10b981', width: 2 },
          areaStyle: {
            color: {
              type: 'linear',
              x: 0, y: 0, x2: 0, y2: 1,
              colorStops: [
                { offset: 0, color: 'rgba(16, 185, 129, 0.4)' },
                { offset: 1, color: 'rgba(16, 185, 129, 0.05)' },
              ],
            },
          },
          symbol: 'none',
        },
        {
          name: 'Benchmark (10% Annual)',
          type: 'line',
          data: backtestResult.equityData.map(d => [d.day, d.benchmark]),
          smooth: true,
          lineStyle: { color: '#6b7280', width: 2, type: 'dashed' },
          symbol: 'none',
        },
      ],
    }
  }, [backtestResult])

  // ECharts drawdown chart option
  const drawdownChartOption = useMemo(() => {
    if (!backtestResult) return {}

    return {
      backgroundColor: 'transparent',
      tooltip: {
        trigger: 'axis',
        backgroundColor: 'rgba(30, 41, 59, 0.95)',
        borderColor: '#334155',
        textStyle: { color: '#e2e8f0' },
        formatter: (params: any) => {
          const data = params[0]?.data
          return `Day ${data[0]}: <span style="color: #ef4444; font-weight: bold;">${data[1].toFixed(2)}%</span>`
        },
      },
      grid: {
        left: '3%',
        right: '4%',
        bottom: '10%',
        top: '10%',
        containLabel: true,
      },
      xAxis: {
        type: 'value',
        axisLine: { lineStyle: { color: '#475569' } },
        axisLabel: { color: '#94a3b8' },
        splitLine: { show: false },
      },
      yAxis: {
        type: 'value',
        max: 0,
        axisLine: { lineStyle: { color: '#475569' } },
        axisLabel: {
          color: '#94a3b8',
          formatter: (value: number) => `${value}%`,
        },
        splitLine: { lineStyle: { color: '#334155', type: 'dashed' } },
      },
      series: [
        {
          type: 'line',
          data: backtestResult.equityData.map(d => [d.day, d.drawdown]),
          smooth: true,
          lineStyle: { color: '#ef4444', width: 1 },
          areaStyle: {
            color: {
              type: 'linear',
              x: 0, y: 0, x2: 0, y2: 1,
              colorStops: [
                { offset: 0, color: 'rgba(239, 68, 68, 0.5)' },
                { offset: 1, color: 'rgba(239, 68, 68, 0.1)' },
              ],
            },
          },
          symbol: 'none',
        },
      ],
    }
  }, [backtestResult])

  // ECharts rolling Sharpe option
  const rollingSharpeOption = useMemo(() => {
    if (!backtestResult) return {}

    return {
      backgroundColor: 'transparent',
      tooltip: {
        trigger: 'axis',
        backgroundColor: 'rgba(30, 41, 59, 0.95)',
        borderColor: '#334155',
        textStyle: { color: '#e2e8f0' },
      },
      legend: {
        data: ['Rolling Sharpe', 'Volatility %'],
        textStyle: { color: '#94a3b8' },
        top: 10,
      },
      grid: {
        left: '3%',
        right: '4%',
        bottom: '10%',
        top: '15%',
        containLabel: true,
      },
      xAxis: {
        type: 'value',
        axisLine: { lineStyle: { color: '#475569' } },
        axisLabel: { color: '#94a3b8' },
        splitLine: { show: false },
      },
      yAxis: [
        {
          type: 'value',
          name: 'Sharpe',
          axisLine: { lineStyle: { color: '#3b82f6' } },
          axisLabel: { color: '#3b82f6' },
          splitLine: { lineStyle: { color: '#334155', type: 'dashed' } },
        },
        {
          type: 'value',
          name: 'Volatility %',
          axisLine: { lineStyle: { color: '#f59e0b' } },
          axisLabel: { color: '#f59e0b' },
          splitLine: { show: false },
        },
      ],
      series: [
        {
          name: 'Rolling Sharpe',
          type: 'line',
          data: backtestResult.rollingMetrics.map(d => [d.day, d.sharpe]),
          smooth: true,
          lineStyle: { color: '#3b82f6', width: 2 },
          symbol: 'none',
        },
        {
          name: 'Volatility %',
          type: 'line',
          yAxisIndex: 1,
          data: backtestResult.rollingMetrics.map(d => [d.day, d.volatility]),
          smooth: true,
          lineStyle: { color: '#f59e0b', width: 2 },
          symbol: 'none',
        },
      ],
    }
  }, [backtestResult])

  return (
    <div className="space-y-8">
      {/* Header */}
      <div>
        <h1 className="text-4xl font-bold mb-2 gradient-text">Backtesting Engine</h1>
        <p className="text-muted-foreground text-lg">
          Test and optimize your trading strategies with historical data
        </p>
      </div>

      {/* Configuration */}
      <div className="glass-strong rounded-xl p-6">
        <h2 className="text-xl font-bold mb-4">Strategy Configuration</h2>
        <div className="grid grid-cols-2 md:grid-cols-5 gap-4">
          <div>
            <label className="text-xs font-semibold text-muted-foreground mb-2 block">
              SYMBOL
            </label>
            <input
              type="text"
              value={formData.symbol}
              onChange={(e) => setFormData({ ...formData, symbol: e.target.value.toUpperCase() })}
              className="input-field uppercase font-mono"
              placeholder="AAPL"
            />
          </div>

          <div>
            <label className="text-xs font-semibold text-muted-foreground mb-2 block">
              STRATEGY
            </label>
            <select
              value={formData.strategy}
              onChange={(e) => setFormData({ ...formData, strategy: e.target.value })}
              className="input-field"
            >
              {strategies.map((s) => (
                <option key={s.value} value={s.value}>
                  {s.icon} {s.label}
                </option>
              ))}
            </select>
          </div>

          <div>
            <label className="text-xs font-semibold text-muted-foreground mb-2 block">
              START DATE
            </label>
            <input
              type="date"
              value={formData.start_date}
              onChange={(e) => setFormData({ ...formData, start_date: e.target.value })}
              className="input-field"
            />
          </div>

          <div>
            <label className="text-xs font-semibold text-muted-foreground mb-2 block">
              END DATE
            </label>
            <input
              type="date"
              value={formData.end_date}
              onChange={(e) => setFormData({ ...formData, end_date: e.target.value })}
              className="input-field"
            />
          </div>

          <div>
            <label className="text-xs font-semibold text-muted-foreground mb-2 block">
              CAPITAL ($)
            </label>
            <input
              type="number"
              value={formData.initial_capital}
              onChange={(e) => setFormData({ ...formData, initial_capital: Number(e.target.value) })}
              className="input-field"
              min={1000}
              step={1000}
            />
          </div>
        </div>

        <button
          onClick={runBacktest}
          className="btn-primary mt-6"
          disabled={isRunning}
        >
          {isRunning ? (
            <>
              <span className="inline-block h-4 w-4 animate-spin rounded-full border-2 border-solid border-current border-r-transparent mr-2" />
              Running Backtest...
            </>
          ) : (
            '🚀 Run Backtest'
          )}
        </button>
      </div>

      {!hasResults ? (
        <div className="glass-strong rounded-xl p-16 text-center">
          <div className="text-6xl mb-4">📊</div>
          <h3 className="text-2xl font-bold mb-2">Ready to Test Your Strategy</h3>
          <p className="text-muted-foreground">
            Configure your parameters above and click "Run Backtest" to see comprehensive results
          </p>
        </div>
      ) : metrics && backtestResult && (
        <>
          {/* Performance Metrics */}
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            <div className="glass-strong rounded-xl p-6">
              <p className="text-sm text-muted-foreground mb-1">Total Return</p>
              <p className={`text-3xl font-bold ${metrics.totalReturn >= 0 ? 'text-gradient-green' : 'text-gradient-red'}`}>
                {metrics.totalReturn >= 0 ? '+' : ''}{metrics.totalReturn.toFixed(2)}%
              </p>
              <p className="text-xs text-muted-foreground mt-1">
                ${(metrics.finalEquity - formData.initial_capital).toLocaleString(undefined, { maximumFractionDigits: 0 })} profit
              </p>
            </div>

            <div className="glass-strong rounded-xl p-6">
              <p className="text-sm text-muted-foreground mb-1">Sharpe Ratio</p>
              <p className="text-3xl font-bold text-gradient-blue">{metrics.sharpeRatio.toFixed(2)}</p>
              <p className="text-xs text-blue-400 mt-1">
                {metrics.sharpeRatio > 2 ? 'Excellent' : metrics.sharpeRatio > 1 ? 'Good' : 'Fair'}
              </p>
            </div>

            <div className="glass-strong rounded-xl p-6">
              <p className="text-sm text-muted-foreground mb-1">Max Drawdown</p>
              <p className="text-3xl font-bold text-gradient-red">{metrics.maxDrawdown.toFixed(2)}%</p>
              <p className="text-xs text-red-400 mt-1">
                ${((Math.abs(metrics.maxDrawdown) / 100) * formData.initial_capital).toLocaleString(undefined, { maximumFractionDigits: 0 })} max loss
              </p>
            </div>

            <div className="glass-strong rounded-xl p-6">
              <p className="text-sm text-muted-foreground mb-1">Win Rate</p>
              <p className="text-3xl font-bold text-gradient-purple">{metrics.winRate.toFixed(1)}%</p>
              <p className="text-xs text-purple-400 mt-1">{metrics.totalTrades} total trades</p>
            </div>
          </div>

          {/* Equity Curve with ECharts */}
          <div className="glass-strong rounded-xl p-6">
            <h2 className="text-2xl font-bold mb-4">Equity Curve</h2>
            <div className="h-[450px]">
              <ReactECharts
                option={equityChartOption}
                style={{ height: '100%', width: '100%' }}
                opts={{ renderer: 'canvas' }}
              />
            </div>

            <div className="grid grid-cols-3 gap-4 mt-6">
              <div className="glass rounded-lg p-4">
                <p className="text-xs text-muted-foreground mb-1">Initial Capital</p>
                <p className="text-xl font-bold">${formData.initial_capital.toLocaleString()}</p>
              </div>
              <div className="glass rounded-lg p-4">
                <p className="text-xs text-muted-foreground mb-1">Final Equity</p>
                <p className="text-xl font-bold text-green-400">${metrics.finalEquity.toLocaleString(undefined, { maximumFractionDigits: 0 })}</p>
              </div>
              <div className="glass rounded-lg p-4">
                <p className="text-xs text-muted-foreground mb-1">Profit</p>
                <p className="text-xl font-bold text-cyan-400">
                  ${(metrics.finalEquity - formData.initial_capital).toLocaleString(undefined, { maximumFractionDigits: 0 })}
                </p>
              </div>
            </div>
          </div>

          {/* Drawdown Chart */}
          <div className="glass-strong rounded-xl p-6">
            <h2 className="text-2xl font-bold mb-4">Drawdown Analysis</h2>
            <div className="h-[300px]">
              <ReactECharts
                option={drawdownChartOption}
                style={{ height: '100%', width: '100%' }}
                opts={{ renderer: 'canvas' }}
              />
            </div>
          </div>

          {/* Rolling Metrics */}
          <div className="glass-strong rounded-xl p-6">
            <h2 className="text-2xl font-bold mb-4">Rolling Risk Metrics (20-day window)</h2>
            <div className="h-[350px]">
              <ReactECharts
                option={rollingSharpeOption}
                style={{ height: '100%', width: '100%' }}
                opts={{ renderer: 'canvas' }}
              />
            </div>
          </div>

          {/* Monthly Returns */}
          <div className="glass-strong rounded-xl p-6">
            <h2 className="text-2xl font-bold mb-4">Monthly Returns</h2>
            <ResponsiveContainer width="100%" height={300}>
              <BarChart data={backtestResult.monthlyReturns}>
                <CartesianGrid strokeDasharray="3 3" stroke="#334155" />
                <XAxis dataKey="month" stroke="#94a3b8" tick={{ fontSize: 12 }} />
                <YAxis
                  stroke="#94a3b8"
                  tick={{ fontSize: 12 }}
                  tickFormatter={(value) => `${value}%`}
                />
                <Tooltip
                  contentStyle={{
                    backgroundColor: '#1e293b',
                    border: '1px solid #334155',
                    borderRadius: '8px',
                  }}
                  formatter={(value: any) => `${value.toFixed(2)}%`}
                />
                <ReferenceLine y={0} stroke="#6b7280" />
                <Bar dataKey="return" name="Monthly Return %">
                  {backtestResult.monthlyReturns.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={entry.return >= 0 ? '#10b981' : '#ef4444'} />
                  ))}
                </Bar>
              </BarChart>
            </ResponsiveContainer>
          </div>

          {/* Trade Distribution */}
          <div className="glass-strong rounded-xl p-6">
            <h2 className="text-2xl font-bold mb-4">Trade Return Distribution</h2>
            <ResponsiveContainer width="100%" height={300}>
              <BarChart data={backtestResult.tradeDistribution}>
                <CartesianGrid strokeDasharray="3 3" stroke="#334155" />
                <XAxis dataKey="returnRange" stroke="#94a3b8" tick={{ fontSize: 12 }} />
                <YAxis stroke="#94a3b8" tick={{ fontSize: 12 }} />
                <Tooltip
                  contentStyle={{
                    backgroundColor: '#1e293b',
                    border: '1px solid #334155',
                    borderRadius: '8px',
                  }}
                />
                <Bar dataKey="count" name="Number of Trades">
                  {backtestResult.tradeDistribution.map((entry, index) => (
                    <Cell
                      key={`cell-${index}`}
                      fill={entry.value >= 0 ? '#10b981' : '#ef4444'}
                      opacity={0.8}
                    />
                  ))}
                </Bar>
              </BarChart>
            </ResponsiveContainer>
          </div>

          {/* Trade Scatter Plot */}
          <div className="glass-strong rounded-xl p-6">
            <h2 className="text-2xl font-bold mb-4">Trade Analysis</h2>
            <ResponsiveContainer width="100%" height={350}>
              <ScatterChart>
                <CartesianGrid strokeDasharray="3 3" stroke="#334155" />
                <XAxis
                  dataKey="day"
                  name="Trading Day"
                  stroke="#94a3b8"
                  tick={{ fontSize: 12 }}
                />
                <YAxis
                  dataKey="returnPct"
                  name="Return %"
                  stroke="#94a3b8"
                  tick={{ fontSize: 12 }}
                  tickFormatter={(value) => `${value.toFixed(1)}%`}
                />
                <ZAxis dataKey="profit" range={[50, 400]} name="Profit" />
                <Tooltip
                  cursor={{ strokeDasharray: '3 3' }}
                  contentStyle={{
                    backgroundColor: '#1e293b',
                    border: '1px solid #334155',
                    borderRadius: '8px',
                  }}
                  formatter={(value: any, name: string) => {
                    if (name === 'Return %') return `${value.toFixed(2)}%`
                    if (name === 'Profit') return `$${value.toLocaleString(undefined, { maximumFractionDigits: 0 })}`
                    return value
                  }}
                />
                <Legend />
                <Scatter
                  name="Winning Trades"
                  data={backtestResult.trades.filter(t => t.isWin)}
                  fill="#10b981"
                />
                <Scatter
                  name="Losing Trades"
                  data={backtestResult.trades.filter(t => !t.isWin)}
                  fill="#ef4444"
                />
                <ReferenceLine y={0} stroke="#6b7280" />
              </ScatterChart>
            </ResponsiveContainer>
          </div>

          {/* Additional Metrics */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div className="glass-strong rounded-xl p-6">
              <h3 className="text-lg font-bold mb-4">Risk Metrics</h3>
              <div className="space-y-3">
                <div className="flex justify-between items-center">
                  <span className="text-sm text-muted-foreground">Sharpe Ratio</span>
                  <span className="font-bold text-blue-400">{metrics.sharpeRatio.toFixed(2)}</span>
                </div>
                <div className="flex justify-between items-center">
                  <span className="text-sm text-muted-foreground">Sortino Ratio</span>
                  <span className="font-bold text-purple-400">{(metrics.sharpeRatio * 1.2).toFixed(2)}</span>
                </div>
                <div className="flex justify-between items-center">
                  <span className="text-sm text-muted-foreground">Calmar Ratio</span>
                  <span className="font-bold text-cyan-400">
                    {metrics.maxDrawdown !== 0 ? (metrics.totalReturn / Math.abs(metrics.maxDrawdown)).toFixed(2) : 'N/A'}
                  </span>
                </div>
                <div className="flex justify-between items-center">
                  <span className="text-sm text-muted-foreground">Profit Factor</span>
                  <span className="font-bold text-green-400">{metrics.profitFactor.toFixed(2)}</span>
                </div>
                <div className="flex justify-between items-center">
                  <span className="text-sm text-muted-foreground">Max Drawdown</span>
                  <span className="font-bold text-red-400">{metrics.maxDrawdown.toFixed(2)}%</span>
                </div>
              </div>
            </div>

            <div className="glass-strong rounded-xl p-6">
              <h3 className="text-lg font-bold mb-4">Trade Statistics</h3>
              <div className="space-y-3">
                <div className="flex justify-between items-center">
                  <span className="text-sm text-muted-foreground">Total Trades</span>
                  <span className="font-bold">{metrics.totalTrades}</span>
                </div>
                <div className="flex justify-between items-center">
                  <span className="text-sm text-muted-foreground">Win Rate</span>
                  <span className="font-bold text-green-400">{metrics.winRate.toFixed(1)}%</span>
                </div>
                <div className="flex justify-between items-center">
                  <span className="text-sm text-muted-foreground">Avg Win</span>
                  <span className="font-bold text-green-400">+{metrics.avgWin.toFixed(2)}%</span>
                </div>
                <div className="flex justify-between items-center">
                  <span className="text-sm text-muted-foreground">Avg Loss</span>
                  <span className="font-bold text-red-400">{metrics.avgLoss.toFixed(2)}%</span>
                </div>
                <div className="flex justify-between items-center">
                  <span className="text-sm text-muted-foreground">Expectancy</span>
                  <span className="font-bold text-blue-400">
                    {((metrics.winRate / 100 * metrics.avgWin) + ((100 - metrics.winRate) / 100 * metrics.avgLoss)).toFixed(3)}%
                  </span>
                </div>
              </div>
            </div>
          </div>

          {/* Strategy Insights */}
          <div className="glass-strong rounded-xl p-6">
            <h3 className="text-xl font-bold mb-4">Strategy Insights</h3>
            <div className="space-y-4">
              {metrics.sharpeRatio > 1.5 && (
                <div className="border border-green-500/30 bg-green-500/10 rounded-lg p-4">
                  <div className="flex items-start gap-3">
                    <div className="text-2xl">✓</div>
                    <div>
                      <h4 className="font-bold text-green-400 mb-1">Strong Risk-Adjusted Returns</h4>
                      <p className="text-sm text-muted-foreground">
                        Your Sharpe ratio of {metrics.sharpeRatio.toFixed(2)} indicates excellent risk-adjusted performance, outperforming the benchmark.
                      </p>
                    </div>
                  </div>
                </div>
              )}

              <div className="border border-blue-500/30 bg-blue-500/10 rounded-lg p-4">
                <div className="flex items-start gap-3">
                  <div className="text-2xl">💡</div>
                  <div>
                    <h4 className="font-bold text-blue-400 mb-1">Monthly Performance</h4>
                    <p className="text-sm text-muted-foreground">
                      {backtestResult.monthlyReturns.filter(m => m.return > 0).length} out of 12 months were profitable, showing{' '}
                      {backtestResult.monthlyReturns.filter(m => m.return > 0).length >= 8 ? 'excellent' : 'moderate'} consistency.
                    </p>
                  </div>
                </div>
              </div>

              {Math.abs(metrics.maxDrawdown) > 15 && (
                <div className="border border-yellow-500/30 bg-yellow-500/10 rounded-lg p-4">
                  <div className="flex items-start gap-3">
                    <div className="text-2xl">⚠️</div>
                    <div>
                      <h4 className="font-bold text-yellow-400 mb-1">Consider Position Sizing</h4>
                      <p className="text-sm text-muted-foreground">
                        Maximum drawdown of {Math.abs(metrics.maxDrawdown).toFixed(1)}% could be reduced with better position sizing and risk management.
                      </p>
                    </div>
                  </div>
                </div>
              )}

              {metrics.profitFactor > 1.5 && (
                <div className="border border-purple-500/30 bg-purple-500/10 rounded-lg p-4">
                  <div className="flex items-start gap-3">
                    <div className="text-2xl">🎯</div>
                    <div>
                      <h4 className="font-bold text-purple-400 mb-1">Positive Edge Detected</h4>
                      <p className="text-sm text-muted-foreground">
                        Profit factor of {metrics.profitFactor.toFixed(2)} indicates your strategy has a sustainable edge over the market.
                      </p>
                    </div>
                  </div>
                </div>
              )}
            </div>
          </div>
        </>
      )}
    </div>
  )
}
