import type { Metadata } from 'next'

// The page this wraps no longer ranks anyone: its "performance" figures were invented
// in the browser and attributed to named members of Congress, so the page was replaced
// with an in-development notice. This metadata must not promise rankings that do not
// exist — and must not be restored until a real, measured leaderboard ships.
export const metadata: Metadata = {
  title: 'Congressional Trading Leaderboard — In Development | QuantEngines',
  description:
    'Performance rankings for congressional traders are being rebuilt on real filing data with published methodology and error bars. Live filings are available now.',
  robots: { index: false, follow: true },
}

export default function LeaderboardLayout({ children }: { children: React.ReactNode }) {
  return <>{children}</>
}
