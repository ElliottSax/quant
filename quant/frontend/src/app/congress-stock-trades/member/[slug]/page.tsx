import type { Metadata } from 'next'
import Link from 'next/link'
import { notFound } from 'next/navigation'
import { getCongressTrades, memberSlug, type Trade } from '@/lib/congress-trades'

export const revalidate = 86400
export const dynamicParams = false

async function forMember(slug: string): Promise<{ trades: Trade[]; name: string; chamber: string } | null> {
  const data = await getCongressTrades()
  if (!data) return null
  const trades = data.trades.filter((t) => memberSlug(t.member) === slug)
  if (trades.length === 0) return null
  return { trades, name: trades[0].member, chamber: trades[0].chamber }
}

export async function generateStaticParams() {
  const data = await getCongressTrades()
  if (!data) return []
  const seen = new Set<string>()
  const params: { slug: string }[] = []
  for (const t of data.trades) {
    const s = memberSlug(t.member)
    if (s && !seen.has(s)) { seen.add(s); params.push({ slug: s }) }
  }
  return params
}

export async function generateMetadata({ params }: { params: Promise<{ slug: string }> }): Promise<Metadata> {
  const { slug } = await params
  const d = await forMember(slug)
  const name = d?.name ?? slug
  const url = `https://quantengines.com/congress-stock-trades/member/${slug}`
  return {
    title: { absolute: `${name} Stock Trades — Recent Buys & Sells | QuantEngines` },
    description: `Every recent stock trade disclosed by ${name} under the STOCK Act — tickers, buy/sell, dates, and amounts, from official congressional disclosures.`,
    alternates: { canonical: url },
  }
}

function Badge({ buy }: { buy: boolean }) {
  return <span className={`inline-block rounded px-2 py-0.5 text-xs font-medium ${buy ? 'bg-emerald-500/15 text-emerald-400' : 'bg-red-500/15 text-red-400'}`}>{buy ? 'Buy' : 'Sell'}</span>
}

export default async function MemberPage({ params }: { params: Promise<{ slug: string }> }) {
  const { slug } = await params
  const d = await forMember(slug)
  if (!d) notFound()

  const { trades, name, chamber } = d
  const buys = trades.filter((t) => t.isBuy).length
  const tickers = new Set(trades.map((t) => t.ticker)).size

  return (
    <div className="container mx-auto px-4 py-12">
      <div className="max-w-4xl mx-auto">
        <nav className="text-sm text-slate-500 mb-4">
          <Link href="/congress-stock-trades" className="hover:text-slate-300">Congress Trades</Link> / <span className="text-slate-300">{name}</span>
        </nav>
        <h1 className="text-4xl font-bold text-white mb-2">{name} — Stock Trades</h1>
        <p className="text-lg text-slate-400 mb-6">
          {chamber} · recent stock trades disclosed under the STOCK Act, from official congressional filings.
        </p>

        <div className="grid grid-cols-3 gap-4 mb-10 max-w-lg">
          <div className="rounded-lg border border-[hsl(215,40%,18%)] bg-[hsl(220,55%,9%)] p-4 text-center"><p className="text-2xl font-bold text-white">{trades.length}</p><p className="text-xs text-slate-500">Trades</p></div>
          <div className="rounded-lg border border-[hsl(215,40%,18%)] bg-[hsl(220,55%,9%)] p-4 text-center"><p className="text-2xl font-bold text-emerald-400">{buys}</p><p className="text-xs text-slate-500">Buys</p></div>
          <div className="rounded-lg border border-[hsl(215,40%,18%)] bg-[hsl(220,55%,9%)] p-4 text-center"><p className="text-2xl font-bold text-white">{tickers}</p><p className="text-xs text-slate-500">Stocks</p></div>
        </div>

        <div className="overflow-x-auto rounded-lg border border-[hsl(215,40%,18%)]">
          <table className="w-full text-sm">
            <thead><tr className="text-left text-slate-500 border-b border-[hsl(215,40%,18%)]"><th className="py-2 px-4">Date</th><th className="py-2 px-4">Stock</th><th className="py-2 px-4">Type</th><th className="py-2 px-4">Amount</th></tr></thead>
            <tbody>
              {trades.map((t, i) => (
                <tr key={i} className="border-b border-[hsl(215,40%,14%)]">
                  <td className="py-2.5 px-4 text-slate-400 whitespace-nowrap">{t.transactionDate}</td>
                  <td className="py-2.5 px-4"><Link href={`/congress-stock-trades/${t.ticker.toUpperCase()}`} className="font-semibold text-indigo-400 hover:underline">{t.ticker}</Link> <span className="text-slate-500 text-xs hidden md:inline">{t.assetDescription?.slice(0, 28)}</span></td>
                  <td className="py-2.5 px-4"><Badge buy={t.isBuy} /></td>
                  <td className="py-2.5 px-4 text-slate-300 whitespace-nowrap">{t.amount}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>

        <p className="mt-8 text-sm text-slate-500">
          Source: official U.S. House &amp; Senate STOCK Act disclosures via Financial Modeling Prep.
          See <Link href="/congress-stock-trades" className="text-indigo-400 hover:underline">all recent congressional trades</Link>.
        </p>
      </div>
    </div>
  )
}
