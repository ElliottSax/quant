import { Metadata } from 'next'
import Link from 'next/link'

export const metadata: Metadata = {
  title: 'Privacy Policy | QuantEngines',
  description:
    'What QuantEngines collects: analytics and newsletter subscriptions. What we do not do, and how to have your data removed.',
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
              to see which pages get read, and we store your email address if you
              subscribe to updates. That is the whole of the personal data we hold.
              We do not sell your personal information and we run no advertising
              networks.
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
              lists. Every email we send carries an unsubscribe link and an
              unsubscribe header; both reach{' '}
              <a href="mailto:hello@quantengines.com" className="text-blue-400 underline">
                hello@quantengines.com
              </a>
              , and one message there is enough — we remove the address and confirm
              it. You can ask us to delete it at any time, unsubscribed or not.
            </p>
          </section>

          <section>
            <h2 className="text-2xl font-bold text-white mb-3">Accounts</h2>
            {/* This said "There are no user accounts... we hold no passwords,
                credentials or profile records". That was wrong on every count:
                /auth/login and /auth/register are live and call api.login(), the
                backend hashes passwords with bcrypt (backend/app/core/security.py),
                issues JWTs, and exposes /me, /change-password and 2FA endpoints. A
                privacy policy denying that it holds credentials while the database
                stores hashed passwords is the most consequential thing on this page
                to get wrong. */}
            <p>
              Most of the site is readable without an account. You can also register
              at{' '}
              <Link href="/auth/register" className="text-blue-400 underline">
                /auth/register
              </Link>{' '}
              to use the dashboard and save your work. If you do, we store the email
              address and profile details you give us, and a hashed version of your
              password — hashed with bcrypt, so we cannot read the password itself
              and neither can anyone who obtains the database.
            </p>
            <p className="mt-4">
              Signed-in sessions use JSON Web Tokens issued by our own backend rather
              than a third-party identity provider. If you enable two-factor
              authentication we also store the secret needed to verify your codes.
              You can change your password from your profile, and you can ask us to
              delete your account and everything attached to it at any time.
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
              processing. In practice the only personal data we hold is a subscriber
              email address and first name. Write to{' '}
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
