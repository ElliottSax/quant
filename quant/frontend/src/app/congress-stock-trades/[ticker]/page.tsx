import type { Metadata } from 'next'
import Link from 'next/link'
import { notFound } from 'next/navigation'
import { getCongressTrades, type Trade } from '@/lib/congress-trades'

export const revalidate = 86400
// Only tickers present in the current data get pages; anything else is a real
// 404 (no fake/thin pages, no soft-404 streaming issue).
export const dynamicParams = false

async function tradesFor(ticker: string): Promise<{ trades: Trade[]; asset: string } | null> {
  const data = await getCongressTrades()
  if (!data) return null
  const up = ticker.toUpperCase()
  const trades = data.trades.filter((t) => t.ticker.toUpperCase() === up)
  if (trades.length === 0) return null
  return { trades, asset: trades[0].assetDescription || up }
}

export async function generateStaticParams() {
  const data = await getCongressTrades()
  if (!data) return []
  const seen = new Set<string>()
  const params: { ticker: string }[] = []
  for (const t of data.trades) {
    const up = t.ticker.toUpperCase()
    if (!seen.has(up)) { seen.add(up); params.push({ ticker: up }) }
  }
  return params
}

export async function generateMetadata({ params }: { params: Promise<{ ticker: string }> }): Promise<Metadata> {
  const { ticker } = await params
  const up = ticker.toUpperCase()
  const data = await tradesFor(up)
  const title = `Congress Trades in ${up}${data ? ` (${data.asset})` : ''}: Who's Buying & Selling`
  const url = `https://quantengines.com/congress-stock-trades/${up}`
  return {
    title: { absolute: `${title} | QuantEngines` },
    description: `Which members of Congress recently traded ${up}? See the latest House and Senate ${up} stock trades from official STOCK Act disclosures — buys, sells, and amounts.`,
    alternates: { canonical: url },
  }
}

function Badge({ buy }: { buy: boolean }) {
  return <span className={`inline-block rounded px-2 py-0.5 text-xs font-medium ${buy ? 'bg-emerald-500/15 text-emerald-400' : 'bg-red-500/15 text-red-400'}`}>{buy ? 'Buy' : 'Sell'}</span>
}

export default async function TickerPage({ params }: { params: Promise<{ ticker: string }> }) {
  const { ticker } = await params
  const up = ticker.toUpperCase()
  const data = await tradesFor(up)
  if (!data) notFound()

  const { trades, asset } = data
  const buys = trades.filter((t) => t.isBuy).length
  const sells = trades.length - buys
  const members = new Set(trades.map((t) => t.member)).size

  return (
    <div className="container mx-auto px-4 py-12">
      <div className="max-w-4xl mx-auto">
        <nav className="text-sm text-slate-500 mb-4">
          <Link href="/congress-stock-trades" className="hover:text-slate-300">Congress Trades</Link> / <span className="text-slate-300">{up}</span>
        </nav>
        <h1 className="text-4xl font-bold text-white mb-2">Congress Trades in {up}</h1>
        <p className="text-lg text-slate-400 mb-6">
          {asset} — recent U.S. House &amp; Senate trades from official STOCK Act disclosures.
        </p>

        <div className="grid grid-cols-3 gap-4 mb-10 max-w-lg">
          <div className="rounded-lg border border-[hsl(215,40%,18%)] bg-[hsl(220,55%,9%)] p-4 text-center">
            <p className="text-2xl font-bold text-emerald-400">{buys}</p><p className="text-xs text-slate-500">Buys</p>
          </div>
          <div className="rounded-lg border border-[hsl(215,40%,18%)] bg-[hsl(220,55%,9%)] p-4 text-center">
            <p className="text-2xl font-bold text-red-400">{sells}</p><p className="text-xs text-slate-500">Sells</p>
          </div>
          <div className="rounded-lg border border-[hsl(215,40%,18%)] bg-[hsl(220,55%,9%)] p-4 text-center">
            <p className="text-2xl font-bold text-white">{members}</p><p className="text-xs text-slate-500">Members</p>
          </div>
        </div>

        <div className="overflow-x-auto rounded-lg border border-[hsl(215,40%,18%)]">
          <table className="w-full text-sm">
            <thead><tr className="text-left text-slate-500 border-b border-[hsl(215,40%,18%)]"><th className="py-2 px-4">Date</th><th className="py-2 px-4">Member</th><th className="py-2 px-4">Chamber</th><th className="py-2 px-4">Type</th><th className="py-2 px-4">Amount</th></tr></thead>
            <tbody>
              {trades.map((t, i) => (
                <tr key={i} className="border-b border-[hsl(215,40%,14%)]">
                  <td className="py-2.5 px-4 text-slate-400 whitespace-nowrap">{t.transactionDate}</td>
                  <td className="py-2.5 px-4 text-white">{t.member}</td>
                  <td className="py-2.5 px-4 text-slate-400">{t.chamber}</td>
                  <td className="py-2.5 px-4"><Badge buy={t.isBuy} /></td>
                  <td className="py-2.5 px-4 text-slate-300 whitespace-nowrap">{t.amount}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>

        <p className="mt-8 text-sm text-slate-500">
          Source: official U.S. House &amp; Senate STOCK Act disclosures via Financial Modeling Prep.
          See <Link href="/congress-stock-trades" className="text-indigo-400 hover:underline">all recent congressional trades</Link> or explore <Link href="/tools" className="text-indigo-400 hover:underline">free trading tools</Link>.
        </p>
      </div>
    </div>
  )
}
