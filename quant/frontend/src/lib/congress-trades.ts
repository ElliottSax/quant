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
  disclosureDate: string
  // Calendar days between the transaction and its disclosure, when both dates
  // parse cleanly. Null if either date is missing/malformed. Used to surface
  // STOCK Act disclosure-timeliness (the Act requires filing within 45 days).
  daysToDisclose: number | null
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

const MS_PER_DAY = 24 * 60 * 60 * 1000
function daysBetween(from: Date | null, to: Date | null): number | null {
  if (!from || !to) return null
  const days = Math.round((to.getTime() - from.getTime()) / MS_PER_DAY)
  // Negative gaps mean a data/parsing anomaly (disclosure can't predate the
  // transaction) — treat as unknown rather than a real "early" filing.
  return days >= 0 ? days : null
}

export interface CongressData {
  trades: Trade[]
  lastUpdated: string
  topMembers: { name: string; chamber: string; count: number; volume: number }[]
  topTickers: { ticker: string; name: string; count: number }[]
}

const sleep = (ms: number) => new Promise((r) => setTimeout(r, ms))

// Strict mode is for the per-ticker / per-member pages. A transient FMP failure
// (rate limit, 5xx) used to come back as an empty list, which those pages rendered
// as notFound() -- and a static build then baked that 404 in for a ticker that is
// really in the data (the sitemap, built from the same feed, still listed it).
// Strict mode retries, then throws, so a bad fetch fails the render (ISR keeps the
// last good page; a build fails and production stays on the previous deploy)
// instead of publishing a false 404.
async function fetchChamber(path: string, chamber: 'House' | 'Senate', key: string, strict = false): Promise<Trade[]> {
  const attempts = strict ? 3 : 1
  let lastErr = 'unknown'
  for (let i = 0; i < attempts; i++) {
    if (i > 0) await sleep(700 * i)
    try {
      const res = await fetch(`${BASE}/${path}?apikey=${key}`, { next: { revalidate: 86400 } })
      if (!res.ok) { lastErr = `HTTP ${res.status}`; continue }
      const raw = (await res.json()) as FmpTrade[]
      if (!Array.isArray(raw)) { lastErr = 'non-array body'; continue }
      return parseChamber(raw, chamber)
    } catch (e) {
      lastErr = e instanceof Error ? e.message : String(e)
    }
  }
  if (strict) throw new Error(`FMP ${path} failed after ${attempts} attempts: ${lastErr}`)
  return []
}

function parseChamber(raw: FmpTrade[], chamber: 'House' | 'Senate'): Trade[] {
  return raw
    .filter((t) => t.symbol && t.symbol !== 'N/A')
    .map((t) => ({
      ticker: t.symbol,
      member: t.office || `${t.firstName} ${t.lastName}`.trim(),
      chamber,
      date: parseDate(t.transactionDate),
      transactionDate: t.transactionDate,
      disclosureDate: t.disclosureDate,
      daysToDisclose: daysBetween(parseDate(t.transactionDate), parseDate(t.disclosureDate)),
      assetDescription: t.assetDescription,
      type: t.type,
      amount: t.amount,
      amountMid: amountMidpoint(t.amount),
      isBuy: /purchase|buy/i.test(t.type),
      link: t.link,
    }))
}

// opts.strict: retry transient FMP failures and THROW instead of returning an
// empty/partial feed. Used by the per-ticker and per-member pages (see fetchChamber).
export async function getCongressTrades(opts: { strict?: boolean } = {}): Promise<CongressData | null> {
  const key = process.env.FMP_API_KEY
  if (!key) return null

  const strict = opts.strict === true
  const [senate, house] = await Promise.all([
    fetchChamber('senate-latest', 'Senate', key, strict),
    fetchChamber('house-latest', 'House', key, strict),
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

  const topMembers = Array.from(memberMap.entries())
    .map(([name, v]) => ({ name, ...v }))
    .sort((a, b) => b.count - a.count)
    .slice(0, 10)
  const topTickers = Array.from(tickerMap.entries())
    .map(([ticker, v]) => ({ ticker, ...v }))
    .sort((a, b) => b.count - a.count)
    .slice(0, 10)

  return { trades, lastUpdated: trades[0]?.transactionDate || '', topMembers, topTickers }
}
