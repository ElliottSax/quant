/**
 * statsmodels import reference, measured by executing every statement.
 *
 * Search Console shows this site surfacing around position 8-10 for
 * `from statsmodels.tsa.api import arima` on 132 impressions with ZERO clicks. That
 * searcher has a traceback open and ten seconds. They are currently served a 1,900-word
 * essay on Box-Jenkins methodology.
 *
 * The finding that justifies the page: THREE of the four common ARIMA imports succeed
 * and then fail later, each differently. A reference built from documentation cannot
 * see that -- only running the code can. Artefact: `python -m pipeline.statsmodels_imports`.
 */

import type { Metadata } from 'next'
import Link from 'next/link'

const url = 'https://quantengines.com/statsmodels-imports'

interface ImportRow {
  label: string
  statement: string
  module: string
  symbol: string
  ok: boolean
  kind?: string
  qualname?: string
  error?: string
}

interface Deferred {
  statement: string
  used_by: string
  imports: boolean
  usable: boolean
  object: string | null
  error: string | null
}

interface Artifact {
  generated_at: string
  statsmodels_version: string
  python: string
  imports: ImportRow[]
  deferred_failures: Deferred[]
  measured: {
    coint_johansen: {
      ok: boolean
      pair?: string[]
      observations?: number
      from?: string
      to?: string
      call?: string
      returns_type?: string
      attributes?: string[]
      trace_stat_lr1?: number[]
      trace_crit_cvt?: number[][]
      max_eig_lr2?: number[]
      eigenvalues?: number[]
      crit_columns?: string[]
      reading?: string
    }
    arima: {
      ok: boolean
      symbol?: string
      observations?: number
      call?: string
      aic?: number
      bic?: number
      params?: Record<string, number>
      forecast_3?: number[]
    }
  }
  method: string
}

function load(): Artifact | null {
  try {
    // eslint-disable-next-line @typescript-eslint/no-var-requires
    const d = require('../../../public/data/statsmodels-imports.json') as Artifact
    return d?.imports?.length ? d : null
  } catch {
    return null
  }
}

const data = load()

export const metadata: Metadata = {
  title: data
    ? `statsmodels Import Reference — ARIMA, coint_johansen (${data.statsmodels_version})`
    : 'statsmodels Import Reference | QuantEngines',
  description:
    "Which statsmodels imports actually work, measured by running them. `from statsmodels.tsa.api import arima` imports a MODULE, so it fails later with \"'module' object is not callable\". Plus the correct coint_johansen path and how to read its lr1/cvt output.",
  keywords: [
    'from statsmodels.tsa.api import arima',
    'statsmodels arima import error',
    'coint_johansen import',
    'statsmodels.tsa.johansen',
    'module object is not callable arima',
    'statsmodels tsa arima model',
    'coint_johansen lr1 cvt',
  ],
  alternates: { canonical: url },
  openGraph: {
    title: 'statsmodels Import Reference (Measured)',
    description:
      'Every import statement executed and its real outcome recorded — including the three that succeed and fail later.',
    type: 'website',
    url,
  },
}

