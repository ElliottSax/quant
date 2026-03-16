import { Metadata } from 'next'

export const metadata: Metadata = {
  title: 'Congressional Stock Trades by Politician | QuantEngines',
  description:
    'Track stock trades by members of Congress. See which politicians are buying and selling stocks, their trading patterns, and portfolio performance.',
  keywords: [
    'congressional stock trades',
    'politician stock trading',
    'congress stock tracker',
    'congressional trading',
    'politician portfolio',
    'STOCK Act',
    'senate stock trades',
    'house stock trades',
    'congressional insider trading',
    'politician stock picks',
  ],
  openGraph: {
    title: 'Congressional Stock Trades by Politician | QuantEngines',
    description:
      'Track stock trades by members of Congress. See which politicians are buying and selling stocks, their trading patterns, and portfolio performance.',
    type: 'website',
    url: 'https://quantengines.com/politicians',
  },
}

export default function PoliticiansLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return children
}
