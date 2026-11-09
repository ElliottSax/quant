import type { Metadata } from 'next'

export const metadata: Metadata = {
  title: 'Congressional Trading Dashboard | QuantEngines',
  description: 'Overview of disclosed congressional stock trading activity, with links to the network analysis and backtesting tools. Free, no signup required.',
  alternates: { canonical: '/dashboard' },
}

export default function DashboardLayout({ children }: { children: React.ReactNode }) {
  return <>{children}</>
}
