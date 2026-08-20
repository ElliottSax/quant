/**
 * Treasury yield curve and the measured record of every inversion since 1990.
 *
 * The commodity version of this page is a chart of today's curve. What is not commonly
 * published is the computed episode record — start, end, duration and deepest point of
 * every inversion — derived from the daily series rather than recalled. Inversion dates
 * are widely repeated and widely wrong.
 *
 * Artefact: `python -m pipeline.treasury_curve`. Treasury data is a US government work,
 * so unlike the equity price APIs this can be republished here without a licence problem.
 */

import type { Metadata } from 'next'
import Link from 'next/link'
import { CurveChart, SpreadChart, type Tenor } from './CurveChart'

const url = 'https://quantengines.com/yield-curve'

interface Episode {
  start: string
  end: string
  trading_days: number
  calendar_days: number
  deepest_bp: number
  deepest_on: string
}

interface Spread {
  label: string
  observations: number
  first: string
  last: string
  current_bp: number
  inverted_now: boolean
  days_inverted: number
  sustained_episodes: Episode[]
  brief_episodes_count: number
  brief_episodes_days: number
}

interface Artifact {
  generated_at: string
  source: { name: string; url: string; licence: string; note: string }
  coverage: { first_date: string; last_date: string; observations: number }
  method: { episode_definition: string; min_episode_calendar_days: number; no_interpolation: string }
  latest: { date: string; curve: Tenor[] }
  spreads: Record<string, Spread>
  history: Array<[string, number | null, number | null]>
}

function load(): Artifact | null {
  try {
    // eslint-disable-next-line @typescript-eslint/no-var-requires
    const d = require('../../../public/data/treasury-curve.json') as Artifact
    return d?.latest?.curve?.length ? d : null
  } catch {
    return null
  }
}

const data = load()
const s2 = data?.spreads?.['10y2y']

export const metadata: Metadata = {
  title: s2
    ? `Is the Yield Curve Inverted? 10Y-2Y is ${s2.current_bp >= 0 ? '+' : ''}${s2.current_bp}bp | QuantEngines`
    : 'Treasury Yield Curve & Inversion History | QuantEngines',
  description: s2
    ? `The 10-year minus 2-year Treasury spread is ${s2.current_bp >= 0 ? '+' : ''}${s2.current_bp} basis points as of ${data!.latest.date} — ${s2.inverted_now ? 'inverted' : 'not inverted'}. Plus every sustained inversion since 1990 with its start, end, duration and deepest point, computed from Treasury's daily series.`
    : 'US Treasury par yield curve and the measured record of every inversion since 1990.',
  keywords: [
    'is the yield curve inverted',
    '10 year 2 year spread',
    'yield curve inversion history',
    'treasury yield curve today',
    '10y 2y treasury spread chart',
    'yield curve inversion dates',
  ],
  alternates: { canonical: url },
  openGraph: {
    title: 'Is the Yield Curve Inverted?',
    description:
      'Current Treasury curve plus every sustained inversion since 1990, with dates, durations and depths computed from the daily series.',
    type: 'website',
    url,
  },
}

const bp = (v: number) => `${v >= 0 ? '+' : ''}${v.toFixed(0)}bp`

