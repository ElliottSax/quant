/**
 * Congressional trader leaderboard — in development.
 *
 * This page ranked twenty named members of Congress by annual return, win rate,
 * best and worst trade, sector allocation and a month-by-month curve against the
 * S&P 500. None of it came from anywhere: the table was a hardcoded array and the
 * performance curves were drawn by Math.random at module load, so the same
 * politician's chart changed on every reload. Attributing invented returns to a
 * real, named person is the worst form the fabrication took on this site, and the
 * page carried share-to-X buttons that put those numbers in someone else's mouth.
 *
 * A ranking may only return here when it is computed from the filed STOCK Act
 * transactions this site already ingests, with the return methodology stated on
 * the page. No hardcoded roster, no generated curve, no estimated figure that
 * cannot be traced to a filing.
 *
 * The prior implementation is preserved in git history. Do not restore it.
 */

import Link from 'next/link'
import type { Metadata } from 'next'

// openGraph/twitter are restated here so the route's social cards stop advertising
// rankings that no longer exist: the parent layout still carries the old marketing
// copy, and page-level keys replace it.
export const metadata: Metadata = {
  title: 'Trader Leaderboard — In Development | QuantEngines',
  description:
    'The congressional trading performance leaderboard is being rebuilt on filed STOCK Act transactions with a stated return methodology. It is not available yet.',
  robots: { index: false, follow: true },
  openGraph: {
    title: 'Trader Leaderboard — In Development | QuantEngines',
    description:
      'The congressional trading performance leaderboard is being rebuilt on filed STOCK Act transactions. It is not available yet.',
    url: 'https://quantengines.com/leaderboard',
  },
  twitter: {
    card: 'summary',
    title: 'Trader Leaderboard — In Development | QuantEngines',
    description:
      'The congressional trading performance leaderboard is being rebuilt on filed STOCK Act transactions. It is not available yet.',
  },
}

export default function LeaderboardPage() {
  return (
    <div className="space-y-4">
      <h1 className="sr-only">Congressional Trader Leaderboard — In Development</h1>

      <div>
        <p className="text-[10px] text-[hsl(215,20%,55%)] font-mono uppercase tracking-widest mb-2">
          In development
        </p>
        <h2 className="text-xl font-bold text-[hsl(45,96%,58%)] uppercase tracking-wider">
          The Leaderboard Is Being Rebuilt
        </h2>
      </div>

      <div className="terminal-panel">
        <div className="terminal-panel-header">
          <span>Why this page is empty</span>
        </div>
        <div className="p-4 bg-[hsl(220,60%,4%)] space-y-4 text-sm text-[hsl(215,20%,70%)]">
          <p>
            This page used to rank named members of Congress by annual return, win rate
            and best trade. Those figures were not measured. The roster was hardcoded and
            the performance charts were generated at random in the browser, so a
            politician&apos;s twelve-month curve changed every time the page loaded.
          </p>
          <p>
            Publishing invented returns under a real person&apos;s name — with a share
            button attached — is not a rough edge, so the page is down rather than
            dressed up. The congressional filings themselves are real and remain
            available.
          </p>
          <p>
            The replacement will compute performance from the filed STOCK Act
            transactions this site already ingests, and will state on the page how a
            return is derived from a disclosed date and a disclosed amount range. Where
            a filing is too coarse to support a figure, the figure will be absent rather
            than estimated.
          </p>
          <p className="text-xs text-[hsl(215,20%,55%)] font-mono">
            We compute and display. We never recommend.
          </p>
        </div>
      </div>

      <div className="flex flex-wrap gap-3 pt-2">
        <Link
          href="/congress-stock-trades"
          className="px-4 py-2 rounded bg-[hsl(210,100%,56%)]/10 border border-[hsl(210,100%,56%)]/30 text-[hsl(210,100%,56%)] text-xs font-mono hover:bg-[hsl(210,100%,56%)]/20 transition-colors"
        >
          CONGRESSIONAL TRADE FILINGS (REAL DATA)
        </Link>
        <Link
          href="/politicians"
          className="px-4 py-2 rounded bg-[hsl(215,50%,10%)] border border-[hsl(215,40%,18%)] text-[hsl(215,20%,70%)] text-xs font-mono hover:bg-[hsl(215,50%,14%)] transition-colors"
        >
          POLITICIANS
        </Link>
      </div>
    </div>
  )
}
