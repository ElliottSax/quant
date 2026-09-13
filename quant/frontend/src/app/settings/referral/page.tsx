'use client'

import Link from 'next/link'
import { ArrowLeft, Gift } from 'lucide-react'

// This used to fetch /api/v1/subscription/referral/code on load. That endpoint's handler
// (referral.py) is correctly written and correctly mounted in this repo's own
// app/api/v1/__init__.py -- but the backend actually live at
// https://elliottsax-quant-backend.hf.space (production's NEXT_PUBLIC_API_URL) is stale and
// doesn't have it: its real /api/v1/openapi.json (checked 2026-09-13) lists only the plural
// /subscriptions/* routes, not /subscription/referral/*. This repo's only deploy workflow
// (.github/workflows/deploy-production.yml) pushes the backend to Railway, not to that HF
// Space, so nothing here currently redeploys what's actually live -- a real infrastructure
// gap, not a code bug, and not something to paper over by guessing at HF Space credentials.
//
// Also: the referral program as designed promises credit "applied to subscription upgrades" --
// which assumes a paid tier that doesn't exist under the current Open Beta / free-forever
// stance (see settings/subscription/page.tsx). Showing a working-looking referral flow whose
// payoff depends on a tier that may never launch would be its own honesty problem, independent
// of the backend being stale.
//
// Stopgap per Elliott (2026-09-13): put off the backend-redeploy + pricing questions, replace
// the broken fetch-driven page with an honest "not live yet" state -- same treatment already
// used on the subscription page -- rather than show a raw fetch error.
export default function ReferralSettingsPage() {
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
          <h1 className="text-4xl font-bold text-white">Referral Program</h1>
        </div>

        <div className="bg-slate-800/50 rounded-lg p-8 border border-slate-700 max-w-2xl">
          <div className="flex items-start gap-4">
            <div className="p-3 rounded-lg bg-gradient-to-br from-blue-500 to-purple-500 flex-shrink-0">
              <Gift className="w-6 h-6 text-white" />
            </div>
            <div>
              <h2 className="text-2xl font-bold text-white mb-2">Not live yet</h2>
              <p className="text-gray-400 mb-4">
                The referral program isn&apos;t turned on yet. Quant is in open beta with no
                paywalls right now, so there&apos;s no subscription tier for referral credit to
                apply to -- we&apos;d rather wait until that&apos;s settled than show you a
                reward that doesn&apos;t go anywhere.
              </p>
              <p className="text-gray-500 text-sm">
                Want to help in the meantime? Share Quant directly with other traders, or see{' '}
                <Link href="/support" className="text-blue-400 hover:text-blue-300">
                  make a one-time contribution
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
