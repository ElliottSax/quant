/**
 * Range windows for the price chart.
 *
 * Windows are derived from the dates in the artefact itself, never from today's clock:
 * the last bar may be several sessions old. A window the history cannot span is reported
 * as unavailable so the page never labels two years of bars "3Y".
 */

export type RangeKey = '1M' | '3M' | '1Y' | '3Y' | 'ALL'

export const RANGES: { key: RangeKey; label: string; months: number | null }[] = [
  { key: '1M', label: '1M', months: 1 },
  { key: '3M', label: '3M', months: 3 },
  { key: '1Y', label: '1Y', months: 12 },
  { key: '3Y', label: '3Y', months: 36 },
  { key: 'ALL', label: 'All', months: null },
]

/** A YYYY-MM-DD date shifted back by whole months, still comparable as a string. */
export function shiftMonths(isoDate: string, months: number): string {
  const [y, m, d] = isoDate.split('-').map(Number)
  const t = new Date(Date.UTC(y, m - 1, d))
  t.setUTCMonth(t.getUTCMonth() - months)
  return t.toISOString().slice(0, 10)
}

/** Which windows the given history actually spans. */
export function rangeAvailability(
  firstDate: string | null,
  lastDate: string | null,
): Record<RangeKey, boolean> {
  const out: Record<RangeKey, boolean> = {
    '1M': false,
    '3M': false,
    '1Y': false,
    '3Y': false,
    ALL: Boolean(firstDate && lastDate),
  }
  if (!firstDate || !lastDate) return out
  for (const r of RANGES) {
    if (r.months === null) continue
    out[r.key] = shiftMonths(lastDate, r.months) >= firstDate
  }
  return out
}

/** Index of the first bar inside the window, given ascending YYYY-MM-DD dates. */
export function windowStartIndex(dates: string[], range: RangeKey): number {
  if (!dates.length) return 0
  const months = RANGES.find((r) => r.key === range)?.months ?? null
  if (months === null) return 0
  const cutoff = shiftMonths(dates[dates.length - 1], months)
  const idx = dates.findIndex((d) => d >= cutoff)
  return idx < 0 ? 0 : idx
}
