/**
 * Compare Politicians Page
 * Side-by-side comparison of politician trading records
 */

'use client'

import { useState } from 'react'

export default function ComparePage() {
  const [selected1, setSelected1] = useState('')
  const [selected2, setSelected2] = useState('')

  const politicians = [
    'Nancy Pelosi',
    'Paul Pelosi Jr',
    'Dan Crenshaw',
    'Brian Higgins',
    'Josh Gottheimer',
    'Debbie Wasserman Schultz',
  ]

  const mockData1 = {
    name: selected1,
    party: 'Democratic',
    state: 'CA',
    totalTrades: 247,
    totalValue: '$43.2M',
    avgReturn: '23.4%',
    winRate: '68%',
    topSectors: ['Technology', 'Finance', 'Healthcare'],
    recentTrades: [
      { date: '2024-01-15', symbol: 'NVDA', type: 'BUY', value: '$2.5M', return: '+34%' },
      { date: '2024-01-10', symbol: 'MSFT', type: 'BUY', value: '$1.8M', return: '+12%' },
      { date: '2024-01-05', symbol: 'AAPL', type: 'SELL', value: '$3.2M', return: '+45%' },
    ],
  }

  const mockData2 = {
    name: selected2,
    party: 'Republican',
    state: 'TX',
    totalTrades: 189,
    totalValue: '$28.7M',
    avgReturn: '18.7%',
    winRate: '62%',
    topSectors: ['Energy', 'Defense', 'Technology'],
    recentTrades: [
      { date: '2024-01-12', symbol: 'XOM', type: 'BUY', value: '$1.2M', return: '+8%' },
      { date: '2024-01-08', symbol: 'LMT', type: 'BUY', value: '$900K', return: '+15%' },
      { date: '2024-01-03', symbol: 'BA', type: 'SELL', value: '$1.5M', return: '+22%' },
    ],
  }

  const showComparison = selected1 && selected2

  return (
    <div className="space-y-8">
      {/* Header */}
      <div className="animate-fade-in">
        <h1 className="text-4xl md:text-5xl font-bold mb-3 bg-clip-text text-transparent bg-gradient-to-r from-foreground to-foreground/70">
          Compare Politicians
        </h1>
        <p className="text-lg text-muted-foreground">
          Compare trading performance, strategies, and returns side-by-side
        </p>
      </div>

      {/* Selection */}
      <div className="glass-strong rounded-xl p-6 border border-border/50">
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div>
            <label className="block text-sm font-semibold mb-2">Select First Politician</label>
            <select
              value={selected1}
              onChange={(e) => setSelected1(e.target.value)}
              className="input-field"
            >
              <option value="">Choose a politician...</option>
              {politicians.filter(p => p !== selected2).map(pol => (
                <option key={pol} value={pol}>{pol}</option>
              ))}
            </select>
          </div>
          <div>
            <label className="block text-sm font-semibold mb-2">Select Second Politician</label>
            <select
              value={selected2}
              onChange={(e) => setSelected2(e.target.value)}
              className="input-field"
            >
              <option value="">Choose a politician...</option>
              {politicians.filter(p => p !== selected1).map(pol => (
                <option key={pol} value={pol}>{pol}</option>
              ))}
            </select>
          </div>
        </div>
      </div>

      {/* Comparison Results */}
      {showComparison ? (
        <div className="space-y-6 animate-fade-in">
          {/* Key Metrics Comparison */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <PoliticianCard data={mockData1} />
            <PoliticianCard data={mockData2} />
          </div>

          {/* Head-to-Head Stats */}
          <div className="glass-strong rounded-xl p-6 border border-border/50">
            <h3 className="text-xl font-bold mb-6">Head-to-Head Statistics</h3>
            <div className="space-y-4">
              <ComparisonBar
                label="Total Trades"
                value1={mockData1.totalTrades}
                value2={mockData2.totalTrades}
                name1={mockData1.name}
                name2={mockData2.name}
              />
              <ComparisonBar
                label="Average Return"
                value1={parseFloat(mockData1.avgReturn)}
                value2={parseFloat(mockData2.avgReturn)}
                name1={mockData1.name}
                name2={mockData2.name}
                suffix="%"
              />
              <ComparisonBar
                label="Win Rate"
                value1={parseFloat(mockData1.winRate)}
                value2={parseFloat(mockData2.winRate)}
                name1={mockData1.name}
                name2={mockData2.name}
                suffix="%"
              />
            </div>
          </div>

          {/* Sector Comparison */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div className="glass-strong rounded-xl p-6 border border-border/50">
              <h3 className="text-lg font-bold mb-4">{mockData1.name} - Top Sectors</h3>
              <div className="space-y-3">
                {mockData1.topSectors.map((sector, i) => (
                  <div key={i} className="flex items-center gap-3">
                    <div className="w-8 h-8 rounded-lg bg-primary/10 text-primary font-bold text-sm flex items-center justify-center">
                      {i + 1}
                    </div>
                    <div className="flex-1">
                      <p className="font-semibold">{sector}</p>
                      <div className="w-full h-2 bg-muted rounded-full mt-1">
                        <div
                          className="h-full bg-primary rounded-full"
                          style={{ width: `${100 - i * 20}%` }}
                        />
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </div>

            <div className="glass-strong rounded-xl p-6 border border-border/50">
              <h3 className="text-lg font-bold mb-4">{mockData2.name} - Top Sectors</h3>
              <div className="space-y-3">
                {mockData2.topSectors.map((sector, i) => (
                  <div key={i} className="flex items-center gap-3">
                    <div className="w-8 h-8 rounded-lg bg-purple-500/10 text-purple-500 font-bold text-sm flex items-center justify-center">
                      {i + 1}
                    </div>
                    <div className="flex-1">
                      <p className="font-semibold">{sector}</p>
                      <div className="w-full h-2 bg-muted rounded-full mt-1">
                        <div
                          className="h-full bg-purple-500 rounded-full"
                          style={{ width: `${100 - i * 20}%` }}
                        />
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </div>
        </div>
      ) : (
        <div className="glass rounded-xl p-16 text-center">
          <div className="inline-flex items-center justify-center w-20 h-20 rounded-full bg-primary/10 mb-6">
            <svg className="w-10 h-10 text-primary" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
            </svg>
          </div>
          <p className="text-xl font-semibold mb-2">Select Two Politicians to Compare</p>
          <p className="text-muted-foreground">Choose politicians from the dropdowns above</p>
        </div>
      )}
    </div>
  )
}

function PoliticianCard({ data }: { data: any }) {
  return (
    <div className="glass-strong rounded-xl p-6 border border-border/50">
      <div className="mb-6">
        <h3 className="text-2xl font-bold mb-1">{data.name}</h3>
        <div className="flex items-center gap-2 text-sm text-muted-foreground">
          <span className={`px-2 py-0.5 rounded-full text-xs font-bold ${
            data.party === 'Democratic'
              ? 'bg-blue-500/10 text-blue-500'
              : 'bg-red-500/10 text-red-500'
          }`}>
            {data.party}
          </span>
          <span>{data.state}</span>
        </div>
      </div>

      <div className="grid grid-cols-2 gap-4 mb-6">
        <MetricBox label="Total Trades" value={data.totalTrades} />
        <MetricBox label="Total Value" value={data.totalValue} />
        <MetricBox label="Avg Return" value={data.avgReturn} highlight="green" />
        <MetricBox label="Win Rate" value={data.winRate} highlight="blue" />
      </div>

      <div>
        <p className="text-sm font-semibold text-muted-foreground mb-3">RECENT TRADES</p>
        <div className="space-y-2">
          {data.recentTrades.slice(0, 3).map((trade: any, i: number) => (
            <div key={i} className="flex items-center justify-between p-2 rounded bg-muted/30 text-xs">
              <div className="flex items-center gap-2">
                <span className="font-bold">{trade.symbol}</span>
                <span className={`px-1.5 py-0.5 rounded text-[10px] font-bold ${
                  trade.type === 'BUY'
                    ? 'bg-green-500/10 text-green-500'
                    : 'bg-red-500/10 text-red-500'
                }`}>
                  {trade.type}
                </span>
              </div>
              <span className="text-green-500 font-bold">{trade.return}</span>
            </div>
          ))}
        </div>
      </div>
    </div>
  )
}

function MetricBox({ label, value, highlight }: { label: string; value: any; highlight?: string }) {
  return (
    <div className="bg-muted/30 rounded-lg p-3">
      <p className="text-xs text-muted-foreground mb-1">{label}</p>
      <p className={`font-bold text-lg ${
        highlight === 'green' ? 'text-green-500' :
        highlight === 'blue' ? 'text-blue-500' :
        ''
      }`}>
        {value}
      </p>
    </div>
  )
}

function ComparisonBar({
  label,
  value1,
  value2,
  name1,
  name2,
  suffix = '',
}: {
  label: string
  value1: number
  value2: number
  name1: string
  name2: string
  suffix?: string
}) {
  const total = value1 + value2
  const percent1 = (value1 / total) * 100
  const percent2 = (value2 / total) * 100

  return (
    <div>
      <div className="flex items-center justify-between mb-2">
        <p className="font-semibold">{label}</p>
        <div className="flex items-center gap-4 text-sm">
          <span className="text-primary font-bold">{value1}{suffix}</span>
          <span className="text-muted-foreground">vs</span>
          <span className="text-purple-500 font-bold">{value2}{suffix}</span>
        </div>
      </div>
      <div className="flex h-4 rounded-full overflow-hidden">
        <div
          className="bg-primary flex items-center justify-center text-[10px] font-bold text-white"
          style={{ width: `${percent1}%` }}
        >
          {percent1 > 20 && `${percent1.toFixed(0)}%`}
        </div>
        <div
          className="bg-purple-500 flex items-center justify-center text-[10px] font-bold text-white"
          style={{ width: `${percent2}%` }}
        >
          {percent2 > 20 && `${percent2.toFixed(0)}%`}
        </div>
      </div>
    </div>
  )
}
