import type { Metadata } from 'next'

export const metadata: Metadata = {
  title: "Congressional Stock Trading Leaderboard | Who's Beating the Market?",
  description:
    'Track and rank congressional stock trades. See which politicians are outperforming the S&P 500 with real trading data and performance analytics.',
  openGraph: {
    title: "Congressional Stock Trading Leaderboard | Who's Beating the Market?",
    description:
      'Track and rank congressional stock trades. See which politicians are outperforming the S&P 500.',
    url: 'https://quantengines.com/leaderboard',
  },
  twitter: {
    card: 'summary_large_image',
    title: "Congressional Stock Trading Leaderboard | Who's Beating the Market?",
    description:
      'Track and rank congressional stock trades. See which politicians are outperforming the S&P 500.',
  },
}

export default function LeaderboardLayout({ children }: { children: React.ReactNode }) {
  return <>{children}</>
}
