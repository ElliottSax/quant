/**
 * CFTC Commitments of Traders positioning, z-scored against each market's own history.
 *
 * The raw COT report is ~130 columns and effectively unreadable as released. The single
 * question people bring to it is "is this group unusually long or short right now", which
 * needs normalising by open interest and then scoring against that market's own past.
 *
 * Artefact: `python -m pipeline.cftc_cot`. CFTC data is a US government work, so it can
 * be republished here without the licence problem every free price API carries.
 */

import type { Metadata } from 'next'
import Link from 'next/link'

const url = 'https://quantengines.com/cot-report'

interface Market {
  code: string
  label: string
  group: string
  weeks: number
  error?: string
  filed_as?: string[]
  first?: string
  last?: string
  open_interest?: number
  commercial_net?: number
  noncommercial_net?: number
  commercial_net_pct?: number
  noncommercial_net_pct?: number
  commercial_z?: number | null
  noncommercial_z?: number | null
  history?: Array<[string, number, number]>
}

interface Artifact {
  generated_at: string
  source: { name: string; url: string; licence: string; cadence: string }
  method: Record<string, string | number>
  caveats: Record<string, string>
  markets: Market[]
}

function load(): Artifact | null {
  try {
    // eslint-disable-next-line @typescript-eslint/no-var-requires
    const d = require('../../../public/data/cot-positioning.json') as Artifact
    return d?.markets?.length ? d : null
  } catch {
    return null
  }
}

const data = load()
const asOf = data?.markets.find((m) => m.last)?.last

export const metadata: Metadata = {
  title: asOf
    ? `COT Report Positioning — Speculator Net Position Z-Scores (${asOf})`
    : 'CFTC Commitments of Traders Positioning | QuantEngines',
  description:
    'Commitments of Traders positioning for 11 major futures markets, normalised by open interest and z-scored against up to 21 years of that market’s own history. Free, sourced directly from the CFTC, with the method and its limits stated.',
  keywords: [
    'commitment of traders report',
    'cot report',
    'cftc cot data',
    'commercial vs non-commercial positioning',
    'cot net positioning chart',
    'speculator positioning extremes',
  ],
  alternates: { canonical: url },
  openGraph: {
    title: 'COT Report Positioning, Z-Scored',
    description:
      'Commitments of Traders net positioning for 11 futures markets, normalised and scored against each market’s own history.',
    type: 'website',
    url,
  },
}

/** A z-score bar centred on zero. Reading a number and a position is faster than reading
 *  the number alone, and this is the one comparison the page exists to make. */
function ZBar({ z }: { z: number | null | undefined }) {
  if (z === null || z === undefined) {
    return <span className="text-xs text-[hsl(215,20%,45%)]">insufficient history</span>
  }
  const clamped = Math.max(-3, Math.min(3, z))
  const pctFromCentre = (clamped / 3) * 50
  const extreme = Math.abs(z) >= 2
  const colour = z > 0 ? 'bg-emerald-400' : 'bg-rose-400'
  return (
    <div className="flex items-center gap-2">
      <div className="relative h-2 w-28 rounded-full bg-[hsl(220,55%,14%)] shrink-0">
        <div className="absolute left-1/2 top-0 h-2 w-px bg-[hsl(215,20%,45%)]" />
        <div
          className={`absolute top-0 h-2 ${colour} ${extreme ? '' : 'opacity-60'} rounded-full`}
          style={
            pctFromCentre >= 0
              ? { left: '50%', width: `${pctFromCentre}%` }
              : { left: `${50 + pctFromCentre}%`, width: `${-pctFromCentre}%` }
          }
        />
      </div>
      <span
        className={`font-mono tabular-nums text-sm ${
          extreme ? (z > 0 ? 'text-emerald-300' : 'text-rose-300') : 'text-slate-300'
        }`}
      >
        {z > 0 ? '+' : ''}{z.toFixed(2)}
      </span>
    </div>
  )
}

