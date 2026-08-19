/**
 * Strategy Builder Page
 * Form-based custom strategy creation with live preview and inline backtest results
 *
 * A custom strategy either backtests against real returned data or it fails visibly.
 * No synthetic fallback may be reintroduced here: every number rendered on this page —
 * equity curve, benchmark, trades, volume, win rate — must come from the backtest API
 * response. A simulated equity curve shown in place of a failed run is worse than no
 * result at all, and this page is the sibling of /backtesting, which holds the same line.
 */

'use client'

import { useState } from 'react'
import Link from 'next/link'
import { api } from '@/lib/api-client'
import { BacktestResultView } from '@/components/backtesting'
import { BacktestDataNotes, NoTradesPanel } from '@/components/BacktestDataNotes'
import { saveBacktestResult } from '@/lib/backtest-storage'
import { normalizeBacktest, type NormalizedBacktest } from '@/lib/backtest-normalize'
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

// Monotonic counter rather than Math.random: these ids are React keys, never data, and
// keeping randomness out of this file lets the fabricated-data merge gate stay strict
// (no file-wide allowlist entry that would also excuse an invented market number).
let conditionSeq = 0

function newCondition(): Condition {
  return {
    // React key only — never used as data.
    id: `c${++conditionSeq}`,
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
  const [result, setResult] = useState<NormalizedBacktest | null>(null)
  const [savedId, setSavedId] = useState<string | null>(null)
  const [runError, setRunError] = useState<string | null>(null)

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
    setRunError(null)
    try {
      const backendStrategy = mapToBackendStrategy(entryConditions)
      const apiResult = await api.backtesting.run({
        symbol, start_date: startDate, end_date: endDate,
        strategy: backendStrategy, initial_capital: initialCapital,
        commission: commission / 100, slippage: 0.0005,
      })

      if (!apiResult.equity_curve?.length) {
        throw new Error(
          `No price history was returned for ${symbol} over ${startDate} to ${endDate}.`
        )
      }

      // The backend sends equity_curve as { timestamp, equity } and ships drawdown
      // separately as drawdown_curve; trades carry `pnl`, never `return_pct`. Mapping is
      // in one place (lib/backtest-normalize) so the two run pages cannot drift apart.
      const normalized = normalizeBacktest(
        apiResult.equity_curve,
        (apiResult as any).drawdown_curve,
        apiResult.trades,
        initialCapital
      )

      if (normalized.points.length < 2) {
        throw new Error(
          `The backtest returned ${normalized.points.length} usable equity point(s) for ` +
            `${symbol}. At least two are needed to measure a return.`
        )
      }

      setResult(normalized)
    } catch (err) {
      setResult(null)
      setRunError(
        err instanceof Error && err.message
          ? err.message
          : 'The backtest service could not be reached.'
      )
    } finally {
      setIsRunning(false)
    }
  }

  // Trade statistics exist only when trades were realised. With none, the metrics object
  // holds zeros that measure nothing, so the page shows the no-trades panel instead.
  const hasTradeStats = (result?.trades.rows.length ?? 0) > 0

  const handleSave = () => {
    if (!result || !hasTradeStats) return
    const { metrics, points } = result
    const rows = result.trades.rows
    // One record: the storage module takes a single object, and the history and compare
    // pages read these flat fields off it.
    const id = saveBacktestResult({
      name: `${strategyName} · ${symbol}`,
      symbol,
      strategy: mapToBackendStrategy(entryConditions),
      strategyLabel: strategyName,
      startDate,
      endDate,
      initialCapital,
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
        executions: result.trades.executions,
        winning_trades: rows.filter(t => t.isWin).length,
        losing_trades: rows.filter(t => !t.isWin && t.profit < 0).length,
        avg_win: metrics.avgWin,
        avg_loss: metrics.avgLoss,
        largest_win: Math.max(...rows.map(t => t.profit)),
        largest_loss: Math.min(...rows.map(t => t.profit)),
        return_unit: result.trades.returnUnit,
        drawdown_source: result.drawdownSource,
        start_date: startDate,
        end_date: endDate,
        duration_days: points.length,
        initial_capital: initialCapital,
        final_capital: metrics.finalEquity,
        peak_capital: Math.max(...points.map(p => p.equity)),
        // Stored the way the API sent them, so reopening a saved run re-derives the same
        // figures instead of reading percentages that were never reported.
        trades: rows.map(t => ({
          timestamp: t.date, side: t.side, quantity: t.quantity, price: t.price, pnl: t.profit,
        })),
        equity_curve: points.map(p => ({ timestamp: p.date, equity: p.equity })),
        drawdown_curve: points.map(p => ({ timestamp: p.date, drawdown: Math.abs(p.drawdown) })),
      },
    })
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
              {s.lastBacktestedDate && (
                <div className="text-xs text-gray-400 mb-1">
                  Backtested: {new Date(s.lastBacktestedDate).toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: '2-digit' })}
                </div>
              )}
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
              {s.lastBacktestedDate && (
                <div className="text-xs text-gray-400 mb-1">
                  Backtested: {new Date(s.lastBacktestedDate).toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: '2-digit' })}
                </div>
              )}
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
              {/* Saving stores the run's headline statistics for the history and compare
                  tables. A run with no trades has none to store. */}
              {result && hasTradeStats && (
                <button onClick={handleSave} className="px-4 py-2 text-sm font-medium rounded-lg bg-green-600 text-white hover:bg-green-500 transition-colors">
                  {savedId ? 'Saved!' : 'Save Result'}
                </button>
              )}
              {runError && !result && (
                <span className="text-sm text-red-400">Backtest failed — see below.</span>
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
                      {/* Undefined with no completed trades — a dash, not 0.0%, which
                          would read as "every trade lost". */}
                      <div className="text-sm font-bold text-purple-400">
                        {hasTradeStats ? `${result.metrics.winRate.toFixed(1)}%` : '—'}
                      </div>
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

      {/* Full Results — shown only when the API returned a real curve */}
      {runError && !result && (
        <div className="glass-strong rounded-xl p-12 text-center border border-red-500/30">
          <h3 className="text-2xl font-bold mb-3">This backtest did not run</h3>
          <p className="text-muted-foreground mb-2 max-w-xl mx-auto">{runError}</p>
          <p className="text-sm text-muted-foreground mb-6 max-w-xl mx-auto">
            Your strategy configuration above is unchanged. No results are shown because none
            were produced — this page will never display a simulated equity curve in place of
            a failed run.
          </p>
          <button onClick={runBacktest} className="btn-primary" disabled={isRunning}>
            Try again
          </button>
        </div>
      )}

      {result && !hasTradeStats && (
        <NoTradesPanel
          symbol={symbol}
          startDate={startDate}
          endDate={endDate}
          equityPoints={result.points.length}
          executions={result.trades.executions}
        />
      )}

      {result && hasTradeStats && (
        <div className="space-y-8">
          <BacktestDataNotes
            returnUnit={result.trades.returnUnit}
            drawdownSource={result.drawdownSource}
            executions={result.trades.executions}
            realizedTrades={result.trades.rows.length}
            hasMonthlyReturns={result.chartData.monthlyReturns.length > 0}
            initialCapital={initialCapital}
          />
          <BacktestResultView
            metrics={result.metrics}
            data={result.chartData}
            initialCapital={initialCapital}
            strategy={mapToBackendStrategy(entryConditions)}
            userTier="free"
          />
        </div>
      )}
    </div>
  )
}
