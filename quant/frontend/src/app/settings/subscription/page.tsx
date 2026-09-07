'use client'

import Link from 'next/link'
import { ArrowLeft, Sparkles } from 'lucide-react'

// This used to call /api/v1/subscription/status, /start-trial, and /downgrade
// -- all handlers in the never-mounted app/api/v1/subscription.py (see this
// repo's CLAUDE.md), so every load 404'd in production. Those tier/upgrade/
// downgrade/trial endpoints stayed unmounted on purpose: quant's pricing page
// commits to "Open Beta - Free Forever / No paywalls", so there is no tier to
// manage or bill. Replaced the broken dashboard with what's actually true,
// rather than fixing calls to a feature that shouldn't exist. The backend's
// dead subscription.py/subscription_deps.py aren't touched here -- quota
// logic elsewhere in the backend still depends on adjacent service code, and
// untangling that is a separate task, not a UI fix.
export default function SubscriptionSettingsPage() {
  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-950 to-slate-900">
      <div className="container mx-auto px-4 py-8">
        <div className="flex items-center gap-4 mb-8">
          <Link
            href="/settings"
            className="p-2 hover:bg-slate-800 rounded-lg transition-colors"
          >
            <ArrowLeft className="w-6 h-6 text-gray-400" />
          </Link>
          <h1 className="text-4xl font-bold text-white">Plan</h1>
        </div>

        <div className="bg-slate-800/50 rounded-lg p-8 border border-slate-700 max-w-2xl">
          <div className="flex items-start gap-4">
            <div className="p-3 rounded-lg bg-gradient-to-br from-blue-500 to-cyan-500 flex-shrink-0">
              <Sparkles className="w-6 h-6 text-white" />
            </div>
            <div>
              <h2 className="text-2xl font-bold text-white mb-2">Free forever</h2>
              <p className="text-gray-400 mb-4">
                Quant is in open beta with no paywalls -- every feature is free while we
                build. There's no tier to manage and nothing to bill.
              </p>
              <p className="text-gray-500 text-sm">
                Want to help support future work? See the{' '}
                <Link href="/settings/referral" className="text-blue-400 hover:text-blue-300">
                  Referral Program
                </Link>
                .
              </p>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}
