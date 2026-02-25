/**
 * Top Movers Widget
 * Biggest gainers and losers of the day
 */

'use client'

import { useState } from 'react'

export function TopMovers() {
  const [activeTab, setActiveTab] = useState<'gainers' | 'losers'>('gainers')

  const gainers = [
    { symbol: 'SMCI', name: 'Super Micro Computer', price: 425.67, change: 45.23, changePercent: 11.89 },
    { symbol: 'COIN', name: 'Coinbase Global', price: 145.89, change: 12.34, changePercent: 9.23 },
    { symbol: 'RIOT', name: 'Riot Platforms', price: 12.45, change: 1.02, changePercent: 8.92 },
    { symbol: 'UPST', name: 'Upstart Holdings', price: 34.56, change: 2.78, changePercent: 8.74 },
  ]

  const losers = [
    { symbol: 'NKLA', name: 'Nikola Corp', price: 0.89, change: -0.12, changePercent: -11.88 },
    { symbol: 'LCID', name: 'Lucid Group', price: 3.45, change: -0.38, changePercent: -9.92 },
    { symbol: 'HOOD', name: 'Robinhood Markets', price: 11.23, change: -0.98, changePercent: -8.03 },
    { symbol: 'PLUG', name: 'Plug Power', price: 4.56, change: -0.36, changePercent: -7.32 },
  ]

  const stocks = activeTab === 'gainers' ? gainers : losers

  return (
    <div className="glass-strong rounded-xl border border-border/50 p-6">
      <div className="flex items-center gap-2 mb-6">
        <div className={`w-10 h-10 rounded-lg bg-gradient-to-br ${
          activeTab === 'gainers'
            ? 'from-green-500 to-emerald-500'
            : 'from-red-500 to-rose-500'
        } flex items-center justify-center transition-all duration-300`}>
          <svg className="w-5 h-5 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth={2}
              d={activeTab === 'gainers'
                ? 'M13 7h8m0 0v8m0-8l-8 8-4-4-6 6'
                : 'M13 17h8m0 0V9m0 8l-8-8-4 4-6-6'
              }
            />
          </svg>
        </div>
        <h3 className="text-lg font-bold">Top Movers Today</h3>
      </div>

      {/* Tabs */}
      <div className="flex gap-2 mb-4">
        <button
          onClick={() => setActiveTab('gainers')}
          className={`flex-1 px-4 py-2 rounded-lg font-semibold text-sm transition-all ${
            activeTab === 'gainers'
              ? 'bg-green-500/10 text-green-500 border border-green-500/20'
              : 'bg-muted/30 text-muted-foreground hover:bg-muted/50'
          }`}
        >
          Top Gainers
        </button>
        <button
          onClick={() => setActiveTab('losers')}
          className={`flex-1 px-4 py-2 rounded-lg font-semibold text-sm transition-all ${
            activeTab === 'losers'
              ? 'bg-red-500/10 text-red-500 border border-red-500/20'
              : 'bg-muted/30 text-muted-foreground hover:bg-muted/50'
          }`}
        >
          Top Losers
        </button>
      </div>

      {/* List */}
      <div className="space-y-3">
        {stocks.map((stock, i) => (
          <div
            key={i}
            className="flex items-center justify-between p-3 rounded-lg hover:bg-muted/30 transition-colors group cursor-pointer"
          >
            <div className="flex items-center gap-3 flex-1">
              <div className={`w-8 h-8 rounded-lg flex items-center justify-center font-bold text-sm ${
                activeTab === 'gainers'
                  ? 'bg-green-500/10 text-green-500'
                  : 'bg-red-500/10 text-red-500'
              }`}>
                {i + 1}
              </div>
              <div className="flex-1">
                <p className="font-bold group-hover:text-primary transition-colors">{stock.symbol}</p>
                <p className="text-xs text-muted-foreground truncate">{stock.name}</p>
              </div>
            </div>
            <div className="text-right">
              <p className="font-bold">${stock.price}</p>
              <p className={`text-sm font-bold ${stock.change >= 0 ? 'text-green-500' : 'text-red-500'}`}>
                {stock.change >= 0 ? '+' : ''}{stock.changePercent}%
              </p>
            </div>
          </div>
        ))}
      </div>

      {/* Footer */}
      <div className="mt-4 pt-4 border-t border-border/50 text-center">
        <button className="text-sm text-primary hover:underline font-medium">
          View All Movers →
        </button>
      </div>
    </div>
  )
}
