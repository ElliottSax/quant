'use client'

import { useState } from 'react'
import { X, Zap, ArrowRight } from 'lucide-react'
import Link from 'next/link'

interface UpgradePromptProps {
  feature: string
  reason: string
  tier: 'premium' | 'enterprise'
  onDismiss?: () => void
}

export function UpgradePrompt({
  feature,
  reason,
  tier,
  onDismiss,
}: UpgradePromptProps) {
  const [dismissed, setDismissed] = useState(false)

  if (dismissed) return null

  const tierInfo = {
    premium: {
      name: 'Premium',
      price: '$29/mo',
      color: 'from-blue-600 to-cyan-600',
      buttonColor: 'bg-blue-600 hover:bg-blue-500',
    },
    enterprise: {
      name: 'Enterprise',
      price: 'Custom',
      color: 'from-purple-600 to-pink-600',
      buttonColor: 'bg-purple-600 hover:bg-purple-500',
    },
  }

  const info = tierInfo[tier]

  return (
    <div className={`relative overflow-hidden rounded-lg bg-gradient-to-r ${info.color} p-6 text-white`}>
      {/* Dismiss button */}
      <button
        onClick={() => {
          setDismissed(true)
          onDismiss?.()
        }}
        className="absolute top-4 right-4 p-1 hover:bg-white/20 rounded transition-colors"
      >
        <X className="w-4 h-4" />
      </button>

      <div className="max-w-2xl">
        <div className="flex items-start gap-3 mb-4">
          <Zap className="w-6 h-6 flex-shrink-0 mt-1" />
          <div>
            <h3 className="text-lg font-bold mb-1">Unlock {feature}</h3>
            <p className="text-sm text-white/90">{reason}</p>
          </div>
        </div>

        <div className="flex items-center gap-4">
          <div className="flex-1">
            <div className="text-sm text-white/80 mb-1">{info.name} Tier</div>
            <div className="text-2xl font-bold">{info.price}</div>
          </div>

          <Link
            href="/pricing"
            className={`${info.buttonColor} text-white px-6 py-2 rounded-lg font-medium flex items-center gap-2 transition-colors`}
          >
            Learn More
            <ArrowRight className="w-4 h-4" />
          </Link>
        </div>
      </div>
    </div>
  )
}
