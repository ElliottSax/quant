import type { Metadata } from 'next'
import Link from 'next/link'
import { getCongressTrades, type Trade } from '@/lib/congress-trades'

export const revalidate = 86400

const url = 'https://quantengines.com/congress-stock-trades/weekly'

export const metadata: Metadata = {
  title: "Congress's Biggest Stock Trades This Week | QuantEngines",
  description:
    "The biggest recent U.S. Congress stock trades from official STOCK Act disclosures — a weekly digest of the largest House and Senate moves. Free, updated daily.",
  alternates: { canonical: url },
  openGraph: { title: "Congress's Biggest Stock Trades This Week", description: 'The largest recent House & Senate stock trades.', type: 'website', url },
}

function money(n: number) {
  return n >= 1_000_000 ? `$${(n / 1_000_000).toFixed(1)}M` : `$${Math.round(n / 1000)}K`
}

export default async function WeeklyDigestPage() {
  const data = await getCongressTrades()
  if (!data || data.trades.length === 0) {
    return (
      <div className="container mx-auto px-4 py-16 text-center text-slate-400">
        <h1 className="text-3xl font-bold text-white mb-3">Congress&apos;s Biggest Trades This Week</h1>
        <p>The data source is temporarily unavailable. Please check back shortly.</p>
      </div>
    )
  }

  // Biggest disclosed trades from the most recent activity.
  const top: Trade[] = [...data.trades]
    .sort((a, b) => b.amountMid - a.amountMid)
    .slice(0, 10)

  const monthYear = new Date().toLocaleString('en-US', { month: 'long', year: 'numeric' })

  // Plain-text digest, ready to copy into Reddit / X / a newsletter.
  const shareText = [
    `Congress's biggest stock trades (as of ${data.lastUpdated}):`,
    '',
    ...top.slice(0, 8).map((t, i) => `${i + 1}. ${t.member} (${t.chamber}) — ${t.isBuy ? 'BOUGHT' : 'SOLD'} ${t.ticker}, ${t.amount}`),
    '',
    'Source: official STOCK Act disclosures. Full tracker: quantengines.com/congress-stock-trades',
  ].join('\n')

  return (
    <div className="container mx-auto px-4 py-12">
      <div className="max-w-3xl mx-auto">
        <h1 className="text-4xl md:text-5xl font-bold text-white mb-3">Congress&apos;s Biggest Stock Trades This Week</h1>
        <p className="text-lg text-slate-400 mb-8">
          The largest recent U.S. House &amp; Senate trades from official STOCK Act disclosures ({monthYear}).
          Updated daily — most recent transaction {data.lastUpdated}.
        </p>

        <ol className="space-y-3 mb-12">
          {top.map((t, i) => (
            <li key={i} className="flex items-center gap-4 rounded-xl border border-[hsl(215,40%,18%)] bg-[hsl(220,55%,9%)] p-4">
              <span className="text-2xl font-bold text-slate-600 w-8 text-center">{i + 1}</span>
              <div className="flex-1">
                <p className="text-white font-semibold">{t.member} <span className="text-xs text-slate-500">{t.chamber}</span></p>
                <p className="text-sm text-slate-400">
                  <span className={t.isBuy ? 'text-emerald-400' : 'text-red-400'}>{t.isBuy ? 'Bought' : 'Sold'}</span>{' '}
                  <Link href={`/congress-stock-trades/${t.ticker.toUpperCase()}`} className="text-indigo-400 hover:underline font-medium">{t.ticker}</Link>
                  {' · '}{t.transactionDate}
                </p>
              </div>
              <span className="text-lg font-bold text-white whitespace-nowrap">{money(t.amountMid)}</span>
            </li>
          ))}
        </ol>

        <div className="rounded-xl border border-[hsl(215,40%,18%)] bg-[hsl(220,55%,7%)] p-5 mb-8">
          <h2 className="text-lg font-bold text-white mb-2">Share this digest</h2>
          <p className="text-sm text-slate-400 mb-3">Copy &amp; paste for Reddit, X, or a newsletter:</p>
          <pre className="whitespace-pre-wrap text-sm text-slate-300 bg-[hsl(220,55%,5%)] rounded-lg p-4 overflow-x-auto select-all">{shareText}</pre>
        </div>

        <p className="text-sm text-slate-500">
          See <Link href="/congress-stock-trades" className="text-indigo-400 hover:underline">all recent congressional trades</Link> or explore <Link href="/tools" className="text-indigo-400 hover:underline">free trading tools</Link>. Source: official U.S. House &amp; Senate STOCK Act disclosures via Financial Modeling Prep.
        </p>
      </div>
    </div>
  )
}
