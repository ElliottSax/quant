/**
 * Market Overview Widget
 * Live market snapshot with indices and trending stocks
 */

'use client'

import { useState, useEffect } from 'react'

export function MarketOverview() {
  const [activeTab, setActiveTab] = useState<'indices' | 'trending' | 'politicians'>('indices')

  const indices = [
    { symbol: 'S&P 500', value: 4783.45, change: 23.67, changePercent: 0.50 },
    { symbol: 'DOW', value: 37305.16, change: -45.23, changePercent: -0.12 },
    { symbol: 'NASDAQ', value: 15188.39, change: 87.54, changePercent: 0.58 },
    { symbol: 'RUSSELL', value: 2027.45, change: 5.32, changePercent: 0.26 },
  ]

  const trending = [
    { symbol: 'NVDA', name: 'NVIDIA Corp', price: 495.22, change: 12.34, volume: '52.3M' },
    { symbol: 'TSLA', name: 'Tesla Inc', price: 248.48, change: -3.67, volume: '89.1M' },
    { symbol: 'AAPL', name: 'Apple Inc', price: 185.92, change: 2.15, volume: '45.7M' },
    { symbol: 'META', name: 'Meta Platforms', price: 352.78, change: 8.92, volume: '23.4M' },
  ]

  const politicianStocks = [
    { symbol: 'MSFT', trades: 23, direction: 'buy', price: 378.91, politicians: 8 },
    { symbol: 'GOOGL', trades: 18, direction: 'buy', price: 140.23, politicians: 6 },
    { symbol: 'JPM', trades: 15, direction: 'sell', price: 167.45, politicians: 5 },
    { symbol: 'XOM', trades: 12, direction: 'buy', price: 102.34, politicians: 4 },
  ]

  return (
    <div className="glass-strong rounded-xl border border-border/50 p-6">
      <div className="flex items-center justify-between mb-6">
        <div className="flex items-center gap-2">
          <div className="w-10 h-10 rounded-lg bg-gradient-to-br from-green-500 to-emerald-500 flex items-center justify-center">
            <svg className="w-5 h-5 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 7h8m0 0v8m0-8l-8 8-4-4-6 6" />
            </svg>
          </div>
          <h3 className="text-lg font-bold">Market Overview</h3>
        </div>
        <div className="flex items-center gap-2 text-xs">
          <span className="relative flex h-2 w-2">
            <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-green-400 opacity-75"></span>
            <span className="relative inline-flex rounded-full h-2 w-2 bg-green-500"></span>
          </span>
          <span className="text-muted-foreground">Live</span>
        </div>
      </div>

      {/* Tabs */}
      <div className="flex gap-2 mb-4 border-b border-border/50">
        <TabButton
          active={activeTab === 'indices'}
          onClick={() => setActiveTab('indices')}
        >
          Indices
        </TabButton>
        <TabButton
          active={activeTab === 'trending'}
          onClick={() => setActiveTab('trending')}
        >
          Trending
        </TabButton>
        <TabButton
          active={activeTab === 'politicians'}
          onClick={() => setActiveTab('politicians')}
        >
          Politicians
        </TabButton>
      </div>

      {/* Content */}
      <div className="space-y-3">
        {activeTab === 'indices' && indices.map((index, i) => (
          <div key={i} className="flex items-center justify-between p-3 rounded-lg hover:bg-muted/30 transition-colors">
            <div className="flex-1">
              <p className="font-semibold">{index.symbol}</p>
            </div>
            <div className="text-right">
              <p className="font-bold">{index.value.toLocaleString()}</p>
              <p className={`text-sm font-semibold ${index.change >= 0 ? 'text-green-500' : 'text-red-500'}`}>
                {index.change >= 0 ? '+' : ''}{index.change} ({index.changePercent >= 0 ? '+' : ''}{index.changePercent}%)
              </p>
            </div>
          </div>
        ))}

        {activeTab === 'trending' && trending.map((stock, i) => (
          <div key={i} className="flex items-center justify-between p-3 rounded-lg hover:bg-muted/30 transition-colors group cursor-pointer">
            <div className="flex-1">
              <p className="font-bold group-hover:text-primary transition-colors">{stock.symbol}</p>
              <p className="text-xs text-muted-foreground">{stock.name}</p>
            </div>
            <div className="text-right">
              <p className="font-bold">${stock.price}</p>
              <div className="flex items-center gap-2 justify-end">
                <p className={`text-sm font-semibold ${stock.change >= 0 ? 'text-green-500' : 'text-red-500'}`}>
                  {stock.change >= 0 ? '+' : ''}{stock.change}
                </p>
                <span className="text-xs text-muted-foreground">{stock.volume}</span>
              </div>
            </div>
          </div>
        ))}

        {activeTab === 'politicians' && politicianStocks.map((stock, i) => (
          <div key={i} className="flex items-center justify-between p-3 rounded-lg hover:bg-muted/30 transition-colors group cursor-pointer">
            <div className="flex-1">
              <div className="flex items-center gap-2 mb-1">
                <p className="font-bold group-hover:text-primary transition-colors">{stock.symbol}</p>
                <span className={`text-xs px-2 py-0.5 rounded-full font-bold ${
                  stock.direction === 'buy'
                    ? 'bg-green-500/10 text-green-500'
                    : 'bg-red-500/10 text-red-500'
                }`}>
                  {stock.direction.toUpperCase()}
                </span>
              </div>
              <p className="text-xs text-muted-foreground">
                {stock.trades} trades by {stock.politicians} politicians
              </p>
            </div>
            <div className="text-right">
              <p className="font-bold">${stock.price}</p>
              <p className="text-xs text-muted-foreground">Last 30 days</p>
            </div>
          </div>
        ))}
      </div>

      {/* View More Link */}
      <div className="mt-4 pt-4 border-t border-border/50 text-center">
        <button className="text-sm text-primary hover:underline font-medium">
          View Full Market Data →
        </button>
      </div>
    </div>
  )
}

function TabButton({ active, onClick, children }: { active: boolean; onClick: () => void; children: React.ReactNode }) {
  return (
    <button
      onClick={onClick}
      className={`px-4 py-2 text-sm font-medium rounded-t-lg transition-colors ${
        active
          ? 'text-primary border-b-2 border-primary'
          : 'text-muted-foreground hover:text-foreground'
      }`}
    >
      {children}
    </button>
  )
}
