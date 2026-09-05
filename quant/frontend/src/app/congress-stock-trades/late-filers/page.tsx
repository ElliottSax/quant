import type { Metadata } from 'next'
import Link from 'next/link'
import { getCongressTrades, memberSlug, type Trade } from '@/lib/congress-trades'

// Daily ISR — same cadence as the rest of the congress-stock-trades section.
export const revalidate = 86400

const url = 'https://quantengines.com/congress-stock-trades/late-filers'
const title = "Congress's Slowest Stock-Trade Filers"

// The STOCK Act (2012) requires members of Congress to publicly disclose a
// stock transaction within 45 days of the trade. This page measures, using
// the same disclosure data already powering the rest of this section, how
// many calendar days actually elapsed between the transaction date and the
// disclosure date on file.
const DEADLINE_DAYS = 45

export const metadata: Metadata = {
  title: `${title} — STOCK Act Disclosure Delays | QuantEngines`,
  description:
    'Which members of Congress take the longest to disclose their stock trades? A STOCK Act compliance check built from official House & Senate disclosure dates — the 45-day filing deadline, and who blows past it.',
  keywords: [
    'stock act violations',
    'congress late stock trade disclosure',
    'congress stock trade filing deadline',
    'congressional trading compliance',
    'senate stock trades late filing',
  ],
  alternates: { canonical: url },
  openGraph: {
    title,
    description: 'Who takes the longest to disclose their stock trades? A STOCK Act 45-day filing-deadline check.',
    type: 'website',
    url,
    images: [{ url: `https://quantengines.com/api/og?${new URLSearchParams({ title }).toString()}`, width: 1200, height: 630 }],
  },
}

interface MemberStats {
  name: string
  chamber: string
  totalTrades: number
  lateTrades: number
  maxDays: number
  avgDaysLate: number
}

function ChamberTag({ c }: { c: string }) {
  return <span className={`text-xs ${c === 'Senate' ? 'text-sky-400' : 'text-violet-400'}`}>{c}</span>
}

