/**
 * Open Beta - Free Forever
 *
 * No paywalls. No tiers. No charges.
 * Everything is free during open beta.
 */

'use client'

import { Check, Zap, TrendingUp, ArrowRight } from 'lucide-react'

export default function PricingPage() {
  const features = [
    { name: 'Unlimited Backtests', included: true, description: 'Run as many backtests as you want' },
    { name: 'All 10+ Strategies', included: true, description: 'Access to every professional trading strategy' },
    { name: 'Full Historical Data', included: true, description: '10+ years of real market OHLC data' },
    { name: 'Advanced Analytics', included: true, description: 'Detailed performance metrics and drawdown analysis' },
    { name: 'Portfolio Tracking', included: true, description: 'Track multiple portfolios and positions' },
    { name: 'Email Alerts', included: true, description: 'Alerts for strategy signals (coming soon)' },
    { name: 'CSV Export', included: true, description: 'Export backtest results for further analysis' },
    { name: 'API Access', included: true, description: 'Programmatic backtesting (coming soon)' },
    { name: 'Congressional Trading', included: true, description: 'Free access to politician trading analytics' },
  ]

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-950 via-slate-900 to-slate-950">
      {/* Header */}
      <div className="container mx-auto px-4 py-20 text-center">
        <div className="inline-block mb-4 px-4 py-2 bg-green-500/10 rounded-full border border-green-500/20">
          <span className="text-green-400 text-sm font-medium">🎉 Open Beta - Completely Free</span>
        </div>

        <h1 className="text-5xl md:text-6xl font-bold text-white mb-6">
          Professional Backtesting
          <span className="block bg-gradient-to-r from-green-400 to-blue-600 bg-clip-text text-transparent">
            No Cost. No Limits.
          </span>
        </h1>

        <p className="text-xl text-gray-400 max-w-2xl mx-auto mb-8">
          Everything is free forever. No paywalls, no tiers, no hidden charges. We're building the most accessible
          quantitative trading platform on the internet.
        </p>

        <div className="flex gap-4 justify-center">
          <a
            href="/auth/register"
            className="bg-gradient-to-r from-blue-500 to-purple-600 hover:from-blue-600 hover:to-purple-700 text-white font-semibold px-8 py-4 rounded-xl shadow-lg shadow-blue-500/25 inline-flex items-center gap-2 transition-all"
          >
            Start Backtesting Now
            <ArrowRight className="w-5 h-5" />
          </a>
          <a
            href="/backtesting"
            className="border border-slate-600 hover:border-slate-500 text-white font-semibold px-8 py-4 rounded-xl transition-all"
          >
            Try Demo
          </a>
        </div>
      </div>

      {/* Features Grid */}
      <div className="container mx-auto px-4 py-16">
        <h2 className="text-3xl font-bold text-white mb-12 text-center">Everything Included</h2>

        <div className="grid md:grid-cols-2 gap-8 max-w-4xl mx-auto">
          {features.map((feature, idx) => (
            <div key={idx} className="flex items-start gap-4 bg-slate-800/30 rounded-xl p-6 border border-slate-700">
              <div className="flex-shrink-0 w-6 h-6 rounded-full bg-green-500/20 flex items-center justify-center mt-1">
                <Check className="w-4 h-4 text-green-400" />
              </div>
              <div className="flex-1">
                <h3 className="text-white font-semibold mb-1">{feature.name}</h3>
                <p className="text-gray-400 text-sm">{feature.description}</p>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Why Free? */}
      <div className="container mx-auto px-4 py-16 border-t border-slate-800">
        <div className="max-w-3xl mx-auto">
          <h2 className="text-3xl font-bold text-white mb-8 text-center">Why Is Everything Free?</h2>

          <div className="space-y-6">
            <div className="bg-slate-800/30 rounded-xl p-6 border border-slate-700">
              <h3 className="text-lg font-semibold text-white mb-3 flex items-center gap-2">
                <Zap className="w-5 h-5 text-yellow-400" />
                Community First
              </h3>
              <p className="text-gray-400">
                We believe retail traders deserve access to professional-grade tools. We're building in public with the
                community, not against it.
              </p>
            </div>

            <div className="bg-slate-800/30 rounded-xl p-6 border border-slate-700">
              <h3 className="text-lg font-semibold text-white mb-3 flex items-center gap-2">
                <TrendingUp className="w-5 h-5 text-green-400" />
                Sustainable Revenue
              </h3>
              <p className="text-gray-400">
                We earn from optional broker affiliate partnerships. We recommend tools we believe in. Your success
                benefits us too.
              </p>
            </div>

            <div className="bg-slate-800/30 rounded-xl p-6 border border-slate-700">
              <h3 className="text-lg font-semibold text-white mb-3 flex items-center gap-2">
                <Check className="w-5 h-5 text-blue-400" />
                Open Development
              </h3>
              <p className="text-gray-400">
                You can see what we're building, contribute ideas, and help shape the future of the platform. This is
                a public project.
              </p>
            </div>
          </div>
        </div>
      </div>

      {/* Social Proof */}
      <div className="container mx-auto px-4 py-16 border-t border-slate-800">
        <div className="max-w-3xl mx-auto text-center">
          <h2 className="text-3xl font-bold text-white mb-12">What Traders Are Using</h2>

          <div className="grid md:grid-cols-3 gap-6">
            <div className="bg-slate-800/30 rounded-xl p-6 border border-slate-700">
              <div className="text-4xl font-bold text-white mb-2">10+</div>
              <div className="text-gray-400">Professional Strategies</div>
            </div>
            <div className="bg-slate-800/30 rounded-xl p-6 border border-slate-700">
              <div className="text-4xl font-bold text-white mb-2">10K+</div>
              <div className="text-gray-400">Market Data Points</div>
            </div>
            <div className="bg-slate-800/30 rounded-xl p-6 border border-slate-700">
              <div className="text-4xl font-bold text-white mb-2">∞</div>
              <div className="text-gray-400">Backtests (Unlimited)</div>
            </div>
          </div>
        </div>
      </div>

      {/* FAQ */}
      <div className="container mx-auto px-4 py-16 border-t border-slate-800">
        <div className="max-w-3xl mx-auto">
          <h2 className="text-3xl font-bold text-white text-center mb-12">Questions?</h2>

          <div className="space-y-6">
            <div className="bg-slate-800/30 rounded-xl p-6 border border-slate-700">
              <h3 className="text-lg font-semibold text-white mb-2">Will you always be free?</h3>
              <p className="text-gray-400">
                Yes! Our commitment is to keep the core platform free forever. If we add premium features, the core
                backtesting suite stays free.
              </p>
            </div>

            <div className="bg-slate-800/30 rounded-xl p-6 border border-slate-700">
              <h3 className="text-lg font-semibold text-white mb-2">Is this data real?</h3>
              <p className="text-gray-400">
                100% real market data from Yahoo Finance. Historical OHLC bars with actual trading volumes. No
                synthetic data.
              </p>
            </div>

            <div className="bg-slate-800/30 rounded-xl p-6 border border-slate-700">
              <h3 className="text-lg font-semibold text-white mb-2">How do you make money?</h3>
              <p className="text-gray-400">
                We earn affiliate commissions when you open a trading account through our platform. You never pay extra
                - your broker just gives us a commission.
              </p>
            </div>

            <div className="bg-slate-800/30 rounded-xl p-6 border border-slate-700">
              <h3 className="text-lg font-semibold text-white mb-2">Can I use this commercially?</h3>
              <p className="text-gray-400">
                Yes! You can use the platform for personal trading, bot development, or even commercial applications.
                Check our terms for details.
              </p>
            </div>
          </div>
        </div>
      </div>

      {/* Final CTA */}
      <div className="container mx-auto px-4 py-20 border-t border-slate-800">
        <div className="max-w-4xl mx-auto text-center">
          <h2 className="text-4xl font-bold text-white mb-6">Ready?</h2>
          <p className="text-xl text-gray-400 mb-8">
            Join traders building their edge with free, professional-grade backtesting.
          </p>
          <a
            href="/auth/register"
            className="bg-gradient-to-r from-green-500 to-blue-600 hover:from-green-600 hover:to-blue-700 text-white font-semibold px-8 py-4 rounded-xl shadow-lg shadow-green-500/25 inline-flex items-center gap-2 transition-all"
          >
            Start Free Now
            <ArrowRight className="w-5 h-5" />
          </a>
        </div>
      </div>
    </div>
  )
}
