'use client'

/**
 * Seasonality screener — the interactive half.
 *
 * Every number rendered here comes from public/data/seasonality.json, which the compute
 * plane writes only when the nightly ingest was clean AND every tier matches the
 * calibration record. There is no fallback: if the file is missing the page says so.
 * Nothing on this page is a recommendation — it describes what the historical record
 * contains and refuses to say more.
 */

import { useMemo, useState } from 'react'

export interface Cell {
  symbol: string
  month: number
  month_name: string
  tier: string
  n: number
  diff_pp: number | null
  ci_low_pp: number | null
  ci_high_pp: number | null
  p: number | null
  q: number | null
  stable: boolean
  failure_years: number[]
  boundary_rule_applied: boolean
}

export interface Dataset {
  generated_at: string
  spec_version: string
  provider: string
  data_start: string
  data_vintage: string
  universe: string[]
  family_size: number
  fdr_q: number
  thresholds: { gradeable_n: number; robust_n: number }
  cells: Cell[]
}

const TIER_ORDER: Record<string, number> = {
  Robust: 0, Weak: 1, Folklore: 2, 'Insufficient history': 3,
}

function tierClass(tier: string) {
  switch (tier) {
    case 'Robust': return 'text-emerald-400 bg-emerald-500/10 border-emerald-500/30'
    case 'Weak': return 'text-amber-400 bg-amber-500/10 border-amber-500/30'
    case 'Folklore': return 'text-slate-400 bg-slate-500/10 border-slate-500/30'
    default: return 'text-slate-500 bg-slate-700/20 border-slate-600/30'
  }
}

