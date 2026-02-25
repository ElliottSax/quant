/**
 * Portfolio Backtesting Page
 *
 * Multi-asset portfolio backtesting with:
 * - Multiple symbol selection (2-20 assets)
 * - 5 optimization methods
 * - Automatic rebalancing
 * - Correlation analysis
 * - Efficient frontier visualization
 */

'use client'

import { useState, useMemo } from 'react'
import dynamic from 'next/dynamic'
import { api } from '@/lib/api-client'
import {
  BarChart,
  Bar,
  LineChart,
  Line,
  ScatterChart,
  Scatter,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
  Cell,
  ZAxis,
} from 'recharts'

// Dynamically import ECharts
const ReactECharts = dynamic(() => import('echarts-for-react'), { ssr: false })

// Popular stock symbols for quick selection
const POPULAR_SYMBOLS = [
  'AAPL', 'MSFT', 'GOOGL', 'AMZN', 'NVDA', 'TSLA', 'META', 'BRK.B',
  'V', 'JPM', 'WMT', 'PG', 'JNJ', 'UNH', 'MA', 'HD', 'DIS', 'NFLX',
  'BAC', 'ADBE', 'CRM', 'COST', 'PEP', 'TMO', 'AVGO', 'MRK', 'ABT', 'CSCO'
]

const OPTIMIZATION_METHODS = [
  { value: 'equal_weight', label: 'Equal Weight', icon: '⚖️', desc: 'Simple 1/N allocation' },
  { value: 'min_variance', label: 'Min Variance', icon: '🛡️', desc: 'Lowest volatility' },
  { value: 'max_sharpe', label: 'Max Sharpe', icon: '📈', desc: 'Best risk-adjusted return' },
  { value: 'risk_parity', label: 'Risk Parity', icon: '🎯', desc: 'Equal risk contribution' },
  { value: 'custom', label: 'Custom Weights', icon: '✏️', desc: 'Manual allocation' },
]

const REBALANCE_FREQUENCIES = [
  { value: 'monthly', label: 'Monthly', desc: 'Rebalance every 30 days (recommended)' },
  { value: 'quarterly', label: 'Quarterly', desc: 'Every 90 days (low turnover)' },
  { value: 'weekly', label: 'Weekly', desc: 'Every 7 days (active)' },
  { value: 'never', label: 'Never', desc: 'Buy and hold' },
]

