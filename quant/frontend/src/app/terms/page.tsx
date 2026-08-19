import { Metadata } from 'next'
import Link from 'next/link'

export const metadata: Metadata = {
  title: 'Terms of Service | QuantEngines',
  description:
    'The terms covering use of QuantEngines: what the service is, what accounts require of you, and the limits of our liability.',
}

export default function TermsPage() {
  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-950 via-slate-900 to-slate-950 py-12">
      <div className="container mx-auto px-4">
        <div className="text-center mb-12">
          <h1 className="text-5xl font-bold text-white mb-4">Terms of Service</h1>
          <p className="text-slate-400">Last updated: August 2026</p>
        </div>

        <div className="max-w-3xl mx-auto space-y-6 text-slate-300 leading-relaxed">
          <section>
            <h2 className="text-2xl font-bold text-white mb-3">1. Agreement</h2>
            <p>
              By using quantengines.com you agree to these terms. If you do not agree,
              please do not use the site.
            </p>
          </section>

          <section>
            <h2 className="text-2xl font-bold text-white mb-3">2. What the service is</h2>
            <p>
              QuantEngines provides research and analytics tools — charts, screeners,
              backtesting, options analytics, and congressional trading data derived
              from public filings. It is an information service. It is not brokerage,
              investment advice, or portfolio management, and we never take custody of
              your money or place trades. This is set out in full in our{' '}
              <Link href="/disclaimer" className="text-blue-400 underline">
                Disclaimer
              </Link>
              , which forms part of these terms.
            </p>
          </section>

          <section>
            <h2 className="text-2xl font-bold text-white mb-3">3. Cost</h2>
            <p>
              The site is currently free to use in full, and no part of it takes
              payment. If we ever introduce paid features we will publish the terms
              covering them before charging anyone; nothing here obliges you to pay for
              anything today.
            </p>
          </section>

          <section>
            <h2 className="text-2xl font-bold text-white mb-3">4. Accounts</h2>
            <p>
              You can read the site without an account. If you create one, give accurate
              details, keep your credentials secure, and do not share the account. You
              are responsible for activity under your account. Tell us at{' '}
              <a href="mailto:hello@quantengines.com" className="text-blue-400 underline">
                hello@quantengines.com
              </a>{' '}
              if you believe it has been compromised, and we can close it on request.
            </p>
          </section>

          <section>
            <h2 className="text-2xl font-bold text-white mb-3">5. Acceptable use</h2>
            <p>You agree not to:</p>
            <ul className="list-disc pl-5 space-y-2 mt-3">
              <li>
                Scrape, crawl, or otherwise extract data at a volume that degrades the
                service for others, or circumvent rate limits.
              </li>
              <li>
                Republish our compiled datasets or analytics wholesale as your own
                product. Quoting figures with attribution and a link is fine.
              </li>
              <li>
                Attempt to break, probe, or gain unauthorised access to the site, its
                APIs, or other users&apos; accounts.
              </li>
              <li>
                Use the site to harass or make unfounded accusations against the public
                officials whose filings we publish.
              </li>
            </ul>
          </section>

          <section>
            <h2 className="text-2xl font-bold text-white mb-3">6. Third-party data</h2>
            <p>
              Some data on this site originates with third parties, including government
              filing systems and market data vendors such as Polygon. Their material
              remains theirs, may be subject to their own terms, and may be delayed,
              incomplete, or wrong. We pass it on in good faith and do not warrant it.
            </p>
          </section>

          <section>
            <h2 className="text-2xl font-bold text-white mb-3">7. Our content</h2>
            <p>
              The site&apos;s design, code, and written material are ours. Public filings
              and other public-record data are not, and we claim no ownership over them.
            </p>
          </section>

          <section>
            <h2 className="text-2xl font-bold text-white mb-3">
              8. No warranty and limitation of liability
            </h2>
            <p>
              The service is provided &quot;as is&quot; and &quot;as available&quot;,
              without warranty of any kind. We do not guarantee it will be accurate,
              uninterrupted, or available at all, and we may change or withdraw features
              at any time. To the fullest extent permitted by law, we are not liable for
              any trading loss, investment loss, lost profit, or other damage arising
              from your use of the site or reliance on anything published on it. Nothing
              in these terms excludes liability that cannot lawfully be excluded.
            </p>
          </section>

          <section>
            <h2 className="text-2xl font-bold text-white mb-3">9. Changes</h2>
            <p>
              We may update these terms. The date at the top will change when we do, and
              continuing to use the site after that means you accept the revised terms.
            </p>
          </section>

          <section>
            <h2 className="text-2xl font-bold text-white mb-3">10. Contact</h2>
            <p>
              Questions about these terms:{' '}
              <a href="mailto:hello@quantengines.com" className="text-blue-400 underline">
                hello@quantengines.com
              </a>
              . Other channels are listed on the{' '}
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
