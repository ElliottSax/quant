/**
 * Cross-sectional fundamental screener over the whole US filing universe.
 *
 * The differentiator is the source: SEC XBRL `frames` returns every filer's value for a
 * concept in one request, so a market-wide screen needs no data vendor and carries no
 * licence restriction (US government work, public domain). Free price APIs uniformly
 * forbid commercial display; this does not.
 *
 * The artefact is produced by `python -m pipeline.edgar_fundamentals`, which matches each
 * company's balance sheets to its OWN fiscal year end rather than to a calendar quarter —
 * so Apple is measured September-to-September and Microsoft June-to-June, and each
 * accrual denominator spans the same twelve months as its numerator.
 */

import type { Metadata } from 'next'
import Link from 'next/link'
import ScreenerTable, { type Row } from './ScreenerTable'

const url = 'https://quantengines.com/fundamentals'

export const metadata: Metadata = {
  title: 'Fundamental Screener — Accruals, Asset Growth & Net Issuance | QuantEngines',
  description:
    'Screen 3,000+ US filers on three documented accounting anomalies — accruals (Sloan 1996), asset growth (Cooper–Gulen–Schill 2008) and net share issuance (Pontiff–Woodgate 2008) — computed directly from SEC XBRL filings. Free, no signup, sources cited.',
  keywords: [
    'accruals screener',
    'asset growth anomaly screener',
    'net share issuance screener',
    'sec xbrl frames api',
    'fundamental stock screener free',
    'sloan accruals ratio',
    'edgar financial data api',
  ],
  alternates: { canonical: url },
  openGraph: {
    title: 'Fundamental Screener — Accruals, Asset Growth & Net Issuance',
    description:
      'Three documented accounting anomalies computed across the whole US filing universe, straight from SEC XBRL.',
    type: 'website',
    url,
  },
}

interface Artifact {
  generated_at: string
  fiscal_year: number
  compared_against: number
  method: { flow_period: string; balance_sheets_searched: string[]; matching: string }
  source: { name: string; urls: string[]; licence: string }
  universe: {
    filers_reporting_annual_flows: number
    screened: number
    dropped: Record<string, number>
    min_assets_usd: number
  }
  signal_coverage: Record<string, number>
  caveats: Record<string, string>
  signals: Record<string, { label: string; formula: string; citation: string; direction: string }>
  rows: Row[]
}

function load(): Artifact | null {
  try {
    // eslint-disable-next-line @typescript-eslint/no-var-requires
    const d = require('../../../public/data/edgar-screener.json') as Artifact
    return d?.rows?.length ? d : null
  } catch {
    return null
  }
}

// Only the largest filers are embedded in the page. The full artefact is served as a
// static file and linked below, so nothing is hidden — this keeps the HTML payload sane
// while still covering everything anyone would realistically screen.
const EMBEDDED_ROWS = 1200

function extremes(rows: Row[], key: keyof Row, n: number) {
  const withVal = rows.filter((r) => r[key] !== null) as Row[]
  const sorted = [...withVal].sort((a, b) => (a[key] as number) - (b[key] as number))
  return { low: sorted.slice(0, n), high: sorted.slice(-n).reverse() }
}