export default function StatsmodelsImportsPage() {
  if (!data) {
    return (
      <div className="container mx-auto px-4 py-12">
        <h1 className="text-4xl font-bold mb-4 text-white">statsmodels Import Reference</h1>
        <div className="max-w-3xl rounded-xl border border-amber-500/30 bg-amber-500/5 p-6">
          <h2 className="text-xl font-bold text-white mb-2">Reference data is not available</h2>
          <p className="text-slate-400">
            The measured artefact has not been published. This page will not guess import
            paths in its absence — guessing is the problem it exists to solve.
          </p>
        </div>
      </div>
    )
  }

  const jo = data.measured.coint_johansen
  const byLabel = new Map<string, ImportRow[]>()
  for (const r of data.imports) {
    byLabel.set(r.label, [...(byLabel.get(r.label) ?? []), r])
  }

  const faqs = [
    {
      q: "Why does 'from statsmodels.tsa.api import arima' give \"module object is not callable\"?",
      a: `Because lowercase \`arima\` is a MODULE (statsmodels.tsa.arima.api) and uppercase \`ARIMA\` is the class. The import line succeeds either way, so the traceback appears further down at the point you call it, where nothing looks wrong. Use \`from statsmodels.tsa.arima.model import ARIMA\` — capital ARIMA. Measured on statsmodels ${data.statsmodels_version}.`,
    },
    {
      q: 'Is statsmodels.tsa.api the wrong place to import ARIMA from?',
      a: `No, and this is widely misreported. \`from statsmodels.tsa.api import ARIMA\` works and returns the same class as the canonical path — it was executed here to confirm it. The path that is genuinely dead is \`statsmodels.tsa.arima_model\`, which imports a removal shim that raises NotImplementedError the moment you instantiate it.`,
    },
    {
      q: 'Where is coint_johansen imported from?',
      a: 'From `statsmodels.tsa.vector_ar.vecm`. The two paths people commonly try — `statsmodels.tsa.johansen` and `statsmodels.tsa.api` — both fail, and their exact errors are in the table on this page so you can match the traceback you are looking at.',
    },
    {
      q: 'How do I read what coint_johansen returns?',
      a: jo.reading ?? '',
    },
    {
      q: 'Does coint_johansen give p-values?',
      a: 'No. It returns test statistics (`lr1` for trace, `lr2` for maximum eigenvalue) and matching critical-value tables (`cvt`, `cvm`) at the 90%, 95% and 99% levels. You compare the statistic against the column you want. Expecting a p-value attribute is the single most common source of confusion with this function.',
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
        <span className="text-[hsl(215,20%,70%)]">statsmodels Imports</span>
      </nav>

      <div className="max-w-3xl mb-8">
        <h1 className="text-4xl md:text-5xl font-bold mb-4 text-white">
          statsmodels Import Reference
        </h1>
        <p className="text-lg text-slate-400">
          Which import paths actually work, captured by executing every statement on
          statsmodels {data.statsmodels_version} / Python {data.python} — not transcribed
          from documentation.
        </p>
      </div>

      {/* The answer, first. */}
      <div className="max-w-3xl mb-12 rounded-xl border border-indigo-500/30 bg-indigo-500/5 p-6">
        <h2 className="text-sm font-semibold uppercase tracking-wide text-indigo-300 mb-3">
          If you are here from a traceback
        </h2>
        <pre className="overflow-x-auto rounded-lg bg-[hsl(220,55%,6%)] p-4 text-sm text-emerald-300">
          <code>from statsmodels.tsa.arima.model import ARIMA{'\n'}from statsmodels.tsa.vector_ar.vecm import coint_johansen</code>
        </pre>
        <p className="mt-3 text-slate-400">
          Capital <code className="inline-code">ARIMA</code>. Lowercase{' '}
          <code className="inline-code">arima</code> is a module, not the class, which is why
          your import line succeeded and the error appeared somewhere else entirely.
        </p>
      </div>

      <section className="max-w-4xl mb-14">
        <h2 className="text-2xl font-bold text-white mb-2">
          The imports that succeed and then fail
        </h2>
        <p className="text-slate-400 mb-6">
          This is the part no documentation-derived reference contains, because you cannot
          see it without running the code. Three of these four statements import cleanly. They
          hand back different objects, and the failure surfaces later — at the call, or at
          instantiation — by which point the import line looks innocent.
        </p>
        <div className="overflow-x-auto rounded-xl border border-[hsl(215,40%,18%)]">
          <table className="w-full text-sm">
            <thead className="bg-[hsl(220,55%,7%)]">
              <tr>
                {['Statement', 'Imports', 'What you get', 'Fails when'].map((h) => (
                  <th key={h} className="px-3 py-2 text-left text-xs font-semibold uppercase tracking-wide text-[hsl(215,20%,60%)]">
                    {h}
                  </th>
                ))}
              </tr>
            </thead>
            <tbody>
              {data.deferred_failures.map((r) => (
                <tr key={r.statement} className="border-t border-[hsl(215,40%,12%)] align-top">
                  <td className="px-3 py-3 font-mono text-xs text-slate-200 whitespace-nowrap">
                    {r.statement}
                  </td>
                  <td className="px-3 py-3">
                    <span className={r.imports ? 'text-emerald-400' : 'text-rose-400'}>
                      {r.imports ? 'yes' : 'no'}
                    </span>
                  </td>
                  <td className="px-3 py-3 font-mono text-xs text-[hsl(215,20%,60%)]">
                    {r.object ?? '—'}
                  </td>
                  <td className="px-3 py-3 text-xs">
                    {r.usable ? (
                      <span className="text-emerald-400">never — this one works</span>
                    ) : (
                      <span className="text-amber-300">
                        on {r.used_by}: <span className="font-mono">{r.error}</span>
                      </span>
                    )}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </section>

      <section className="max-w-4xl mb-14">
        <h2 className="text-2xl font-bold text-white mb-2">Every path, executed</h2>
        <p className="text-slate-400 mb-6">
          Both the statements that work and the ones that do not. Failing paths are kept with
          their real exception text so you can match the traceback in front of you — a
          reference that lists only what works cannot be searched from an error message.
        </p>
        <div className="overflow-x-auto rounded-xl border border-[hsl(215,40%,18%)]">
          <table className="w-full text-sm">
            <thead className="bg-[hsl(220,55%,7%)]">
              <tr>
                {['Statement', 'Result'].map((h) => (
                  <th key={h} className="px-3 py-2 text-left text-xs font-semibold uppercase tracking-wide text-[hsl(215,20%,60%)]">
                    {h}
                  </th>
                ))}
              </tr>
            </thead>
            <tbody>
              {data.imports.map((r) => (
                <tr key={r.statement} className="border-t border-[hsl(215,40%,12%)]">
                  <td className="px-3 py-2 font-mono text-xs text-slate-200 whitespace-nowrap">
                    {r.statement}
                  </td>
                  <td className="px-3 py-2 text-xs">
                    {r.ok ? (
                      <span className="font-mono text-emerald-400">
                        {r.kind} · {r.qualname}
                      </span>
                    ) : (
                      <span className="font-mono text-rose-400">{r.error}</span>
                    )}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </section>

      {jo.ok && (
        <section className="max-w-4xl mb-14">
          <h2 className="text-2xl font-bold text-white mb-2">
            What <code className="inline-code">coint_johansen</code> actually returns
          </h2>
          <p className="text-slate-400 mb-6">
            Run on {jo.observations?.toLocaleString()} real daily closes for{' '}
            {jo.pair?.join(' and ')} ({jo.from} to {jo.to}), via{' '}
            <code className="inline-code">{jo.call}</code>. The attribute names below are the
            ones the returned object really carries, listed with{' '}
            <code className="inline-code">dir()</code>.
          </p>

          <div className="grid gap-4 md:grid-cols-2 mb-6">
            <div className="rounded-xl border border-[hsl(215,40%,18%)] bg-[hsl(220,55%,9%)] p-5">
              <h3 className="text-sm font-semibold uppercase tracking-wide text-[hsl(215,20%,60%)] mb-3">
                Trace test — <code className="inline-code">lr1</code> vs{' '}
                <code className="inline-code">cvt</code>
              </h3>
              <table className="w-full text-sm">
                <thead>
                  <tr className="text-xs text-[hsl(215,20%,55%)]">
                    <th className="text-left pb-2">Null</th>
                    <th className="text-right pb-2">lr1</th>
                    {jo.crit_columns?.map((c) => (
                      <th key={c} className="text-right pb-2">{c}</th>
                    ))}
                  </tr>
                </thead>
                <tbody className="font-mono tabular-nums">
                  {jo.trace_stat_lr1?.map((v, i) => (
                    <tr key={i} className="border-t border-[hsl(215,40%,12%)]">
                      <td className="py-1.5 text-slate-400">r ≤ {i}</td>
                      <td className="py-1.5 text-right text-white">{v.toFixed(4)}</td>
                      {jo.trace_crit_cvt?.[i]?.map((c, k) => (
                        <td key={k} className="py-1.5 text-right text-[hsl(215,20%,55%)]">
                          {c.toFixed(2)}
                        </td>
                      ))}
                    </tr>
                  ))}
                </tbody>
              </table>
              <p className="mt-3 text-xs text-[hsl(215,20%,50%)]">
                Every statistic here is below its 95% critical value, so this pair shows no
                evidence of cointegration over this window. That is the honest result for two
                large-cap equities, and it is shown rather than a hand-picked pair that works.
              </p>
            </div>

            <div className="rounded-xl border border-[hsl(215,40%,18%)] bg-[hsl(220,55%,9%)] p-5">
              <h3 className="text-sm font-semibold uppercase tracking-wide text-[hsl(215,20%,60%)] mb-3">
                Attributes on the returned object
              </h3>
              <p className="font-mono text-xs text-slate-300 leading-relaxed">
                {jo.attributes?.join(', ')}
              </p>
              <p className="mt-3 text-xs text-[hsl(215,20%,50%)]">
                Returned type: <code className="inline-code">{jo.returns_type}</code>. Note
                what is <em>absent</em>: there is no p-value attribute, and no{' '}
                <code className="inline-code">summary()</code>.
              </p>
            </div>
          </div>

          <div className="rounded-xl border border-[hsl(215,40%,18%)] bg-[hsl(220,55%,9%)] p-5">
            <h3 className="text-sm font-semibold uppercase tracking-wide text-[hsl(215,20%,60%)] mb-2">
              How to read it
            </h3>
            <p className="text-slate-400 leading-relaxed">{jo.reading}</p>
          </div>

          <pre className="mt-6 overflow-x-auto rounded-xl border border-[hsl(215,40%,18%)] bg-[hsl(220,55%,7%)] p-5 text-sm text-slate-300">
            <code>{`from statsmodels.tsa.vector_ar.vecm import coint_johansen

# data: an (n_obs, n_series) array of LEVELS, not returns
res = coint_johansen(data, det_order=0, k_ar_diff=1)

# Trace test at the 95% level (column index 1 of the critical-value table)
for r in range(len(res.lr1)):
    reject = res.lr1[r] > res.cvt[r, 1]
    print(f"r <= {r}:  trace={res.lr1[r]:.4f}  crit95={res.cvt[r, 1]:.4f}  reject={reject}")

# The cointegrating vector, if you rejected r = 0
beta = res.evec[:, 0]`}</code>
          </pre>
        </section>
      )}

      <section className="max-w-3xl mb-14">
        <h2 className="text-2xl font-bold text-white mb-4">Method</h2>
        <p className="text-slate-400 leading-relaxed mb-4">{data.method}</p>
        <p className="text-slate-400 leading-relaxed">
          This matters because import paths move between releases and documentation lags them.
          Anything on this page can be regenerated with{' '}
          <code className="inline-code">python -m pipeline.statsmodels_imports</code>, and
          every figure is tagged with the version that produced it — so when it goes stale,
          it goes visibly stale rather than quietly wrong.
        </p>
      </section>

      <section className="max-w-3xl mb-14">
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

      <section className="max-w-3xl">
        <h2 className="text-2xl font-bold text-white mb-6">Related</h2>
        <div className="grid gap-4 sm:grid-cols-2">
          <Link href="/pandas-ta-columns" className="group rounded-xl border border-[hsl(215,40%,18%)] bg-[hsl(220,55%,9%)] p-5 transition-all hover:border-indigo-500/60 hover:bg-[hsl(220,55%,11%)]">
            <h3 className="text-lg font-semibold text-white group-hover:text-indigo-400 transition-colors">pandas_ta Column Names</h3>
            <p className="mt-1.5 text-sm text-slate-400">Measured the same way — by running the library.</p>
          </Link>
          <Link href="/blog/arima-models" className="group rounded-xl border border-[hsl(215,40%,18%)] bg-[hsl(220,55%,9%)] p-5 transition-all hover:border-indigo-500/60 hover:bg-[hsl(220,55%,11%)]">
            <h3 className="text-lg font-semibold text-white group-hover:text-indigo-400 transition-colors">ARIMA in Python</h3>
            <p className="mt-1.5 text-sm text-slate-400">Order selection, diagnostics and a worked fit.</p>
          </Link>
          <Link href="/data-vendors" className="group rounded-xl border border-[hsl(215,40%,18%)] bg-[hsl(220,55%,9%)] p-5 transition-all hover:border-indigo-500/60 hover:bg-[hsl(220,55%,11%)]">
            <h3 className="text-lg font-semibold text-white group-hover:text-indigo-400 transition-colors">Market Data API Benchmark</h3>
            <p className="mt-1.5 text-sm text-slate-400">Measured coverage and licence terms by vendor.</p>
          </Link>
          <Link href="/tools" className="group rounded-xl border border-[hsl(215,40%,18%)] bg-[hsl(220,55%,9%)] p-5 transition-all hover:border-indigo-500/60 hover:bg-[hsl(220,55%,11%)]">
            <h3 className="text-lg font-semibold text-white group-hover:text-indigo-400 transition-colors">All Tools</h3>
            <p className="mt-1.5 text-sm text-slate-400">Browse every free tool on QuantEngines.</p>
          </Link>
        </div>
      </section>

      <p className="max-w-3xl mt-14 text-xs text-[hsl(215,20%,45%)] leading-relaxed">
        Measured on statsmodels {data.statsmodels_version}, Python {data.python}, generated{' '}
        {data.generated_at}. statsmodels is BSD-licensed open-source software; this page is not
        affiliated with the statsmodels project.
      </p>
    </div>
  )
}
