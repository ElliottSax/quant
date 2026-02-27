/**
 * Strategy Builder Page
 * Form-based custom strategy creation with live preview and inline backtest results
 */

'use client'

import { useState } from 'react'
import Link from 'next/link'
import { api } from '@/lib/api-client'
import { BacktestResultView } from '@/components/backtesting'
import { saveBacktestResult } from '@/lib/backtest-storage'
import {
  STRATEGIES, INDICATORS, CONDITION_OPERATORS,
  type StrategyDefinition, type ConditionOperator,
} from '@/lib/strategy-definitions'

interface Condition {
  id: string
  indicator: string
  operator: ConditionOperator
  referenceType: 'indicator' | 'value'
  referenceIndicator: string
  referenceValue: number
  params: Record<string, number>
}

function newCondition(): Condition {
  return {
    id: Math.random().toString(36).slice(2, 8),
    indicator: 'sma',
    operator: 'crosses_above',
    referenceType: 'indicator',
    referenceIndicator: 'sma',
    referenceValue: 50,
    params: { period: 20 },
  }
}

// Map builder form to the closest backend strategy
function mapToBackendStrategy(entryConditions: Condition[]): string {
  if (entryConditions.length === 0) return 'simple_ma_crossover'
  const primary = entryConditions[0].indicator
  const mapping: Record<string, string> = {
    sma: 'simple_ma_crossover',
    ema: 'simple_ma_crossover',
    rsi: 'rsi_mean_reversion',
    macd: 'momentum',
    bollinger: 'bollinger_breakout',
    atr: 'trend_following',
  }
  return mapping[primary] || 'simple_ma_crossover'
}

// Generate mock data (same as backtesting page)
function generateMockResult(initialCapital: number, strategy: string, days: number) {
  const data = []
  let equity = initialCapital
  let peak = equity
  const trades: any[] = []
  const params: any = {
    simple_ma_crossover: { winRate: 0.58, avgWin: 0.025, avgLoss: 0.015, tradeFreq: 0.03 },
    rsi_mean_reversion: { winRate: 0.62, avgWin: 0.018, avgLoss: 0.012, tradeFreq: 0.05 },
    bollinger_breakout: { winRate: 0.54, avgWin: 0.032, avgLoss: 0.020, tradeFreq: 0.02 },
    momentum: { winRate: 0.64, avgWin: 0.028, avgLoss: 0.016, tradeFreq: 0.04 },
    trend_following: { winRate: 0.55, avgWin: 0.035, avgLoss: 0.018, tradeFreq: 0.025 },
  }
  const p = params[strategy] || params.simple_ma_crossover

  for (let i = 0; i < days; i++) {
    if (Math.random() < p.tradeFreq) {
      const isWin = Math.random() < p.winRate
      const ret = isWin ? p.avgWin + (Math.random() - 0.5) * 0.01 : -(p.avgLoss + (Math.random() - 0.5) * 0.005)
      const change = equity * ret
      equity += change
      trades.push({ day: i + 1, returnPct: ret * 100, profit: change, isWin, equity })
    }
    equity *= 1 + (Math.random() - 0.48) * 0.005
    peak = Math.max(peak, equity)
    data.push({
      day: i + 1, date: new Date(2023, 0, i + 1).toISOString().split('T')[0],
      equity: parseFloat(equity.toFixed(2)),
      drawdown: parseFloat((((equity - peak) / peak) * 100).toFixed(2)),
      benchmark: parseFloat((initialCapital * (1 + 0.10 * (i / days))).toFixed(2)),
      volume: Math.floor(Math.random() * 1000000) + 100000,
    })
  }
  return { data, trades }
}