export default function FundamentalsPage() {
  const data = load()

  if (!data) {
    return (
      <div className="container mx-auto px-4 py-12">
        <h1 className="text-4xl font-bold mb-4 text-white">Fundamental Screener</h1>
        <div className="max-w-3xl rounded-xl border border-amber-500/30 bg-amber-500/5 p-6">
          <h2 className="text-xl font-bold text-white mb-2">Screener data is not available</h2>
          <p className="text-slate-400">
            The measured artefact has not been published, so there is nothing to screen. This
            page will not show illustrative or sample companies in its absence — the whole
            point of it is that every figure came from a filing.
          </p>
        </div>
      </div>
    )
  }

  const rows = data.rows
  const embedded = rows.slice(0, EMBEDDED_ROWS)
  // Extremes are computed over the FULL universe, not the embedded slice, so the
  // "highest accruals" table really is the highest and not merely the highest among
  // large caps.
  const accr = extremes(rows, 'accruals', 10)
  const growth = extremes(rows, 'asset_growth', 10)

  const dropped = Object.entries(data.universe.dropped).sort((a, b) => b[1] - a[1])

  const datasetSchema = {
    '@context': 'https://schema.org',
    '@type': 'Dataset',
    name: 'US fundamental anomaly screener (accruals, asset growth, net issuance)',
    description:
      'Accruals, asset growth and net share issuance for US SEC filers, computed from XBRL company facts and matched to each company fiscal year.',
    url,
    license: 'https://www.usa.gov/government-works',
    isAccessibleForFree: true,
    creator: { '@type': 'Organization', name: 'QuantEngines' },
    temporalCoverage: `${data.compared_against}/${data.fiscal_year}`,
    distribution: {
      '@type': 'DataDownload',
      encodingFormat: 'application/json',
      contentUrl: `${url.replace('/fundamentals', '')}/data/edgar-screener.json`,
    },
  }

  const pct = (v: number | null) => (v === null ? '—' : `${(v * 100).toFixed(1)}%`)

  const ExtremeTable = ({ title, note, list, k }: { title: string; note: string; list: Row[]; k: keyof Row }) => (
    <div className="rounded-xl border border-[hsl(215,40%,18%)] bg-[hsl(220,55%,9%)] p-5">
      <h3 className="font-semibold text-white">{title}</h3>
      <p className="mt-1 mb-3 text-xs text-[hsl(215,20%,50%)]">{note}</p>
      <table className="w-full text-sm">
        <tbody>
          {list.map((r) => (
            <tr key={r.cik} className="border-t border-[hsl(215,40%,12%)]">
              <td className="py-1.5 pr-2 font-mono text-indigo-400">{r.ticker}</td>
              <td className="py-1.5 pr-2 text-xs text-[hsl(215,20%,50%)] truncate max-w-[10rem]">{r.name}</td>
              <td className="py-1.5 text-right font-mono tabular-nums text-slate-200">
                {pct(r[k] as number | null)}
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  )

  return (
    <div className="container mx-auto px-4 py-12">
      <script type="application/ld+json" dangerouslySetInnerHTML={{ __html: JSON.stringify(datasetSchema) }} />

      <nav className="text-sm text-[hsl(215,20%,55%)] mb-6">
        <Link href="/tools" className="hover:text-indigo-400">Tools</Link>
        <span className="mx-2">/</span>
        <span className="text-[hsl(215,20%,70%)]">Fundamental Screener</span>
      </nav>

      <div className="max-w-3xl mb-8">
        <h1 className="text-4xl md:text-5xl font-bold mb-4 text-white">Fundamental Screener</h1>
        <p className="text-lg text-slate-400">
          {data.universe.screened.toLocaleString()} US filers ranked on three documented
          accounting anomalies — accruals, asset growth and net share issuance — computed
          directly from SEC XBRL filings for fiscal {data.fiscal_year} against{' '}
          {data.compared_against}. No data vendor is involved, and no figure here is
          estimated.
        </p>
      </div>

      <div className="max-w-3xl mb-10 rounded-xl border border-amber-500/30 bg-amber-500/5 p-5">
        <h2 className="text-sm font-semibold uppercase tracking-wide text-amber-300 mb-2">
          Read this before using it
        </h2>
        <p className="text-sm text-amber-100/80 leading-relaxed">{data.caveats.not_point_in_time}</p>
      </div>

      <ScreenerTable rows={embedded} />

      <section className="max-w-5xl mt-14">
        <h2 className="text-2xl font-bold text-white mb-2">The three signals</h2>
        <p className="text-slate-400 mb-6 max-w-3xl">
          Each is a published cross-sectional association between an accounting quantity and
          subsequent stock returns, replicated independently after publication. Each is
          computable from filings alone, which is why these three and not others.
        </p>
        <div className="grid gap-4 md:grid-cols-3">
          {Object.entries(data.signals).map(([key, s]) => (
            <div key={key} className="rounded-xl border border-[hsl(215,40%,18%)] bg-[hsl(220,55%,9%)] p-5">
              <h3 className="text-lg font-semibold text-white">{s.label}</h3>
              <p className="mt-2 font-mono text-sm text-indigo-300">{s.formula}</p>
              <p className="mt-3 text-sm text-slate-400">{s.direction}</p>
              <p className="mt-3 text-xs text-[hsl(215,20%,45%)]">{s.citation}</p>
              <p className="mt-2 text-xs text-[hsl(215,20%,45%)]">
                Reported for {data.signal_coverage[key]?.toLocaleString()} of{' '}
                {data.universe.screened.toLocaleString()} companies.
              </p>
            </div>
          ))}
        </div>
      </section>

      <section className="max-w-5xl mt-14">
        <h2 className="text-2xl font-bold text-white mb-6">The extremes</h2>
        <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
          <ExtremeTable
            title="Lowest accruals"
            note="Earnings most backed by cash."
            list={accr.low}
            k="accruals"
          />
          <ExtremeTable
            title="Highest accruals"
            note="Earnings least backed by cash."
            list={accr.high}
            k="accruals"
          />
          <ExtremeTable
            title="Lowest asset growth"
            note="Balance sheets that shrank most."
            list={growth.low}
            k="asset_growth"
          />
          <ExtremeTable
            title="Highest asset growth"
            note="Balance sheets that expanded most."
            list={growth.high}
            k="asset_growth"
          />
        </div>
        <p className="mt-4 text-sm text-[hsl(215,20%,50%)] max-w-3xl">
          These are the extremes of the whole screened universe, not of the table above. An
          extreme value is more often an accounting event — an acquisition, a spin-off, a
          reverse merger — than a signal, and none of these lists is a recommendation.
        </p>
      </section>

      <section className="max-w-3xl mt-14">
        <h2 className="text-2xl font-bold text-white mb-4">How the numbers were built</h2>
        <p className="text-slate-400 leading-relaxed mb-4">
          The SEC&apos;s XBRL <code className="inline-code">frames</code> API returns one
          reported fact for every filer in a period in a single request — roughly 6,000
          companies&apos; total assets in one call. That is what makes a market-wide screen
          possible without a data vendor, and because SEC filings are US government works in
          the public domain, the results can be published here without the licence
          restrictions that every free price API imposes.
        </p>
        <p className="text-slate-400 leading-relaxed mb-4">{data.method.matching}</p>
        <p className="text-slate-400 leading-relaxed mb-4">
          Companies were checked against their filings before publication. Apple&apos;s fiscal
          2024 total assets resolve to $364.98bn against $352.58bn a year earlier, a 3.5%
          asset growth, and accruals of −6.8% from $93.7bn of net income against $118.3bn of
          operating cash flow — each matching the 10-K. Microsoft resolves to its June year
          end, NVIDIA and Walmart to their January ones.
        </p>
        <div className="rounded-xl border border-[hsl(215,40%,18%)] bg-[hsl(220,55%,9%)] p-5">
          <h3 className="text-sm font-semibold uppercase tracking-wide text-[hsl(215,20%,60%)] mb-3">
            Coverage, and what was excluded
          </h3>
          <p className="text-sm text-slate-400 mb-3">
            {data.universe.filers_reporting_annual_flows.toLocaleString()} filers reported an
            annual income statement for the period.{' '}
            {data.universe.screened.toLocaleString()} survived to the screen. Every exclusion
            is counted rather than silently dropped:
          </p>
          <table className="w-full text-sm">
            <tbody>
              {dropped.map(([k, v]) => (
                <tr key={k} className="border-t border-[hsl(215,40%,12%)]">
                  <td className="py-1.5 font-mono text-xs text-slate-400">{k.replace(/_/g, ' ')}</td>
                  <td className="py-1.5 text-right font-mono tabular-nums text-slate-300">
                    {v.toLocaleString()}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
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
        <h2 className="text-2xl font-bold text-white mb-4">Get the data</h2>
        <p className="text-slate-400 leading-relaxed mb-4">
          The complete artefact — all {data.universe.screened.toLocaleString()} companies with
          every field, the provenance block and the exclusion counts — is served as a static
          JSON file. It is public-domain source data, so use it however you like.
        </p>
        <a
          href="/data/edgar-screener.json"
          className="inline-block rounded-lg bg-indigo-600 px-5 py-3 text-white transition-colors hover:bg-indigo-500"
        >
          Download edgar-screener.json
        </a>
        <p className="mt-4 text-xs text-[hsl(215,20%,45%)]">
          Generated {data.generated_at} from {data.source.name}. {data.source.licence} The table
          above embeds the {Math.min(EMBEDDED_ROWS, rows.length).toLocaleString()} largest filers
          by total assets; the download has all of them.
        </p>
      </section>

      <section className="max-w-3xl mt-14">
        <h2 className="text-2xl font-bold text-white mb-6">Related tools</h2>
        <div className="grid gap-4 sm:grid-cols-2">
          <Link href="/scanner" className="group rounded-xl border border-[hsl(215,40%,18%)] bg-[hsl(220,55%,9%)] p-5 transition-all hover:border-indigo-500/60 hover:bg-[hsl(220,55%,11%)]">
            <h3 className="text-lg font-semibold text-white group-hover:text-indigo-400 transition-colors">Seasonality Screener</h3>
            <p className="mt-1.5 text-sm text-slate-400">Multiple-testing-corrected seasonal effects.</p>
          </Link>
          <Link href="/tools/max-sharpe" className="group rounded-xl border border-[hsl(215,40%,18%)] bg-[hsl(220,55%,9%)] p-5 transition-all hover:border-indigo-500/60 hover:bg-[hsl(220,55%,11%)]">
            <h3 className="text-lg font-semibold text-white group-hover:text-indigo-400 transition-colors">Max Sharpe Portfolio</h3>
            <p className="mt-1.5 text-sm text-slate-400">Closed-form tangency portfolio weights.</p>
          </Link>
          <Link href="/data-vendors" className="group rounded-xl border border-[hsl(215,40%,18%)] bg-[hsl(220,55%,9%)] p-5 transition-all hover:border-indigo-500/60 hover:bg-[hsl(220,55%,11%)]">
            <h3 className="text-lg font-semibold text-white group-hover:text-indigo-400 transition-colors">Market Data API Benchmark</h3>
            <p className="mt-1.5 text-sm text-slate-400">Measured coverage and licence terms by vendor.</p>
          </Link>
          <Link href="/tools" className="group rounded-xl border border-[hsl(215,40%,18%)] bg-[hsl(220,55%,9%)] p-5 transition-all hover:border-indigo-500/60 hover:bg-[hsl(220,55%,11%)]">
            <h3 className="text-lg font-semibold text-white group-hover:text-indigo-400 transition-colors">All Trading Tools</h3>
            <p className="mt-1.5 text-sm text-slate-400">Browse every free tool on QuantEngines.</p>
          </Link>
        </div>
      </section>

      <p className="max-w-3xl mt-14 text-xs text-[hsl(215,20%,45%)] leading-relaxed">
        Source: US Securities and Exchange Commission, EDGAR XBRL company facts. This page is
        not affiliated with or endorsed by the SEC. The signals shown are historical academic
        associations, not forecasts; nothing here is investment advice or a recommendation to
        buy or sell any security.
      </p>
    </div>
  )
}
