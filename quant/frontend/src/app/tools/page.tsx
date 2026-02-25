/**
 * Free Tools Page
 * Value-add tools for users: stock screener, calculators, pattern finder
 */

'use client'

import { useState } from 'react'
import { AnimatedCard } from '@/components/ui/AnimatedCard'

export default function ToolsPage() {
  const [selectedTool, setSelectedTool] = useState<string | null>(null)

  const tools = [
    {
      id: 'screener',
      name: 'Stock Screener',
      description: 'Filter stocks by technical indicators, fundamentals, and custom criteria',
      icon: '🔍',
      gradient: 'from-blue-500 to-cyan-500',
      premium: false,
    },
    {
      id: 'calculator',
      name: 'Position Size Calculator',
      description: 'Calculate optimal position sizes based on risk tolerance and account size',
      icon: '🧮',
      gradient: 'from-green-500 to-emerald-500',
      premium: false,
    },
    {
      id: 'risk',
      name: 'Risk/Reward Calculator',
      description: 'Analyze risk-reward ratios for your trades before entering positions',
      icon: '⚖️',
      gradient: 'from-purple-500 to-pink-500',
      premium: false,
    },
    {
      id: 'patterns',
      name: 'Pattern Scanner',
      description: 'Scan for chart patterns: head & shoulders, double tops, triangles, and more',
      icon: '📈',
      gradient: 'from-orange-500 to-red-500',
      premium: true,
    },
    {
      id: 'correlation',
      name: 'Correlation Matrix',
      description: 'Find correlations between stocks, sectors, and asset classes',
      icon: '🔗',
      gradient: 'from-indigo-500 to-blue-500',
      premium: true,
    },
    {
      id: 'volatility',
      name: 'Volatility Analyzer',
      description: 'Measure historical and implied volatility with percentile rankings',
      icon: '📊',
      gradient: 'from-pink-500 to-rose-500',
      premium: true,
    },
  ]

  return (
    <div className="space-y-8">
      {/* Header */}
      <div className="animate-fade-in">
        <div className="inline-flex items-center gap-2 px-4 py-2 rounded-full bg-primary/10 border border-primary/20 mb-4">
          <span className="text-sm font-medium text-primary">Free Trading Tools</span>
        </div>
        <h1 className="text-4xl md:text-5xl font-bold mb-3 bg-clip-text text-transparent bg-gradient-to-r from-foreground to-foreground/70">
          Quant Tools & Calculators
        </h1>
        <p className="text-lg text-muted-foreground max-w-3xl">
          Professional-grade tools for stock analysis, risk management, and trading strategy development.
          All tools are free to use with real-time data.
        </p>
      </div>

      {/* Tools Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {tools.map((tool, idx) => (
          <div
            key={tool.id}
            className="relative group cursor-pointer"
            onClick={() => setSelectedTool(tool.id)}
          >
            <div
              className="glass-strong rounded-xl p-6 border border-border/50 hover:shadow-2xl hover:border-primary/30 transition-all duration-300 h-full animate-fade-in"
              style={{ animationDelay: `${idx * 100}ms`, animationFillMode: 'backwards' }}
            >
              {/* Premium Badge */}
              {tool.premium && (
                <div className="absolute top-4 right-4">
                  <span className="inline-flex items-center gap-1 px-2 py-1 rounded-full bg-gradient-to-r from-yellow-500 to-orange-500 text-white text-xs font-bold">
                    <svg className="w-3 h-3" fill="currentColor" viewBox="0 0 20 20">
                      <path d="M9.049 2.927c.3-.921 1.603-.921 1.902 0l1.07 3.292a1 1 0 00.95.69h3.462c.969 0 1.371 1.24.588 1.81l-2.8 2.034a1 1 0 00-.364 1.118l1.07 3.292c.3.921-.755 1.688-1.54 1.118l-2.8-2.034a1 1 0 00-1.175 0l-2.8 2.034c-.784.57-1.838-.197-1.539-1.118l1.07-3.292a1 1 0 00-.364-1.118L2.98 8.72c-.783-.57-.38-1.81.588-1.81h3.461a1 1 0 00.951-.69l1.07-3.292z" />
                    </svg>
                    PRO
                  </span>
                </div>
              )}

              {/* Icon */}
              <div className={`inline-flex items-center justify-center w-16 h-16 rounded-2xl bg-gradient-to-br ${tool.gradient} text-white text-3xl mb-4 shadow-lg group-hover:scale-110 transition-transform duration-300`}>
                {tool.icon}
              </div>

              {/* Content */}
              <h3 className="text-xl font-bold mb-2 group-hover:text-primary transition-colors">
                {tool.name}
              </h3>
              <p className="text-sm text-muted-foreground mb-4">
                {tool.description}
              </p>

              {/* CTA */}
              <div className="flex items-center gap-2 text-primary text-sm font-semibold opacity-0 group-hover:opacity-100 transition-opacity">
                {tool.premium ? 'Try Premium Tool' : 'Use Free Tool'}
                <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 7l5 5m0 0l-5 5m5-5H6" />
                </svg>
              </div>
            </div>
          </div>
        ))}
      </div>

      {/* Stock Screener Tool */}
      {selectedTool === 'screener' && <StockScreener onClose={() => setSelectedTool(null)} />}
      {selectedTool === 'calculator' && <PositionCalculator onClose={() => setSelectedTool(null)} />}
      {selectedTool === 'risk' && <RiskRewardCalculator onClose={() => setSelectedTool(null)} />}

      {/* Feature Highlights */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mt-12">
        <FeatureHighlight
          title="Real-time Data"
          description="Access live market data and real-time calculations"
          icon="⚡"
        />
        <FeatureHighlight
          title="No Registration Required"
          description="Use all free tools instantly without signing up"
          icon="🔓"
        />
        <FeatureHighlight
          title="Professional Grade"
          description="Same tools used by professional traders and institutions"
          icon="🏆"
        />
      </div>
    </div>
  )
}

