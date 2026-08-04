import type { Metadata } from 'next'
import Link from 'next/link'
import { getCongressTrades, memberSlug, type Trade } from '@/lib/congress-trades'

// Daily ISR — regenerated at most once per 24h from Financial Modeling Prep.
export const revalidate = 86400

const url = 'https://quantengines.com/congress-stock-trades'

export const metadata: Metadata = {
  title: 'Congress Stock Trades Tracker — Latest House & Senate Trades | QuantEngines',
  description:
    'Track the latest U.S. Congress stock trades (House and Senate) from official STOCK Act disclosures. See recent and biggest trades, most active members, and most-traded stocks. Free, updated daily.',
  keywords: ['congress stock trades', 'congressional trading tracker', 'senate stock trades', 'house stock trades', 'politician stock trades', 'stock act disclosures'],
  alternates: { canonical: url },
  openGraph: { title: 'Congress Stock Trades Tracker', description: 'The latest House & Senate stock trades from official disclosures.', type: 'website', url },
}

function ChamberTag({ c }: { c: 'House' | 'Senate' }) {
  return <span className={`text-xs ${c === 'Senate' ? 'text-sky-400' : 'text-violet-400'}`}>{c}</span>
}
function Badge({ buy }: { buy: boolean }) {
  return <span className={`inline-block rounded px-2 py-0.5 text-xs font-medium ${buy ? 'bg-emerald-500/15 text-emerald-400' : 'bg-red-500/15 text-red-400'}`}>{buy ? 'Buy' : 'Sell'}</span>
}

function Row({ t }: { t: Trade }) {
  return (
    <tr className="border-b border-[hsl(215,40%,14%)]">
      <td className="py-2.5 pr-4 text-slate-400 whitespace-nowrap">{t.transactionDate}</td>
      <td className="py-2.5 pr-4"><Link href={`/congress-stock-trades/member/${memberSlug(t.member)}`} className="text-white hover:text-indigo-400 hover:underline">{t.member}</Link> <ChamberTag c={t.chamber} /></td>
      <td className="py-2.5 pr-4">
        <Link href={`/congress-stock-trades/${t.ticker.toUpperCase()}`} className="font-semibold text-indigo-400 hover:underline">{t.ticker}</Link>
        <span className="ml-2 text-slate-500 text-xs hidden md:inline">{t.assetDescription?.slice(0, 30)}</span>
      </td>
      <td className="py-2.5 pr-4"><Badge buy={t.isBuy} /></td>
      <td className="py-2.5 text-slate-300 whitespace-nowrap">{t.amount}</td>
    </tr>
  )
}

const THEAD = (
  <thead><tr className="text-left text-slate-500 border-b border-[hsl(215,40%,18%)]">
    <th className="py-2 px-4">Date</th><th className="py-2 px-4">Member</th><th className="py-2 px-4">Stock</th><th className="py-2 px-4">Type</th><th className="py-2 px-4">Amount</th>
  </tr></thead>
)

export default async function CongressTradesPage() {
  const data = await getCongressTrades()

  if (!data || data.trades.length === 0) {
    return (
      <div className="container mx-auto px-4 py-16 text-center text-slate-400">
        <h1 className="text-3xl font-bold text-white mb-3">Congress Stock Trades</h1>
        <p>The trade data source is temporarily unavailable. Please check back shortly.</p>
      </div>
    )
  }

  const recent = data.trades.slice(0, 40)
  const biggest = [...data.trades].sort((a, b) => b.amountMid - a.amountMid).slice(0, 12)
  const schema = {
    '@context': 'https://schema.org', '@type': 'Dataset',
    name: 'U.S. Congress Stock Trades (House & Senate)',
    description: 'Recent U.S. House and Senate stock trades from official STOCK Act financial disclosures.',
    url, creator: { '@type': 'Organization', name: 'QuantEngines' }, isAccessibleForFree: true,
  }

  return (
    <div className="container mx-auto px-4 py-12">
      <script type="application/ld+json" dangerouslySetInnerHTML={{ __html: JSON.stringify(schema) }} />

      <div className="max-w-3xl mb-8">
        <h1 className="text-4xl md:text-5xl font-bold text-white mb-3">Congress Stock Trades Tracker</h1>
        <p className="text-lg text-slate-400">
          The latest U.S. House and Senate stock trades, from official STOCK Act disclosures. Updated
          daily. Most recent transaction: <strong className="text-white">{data.lastUpdated}</strong>.
        </p>
        <Link href="/congress-stock-trades/weekly" className="inline-block mt-4 text-indigo-400 hover:underline font-medium">
          → See this week&apos;s biggest trades digest
        </Link>
      </div>

      <div className="grid gap-6 lg:grid-cols-2 mb-12">
        <div className="rounded-xl border border-[hsl(215,40%,18%)] bg-[hsl(220,55%,9%)] p-5">
          <h2 className="text-lg font-bold text-white mb-3">Most Active Members (recent filings)</h2>
          <ol className="space-y-1.5">
            {data.topMembers.map((s, i) => (
              <li key={s.name} className="flex items-center justify-between text-sm">
                <span className="text-slate-300"><span className="text-slate-500 mr-2">{i + 1}.</span><Link href={`/congress-stock-trades/member/${memberSlug(s.name)}`} className="hover:text-indigo-400 hover:underline">{s.name}</Link> <ChamberTag c={s.chamber as 'House' | 'Senate'} /></span>
                <span className="text-slate-400">{s.count} trades</span>
              </li>
            ))}
          </ol>
        </div>
        <div className="rounded-xl border border-[hsl(215,40%,18%)] bg-[hsl(220,55%,9%)] p-5">
          <h2 className="text-lg font-bold text-white mb-3">Most-Traded Stocks (recent filings)</h2>
          <ol className="space-y-1.5">
            {data.topTickers.map((t, i) => (
              <li key={t.ticker} className="flex items-center justify-between text-sm">
                <span className="text-slate-300"><span className="text-slate-500 mr-2">{i + 1}.</span><Link href={`/congress-stock-trades/${t.ticker.toUpperCase()}`} className="font-semibold text-indigo-400 hover:underline">{t.ticker}</Link> <span className="text-slate-500">{t.name?.slice(0, 26)}</span></span>
                <span className="text-slate-400">{t.count} trades</span>
              </li>
            ))}
          </ol>
        </div>
      </div>

      <h2 className="text-2xl font-bold text-white mb-4">Biggest Recent Trades</h2>
      <div className="overflow-x-auto rounded-lg border border-[hsl(215,40%,18%)] mb-12">
        <table className="w-full text-sm">{THEAD}<tbody>{biggest.map((t, i) => <Row key={i} t={t} />)}</tbody></table>
      </div>

      <h2 className="text-2xl font-bold text-white mb-4">Latest Trades</h2>
      <div className="overflow-x-auto rounded-lg border border-[hsl(215,40%,18%)]">
        <table className="w-full text-sm">{THEAD}<tbody>{recent.map((t, i) => <Row key={i} t={t} />)}</tbody></table>
      </div>

      <div className="mt-8 text-sm text-slate-500">
        <p>Data source: official U.S. House &amp; Senate financial disclosures (STOCK Act), via Financial Modeling Prep. Explore our <Link href="/tools" className="text-indigo-400 hover:underline">free trading tools</Link>.</p>
      </div>
    </div>
  )
}
