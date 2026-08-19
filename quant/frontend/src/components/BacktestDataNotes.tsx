'use client'

import type { TradeReturnUnit } from '@/lib/backtest-normalize'

interface BacktestDataNotesProps {
  returnUnit: TradeReturnUnit
  drawdownSource: 'reported' | 'derived'
  executions: number
  realizedTrades: number
  hasMonthlyReturns: boolean
  initialCapital: number
}

/**
 * States, in the reader's view, which figures below are reported by the backtest and
 * which are transforms of them — and which charts are empty because the run does not
 * carry the measurement they need. Charts that cannot be drawn are left blank and
 * explained here rather than filled with placeholder zeros.
 */
export function BacktestDataNotes({
  returnUnit,
  drawdownSource,
  executions,
  realizedTrades,
  hasMonthlyReturns,
  initialCapital,
}: BacktestDataNotesProps) {
  const notes: string[] = []

  if (returnUnit === 'share_of_initial_capital') {
    notes.push(
      `Per-trade returns are each trade's realised profit or loss as a share of the ` +
        `$${initialCapital.toLocaleString()} starting capital. The backtest reports trade P&L in ` +
        `dollars and no per-trade percentage, so the "Return %" axis, average win/loss and ` +
        `expectancy below are in those units — not per-trade returns on position size.`
    )
  }

  if (drawdownSource === 'derived') {
    notes.push(
      'Drawdown was recomputed from the returned equity curve because the run reported no ' +
        'drawdown series. It is measured from the equity shown, not supplied separately.'
    )
  }

  if (executions > realizedTrades) {
    notes.push(
      `${executions} fills were returned; ${realizedTrades} carry a realised profit or loss. ` +
        'Opening legs have no outcome yet and are excluded from the win rate and trade counts.'
    )
  }

  if (!hasMonthlyReturns) {
    notes.push(
      'Monthly returns are blank: the returned equity points carry no dates, so the months ' +
        'they fall in are unknown. Twelve Jan–Dec bars would name months this run never covered.'
    )
  }

  if (notes.length === 0) return null

  return (
    <div className="glass rounded-xl p-5 border border-slate-700">
      <h3 className="text-sm font-semibold text-slate-200 mb-2">How to read these numbers</h3>
      <ul className="space-y-2">
        {notes.map((note) => (
          <li key={note} className="text-xs text-muted-foreground leading-relaxed">
            {note}
          </li>
        ))}
      </ul>
    </div>
  )
}

interface NoTradesPanelProps {
  symbol: string
  startDate: string
  endDate: string
  equityPoints: number
  executions: number
}

/**
 * A strategy that fires no signals is a legitimate outcome, and the honest rendering of
 * it is this panel — not a win rate of NaN%, not zeros standing in for statistics that
 * are undefined when there are no trades to measure.
 */
export function NoTradesPanel({
  symbol,
  startDate,
  endDate,
  equityPoints,
  executions,
}: NoTradesPanelProps) {
  return (
    <div className="glass-strong rounded-xl p-12 text-center border border-amber-500/30">
      <h3 className="text-2xl font-bold mb-3">No trades were generated in this window</h3>
      <p className="text-muted-foreground mb-2 max-w-xl mx-auto">
        The backtest ran over {equityPoints.toLocaleString()} price points for {symbol} between{' '}
        {startDate} and {endDate}
        {executions > 0
          ? `, and returned ${executions} fill${executions === 1 ? '' : 's'} with no realised profit or loss.`
          : ', and the strategy never met its entry conditions.'}
      </p>
      <p className="text-sm text-muted-foreground max-w-xl mx-auto">
        Win rate, average win and loss, profit factor and expectancy are undefined with no
        completed trades, so they are not shown. Capital stayed at its starting value. Try a
        different symbol, a longer window, or looser entry conditions.
      </p>
    </div>
  )
}
