'use client'

import { X } from 'lucide-react'
import { useState } from 'react'

interface AdBannerProps {
  position?: 'top' | 'bottom' | 'sidebar'
  userTier?: string
  onClose?: () => void
}

/**
 * Ad Banner Component - Displays for free tier users
 * Sponsors trading platforms and brokers
 */
export function AdBanner({ position = 'bottom', userTier = 'free', onClose }: AdBannerProps) {
  const [isVisible, setIsVisible] = useState(true)

  // Don't show ads for paid tiers
  if (userTier !== 'free') {
    return null
  }

  if (!isVisible) {
    return null
  }

  const handleClose = () => {
    setIsVisible(false)
    onClose?.()
  }

  const adContent = {
    top: {
      title: 'Upgrade to Ad-Free',
      description: 'Remove ads and get faster backtests for just $9.99/month',
      cta: 'Upgrade Now',
      bg: 'bg-gradient-to-r from-blue-500 to-purple-600',
    },
    bottom: {
      title: 'Ready to trade?',
      description: 'Open an account with one of our recommended brokers',
      cta: 'View Brokers',
      bg: 'bg-gradient-to-r from-green-500 to-emerald-600',
    },
    sidebar: {
      title: 'Trading Sponsors',
      description: 'Professional brokers for quantitative traders',
      cta: 'Learn More',
      bg: 'bg-slate-800',
    },
  }

  const config = adContent[position]

  return (
    <div className={`${config.bg} rounded-lg p-4 text-white relative`}>
      <button
        onClick={handleClose}
        className="absolute top-2 right-2 p-1 hover:bg-white/20 rounded-full transition-colors"
        aria-label="Close ad"
      >
        <X className="w-4 h-4" />
      </button>

      <h3 className="font-bold text-sm mb-1">{config.title}</h3>
      <p className="text-xs text-white/90 mb-3">{config.description}</p>

      <button className="w-full bg-white text-gray-900 rounded-md py-2 text-sm font-semibold hover:bg-gray-100 transition-colors">
        {config.cta}
      </button>

      <p className="text-xs text-white/60 mt-2 text-center">
        Free tier users see sponsor ads. <a href="/pricing" className="underline hover:text-white">Upgrade now</a>
      </p>
    </div>
  )
}
