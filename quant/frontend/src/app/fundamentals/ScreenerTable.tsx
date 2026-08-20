'use client'

import { useMemo, useState } from 'react'

export interface Row {
  cik: number
  ticker: string
  name: string
  assets_musd: number
  fy_start: string
  fy_end: string
  asset_growth: number | null
  accruals: number | null
  net_issuance: number | null
}

type SignalKey = 'asset_growth' | 'accruals' | 'net_issuance'

const SIGNALS: { key: SignalKey; label: string; short: string }[] = [
  { key: 'asset_growth', label: 'Asset growth', short: 'Asset growth' },
  { key: 'accruals', label: 'Accruals', short: 'Accruals' },
  { key: 'net_issuance', label: 'Net issuance', short: 'Net issuance' },
]

const fmtPct = (v: number | null) => (v === null ? '—' : `${(v * 100).toFixed(1)}%`)

function fmtAssets(m: number) {
  if (m >= 1e6) return `$${(m / 1e6).toFixed(2)}T`
  if (m >= 1e3) return `$${(m / 1e3).toFixed(1)}B`
  return `$${m.toFixed(0)}M`
}

/** Colour scales with the magnitude, but only within a band that is actually meaningful.
 *  A ±5% accrual and a ±500% one should not look the same, and a 900% outlier should not
 *  make everything else look neutral, so the scale saturates at the band edge. */
function tone(v: number | null, band: number) {
  if (v === null) return 'text-slate-500'
  const t = Math.min(Math.abs(v) / band, 1)
  if (t < 0.25) return 'text-slate-300'
  if (v > 0) return t > 0.7 ? 'text-rose-300' : 'text-rose-400/70'
  return t > 0.7 ? 'text-emerald-300' : 'text-emerald-400/70'
}

const BAND: Record<SignalKey, number> = { asset_growth: 0.5, accruals: 0.2, net_issuance: 0.25 }

