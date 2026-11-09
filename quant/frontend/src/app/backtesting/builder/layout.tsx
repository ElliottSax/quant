import type { Metadata } from 'next'

export const metadata: Metadata = {
  title: 'Trading Strategy Builder | QuantEngines',
  description: 'Create custom trading strategies with visual configuration, then backtest them on historical data. Free, no signup required.',
  alternates: { canonical: '/backtesting/builder' },
}

export default function StrategyBuilderLayout({ children }: { children: React.ReactNode }) {
  return <>{children}</>
}
