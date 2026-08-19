/**
 * Loader for public/data/prices.json — the only price source this page has.
 *
 * The file is ~370 KB, so it is fetched at runtime rather than imported into the bundle.
 * Parsing is strict: the column order is checked before any row is read positionally, and
 * a row that is not six well-formed fields is dropped rather than patched. A symbol left
 * with no usable rows is removed from the picker, so the page can never offer a ticker it
 * has no history for.
 */

export const EXPECTED_COLUMNS = ['date', 'open', 'high', 'low', 'close', 'volume'] as const

/** One end-of-day bar: [date, open, high, low, close, volume]. */
export type Bar = [string, number, number, number, number, number]

export interface LatestQuote {
  day: string
  close: number
  change: number
  change_pct: number
}

export interface PriceArtefact {
  generated_at: string
  provider: string
  adjusted: boolean
  years: number | null
  symbols: string[]
  latest: Record<string, LatestQuote>
  series: Record<string, Bar[]>
}

function isFiniteNumber(v: unknown): v is number {
  return typeof v === 'number' && Number.isFinite(v)
}

function parseBar(raw: unknown): Bar | null {
  if (!Array.isArray(raw) || raw.length < 6) return null
  const [date, open, high, low, close, volume] = raw
  if (typeof date !== 'string' || !date) return null
  if (![open, high, low, close, volume].every(isFiniteNumber)) return null
  return [date, open, high, low, close, volume]
}

function parseLatest(raw: unknown): LatestQuote | null {
  if (!raw || typeof raw !== 'object') return null
  const r = raw as Record<string, unknown>
  if (typeof r.day !== 'string') return null
  if (!isFiniteNumber(r.close) || !isFiniteNumber(r.change) || !isFiniteNumber(r.change_pct)) {
    return null
  }
  return { day: r.day, close: r.close, change: r.change, change_pct: r.change_pct }
}

export function parseArtefact(raw: unknown): PriceArtefact | null {
  if (!raw || typeof raw !== 'object') return null
  const r = raw as Record<string, unknown>

  // Rows are positional. If the writer ever reorders the columns, refuse the file rather
  // than plot open prices as closes.
  const columns = r.columns
  if (
    !Array.isArray(columns) ||
    columns.length !== EXPECTED_COLUMNS.length ||
    !EXPECTED_COLUMNS.every((c, i) => columns[i] === c)
  ) {
    return null
  }

  if (!Array.isArray(r.symbols) || !r.series || typeof r.series !== 'object') return null

  const rawSeries = r.series as Record<string, unknown>
  const rawLatest = (r.latest && typeof r.latest === 'object' ? r.latest : {}) as Record<
    string,
    unknown
  >

  const symbols: string[] = []
  const series: Record<string, Bar[]> = {}
  const latest: Record<string, LatestQuote> = {}

  for (const sym of r.symbols) {
    if (typeof sym !== 'string' || !sym) continue
    const rows = rawSeries[sym]
    if (!Array.isArray(rows)) continue

    const bars: Bar[] = []
    for (const row of rows) {
      const bar = parseBar(row)
      if (bar) bars.push(bar)
    }
    if (!bars.length) continue

    bars.sort((a, b) => (a[0] < b[0] ? -1 : a[0] > b[0] ? 1 : 0))
    symbols.push(sym)
    series[sym] = bars

    const quote = parseLatest(rawLatest[sym])
    if (quote) latest[sym] = quote
  }

  if (!symbols.length) return null

  return {
    generated_at: typeof r.generated_at === 'string' ? r.generated_at : '',
    provider: typeof r.provider === 'string' ? r.provider : '',
    adjusted: r.adjusted === true,
    years: isFiniteNumber(r.years) ? r.years : null,
    symbols,
    latest,
    series,
  }
}

export async function fetchArtefact(signal?: AbortSignal): Promise<PriceArtefact | null> {
  const res = await fetch('/data/prices.json', { signal })
  if (!res.ok) return null
  return parseArtefact(await res.json())
}