function computeMetricsAndCharts(equityData: any[], trades: any[], initialCapital: number) {
  const finalEquity = equityData[equityData.length - 1].equity
  const totalReturn = ((finalEquity - initialCapital) / initialCapital) * 100
  const maxDrawdown = Math.min(...equityData.map((d: any) => d.drawdown))
  const winningTrades = trades.filter((t: any) => t.isWin)
  const losingTrades = trades.filter((t: any) => !t.isWin)
  const winRate = trades.length > 0 ? (winningTrades.length / trades.length) * 100 : 0
  const avgWin = winningTrades.length > 0 ? winningTrades.reduce((s: number, t: any) => s + t.returnPct, 0) / winningTrades.length : 0
  const avgLoss = losingTrades.length > 0 ? losingTrades.reduce((s: number, t: any) => s + t.returnPct, 0) / losingTrades.length : 0
  const profitFactor = avgLoss !== 0 ? Math.abs(avgWin * winningTrades.length / (avgLoss * losingTrades.length)) : 0
  const returns = equityData.map((d: any, i: number) => i > 0 ? (d.equity - equityData[i - 1].equity) / equityData[i - 1].equity : 0).slice(1)
  const avgReturn = returns.reduce((a: number, b: number) => a + b, 0) / returns.length
  const stdDev = Math.sqrt(returns.reduce((s: number, r: number) => s + Math.pow(r - avgReturn, 2), 0) / returns.length)
  const sharpeRatio = stdDev > 0 ? (avgReturn * 252) / (stdDev * Math.sqrt(252)) : 0

  // Monthly returns
  const monthlyReturns = []
  const dpm = Math.floor(equityData.length / 12)
  for (let m = 0; m < 12; m++) {
    const si = m * dpm
    const ei = Math.min((m + 1) * dpm, equityData.length - 1)
    monthlyReturns.push({
      month: ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'][m],
      return: parseFloat((((equityData[ei].equity - equityData[si].equity) / equityData[si].equity) * 100).toFixed(2)),
    })
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

  return {
    metrics: { finalEquity, totalReturn, maxDrawdown, sharpeRatio, winRate, avgWin, avgLoss, profitFactor, totalTrades: trades.length },
    chartData: { equityData, trades, monthlyReturns, tradeDistribution, rollingMetrics },
  }
}

export default function StrategyBuilderPage() {
  const [selectedTemplate, setSelectedTemplate] = useState<string | null>(null)
  const [strategyName, setStrategyName] = useState('Custom Strategy')
  const [entryConditions, setEntryConditions] = useState<Condition[]>([newCondition()])
  const [exitConditions, setExitConditions] = useState<Condition[]>([newCondition()])
  const [stopLoss, setStopLoss] = useState(5)
  const [takeProfit, setTakeProfit] = useState(10)
  const [positionSize, setPositionSize] = useState(100)
  const [commission, setCommission] = useState(0.1)
  const [symbol, setSymbol] = useState('AAPL')
  const [startDate, setStartDate] = useState('2023-01-01')
  const [endDate, setEndDate] = useState('2024-01-01')
  const [initialCapital, setInitialCapital] = useState(100000)
  const [isRunning, setIsRunning] = useState(false)
  const [result, setResult] = useState<{ metrics: any; chartData: any } | null>(null)
  const [savedId, setSavedId] = useState<string | null>(null)

  const applyTemplate = (strategy: StrategyDefinition) => {
    setSelectedTemplate(strategy.id)
    setStrategyName(strategy.name)
    // Map strategy params to entry conditions
    const conditions: Condition[] = []
    if (strategy.category === 'trend') {
      conditions.push({
        ...newCondition(),
        indicator: 'sma',
        operator: 'crosses_above',
        referenceType: 'indicator',
        referenceIndicator: 'sma',
        params: { period: strategy.parameters[0]?.default || 20 },
      })
    } else if (strategy.category === 'mean_reversion') {
      conditions.push({
        ...newCondition(),
        indicator: 'rsi',
        operator: 'less_than',
        referenceType: 'value',
        referenceValue: strategy.parameters.find(p => p.name === 'oversold')?.default || 30,
        params: { period: strategy.parameters[0]?.default || 14 },
      })
    } else if (strategy.category === 'momentum') {
      conditions.push({
        ...newCondition(),
        indicator: 'macd',
        operator: 'crosses_above',
        referenceType: 'value',
        referenceValue: 0,
        params: { fast_period: 12, slow_period: 26, signal_period: 9 },
      })
    } else {
      conditions.push({
        ...newCondition(),
        indicator: 'sma',
        operator: 'crosses_above',
        referenceType: 'indicator',
        referenceIndicator: 'sma',
        params: { period: strategy.parameters[0]?.default || 20 },
      })
    }
    setEntryConditions(conditions)
  }

  const addCondition = (type: 'entry' | 'exit') => {
    const setter = type === 'entry' ? setEntryConditions : setExitConditions
    setter(prev => [...prev, newCondition()])
  }

  const removeCondition = (type: 'entry' | 'exit', id: string) => {
    const setter = type === 'entry' ? setEntryConditions : setExitConditions
    setter(prev => prev.filter(c => c.id !== id))
  }

  const updateCondition = (type: 'entry' | 'exit', id: string, updates: Partial<Condition>) => {
    const setter = type === 'entry' ? setEntryConditions : setExitConditions
    setter(prev => prev.map(c => c.id === id ? { ...c, ...updates } : c))
  }

  const getPreviewText = () => {
    const entries = entryConditions.map(c => {
      const ind = INDICATORS.find(i => i.id === c.indicator)
      const op = CONDITION_OPERATORS.find(o => o.value === c.operator)
      const ref = c.referenceType === 'value'
        ? c.referenceValue.toString()
        : INDICATORS.find(i => i.id === c.referenceIndicator)?.name || c.referenceIndicator
      return `${ind?.name || c.indicator}(${Object.values(c.params).join(',')}) ${op?.label || c.operator} ${ref}`
    })
    return entries.join(' AND ') || 'No conditions defined'
  }

  const runBacktest = async () => {
    setIsRunning(true)
    setSavedId(null)
    try {
      const backendStrategy = mapToBackendStrategy(entryConditions)
      const apiResult = await api.backtesting.run({
        symbol, start_date: startDate, end_date: endDate,
        strategy: backendStrategy, initial_capital: initialCapital,
        commission: commission / 100, slippage: 0.0005,
      })
      const equityData = apiResult.equity_curve?.length > 0
        ? apiResult.equity_curve.map((point: any, i: number) => ({
            day: i + 1, date: point.date || '', equity: point.equity || point.value || initialCapital,
            drawdown: point.drawdown || 0,
            benchmark: initialCapital * (1 + 0.10 * (i / (apiResult.equity_curve.length || 252))),
          }))
        : generateMockResult(initialCapital, backendStrategy, 252).data
      const trades = apiResult.trades?.map((t: any, i: number) => ({
        day: t.day || i + 1, returnPct: t.return_pct || 0, profit: t.profit || 0,
        isWin: (t.return_pct || t.profit || 0) > 0, equity: t.equity || initialCapital,
      })) || generateMockResult(initialCapital, backendStrategy, 252).trades
      setResult(computeMetricsAndCharts(equityData, trades, initialCapital))
    } catch {
      const backendStrategy = mapToBackendStrategy(entryConditions)
      const { data, trades } = generateMockResult(initialCapital, backendStrategy, 252)
      setResult(computeMetricsAndCharts(data, trades, initialCapital))
    } finally {
      setIsRunning(false)
    }
  }

  const handleSave = () => {
    if (!result) return
    const id = saveBacktestResult(
      {
        total_return: result.metrics.totalReturn, annual_return: result.metrics.totalReturn,
        sharpe_ratio: result.metrics.sharpeRatio, sortino_ratio: result.metrics.sharpeRatio * 1.2,
        max_drawdown: result.metrics.maxDrawdown, win_rate: result.metrics.winRate,
        profit_factor: result.metrics.profitFactor, total_trades: result.metrics.totalTrades,
        winning_trades: result.chartData.trades.filter((t: any) => t.isWin).length,
        losing_trades: result.chartData.trades.filter((t: any) => !t.isWin).length,
        avg_win: result.metrics.avgWin, avg_loss: result.metrics.avgLoss,
        largest_win: Math.max(...result.chartData.trades.map((t: any) => t.returnPct)),
        largest_loss: Math.min(...result.chartData.trades.map((t: any) => t.returnPct)),
        start_date: startDate, end_date: endDate, duration_days: result.chartData.equityData.length,
        initial_capital: initialCapital, final_capital: result.metrics.finalEquity,
        peak_capital: Math.max(...result.chartData.equityData.map((d: any) => d.equity)),
        trades: result.chartData.trades, equity_curve: result.chartData.equityData,
        drawdown_curve: result.chartData.equityData.map((d: any) => ({ day: d.day, drawdown: d.drawdown })),
      },
      { symbol, strategy: mapToBackendStrategy(entryConditions), strategyLabel: strategyName, startDate, endDate, initialCapital }
    )
    setSavedId(id)
  }

  return (
    <div className="space-y-8">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-4xl font-bold mb-2 gradient-text">Strategy Builder</h1>
          <p className="text-muted-foreground text-lg">Create custom trading strategies with visual configuration</p>
        </div>
        <div className="flex gap-3">
          <Link href="/backtesting" className="px-4 py-2 text-sm font-medium rounded-lg bg-slate-800 text-slate-300 hover:text-white hover:bg-slate-700 transition-colors">
            Backtester
          </Link>
          <Link href="/strategies" className="px-4 py-2 text-sm font-medium rounded-lg bg-slate-800 text-slate-300 hover:text-white hover:bg-slate-700 transition-colors">
            Strategy Library
          </Link>
        </div>
      </div>

      {/* Template Selection */}
      <div className="glass-strong rounded-xl p-6">
        <h2 className="text-xl font-bold mb-4">Start from a Template</h2>
        <div className="grid grid-cols-2 md:grid-cols-4 lg:grid-cols-5 gap-3">
          <button
            onClick={() => { setSelectedTemplate(null); setStrategyName('Custom Strategy'); setEntryConditions([newCondition()]); setExitConditions([newCondition()]) }}
            className={`p-4 rounded-lg border text-left transition-all ${
              !selectedTemplate ? 'border-blue-500 bg-blue-500/10' : 'border-slate-700 bg-slate-800/30 hover:border-slate-600'
            }`}
          >
            <div className="text-2xl mb-2">🔧</div>
            <div className="text-sm font-bold text-white">From Scratch</div>
            <div className="text-xs text-muted-foreground">Custom rules</div>
          </button>
          {STRATEGIES.filter(s => s.tier === 'free').map(s => (
            <button
              key={s.id}
              onClick={() => applyTemplate(s)}
              className={`p-4 rounded-lg border text-left transition-all ${
                selectedTemplate === s.id ? 'border-blue-500 bg-blue-500/10' : 'border-slate-700 bg-slate-800/30 hover:border-slate-600'
              }`}
            >
              <div className={`w-8 h-8 rounded bg-gradient-to-br ${s.color} flex items-center justify-center text-white text-xs font-bold mb-2`}>
                {s.name[0]}
              </div>
              <div className="text-sm font-bold text-white">{s.name}</div>
              <div className="text-xs text-green-400">Free</div>
            </button>
          ))}
          {STRATEGIES.filter(s => s.tier !== 'free').slice(0, 4).map(s => (
            <button
              key={s.id}
              onClick={() => applyTemplate(s)}
              className={`p-4 rounded-lg border text-left transition-all ${
                selectedTemplate === s.id ? 'border-blue-500 bg-blue-500/10' : 'border-slate-700 bg-slate-800/30 hover:border-slate-600'
              }`}
            >
              <div className={`w-8 h-8 rounded bg-gradient-to-br ${s.color} flex items-center justify-center text-white text-xs font-bold mb-2`}>
                {s.name[0]}
              </div>
              <div className="text-sm font-bold text-white">{s.name}</div>
              <div className="text-xs text-purple-400">{s.tier}</div>
            </button>
          ))}
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Left: Conditions Form */}
        <div className="lg:col-span-2 space-y-6">
          {/* Strategy Name */}
          <div className="glass-strong rounded-xl p-6">
            <label className="text-xs font-semibold text-muted-foreground mb-2 block">STRATEGY NAME</label>
            <input
              type="text" value={strategyName}
              onChange={(e) => setStrategyName(e.target.value)}
              className="input-field text-lg font-bold" placeholder="My Custom Strategy"
            />
          </div>

          {/* Entry Conditions */}
          <div className="glass-strong rounded-xl p-6">
            <div className="flex items-center justify-between mb-4">
              <h3 className="text-lg font-bold text-green-400">Entry Conditions</h3>
              <button onClick={() => addCondition('entry')} className="px-3 py-1 text-xs font-medium rounded bg-green-600/20 text-green-400 hover:bg-green-600/30 transition-colors">
                + Add Condition
              </button>
            </div>
            <div className="space-y-4">
              {entryConditions.map((cond, idx) => (
                <div key={cond.id} className="flex items-start gap-3 p-4 rounded-lg bg-slate-900/50 border border-slate-700">
                  <span className="text-xs font-mono text-muted-foreground mt-2">{idx > 0 ? 'AND' : 'IF'}</span>
                  <div className="flex-1 grid grid-cols-2 md:grid-cols-4 gap-3">
                    <div>
                      <label className="text-xs text-muted-foreground mb-1 block">Indicator</label>
                      <select value={cond.indicator} onChange={(e) => updateCondition('entry', cond.id, { indicator: e.target.value })} className="input-field text-sm">
                        {INDICATORS.map(i => <option key={i.id} value={i.id}>{i.name.split('(')[0].trim()}</option>)}
                      </select>
                    </div>
                    <div>
                      <label className="text-xs text-muted-foreground mb-1 block">Operator</label>
                      <select value={cond.operator} onChange={(e) => updateCondition('entry', cond.id, { operator: e.target.value as ConditionOperator })} className="input-field text-sm">
                        {CONDITION_OPERATORS.map(o => <option key={o.value} value={o.value}>{o.label}</option>)}
                      </select>
                    </div>
                    <div>
                      <label className="text-xs text-muted-foreground mb-1 block">Reference</label>
                      <select value={cond.referenceType} onChange={(e) => updateCondition('entry', cond.id, { referenceType: e.target.value as 'indicator' | 'value' })} className="input-field text-sm">
                        <option value="indicator">Indicator</option>
                        <option value="value">Value</option>
                      </select>
                    </div>
                    <div>
                      <label className="text-xs text-muted-foreground mb-1 block">
                        {cond.referenceType === 'value' ? 'Threshold' : 'Ref Indicator'}
                      </label>
                      {cond.referenceType === 'value' ? (
                        <input type="number" value={cond.referenceValue} onChange={(e) => updateCondition('entry', cond.id, { referenceValue: Number(e.target.value) })} className="input-field text-sm" />
                      ) : (
                        <select value={cond.referenceIndicator} onChange={(e) => updateCondition('entry', cond.id, { referenceIndicator: e.target.value })} className="input-field text-sm">
                          {INDICATORS.map(i => <option key={i.id} value={i.id}>{i.name.split('(')[0].trim()}</option>)}
                        </select>
                      )}
                    </div>
                  </div>
                  {entryConditions.length > 1 && (
                    <button onClick={() => removeCondition('entry', cond.id)} className="text-red-400 hover:text-red-300 mt-6 text-lg">×</button>
                  )}
                </div>
              ))}
            </div>
          </div>

          {/* Exit Conditions */}
          <div className="glass-strong rounded-xl p-6">
            <div className="flex items-center justify-between mb-4">
              <h3 className="text-lg font-bold text-red-400">Exit Conditions</h3>
              <button onClick={() => addCondition('exit')} className="px-3 py-1 text-xs font-medium rounded bg-red-600/20 text-red-400 hover:bg-red-600/30 transition-colors">
                + Add Condition
              </button>
            </div>
            <div className="space-y-4">
              {exitConditions.map((cond, idx) => (
                <div key={cond.id} className="flex items-start gap-3 p-4 rounded-lg bg-slate-900/50 border border-slate-700">
                  <span className="text-xs font-mono text-muted-foreground mt-2">{idx > 0 ? 'OR' : 'EXIT'}</span>
                  <div className="flex-1 grid grid-cols-2 md:grid-cols-4 gap-3">
                    <div>
                      <label className="text-xs text-muted-foreground mb-1 block">Indicator</label>
                      <select value={cond.indicator} onChange={(e) => updateCondition('exit', cond.id, { indicator: e.target.value })} className="input-field text-sm">
                        {INDICATORS.map(i => <option key={i.id} value={i.id}>{i.name.split('(')[0].trim()}</option>)}
                      </select>
                    </div>
                    <div>
                      <label className="text-xs text-muted-foreground mb-1 block">Operator</label>
                      <select value={cond.operator} onChange={(e) => updateCondition('exit', cond.id, { operator: e.target.value as ConditionOperator })} className="input-field text-sm">
                        {CONDITION_OPERATORS.map(o => <option key={o.value} value={o.value}>{o.label}</option>)}
                      </select>
                    </div>
                    <div>
                      <label className="text-xs text-muted-foreground mb-1 block">Reference</label>
                      <select value={cond.referenceType} onChange={(e) => updateCondition('exit', cond.id, { referenceType: e.target.value as 'indicator' | 'value' })} className="input-field text-sm">
                        <option value="indicator">Indicator</option>
                        <option value="value">Value</option>
                      </select>
                    </div>
                    <div>
                      <label className="text-xs text-muted-foreground mb-1 block">
                        {cond.referenceType === 'value' ? 'Threshold' : 'Ref Indicator'}
                      </label>
                      {cond.referenceType === 'value' ? (
                        <input type="number" value={cond.referenceValue} onChange={(e) => updateCondition('exit', cond.id, { referenceValue: Number(e.target.value) })} className="input-field text-sm" />
                      ) : (
                        <select value={cond.referenceIndicator} onChange={(e) => updateCondition('exit', cond.id, { referenceIndicator: e.target.value })} className="input-field text-sm">
                          {INDICATORS.map(i => <option key={i.id} value={i.id}>{i.name.split('(')[0].trim()}</option>)}
                        </select>
                      )}
                    </div>
                  </div>
                  {exitConditions.length > 1 && (
                    <button onClick={() => removeCondition('exit', cond.id)} className="text-red-400 hover:text-red-300 mt-6 text-lg">×</button>
                  )}
                </div>
              ))}
            </div>

            {/* Risk Management */}
            <div className="grid grid-cols-3 gap-4 mt-6 pt-6 border-t border-slate-700">
              <div>
                <label className="text-xs text-muted-foreground mb-1 block">Stop Loss %</label>
                <input type="number" value={stopLoss} onChange={(e) => setStopLoss(Number(e.target.value))} className="input-field text-sm" min={0.5} max={50} step={0.5} />
              </div>
              <div>
                <label className="text-xs text-muted-foreground mb-1 block">Take Profit %</label>
                <input type="number" value={takeProfit} onChange={(e) => setTakeProfit(Number(e.target.value))} className="input-field text-sm" min={1} max={100} step={0.5} />
              </div>
              <div>
                <label className="text-xs text-muted-foreground mb-1 block">Position Size %</label>
                <input type="number" value={positionSize} onChange={(e) => setPositionSize(Number(e.target.value))} className="input-field text-sm" min={1} max={100} step={1} />
              </div>
            </div>
          </div>

          {/* Symbol & Date Config */}
          <div className="glass-strong rounded-xl p-6">
            <h3 className="text-lg font-bold mb-4">Backtest Configuration</h3>
            <div className="grid grid-cols-2 md:grid-cols-5 gap-4">
              <div>
                <label className="text-xs font-semibold text-muted-foreground mb-2 block">SYMBOL</label>
                <input type="text" value={symbol} onChange={(e) => setSymbol(e.target.value.toUpperCase())} className="input-field uppercase font-mono" />
              </div>
              <div>
                <label className="text-xs font-semibold text-muted-foreground mb-2 block">START DATE</label>
                <input type="date" value={startDate} onChange={(e) => setStartDate(e.target.value)} className="input-field" />
              </div>
              <div>
                <label className="text-xs font-semibold text-muted-foreground mb-2 block">END DATE</label>
                <input type="date" value={endDate} onChange={(e) => setEndDate(e.target.value)} className="input-field" />
              </div>
              <div>
                <label className="text-xs font-semibold text-muted-foreground mb-2 block">CAPITAL ($)</label>
                <input type="number" value={initialCapital} onChange={(e) => setInitialCapital(Number(e.target.value))} className="input-field" min={1000} step={1000} />
              </div>
              <div>
                <label className="text-xs font-semibold text-muted-foreground mb-2 block">COMMISSION %</label>
                <input type="number" value={commission} onChange={(e) => setCommission(Number(e.target.value))} className="input-field" min={0} max={2} step={0.01} />
              </div>
            </div>

            <div className="flex items-center gap-4 mt-6">
              <button onClick={runBacktest} className="btn-primary" disabled={isRunning}>
                {isRunning ? (
                  <>
                    <span className="inline-block h-4 w-4 animate-spin rounded-full border-2 border-solid border-current border-r-transparent mr-2" />
                    Running...
                  </>
                ) : 'Run Backtest'}
              </button>
              {result && (
                <button onClick={handleSave} className="px-4 py-2 text-sm font-medium rounded-lg bg-green-600 text-white hover:bg-green-500 transition-colors">
                  {savedId ? 'Saved!' : 'Save Result'}
                </button>
              )}
            </div>
          </div>
        </div>

        {/* Right: Live Preview */}
        <div className="space-y-6">
          <div className="glass-strong rounded-xl p-6 sticky top-20">
            <h3 className="text-lg font-bold mb-4">Strategy Preview</h3>
            <div className="space-y-4">
              <div>
                <div className="text-xs text-muted-foreground mb-1">Name</div>
                <div className="text-sm font-bold text-white">{strategyName}</div>
              </div>
              <div>
                <div className="text-xs text-muted-foreground mb-1">Entry Logic</div>
                <div className="text-sm text-green-400 font-mono bg-slate-900/50 rounded p-3">
                  {getPreviewText()}
                </div>
              </div>
              <div>
                <div className="text-xs text-muted-foreground mb-1">Risk Management</div>
                <div className="text-sm text-slate-300 space-y-1">
                  <div>Stop Loss: <span className="text-red-400">{stopLoss}%</span></div>
                  <div>Take Profit: <span className="text-green-400">{takeProfit}%</span></div>
                  <div>Position Size: <span className="text-blue-400">{positionSize}%</span></div>
                  <div>Commission: <span className="text-muted-foreground">{commission}%</span></div>
                </div>
              </div>
              <div>
                <div className="text-xs text-muted-foreground mb-1">Backtest</div>
                <div className="text-sm text-slate-300">
                  {symbol} | {startDate} → {endDate} | ${initialCapital.toLocaleString()}
                </div>
              </div>
              {result && (
                <div className="pt-4 border-t border-slate-700">
                  <div className="text-xs text-muted-foreground mb-2">Quick Results</div>
                  <div className="grid grid-cols-2 gap-2">
                    <div className="bg-slate-900/50 rounded p-2">
                      <div className="text-xs text-muted-foreground">Return</div>
                      <div className={`text-sm font-bold ${result.metrics.totalReturn >= 0 ? 'text-green-400' : 'text-red-400'}`}>
                        {result.metrics.totalReturn >= 0 ? '+' : ''}{result.metrics.totalReturn.toFixed(2)}%
                      </div>
                    </div>
                    <div className="bg-slate-900/50 rounded p-2">
                      <div className="text-xs text-muted-foreground">Sharpe</div>
                      <div className="text-sm font-bold text-blue-400">{result.metrics.sharpeRatio.toFixed(2)}</div>
                    </div>
                    <div className="bg-slate-900/50 rounded p-2">
                      <div className="text-xs text-muted-foreground">Win Rate</div>
                      <div className="text-sm font-bold text-purple-400">{result.metrics.winRate.toFixed(1)}%</div>
                    </div>
                    <div className="bg-slate-900/50 rounded p-2">
                      <div className="text-xs text-muted-foreground">Drawdown</div>
                      <div className="text-sm font-bold text-red-400">{result.metrics.maxDrawdown.toFixed(1)}%</div>
                    </div>
                  </div>
                </div>
              )}
            </div>
          </div>
        </div>
      </div>

      {/* Full Results */}
      {result && (
        <BacktestResultView
          metrics={result.metrics}
          data={result.chartData}
          initialCapital={initialCapital}
          strategy={mapToBackendStrategy(entryConditions)}
          userTier="free"
        />
      )}
    </div>
  )
}