function StockScreener({ onClose }: { onClose: () => void }) {
  const [filters, setFilters] = useState({
    minPrice: '',
    maxPrice: '',
    minVolume: '',
    rsi: 'all',
    sector: 'all',
  })

  return (
    <div className="fixed inset-0 bg-black/60 backdrop-blur-sm z-50 flex items-center justify-center p-4 animate-fade-in">
      <div className="glass-strong rounded-2xl border border-border/50 max-w-4xl w-full max-h-[90vh] overflow-y-auto">
        <div className="sticky top-0 glass-strong border-b border-border/50 p-6 flex items-center justify-between">
          <h2 className="text-2xl font-bold">Stock Screener</h2>
          <button onClick={onClose} className="btn-ghost !px-3 !py-2">
            <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </div>

        <div className="p-6 space-y-6">
          {/* Filters */}
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            <div>
              <label className="block text-sm font-semibold mb-2">Min Price</label>
              <input
                type="number"
                value={filters.minPrice}
                onChange={(e) => setFilters({ ...filters, minPrice: e.target.value })}
                placeholder="$0"
                className="input-field"
              />
            </div>
            <div>
              <label className="block text-sm font-semibold mb-2">Max Price</label>
              <input
                type="number"
                value={filters.maxPrice}
                onChange={(e) => setFilters({ ...filters, maxPrice: e.target.value })}
                placeholder="$1000"
                className="input-field"
              />
            </div>
            <div>
              <label className="block text-sm font-semibold mb-2">Min Volume</label>
              <input
                type="number"
                value={filters.minVolume}
                onChange={(e) => setFilters({ ...filters, minVolume: e.target.value })}
                placeholder="1,000,000"
                className="input-field"
              />
            </div>
            <div>
              <label className="block text-sm font-semibold mb-2">RSI Condition</label>
              <select
                value={filters.rsi}
                onChange={(e) => setFilters({ ...filters, rsi: e.target.value })}
                className="input-field"
              >
                <option value="all">All</option>
                <option value="oversold">Oversold (&lt; 30)</option>
                <option value="neutral">Neutral (30-70)</option>
                <option value="overbought">Overbought (&gt; 70)</option>
              </select>
            </div>
            <div>
              <label className="block text-sm font-semibold mb-2">Sector</label>
              <select
                value={filters.sector}
                onChange={(e) => setFilters({ ...filters, sector: e.target.value })}
                className="input-field"
              >
                <option value="all">All Sectors</option>
                <option value="tech">Technology</option>
                <option value="finance">Finance</option>
                <option value="healthcare">Healthcare</option>
                <option value="energy">Energy</option>
              </select>
            </div>
          </div>

          <button className="btn-primary w-full">
            <span className="flex items-center justify-center gap-2">
              <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
              </svg>
              Screen Stocks
            </span>
          </button>

          {/* Demo Results */}
          <div className="glass rounded-xl p-4 border border-border/50">
            <p className="text-sm text-muted-foreground text-center py-8">
              Configure filters above and click &quot;Screen Stocks&quot; to find matching opportunities
            </p>
          </div>
        </div>
      </div>
    </div>
  )
}