export function ScannerClient({ data }: { data: Dataset }) {
  const [symbol, setSymbol] = useState('all')
  const [month, setMonth] = useState<'all' | 'current' | number>('current')
  const [tier, setTier] = useState('all')
  const [minN, setMinN] = useState(0)

  // "Opens this month" is a calendar fact about which window is next, not a claim that
  // anything will happen in it.
  const currentMonth = new Date().getUTCMonth() + 1

  const rows = useMemo(() => {
    let r = data.cells.slice()
    if (symbol !== 'all') r = r.filter(c => c.symbol === symbol)
    if (month === 'current') r = r.filter(c => c.month === currentMonth)
    else if (month !== 'all') r = r.filter(c => c.month === month)
    if (tier !== 'all') r = r.filter(c => c.tier === tier)
    if (minN > 0) r = r.filter(c => c.n >= minN)
    return r.sort((a, b) =>
      (TIER_ORDER[a.tier] ?? 9) - (TIER_ORDER[b.tier] ?? 9) ||
      (a.q ?? 1) - (b.q ?? 1) ||
      a.symbol.localeCompare(b.symbol))
  }, [data.cells, symbol, month, tier, minN, currentMonth])

  const counts = useMemo(() => {
    const c: Record<string, number> = {}
    for (const cell of data.cells) c[cell.tier] = (c[cell.tier] ?? 0) + 1
    return c
  }, [data.cells])

  return (
    <div className="space-y-6">
      <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
        {['Robust', 'Weak', 'Folklore', 'Insufficient history'].map(t => (
          <div key={t} className="glass-card p-4">
            <div className="text-2xl font-bold font-mono">{counts[t] ?? 0}</div>
            <div className="text-xs text-slate-400 mt-1">{t}</div>
          </div>
        ))}
      </div>

      {counts['Robust'] === 0 && (
        <div className="glass-card p-5 border border-amber-500/30">
          <h2 className="font-bold mb-1">Nothing clears the bar</h2>
          <p className="text-sm text-slate-400">
            No cell in this universe reaches <strong>Robust</strong>. {data.family_size} tests were
            run together and corrected for that fact; the strongest result still has a false-discovery
            rate far above the {(data.fdr_q * 100).toFixed(0)}% threshold. Patterns that look
            significant on their own stop looking significant once you count how many were examined —
            that is the finding, and we publish it rather than hide it.
          </p>
        </div>
      )}

      <div className="glass-card p-4 flex flex-wrap gap-4 items-end">
        <label className="text-sm">
          <span className="block text-xs text-slate-400 mb-1">Symbol</span>
          <select value={symbol} onChange={e => setSymbol(e.target.value)}
                  className="bg-slate-800 border border-slate-700 rounded px-3 py-1.5 text-sm">
            <option value="all">All ({data.universe.length})</option>
            {data.universe.map(s => <option key={s} value={s}>{s}</option>)}
          </select>
        </label>
        <label className="text-sm">
          <span className="block text-xs text-slate-400 mb-1">Window</span>
          <select value={String(month)}
                  onChange={e => setMonth(e.target.value === 'all' || e.target.value === 'current'
                    ? (e.target.value as 'all' | 'current') : Number(e.target.value))}
                  className="bg-slate-800 border border-slate-700 rounded px-3 py-1.5 text-sm">
            <option value="current">Opens this month</option>
            <option value="all">All months</option>
            {Array.from({ length: 12 }, (_, i) => i + 1).map(m => (
              <option key={m} value={m}>
                {new Date(Date.UTC(2000, m - 1, 1)).toLocaleString('en', { month: 'long', timeZone: 'UTC' })}
              </option>
            ))}
          </select>
        </label>
        <label className="text-sm">
          <span className="block text-xs text-slate-400 mb-1">Verdict</span>
          <select value={tier} onChange={e => setTier(e.target.value)}
                  className="bg-slate-800 border border-slate-700 rounded px-3 py-1.5 text-sm">
            <option value="all">Any</option>
            {['Robust', 'Weak', 'Folklore', 'Insufficient history'].map(t => (
              <option key={t} value={t}>{t}</option>
            ))}
          </select>
        </label>
        <label className="text-sm">
          <span className="block text-xs text-slate-400 mb-1">Min. observations</span>
          <input type="number" min={0} max={40} value={minN}
                 onChange={e => setMinN(Number(e.target.value) || 0)}
                 className="bg-slate-800 border border-slate-700 rounded px-3 py-1.5 text-sm w-24" />
        </label>
        <div className="text-sm text-slate-400 ml-auto">{rows.length} of {data.cells.length}</div>
      </div>

      <div className="glass-card overflow-x-auto">
        <table className="w-full text-sm">
          <thead>
            <tr className="text-left text-xs uppercase tracking-wide text-slate-400 border-b border-slate-700">
              <th className="p-3">Symbol</th>
              <th className="p-3">Month</th>
              <th className="p-3 text-right">n</th>
              <th className="p-3 text-right">Difference</th>
              <th className="p-3 text-right">95% interval</th>
              <th className="p-3 text-right">p</th>
              <th className="p-3 text-right">q</th>
              <th className="p-3 text-right">Years against</th>
              <th className="p-3">Verdict</th>
            </tr>
          </thead>
          <tbody>
            {rows.map(c => (
              <tr key={`${c.symbol}-${c.month}`} className="border-b border-slate-800/60">
                <td className="p-3 font-mono font-semibold">{c.symbol}</td>
                <td className="p-3">{c.month_name}</td>
                <td className="p-3 text-right font-mono tabular-nums">{c.n}</td>
                <td className="p-3 text-right font-mono tabular-nums">
                  {c.diff_pp === null ? '—' : `${c.diff_pp > 0 ? '+' : ''}${c.diff_pp.toFixed(2)} pp`}
                </td>
                <td className="p-3 text-right font-mono tabular-nums text-slate-400">
                  {c.ci_low_pp === null || c.ci_high_pp === null
                    ? '—'
                    : `[${c.ci_low_pp.toFixed(2)}, ${c.ci_high_pp.toFixed(2)}]`}
                </td>
                <td className="p-3 text-right font-mono tabular-nums">
                  {c.p === null ? '—' : c.p < 0.001 ? '<0.001' : c.p.toFixed(4)}
                </td>
                <td className="p-3 text-right font-mono tabular-nums">
                  {c.q === null ? '—' : c.q.toFixed(3)}
                </td>
                <td className="p-3 text-right font-mono tabular-nums text-slate-400">
                  {c.failure_years.length}/{c.n}
                </td>
                <td className="p-3">
                  <span className={`inline-block text-xs font-semibold px-2 py-0.5 rounded border ${tierClass(c.tier)}`}>
                    {c.tier}
                  </span>
                  {c.boundary_rule_applied && (
                    <span title="Decided conservatively: the p-value sits within Monte Carlo error of the threshold"
                          className="ml-2 text-[10px] font-mono text-blue-400 border border-blue-400/40 rounded px-1">
                      MC
                    </span>
                  )}
                </td>
              </tr>
            ))}
            {rows.length === 0 && (
              <tr><td colSpan={9} className="p-6 text-center text-slate-400">
                No cells match these filters.
              </td></tr>
            )}
          </tbody>
        </table>
      </div>
    </div>
  )
}
