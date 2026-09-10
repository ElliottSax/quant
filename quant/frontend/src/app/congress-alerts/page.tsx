import type { Metadata } from 'next'
import Link from 'next/link'
import { CongressAlertsSignupForm } from './CongressAlertsSignupForm'
import { PRO_PRICE_MONTHLY_USD, PRO_PRICE_YEARLY_USD } from '@/lib/congress-alerts'

const url = 'https://quantengines.com/congress-alerts'
const title = 'Congress Trading Alerts'

export const metadata: Metadata = {
  title: `${title} — Get Notified of New STOCK Act Disclosures | QuantEngines`,
  description:
    'Save filters by ticker, member, or chamber and get an email digest when Congress discloses a new stock trade. Free weekly digest, or $9/mo for daily alerts with full filters. Same-day-to-next-day freshness — not real-time, honestly.',
  keywords: [
    'congress trading alerts',
    'congressional stock trade alerts',
    'stock act disclosure alerts',
    'politician trading notifications',
    'congress trade email digest',
  ],
  alternates: { canonical: url },
  openGraph: {
    title,
    description: 'Email alerts when Congress discloses a new stock trade — filter by ticker, member, or chamber.',
    type: 'website',
    url,
    images: [{ url: `https://quantengines.com/api/og?${new URLSearchParams({ title }).toString()}`, width: 1200, height: 630 }],
  },
}

const schema = {
  '@context': 'https://schema.org',
  '@type': 'Product',
  name: 'QuantEngines Congress Trading Alerts',
  description: 'Email digest alerts for new U.S. Congress STOCK Act stock trade disclosures, filterable by ticker, member, and chamber.',
  brand: { '@type': 'Organization', name: 'QuantEngines' },
  offers: [
    { '@type': 'Offer', name: 'Free', price: '0', priceCurrency: 'USD' },
    { '@type': 'Offer', name: 'Pro Monthly', price: String(PRO_PRICE_MONTHLY_USD), priceCurrency: 'USD' },
    { '@type': 'Offer', name: 'Pro Yearly', price: String(PRO_PRICE_YEARLY_USD), priceCurrency: 'USD' },
  ],
}

export default function CongressAlertsPage() {
  return (
    <div className="container mx-auto px-4 py-12">
      <script type="application/ld+json" dangerouslySetInnerHTML={{ __html: JSON.stringify(schema) }} />

      <div className="max-w-3xl mb-4">
        <nav className="text-sm text-slate-500 mb-4">
          <Link href="/congress-stock-trades" className="hover:text-slate-300">Congress Trades</Link> / <span className="text-slate-300">Alerts</span>
        </nav>
        <div className="inline-flex items-center gap-2 mb-4 px-3 py-1 rounded-full border border-[hsl(45,96%,58%)]/30 bg-[hsl(45,96%,58%)]/10">
          <span className="text-xs font-semibold text-[hsl(45,96%,58%)] uppercase tracking-wide">Premium add-on</span>
        </div>
        <h1 className="text-4xl md:text-5xl font-bold text-white mb-3">{title}</h1>
        <p className="text-lg text-slate-400">
          The free <Link href="/congress-stock-trades" className="text-indigo-400 hover:underline">congress trades browser</Link> and{' '}
          <Link href="/backtesting" className="text-indigo-400 hover:underline">backtesting tool</Link> stay free with no paywall -- this is a
          separate, optional product for people who&apos;d rather get an email than check the page. Save filters once, get a digest
          when something new matching them is disclosed.
        </p>
      </div>

      <div className="max-w-3xl rounded-lg border border-[hsl(215,40%,18%)] bg-[hsl(220,55%,7%)] p-4 mb-10 text-sm text-slate-400">
        <strong className="text-slate-300">Honest freshness:</strong> disclosures reach this feed same-day to next-day after a
        member files with Financial Modeling Prep&apos;s data (the same source the free browser uses). Members themselves have up to{' '}
        <strong className="text-slate-300">45 days</strong> to file after a trade under the STOCK Act — no alerts product, ours
        included, can see a trade before it&apos;s disclosed. See the{' '}
        <Link href="/congress-stock-trades/late-filers" className="text-indigo-400 hover:underline">late-filers tracker</Link> for how
        often that 45-day window itself gets stretched.
      </div>

      <div className="grid lg:grid-cols-5 gap-8 max-w-5xl">
        <div className="lg:col-span-2 space-y-4">
          <div className="rounded-xl border border-[hsl(215,40%,18%)] bg-[hsl(220,55%,9%)] p-5">
            <h2 className="text-lg font-bold text-white mb-1">Free</h2>
            <p className="text-2xl font-bold text-white mb-3">$0</p>
            <ul className="space-y-2 text-sm text-slate-300">
              <li>✓ Weekly digest</li>
              <li>✓ 1 saved filter, or unfiltered (everything)</li>
              <li>✓ Email delivery</li>
            </ul>
          </div>
          <div className="rounded-xl border border-[hsl(45,96%,58%)]/40 bg-[hsl(45,96%,58%)]/5 p-5">
            <h2 className="text-lg font-bold text-white mb-1">Pro</h2>
            <p className="text-2xl font-bold text-white mb-3">
              ${PRO_PRICE_MONTHLY_USD}<span className="text-sm font-normal text-slate-400">/mo</span>{' '}
              <span className="text-sm font-normal text-slate-500">or ${PRO_PRICE_YEARLY_USD}/yr</span>
            </p>
            <ul className="space-y-2 text-sm text-slate-300">
              <li>✓ Daily digest</li>
              <li>✓ Up to 25 saved filters (ticker, member, chamber)</li>
              <li>✓ Everything in Free</li>
              <li>✓ Cancel any time, self-serve</li>
            </ul>
            <p className="text-xs text-slate-500 mt-3">
              For comparison: Quiver Quantitative Premium runs ~$25–30/mo, and Unusual Whales&apos; cheapest tier with congress alerts
              is $50/mo bundled into an unrelated options-flow product. This is congress alerts only.
            </p>
          </div>
        </div>

        <div className="lg:col-span-3">
          <CongressAlertsSignupForm />
        </div>
      </div>

      <div className="max-w-3xl mt-16 space-y-6">
        <h2 className="text-2xl font-bold text-white">Questions</h2>
        <div className="space-y-4 text-sm">
          <div>
            <h3 className="font-semibold text-white mb-1">Is this real-time?</h3>
            <p className="text-slate-400">
              No — see the freshness note above. It&apos;s the fastest this data honestly gets: same-day to next-day after a member
              files, which is already faster than checking a leaderboard page manually every day.
            </p>
          </div>
          <div>
            <h3 className="font-semibold text-white mb-1">Does this replace the free backtesting tool?</h3>
            <p className="text-slate-400">
              No. Backtesting, the strategy library, and the congress-trades browser stay free, no paywall. This is a
              separate, optional product for people who want a push instead of a pull.
            </p>
          </div>
          <div>
            <h3 className="font-semibold text-white mb-1">Can I change my filters or cancel later?</h3>
            <p className="text-slate-400">
              Yes — every digest includes a manage link. No account or password needed.
            </p>
          </div>
        </div>
      </div>
    </div>
  )
}
