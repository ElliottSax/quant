/**
 * MarketTicker Component
 * BigCharts-style real-time scrolling market data ticker
 */

'use client'

import { useState, useEffect, useRef } from 'react'

interface TickerItem {
  symbol: string
  price: number
  change: number
  changePercent: number
  type?: 'index' | 'stock' | 'futures'
}

// Simulated real-time market data
const generateMarketData = (): TickerItem[] => [
  { symbol: 'DJIA', price: 38892.45, change: 156.78, changePercent: 0.40, type: 'index' },
  { symbol: 'S&P 500', price: 5021.84, change: 23.45, changePercent: 0.47, type: 'index' },
  { symbol: 'NASDAQ', price: 15927.90, change: -45.23, changePercent: -0.28, type: 'index' },
  { symbol: 'SPY', price: 502.18, change: 2.34, changePercent: 0.47, type: 'stock' },
  { symbol: 'QQQ', price: 437.52, change: -1.23, changePercent: -0.28, type: 'stock' },
  { symbol: 'AAPL', price: 189.45, change: 1.89, changePercent: 1.01, type: 'stock' },
  { symbol: 'MSFT', price: 412.91, change: 3.45, changePercent: 0.84, type: 'stock' },
  { symbol: 'NVDA', price: 878.35, change: 12.56, changePercent: 1.45, type: 'stock' },
  { symbol: 'GOOGL', price: 141.28, change: 0.78, changePercent: 0.56, type: 'stock' },
  { symbol: 'TSLA', price: 185.67, change: -4.34, changePercent: -2.28, type: 'stock' },
  { symbol: 'META', price: 485.12, change: 8.92, changePercent: 1.87, type: 'stock' },
  { symbol: 'ES=F', price: 5025.50, change: 18.25, changePercent: 0.36, type: 'futures' },
  { symbol: 'NQ=F', price: 17845.75, change: -32.50, changePercent: -0.18, type: 'futures' },
  { symbol: 'VIX', price: 14.23, change: -0.45, changePercent: -3.06, type: 'index' },
]

export function MarketTicker() {
  const [data, setData] = useState<TickerItem[]>(generateMarketData())
  const [isPaused, setIsPaused] = useState(false)
  const tickerRef = useRef<HTMLDivElement>(null)

  // Simulate real-time price updates
  useEffect(() => {
    const interval = setInterval(() => {
      setData(prev => prev.map(item => {
        const volatility = item.type === 'index' ? 0.3 : item.type === 'futures' ? 0.5 : 0.4
        const priceChange = (Math.random() - 0.5) * volatility * (item.price / 100)
        const newPrice = Math.max(0.01, item.price + priceChange)
        const newChange = item.change + priceChange
        const newChangePercent = (newChange / (newPrice - newChange)) * 100

        return {
          ...item,
          price: parseFloat(newPrice.toFixed(2)),
          change: parseFloat(newChange.toFixed(2)),
          changePercent: parseFloat(newChangePercent.toFixed(2)),
        }
      }))
    }, 1500)

    return () => clearInterval(interval)
  }, [])

  const formatPrice = (price: number, symbol: string) => {
    if (symbol.includes('=F') || ['DJIA', 'S&P 500', 'NASDAQ'].includes(symbol)) {
      return price.toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 })
    }
    return price.toFixed(2)
  }

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

        {/* Time display */}
        <div className="flex-shrink-0 px-3 py-1.5 text-[10px] font-mono text-[hsl(215,20%,50%)] border-l border-[hsl(215,40%,12%)] bg-[hsl(220,60%,4%)]">
          <span className="text-[hsl(142,71%,55%)]">●</span> LIVE
        </div>
      </div>

      {/* Gradient fade edges */}
      <div className="absolute left-[70px] top-0 bottom-0 w-6 bg-gradient-to-r from-[hsl(220,60%,3%)] to-transparent pointer-events-none" />
      <div className="absolute right-[60px] top-0 bottom-0 w-6 bg-gradient-to-l from-[hsl(220,60%,3%)] to-transparent pointer-events-none" />
    </div>
  )
}
