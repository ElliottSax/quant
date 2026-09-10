/**
 * Open Beta - Free, No Paywall
 *
 * No paywalls. No tiers. No charges. Everything is free to use.
 *
 * RESOLVED 2026-09-10: the prior "free forever" commitment (see git history)
 * is gone -- Elliott's explicit call, in response to running costs not being
 * sustainable as an unconditional permanent promise. The product itself is
 * unchanged: still no paywalls, no tiers, nothing gated. Only the *permanence
 * claim* was removed, replaced with an honest ask for optional support (see
 * "Support This Project" section below, links to /support). The 3-way
 * mismatched checkout API contract (frontend singular /subscription/* vs
 * backend plural /subscriptions/* vs HYBRID_MODEL_SETUP.md) is still
 * unresolved and still out of scope here -- /support uses a standalone
 * Stripe Payment Link, not this broken checkout plumbing, specifically so
 * that reconciling that mess isn't a prerequisite for shipping this.
 */

'use client'

import { Check, Clock, Zap, TrendingUp, ArrowRight } from 'lucide-react'

export default function PricingPage() {
  const features = [
    { name: 'Unlimited Backtests', included: true, description: 'Run as many backtests as you want' },
    { name: 'All 10+ Strategies', included: true, description: 'Access to every professional trading strategy' },
    { name: 'Full Historical Data', included: true, description: '10+ years of real market OHLC data' },
    { name: 'Advanced Analytics', included: true, description: 'Detailed performance metrics and drawdown analysis' },
    // "Portfolio Tracking" was listed here as included. /portfolio is an
    // in-development page carrying robots.index = false, so the feature is off —
    // advertising it, even on a free plan, is a false claim. It goes back on the
    // list when the page ships.
    // `included: false` items are not built yet. They are rendered as "Planned",
    // never with the green tick — a tick beside "coming soon" told visitors a
    // feature was available and unavailable in the same row.
    { name: 'Email Alerts', included: false, description: 'Alerts for strategy signals' },
    { name: 'CSV Export', included: true, description: 'Export backtest results for further analysis' },
    { name: 'API Access', included: false, description: 'Programmatic backtesting' },
    { name: 'Congressional Trading', included: true, description: 'Free access to politician trading analytics' },
  ]

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-950 via-slate-900 to-slate-950">
      {/* Header */}
      <div className="container mx-auto px-4 py-20 text-center">
        <div className="inline-block mb-4 px-4 py-2 bg-green-500/10 rounded-full border border-green-500/20">
          <span className="text-green-400 text-sm font-medium">🎉 Open Beta - Free, No Paywall</span>
        </div>

        <h1 className="text-5xl md:text-6xl font-bold text-white mb-6">
          Professional Backtesting
          <span className="block bg-gradient-to-r from-green-400 to-blue-600 bg-clip-text text-transparent">
            No Cost. No Limits.
          </span>
        </h1>

        <p className="text-xl text-gray-400 max-w-2xl mx-auto mb-8">
          No paywalls, no tiers, no hidden charges. We're building the most accessible quantitative trading
          platform on the internet -- and running it costs real money, so if it's useful to you,{' '}
          <a href="/support" className="text-green-400 hover:underline">optional support</a> keeps it that way.
        </p>

        <div className="flex gap-4 justify-center">
          {/* These buttons pointed at /auth/register, which cannot complete: the page
              calls api.register(), and the frontend client never implemented it. The
              ACCOUNT SYSTEM ITSELF IS REAL — the backend mounts 13 /auth endpoints and
              stores bcrypt password hashes — so this is a half-finished integration, not
              an absent feature, and the privacy policy correctly says accounts exist.
              Until the client is wired up, sending visitors into a form that throws is
              worse than sending them to the tools, which need no account. */}
          <a
            href="/backtesting/builder"
            className="bg-gradient-to-r from-blue-500 to-purple-600 hover:from-blue-600 hover:to-purple-700 text-white font-semibold px-8 py-4 rounded-xl shadow-lg shadow-blue-500/25 inline-flex items-center gap-2 transition-all"
          >
            Start Backtesting Now
            <ArrowRight className="w-5 h-5" />
          </a>
          <a
            href="/backtesting"
            className="border border-slate-600 hover:border-slate-500 text-white font-semibold px-8 py-4 rounded-xl transition-all"
          >
            Try Demo
          </a>
        </div>
      </div>

      {/* Features Grid */}
      <div className="container mx-auto px-4 py-16">
        <h2 className="text-3xl font-bold text-white mb-12 text-center">What You Get</h2>

        <div className="grid md:grid-cols-2 gap-8 max-w-4xl mx-auto">
          {features.map((feature, idx) => (
            <div key={idx} className="flex items-start gap-4 bg-slate-800/30 rounded-xl p-6 border border-slate-700">
              <div
                className={`flex-shrink-0 w-6 h-6 rounded-full flex items-center justify-center mt-1 ${
                  feature.included ? 'bg-green-500/20' : 'bg-slate-600/30'
                }`}
              >
                {feature.included ? (
                  <Check className="w-4 h-4 text-green-400" />
                ) : (
                  <Clock className="w-4 h-4 text-slate-400" />
                )}
              </div>
              <div className="flex-1">
                <h3 className="text-white font-semibold mb-1 flex items-center gap-2">
                  {feature.name}
                  {!feature.included && (
                    <span className="text-[10px] uppercase tracking-wider font-semibold text-slate-400 border border-slate-600 rounded px-1.5 py-0.5">
                      Planned
                    </span>
                  )}
                </h3>
                <p className="text-gray-400 text-sm">{feature.description}</p>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Why Free? */}
      <div className="container mx-auto px-4 py-16 border-t border-slate-800">
        <div className="max-w-3xl mx-auto">
          <h2 className="text-3xl font-bold text-white mb-8 text-center">Why Is Everything Free?</h2>

          <div className="space-y-6">
            <div className="bg-slate-800/30 rounded-xl p-6 border border-slate-700">
              <h3 className="text-lg font-semibold text-white mb-3 flex items-center gap-2">
                <Zap className="w-5 h-5 text-yellow-400" />
                Community First
              </h3>
              <p className="text-gray-400">
                We believe retail traders deserve access to professional-grade tools. We're building in public with the
                community, not against it.
              </p>
            </div>

            <div className="bg-slate-800/30 rounded-xl p-6 border border-slate-700">
              <h3 className="text-lg font-semibold text-white mb-3 flex items-center gap-2">
                <TrendingUp className="w-5 h-5 text-green-400" />
                Sustainable Revenue
              </h3>
              <p className="text-gray-400">
                We earn from optional broker affiliate partnerships. We recommend tools we believe in. Your success
                benefits us too.
              </p>
            </div>

            <div className="bg-slate-800/30 rounded-xl p-6 border border-slate-700">
              <h3 className="text-lg font-semibold text-white mb-3 flex items-center gap-2">
                <Check className="w-5 h-5 text-blue-400" />
                Open Development
              </h3>
              <p className="text-gray-400">
                You can see what we're building, contribute ideas, and help shape the future of the platform. This is
                a public project.
              </p>
            </div>
          </div>
        </div>
      </div>

      {/* Social Proof */}
      <div className="container mx-auto px-4 py-16 border-t border-slate-800">
        <div className="max-w-3xl mx-auto text-center">
          <h2 className="text-3xl font-bold text-white mb-12">What Traders Are Using</h2>

          <div className="grid md:grid-cols-3 gap-6">
            <div className="bg-slate-800/30 rounded-xl p-6 border border-slate-700">
              <div className="text-4xl font-bold text-white mb-2">10+</div>
              <div className="text-gray-400">Professional Strategies</div>
            </div>
            <div className="bg-slate-800/30 rounded-xl p-6 border border-slate-700">
              <div className="text-4xl font-bold text-white mb-2">10K+</div>
              <div className="text-gray-400">Market Data Points</div>
            </div>
            <div className="bg-slate-800/30 rounded-xl p-6 border border-slate-700">
              <div className="text-4xl font-bold text-white mb-2">∞</div>
              <div className="text-gray-400">Backtests (Unlimited)</div>
            </div>
          </div>
        </div>
      </div>

      {/* FAQ */}
      <div className="container mx-auto px-4 py-16 border-t border-slate-800">
        <div className="max-w-3xl mx-auto">
          <h2 className="text-3xl font-bold text-white text-center mb-12">Questions?</h2>

          <div className="space-y-6">
            <div className="bg-slate-800/30 rounded-xl p-6 border border-slate-700">
              <h3 className="text-lg font-semibold text-white mb-2">Will this stay free?</h3>
              <p className="text-gray-400">
                Right now, yes -- no paywalls, no tiers, nothing gated. Running the servers and data feeds behind it
                costs real money though, so "free forever, no matter what" isn't a promise we can honestly make. If
                you find it useful, <a href="/support" className="text-blue-400 hover:underline">optional support</a>{' '}
                is what keeps it free for everyone else too.
              </p>
            </div>

            <div className="bg-slate-800/30 rounded-xl p-6 border border-slate-700">
              <h3 className="text-lg font-semibold text-white mb-2">Is this data real?</h3>
              <p className="text-gray-400">
                100% real market data from Yahoo Finance. Historical OHLC bars with actual trading volumes. No
                synthetic data.
              </p>
            </div>

            <div className="bg-slate-800/30 rounded-xl p-6 border border-slate-700">
              <h3 className="text-lg font-semibold text-white mb-2">How do you make money?</h3>
              <p className="text-gray-400">
                We earn affiliate commissions when you open a trading account through our platform. You never pay extra
                - your broker just gives us a commission.
              </p>
            </div>

            <div className="bg-slate-800/30 rounded-xl p-6 border border-slate-700">
              <h3 className="text-lg font-semibold text-white mb-2">Can I use this commercially?</h3>
              <p className="text-gray-400">
                Yes! You can use the platform for personal trading, bot development, or even commercial applications.
                Check our terms for details.
              </p>
            </div>
          </div>
        </div>
      </div>

      {/* Congress Trading Alerts -- a separate, optional premium add-on. This
          section does not change anything above: the core backtesting suite
          stays free with no paywall. This is a different product (email
          digests for the congress-trades feature), sold alongside it, not a
          reversal of it. */}
      <div className="container mx-auto px-4 py-16 border-t border-slate-800">
        <div className="max-w-3xl mx-auto text-center">
          <div className="inline-block mb-4 px-4 py-2 bg-indigo-500/10 rounded-full border border-indigo-500/20">
            <span className="text-indigo-400 text-sm font-medium">Optional add-on</span>
          </div>
          <h2 className="text-3xl font-bold text-white mb-4">Want a Congress Trade Alert in Your Inbox?</h2>
          <p className="text-gray-400 mb-8">
            The congress-trades browser above is, and stays, free. If you&apos;d rather get an email than check the page,
            Congress Trading Alerts is a separate paid add-on: save filters by ticker, member, or chamber and get a
            digest when something new is disclosed. Free weekly digest available too — no card required.
          </p>
          <a
            href="/congress-alerts"
            className="inline-flex items-center gap-2 bg-slate-800 hover:bg-slate-700 border border-slate-700 text-white font-semibold px-6 py-3 rounded-xl transition-all"
          >
            See Congress Trading Alerts
            <ArrowRight className="w-4 h-4" />
          </a>
        </div>
      </div>

      {/* Support This Project -- a standalone, optional Stripe Payment Link,
          deliberately not the broken /subscription checkout plumbing. See the
          file-header comment for why. */}
      <div className="container mx-auto px-4 py-16 border-t border-slate-800">
        <div className="max-w-3xl mx-auto text-center">
          <div className="inline-block mb-4 px-4 py-2 bg-pink-500/10 rounded-full border border-pink-500/20">
            <span className="text-pink-400 text-sm font-medium">No pressure, no gate</span>
          </div>
          <h2 className="text-3xl font-bold text-white mb-4">Support This Project</h2>
          <p className="text-gray-400 mb-8">
            Servers, market data, and the time to keep this maintained all cost real money. Everything above stays
            free either way -- but if this has saved you time or made you money, a small optional contribution
            helps keep it running and free for the next trader too.
          </p>
          <a
            href="/support"
            className="inline-flex items-center gap-2 bg-pink-600 hover:bg-pink-500 text-white font-semibold px-6 py-3 rounded-xl transition-all"
          >
            Support the Project
            <ArrowRight className="w-4 h-4" />
          </a>
        </div>
      </div>

      {/* Final CTA */}
      <div className="container mx-auto px-4 py-20 border-t border-slate-800">
        <div className="max-w-4xl mx-auto text-center">
          <h2 className="text-4xl font-bold text-white mb-6">Ready?</h2>
          <p className="text-xl text-gray-400 mb-8">
            Join traders building their edge with free, professional-grade backtesting.
          </p>
          <a
            href="/backtesting"
            className="bg-gradient-to-r from-green-500 to-blue-600 hover:from-green-600 hover:to-blue-700 text-white font-semibold px-8 py-4 rounded-xl shadow-lg shadow-green-500/25 inline-flex items-center gap-2 transition-all"
          >
            Start Free Now
            <ArrowRight className="w-5 h-5" />
          </a>
        </div>
      </div>
    </div>
  )
}
