import type { Metadata } from 'next'
import StrategiesClient from './StrategiesClient'

export const metadata: Metadata = {
  title: 'Trading Strategy Library | QuantEngines',
  description: 'Browse the built-in trading strategies and their parameters, and run them in the backtester. Free, no signup required.',
  alternates: { canonical: '/strategies' },
}

export default function StrategiesPage() {
  return <StrategiesClient />
}
