'use client'

interface RiskMetricsPanelProps {
  sharpeRatio: number
  // Real Sortino from the caller. Null when downside deviation is undefined (no losing
  // periods) — rendered as a dash. It is NOT derivable from Sharpe: this panel used to
  // display sharpeRatio * 1.2, which flatters every strategy because downside deviation
  // is by construction no larger than total deviation.
  sortinoRatio?: number | null
  maxDrawdown: number
  profitFactor: number
  totalReturn: number
  totalTrades: number
  winRate: number
  avgWin: number
  avgLoss: number
}

export function RiskMetricsPanel({
  sharpeRatio, sortinoRatio, maxDrawdown, profitFactor, totalReturn,
  totalTrades, winRate, avgWin, avgLoss,
}: RiskMetricsPanelProps) {
  const expectancy = (winRate / 100 * avgWin) + ((100 - winRate) / 100 * avgLoss)

  return (
    <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
      <div className="glass-strong rounded-xl p-6">
        <h3 className="text-lg font-bold mb-4">Risk Metrics</h3>
        <div className="space-y-3">
          <div className="flex justify-between items-center">
            <span className="text-sm text-muted-foreground">Sharpe Ratio</span>
            <span className="font-bold text-blue-400">{sharpeRatio.toFixed(2)}</span>
          </div>
          <div className="flex justify-between items-center">
            <span className="text-sm text-muted-foreground">Sortino Ratio</span>
            <span className="font-bold text-purple-400">
              {typeof sortinoRatio === 'number' ? sortinoRatio.toFixed(2) : '—'}
            </span>
          </div>
          <div className="flex justify-between items-center">
            <span className="text-sm text-muted-foreground">Calmar Ratio</span>
            <span className="font-bold text-cyan-400">
              {maxDrawdown !== 0 ? (totalReturn / Math.abs(maxDrawdown)).toFixed(2) : 'N/A'}
            </span>
          </div>
          <div className="flex justify-between items-center">
            <span className="text-sm text-muted-foreground">Profit Factor</span>
            <span className="font-bold text-green-400">{profitFactor.toFixed(2)}</span>
          </div>
          <div className="flex justify-between items-center">
            <span className="text-sm text-muted-foreground">Max Drawdown</span>
            <span className="font-bold text-red-400">{maxDrawdown.toFixed(2)}%</span>
          </div>
        </div>
      </div>

      <div className="glass-strong rounded-xl p-6">
        <h3 className="text-lg font-bold mb-4">Trade Statistics</h3>
        <div className="space-y-3">
          <div className="flex justify-between items-center">
            <span className="text-sm text-muted-foreground">Total Trades</span>
            <span className="font-bold">{totalTrades}</span>
          </div>
          <div className="flex justify-between items-center">
            <span className="text-sm text-muted-foreground">Win Rate</span>
            <span className="font-bold text-green-400">{winRate.toFixed(1)}%</span>
          </div>
          <div className="flex justify-between items-center">
            <span className="text-sm text-muted-foreground">Avg Win</span>
            <span className="font-bold text-green-400">+{avgWin.toFixed(2)}%</span>
          </div>
          <div className="flex justify-between items-center">
            <span className="text-sm text-muted-foreground">Avg Loss</span>
            <span className="font-bold text-red-400">{avgLoss.toFixed(2)}%</span>
          </div>
          <div className="flex justify-between items-center">
            <span className="text-sm text-muted-foreground">Expectancy</span>
            <span className="font-bold text-blue-400">{expectancy.toFixed(3)}%</span>
          </div>
        </div>
      </div>
    </div>
  )
}
