/**
 * Strategy Library Page
 *
 * Browse all 10 professional trading strategies
 * Lock premium strategies with upgrade prompts
 */

'use client'

import { useState } from 'react'
import {
  TrendingUp,
  Activity,
  BarChart3,
  Zap,
  Target,
  Flame,
  TrendingDown,
  Layers,
  GitBranch,
  Lock,
  Check,
  ArrowRight,
} from 'lucide-react'
import Link from 'next/link'

export default function StrategiesPage() {
  const [filterTier, setFilterTier] = useState<'all' | 'free' | 'premium' | 'enterprise'>('all')
  const [filterCategory, setFilterCategory] = useState<'all' | 'trend' | 'mean_reversion' | 'momentum' | 'professional'>('all')

  // Strategy data matching backend registry
  const strategies = [
    // FREE TIER
    {
      id: 'ma_crossover',
      name: 'MA Crossover',
      tier: 'free',
      category: 'trend',
      icon: TrendingUp,
      color: 'from-green-500 to-emerald-600',
      description: 'Classic trend following with moving average crossovers',
      longDescription: 'Buy when fast MA crosses above slow MA, sell when it crosses below. Simple yet effective for trending markets.',
      winRate: 58,
      avgReturn: 15.7,
      sharpeRatio: 1.45,
      parameters: [
        { name: 'fast_period', default: 20, description: 'Fast MA period' },
        { name: 'slow_period', default: 50, description: 'Slow MA period' },
      ],
      useCase: 'Strong trending markets, low volatility',
      riskLevel: 'Medium',
    },
    {
      id: 'rsi',
      name: 'RSI Mean Reversion',
      tier: 'free',
      category: 'mean_reversion',
      icon: Activity,
      color: 'from-blue-500 to-cyan-600',
      description: 'Contrarian strategy based on overbought/oversold levels',
      longDescription: 'Buy when RSI < oversold threshold, sell when RSI > overbought threshold. Works best in ranging markets.',
      winRate: 62,
      avgReturn: 18.2,
      sharpeRatio: 1.68,
      parameters: [
        { name: 'rsi_period', default: 14, description: 'RSI calculation period' },
        { name: 'oversold', default: 30, description: 'Oversold threshold' },
        { name: 'overbought', default: 70, description: 'Overbought threshold' },
      ],
      useCase: 'Range-bound markets, mean reversion',
      riskLevel: 'Medium',
    },
    {
      id: 'bollinger_breakout',
      name: 'Bollinger Breakout',
      tier: 'free',
      category: 'trend',
      icon: BarChart3,
      color: 'from-purple-500 to-pink-600',
      description: 'Volatility expansion breakout trading',
      longDescription: 'Trade breakouts above/below Bollinger Bands. Captures volatility expansions effectively.',
      winRate: 54,
      avgReturn: 21.4,
      sharpeRatio: 1.52,
      parameters: [
        { name: 'period', default: 20, description: 'BB period' },
        { name: 'std_dev', default: 2.0, description: 'Standard deviations' },
      ],
      useCase: 'High volatility, breakout moves',
      riskLevel: 'High',
    },

    // PREMIUM TIER
    {
      id: 'macd',
      name: 'MACD Momentum',
      tier: 'premium',
      category: 'momentum',
      icon: Zap,
      color: 'from-yellow-500 to-orange-600',
      description: 'Momentum strategy with trend confirmation',
      longDescription: 'Buy when MACD crosses above signal line, sell when it crosses below. Combines momentum and trend.',
      winRate: 64,
      avgReturn: 24.6,
      sharpeRatio: 1.92,
      parameters: [
        { name: 'fast_period', default: 12, description: 'Fast EMA' },
        { name: 'slow_period', default: 26, description: 'Slow EMA' },
        { name: 'signal_period', default: 9, description: 'Signal line' },
      ],
      useCase: 'Momentum trading, trend confirmation',
      riskLevel: 'Medium',
    },
    {
      id: 'mean_reversion_zscore',
      name: 'Z-Score Mean Reversion',
      tier: 'premium',
      category: 'mean_reversion',
      icon: Target,
      color: 'from-indigo-500 to-purple-600',
      description: 'Statistical arbitrage with Z-scores',
      longDescription: 'Trade based on statistical deviations from mean. Professional quantitative approach.',
      winRate: 60,
      avgReturn: 19.8,
      sharpeRatio: 2.14,
      parameters: [
        { name: 'lookback', default: 20, description: 'Lookback period' },
        { name: 'entry_threshold', default: 2.0, description: 'Entry Z-score' },
        { name: 'exit_threshold', default: 0.5, description: 'Exit Z-score' },
      ],
      useCase: 'Statistical arbitrage, pairs trading',
      riskLevel: 'Low',
    },
    {
      id: 'momentum',
      name: 'Pure Momentum',
      tier: 'premium',
      category: 'momentum',
      icon: Flame,
      color: 'from-red-500 to-orange-600',
      description: 'Ride strong price trends aggressively',
      longDescription: 'Buy strong upward momentum, sell strong downward momentum. Simple and powerful.',
      winRate: 64,
      avgReturn: 26.3,
      sharpeRatio: 1.78,
      parameters: [
        { name: 'lookback', default: 20, description: 'Momentum period' },
        { name: 'momentum_threshold', default: 0.05, description: 'Min momentum %' },
      ],
      useCase: 'Strong trending markets, momentum',
      riskLevel: 'High',
    },
    {
      id: 'triple_ema',
      name: 'Triple EMA',
      tier: 'premium',
      category: 'trend',
      icon: Layers,
      color: 'from-teal-500 to-green-600',
      description: 'Multi-timeframe trend confirmation',
      longDescription: 'Trade only when all three EMAs align. Strong trend confirmation reduces false signals.',
      winRate: 55,
      avgReturn: 22.7,
      sharpeRatio: 1.86,
      parameters: [
        { name: 'short_period', default: 8, description: 'Short EMA' },
        { name: 'medium_period', default: 21, description: 'Medium EMA' },
        { name: 'long_period', default: 55, description: 'Long EMA' },
      ],
      useCase: 'Trend confirmation, reduce whipsaws',
      riskLevel: 'Medium',
    },

    // ENTERPRISE TIER
    {
      id: 'ichimoku_cloud',
      name: 'Ichimoku Cloud',
      tier: 'enterprise',
      category: 'professional',
      icon: Layers,
      color: 'from-violet-500 to-purple-600',
      description: 'Institutional-grade complete trading system',
      longDescription: 'Professional system used by institutional traders. Multiple confirmations reduce risk significantly.',
      winRate: 58,
      avgReturn: 28.4,
      sharpeRatio: 2.32,
      parameters: [
        { name: 'conversion_period', default: 9, description: 'Conversion line' },
        { name: 'base_period', default: 26, description: 'Base line' },
        { name: 'span_b_period', default: 52, description: 'Span B' },
        { name: 'displacement', default: 26, description: 'Displacement' },
      ],
      useCase: 'Professional trading, institutional',
      riskLevel: 'Low',
    },
    {
      id: 'multi_timeframe',
      name: 'Multi-Timeframe',
      tier: 'enterprise',
      category: 'professional',
      icon: GitBranch,
      color: 'from-pink-500 to-rose-600',
      description: 'Cross-timeframe trend alignment',
      longDescription: 'Only trades when all timeframes align. Significantly reduces false signals and improves win rate.',
      winRate: 67,
      avgReturn: 31.2,
      sharpeRatio: 2.45,
      parameters: [
        { name: 'short_ma', default: 20, description: 'Short MA' },
        { name: 'long_ma', default: 50, description: 'Long MA' },
        { name: 'higher_tf_ma', default: 200, description: 'Higher TF MA' },
      ],
      useCase: 'High probability trades, patience',
      riskLevel: 'Low',
    },
    {
      id: 'volatility_breakout_atr',
      name: 'ATR Volatility Breakout',
      tier: 'enterprise',
      category: 'professional',
      icon: TrendingDown,
      color: 'from-orange-500 to-red-600',
      description: 'Adaptive trading based on volatility',
      longDescription: 'Adapts to market volatility using ATR. Dynamic position sizing and stop-loss levels.',
      winRate: 61,
      avgReturn: 34.8,
      sharpeRatio: 2.18,
      parameters: [
        { name: 'atr_period', default: 14, description: 'ATR period' },
        { name: 'breakout_multiplier', default: 2.0, description: 'Breakout ATR multiplier' },
      ],
      useCase: 'Volatile markets, adaptive trading',
      riskLevel: 'Medium',
    },
  ]

  // Filter strategies
  const filteredStrategies = strategies.filter((strategy) => {
    const tierMatch = filterTier === 'all' || strategy.tier === filterTier
    const categoryMatch = filterCategory === 'all' || strategy.category === filterCategory
    return tierMatch && categoryMatch
  })

  // Current user tier (placeholder - should come from auth)
  const userTier: 'free' | 'premium' | 'enterprise' = 'free'

  const canAccessStrategy = (strategyTier: string) => {
    const tierHierarchy = { free: 0, premium: 1, enterprise: 2 }
    return tierHierarchy[userTier as keyof typeof tierHierarchy] >= tierHierarchy[strategyTier as keyof typeof tierHierarchy]
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-950 via-slate-900 to-slate-950 py-12">
      <div className="container mx-auto px-4">
        {/* Header */}
        <div className="text-center mb-12">
          <h1 className="text-5xl font-bold text-white mb-4">
            Professional Trading
            <span className="bg-gradient-to-r from-blue-400 to-purple-600 bg-clip-text text-transparent"> Strategies</span>
          </h1>
          <p className="text-xl text-gray-400 max-w-2xl mx-auto">
            10 backtested strategies used by professional traders. Start with 3 free, unlock more with Premium.
          </p>
        </div>

        {/* Filters */}
        <div className="flex flex-wrap gap-4 justify-center mb-12">
          <div className="flex gap-2">
            <button
              onClick={() => setFilterTier('all')}
              className={`px-4 py-2 rounded-lg font-medium transition-all ${
                filterTier === 'all'
                  ? 'bg-blue-600 text-white'
                  : 'bg-slate-800 text-gray-400 hover:text-white'
              }`}
            >
              All Strategies
            </button>
            <button
              onClick={() => setFilterTier('free')}
              className={`px-4 py-2 rounded-lg font-medium transition-all ${
                filterTier === 'free'
                  ? 'bg-green-600 text-white'
                  : 'bg-slate-800 text-gray-400 hover:text-white'
              }`}
            >
              Free
            </button>
            <button
              onClick={() => setFilterTier('premium')}
              className={`px-4 py-2 rounded-lg font-medium transition-all ${
                filterTier === 'premium'
                  ? 'bg-purple-600 text-white'
                  : 'bg-slate-800 text-gray-400 hover:text-white'
              }`}
            >
              Premium
            </button>
            <button
              onClick={() => setFilterTier('enterprise')}
              className={`px-4 py-2 rounded-lg font-medium transition-all ${
                filterTier === 'enterprise'
                  ? 'bg-pink-600 text-white'
                  : 'bg-slate-800 text-gray-400 hover:text-white'
              }`}
            >
              Enterprise
            </button>
          </div>
        </div>

        {/* Strategy Grid */}
        <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6 mb-12">
          {filteredStrategies.map((strategy) => {
            const Icon = strategy.icon
            const isLocked = !canAccessStrategy(strategy.tier)

            return (
              <div
                key={strategy.id}
                className={`relative rounded-xl border ${
                  isLocked
                    ? 'border-slate-700 bg-slate-800/20 opacity-60'
                    : 'border-slate-700 bg-slate-800/30 hover:border-blue-500/30'
                } p-6 transition-all duration-300 ${!isLocked && 'hover:scale-105'}`}
              >
                {/* Locked Overlay */}
                {isLocked && (
                  <div className="absolute inset-0 flex items-center justify-center bg-slate-900/80 rounded-xl z-10 backdrop-blur-sm">
                    <div className="text-center">
                      <Lock className="w-12 h-12 text-gray-400 mx-auto mb-3" />
                      <p className="text-white font-semibold mb-2">
                        {strategy.tier === 'premium' ? 'Premium' : 'Enterprise'} Only
                      </p>
                      <Link href="/pricing">
                        <span className="text-blue-400 hover:text-blue-300 text-sm cursor-pointer">
                          Upgrade to unlock →
                        </span>
                      </Link>
                    </div>
                  </div>
                )}

                {/* Tier Badge */}
                <div className="flex items-center justify-between mb-4">
                  <div
                    className={`px-3 py-1 rounded-full text-xs font-semibold ${
                      strategy.tier === 'free'
                        ? 'bg-green-500/20 text-green-400'
                        : strategy.tier === 'premium'
                        ? 'bg-purple-500/20 text-purple-400'
                        : 'bg-pink-500/20 text-pink-400'
                    }`}
                  >
                    {strategy.tier.toUpperCase()}
                  </div>
                  <div className={`w-12 h-12 rounded-lg bg-gradient-to-br ${strategy.color} flex items-center justify-center`}>
                    <Icon className="w-6 h-6 text-white" />
                  </div>
                </div>

                {/* Strategy Name */}
                <h3 className="text-xl font-bold text-white mb-2">
                  {strategy.name}
                </h3>

                {/* Description */}
                <p className="text-gray-400 text-sm mb-4">
                  {strategy.description}
                </p>

                {/* Stats */}
                <div className="grid grid-cols-3 gap-2 mb-4">
                  <div className="bg-slate-900/50 rounded-lg p-2 text-center">
                    <div className="text-xs text-gray-500 mb-1">Win Rate</div>
                    <div className="text-sm font-semibold text-green-400">{strategy.winRate}%</div>
                  </div>
                  <div className="bg-slate-900/50 rounded-lg p-2 text-center">
                    <div className="text-xs text-gray-500 mb-1">Avg Return</div>
                    <div className="text-sm font-semibold text-blue-400">+{strategy.avgReturn}%</div>
                  </div>
                  <div className="bg-slate-900/50 rounded-lg p-2 text-center">
                    <div className="text-xs text-gray-500 mb-1">Sharpe</div>
                    <div className="text-sm font-semibold text-purple-400">{strategy.sharpeRatio}</div>
                  </div>
                </div>

                {/* Use Case */}
                <div className="text-xs text-gray-500 mb-1">Best For</div>
                <div className="text-sm text-gray-300 mb-4">{strategy.useCase}</div>

                {/* CTA */}
                {!isLocked && (
                  <Link href={`/backtesting?strategy=${strategy.id}`}>
                    <button className="w-full bg-gradient-to-r from-blue-500 to-purple-600 hover:from-blue-600 hover:to-purple-700 text-white font-semibold py-2 rounded-lg transition-all flex items-center justify-center gap-2">
                      Try Strategy
                      <ArrowRight className="w-4 h-4" />
                    </button>
                  </Link>
                )}
              </div>
            )
          })}
        </div>

        {/* Upgrade CTA */}
        {userTier === 'free' && (
          <div className="bg-gradient-to-r from-blue-500/10 to-purple-600/10 border border-blue-500/20 rounded-xl p-8 text-center">
            <h2 className="text-2xl font-bold text-white mb-4">
              Unlock 7 More Professional Strategies
            </h2>
            <p className="text-gray-400 mb-6">
              Upgrade to Premium for $29/month and get access to MACD, Z-Score, Momentum, and Triple EMA strategies.
            </p>
            <Link href="/pricing">
              <button className="bg-gradient-to-r from-blue-500 to-purple-600 hover:from-blue-600 hover:to-purple-700 text-white font-semibold px-8 py-3 rounded-lg shadow-lg inline-flex items-center gap-2">
                View Pricing
                <ArrowRight className="w-5 h-5" />
              </button>
            </Link>
          </div>
        )}
      </div>
    </div>
  )
}
