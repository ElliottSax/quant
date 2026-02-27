'use client'

interface MetricsGridProps {
  totalReturn: number
  sharpeRatio: number
  maxDrawdown: number
  winRate: number
  totalTrades: number
  finalEquity: number
  initialCapital: number
}

export function MetricsGrid({ totalReturn, sharpeRatio, maxDrawdown, winRate, totalTrades, finalEquity, initialCapital }: MetricsGridProps) {
  return (
    <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
      <div className="glass-strong rounded-xl p-6">
        <p className="text-sm text-muted-foreground mb-1">Total Return</p>
        <p className={`text-3xl font-bold ${totalReturn >= 0 ? 'text-gradient-green' : 'text-gradient-red'}`}>
          {totalReturn >= 0 ? '+' : ''}{totalReturn.toFixed(2)}%
        </p>
        <p className="text-xs text-muted-foreground mt-1">
          ${(finalEquity - initialCapital).toLocaleString(undefined, { maximumFractionDigits: 0 })} profit
        </p>
      </div>

      <div className="glass-strong rounded-xl p-6">
        <p className="text-sm text-muted-foreground mb-1">Sharpe Ratio</p>
        <p className="text-3xl font-bold text-gradient-blue">{sharpeRatio.toFixed(2)}</p>
        <p className="text-xs text-blue-400 mt-1">
          {sharpeRatio > 2 ? 'Excellent' : sharpeRatio > 1 ? 'Good' : 'Fair'}
        </p>
      </div>

      <div className="glass-strong rounded-xl p-6">
        <p className="text-sm text-muted-foreground mb-1">Max Drawdown</p>
        <p className="text-3xl font-bold text-gradient-red">{maxDrawdown.toFixed(2)}%</p>
        <p className="text-xs text-red-400 mt-1">
          ${((Math.abs(maxDrawdown) / 100) * initialCapital).toLocaleString(undefined, { maximumFractionDigits: 0 })} max loss
        </p>
      </div>

      <div className="glass-strong rounded-xl p-6">
        <p className="text-sm text-muted-foreground mb-1">Win Rate</p>
        <p className="text-3xl font-bold text-gradient-purple">{winRate.toFixed(1)}%</p>
        <p className="text-xs text-purple-400 mt-1">{totalTrades} total trades</p>
      </div>
    </div>
  )
}
