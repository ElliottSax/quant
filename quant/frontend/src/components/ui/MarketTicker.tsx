/**
 * MarketTicker Component
 * Scrolling market data ticker — real quotes only.
 *
 * This component previously seeded itself with a hardcoded price table and
 * jittered it with Math.random on an interval, under a green "LIVE" badge.
 * That is fabricated market data and it is gone: the ticker now renders only
 * quotes returned by the market-data API, and renders nothing at all when
 * none are available. Never reintroduce a synthetic fallback here — an empty
 * ticker is honest, a fake one is not.
 */

'use client'

import { useState, useEffect, useRef } from 'react'
import { useMarketQuotes } from '@/lib/hooks'

interface TickerItem {
  symbol: string
  price: number
  change: number
  changePercent: number
  type?: 'index' | 'stock' | 'futures'
}

const TICKER_SYMBOLS = ['SPY', 'QQQ', 'AAPL', 'MSFT', 'NVDA', 'GOOGL', 'TSLA', 'META', 'AMZN']

export function MarketTicker() {
  const [data, setData] = useState<TickerItem[]>([])
  const [isPaused, setIsPaused] = useState(false)
  const tickerRef = useRef<HTMLDivElement>(null)

  const { data: quotesData } = useMarketQuotes(TICKER_SYMBOLS)

  useEffect(() => {
    if (!quotesData?.quotes) return

    const realItems: TickerItem[] = Object.entries(quotesData.quotes)
      .filter(([, quote]) => typeof quote?.price === 'number')
      .map(([symbol, quote]) => ({
        symbol,
        price: quote.price,
        change: quote.change ?? 0,
        changePercent: quote.change_percent ?? 0,
        type: 'stock' as const,
      }))

    setData(realItems)
  }, [quotesData])

  const formatPrice = (price: number, symbol: string) => {
    if (symbol.includes('=F') || ['DJIA', 'S&P 500', 'NASDAQ'].includes(symbol)) {
      return price.toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 })
    }
    return price.toFixed(2)
  }

  // No real quotes, no ticker. The bar is absent rather than invented.
  if (data.length === 0) return null

  return (
    <div
      className="relative overflow-hidden bg-[hsl(220,60%,3%)] border-b border-[hsl(215,40%,12%)]"
      onMouseEnter={() => setIsPaused(true)}
      onMouseLeave={() => setIsPaused(false)}
    >
      <div className="flex items-center">
        {/* Static market label */}
        <div className="flex-shrink-0 px-3 py-1.5 bg-gradient-to-r from-[hsl(45,96%,58%)] to-[hsl(38,92%,50%)] text-[hsl(220,60%,8%)] text-xs font-bold uppercase tracking-wider">
          Markets
        </div>

        {/* Scrolling ticker */}
        <div className="flex-1 overflow-hidden">
          <div
            ref={tickerRef}
            className={`flex items-center gap-0 ${isPaused ? '' : 'animate-ticker'}`}
            style={{ width: 'max-content' }}
          >
            {/* Duplicate items for seamless loop */}
            {[...data, ...data].map((item, idx) => (
              <div
                key={`${item.symbol}-${idx}`}
                className="flex items-center border-r border-[hsl(215,40%,12%)] px-4 py-1.5"
              >
                <span className={`text-xs font-bold mr-2 ${
                  item.type === 'index' ? 'text-[hsl(45,96%,58%)]' :
                  item.type === 'futures' ? 'text-[hsl(210,100%,56%)]' :
                  'text-[hsl(210,20%,70%)]'
                }`}>
                  {item.symbol}
                </span>
                <span className="text-xs font-mono text-white mr-2">
                  {formatPrice(item.price, item.symbol)}
                </span>
                <span className={`text-xs font-mono font-semibold flex items-center gap-0.5 ${
                  item.change >= 0 ? 'text-[hsl(142,71%,55%)]' : 'text-[hsl(0,72%,55%)]'
                }`}>
                  {item.change >= 0 ? '+' : ''}{item.change.toFixed(2)}
                  <span className="text-[10px] ml-1">
                    ({item.change >= 0 ? '+' : ''}{item.changePercent.toFixed(2)}%)
                  </span>
                </span>
              </div>
            ))}
          </div>
        </div>

        {/* Delayed-quote label: the badge describes the feed, never a liveness claim
            the component cannot substantiate. */}
        <div className="flex-shrink-0 px-3 py-1.5 text-[10px] font-mono text-[hsl(215,20%,50%)] border-l border-[hsl(215,40%,12%)] bg-[hsl(220,60%,4%)]">
          END OF DAY
        </div>
      </div>

      {/* Gradient fade edges */}
      <div className="absolute left-[70px] top-0 bottom-0 w-6 bg-gradient-to-r from-[hsl(220,60%,3%)] to-transparent pointer-events-none" />
      <div className="absolute right-[60px] top-0 bottom-0 w-6 bg-gradient-to-l from-[hsl(220,60%,3%)] to-transparent pointer-events-none" />
    </div>
  )
}