function PositionCalculator({ onClose }: { onClose: () => void }) {
  const [inputs, setInputs] = useState({
    accountSize: '10000',
    riskPercent: '2',
    entryPrice: '100',
    stopLoss: '95',
  })

  const calculatePosition = () => {
    const account = parseFloat(inputs.accountSize)
    const risk = parseFloat(inputs.riskPercent) / 100
    const entry = parseFloat(inputs.entryPrice)
    const stop = parseFloat(inputs.stopLoss)

    const riskAmount = account * risk
    const riskPerShare = Math.abs(entry - stop)
    const shares = Math.floor(riskAmount / riskPerShare)
    const positionSize = shares * entry

    return { shares, positionSize, riskAmount }
  }

  const result = calculatePosition()

  return (
    <div className="fixed inset-0 bg-black/60 backdrop-blur-sm z-50 flex items-center justify-center p-4 animate-fade-in">
      <div className="glass-strong rounded-2xl border border-border/50 max-w-2xl w-full">
        <div className="glass-strong border-b border-border/50 p-6 flex items-center justify-between">
          <h2 className="text-2xl font-bold">Position Size Calculator</h2>
          <button onClick={onClose} className="btn-ghost !px-3 !py-2">
            <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </div>

        <div className="p-6 space-y-6">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-semibold mb-2">Account Size ($)</label>
              <input
                type="number"
                value={inputs.accountSize}
                onChange={(e) => setInputs({ ...inputs, accountSize: e.target.value })}
                className="input-field"
              />
            </div>
            <div>
              <label className="block text-sm font-semibold mb-2">Risk Per Trade (%)</label>
              <input
                type="number"
                value={inputs.riskPercent}
                onChange={(e) => setInputs({ ...inputs, riskPercent: e.target.value })}
                className="input-field"
                step="0.1"
              />
            </div>
            <div>
              <label className="block text-sm font-semibold mb-2">Entry Price ($)</label>
              <input
                type="number"
                value={inputs.entryPrice}
                onChange={(e) => setInputs({ ...inputs, entryPrice: e.target.value })}
                className="input-field"
                step="0.01"
              />
            </div>
            <div>
              <label className="block text-sm font-semibold mb-2">Stop Loss ($)</label>
              <input
                type="number"
                value={inputs.stopLoss}
                onChange={(e) => setInputs({ ...inputs, stopLoss: e.target.value })}
                className="input-field"
                step="0.01"
              />
            </div>
          </div>

          {/* Results */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div className="glass rounded-xl p-4 border border-border/50">
              <p className="text-sm text-muted-foreground mb-1">Shares to Buy</p>
              <p className="text-3xl font-bold text-primary">{result.shares.toLocaleString()}</p>
            </div>
            <div className="glass rounded-xl p-4 border border-border/50">
              <p className="text-sm text-muted-foreground mb-1">Position Size</p>
              <p className="text-3xl font-bold text-green-500">${result.positionSize.toLocaleString()}</p>
            </div>
            <div className="glass rounded-xl p-4 border border-border/50">
              <p className="text-sm text-muted-foreground mb-1">Risk Amount</p>
              <p className="text-3xl font-bold text-red-500">${result.riskAmount.toFixed(2)}</p>
            </div>
          </div>

          <div className="bg-primary/5 border border-primary/10 rounded-xl p-4">
            <p className="text-sm">
              <span className="font-bold text-primary">Recommendation:</span> Buy {result.shares} shares at ${inputs.entryPrice}
              with a stop loss at ${inputs.stopLoss}. This risks ${result.riskAmount.toFixed(2)} ({inputs.riskPercent}% of your account).
            </p>
          </div>
        </div>
      </div>
    </div>
  )
}

function RiskRewardCalculator({ onClose }: { onClose: () => void }) {
  const [inputs, setInputs] = useState({
    entry: '100',
    target: '110',
    stop: '95',
  })

  const calculate = () => {
    const entry = parseFloat(inputs.entry)
    const target = parseFloat(inputs.target)
    const stop = parseFloat(inputs.stop)

    const reward = target - entry
    const risk = entry - stop
    const ratio = reward / risk

    return { reward, risk, ratio }
  }

  const result = calculate()

  return (
    <div className="fixed inset-0 bg-black/60 backdrop-blur-sm z-50 flex items-center justify-center p-4 animate-fade-in">
      <div className="glass-strong rounded-2xl border border-border/50 max-w-2xl w-full">
        <div className="glass-strong border-b border-border/50 p-6 flex items-center justify-between">
          <h2 className="text-2xl font-bold">Risk/Reward Calculator</h2>
          <button onClick={onClose} className="btn-ghost !px-3 !py-2">
            <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </div>

        <div className="p-6 space-y-6">
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div>
              <label className="block text-sm font-semibold mb-2">Entry Price ($)</label>
              <input
                type="number"
                value={inputs.entry}
                onChange={(e) => setInputs({ ...inputs, entry: e.target.value })}
                className="input-field"
                step="0.01"
              />
            </div>
            <div>
              <label className="block text-sm font-semibold mb-2">Target Price ($)</label>
              <input
                type="number"
                value={inputs.target}
                onChange={(e) => setInputs({ ...inputs, target: e.target.value })}
                className="input-field"
                step="0.01"
              />
            </div>
            <div>
              <label className="block text-sm font-semibold mb-2">Stop Loss ($)</label>
              <input
                type="number"
                value={inputs.stop}
                onChange={(e) => setInputs({ ...inputs, stop: e.target.value })}
                className="input-field"
                step="0.01"
              />
            </div>
          </div>

          {/* Visual Risk/Reward */}
          <div className="relative h-48 glass rounded-xl border border-border/50 p-6">
            <div className="absolute inset-6 flex items-center">
              <div className="w-full h-2 bg-muted rounded-full relative">
                {/* Stop Loss */}
                <div className="absolute -left-2 top-1/2 -translate-y-1/2 w-4 h-4 rounded-full bg-red-500 border-2 border-background" />
                <div className="absolute left-0 -top-8 text-sm font-semibold text-red-500">
                  Stop: ${inputs.stop}
                </div>

                {/* Entry */}
                <div className="absolute left-1/2 -translate-x-1/2 top-1/2 -translate-y-1/2 w-4 h-4 rounded-full bg-primary border-2 border-background" />
                <div className="absolute left-1/2 -translate-x-1/2 -top-8 text-sm font-semibold text-primary">
                  Entry: ${inputs.entry}
                </div>

                {/* Target */}
                <div className="absolute -right-2 top-1/2 -translate-y-1/2 w-4 h-4 rounded-full bg-green-500 border-2 border-background" />
                <div className="absolute right-0 -top-8 text-sm font-semibold text-green-500">
                  Target: ${inputs.target}
                </div>
              </div>
            </div>

            <div className="absolute bottom-6 left-6 right-6 flex justify-between text-xs text-muted-foreground">
              <span>Risk: ${result.risk.toFixed(2)}</span>
              <span>Reward: ${result.reward.toFixed(2)}</span>
            </div>
          </div>

          {/* Result */}
          <div className={`glass rounded-xl p-6 border-2 ${
            result.ratio >= 2 ? 'border-green-500/50 bg-green-500/5' :
            result.ratio >= 1 ? 'border-yellow-500/50 bg-yellow-500/5' :
            'border-red-500/50 bg-red-500/5'
          }`}>
            <div className="text-center">
              <p className="text-sm text-muted-foreground mb-2">Risk/Reward Ratio</p>
              <p className="text-6xl font-bold mb-4">
                <span className={
                  result.ratio >= 2 ? 'text-green-500' :
                  result.ratio >= 1 ? 'text-yellow-500' :
                  'text-red-500'
                }>
                  {result.ratio.toFixed(2)}
                </span>
                <span className="text-2xl text-muted-foreground">:1</span>
              </p>
              <p className="text-sm">
                {result.ratio >= 2 ? '✅ Excellent trade setup' :
                 result.ratio >= 1 ? '⚠️ Acceptable but not ideal' :
                 '❌ Poor risk/reward - avoid this trade'}
              </p>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}

function FeatureHighlight({ title, description, icon }: { title: string; description: string; icon: string }) {
  return (
    <div className="text-center">
      <div className="inline-flex items-center justify-center w-16 h-16 rounded-full bg-primary/10 text-4xl mb-4">
        {icon}
      </div>
      <h3 className="font-bold mb-2">{title}</h3>
      <p className="text-sm text-muted-foreground">{description}</p>
    </div>
  )
}
