'use client'

import { useEffect, useState } from 'react'
import Link from 'next/link'
import { ArrowLeft, AlertCircle } from 'lucide-react'
import { SubscriptionStatus } from '@/components/subscription/SubscriptionStatus'

interface SubscriptionData {
  tier: string
  status: string
  trial_starts_at?: string
  trial_ends_at?: string
  period_end?: string
  usage?: Record<string, unknown>
}

export default function SubscriptionSettingsPage() {
  const [subscriptionData, setSubscriptionData] = useState<SubscriptionData | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    const fetchSubscriptionData = async () => {
      try {
        const token = localStorage.getItem('token')
        if (!token) {
          window.location.href = '/auth/login'
          return
        }

        const response = await fetch('/api/v1/subscription/status', {
          headers: {
            Authorization: `Bearer ${token}`,
          },
        })

        if (!response.ok) {
          throw new Error('Failed to fetch subscription data')
        }

        const data = await response.json()
        setSubscriptionData(data)
      } catch (err) {
        setError(err instanceof Error ? err.message : 'An error occurred')
      } finally {
        setLoading(false)
      }
    }

    fetchSubscriptionData()
  }, [])

  const handleUpgrade = () => {
    window.location.href = '/pricing'
  }

  const handleStartTrial = async () => {
    try {
      const token = localStorage.getItem('token')
      const response = await fetch('/api/v1/subscription/start-trial', {
        method: 'POST',
        headers: {
          Authorization: `Bearer ${token}`,
        },
      })

      if (response.ok) {
        alert('Free trial started! You have 7 days of premium access.')
        window.location.reload()
      } else {
        const data = await response.json()
        alert(data.detail || 'Failed to start trial')
      }
    } catch (err) {
      alert('Error starting trial')
    }
  }

  const handleDowngrade = async () => {
    if (!confirm('Are you sure? You will lose access to premium features.')) {
      return
    }

    try {
      const token = localStorage.getItem('token')
      const response = await fetch('/api/v1/subscription/downgrade', {
        method: 'POST',
        headers: {
          Authorization: `Bearer ${token}`,
        },
      })

      if (response.ok) {
        alert('Downgraded to free tier')
        window.location.reload()
      } else {
        alert('Failed to downgrade subscription')
      }
    } catch (err) {
      alert('Error downgrading subscription')
    }
  }

  if (loading) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-slate-950 to-slate-900">
        <div className="container mx-auto px-4 py-16">
          <div className="text-center text-white">Loading...</div>
        </div>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-950 to-slate-900">
      <div className="container mx-auto px-4 py-8">
        {/* Header */}
        <div className="flex items-center gap-4 mb-8">
          <Link
            href="/settings"
            className="p-2 hover:bg-slate-800 rounded-lg transition-colors"
          >
            <ArrowLeft className="w-6 h-6 text-gray-400" />
          </Link>
          <h1 className="text-4xl font-bold text-white">Subscription Settings</h1>
        </div>

        {error && (
          <div className="mb-8 p-4 bg-red-500/10 border border-red-500/30 rounded-lg text-red-200">
            {error}
          </div>
        )}

        {subscriptionData && (
          <div className="space-y-8">
            {/* Subscription Status */}
            <div>
              <h2 className="text-2xl font-bold text-white mb-6">Current Subscription</h2>
              <SubscriptionStatus
                tier={subscriptionData.tier}
                status={subscriptionData.status}
                trialEndsAt={subscriptionData.trial_ends_at}
                periodEnd={subscriptionData.period_end}
                onUpgrade={handleUpgrade}
                onStartTrial={handleStartTrial}
              />
            </div>

            {/* Usage Stats */}
            {subscriptionData.usage && (
              <div className="bg-slate-800/50 rounded-lg p-6 border border-slate-700">
                <h3 className="text-xl font-bold text-white mb-4">Usage This Month</h3>
                <div className="grid md:grid-cols-3 gap-4">
                  <div className="bg-slate-900/50 rounded-lg p-4">
                    <p className="text-gray-400 text-sm mb-1">Backtests Used</p>
                    <p className="text-3xl font-bold text-white">
                      {(subscriptionData.usage as any).used || 0}
                    </p>
                  </div>
                  <div className="bg-slate-900/50 rounded-lg p-4">
                    <p className="text-gray-400 text-sm mb-1">Monthly Limit</p>
                    <p className="text-3xl font-bold text-white">
                      {(subscriptionData.usage as any).limit === Infinity
                        ? '∞'
                        : (subscriptionData.usage as any).limit || '∞'}
                    </p>
                  </div>
                  <div className="bg-slate-900/50 rounded-lg p-4">
                    <p className="text-gray-400 text-sm mb-1">Remaining</p>
                    <p className="text-3xl font-bold text-green-400">
                      {(subscriptionData.usage as any).remaining === Infinity
                        ? '∞'
                        : (subscriptionData.usage as any).remaining || '∞'}
                    </p>
                  </div>
                </div>
              </div>
            )}

            {/* Danger Zone */}
            {subscriptionData.tier !== 'free' && (
              <div className="bg-red-500/10 border border-red-500/30 rounded-lg p-6">
                <div className="flex items-start gap-4 mb-4">
                  <AlertCircle className="w-6 h-6 text-red-400 flex-shrink-0 mt-1" />
                  <div>
                    <h3 className="text-lg font-bold text-red-200 mb-2">Danger Zone</h3>
                    <p className="text-red-200/80 mb-4">
                      Downgrading will immediately revoke access to premium features.
                    </p>
                    <button
                      onClick={handleDowngrade}
                      className="px-4 py-2 bg-red-600 hover:bg-red-700 text-white rounded-lg transition-colors font-semibold"
                    >
                      Downgrade to Free Tier
                    </button>
                  </div>
                </div>
              </div>
            )}

            {/* Help */}
            <div className="bg-slate-800/50 rounded-lg p-6 border border-slate-700">
              <h3 className="text-lg font-bold text-white mb-4">Need Help?</h3>
              <p className="text-gray-400 mb-4">
                Have questions about your subscription?{' '}
                <Link href="/contact" className="text-blue-400 hover:text-blue-300">
                  Contact support
                </Link>
                {' or '}
                <Link href="/docs/faq" className="text-blue-400 hover:text-blue-300">
                  read the FAQ
                </Link>
              </p>
            </div>
          </div>
        )}
      </div>
    </div>
  )
}
