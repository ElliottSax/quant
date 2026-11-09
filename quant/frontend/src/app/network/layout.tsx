import type { Metadata } from 'next'

export const metadata: Metadata = {
  title: 'Congressional Trading Network Analysis | QuantEngines',
  description: 'Interactive visualization of trading correlations between members of Congress. Explore connections, clusters and influential traders. Free, no signup required.',
  alternates: { canonical: '/network' },
}

export default function NetworkLayout({ children }: { children: React.ReactNode }) {
  return <>{children}</>
}
