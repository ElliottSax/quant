'use client'

import { Heart, Server, Database, ArrowRight, ArrowLeft } from 'lucide-react'

// Standalone Stripe Payment Link, set via env var so it can be swapped
// without a redeploy-requiring code change. Deliberately NOT routed through
// the existing /subscription checkout plumbing (frontend calls singular
// /subscription/*, backend router is plural /subscriptions/* -- a real,
// still-unresolved mismatch). A support/donate flow doesn't need to touch
// that at all: it's a one-off optional payment, not a gated feature.
const DONATE_LINK = process.env.NEXT_PUBLIC_DONATE_LINK || ''

export default function SupportPage() {
  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-950 via-slate-900 to-slate-950">
      <div className="container mx-auto px-4 py-20 text-center">
        <a href="/pricing" className="inline-flex items-center gap-2 text-slate-500 hover:text-slate-300 text-sm mb-8 transition-colors">
          <ArrowLeft className="w-4 h-4" />
          Back to Pricing
        </a>

        <div className="inline-block mb-4 px-4 py-2 bg-pink-500/10 rounded-full border border-pink-500/20">
          <span className="text-pink-400 text-sm font-medium">Optional -- nothing here is gated</span>
        </div>

        <h1 className="text-5xl md:text-6xl font-bold text-white mb-6">
          Help Keep This
          <span className="block bg-gradient-to-r from-pink-400 to-purple-500 bg-clip-text text-transparent">
            Free For Everyone
          </span>
        </h1>

        <p className="text-xl text-gray-400 max-w-2xl mx-auto mb-10">
          Backtesting, the congress-trades browser, charts, and the scanner are free to use and stay that way
          whether or not you support this. But running it isn&apos;t free on our end -- if it&apos;s been useful to
          you, a small optional contribution helps cover real costs and keeps it free for the next trader too.
        </p>

        {DONATE_LINK ? (
          <a
            href={DONATE_LINK}
            target="_blank"
            rel="noopener noreferrer"
            className="inline-flex items-center gap-2 bg-gradient-to-r from-pink-500 to-purple-600 hover:from-pink-600 hover:to-purple-700 text-white font-semibold px-8 py-4 rounded-xl shadow-lg shadow-pink-500/25 transition-all"
          >
            <Heart className="w-5 h-5" />
            Support the Project
          </a>
        ) : (
          <div className="max-w-md mx-auto rounded-xl border border-slate-700 bg-slate-800/40 p-6 text-left text-sm text-gray-400">
            Donate link isn&apos;t configured yet -- set <code className="text-pink-400">NEXT_PUBLIC_DONATE_LINK</code>{' '}
            to a real Stripe Payment Link URL (Stripe Dashboard &rarr; Payment Links &rarr; New, &ldquo;customer
            chooses amount&rdquo;) in Vercel&apos;s project environment variables.
          </div>
        )}
      </div>

      {/* Where the money goes */}
      <div className="container mx-auto px-4 py-16 border-t border-slate-800">
        <div className="max-w-3xl mx-auto">
          <h2 className="text-3xl font-bold text-white mb-8 text-center">Where This Actually Goes</h2>

          <div className="space-y-6">
            <div className="bg-slate-800/30 rounded-xl p-6 border border-slate-700">
              <h3 className="text-lg font-semibold text-white mb-3 flex items-center gap-2">
                <Server className="w-5 h-5 text-blue-400" />
                Hosting &amp; Compute
              </h3>
              <p className="text-gray-400">
                Running backtests, serving charts, and keeping the site fast for everyone costs real server bills
                every month, not a one-time setup fee.
              </p>
            </div>

            <div className="bg-slate-800/30 rounded-xl p-6 border border-slate-700">
              <h3 className="text-lg font-semibold text-white mb-3 flex items-center gap-2">
                <Database className="w-5 h-5 text-green-400" />
                Market &amp; Congressional Data
              </h3>
              <p className="text-gray-400">
                Real historical OHLC data and congressional trade disclosures come from paid data providers, not
                free scrapes -- that's part of why the numbers here are trustworthy instead of synthetic.
              </p>
            </div>

            <div className="bg-slate-800/30 rounded-xl p-6 border border-slate-700">
              <h3 className="text-lg font-semibold text-white mb-3 flex items-center gap-2">
                <Heart className="w-5 h-5 text-pink-400" />
                Keeping It Free, No Paywall
              </h3>
              <p className="text-gray-400">
                Optional support from people who find this useful is what lets everyone else keep using it without
                a paywall -- not ads, not selling your data, not a "free tier" designed to push you into upgrading.
              </p>
            </div>
          </div>
        </div>
      </div>

      {/* Other ways to help */}
      <div className="container mx-auto px-4 py-16 border-t border-slate-800">
        <div className="max-w-3xl mx-auto text-center">
          <h2 className="text-2xl font-bold text-white mb-4">Not Ready to Contribute? That&apos;s Fine.</h2>
          <p className="text-gray-400 mb-8">
            Using a broker link from our recommendations, or just sharing a tool you found useful with another
            trader, helps just as much and costs you nothing.
          </p>
          <a
            href="/pricing"
            className="inline-flex items-center gap-2 border border-slate-600 hover:border-slate-500 text-white font-semibold px-6 py-3 rounded-xl transition-all"
          >
            Back to Pricing
            <ArrowRight className="w-4 h-4" />
          </a>
        </div>
      </div>
    </div>
  )
}
