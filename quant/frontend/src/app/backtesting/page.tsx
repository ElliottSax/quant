import type { Metadata } from 'next'
import BacktestingClient from './BacktestingClient'

export const metadata: Metadata = {
  title: 'Backtesting Engine: Test Trading Strategies | QuantEngines',
  description: 'Test and optimize trading strategies on historical data and review the performance metrics. Free, no signup required.',
  alternates: { canonical: '/backtesting' },
}

export default function BacktestingPage() {
  return <BacktestingClient />
}
