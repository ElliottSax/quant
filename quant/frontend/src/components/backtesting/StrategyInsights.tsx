'use client'

interface StrategyInsightsProps {
  sharpeRatio: number
  maxDrawdown: number
  profitFactor: number
  profitableMonths: number
}

export function StrategyInsights({ sharpeRatio, maxDrawdown, profitFactor, profitableMonths }: StrategyInsightsProps) {
  return (
    <div className="glass-strong rounded-xl p-6">
      <h3 className="text-xl font-bold mb-4">Strategy Insights</h3>
      <div className="space-y-4">
        {sharpeRatio > 1.5 && (
          <div className="border border-green-500/30 bg-green-500/10 rounded-lg p-4">
            <div className="flex items-start gap-3">
              <div className="text-2xl">&#10003;</div>
              <div>
                <h4 className="font-bold text-green-400 mb-1">Strong Risk-Adjusted Returns</h4>
                <p className="text-sm text-muted-foreground">
                  Your Sharpe ratio of {sharpeRatio.toFixed(2)} indicates excellent risk-adjusted performance, outperforming the benchmark.
                </p>
              </div>
            </div>
          </div>
        )}

        <div className="border border-blue-500/30 bg-blue-500/10 rounded-lg p-4">
          <div className="flex items-start gap-3">
            <div className="text-2xl">&#128161;</div>
            <div>
              <h4 className="font-bold text-blue-400 mb-1">Monthly Performance</h4>
              <p className="text-sm text-muted-foreground">
                {profitableMonths} out of 12 months were profitable, showing{' '}
                {profitableMonths >= 8 ? 'excellent' : 'moderate'} consistency.
              </p>
            </div>
          </div>
        </div>

        {Math.abs(maxDrawdown) > 15 && (
          <div className="border border-yellow-500/30 bg-yellow-500/10 rounded-lg p-4">
            <div className="flex items-start gap-3">
              <div className="text-2xl">&#9888;&#65039;</div>
              <div>
                <h4 className="font-bold text-yellow-400 mb-1">Consider Position Sizing</h4>
                <p className="text-sm text-muted-foreground">
                  Maximum drawdown of {Math.abs(maxDrawdown).toFixed(1)}% could be reduced with better position sizing and risk management.
                </p>
              </div>
            </div>
          </div>
        )}

        {profitFactor > 1.5 && (
          <div className="border border-purple-500/30 bg-purple-500/10 rounded-lg p-4">
            <div className="flex items-start gap-3">
              <div className="text-2xl">&#127919;</div>
              <div>
                <h4 className="font-bold text-purple-400 mb-1">Positive Edge Detected</h4>
                <p className="text-sm text-muted-foreground">
                  Profit factor of {profitFactor.toFixed(2)} indicates your strategy has a sustainable edge over the market.
                </p>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  )
}
