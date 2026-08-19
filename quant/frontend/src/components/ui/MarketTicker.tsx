/**
 * MarketTicker — real end-of-day closes only.
 *
 * History: this component seeded itself with a hardcoded price table and jittered it
 * with Math.random on an interval, under a green "LIVE" badge. That was removed, but the
 * replacement read `quotesData.quotes` from a hook that could never return anything —
 * the client namespace was wrong AND the endpoints it called do not exist on the
 * deployed backend — so the honest version rendered nothing at all.
 *
 * It now reads the same published artefact the rest of the site uses:
 * /data/prices.json, written by the compute plane from adjusted end-of-day bars, only
 * when the nightly ingest was clean. The label says END OF DAY because that is what it
 * is; there is no live feed behind this site and the bar must not imply one.
 *
 * No fallback. If the artefact is missing, the ticker is absent — an empty bar is
 * honest, an invented one is not.
 */

'use client'

import { useState, useEffect, useRef } from 'react'

interface TickerItem {
  symbol: string
  close: number
  change: number
  changePercent: number
}

interface PricesArtefact {
  generated_at: string
  latest: Record<string, { day: string; close: number; change: number; change_pct: number | null }>
  symbols: string[]
}

export function MarketTicker() {
  const [data, setData] = useState<TickerItem[]>([])
  const [asOf, setAsOf] = useState<string | null>(null)
  const [isPaused, setIsPaused] = useState(false)
  const tickerRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    let cancelled = false
    fetch('/data/prices.json')
      .then(r => (r.ok ? r.json() : Promise.reject(new Error(String(r.status)))))
      .then((p: PricesArtefact) => {
        if (cancelled || !p?.latest) return
        const items = Object.entries(p.latest)
          .filter(([, v]) => typeof v?.close === 'number' && typeof v?.change === 'number')
          .map(([symbol, v]) => ({
            symbol,
            close: v.close,
            change: v.change,
            changePercent: typeof v.change_pct === 'number' ? v.change_pct : 0,
          }))
          .sort((a, b) => a.symbol.localeCompare(b.symbol))
        setData(items)
        const days = Object.values(p.latest).map(v => v.day).filter(Boolean).sort()
        setAsOf(days[days.length - 1] ?? null)
      })
      .catch(() => {
        // Deliberately silent and empty: a ticker that cannot show real closes shows none.
      })
    return () => { cancelled = true }
  }, [])

  if (data.length === 0) return null

  return (
    <div
      className="relative overflow-hidden bg-[hsl(220,60%,3%)] border-b border-[hsl(215,40%,12%)]"
      onMouseEnter={() => setIsPaused(true)}
      onMouseLeave={() => setIsPaused(false)}
    >
      <div className="flex items-center">
        <div className="flex-shrink-0 px-3 py-1.5 bg-gradient-to-r from-[hsl(45,96%,58%)] to-[hsl(38,92%,50%)] text-[hsl(220,60%,8%)] text-xs font-bold uppercase tracking-wider">
          Markets
        </div>

        <div className="flex-1 overflow-hidden">
          <div
            ref={tickerRef}
            className={`flex items-center gap-0 ${isPaused ? '' : 'animate-ticker'}`}
            style={{ width: 'max-content' }}
          >
            {[...data, ...data].map((item, idx) => (
              <div
                key={`${item.symbol}-${idx}`}
                className="flex items-center border-r border-[hsl(215,40%,12%)] px-4 py-1.5"
              >
                <span className="text-xs font-bold mr-2 text-[hsl(210,20%,70%)]">
                  {item.symbol}
                </span>
                <span className="text-xs font-mono text-white mr-2">
                  {item.close.toFixed(2)}
                </span>
                <span className={`text-xs font-mono font-semibold flex items-center gap-0.5 ${
                  item.change >= 0 ? 'text-[hsl(142,71%,55%)]' : 'text-[hsl(0,72%,55%)]'
                }`}>
                  {item.change >= 0 ? '+' : ''}{item.change.toFixed(2)}
                  <span className="text-[10px] ml-1">
                    ({item.changePercent >= 0 ? '+' : ''}{item.changePercent.toFixed(2)}%)
                  </span>
                </span>
              </div>
            ))}
          </div>
        </div>

        {/* Describes the feed rather than asserting a liveness the site does not have. */}
        <div className="flex-shrink-0 px-3 py-1.5 text-[10px] font-mono text-[hsl(215,20%,50%)] border-l border-[hsl(215,40%,12%)] bg-[hsl(220,60%,4%)] whitespace-nowrap">
          END OF DAY{asOf ? ` · ${asOf}` : ''}
        </div>
      </div>

      <div className="absolute left-[70px] top-0 bottom-0 w-6 bg-gradient-to-r from-[hsl(220,60%,3%)] to-transparent pointer-events-none" />
      <div className="absolute right-[130px] top-0 bottom-0 w-6 bg-gradient-to-l from-[hsl(220,60%,3%)] to-transparent pointer-events-none" />
    </div>
  )
}
