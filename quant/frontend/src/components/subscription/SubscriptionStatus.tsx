'use client'

import { useState } from 'react'
import { Check, AlertCircle, Clock } from 'lucide-react'

interface SubscriptionStatusProps {
  tier: string
  status: string
  trialEndsAt?: string
  periodEnd?: string
  onUpgrade?: () => void
  onStartTrial?: () => void
}

/**
 * Subscription Status Component
 * Display current subscription tier and offers
 */
export function SubscriptionStatus({
  tier,
  status,
  trialEndsAt,
  periodEnd,
  onUpgrade,
  onStartTrial,
}: SubscriptionStatusProps) {
  const [showTrialOffer, setShowTrialOffer] = useState(true)

  const tierConfig = {
    free: {
      name: 'Free',
      color: 'from-gray-500 to-gray-600',
      badge: 'Free Tier',
      description: 'Ad-supported, unlimited backtests',
      features: ['Unlimited backtests', 'All strategies', 'Basic analytics'],
    },
    starter: {
      name: 'Starter',
      color: 'from-blue-500 to-purple-600',
      badge: 'Popular',
      description: 'Ad-free experience with faster backtests',
      features: ['Ad-free experience', '2x faster backtests', 'CSV export', 'Advanced analytics'],
      price: '$9.99/month',
    },
    professional: {
      name: 'Professional',
      color: 'from-purple-600 to-pink-600',
      badge: 'Premium',
      description: 'Full suite of professional tools',
      features: ['All Starter features', 'Portfolio tracking', 'Email alerts', 'API access'],
      price: '$29/month',
    },
    enterprise: {
      name: 'Enterprise',
      color: 'from-amber-500 to-red-600',
      badge: 'Custom',
      description: 'Everything with dedicated support',
      features: ['All Professional features', 'White label', 'Dedicated support'],
    },
  }

  const config = tierConfig[tier as keyof typeof tierConfig] || tierConfig.free

  const isTrialing = status === 'trialing' && trialEndsAt
  const isActive = status === 'active'
  const trialDaysRemaining = isTrialing ? calculateDaysRemaining(trialEndsAt!) : 0

  return (
    <div className="space-y-4">
      {/* Current Subscription Card */}
      <div className={`bg-gradient-to-br ${config.color} rounded-lg p-6 text-white relative overflow-hidden`}>
        {/* Background pattern */}
        <div className="absolute top-0 right-0 w-40 h-40 bg-white/10 rounded-full -mr-20 -mt-20"></div>

        <div className="relative z-10">
          <div className="flex justify-between items-start mb-4">
            <div>
              <h3 className="text-3xl font-bold">{config.name}</h3>
              <p className="text-white/80 text-sm mt-1">{config.description}</p>
            </div>
            <span className="px-3 py-1 bg-white/30 rounded-full text-sm font-semibold whitespace-nowrap">
              {config.badge}
            </span>
          </div>

          {/* Trial Banner */}
          {isTrialing && (
            <div className="bg-white/20 rounded-lg p-3 mb-4 border border-white/30 flex items-start gap-3">
              <Clock className="w-5 h-5 flex-shrink-0 mt-0.5" />
              <div>
                <p className="font-semibold text-sm">Free Trial Active</p>
                <p className="text-white/90 text-sm">{trialDaysRemaining} days remaining</p>
              </div>
            </div>
          )}

          {/* Features List */}
          <div className="space-y-2 mb-6">
            {config.features.map((feature, idx) => (
              <div key={idx} className="flex items-center gap-2">
                <Check className="w-4 h-4 flex-shrink-0" />
                <span className="text-sm">{feature}</span>
              </div>
            ))}
          </div>

          {/* Price and Actions */}
          {config.price && (
            <div className="flex items-center justify-between">
              <div>
                <p className="text-white/80 text-sm">Pricing</p>
                <p className="text-2xl font-bold">{config.price}</p>
              </div>
              {tier === 'free' && (
                <button
                  onClick={onUpgrade}
                  className="px-6 py-2 bg-white text-gray-900 rounded-lg font-semibold hover:bg-gray-100 transition-colors"
                >
                  Upgrade
                </button>
              )}
            </div>
          )}
        </div>
      </div>

      {/* Trial Offer (for free tier) */}
      {tier === 'free' && showTrialOffer && (
        <div className="bg-gradient-to-r from-amber-50 to-orange-50 dark:from-amber-900/20 dark:to-orange-900/20 rounded-lg p-4 border border-amber-200 dark:border-amber-800">
          <div className="flex gap-3">
            <AlertCircle className="w-5 h-5 text-amber-600 dark:text-amber-400 flex-shrink-0 mt-0.5" />
            <div className="flex-1">
              <h4 className="font-semibold text-amber-900 dark:text-amber-200 mb-1">Start Your Free Trial</h4>
              <p className="text-sm text-amber-800 dark:text-amber-300 mb-3">
                Get 7 days of ad-free, faster backtests completely free. No credit card required!
              </p>
              <button
                onClick={onStartTrial}
                className="px-4 py-2 bg-amber-600 hover:bg-amber-700 text-white rounded-lg text-sm font-medium transition-colors"
              >
                Start Free Trial
              </button>
            </div>
            <button
              onClick={() => setShowTrialOffer(false)}
              className="text-amber-600 dark:text-amber-400 hover:text-amber-700 dark:hover:text-amber-300 font-bold text-lg"
            >
              ×
            </button>
          </div>
        </div>
      )}

      {/* Period Info */}
      {periodEnd && (
        <div className="text-sm text-gray-600 dark:text-gray-400 bg-gray-100 dark:bg-gray-800 rounded-lg p-3">
          <p>Current billing period ends: {new Date(periodEnd).toLocaleDateString()}</p>
        </div>
      )}
    </div>
  )
}

function calculateDaysRemaining(dateString: string): number {
  const date = new Date(dateString)
  const today = new Date()
  const diffMs = date.getTime() - today.getTime()
  return Math.ceil(diffMs / (1000 * 60 * 60 * 24))
}
