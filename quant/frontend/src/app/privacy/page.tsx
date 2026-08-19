import { Metadata } from 'next'
import Link from 'next/link'

export const metadata: Metadata = {
  title: 'Privacy Policy | QuantEngines',
  description:
    'What QuantEngines collects: analytics, newsletter subscriptions and account data. What we do not do, and how to have your data removed.',
}

export default function PrivacyPolicyPage() {
  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-950 via-slate-900 to-slate-950 py-12">
      <div className="container mx-auto px-4">
        <div className="text-center mb-12">
          <h1 className="text-5xl font-bold text-white mb-4">Privacy Policy</h1>
          <p className="text-slate-400">Last updated: August 2026</p>
        </div>

        <div className="max-w-3xl mx-auto space-y-6 text-slate-300 leading-relaxed">
          <section>
            <h2 className="text-2xl font-bold text-white mb-3">The short version</h2>
            <p>
              QuantEngines is a research and analytics site. We use Google Analytics
              to see which pages get read, we store your email address if you
              subscribe to updates, and we store account details if you create an
              account. We do not sell your personal information and we run no
              advertising networks.
            </p>
          </section>

          <section>
            <h2 className="text-2xl font-bold text-white mb-3">Analytics</h2>
            <p>
              We use Google Analytics, which sets cookies and records the pages you
              visit, approximate location derived from your IP address, browser and
              device type, and the site or search that referred you. Google processes
              this on our behalf — see{' '}
              <a
                href="https://policies.google.com/privacy"
                target="_blank"
                rel="noopener noreferrer"
                className="text-blue-400 underline"
              >
                Google&apos;s Privacy Policy
              </a>
              . You can opt out with Google&apos;s{' '}
              <a
                href="https://tools.google.com/dlpage/gaoptout"
                target="_blank"
                rel="noopener noreferrer"
                className="text-blue-400 underline"
              >
                browser add-on
              </a>{' '}
              or by blocking cookies. The site works either way.
            </p>
          </section>

          <section>
            <h2 className="text-2xl font-bold text-white mb-3">Email updates</h2>
            <p>
              If you subscribe, we store the email address and first name you give
              us so we can send you updates. Delivery is handled by Resend, which
              processes the address on our behalf. We do not sell or rent subscriber
              lists. Every email includes an unsubscribe link, and you can ask us to
              delete your address at any time.
            </p>
          </section>

          <section>
            <h2 className="text-2xl font-bold text-white mb-3">Accounts</h2>
            <p>
              Most of the site is readable without an account. If you register, sign-in
              is handled by Supabase, which stores the credentials and profile details
              you provide to it. We do not store your password. Any watchlist or
              settings you save are held against your account so we can show them back
              to you.
            </p>
          </section>

          <section>
            <h2 className="text-2xl font-bold text-white mb-3">
              The congressional trading data
            </h2>
            <p>
              The trading records on this site concern public officials and come from
              disclosures those officials filed publicly under the STOCK Act. That is
              public record, not information collected from you, and it is not covered
              by this policy. What we can and cannot vouch for in that data is set out
              in our{' '}
              <Link href="/disclaimer" className="text-blue-400 underline">
                Disclaimer
              </Link>
              .
            </p>
          </section>

          <section>
            <h2 className="text-2xl font-bold text-white mb-3">What we never do</h2>
            <ul className="list-disc pl-5 space-y-2">
              <li>We do not sell or rent your personal information.</li>
              <li>We do not run third-party advertising or behavioural ad trackers.</li>
              <li>
                We do not knowingly collect information from children under 13. If you
                believe a child has given us information, tell us and we will delete
                it.
              </li>
            </ul>
          </section>

          <section>
            <h2 className="text-2xl font-bold text-white mb-3">Your rights</h2>
            <p>
              Depending on where you live — including under the UK GDPR, EU GDPR and
              the CCPA — you may have the right to ask what personal data we hold about
              you, to have it corrected or deleted, and to object to certain
              processing. In practice the personal data we hold is a subscriber email
              address and, if you registered, your account details. Write to{' '}
              <a href="mailto:hello@quantengines.com" className="text-blue-400 underline">
                hello@quantengines.com
              </a>{' '}
              and we will act on it.
            </p>
          </section>

          <section>
            <h2 className="text-2xl font-bold text-white mb-3">Changes</h2>
            <p>
              If we change what we collect or how we use it, we will update this page
              and the date at the top. Material changes will be described here rather
              than made quietly.
            </p>
          </section>
        </div>
      </div>
    </div>
  )
}
