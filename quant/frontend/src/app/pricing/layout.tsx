import type { Metadata } from 'next'

export const metadata: Metadata = {
  title: 'Pricing: Free During Open Beta | QuantEngines',
  description: 'QuantEngines is free during the open beta: no paywalls and no tiers. See what is included, what is still planned, and how to support the project.',
  alternates: { canonical: '/pricing' },
}

export default function PricingLayout({ children }: { children: React.ReactNode }) {
  return <>{children}</>
}
