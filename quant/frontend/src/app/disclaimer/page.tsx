import { Metadata } from 'next'
import Link from 'next/link'
import { AlertTriangle, Scale, Database, TrendingDown } from 'lucide-react'

export const metadata: Metadata = {
  title: 'Disclaimer | QuantEngines',
  description:
    'QuantEngines publishes research and analytics tools, not investment advice. What our data is, where it comes from, and the limits of what it can tell you.',
}

export default function DisclaimerPage() {
  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-950 via-slate-900 to-slate-950 py-12">
      <div className="container mx-auto px-4">
        <div className="text-center mb-12">
          <h1 className="text-5xl font-bold text-white mb-4">
            Disclaimer
          </h1>
          <p className="text-slate-400">Last updated: August 2026</p>
        </div>

        <div className="max-w-3xl mx-auto space-y-8">
          <section className="bg-slate-900/60 border border-amber-500/30 rounded-xl p-6">
            <div className="flex items-start gap-3 mb-3">
              <AlertTriangle className="h-6 w-6 text-amber-400 shrink-0 mt-0.5" />
              <h2 className="text-2xl font-bold text-white">
                This is not investment advice
              </h2>
            </div>
            <p className="text-slate-300 leading-relaxed">
              QuantEngines is a research and analytics site. Everything here —
              screeners, backtests, signals, strategy validation, congressional
              trading analysis — is published for information and education. None
              of it is a recommendation to buy or sell any security, and none of it
              is tailored to your circumstances.
            </p>
            <p className="text-slate-300 leading-relaxed mt-4">
              We are not a registered investment adviser, broker-dealer, or
              financial planner, and no content on this site creates an advisory
              relationship. Before acting on anything you read here, consider
              speaking to a licensed professional who knows your situation.
            </p>
          </section>

          <section className="bg-slate-900/60 border border-slate-700 rounded-xl p-6">
            <div className="flex items-start gap-3 mb-3">
              <TrendingDown className="h-6 w-6 text-blue-400 shrink-0 mt-0.5" />
              <h2 className="text-2xl font-bold text-white">
                Past performance means very little
              </h2>
            </div>
            <p className="text-slate-300 leading-relaxed">
              Backtested and simulated results are hypothetical. They are computed
              with the benefit of hindsight, they do not account for slippage,
              liquidity, taxes, or the emotional reality of holding a losing
              position, and they are not a promise about the future. A strategy that
              tested well can lose money immediately and permanently.
            </p>
            <p className="text-slate-300 leading-relaxed mt-4">
              You can lose some or all of the money you invest. Options and
              derivatives can lose more than you put in. Only risk what you can
              afford to lose entirely.
            </p>
          </section>

          <section className="bg-slate-900/60 border border-slate-700 rounded-xl p-6">
            <div className="flex items-start gap-3 mb-3">
              <Database className="h-6 w-6 text-purple-400 shrink-0 mt-0.5" />
              <h2 className="text-2xl font-bold text-white">
                Where our data comes from, and how it can be wrong
              </h2>
            </div>
            <p className="text-slate-300 leading-relaxed">
              Congressional trading data is derived from public periodic transaction
              reports filed with the House and Senate under the STOCK Act, published
              at house.gov and senate.gov. Market data — prices, quotes and historical
              bars — is retrieved from Yahoo Finance, with automatic fallback to Twelve Data, Alpha Vantage and Finnhub when it is unavailable. It is not a real-time exchange
              feed: quotes are delayed and are best treated as end-of-day.
            </p>
            <ul className="list-disc pl-5 space-y-2 text-slate-300 leading-relaxed mt-4">
              <li>
                Filings are self-reported and are often submitted weeks after the
                trade. What you see here is a record of a disclosure, not a live
                trade feed.
              </li>
              <li>
                Filed amounts are ranges, not exact figures. Any total we show from
                them is an estimate.
              </li>
              <li>
                Filings contain errors, amendments and omissions. We reproduce what
                was filed; we cannot verify that a filing is accurate or complete.
              </li>
              <li>
                Market data is delayed and may be incomplete or incorrect. We do not
                guarantee it, and nothing on this site should be relied on as a live
                or executable price.
              </li>
            </ul>
            <p className="text-slate-300 leading-relaxed mt-4">
              A disclosed trade is not evidence of wrongdoing by anyone named on this
              site. If you believe something here is wrong, tell us — see our{' '}
              <Link href="/corrections-policy" className="text-blue-400 underline">
                Corrections Policy
              </Link>
              .
            </p>
          </section>

          <section className="bg-slate-900/60 border border-slate-700 rounded-xl p-6">
            <div className="flex items-start gap-3 mb-3">
              <Scale className="h-6 w-6 text-emerald-400 shrink-0 mt-0.5" />
              <h2 className="text-2xl font-bold text-white">No warranty</h2>
            </div>
            <p className="text-slate-300 leading-relaxed">
              The site and its tools are provided &quot;as is&quot;, without warranty
              of any kind. We do not guarantee that the site will be available,
              accurate, or uninterrupted. To the fullest extent permitted by law, we
              accept no liability for any loss arising from your use of this site or
              reliance on anything published here.
            </p>
          </section>

          <p className="text-center text-slate-400 text-sm">
            Questions about this disclaimer:{' '}
            <a href="mailto:hello@quantengines.com" className="text-blue-400 underline">
              hello@quantengines.com
            </a>
          </p>
        </div>
      </div>
    </div>
  )
}