export default function YieldCurvePage() {
  if (!data || !s2) {
    return (
      <div className="container mx-auto px-4 py-12">
        <h1 className="text-4xl font-bold mb-4 text-white">Treasury Yield Curve</h1>
        <div className="max-w-3xl rounded-xl border border-amber-500/30 bg-amber-500/5 p-6">
          <h2 className="text-xl font-bold text-white mb-2">Curve data is not available</h2>
          <p className="text-slate-400">
            The measured artefact has not been published. This page will not show an
            illustrative or last-known curve in its absence — a stale yield curve presented as
            current is worse than none.
          </p>
        </div>
      </div>
    )
  }

  const s3 = data.spreads['10y3m']
  const longest = [...s2.sustained_episodes].sort((a, b) => b.calendar_days - a.calendar_days)[0]
  const deepest = [...s2.sustained_episodes].sort((a, b) => a.deepest_bp - b.deepest_bp)[0]

  const faqs = [
    {
      q: 'Is the yield curve inverted right now?',
      a: `As of ${data.latest.date}, the 10-year minus 2-year spread is ${bp(s2.current_bp)}, so it is ${s2.inverted_now ? 'inverted' : 'not inverted'}. The 10-year minus 3-month spread is ${bp(s3.current_bp)}, ${s3.inverted_now ? 'also inverted' : 'also not inverted'}. Both are computed from the Treasury par yields published for that date.`,
    },
    {
      q: 'What does an inverted yield curve mean?',
      a: 'It means investors accept a lower yield to lend for ten years than for two, which is the reverse of the usual compensation for tying money up longer. The common reading is that the market expects short-term rates to fall, which usually happens when growth is expected to weaken. It is a description of market prices, not a forecast, and the association with recessions is a historical statistical relationship over a modest number of episodes.',
    },
    {
      q: 'How many times has the curve inverted?',
      a: `Since ${s2.first}, the 10-year minus 2-year spread has been negative on ${s2.days_inverted.toLocaleString()} of ${s2.observations.toLocaleString()} published business days, across ${s2.sustained_episodes.length} sustained episodes lasting at least ${data.method.min_episode_calendar_days} calendar days. There were a further ${s2.brief_episodes_count} briefer dips totalling ${s2.brief_episodes_days} days, listed separately because the spread crosses zero repeatedly when it sits near the line and counting each crossing separately inflates the total.`,
    },
    {
      q: 'What was the longest inversion?',
      a: `${longest.start} to ${longest.end} — ${longest.calendar_days.toLocaleString()} calendar days (${longest.trading_days.toLocaleString()} trading days), reaching ${bp(longest.deepest_bp)} at its deepest on ${longest.deepest_on}. The deepest of any episode in this record was ${bp(deepest.deepest_bp)} on ${deepest.deepest_on}.`,
    },
    {
      q: 'Which spread should I look at, 10y-2y or 10y-3m?',
      a: 'Both are shown because they do not always agree, and the disagreement is informative. The 10y-3m spread is the one used in most of the academic recession-prediction literature (Estrella and Mishkin), while 10y-2y is the one financial media quote most often. The 3-month leg tracks policy rates closely, so 10y-3m tends to invert later and more sharply.',
    },
    {
      q: 'Where does this data come from?',
      a: `Directly from the US Treasury's daily par yield curve rates — ${data.coverage.observations.toLocaleString()} published business days from ${data.coverage.first_date} to ${data.coverage.last_date}. These are par yields, not zero-coupon yields. Treasury data is a US government work in the public domain, so it can be republished here freely.`,
    },
  ]

  const faqSchema = {
    '@context': 'https://schema.org',
    '@type': 'FAQPage',
    mainEntity: faqs.map((f) => ({
      '@type': 'Question',
      name: f.q,
      acceptedAnswer: { '@type': 'Answer', text: f.a },
    })),
  }

  const StatusCard = ({ s, name }: { s: Spread; name: string }) => (
    <div
      className={`rounded-xl border p-5 ${
        s.inverted_now
          ? 'border-rose-500/40 bg-rose-500/10'
          : 'border-emerald-500/30 bg-emerald-500/5'
      }`}
    >
      <div className="text-xs font-semibold uppercase tracking-wide text-[hsl(215,20%,60%)]">
        {name}
      </div>
      <div className="mt-1 font-mono text-4xl font-bold tabular-nums text-white">
        {bp(s.current_bp)}
      </div>
      <div
        className={`mt-2 inline-block rounded-full px-2.5 py-0.5 text-xs font-semibold ${
          s.inverted_now ? 'bg-rose-500/20 text-rose-300' : 'bg-emerald-500/20 text-emerald-300'
        }`}
      >
        {s.inverted_now ? 'Inverted' : 'Not inverted'}
      </div>
      <div className="mt-3 text-xs text-[hsl(215,20%,50%)]">
        {s.days_inverted.toLocaleString()} of {s.observations.toLocaleString()} days inverted
        since {s.first}
      </div>
    </div>
  )

  return (
    <div className="container mx-auto px-4 py-12">
      <script type="application/ld+json" dangerouslySetInnerHTML={{ __html: JSON.stringify(faqSchema) }} />

      <nav className="text-sm text-[hsl(215,20%,55%)] mb-6">
        <Link href="/tools" className="hover:text-indigo-400">Tools</Link>
        <span className="mx-2">/</span>
        <span className="text-[hsl(215,20%,70%)]">Treasury Yield Curve</span>
      </nav>

      <div className="max-w-3xl mb-8">
        <h1 className="text-4xl md:text-5xl font-bold mb-4 text-white">
          Is the Yield Curve Inverted?
        </h1>
        <p className="text-lg text-slate-400">
          As of {data.latest.date}, the 10-year minus 2-year Treasury spread is{' '}
          <strong className="text-white">{bp(s2.current_bp)}</strong> — {s2.inverted_now ? 'inverted' : 'not inverted'}.
          Below: today&apos;s full par curve, and every sustained inversion since{' '}
          {s2.first}, computed from Treasury&apos;s own daily series rather than recalled.
        </p>
      </div>

      <div className="grid gap-4 sm:grid-cols-2 max-w-2xl mb-10">
        <StatusCard s={s2} name="10-year − 2-year" />
        <StatusCard s={s3} name="10-year − 3-month" />
      </div>

      <section className="rounded-xl border border-[hsl(215,40%,18%)] bg-[hsl(220,55%,9%)] p-6 mb-6">
        <h2 className="text-xl font-bold text-white mb-1">Par yield curve, {data.latest.date}</h2>
        <p className="text-sm text-[hsl(215,20%,50%)] mb-4">
          Maturities are spaced logarithmically — on a linear axis the eleven tenors under
          two years collapse into the left edge and the short end, which is the part that
          inverts, becomes unreadable.
        </p>
        <CurveChart curve={data.latest.curve} asOf={data.latest.date} />
        <div className="mt-4 overflow-x-auto">
          <table className="w-full text-sm">
            <thead>
              <tr className="border-b border-[hsl(215,40%,14%)]">
                {data.latest.curve.map((t) => (
                  <th key={t.tenor} className="px-2 py-1.5 text-right text-xs font-semibold uppercase tracking-wide text-[hsl(215,20%,55%)] whitespace-nowrap">
                    {t.tenor}
                  </th>
                ))}
              </tr>
            </thead>
            <tbody>
              <tr>
                {data.latest.curve.map((t) => (
                  <td key={t.tenor} className="px-2 py-2 text-right font-mono tabular-nums text-slate-200">
                    {t.yield.toFixed(2)}
                  </td>
                ))}
              </tr>
            </tbody>
          </table>
        </div>
      </section>

      <section className="rounded-xl border border-[hsl(215,40%,18%)] bg-[hsl(220,55%,9%)] p-6 mb-14">
        <h2 className="text-xl font-bold text-white mb-1">
          10-year minus 2-year spread, {s2.first} to {s2.last}
        </h2>
        <p className="text-sm text-[hsl(215,20%,50%)] mb-4">
          Shaded bands are the periods the spread spent below zero. Values are percentage
          points.
        </p>
        <SpreadChart history={data.history} label="10-year minus 2-year Treasury spread" />
      </section>

      <section className="max-w-4xl mt-14">
        <h2 className="text-2xl font-bold text-white mb-2">Every sustained inversion since {s2.first}</h2>
        <p className="text-slate-400 mb-6">
          {s2.sustained_episodes.length} episodes of the 10y−2y spread lasting at least{' '}
          {data.method.min_episode_calendar_days} calendar days. Each row is computed from the
          daily series: the run of consecutive published observations with a negative spread,
          and the single deepest reading within it.
        </p>
        <div className="overflow-x-auto rounded-xl border border-[hsl(215,40%,18%)]">
          <table className="w-full text-sm">
            <thead className="bg-[hsl(220,55%,7%)]">
              <tr>
                {['Start', 'End', 'Calendar days', 'Trading days', 'Deepest', 'Deepest on'].map((h, i) => (
                  <th key={h} className={`px-3 py-2 text-xs font-semibold uppercase tracking-wide text-[hsl(215,20%,60%)] whitespace-nowrap ${i < 2 ? 'text-left' : 'text-right'}`}>
                    {h}
                  </th>
                ))}
              </tr>
            </thead>
            <tbody>
              {[...s2.sustained_episodes].reverse().map((e) => (
                <tr key={e.start} className="border-t border-[hsl(215,40%,12%)]">
                  <td className="px-3 py-2 font-mono text-slate-200">{e.start}</td>
                  <td className="px-3 py-2 font-mono text-slate-200">{e.end}</td>
                  <td className="px-3 py-2 text-right font-mono tabular-nums text-slate-300">
                    {e.calendar_days.toLocaleString()}
                  </td>
                  <td className="px-3 py-2 text-right font-mono tabular-nums text-[hsl(215,20%,55%)]">
                    {e.trading_days.toLocaleString()}
                  </td>
                  <td className="px-3 py-2 text-right font-mono tabular-nums text-rose-300">
                    {bp(e.deepest_bp)}
                  </td>
                  <td className="px-3 py-2 text-right font-mono text-xs text-[hsl(215,20%,50%)]">
                    {e.deepest_on}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
        <p className="mt-4 text-sm text-[hsl(215,20%,50%)]">
          A further {s2.brief_episodes_count} dips below zero lasted under{' '}
          {data.method.min_episode_calendar_days} days, totalling {s2.brief_episodes_days} days.
          They are excluded from the table above and counted here instead: when the spread sits
          near zero it crosses repeatedly, and treating each crossing as a separate inversion
          inflates the count without adding information.
        </p>
      </section>

      <section className="max-w-3xl mt-14">
        <h2 className="text-2xl font-bold text-white mb-4">How an episode is defined</h2>
        <p className="text-slate-400 leading-relaxed mb-4">{data.method.episode_definition}</p>
        <p className="text-slate-400 leading-relaxed mb-4">{data.method.no_interpolation}</p>
        <p className="text-slate-400 leading-relaxed">
          This matters more than it sounds. Published inversion dates disagree with each other
          largely because of these two choices — whether a weekend counts as a break, and
          whether a one-day flicker back above zero ends an episode. Both choices are stated
          here and applied uniformly, so the numbers are reproducible from the source data by
          anyone who wants to check them.
        </p>
      </section>

      <section className="max-w-3xl mt-14">
        <h2 className="text-2xl font-bold text-white mb-4">What this does not tell you</h2>
        <p className="text-slate-400 leading-relaxed">
          The association between inversions and subsequent recessions rests on a handful of
          episodes — nine in this record — which is far too few to support a confident
          probability, however often the relationship is quoted. Lead times in past episodes
          have varied from months to more than two years, and an average taken over nine
          observations with that much spread carries almost no information about the next one.
          This page reports what the curve has done. It does not forecast, and nothing here is
          investment advice.
        </p>
      </section>

      <section className="max-w-3xl mt-14">
        <h2 className="text-2xl font-bold text-white mb-6">Frequently asked questions</h2>
        <div className="space-y-4">
          {faqs.map((f) => (
            <details key={f.q} className="group rounded-xl border border-[hsl(215,40%,18%)] bg-[hsl(220,55%,9%)] p-5">
              <summary className="cursor-pointer text-white font-semibold list-none flex justify-between items-center gap-4">
                {f.q}
                <span className="text-indigo-400 group-open:rotate-45 transition-transform shrink-0">+</span>
              </summary>
              <p className="mt-3 text-slate-400 leading-relaxed">{f.a}</p>
            </details>
          ))}
        </div>
      </section>

      <section className="max-w-3xl mt-14">
        <h2 className="text-2xl font-bold text-white mb-4">Get the data</h2>
        <p className="text-slate-400 leading-relaxed mb-4">
          The full artefact — {data.coverage.observations.toLocaleString()} daily observations,
          both spread series, and every episode with its provenance — is served as static JSON.
        </p>
        <a href="/data/treasury-curve.json"
           className="inline-block rounded-lg bg-indigo-600 px-5 py-3 text-white transition-colors hover:bg-indigo-500">
          Download treasury-curve.json
        </a>
        <p className="mt-4 text-xs text-[hsl(215,20%,45%)]">
          Generated {data.generated_at}. Source: {data.source.name}. {data.source.note}{' '}
          {data.source.licence}
        </p>
      </section>

      <section className="max-w-3xl mt-14">
        <h2 className="text-2xl font-bold text-white mb-6">Related tools</h2>
        <div className="grid gap-4 sm:grid-cols-2">
          <Link href="/fundamentals" className="group rounded-xl border border-[hsl(215,40%,18%)] bg-[hsl(220,55%,9%)] p-5 transition-all hover:border-indigo-500/60 hover:bg-[hsl(220,55%,11%)]">
            <h3 className="text-lg font-semibold text-white group-hover:text-indigo-400 transition-colors">Fundamental Screener</h3>
            <p className="mt-1.5 text-sm text-slate-400">Accruals and asset growth from SEC XBRL filings.</p>
          </Link>
          <Link href="/tools/max-sharpe" className="group rounded-xl border border-[hsl(215,40%,18%)] bg-[hsl(220,55%,9%)] p-5 transition-all hover:border-indigo-500/60 hover:bg-[hsl(220,55%,11%)]">
            <h3 className="text-lg font-semibold text-white group-hover:text-indigo-400 transition-colors">Max Sharpe Portfolio</h3>
            <p className="mt-1.5 text-sm text-slate-400">Closed-form tangency portfolio weights.</p>
          </Link>
          <Link href="/scanner" className="group rounded-xl border border-[hsl(215,40%,18%)] bg-[hsl(220,55%,9%)] p-5 transition-all hover:border-indigo-500/60 hover:bg-[hsl(220,55%,11%)]">
            <h3 className="text-lg font-semibold text-white group-hover:text-indigo-400 transition-colors">Seasonality Screener</h3>
            <p className="mt-1.5 text-sm text-slate-400">Multiple-testing-corrected seasonal effects.</p>
          </Link>
          <Link href="/tools" className="group rounded-xl border border-[hsl(215,40%,18%)] bg-[hsl(220,55%,9%)] p-5 transition-all hover:border-indigo-500/60 hover:bg-[hsl(220,55%,11%)]">
            <h3 className="text-lg font-semibold text-white group-hover:text-indigo-400 transition-colors">All Trading Tools</h3>
            <p className="mt-1.5 text-sm text-slate-400">Browse every free tool on QuantEngines.</p>
          </Link>
        </div>
      </section>

      <p className="max-w-3xl mt-14 text-xs text-[hsl(215,20%,45%)] leading-relaxed">
        Source: US Department of the Treasury, Daily Treasury Par Yield Curve Rates. This page
        is not affiliated with or endorsed by the Treasury. Nothing here is investment advice or
        a forecast of interest rates, growth, or recession.
      </p>
    </div>
  )
}
