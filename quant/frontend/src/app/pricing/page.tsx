/**
 * Pricing Page - Revenue-Generating Subscription Tiers
 *
 * FREE: 3 basic strategies
 * PREMIUM $29/mo: 7 strategies
 * ENTERPRISE $99/mo: 10 strategies + advanced features
 */

'use client'

import { useState } from 'react'
import { Check, X, Zap, TrendingUp, Crown, ArrowRight } from 'lucide-react'

export default function PricingPage() {
  const [billingCycle, setBillingCycle] = useState<'monthly' | 'annual'>('monthly')

  const tiers = [
    {
      name: 'Free',
      tagline: 'Get Started',
      price: 0,
      annualPrice: 0,
      icon: TrendingUp,
      color: 'from-gray-500 to-gray-600',
      features: [
        { name: '3 Basic Strategies', included: true, description: 'MA Crossover, RSI, Bollinger' },
        { name: '3 Backtests per month', included: true },
        { name: '1 Year Historical Data', included: true },
        { name: 'Basic Performance Metrics', included: true },
        { name: 'Community Support', included: true },
        { name: 'Unlimited Backtests', included: false },
        { name: 'Advanced Strategies', included: false },
        { name: 'CSV/PDF Export', included: false },
        { name: 'Portfolio Optimization', included: false },
      ],
      cta: 'Start Free',
      ctaAction: 'register',
      popular: false,
    },
    {
      name: 'Premium',
      tagline: 'Most Popular',
      price: 29,
      annualPrice: 290, // 2 months free
      icon: Zap,
      color: 'from-blue-500 to-purple-600',
      features: [
        { name: '7 Total Strategies', included: true, description: 'All free + MACD, Z-Score, Momentum, Triple EMA' },
        { name: 'Unlimited Backtests', included: true },
        { name: '10 Years Historical Data', included: true },
        { name: 'Advanced Performance Metrics', included: true },
        { name: 'CSV Export', included: true },
        { name: 'Email Support', included: true },
        { name: 'Strategy Comparison', included: true },
        { name: 'Real-time Notifications', included: true },
        { name: 'Portfolio Optimization', included: false },
      ],
      cta: 'Start Premium',
      ctaAction: 'checkout-premium',
      popular: true,
    },
    {
      name: 'Enterprise',
      tagline: 'Professional',
      price: 99,
      annualPrice: 990, // 2 months free
      icon: Crown,
      color: 'from-purple-600 to-pink-600',
      features: [
        { name: '10 Total Strategies', included: true, description: 'All premium + Ichimoku, Multi-TF, ATR Volatility' },
        { name: 'Unlimited Backtests', included: true },
        { name: 'Full Historical Data', included: true },
        { name: 'Professional Analytics', included: true },
        { name: 'CSV + PDF Export', included: true },
        { name: 'Priority Support', included: true },
        { name: 'Walk-Forward Analysis', included: true },
        { name: 'Portfolio Optimization', included: true },
        { name: 'Monte Carlo Simulation', included: true },
      ],
      cta: 'Start Enterprise',
      ctaAction: 'checkout-enterprise',
      popular: false,
    },
  ]

  const handleCTA = async (action: string) => {
    if (action === 'register') {
      window.location.href = '/auth/register'
    } else if (action.startsWith('checkout-')) {
      const tier = action.replace('checkout-', '').toUpperCase()

      try {
        // Call backend to create Stripe checkout session
        const response = await fetch('/api/v1/subscriptions/subscribe', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            // Include auth token if user is logged in
            ...(localStorage.getItem('token') && {
              Authorization: `Bearer ${localStorage.getItem('token')}`,
            }),
          },
          body: JSON.stringify({
            tier,
            billing_cycle: billingCycle === 'annual' ? 'yearly' : 'monthly',
          }),
        })

        if (!response.ok) {
          const error = await response.json()
          throw new Error(error.detail || 'Failed to create checkout session')
        }

        const data = await response.json()

        // Redirect to Stripe Checkout or show success
        if (data.checkout_url) {
          window.location.href = data.checkout_url
        } else {
          // Subscription updated directly (for logged-in users)
          alert(`Successfully upgraded to ${tier} tier!`)
          window.location.reload()
        }
      } catch (error) {
        console.error('Checkout error:', error)
        alert(
          error instanceof Error
            ? error.message
            : 'Failed to initiate checkout. Please try again or contact support.'
        )
      }
    }
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-950 via-slate-900 to-slate-950">
      {/* Header */}
      <div className="container mx-auto px-4 py-16 text-center">
        <div className="inline-block mb-4 px-4 py-2 bg-blue-500/10 rounded-full border border-blue-500/20">
          <span className="text-blue-400 text-sm font-medium">🚀 Revenue-Generating Trading Platform</span>
        </div>

        <h1 className="text-5xl md:text-6xl font-bold text-white mb-6">
          Choose Your
          <span className="bg-gradient-to-r from-blue-400 to-purple-600 bg-clip-text text-transparent"> Trading Edge</span>
        </h1>

        <p className="text-xl text-gray-400 max-w-2xl mx-auto mb-12">
          Professional backtesting strategies with real market data. Start free, upgrade when you're ready.
        </p>

        {/* Billing Toggle */}
        <div className="inline-flex items-center gap-4 bg-slate-800/50 rounded-full p-1.5 border border-slate-700">
          <button
            onClick={() => setBillingCycle('monthly')}
            className={`px-6 py-2 rounded-full text-sm font-medium transition-all ${
              billingCycle === 'monthly'
                ? 'bg-gradient-to-r from-blue-500 to-purple-600 text-white shadow-lg'
                : 'text-gray-400 hover:text-white'
            }`}
          >
            Monthly
          </button>
          <button
            onClick={() => setBillingCycle('annual')}
            className={`px-6 py-2 rounded-full text-sm font-medium transition-all flex items-center gap-2 ${
              billingCycle === 'annual'
                ? 'bg-gradient-to-r from-blue-500 to-purple-600 text-white shadow-lg'
                : 'text-gray-400 hover:text-white'
            }`}
          >
            Annual
            <span className="bg-green-500/20 text-green-400 text-xs px-2 py-0.5 rounded-full">
              Save 17%
            </span>
          </button>
        </div>
      </div>

      {/* Pricing Cards */}
      <div className="container mx-auto px-4 pb-16">
        <div className="grid md:grid-cols-3 gap-8 max-w-7xl mx-auto">
          {tiers.map((tier) => {
            const Icon = tier.icon
            const displayPrice = billingCycle === 'monthly' ? tier.price : tier.annualPrice
            const perMonth = billingCycle === 'monthly' ? '/mo' : '/year'

            return (
              <div
                key={tier.name}
                className={`relative rounded-2xl border ${
                  tier.popular
                    ? 'border-blue-500/50 bg-gradient-to-b from-blue-500/5 to-transparent'
                    : 'border-slate-700 bg-slate-800/30'
                } p-8 hover:border-blue-500/30 transition-all duration-300 hover:scale-105`}
              >
                {/* Popular Badge */}
                {tier.popular && (
                  <div className="absolute -top-4 left-1/2 -translate-x-1/2">
                    <div className="bg-gradient-to-r from-blue-500 to-purple-600 px-4 py-1 rounded-full text-sm font-semibold text-white shadow-lg">
                      {tier.tagline}
                    </div>
                  </div>
                )}

                {/* Icon */}
                <div className={`w-14 h-14 rounded-xl bg-gradient-to-br ${tier.color} flex items-center justify-center mb-6`}>
                  <Icon className="w-7 h-7 text-white" />
                </div>

                {/* Tier Name */}
                <h3 className="text-2xl font-bold text-white mb-2">{tier.name}</h3>
                {!tier.popular && (
                  <p className="text-sm text-gray-400 mb-6">{tier.tagline}</p>
                )}

                {/* Price */}
                <div className="mb-8">
                  <div className="flex items-baseline gap-2">
                    <span className="text-5xl font-bold text-white">
                      ${displayPrice}
                    </span>
                    <span className="text-gray-400 text-lg">{perMonth}</span>
                  </div>
                  {billingCycle === 'annual' && displayPrice > 0 && (
                    <p className="text-sm text-green-400 mt-2">
                      ${tier.price}/mo × 10 months
                    </p>
                  )}
                </div>

                {/* CTA Button */}
                <button
                  onClick={() => handleCTA(tier.ctaAction)}
                  className={`w-full py-3 rounded-xl font-semibold text-white mb-8 transition-all flex items-center justify-center gap-2 ${
                    tier.popular
                      ? 'bg-gradient-to-r from-blue-500 to-purple-600 hover:from-blue-600 hover:to-purple-700 shadow-lg shadow-blue-500/25'
                      : 'bg-slate-700 hover:bg-slate-600'
                  }`}
                >
                  {tier.cta}
                  <ArrowRight className="w-4 h-4" />
                </button>

                {/* Features */}
                <div className="space-y-4">
                  {tier.features.map((feature, idx) => (
                    <div key={idx} className="flex items-start gap-3">
                      <div
                        className={`flex-shrink-0 w-5 h-5 rounded-full flex items-center justify-center ${
                          feature.included ? 'bg-green-500/20' : 'bg-slate-700/50'
                        }`}
                      >
                        {feature.included ? (
                          <Check className="w-3 h-3 text-green-400" />
                        ) : (
                          <X className="w-3 h-3 text-gray-600" />
                        )}
                      </div>
                      <div className="flex-1">
                        <p
                          className={`text-sm ${
                            feature.included ? 'text-white' : 'text-gray-600'
                          }`}
                        >
                          {feature.name}
                        </p>
                        {feature.description && (
                          <p className="text-xs text-gray-500 mt-0.5">
                            {feature.description}
                          </p>
                        )}
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            )
          })}
        </div>
      </div>

      {/* Social Proof */}
      <div className="container mx-auto px-4 py-16 border-t border-slate-800">
        <div className="max-w-4xl mx-auto text-center">
          <h2 className="text-3xl font-bold text-white mb-12">
            Trusted by Traders Worldwide
          </h2>

          <div className="grid md:grid-cols-3 gap-8 mb-12">
            <div className="bg-slate-800/30 rounded-xl p-6 border border-slate-700">
              <div className="text-4xl font-bold text-white mb-2">10</div>
              <div className="text-gray-400">Professional Strategies</div>
            </div>
            <div className="bg-slate-800/30 rounded-xl p-6 border border-slate-700">
              <div className="text-4xl font-bold text-white mb-2">10+</div>
              <div className="text-gray-400">Years Historical Data</div>
            </div>
            <div className="bg-slate-800/30 rounded-xl p-6 border border-slate-700">
              <div className="text-4xl font-bold text-white mb-2">Free</div>
              <div className="text-gray-400">Yahoo Finance API</div>
            </div>
          </div>

          {/* Testimonials Placeholder */}
          <div className="grid md:grid-cols-2 gap-6">
            <div className="bg-slate-800/30 rounded-xl p-6 border border-slate-700 text-left">
              <div className="flex gap-1 mb-3">
                {[...Array(5)].map((_, i) => (
                  <span key={i} className="text-yellow-400">★</span>
                ))}
              </div>
              <p className="text-gray-300 mb-4">
                "The Ichimoku Cloud strategy alone is worth the Enterprise subscription. Professional-grade backtesting."
              </p>
              <p className="text-sm text-gray-500">— Alex K., Day Trader</p>
            </div>
            <div className="bg-slate-800/30 rounded-xl p-6 border border-slate-700 text-left">
              <div className="flex gap-1 mb-3">
                {[...Array(5)].map((_, i) => (
                  <span key={i} className="text-yellow-400">★</span>
                ))}
              </div>
              <p className="text-gray-300 mb-4">
                "Finally, a backtesting platform that doesn't break the bank. The free tier got me hooked!"
              </p>
              <p className="text-sm text-gray-500">— Sarah M., Retail Investor</p>
            </div>
          </div>
        </div>
      </div>

      {/* FAQ Section */}
      <div className="container mx-auto px-4 py-16 border-t border-slate-800">
        <div className="max-w-3xl mx-auto">
          <h2 className="text-3xl font-bold text-white text-center mb-12">
            Frequently Asked Questions
          </h2>

          <div className="space-y-6">
            <div className="bg-slate-800/30 rounded-xl p-6 border border-slate-700">
              <h3 className="text-lg font-semibold text-white mb-2">
                Can I cancel anytime?
              </h3>
              <p className="text-gray-400">
                Yes! All subscriptions are month-to-month or annual. Cancel anytime with no questions asked.
              </p>
            </div>

            <div className="bg-slate-800/30 rounded-xl p-6 border border-slate-700">
              <h3 className="text-lg font-semibold text-white mb-2">
                What's included in the Free tier?
              </h3>
              <p className="text-gray-400">
                3 professional strategies (MA Crossover, RSI, Bollinger), 3 backtests per month, and 1 year of historical data.
              </p>
            </div>

            <div className="bg-slate-800/30 rounded-xl p-6 border border-slate-700">
              <h3 className="text-lg font-semibold text-white mb-2">
                Is the data real or simulated?
              </h3>
              <p className="text-gray-400">
                100% real market data from Yahoo Finance. No synthetic data. Historical OHLC bars with actual volumes.
              </p>
            </div>

            <div className="bg-slate-800/30 rounded-xl p-6 border border-slate-700">
              <h3 className="text-lg font-semibold text-white mb-2">
                Can I upgrade or downgrade?
              </h3>
              <p className="text-gray-400">
                Absolutely! Upgrade instantly to unlock more strategies. Downgrades take effect at the end of your billing cycle.
              </p>
            </div>
          </div>
        </div>
      </div>

      {/* Final CTA */}
      <div className="container mx-auto px-4 py-16 border-t border-slate-800">
        <div className="max-w-4xl mx-auto text-center">
          <h2 className="text-4xl font-bold text-white mb-6">
            Ready to Start Backtesting?
          </h2>
          <p className="text-xl text-gray-400 mb-8">
            Join thousands of traders using professional strategies with real market data.
          </p>
          <button
            onClick={() => handleCTA('register')}
            className="bg-gradient-to-r from-blue-500 to-purple-600 hover:from-blue-600 hover:to-purple-700 text-white font-semibold px-8 py-4 rounded-xl shadow-lg shadow-blue-500/25 inline-flex items-center gap-2 transition-all"
          >
            Start Free Trial
            <ArrowRight className="w-5 h-5" />
          </button>
        </div>
      </div>
    </div>
  )
}