export default function ScreenerTable({ rows }: { rows: Row[] }) {
  const [sortKey, setSortKey] = useState<SignalKey | 'assets_musd'>('assets_musd')
  const [asc, setAsc] = useState(false)
  const [query, setQuery] = useState('')
  const [minAssets, setMinAssets] = useState(0)
  const [limit, setLimit] = useState(50)

  const filtered = useMemo(() => {
    const q = query.trim().toUpperCase()
    let out = rows
    if (q) out = out.filter((r) => r.ticker.includes(q) || r.name.toUpperCase().includes(q))
    if (minAssets > 0) out = out.filter((r) => r.assets_musd >= minAssets)

    return [...out].sort((a, b) => {
      const av = a[sortKey]
      const bv = b[sortKey]
      // Companies missing a signal sort to the bottom in both directions rather than
      // being treated as zero, which would place them in the middle of the ranking as
      // though a value had been observed.
      if (av === null && bv === null) return 0
      if (av === null) return 1
      if (bv === null) return -1
      return asc ? av - bv : bv - av
    })
  }, [rows, query, minAssets, sortKey, asc])

  const clickSort = (k: SignalKey | 'assets_musd') => {
    if (k === sortKey) setAsc((v) => !v)
    else {
      setSortKey(k)
      // Assets are most useful largest-first; the signals are most useful smallest-first,
      // because for all three the low end is the side the research associates with
      // higher subsequent returns.
      setAsc(k !== 'assets_musd')
    }
  }

  const arrow = (k: string) => (sortKey === k ? (asc ? ' ▲' : ' ▼') : '')
  const th =
    'px-3 py-2 text-right text-xs font-semibold uppercase tracking-wide text-[hsl(215,20%,60%)] ' +
    'cursor-pointer select-none hover:text-indigo-400 transition-colors whitespace-nowrap'

  return (
    <div>
      <div className="flex flex-wrap items-end gap-4 mb-4">
        <label className="text-xs">
          <span className="block font-semibold uppercase tracking-wide text-[hsl(215,20%,60%)] mb-1.5">
            Ticker or name
          </span>
          <input
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            placeholder="AAPL"
            className="w-44 rounded-md border border-[hsl(215,40%,18%)] bg-[hsl(220,55%,7%)] px-3 py-1.5 text-sm text-slate-200 placeholder:text-[hsl(215,20%,35%)] focus:border-indigo-500 focus:outline-none"
          />
        </label>
        <label className="text-xs">
          <span className="block font-semibold uppercase tracking-wide text-[hsl(215,20%,60%)] mb-1.5">
            Minimum assets
          </span>
          <select
            value={minAssets}
            onChange={(e) => setMinAssets(Number(e.target.value))}
            className="rounded-md border border-[hsl(215,40%,18%)] bg-[hsl(220,55%,7%)] px-3 py-1.5 text-sm text-slate-200"
          >
            <option value={0}>Any</option>
            <option value={1000}>$1B+</option>
            <option value={10000}>$10B+</option>
            <option value={100000}>$100B+</option>
          </select>
        </label>
        <label className="text-xs">
          <span className="block font-semibold uppercase tracking-wide text-[hsl(215,20%,60%)] mb-1.5">
            Show
          </span>
          <select
            value={limit}
            onChange={(e) => setLimit(Number(e.target.value))}
            className="rounded-md border border-[hsl(215,40%,18%)] bg-[hsl(220,55%,7%)] px-3 py-1.5 text-sm text-slate-200"
          >
            {[25, 50, 100, 250].map((k) => (
              <option key={k} value={k}>{k} rows</option>
            ))}
          </select>
        </label>
        <div className="text-xs text-[hsl(215,20%,45%)] pb-2">
          {filtered.length.toLocaleString()} of {rows.length.toLocaleString()} companies match
        </div>
      </div>

      <div className="overflow-x-auto rounded-xl border border-[hsl(215,40%,18%)]">
        <table className="w-full text-sm">
          <thead className="bg-[hsl(220,55%,7%)]">
            <tr>
              <th className="px-3 py-2 text-left text-xs font-semibold uppercase tracking-wide text-[hsl(215,20%,60%)]">
                Company
              </th>
              <th className={th} onClick={() => clickSort('assets_musd')}>
                Assets{arrow('assets_musd')}
              </th>
              {SIGNALS.map((s) => (
                <th key={s.key} className={th} onClick={() => clickSort(s.key)}>
                  {s.short}{arrow(s.key)}
                </th>
              ))}
              <th className="px-3 py-2 text-right text-xs font-semibold uppercase tracking-wide text-[hsl(215,20%,60%)] whitespace-nowrap">
                Fiscal year
              </th>
            </tr>
          </thead>
          <tbody>
            {filtered.slice(0, limit).map((r) => (
              <tr key={r.cik} className="border-t border-[hsl(215,40%,12%)] hover:bg-[hsl(220,55%,11%)]">
                <td className="px-3 py-2">
                  <a
                    href={`https://www.sec.gov/cgi-bin/browse-edgar?action=getcompany&CIK=${r.cik}&type=10-K`}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="font-mono font-semibold text-indigo-400 hover:text-indigo-300"
                  >
                    {r.ticker}
                  </a>
                  <span className="ml-2 text-xs text-[hsl(215,20%,50%)]">{r.name}</span>
                </td>
                <td className="px-3 py-2 text-right font-mono tabular-nums text-slate-300">
                  {fmtAssets(r.assets_musd)}
                </td>
                {SIGNALS.map((s) => (
                  <td
                    key={s.key}
                    className={`px-3 py-2 text-right font-mono tabular-nums ${tone(r[s.key], BAND[s.key])}`}
                  >
                    {fmtPct(r[s.key])}
                  </td>
                ))}
                <td className="px-3 py-2 text-right font-mono text-xs text-[hsl(215,20%,45%)] whitespace-nowrap">
                  {r.fy_end}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {filtered.length === 0 && (
        <p className="mt-4 rounded-lg border border-amber-500/30 bg-amber-500/5 p-4 text-sm text-amber-200/80">
          No company in the screened universe matches that filter. The universe is filers
          that reported both an annual income statement and a matching balance sheet, so
          it is not the whole market — see the coverage figures below.
        </p>
      )}

      <p className="mt-3 text-xs text-[hsl(215,20%,45%)]">
        Green is the end of each range the cited research associates with higher subsequent
        returns; red the other end. That is a historical association from the papers cited
        below, not a prediction, and not a recommendation. A dash means the company did not
        report the tags that signal needs.
      </p>
    </div>
  )
}
