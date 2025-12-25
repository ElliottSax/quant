/**
 * MarketTicker Component
 * Real-time scrolling market data ticker for the navbar
 */

'use client'

import { useState, useEffect, useRef } from 'react'

interface TickerItem {
  symbol: string
  price: number
  change: number
  changePercent: number
}

// Simulated real-time market data
const generateMarketData = (): TickerItem[] => [
  { symbol: 'SPY', price: 478.52, change: 2.34, changePercent: 0.49 },
  { symbol: 'QQQ', price: 412.18, change: -1.23, changePercent: -0.30 },
  { symbol: 'AAPL', price: 189.45, change: 1.89, changePercent: 1.01 },
  { symbol: 'MSFT', price: 378.91, change: 3.45, changePercent: 0.92 },
  { symbol: 'NVDA', price: 495.22, change: -4.56, changePercent: -0.91 },
  { symbol: 'GOOGL', price: 141.28, change: 0.78, changePercent: 0.56 },
  { symbol: 'TSLA', price: 248.67, change: -2.34, changePercent: -0.93 },
  { symbol: 'META', price: 358.91, change: 4.12, changePercent: 1.16 },
]

export function MarketTicker() {
  const [data, setData] = useState<TickerItem[]>(generateMarketData())
  const [isPaused, setIsPaused] = useState(false)
  const tickerRef = useRef<HTMLDivElement>(null)

  // Simulate real-time price updates
  useEffect(() => {
    const interval = setInterval(() => {
      setData(prev => prev.map(item => {
        const priceChange = (Math.random() - 0.5) * 0.5
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
    }, 2000)

    return () => clearInterval(interval)
  }, [])

  return (
    <div
      className="relative overflow-hidden bg-slate-900/50 border-b border-slate-800/50"
      onMouseEnter={() => setIsPaused(true)}
      onMouseLeave={() => setIsPaused(false)}
    >
      <div
        ref={tickerRef}
        className={`flex items-center gap-8 py-1.5 px-4 ${isPaused ? '' : 'animate-ticker'}`}
        style={{ width: 'max-content' }}
      >
        {/* Duplicate items for seamless loop */}
        {[...data, ...data].map((item, idx) => (
          <div
            key={`${item.symbol}-${idx}`}
            className="flex items-center gap-2 text-xs font-medium whitespace-nowrap"
          >
            <span className="text-slate-400 font-mono">{item.symbol}</span>
            <span className="text-white font-semibold">${item.price.toFixed(2)}</span>
            <span className={`flex items-center gap-0.5 ${
              item.change >= 0 ? 'text-emerald-400' : 'text-red-400'
            }`}>
              {item.change >= 0 ? (
                <svg className="w-3 h-3" fill="currentColor" viewBox="0 0 20 20">
                  <path fillRule="evenodd" d="M5.293 9.707a1 1 0 010-1.414l4-4a1 1 0 011.414 0l4 4a1 1 0 01-1.414 1.414L11 7.414V15a1 1 0 11-2 0V7.414L6.707 9.707a1 1 0 01-1.414 0z" clipRule="evenodd" />
                </svg>
              ) : (
                <svg className="w-3 h-3" fill="currentColor" viewBox="0 0 20 20">
                  <path fillRule="evenodd" d="M14.707 10.293a1 1 0 010 1.414l-4 4a1 1 0 01-1.414 0l-4-4a1 1 0 111.414-1.414L9 12.586V5a1 1 0 012 0v7.586l2.293-2.293a1 1 0 011.414 0z" clipRule="evenodd" />
                </svg>
              )}
              <span>{Math.abs(item.changePercent).toFixed(2)}%</span>
            </span>
          </div>
        ))}
      </div>

      {/* Gradient fade edges */}
      <div className="absolute left-0 top-0 bottom-0 w-8 bg-gradient-to-r from-slate-900/90 to-transparent pointer-events-none" />
      <div className="absolute right-0 top-0 bottom-0 w-8 bg-gradient-to-l from-slate-900/90 to-transparent pointer-events-none" />
    </div>
  )
}
