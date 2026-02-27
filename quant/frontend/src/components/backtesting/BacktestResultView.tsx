'use client'

import { MetricsGrid } from './MetricsGrid'
import { EquityCurveChart } from './EquityCurveChart'
import { DrawdownChart } from './DrawdownChart'
import { RollingMetricsChart } from './RollingMetricsChart'
import { MonthlyReturnsChart } from './MonthlyReturnsChart'
import { TradeDistributionChart } from './TradeDistributionChart'
import { TradeScatterPlot } from './TradeScatterPlot'
import { RiskMetricsPanel } from './RiskMetricsPanel'
import { StrategyInsights } from './StrategyInsights'
import { BrokerRecommendations } from './BrokerRecommendations'

interface BacktestMetrics {
  finalEquity: number
  totalReturn: number
  maxDrawdown: number
  sharpeRatio: number
  winRate: number
  avgWin: number
  avgLoss: number
  profitFactor: number
  totalTrades: number
}

interface BacktestData {
  equityData: Array<{ day: number; equity: number; drawdown: number; benchmark: number }>
  trades: Array<{ day: number; returnPct: number; profit: number; isWin: boolean }>
  monthlyReturns: Array<{ month: string; return: number }>
  tradeDistribution: Array<{ returnRange: string; count: number; value: number }>
  rollingMetrics: Array<{ day: number; sharpe: number; volatility: number }>
}

interface BacktestResultViewProps {
  metrics: BacktestMetrics
  data: BacktestData
  initialCapital: number
  strategy?: string
  userTier?: string
}

export function BacktestResultView({
  metrics,
  data,
  initialCapital,
  strategy = 'trend',
  userTier = 'free',
}: BacktestResultViewProps) {
  const profitableMonths = data.monthlyReturns.filter(m => m.return > 0).length

  return (
    <div className="space-y-8">
      {/* Broker recommendations section */}
      <BrokerRecommendations strategy={strategy} userTier={userTier} />

      <MetricsGrid
        totalReturn={metrics.totalReturn}
        sharpeRatio={metrics.sharpeRatio}
        maxDrawdown={metrics.maxDrawdown}
        winRate={metrics.winRate}
        totalTrades={metrics.totalTrades}
        finalEquity={metrics.finalEquity}
        initialCapital={initialCapital}
      />

      <EquityCurveChart
        equityData={data.equityData}
        initialCapital={initialCapital}
        finalEquity={metrics.finalEquity}
      />

      <DrawdownChart equityData={data.equityData} />

      <RollingMetricsChart rollingMetrics={data.rollingMetrics} />

      <MonthlyReturnsChart monthlyReturns={data.monthlyReturns} />

      <TradeDistributionChart tradeDistribution={data.tradeDistribution} />

      <TradeScatterPlot trades={data.trades} />

      <RiskMetricsPanel
        sharpeRatio={metrics.sharpeRatio}
        maxDrawdown={metrics.maxDrawdown}
        profitFactor={metrics.profitFactor}
        totalReturn={metrics.totalReturn}
        totalTrades={metrics.totalTrades}
        winRate={metrics.winRate}
        avgWin={metrics.avgWin}
        avgLoss={metrics.avgLoss}
      />

      <StrategyInsights
        sharpeRatio={metrics.sharpeRatio}
        maxDrawdown={metrics.maxDrawdown}
        profitFactor={metrics.profitFactor}
        profitableMonths={profitableMonths}
      />
    </div>
  )
}
