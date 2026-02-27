'use client'

import { useState, useEffect } from 'react'
import Link from 'next/link'
import { ExternalLink, ChevronRight } from 'lucide-react'
import { api } from '@/lib/api-client'

interface BrokerRecommendation {
  broker: string
  name: string
  logo_url: string
  signup_url: string
  description: string
  features: string[]
  recommended_for: string[]
  commission: number
  display_commission: string
}

interface BrokerRecommendationsProps {
  strategy?: string
  userTier?: string
}

export function BrokerRecommendations({
  strategy = 'trend',
  userTier = 'free',
}: BrokerRecommendationsProps) {
  const [brokers, setBrokers] = useState<BrokerRecommendation[]>([])
  const [loading, setLoading] = useState(true)
  const [clicked, setClicked] = useState<string | null>(null)

  useEffect(() => {
    const fetchRecommendations = async () => {
      try {
        setLoading(true)
        // Fetch recommended brokers for the strategy
        const response = await fetch(
          `/api/v1/affiliate/brokers/recommendations?strategy=${strategy}&user_tier=${userTier}`
        )
        if (response.ok) {
          const data = await response.json()
          setBrokers(data.slice(0, 3)) // Show top 3
        }
      } catch (error) {
        console.error('Failed to fetch broker recommendations:', error)
      } finally {
        setLoading(false)
      }
    }

    fetchRecommendations()
  }, [strategy, userTier])

  const handleBrokerClick = async (broker: BrokerRecommendation) => {
    setClicked(broker.broker)

    // Track the click
    try {
      await fetch(`/api/v1/affiliate/track-click`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          broker: broker.broker,
          strategy: strategy,
        }),
      })
    } catch (error) {
      console.error('Failed to track affiliate click:', error)
    }

    // Open affiliate link
    window.open(broker.signup_url, '_blank')
  }

  if (loading) {
    return (
      <div className="glass-strong rounded-xl p-6 animate-pulse">
        <div className="h-6 bg-slate-700 rounded w-40 mb-4"></div>
        <div className="space-y-3">
          {[1, 2, 3].map(i => (
            <div key={i} className="h-20 bg-slate-700 rounded"></div>
          ))}
        </div>
      </div>
    )
  }

  if (!brokers.length) {
    return null
  }

  return (
    <div className="glass-strong rounded-xl p-6">
      <div className="mb-6">
        <h3 className="text-lg font-bold mb-2">
          Recommended Brokers for {strategy}
        </h3>
        <p className="text-sm text-muted-foreground">
          These brokers are optimized for your strategy. We earn a small commission
          if you sign up, at no cost to you.
        </p>
      </div>

      <div className="space-y-4">
        {brokers.map(broker => (
          <div
            key={broker.broker}
            className="border border-slate-700 rounded-lg p-4 hover:border-slate-600 hover:bg-slate-800/50 transition-colors"
          >
            <div className="flex items-start justify-between gap-4 mb-3">
              <div className="flex-1">
                <h4 className="font-bold text-white mb-1">{broker.name}</h4>
                <p className="text-sm text-muted-foreground mb-2">
                  {broker.description}
                </p>
              </div>
              <div className="text-right whitespace-nowrap">
                <div className="text-xs text-green-400 font-semibold">
                  {broker.display_commission} commission
                </div>
              </div>
            </div>

            {/* Features */}
            <div className="mb-3 flex flex-wrap gap-2">
              {broker.features.slice(0, 3).map((feature, i) => (
                <span
                  key={i}
                  className="text-xs bg-slate-900/50 text-slate-300 px-2 py-1 rounded"
                >
                  {feature}
                </span>
              ))}
            </div>

            {/* Recommended for */}
            <div className="mb-4">
              <div className="text-xs text-muted-foreground mb-1">Recommended for:</div>
              <div className="flex flex-wrap gap-1">
                {broker.recommended_for.map((rec, i) => (
                  <span key={i} className="text-xs text-blue-400">
                    {rec}
                    {i < broker.recommended_for.length - 1 && ', '}
                  </span>
                ))}
              </div>
            </div>

            {/* CTA Button */}
            <button
              onClick={() => handleBrokerClick(broker)}
              className="w-full flex items-center justify-between px-4 py-2 bg-blue-600 hover:bg-blue-500 text-white rounded-lg font-medium transition-colors"
            >
              <span>Open Account</span>
              {clicked === broker.broker ? (
                <span className="text-sm">Opening...</span>
              ) : (
                <ExternalLink className="w-4 h-4" />
              )}
            </button>
          </div>
        ))}
      </div>

      {/* Disclaimer */}
      <div className="mt-4 text-xs text-muted-foreground border-t border-slate-700 pt-4">
        <p>
          We may earn an affiliate commission from broker signups at no additional cost
          to you. This helps support the platform's development.
        </p>
      </div>
    </div>
  )
}
