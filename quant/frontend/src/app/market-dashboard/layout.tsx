import type { Metadata } from 'next'

export const metadata: Metadata = {
  title: 'Market Dashboard | Stock Quotes, Fear & Greed Index, Volatility',
  description: 'Market dashboard with the Crypto Fear & Greed Index, major index quotes and quick stock lookup, drawn from live sources only. No login required.',
  alternates: { canonical: '/market-dashboard' },
}

export default function MarketDashboardLayout({ children }: { children: React.ReactNode }) {
  return <>{children}</>
}
