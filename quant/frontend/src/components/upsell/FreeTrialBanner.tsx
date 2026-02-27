'use client'

import { useState } from 'react'
import { Zap, X } from 'lucide-react'
import Link from 'next/link'

interface FreeTrialBannerProps {
  trialDaysRemaining?: number
  onClose?: () => void
}

export function FreeTrialBanner({
  trialDaysRemaining,
  onClose,
}: FreeTrialBannerProps) {
  const [dismissed, setDismissed] = useState(false)

  if (dismissed) return null

  // If user already used trial, show upgrade message
  if (trialDaysRemaining === 0) {
    return (
      <div className="bg-gradient-to-r from-orange-600 to-red-600 text-white rounded-lg p-4 flex items-center justify-between">
        <div className="flex items-center gap-3">
          <Zap className="w-5 h-5" />
          <div>
            <p className="font-semibold">Trial Ended</p>
            <p className="text-sm text-white/90">Upgrade to Premium to keep using advanced features</p>
          </div>
        </div>
        <Link
          href="/pricing"
          className="px-4 py-2 bg-white text-orange-600 font-semibold rounded hover:bg-orange-50 transition-colors whitespace-nowrap"
        >
          Upgrade Now
        </Link>
      </div>
    )
  }

  // If user has trial days remaining, show countdown
  if (trialDaysRemaining && trialDaysRemaining > 0) {
    return (
      <div className="bg-gradient-to-r from-green-600 to-emerald-600 text-white rounded-lg p-4 flex items-center justify-between">
        <div className="flex items-center gap-3 flex-1">
          <Zap className="w-5 h-5" />
          <div>
            <p className="font-semibold">Free Trial Active</p>
            <p className="text-sm text-white/90">
              {trialDaysRemaining} day{trialDaysRemaining !== 1 ? 's' : ''} remaining • 50
              backtests/month
            </p>
          </div>
        </div>
        <div className="flex items-center gap-2">
          <button
            onClick={() => {
              setDismissed(true)
              onClose?.()
            }}
            className="p-1 hover:bg-white/20 rounded transition-colors"
          >
            <X className="w-4 h-4" />
          </button>
        </div>
      </div>
    )
  }

  // Default: Show trial offer
  return (
    <div className="bg-gradient-to-r from-blue-600 to-purple-600 text-white rounded-lg p-6">
      <div className="flex items-start justify-between mb-4">
        <div className="flex items-start gap-3">
          <Zap className="w-6 h-6 flex-shrink-0 mt-0.5" />
          <div>
            <h3 className="text-lg font-bold mb-2">Try Premium Free for 7 Days</h3>
            <ul className="text-sm text-white/90 space-y-1">
              <li>✓ 50 backtests/month (vs 5 free)</li>
              <li>✓ All 10+ professional strategies</li>
              <li>✓ Advanced portfolio optimization</li>
              <li>✓ Email alerts & notifications</li>
            </ul>
          </div>
        </div>
        <button
          onClick={() => setDismissed(true)}
          className="p-1 hover:bg-white/20 rounded transition-colors flex-shrink-0"
        >
          <X className="w-4 h-4" />
        </button>
      </div>

      <div className="flex gap-3">
        <Link
          href="/auth/start-trial"
          className="flex-1 bg-white text-blue-600 px-4 py-2 rounded-lg font-semibold hover:bg-blue-50 transition-colors text-center"
        >
          Start Free Trial
        </Link>
        <button
          onClick={() => setDismissed(true)}
          className="px-4 py-2 border border-white/30 hover:border-white/50 rounded-lg font-semibold transition-colors"
        >
          Later
        </button>
      </div>
    </div>
  )
}
