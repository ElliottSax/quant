'use client'

import { useState } from 'react'
import { Copy, Share2, CheckCircle } from 'lucide-react'

interface ReferralCodeProps {
  code: string
  creditBalance: number
  onShare?: () => void
}

/**
 * Referral Code Component
 * Display user's referral code and track earnings
 */
export function ReferralCode({ code, creditBalance, onShare }: ReferralCodeProps) {
  const [copied, setCopied] = useState(false)

  const referralUrl = `${typeof window !== 'undefined' ? window.location.origin : ''}/signup?ref=${code}`

  const handleCopyCode = () => {
    navigator.clipboard.writeText(code)
    setCopied(true)
    setTimeout(() => setCopied(false), 2000)
  }

  const handleCopyUrl = () => {
    navigator.clipboard.writeText(referralUrl)
    setCopied(true)
    setTimeout(() => setCopied(false), 2000)
  }

  const handleShare = () => {
    if (navigator.share) {
      navigator.share({
        title: 'Quant Trading Platform',
        text: 'Join me on Quant - professional backtesting for traders. Get $10 credit with my referral code!',
        url: referralUrl,
      })
    }
    onShare?.()
  }

  return (
    <div className="bg-gradient-to-br from-blue-50 to-purple-50 dark:from-blue-900/20 dark:to-purple-900/20 rounded-lg p-6 border border-blue-200 dark:border-blue-800">
      <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">Referral Program</h3>

      {/* Referral Code Section */}
      <div className="mb-6">
        <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">Your Referral Code</label>
        <div className="flex gap-2">
          <div className="flex-1 bg-white dark:bg-gray-800 rounded-lg px-4 py-3 text-sm font-mono text-gray-900 dark:text-white border border-gray-300 dark:border-gray-600">
            {code}
          </div>
          <button
            onClick={handleCopyCode}
            className="px-4 py-3 bg-blue-500 hover:bg-blue-600 text-white rounded-lg text-sm font-medium transition-colors flex items-center gap-2"
          >
            {copied ? <CheckCircle className="w-4 h-4" /> : <Copy className="w-4 h-4" />}
            {copied ? 'Copied' : 'Copy'}
          </button>
        </div>
      </div>

      {/* Referral URL Section */}
      <div className="mb-6">
        <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">Referral Link</label>
        <div className="flex gap-2">
          <div className="flex-1 bg-white dark:bg-gray-800 rounded-lg px-4 py-3 text-sm text-gray-600 dark:text-gray-400 border border-gray-300 dark:border-gray-600 truncate">
            {referralUrl}
          </div>
          <button
            onClick={handleCopyUrl}
            className="px-4 py-3 bg-green-500 hover:bg-green-600 text-white rounded-lg text-sm font-medium transition-colors flex items-center gap-2 whitespace-nowrap"
          >
            <Copy className="w-4 h-4" />
            Copy Link
          </button>
        </div>
      </div>

      {/* Share Button */}
      <button
        onClick={handleShare}
        className="w-full px-4 py-3 bg-purple-500 hover:bg-purple-600 text-white rounded-lg text-sm font-medium transition-colors flex items-center justify-center gap-2 mb-6"
      >
        <Share2 className="w-4 h-4" />
        Share Referral
      </button>

      {/* Credit Balance */}
      <div className="bg-white dark:bg-gray-800 rounded-lg p-4 border border-gray-200 dark:border-gray-700">
        <div className="flex justify-between items-center">
          <div>
            <p className="text-sm text-gray-600 dark:text-gray-400">Referral Credit Balance</p>
            <p className="text-2xl font-bold text-gray-900 dark:text-white">${creditBalance.toFixed(2)}</p>
          </div>
          <div className="text-right">
            <p className="text-sm text-gray-600 dark:text-gray-400">Per Referral</p>
            <p className="text-2xl font-bold text-green-600 dark:text-green-400">$10</p>
          </div>
        </div>
        <p className="text-xs text-gray-500 dark:text-gray-400 mt-3">
          Earn $10 credit for each friend who signs up and verifies their email. Credits can be applied to subscription upgrades.
        </p>
      </div>

      {/* Info Box */}
      <div className="mt-4 p-3 bg-blue-100 dark:bg-blue-900/30 rounded-lg border border-blue-200 dark:border-blue-800">
        <p className="text-sm text-blue-900 dark:text-blue-200">
          💡 Pro Tip: Share your referral link on trading forums and communities to grow your credit balance!
        </p>
      </div>
    </div>
  )
}
