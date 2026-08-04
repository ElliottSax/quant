// Real, current U.S. Congress (House + Senate) stock-trade data from Financial
// Modeling Prep, which parses the official STOCK Act disclosures
// (efdsearch.senate.gov + disclosures-clerk.house.gov). Fetched server-side with
// ISR (revalidate daily) so we make ~2 calls/day, well within the free tier.

const BASE = 'https://financialmodelingprep.com/stable'

interface FmpTrade {
  symbol: string
  disclosureDate: string
  transactionDate: string
  firstName: string
  lastName: string
  office: string
  district?: string
  owner: string
  assetDescription: string
  assetType: string
  type: string
  amount: string
  link: string
}

export interface Trade {
  ticker: string
  member: string
  chamber: 'House' | 'Senate'
  date: Date | null
  transactionDate: string
  assetDescription: string
  type: string
  amount: string
  amountMid: number
  isBuy: boolean
  link: string
}

// Stable slug for a member name, shared by the per-member page and its links.
export function memberSlug(name: string): string {
  return name.toLowerCase().replace(/[^a-z0-9]+/g, '-').replace(/^-+|-+$/g, '')
}

const AMOUNT_RE = /\$([\d,]+)\s*-\s*\$([\d,]+)/
function amountMidpoint(amount: string): number {
  const m = AMOUNT_RE.exec(amount || '')
  if (m) return (Number(m[1].replace(/,/g, '')) + Number(m[2].replace(/,/g, ''))) / 2
  const s = /\$([\d,]+)/.exec(amount || '')
  return s ? Number(s[1].replace(/,/g, '')) : 0
}

function parseDate(s: string): Date | null {
  const m = /^(\d{4})-(\d{2})-(\d{2})$/.exec((s || '').trim())
  if (!m) return null
  const d = new Date(Number(m[1]), Number(m[2]) - 1, Number(m[3]))
  return isNaN(d.getTime()) ? null : d
}

export interface CongressData {
  trades: Trade[]
  lastUpdated: string
  topMembers: { name: string; chamber: string; count: number; volume: number }[]
  topTickers: { ticker: string; name: string; count: number }[]
}

async function fetchChamber(path: string, chamber: 'House' | 'Senate', key: string): Promise<Trade[]> {
  try {
    const res = await fetch(`${BASE}/${path}?apikey=${key}`, { next: { revalidate: 86400 } })
    if (!res.ok) return []
    const raw = (await res.json()) as FmpTrade[]
    if (!Array.isArray(raw)) return []
    return raw
      .filter((t) => t.symbol && t.symbol !== 'N/A')
      .map((t) => ({
        ticker: t.symbol,
        member: t.office || `${t.firstName} ${t.lastName}`.trim(),
        chamber,
        date: parseDate(t.transactionDate),
        transactionDate: t.transactionDate,
        assetDescription: t.assetDescription,
        type: t.type,
        amount: t.amount,
        amountMid: amountMidpoint(t.amount),
        isBuy: /purchase|buy/i.test(t.type),
        link: t.link,
      }))
  } catch {
    return []
  }
}

export async function getCongressTrades(): Promise<CongressData | null> {
  const key = process.env.FMP_API_KEY
  if (!key) return null

  const [senate, house] = await Promise.all([
    fetchChamber('senate-latest', 'Senate', key),
    fetchChamber('house-latest', 'House', key),
  ])
  const trades = [...senate, ...house]
    .filter((t) => t.date)
    .sort((a, b) => b.date!.getTime() - a.date!.getTime())

  if (trades.length === 0) return null

  const memberMap = new Map<string, { chamber: string; count: number; volume: number }>()
  const tickerMap = new Map<string, { name: string; count: number }>()
  for (const t of trades) {
    const m = memberMap.get(t.member) || { chamber: t.chamber, count: 0, volume: 0 }
    m.count++
    m.volume += t.amountMid
    memberMap.set(t.member, m)
    const k = tickerMap.get(t.ticker) || { name: t.assetDescription, count: 0 }
    k.count++
    tickerMap.set(t.ticker, k)
  }

  const topMembers = [...memberMap.entries()]
    .map(([name, v]) => ({ name, ...v }))
    .sort((a, b) => b.count - a.count)
    .slice(0, 10)
  const topTickers = [...tickerMap.entries()]
    .map(([ticker, v]) => ({ ticker, ...v }))
    .sort((a, b) => b.count - a.count)
    .slice(0, 10)

  return { trades, lastUpdated: trades[0]?.transactionDate || '', topMembers, topTickers }
}