export default function CotReportPage() {
  if (!data) {
    return (
      <div className="container mx-auto px-4 py-12">
        <h1 className="text-4xl font-bold mb-4 text-white">Commitments of Traders</h1>
        <div className="max-w-3xl rounded-xl border border-amber-500/30 bg-amber-500/5 p-6">
          <h2 className="text-xl font-bold text-white mb-2">Positioning data is not available</h2>
          <p className="text-slate-400">
            The measured artefact has not been published. Stale positioning shown as current
            would be worse than none, so nothing is displayed.
          </p>
        </div>
      </div>
    )
  }

  const live = data.markets.filter((m) => m.weeks > 0)
  const stretched = live
    .filter((m) => m.noncommercial_z !== null && Math.abs(m.noncommercial_z!) >= 1.5)
    .sort((a, b) => Math.abs(b.noncommercial_z!) - Math.abs(a.noncommercial_z!))

  const groups = Array.from(new Set(live.map((m) => m.group)))

  const faqs = [
    {
      q: 'What is the Commitments of Traders report?',
      a: `A weekly CFTC publication breaking down open interest in US futures markets by trader category. ${data.source.cadence}`,
    },
    {
      q: 'What is the difference between commercial and non-commercial?',
      a: 'Commercials are hedgers — producers, processors and users of the underlying, whose positions are driven by hedging need rather than a market view. Non-commercials are large speculators taking a directional position. A commercial short in a commodity is usually a producer hedging output, not a bearish opinion, which is the most commonly misread part of the report.',
    },
    {
      q: 'What does the z-score mean here?',
      a: `${data.method.z_score} A score of +2 means current net positioning is two standard deviations above that market's own average, so it is unusual by its own standards — it does not mean the position is large compared with another market.`,
    },
    {
      q: 'Why divide by open interest?',
      a: String(data.method.normalisation) + ' A net position of 300,000 contracts is enormous in one market and unremarkable in another, and markets grow over decades, so raw contract counts are not comparable across either dimension.',
    },
    {
      q: 'Is extreme positioning a trading signal?',
      a: data.caveats.not_a_signal,
    },
    {
      q: 'Why do commercial and speculator scores mirror each other?',
      a: data.caveats.mirror_image,
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

  return (
    <div className="container mx-auto px-4 py-12">
      <script type="application/ld+json" dangerouslySetInnerHTML={{ __html: JSON.stringify(faqSchema) }} />

      <nav className="text-sm text-[hsl(215,20%,55%)] mb-6">
        <Link href="/tools" className="hover:text-indigo-400">Tools</Link>
        <span className="mx-2">/</span>
        <span className="text-[hsl(215,20%,70%)]">COT Report</span>
      </nav>

      <div className="max-w-3xl mb-8">
        <h1 className="text-4xl md:text-5xl font-bold mb-4 text-white">
          COT Report Positioning
        </h1>
        <p className="text-lg text-slate-400">
          Speculator and hedger net positioning for {live.length} major futures markets as of{' '}
          {asOf}, divided by open interest and scored against each market&apos;s own history —
          up to {Math.max(...live.map((m) => m.weeks)).toLocaleString()} weeks of it. Straight
          from the CFTC, with the method and its limits stated rather than implied.
        </p>
      </div>

      <div className="max-w-3xl mb-10 rounded-xl border border-amber-500/30 bg-amber-500/5 p-5">
        <h2 className="text-sm font-semibold uppercase tracking-wide text-amber-300 mb-2">
          Read this before using it
        </h2>
        <p className="text-sm text-amber-100/80 leading-relaxed">{data.caveats.not_a_signal}</p>
      </div>

      {stretched.length > 0 && (
        <section className="mb-12">
          <h2 className="text-2xl font-bold text-white mb-2">Most stretched right now</h2>
          <p className="text-slate-400 mb-5 max-w-3xl">
            Markets where speculator net positioning is at least 1.5 standard deviations from
            its own long-run average. That is a statement about how unusual the position is,
            not about what happens next.
          </p>
          <div className="grid gap-3 sm:grid-cols-2 lg:grid-cols-3">
            {stretched.map((m) => (
              <div key={m.code} className="rounded-xl border border-[hsl(215,40%,18%)] bg-[hsl(220,55%,9%)] p-5">
                <div className="flex items-baseline justify-between gap-2">
                  <h3 className="font-semibold text-white">{m.label}</h3>
                  <span className="text-xs text-[hsl(215,20%,50%)]">{m.group}</span>
                </div>
                <div className="mt-2 font-mono text-2xl font-bold tabular-nums text-white">
                  {m.noncommercial_net_pct! > 0 ? '+' : ''}{m.noncommercial_net_pct}%
                </div>
                <div className="text-xs text-[hsl(215,20%,50%)]">
                  speculator net, as a share of open interest
                </div>
                <div className="mt-3">
                  <ZBar z={m.noncommercial_z} />
                </div>
              </div>
            ))}
          </div>
        </section>
      )}

      {groups.map((g) => (
        <section key={g} className="mb-10">
          <h2 className="text-xl font-bold text-white mb-3">{g}</h2>
          <div className="overflow-x-auto rounded-xl border border-[hsl(215,40%,18%)]">
            <table className="w-full text-sm">
              <thead className="bg-[hsl(220,55%,7%)]">
                <tr>
                  {['Market', 'Open interest', 'Speculator net', 'Speculator z', 'Hedger net', 'Hedger z', 'History'].map((h, i) => (
                    <th key={h} className={`px-3 py-2 text-xs font-semibold uppercase tracking-wide text-[hsl(215,20%,60%)] whitespace-nowrap ${i === 0 ? 'text-left' : 'text-right'}`}>
                      {h}
                    </th>
                  ))}
                </tr>
              </thead>
              <tbody>
                {live.filter((m) => m.group === g).map((m) => (
                  <tr key={m.code} className="border-t border-[hsl(215,40%,12%)]">
                    <td className="px-3 py-3 text-slate-200 whitespace-nowrap">{m.label}</td>
                    <td className="px-3 py-3 text-right font-mono tabular-nums text-slate-300">
                      {m.open_interest!.toLocaleString()}
                    </td>
                    <td className="px-3 py-3 text-right font-mono tabular-nums text-slate-200">
                      {m.noncommercial_net_pct! > 0 ? '+' : ''}{m.noncommercial_net_pct}%
                    </td>
                    <td className="px-3 py-3"><div className="flex justify-end"><ZBar z={m.noncommercial_z} /></div></td>
                    <td className="px-3 py-3 text-right font-mono tabular-nums text-slate-200">
                      {m.commercial_net_pct! > 0 ? '+' : ''}{m.commercial_net_pct}%
                    </td>
                    <td className="px-3 py-3"><div className="flex justify-end"><ZBar z={m.commercial_z} /></div></td>
                    <td className="px-3 py-3 text-right font-mono text-xs text-[hsl(215,20%,45%)] whitespace-nowrap">
                      {m.weeks.toLocaleString()} wks<br />
                      <span className="text-[10px]">from {m.first}</span>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </section>
      ))}

      <section className="max-w-3xl mt-14">
        <h2 className="text-2xl font-bold text-white mb-4">Method</h2>
        <p className="text-slate-400 leading-relaxed mb-4">{data.method.normalisation}</p>
        <p className="text-slate-400 leading-relaxed mb-4">{data.method.z_score}</p>
        <p className="text-slate-400 leading-relaxed mb-4">{data.method.no_interpolation}</p>
        <p className="text-slate-400 leading-relaxed">
          Series are keyed on the CFTC contract market code rather than the contract&apos;s
          display name, because the name is not stable. The E-mini S&amp;P 500 has filed under
          three different names since 1997; keying on the current one would silently cut its
          history to four years and score today&apos;s positioning against a much shorter idea
          of &quot;normal&quot; than gold or the yen get. Each code was checked against its
          real date range rather than assumed — corn trades under 002602, while the 002601 a
          name lookup returns first was retired in 1997.
        </p>
      </section>

      <section className="max-w-3xl mt-14">
        <h2 className="text-2xl font-bold text-white mb-4">Limitations</h2>
        <div className="space-y-4">
          {Object.entries(data.caveats).map(([k, v]) => (
            <div key={k}>
              <h3 className="text-sm font-semibold text-slate-200 mb-1">
                {k.replace(/_/g, ' ').replace(/^./, (c) => c.toUpperCase())}
              </h3>
              <p className="text-sm text-slate-400 leading-relaxed">{v}</p>
            </div>
          ))}
        </div>
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
          The full artefact — every weekly observation for all {live.length} markets, both
          series, plus the provenance and method blocks — is served as static JSON.
        </p>
        <a href="/data/cot-positioning.json"
           className="inline-block rounded-lg bg-indigo-600 px-5 py-3 text-white transition-colors hover:bg-indigo-500">
          Download cot-positioning.json
        </a>
        <p className="mt-4 text-xs text-[hsl(215,20%,45%)]">
          Generated {data.generated_at}. Source: {data.source.name}. {data.source.licence}
        </p>
      </section>

      <section className="max-w-3xl mt-14">
        <h2 className="text-2xl font-bold text-white mb-6">Related tools</h2>
        <div className="grid gap-4 sm:grid-cols-2">
          <Link href="/yield-curve" className="group rounded-xl border border-[hsl(215,40%,18%)] bg-[hsl(220,55%,9%)] p-5 transition-all hover:border-indigo-500/60 hover:bg-[hsl(220,55%,11%)]">
            <h3 className="text-lg font-semibold text-white group-hover:text-indigo-400 transition-colors">Treasury Yield Curve</h3>
            <p className="mt-1.5 text-sm text-slate-400">Every sustained inversion since 1990, measured.</p>
          </Link>
          <Link href="/fundamentals" className="group rounded-xl border border-[hsl(215,40%,18%)] bg-[hsl(220,55%,9%)] p-5 transition-all hover:border-indigo-500/60 hover:bg-[hsl(220,55%,11%)]">
            <h3 className="text-lg font-semibold text-white group-hover:text-indigo-400 transition-colors">Fundamental Screener</h3>
            <p className="mt-1.5 text-sm text-slate-400">Accruals and asset growth from SEC XBRL filings.</p>
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
        Source: US Commodity Futures Trading Commission. This page is not affiliated with or
        endorsed by the CFTC. Positioning data describes who held what as of the report date;
        nothing here is investment advice, a forecast, or a trading signal.
      </p>
    </div>
  )
}
