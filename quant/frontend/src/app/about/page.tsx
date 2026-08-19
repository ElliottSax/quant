import { Metadata } from 'next'
import Link from 'next/link'

export const metadata: Metadata = {
  title: 'About | QuantEngines',
  description:
    'QuantEngines builds free quantitative trading tools: charts, screeners, backtesting, options analytics and congressional trading data drawn from public STOCK Act filings.',
}

export default function AboutPage() {
  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-950 via-slate-900 to-slate-950 py-12">
      <div className="container mx-auto px-4">
        <div className="text-center mb-12">
          <h1 className="text-5xl font-bold text-white mb-4">About QuantEngines</h1>
          <p className="text-slate-400 max-w-2xl mx-auto">
            Professional-grade quantitative trading tools, free to use.
          </p>
        </div>

        <div className="max-w-3xl mx-auto space-y-6 text-slate-300 leading-relaxed">
          <section>
            <h2 className="text-2xl font-bold text-white mb-3">What we do</h2>
            <p>
              QuantEngines publishes analytics tools for people who want to test an
              idea before risking money on it. The site is open to read without an
              account, and everything on it is currently free — no tiers, no paywall,
              and no payment is taken anywhere on the site.
            </p>
          </section>

          <section>
            <h2 className="text-2xl font-bold text-white mb-3">The tools</h2>
            <ul className="list-disc pl-5 space-y-2">
              <li>
                <Link href="/backtesting" className="text-blue-400 underline">
                  Backtesting
                </Link>{' '}
                and a{' '}
                <Link href="/backtesting/builder" className="text-blue-400 underline">
                  strategy builder
                </Link>{' '}
                for running rule-based strategies against historical price data.
              </li>
              <li>
                A{' '}
                <Link href="/scanner" className="text-blue-400 underline">
                  stock screener
                </Link>
                ,{' '}
                <Link href="/charts" className="text-blue-400 underline">
                  charts
                </Link>
                , a{' '}
                <Link href="/compare" className="text-blue-400 underline">
                  comparison tool
                </Link>{' '}
                and a{' '}
                <Link href="/network" className="text-blue-400 underline">
                  correlation network
                </Link>
                .
              </li>
              <li>
                An{' '}
                <Link href="/options" className="text-blue-400 underline">
                  options calculator
                </Link>{' '}
                and a library of{' '}
                <Link href="/strategies" className="text-blue-400 underline">
                  pre-built strategies
                </Link>
                .
              </li>
              <li>
                <Link href="/congressional-trades" className="text-blue-400 underline">
                  Congressional trading analytics
                </Link>{' '}
                built from the periodic transaction reports members of Congress file
                publicly under the STOCK Act.
              </li>
            </ul>
          </section>

          <section>
            <h2 className="text-2xl font-bold text-white mb-3">Where the data comes from</h2>
            <p>
              Congressional trading records are derived from public filings published at
              house.gov and senate.gov. Market data comes from third-party providers
              including Polygon. Neither source is perfect: filings are self-reported,
              delayed and stated as ranges rather than exact amounts, and vendor market
              data can be delayed or incomplete. We set out those limits plainly in the{' '}
              <Link href="/disclaimer" className="text-blue-400 underline">
                Disclaimer
              </Link>
              .
            </p>
          </section>

          <section>
            <h2 className="text-2xl font-bold text-white mb-3">How we handle being wrong</h2>
            <p>
              A site that publishes numbers about named public figures will eventually
              publish something incorrect. When that happens we want to hear about it and
              fix it in the open, which is why we keep a{' '}
              <Link href="/corrections-policy" className="text-blue-400 underline">
                Corrections Policy
              </Link>
              . The reasoning behind our strategy results is documented in{' '}
              <Link href="/strategy-validation" className="text-blue-400 underline">
                Validation Methodology
              </Link>{' '}
              and the literature we draw on is listed in{' '}
              <Link href="/research-references" className="text-blue-400 underline">
                Academic References
              </Link>
              .
            </p>
          </section>

          <section>
            <h2 className="text-2xl font-bold text-white mb-3">What we are not</h2>
            <p>
              We are not a broker, a registered investment adviser, or a financial
              planner. We do not manage money, take custody of funds, or execute trades.
              Nothing published here is a recommendation to buy or sell anything.
            </p>
          </section>

          <section>
            <h2 className="text-2xl font-bold text-white mb-3">Get in touch</h2>
            <p>
              Questions, corrections and bug reports are all welcome — see the{' '}
              <Link href="/contact" className="text-blue-400 underline">
                contact page
              </Link>
              .
            </p>
          </section>
        </div>
      </div>
    </div>
  )
}
