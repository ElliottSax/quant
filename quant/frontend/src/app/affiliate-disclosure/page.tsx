import { Metadata } from 'next'
import Link from 'next/link'
// `Handshake` does not exist in lucide-react 0.263.1 (added much later). Because
// the app is force-dynamic nothing catches that at build time -- the page compiles
// and then 500s on first request. Only use icons verified against the pinned version.
import { Link2, ShieldCheck, Ban } from 'lucide-react'

export const metadata: Metadata = {
  title: 'Affiliate Disclosure | QuantEngines',
  description:
    'Whether QuantEngines earns commissions from links on this site, what that can and cannot influence, and how paid links are marked.',
}

// Written to be true on the day it ships: the site currently carries no affiliate
// links and earns no commissions. Say so plainly rather than publishing the usual
// "we may earn from purchases" hedge that reads as a live disclosure when it is not.
// When the first live link ships, update the status paragraph in the same commit —
// a disclosure that lags the links it describes is the failure this page exists to
// prevent, and it is the thing affiliate networks check hardest.
export default function AffiliateDisclosurePage() {
  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-950 via-slate-900 to-slate-950 py-12">
      <div className="container mx-auto px-4">
        <div className="text-center mb-12">
          <h1 className="text-5xl font-bold text-white mb-4">Affiliate Disclosure</h1>
          <p className="text-slate-400">Last updated: August 2026</p>
        </div>

        <div className="max-w-3xl mx-auto space-y-8">
          <section className="bg-slate-900/60 border border-blue-500/30 rounded-xl p-6">
            <div className="flex items-start gap-3 mb-3">
              <Link2 className="h-6 w-6 text-blue-400 shrink-0 mt-0.5" />
              <h2 className="text-2xl font-bold text-white">Current status</h2>
            </div>
            <p className="text-slate-300 leading-relaxed">
              As of August 2026, QuantEngines carries <strong>no affiliate links</strong> and
              earns <strong>no commissions</strong> from any broker, data vendor or software
              company. Nothing on this site is a paid placement today. This page exists so
              that the rules are published before any such link appears, not after.
            </p>
          </section>

          <section className="bg-slate-900/60 border border-slate-700 rounded-xl p-6">
            <h2 className="text-2xl font-bold text-white mb-3">If that changes</h2>
            <p className="text-slate-300 leading-relaxed mb-4">
              We may in future earn a commission when a reader signs up with a broker or
              service through a link on this site. If and when that happens:
            </p>
            <ul className="space-y-2 text-slate-300 list-disc pl-5">
              <li>
                The link will be <strong>marked as an affiliate link where it appears</strong>,
                not only described on this page.
              </li>
              <li>
                It costs you nothing extra. Any commission is paid by the company, not added
                to your price.
              </li>
              <li>
                This page will be updated in the same change that ships the link, so the
                disclosure is never behind the site.
              </li>
            </ul>
          </section>

          <section className="bg-slate-900/60 border border-emerald-500/30 rounded-xl p-6">
            <div className="flex items-start gap-3 mb-3">
              <ShieldCheck className="h-6 w-6 text-emerald-400 shrink-0 mt-0.5" />
              <h2 className="text-2xl font-bold text-white">What money cannot influence</h2>
            </div>
            <p className="text-slate-300 leading-relaxed">
              This is the part that matters more than the disclosure itself. Our published
              results — seasonality verdicts, backtests, congressional trading analysis — are
              computed from data by a documented method, and a commercial relationship does not
              and will not change a single one of them. We publish results that are
              inconvenient, including findings that a pattern people believe in does not hold
              up. A commission cannot buy a verdict, a ranking, or a place on a list, and if it
              ever could, the site would be worthless.
            </p>
          </section>

          <section className="bg-slate-900/60 border border-slate-700 rounded-xl p-6">
            <div className="flex items-start gap-3 mb-3">
              <Ban className="h-6 w-6 text-slate-400 shrink-0 mt-0.5" />
              <h2 className="text-2xl font-bold text-white">Still not advice</h2>
            </div>
            <p className="text-slate-300 leading-relaxed">
              A disclosure about commissions does not turn this site into a financial adviser,
              and none of it is a recommendation to buy or sell anything. See the{' '}
              <Link href="/disclaimer" className="text-blue-400 hover:text-blue-300 underline">
                full disclaimer
              </Link>{' '}
              and our{' '}
              <Link href="/terms" className="text-blue-400 hover:text-blue-300 underline">
                terms of service
              </Link>
              .
            </p>
          </section>

          <p className="text-slate-400 text-sm text-center">
            Questions about this policy?{' '}
            <a href="mailto:hello@quantengines.com" className="text-blue-400 hover:text-blue-300 underline">
              hello@quantengines.com
            </a>
          </p>
        </div>
      </div>
    </div>
  )
}
