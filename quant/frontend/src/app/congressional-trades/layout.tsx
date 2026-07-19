import type { Metadata } from 'next'

// SEO metadata lives here (a server component) because page.tsx is a client
// component ('use client'), and Next.js App Router disallows exporting
// `metadata` from client components.
export const metadata: Metadata = {
  title: 'Congressional Stock Trades Tracker | Real-Time Politician Trading Data',
  description:
    'Track every stock trade made by U.S. Congress members in real time. See which politicians are buying and selling, the most traded stocks by Congress, and gain insights into congressional trading patterns.',
  keywords:
    'congressional stock trades, politician stock trades, congress trading tracker, congressional trading data, STOCK Act, politician stock tracker, congress insider trading, senate stock trades, house stock trades',
  openGraph: {
    title: 'Congressional Stock Trades Tracker | QuantEngines',
    description:
      'Real-time tracking of every stock trade made by members of the U.S. Congress. Discover patterns, top traders, and the most popular stocks among politicians.',
    type: 'website',
    url: '/congressional-trades',
  },
  twitter: {
    card: 'summary_large_image',
    title: 'Congressional Stock Trades Tracker',
    description:
      'Track real-time congressional stock trades. See what politicians are buying and selling.',
  },
}

export default function CongressionalTradesLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return children
}