export default async function LateFilersPage() {
  const data = await getCongressTrades()

  if (!data || data.trades.length === 0) {
    return (
      <div className="container mx-auto px-4 py-16 text-center text-slate-400">
        <h1 className="text-3xl font-bold text-white mb-3">{title}</h1>
        <p>The trade data source is temporarily unavailable. Please check back shortly.</p>
      </div>
    )
  }

  // Only trades where both the transaction date and disclosure date parsed
  // cleanly are usable for a timeliness measurement.
  const timed: (Trade & { daysToDisclose: number })[] = data.trades.filter(
    (t): t is Trade & { daysToDisclose: number } => t.daysToDisclose !== null
  )
  const lateTrades = timed.filter((t) => t.daysToDisclose > DEADLINE_DAYS)

  const memberMap = new Map<string, MemberStats>()
  for (const t of timed) {
    const s = memberMap.get(t.member) || { name: t.member, chamber: t.chamber, totalTrades: 0, lateTrades: 0, maxDays: 0, avgDaysLate: 0 }
    s.totalTrades++
    if (t.daysToDisclose > DEADLINE_DAYS) {
      s.lateTrades++
      s.maxDays = Math.max(s.maxDays, t.daysToDisclose)
      // Accumulate days *past* the deadline (not total days-to-disclose) so
      // the average below reads directly as "how late, on average."
      s.avgDaysLate += t.daysToDisclose - DEADLINE_DAYS
    }
    memberMap.set(t.member, s)
  }
  const leaderboard = Array.from(memberMap.values())
    .filter((s) => s.lateTrades > 0)
    .map((s) => ({ ...s, avgDaysLate: Math.round(s.avgDaysLate / s.lateTrades) }))
    .sort((a, b) => b.lateTrades - a.lateTrades || b.maxDays - a.maxDays)
    .slice(0, 15)

  const worstTrades = [...lateTrades].sort((a, b) => b.daysToDisclose - a.daysToDisclose).slice(0, 10)

  const pctLate = timed.length ? Math.round((lateTrades.length / timed.length) * 1000) / 10 : 0
  const avgDaysOverall = timed.length ? Math.round(timed.reduce((s, t) => s + t.daysToDisclose, 0) / timed.length) : 0

  const shareText = [
    `Congress's slowest stock-trade filers (STOCK Act requires disclosure within ${DEADLINE_DAYS} days):`,
    '',
    ...leaderboard.slice(0, 8).map((m, i) => `${i + 1}. ${m.name} (${m.chamber}) — ${m.lateTrades} trade${m.lateTrades === 1 ? '' : 's'} filed late, worst was ${m.maxDays} days`),
    '',
    `${pctLate}% of trades in the current disclosure window (${timed.length} trades with usable dates) were filed after the ${DEADLINE_DAYS}-day deadline.`,
    '',
    'Source: official STOCK Act disclosures. Full breakdown: quantengines.com/congress-stock-trades/late-filers',
  ].join('\n')

  const schema = {
    '@context': 'https://schema.org',
    '@type': 'Dataset',
    name: "Congress Stock Trade Disclosure Timeliness (STOCK Act)",
    description:
      'Calendar days between transaction date and disclosure date for recent U.S. House and Senate stock trades, measured against the STOCK Act 45-day filing deadline.',
    url,
    creator: { '@type': 'Organization', name: 'QuantEngines' },
    isAccessibleForFree: true,
  }

  return (
    <div className="container mx-auto px-4 py-12">
      <script type="application/ld+json" dangerouslySetInnerHTML={{ __html: JSON.stringify(schema) }} />

      <div className="max-w-3xl mb-8">
        <nav className="text-sm text-slate-500 mb-4">
          <Link href="/congress-stock-trades" className="hover:text-slate-300">Congress Trades</Link> / <span className="text-slate-300">Late Filers</span>
        </nav>
        <h1 className="text-4xl md:text-5xl font-bold text-white mb-3">{title}</h1>
        <p className="text-lg text-slate-400">
          The STOCK Act requires members of Congress to publicly disclose a stock transaction within{' '}
          <strong className="text-white">{DEADLINE_DAYS} days</strong>. Using the transaction and disclosure
          dates on file for trades currently in this tracker, here&apos;s who&apos;s cutting it closest — and who&apos;s
          well past it.
        </p>
      </div>

      <div className="grid gap-4 sm:grid-cols-3 mb-10 max-w-2xl">
        <div className="rounded-lg border border-[hsl(215,40%,18%)] bg-[hsl(220,55%,9%)] p-4 text-center">
          <p className="text-2xl font-bold text-white">{timed.length}</p>
          <p className="text-xs text-slate-500">Trades with usable dates</p>
        </div>
        <div className="rounded-lg border border-[hsl(215,40%,18%)] bg-[hsl(220,55%,9%)] p-4 text-center">
          <p className="text-2xl font-bold text-amber-400">{pctLate}%</p>
          <p className="text-xs text-slate-500">Filed after {DEADLINE_DAYS} days</p>
        </div>
        <div className="rounded-lg border border-[hsl(215,40%,18%)] bg-[hsl(220,55%,9%)] p-4 text-center">
          <p className="text-2xl font-bold text-white">{avgDaysOverall}</p>
          <p className="text-xs text-slate-500">Avg. days to disclose</p>
        </div>
      </div>

      {leaderboard.length > 0 && (
        <>
          <h2 className="text-2xl font-bold text-white mb-4">Members With the Most Late Filings</h2>
          <div className="overflow-x-auto rounded-lg border border-[hsl(215,40%,18%)] mb-4">
            <table className="w-full text-sm">
              <thead>
                <tr className="text-left text-slate-500 border-b border-[hsl(215,40%,18%)]">
                  <th className="py-2 px-4">Member</th>
                  <th className="py-2 px-4">Late trades</th>
                  <th className="py-2 px-4">Avg. days late</th>
                  <th className="py-2 px-4">Worst filing</th>
                </tr>
              </thead>
              <tbody>
                {leaderboard.map((m) => (
                  <tr key={m.name} className="border-b border-[hsl(215,40%,14%)]">
                    <td className="py-2.5 px-4">
                      <Link href={`/congress-stock-trades/member/${memberSlug(m.name)}`} className="text-white hover:text-indigo-400 hover:underline">{m.name}</Link>{' '}
                      <ChamberTag c={m.chamber} />
                    </td>
                    <td className="py-2.5 px-4 text-slate-300">{m.lateTrades} of {m.totalTrades}</td>
                    <td className="py-2.5 px-4 text-slate-300">{m.avgDaysLate} days past deadline</td>
                    <td className="py-2.5 px-4 text-red-400 font-medium">{m.maxDays} days</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
          <p className="text-xs text-slate-500 mb-12">
            &quot;Days past deadline&quot; counts only the overage past the {DEADLINE_DAYS}-day window (i.e. a trade disclosed 50 days after the transaction counts as 5 days late).
          </p>
        </>
      )}

      {worstTrades.length > 0 && (
        <>
          <h2 className="text-2xl font-bold text-white mb-4">Slowest Individual Filings</h2>
          <div className="overflow-x-auto rounded-lg border border-[hsl(215,40%,18%)] mb-12">
            <table className="w-full text-sm">
              <thead>
                <tr className="text-left text-slate-500 border-b border-[hsl(215,40%,18%)]">
                  <th className="py-2 px-4">Member</th>
                  <th className="py-2 px-4">Stock</th>
                  <th className="py-2 px-4">Transaction date</th>
                  <th className="py-2 px-4">Disclosed</th>
                  <th className="py-2 px-4">Days to disclose</th>
                </tr>
              </thead>
              <tbody>
                {worstTrades.map((t, i) => (
                  <tr key={i} className="border-b border-[hsl(215,40%,14%)]">
                    <td className="py-2.5 px-4"><Link href={`/congress-stock-trades/member/${memberSlug(t.member)}`} className="text-white hover:text-indigo-400 hover:underline">{t.member}</Link> <ChamberTag c={t.chamber} /></td>
                    <td className="py-2.5 px-4"><Link href={`/congress-stock-trades/${t.ticker.toUpperCase()}`} className="font-semibold text-indigo-400 hover:underline">{t.ticker}</Link></td>
                    <td className="py-2.5 px-4 text-slate-400 whitespace-nowrap">{t.transactionDate}</td>
                    <td className="py-2.5 px-4 text-slate-400 whitespace-nowrap">{t.disclosureDate}</td>
                    <td className="py-2.5 px-4 font-bold text-red-400">{t.daysToDisclose} days</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </>
      )}

      <div className="rounded-xl border border-[hsl(215,40%,18%)] bg-[hsl(220,55%,7%)] p-5 mb-8 max-w-3xl">
        <h2 className="text-lg font-bold text-white mb-2">Share this</h2>
        <p className="text-sm text-slate-400 mb-3">Copy &amp; paste for Reddit, X, or a newsletter:</p>
        <pre className="whitespace-pre-wrap text-sm text-slate-300 bg-[hsl(220,55%,5%)] rounded-lg p-4 overflow-x-auto select-all">{shareText}</pre>
      </div>

      <div className="max-w-3xl text-sm text-slate-500 space-y-2">
        <p className="font-semibold text-slate-400">How this is measured, and its limits:</p>
        <ul className="list-disc pl-5 space-y-1">
          <li>&quot;Days to disclose&quot; is the calendar-day gap between the transaction date and disclosure date on each official filing — not a legal determination of a STOCK Act violation. Members can receive extensions, and some delays reflect amended or corrected filings rather than late originals.</li>
          <li>This reflects only the trades currently in this tracker&apos;s rolling recent-disclosures window ({timed.length} trades with usable dates as of {data.lastUpdated}), not each member&apos;s full career filing history.</li>
          <li>Trades with missing or malformed dates in the underlying filing are excluded rather than guessed at.</li>
        </ul>
        <p className="pt-2">
          Source: official U.S. House &amp; Senate financial disclosures (STOCK Act), via Financial Modeling Prep. See{' '}
          <Link href="/congress-stock-trades" className="text-indigo-400 hover:underline">all recent congressional trades</Link>.
        </p>
      </div>
    </div>
  )
}
