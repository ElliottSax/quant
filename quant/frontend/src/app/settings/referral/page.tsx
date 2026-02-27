'use client'

import { useEffect, useState } from 'react'
import Link from 'next/link'
import { ArrowLeft } from 'lucide-react'
import { ReferralCode } from '@/components/referral/ReferralCode'

interface ReferralData {
  referral_code: string
  referral_credit: number
  referral_url: string
}

export default function ReferralSettingsPage() {
  const [referralData, setReferralData] = useState<ReferralData | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    const fetchReferralData = async () => {
      try {
        const token = localStorage.getItem('token')
        if (!token) {
          window.location.href = '/auth/login'
          return
        }

        const response = await fetch('/api/v1/subscription/referral/code', {
          headers: {
            Authorization: `Bearer ${token}`,
          },
        })

        if (!response.ok) {
          throw new Error('Failed to fetch referral data')
        }

        const data = await response.json()
        setReferralData(data)
      } catch (err) {
        setError(err instanceof Error ? err.message : 'An error occurred')
      } finally {
        setLoading(false)
      }
    }

    fetchReferralData()
  }, [])

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
          <h1 className="text-4xl font-bold text-white">Referral Program</h1>
        </div>

        {error && (
          <div className="mb-8 p-4 bg-red-500/10 border border-red-500/30 rounded-lg text-red-200">
            {error}
          </div>
        )}

        {referralData && (
          <div className="space-y-8">
            {/* Referral Code Component */}
            <div>
              <ReferralCode
                code={referralData.referral_code}
                creditBalance={referralData.referral_credit}
              />
            </div>

            {/* How It Works */}
            <div className="bg-slate-800/50 rounded-lg p-6 border border-slate-700">
              <h3 className="text-2xl font-bold text-white mb-4">How It Works</h3>
              <ol className="space-y-4 text-gray-300">
                <li className="flex gap-4">
                  <span className="flex-shrink-0 w-8 h-8 bg-blue-600 text-white rounded-full flex items-center justify-center font-bold">
                    1
                  </span>
                  <div>
                    <p className="font-semibold text-white">Share Your Code</p>
                    <p className="text-sm">
                      Copy your unique referral code and share it with friends, family, or your trading community.
                    </p>
                  </div>
                </li>
                <li className="flex gap-4">
                  <span className="flex-shrink-0 w-8 h-8 bg-blue-600 text-white rounded-full flex items-center justify-center font-bold">
                    2
                  </span>
                  <div>
                    <p className="font-semibold text-white">They Sign Up</p>
                    <p className="text-sm">
                      Your friend creates an account using your referral code or link.
                    </p>
                  </div>
                </li>
                <li className="flex gap-4">
                  <span className="flex-shrink-0 w-8 h-8 bg-blue-600 text-white rounded-full flex items-center justify-center font-bold">
                    3
                  </span>
                  <div>
                    <p className="font-semibold text-white">They Verify Email</p>
                    <p className="text-sm">
                      Once they verify their email address, the referral is complete.
                    </p>
                  </div>
                </li>
                <li className="flex gap-4">
                  <span className="flex-shrink-0 w-8 h-8 bg-green-600 text-white rounded-full flex items-center justify-center font-bold">
                    4
                  </span>
                  <div>
                    <p className="font-semibold text-white">You Get $10 Credit</p>
                    <p className="text-sm">
                      Instantly receive $10 in account credits that can be applied to any subscription tier.
                    </p>
                  </div>
                </li>
              </ol>
            </div>

            {/* Benefits */}
            <div className="grid md:grid-cols-2 gap-6">
              <div className="bg-blue-500/10 rounded-lg p-6 border border-blue-500/30">
                <h4 className="text-lg font-bold text-blue-200 mb-3">For You</h4>
                <ul className="space-y-2 text-blue-100/80 text-sm">
                  <li>✓ Earn $10 per successful referral</li>
                  <li>✓ Unlimited earning potential</li>
                  <li>✓ Credits apply to any tier upgrade</li>
                  <li>✓ Track your earnings in real-time</li>
                </ul>
              </div>
              <div className="bg-green-500/10 rounded-lg p-6 border border-green-500/30">
                <h4 className="text-lg font-bold text-green-200 mb-3">For Your Friends</h4>
                <ul className="space-y-2 text-green-100/80 text-sm">
                  <li>✓ No risk - try free tier first</li>
                  <li>✓ Full access to all backtesting features</li>
                  <li>✓ Unlimited historical data</li>
                  <li>✓ Join a growing trading community</li>
                </ul>
              </div>
            </div>

            {/* FAQ */}
            <div className="bg-slate-800/50 rounded-lg p-6 border border-slate-700">
              <h3 className="text-xl font-bold text-white mb-4">Frequently Asked Questions</h3>
              <div className="space-y-4">
                <div>
                  <p className="font-semibold text-white mb-2">When do I get my credit?</p>
                  <p className="text-gray-400 text-sm">
                    You'll receive your $10 credit immediately after your referred friend verifies their email address.
                  </p>
                </div>
                <div>
                  <p className="font-semibold text-white mb-2">Can I use credits on any tier?</p>
                  <p className="text-gray-400 text-sm">
                    Yes! Your referral credits can be applied to any paid subscription tier upgrade.
                  </p>
                </div>
                <div>
                  <p className="font-semibold text-white mb-2">Is there a limit to referrals?</p>
                  <p className="text-gray-400 text-sm">
                    No! You can refer as many people as you'd like and earn unlimited credits.
                  </p>
                </div>
                <div>
                  <p className="font-semibold text-white mb-2">Can my credits expire?</p>
                  <p className="text-gray-400 text-sm">
                    Credits don't expire, so feel free to save them up and use them whenever you want.
                  </p>
                </div>
              </div>
            </div>

            {/* Share Buttons */}
            <div className="bg-gradient-to-r from-blue-600 to-purple-600 rounded-lg p-8 text-center">
              <h3 className="text-2xl font-bold text-white mb-4">Start Sharing!</h3>
              <p className="text-white/90 mb-6">
                Your referral code is ready to share. Every person who signs up through your link helps you earn credits.
              </p>
              <div className="flex flex-wrap justify-center gap-3">
                <a
                  href={`https://twitter.com/intent/tweet?text=Check%20out%20this%20awesome%20backtesting%20platform!%20Get%20started%20free:%20${referralData.referral_url}`}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="px-6 py-2 bg-white text-blue-600 rounded-lg font-semibold hover:bg-gray-100 transition-colors"
                >
                  Share on Twitter
                </a>
                <a
                  href={`https://reddit.com/r/algotrading`}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="px-6 py-2 bg-white text-orange-600 rounded-lg font-semibold hover:bg-gray-100 transition-colors"
                >
                  Post on Reddit
                </a>
                <button
                  onClick={() => {
                    navigator.clipboard.writeText(referralData.referral_url)
                    alert('Referral link copied to clipboard!')
                  }}
                  className="px-6 py-2 bg-white text-purple-600 rounded-lg font-semibold hover:bg-gray-100 transition-colors"
                >
                  Copy Link
                </button>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  )
}