export default function PortfolioBacktestingPage() {
  // Portfolio configuration
  const [symbols, setSymbols] = useState<string[]>(['AAPL', 'MSFT', 'GOOGL'])
  const [newSymbol, setNewSymbol] = useState('')
  const [weights, setWeights] = useState<Record<string, number>>({})
  const [optimizationMethod, setOptimizationMethod] = useState('equal_weight')
  const [rebalanceFrequency, setRebalanceFrequency] = useState('monthly')
  const [startDate, setStartDate] = useState('2025-01-01')
  const [endDate, setEndDate] = useState('2025-12-31')
  const [initialCapital, setInitialCapital] = useState(100000)

  // Results state
  const [isRunning, setIsRunning] = useState(false)
  const [results, setResults] = useState<any>(null)
  const [error, setError] = useState<string | null>(null)

  // Add symbol
  const addSymbol = () => {
    const sym = newSymbol.trim().toUpperCase()
    if (sym && !symbols.includes(sym) && symbols.length < 20) {
      setSymbols([...symbols, sym])
      setNewSymbol('')

      // Initialize weight
      if (optimizationMethod === 'custom') {
        setWeights({ ...weights, [sym]: 0 })
      }
    }
  }

  // Remove symbol
  const removeSymbol = (symbol: string) => {
    setSymbols(symbols.filter(s => s !== symbol))
    const newWeights = { ...weights }
    delete newWeights[symbol]
    setWeights(newWeights)
  }

  // Update custom weight
  const updateWeight = (symbol: string, value: number) => {
    setWeights({ ...weights, [symbol]: value / 100 })
  }

  // Run portfolio backtest
  const runBacktest = async () => {
    if (symbols.length < 2) {
      setError('Please add at least 2 symbols')
      return
    }

    setIsRunning(true)
    setError(null)

    try {
      const requestWeights = optimizationMethod === 'custom' ? weights : undefined

      const result = await api.backtesting.portfolio.run({
        symbols,
        start_date: new Date(startDate).toISOString(),
        end_date: new Date(endDate).toISOString(),
        weights: requestWeights,
        optimization_method: optimizationMethod,
        initial_capital: initialCapital,
        rebalance_frequency: rebalanceFrequency,
      })

      setResults(result)
    } catch (err: any) {
      setError(err.message || 'Backtest failed')
    } finally {
      setIsRunning(false)
    }
  }

  // Correlation heatmap data
  const correlationHeatmapOption = useMemo(() => {
    if (!results?.correlation_matrix) return {}

    const syms = Object.keys(results.correlation_matrix)
    const data: any[] = []

    syms.forEach((sym1, i) => {
      syms.forEach((sym2, j) => {
        const corr = results.correlation_matrix[sym1][sym2]
        data.push([i, j, corr])
      })
    })

    return {
      backgroundColor: 'transparent',
      tooltip: {
        position: 'top',
        formatter: (params: any) => {
          const sym1 = syms[params.data[0]]
          const sym2 = syms[params.data[1]]
          const corr = params.data[2].toFixed(2)
          return `${sym1} vs ${sym2}<br/>Correlation: <strong>${corr}</strong>`
        }
      },
      grid: {
        height: '60%',
        top: '15%',
        left: '15%',
      },
      xAxis: {
        type: 'category',
        data: syms,
        splitArea: { show: true },
        axisLabel: { color: '#94a3b8', fontSize: 10 }
      },
      yAxis: {
        type: 'category',
        data: syms,
        splitArea: { show: true },
        axisLabel: { color: '#94a3b8', fontSize: 10 }
      },
      visualMap: {
        min: -1,
        max: 1,
        calculable: true,
        orient: 'horizontal',
        left: 'center',
        bottom: '5%',
        inRange: {
          color: ['#ef4444', '#f59e0b', '#84cc16', '#10b981']
        },
        textStyle: { color: '#94a3b8' }
      },
      series: [{
        name: 'Correlation',
        type: 'heatmap',
        data: data,
        label: {
          show: true,
          formatter: (params: any) => params.data[2].toFixed(2),
          fontSize: 10
        },
        emphasis: {
          itemStyle: {
            shadowBlur: 10,
            shadowColor: 'rgba(0, 0, 0, 0.5)'
          }
        }
      }]
    }
  }, [results])

  return (
    <div className="space-y-8">
      {/* Header */}
      <div>
        <h1 className="text-4xl font-bold mb-2 gradient-text">Portfolio Backtesting</h1>
        <p className="text-muted-foreground text-lg">
          Multi-asset portfolio optimization with rebalancing and correlation analysis
        </p>
      </div>

      {/* Configuration */}
      <div className="glass-strong rounded-xl p-6 space-y-6">
        <h2 className="text-xl font-bold">Portfolio Configuration</h2>

        {/* Symbol Selection */}
        <div>
          <label className="text-sm font-semibold text-muted-foreground mb-2 block">
            SYMBOLS ({symbols.length}/20)
          </label>

          {/* Symbol chips */}
          <div className="flex flex-wrap gap-2 mb-3">
            {symbols.map(symbol => (
              <div
                key={symbol}
                className="flex items-center gap-2 px-3 py-1.5 bg-blue-500/20 border border-blue-500/30 rounded-lg"
              >
                <span className="font-mono font-bold text-blue-400">{symbol}</span>
                <button
                  onClick={() => removeSymbol(symbol)}
                  className="text-red-400 hover:text-red-300"
                >
                  ✕
                </button>
              </div>
            ))}
          </div>

          {/* Add symbol */}
          <div className="flex gap-2">
            <input
              type="text"
              value={newSymbol}
              onChange={(e) => setNewSymbol(e.target.value)}
              onKeyPress={(e) => e.key === 'Enter' && addSymbol()}
              placeholder="Enter symbol (e.g., AAPL)"
              className="input-field flex-1 uppercase"
              maxLength={10}
            />
            <button onClick={addSymbol} className="btn-primary px-6">
              Add
            </button>
          </div>

          {/* Quick add popular symbols */}
          <div className="mt-3">
            <p className="text-xs text-muted-foreground mb-2">Quick add:</p>
            <div className="flex flex-wrap gap-1">
              {POPULAR_SYMBOLS.slice(0, 12).map(sym => (
                <button
                  key={sym}
                  onClick={() => {
                    if (!symbols.includes(sym) && symbols.length < 20) {
                      setSymbols([...symbols, sym])
                    }
                  }}
                  className="px-2 py-1 text-xs bg-slate-700 hover:bg-slate-600 rounded transition-colors"
                  disabled={symbols.includes(sym)}
                >
                  {sym}
                </button>
              ))}
            </div>
          </div>
        </div>

        {/* Optimization Method */}
        <div>
          <label className="text-sm font-semibold text-muted-foreground mb-2 block">
            OPTIMIZATION METHOD
          </label>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-3">
            {OPTIMIZATION_METHODS.map(method => (
              <button
                key={method.value}
                onClick={() => setOptimizationMethod(method.value)}
                className={`p-4 rounded-lg border-2 transition-all text-left ${
                  optimizationMethod === method.value
                    ? 'border-blue-500 bg-blue-500/10'
                    : 'border-slate-700 hover:border-slate-600'
                }`}
              >
                <div className="flex items-center gap-2 mb-1">
                  <span className="text-2xl">{method.icon}</span>
                  <span className="font-bold">{method.label}</span>
                </div>
                <p className="text-xs text-muted-foreground">{method.desc}</p>
              </button>
            ))}
          </div>
        </div>

        {/* Custom Weights (if custom method selected) */}
        {optimizationMethod === 'custom' && (
          <div>
            <label className="text-sm font-semibold text-muted-foreground mb-3 block">
              CUSTOM WEIGHTS (must sum to 100%)
            </label>
            <div className="space-y-3">
              {symbols.map(symbol => (
                <div key={symbol} className="flex items-center gap-4">
                  <span className="w-16 font-mono font-bold">{symbol}</span>
                  <input
                    type="range"
                    min="0"
                    max="100"
                    value={(weights[symbol] || 0) * 100}
                    onChange={(e) => updateWeight(symbol, Number(e.target.value))}
                    className="flex-1"
                  />
                  <input
                    type="number"
                    min="0"
                    max="100"
                    value={Math.round((weights[symbol] || 0) * 100)}
                    onChange={(e) => updateWeight(symbol, Number(e.target.value))}
                    className="input-field w-20 text-center"
                  />
                  <span className="text-muted-foreground">%</span>
                </div>
              ))}
              <div className="border-t border-slate-700 pt-3">
                <div className="flex justify-between items-center">
                  <span className="font-semibold">Total:</span>
                  <span className={`text-xl font-bold ${
                    Math.abs(Object.values(weights).reduce((a, b) => a + b, 0) - 1.0) < 0.01
                      ? 'text-green-400'
                      : 'text-red-400'
                  }`}>
                    {(Object.values(weights).reduce((a, b) => a + b, 0) * 100).toFixed(1)}%
                  </span>
                </div>
              </div>
            </div>
          </div>
        )}

        {/* Rebalancing */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div>
            <label className="text-sm font-semibold text-muted-foreground mb-2 block">
              REBALANCING
            </label>
            <select
              value={rebalanceFrequency}
              onChange={(e) => setRebalanceFrequency(e.target.value)}
              className="input-field"
            >
              {REBALANCE_FREQUENCIES.map(freq => (
                <option key={freq.value} value={freq.value}>
                  {freq.label} - {freq.desc}
                </option>
              ))}
            </select>
          </div>

          <div>
            <label className="text-sm font-semibold text-muted-foreground mb-2 block">
              INITIAL CAPITAL
            </label>
            <input
              type="number"
              value={initialCapital}
              onChange={(e) => setInitialCapital(Number(e.target.value))}
              className="input-field"
              min={10000}
              step={10000}
            />
          </div>
        </div>

        {/* Date Range */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div>
            <label className="text-sm font-semibold text-muted-foreground mb-2 block">
              START DATE
            </label>
            <input
              type="date"
              value={startDate}
              onChange={(e) => setStartDate(e.target.value)}
              className="input-field"
            />
          </div>

          <div>
            <label className="text-sm font-semibold text-muted-foreground mb-2 block">
              END DATE
            </label>
            <input
              type="date"
              value={endDate}
              onChange={(e) => setEndDate(e.target.value)}
              className="input-field"
            />
          </div>
        </div>

        {/* Run Button */}
        <button
          onClick={runBacktest}
          className="btn-primary w-full"
          disabled={isRunning || symbols.length < 2}
        >
          {isRunning ? (
            <>
              <span className="inline-block h-4 w-4 animate-spin rounded-full border-2 border-solid border-current border-r-transparent mr-2" />
              Running Portfolio Backtest...
            </>
          ) : (
            '🚀 Run Portfolio Backtest'
          )}
        </button>

        {error && (
          <div className="border border-red-500/30 bg-red-500/10 rounded-lg p-4 text-red-400">
            {error}
          </div>
        )}
      </div>

      {/* Results */}
      {results && (
        <div className="space-y-6">
          {/* Performance Metrics */}
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            <div className="glass-strong rounded-xl p-6">
              <p className="text-sm text-muted-foreground mb-1">Total Return</p>
              <p className={`text-3xl font-bold ${
                results.metrics.total_return >= 0 ? 'text-gradient-green' : 'text-gradient-red'
              }`}>
                {results.metrics.total_return >= 0 ? '+' : ''}{results.metrics.total_return.toFixed(2)}%
              </p>
            </div>

            <div className="glass-strong rounded-xl p-6">
              <p className="text-sm text-muted-foreground mb-1">Sharpe Ratio</p>
              <p className="text-3xl font-bold text-gradient-blue">
                {results.metrics.sharpe_ratio.toFixed(2)}
              </p>
            </div>

            <div className="glass-strong rounded-xl p-6">
              <p className="text-sm text-muted-foreground mb-1">Volatility</p>
              <p className="text-3xl font-bold text-gradient-purple">
                {results.metrics.volatility.toFixed(1)}%
              </p>
            </div>

            <div className="glass-strong rounded-xl p-6">
              <p className="text-sm text-muted-foreground mb-1">Max Drawdown</p>
              <p className="text-3xl font-bold text-gradient-red">
                {results.metrics.max_drawdown.toFixed(2)}%
              </p>
            </div>
          </div>

          {/* Equity Curve */}
          <div className="glass-strong rounded-xl p-6">
            <h2 className="text-2xl font-bold mb-4">Portfolio Equity Curve</h2>
            <ResponsiveContainer width="100%" height={400}>
              <LineChart data={results.equity_curve}>
                <CartesianGrid strokeDasharray="3 3" stroke="#334155" />
                <XAxis
                  dataKey="timestamp"
                  stroke="#94a3b8"
                  tick={{ fontSize: 12 }}
                  tickFormatter={(val) => new Date(val).toLocaleDateString()}
                />
                <YAxis
                  stroke="#94a3b8"
                  tick={{ fontSize: 12 }}
                  tickFormatter={(val) => `$${(val / 1000).toFixed(0)}k`}
                />
                <Tooltip
                  contentStyle={{
                    backgroundColor: '#1e293b',
                    border: '1px solid #334155',
                    borderRadius: '8px',
                  }}
                />
                <Legend />
                <Line
                  type="monotone"
                  dataKey="portfolio_value"
                  stroke="#10b981"
                  strokeWidth={2}
                  dot={false}
                  name="Portfolio Value"
                />
              </LineChart>
            </ResponsiveContainer>
          </div>

          {/* Correlation Heatmap */}
          <div className="glass-strong rounded-xl p-6">
            <h2 className="text-2xl font-bold mb-4">Asset Correlation Matrix</h2>
            <div className="h-[500px]">
              <ReactECharts
                option={correlationHeatmapOption}
                style={{ height: '100%', width: '100%' }}
                opts={{ renderer: 'canvas' }}
              />
            </div>
          </div>

          {/* Individual Asset Performance */}
          <div className="glass-strong rounded-xl p-6">
            <h2 className="text-2xl font-bold mb-4">Individual Asset Returns</h2>
            <ResponsiveContainer width="100%" height={300}>
              <BarChart data={Object.entries(results.individual_returns).map(([symbol, ret]) => ({
                symbol,
                return: ret
              }))}>
                <CartesianGrid strokeDasharray="3 3" stroke="#334155" />
                <XAxis dataKey="symbol" stroke="#94a3b8" />
                <YAxis stroke="#94a3b8" tickFormatter={(val) => `${val}%`} />
                <Tooltip
                  contentStyle={{
                    backgroundColor: '#1e293b',
                    border: '1px solid #334155',
                    borderRadius: '8px',
                  }}
                  formatter={(value: any) => `${value.toFixed(2)}%`}
                />
                <Bar dataKey="return" name="Return %">
                  {Object.entries(results.individual_returns).map(([_, ret], index) => (
                    <Cell key={`cell-${index}`} fill={(ret as number) >= 0 ? '#10b981' : '#ef4444'} />
                  ))}
                </Bar>
              </BarChart>
            </ResponsiveContainer>
          </div>

          {/* Portfolio Metrics Summary */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div className="glass-strong rounded-xl p-6">
              <h3 className="text-lg font-bold mb-4">Risk Metrics</h3>
              <div className="space-y-3">
                <div className="flex justify-between">
                  <span className="text-muted-foreground">Sharpe Ratio</span>
                  <span className="font-bold text-blue-400">{results.metrics.sharpe_ratio.toFixed(2)}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-muted-foreground">Sortino Ratio</span>
                  <span className="font-bold text-purple-400">{results.metrics.sortino_ratio.toFixed(2)}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-muted-foreground">Volatility</span>
                  <span className="font-bold text-yellow-400">{results.metrics.volatility.toFixed(2)}%</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-muted-foreground">Max Drawdown</span>
                  <span className="font-bold text-red-400">{results.metrics.max_drawdown.toFixed(2)}%</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-muted-foreground">Avg Correlation</span>
                  <span className="font-bold text-cyan-400">{results.metrics.avg_correlation.toFixed(3)}</span>
                </div>
              </div>
            </div>

            <div className="glass-strong rounded-xl p-6">
              <h3 className="text-lg font-bold mb-4">Portfolio Info</h3>
              <div className="space-y-3">
                <div className="flex justify-between">
                  <span className="text-muted-foreground">Total Assets</span>
                  <span className="font-bold">{results.symbol_list.length}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-muted-foreground">Rebalances</span>
                  <span className="font-bold">{results.metrics.num_rebalances}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-muted-foreground">Turnover (Annual)</span>
                  <span className="font-bold">{results.metrics.turnover.toFixed(2)}x</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-muted-foreground">Best Asset</span>
                  <span className="font-bold text-green-400">{results.metrics.best_asset}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-muted-foreground">Worst Asset</span>
                  <span className="font-bold text-red-400">{results.metrics.worst_asset}</span>
                </div>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}
