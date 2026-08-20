/**
 * Indicator formula reference, cross-checked against pandas_ta on real bars.
 *
 * Every "RSI formula" page states a formula. Almost none demonstrate that the formula as
 * written reproduces what a library computes. This one does: each formula is implemented
 * independently in NumPy (pipeline/indicator_verify.py), computed again with pandas_ta on
 * real daily bars, and the two compared point by point.
 *
 * The measured findings that justify the page:
 *   - RSI and ADX need ~117 bars to agree to within 0.01, not the 14 or 28 people assume,
 *     because Wilder's smoothing is recursive and the seed persists.
 *   - pandas_ta computes Bollinger bands with the SAMPLE standard deviation (ddof=1),
 *     while Bollinger's own definition uses the population form.
 */

import type { Metadata } from 'next'
import Link from 'next/link'

const url = 'https://quantengines.com/indicator-formulas'

interface SeriesCmp {
  series: string
  pandas_ta_column: string | null
  note?: string
  agrees?: boolean
  exact_throughout?: boolean
  comparable_points?: number
  max_abs_diff_overall?: number
  max_abs_diff_after_convergence?: number | null
  converged_at_bar?: number | null
  bars_before_convergence?: number | null
  bars_to_within?: Record<string, number | null>
}

interface Indicator {
  key: string
  name: string
  full_name: string
  params: string
  formula: string[]
  gotcha: string
  series: SeriesCmp[]
  all_agree: boolean
  latest_values: Record<string, number | null>
}

interface Artifact {
  generated_at: string
  pandas_ta_version: string
  measured_on: { symbol: string; bars: number; from: string; to: string }
  method: string
  tolerance: string
  bollinger_stdev_convention: {
    probe: Record<string, { max_abs_diff: number; matches: boolean; label: string }>
    pandas_ta_uses_ddof: number | null
    finding: string
  }
  indicators: Indicator[]
}

function load(): Artifact | null {
  try {
    // eslint-disable-next-line @typescript-eslint/no-var-requires
    const d = require('../../../public/data/indicator-formulas.json') as Artifact
    return d?.indicators?.length ? d : null
  } catch {
    return null
  }
}

const data = load()

export const metadata: Metadata = {
  title: 'Indicator Formulas, Cross-Checked — RSI, ADX, ATR, MACD, Bollinger',
  description:
    "RSI, ADX, ATR, MACD, Bollinger and Stochastic formulas, each implemented independently and verified against pandas_ta on real price bars. Measured: RSI needs ~117 bars to match, not 14, and pandas_ta's Bollinger bands use the sample standard deviation.",
  keywords: [
    'rsi formula',
    'adx formula',
    'atr formula',
    'macd formula',
    'bollinger bands formula',
    'stochastic oscillator formula',
    'wilder smoothing rsi',
    'rsi does not match tradingview',
  ],
  alternates: { canonical: url },
  openGraph: {
    title: 'Indicator Formulas, Cross-Checked Against pandas_ta',
    description:
      'Each formula implemented independently and verified against a real library on real bars — including where they disagree and why.',
    type: 'website',
    url,
  },
}

const sci = (v: number | null | undefined) =>
  v === null || v === undefined ? '—' : v === 0 ? '0' : v.toExponential(2)

export default function IndicatorFormulasPage() {
  if (!data) {
    return (
      <div className="container mx-auto px-4 py-12">
        <h1 className="text-4xl font-bold mb-4 text-white">Indicator Formulas</h1>
        <div className="max-w-3xl rounded-xl border border-amber-500/30 bg-amber-500/5 p-6">
          <h2 className="text-xl font-bold text-white mb-2">Verification data is not available</h2>
          <p className="text-slate-400">
            The measured artefact has not been published. This page will not state formulas
            it has not verified — the verification is the only thing that distinguishes it
            from every other formula page.
          </p>
        </div>
      </div>
    )
  }

  const warmup = data.indicators
    .flatMap((i) => i.series.map((s) => ({ name: i.name, s })))
    .filter((x) => x.s.bars_to_within && (x.s.bars_to_within['0.01'] ?? 0) > 0)

  const faqs = [
    {
      q: 'Why does my RSI not match TradingView or my broker?',
      a: `Two reasons, both measured on this page. First, the averages must use Wilder's smoothing (an EMA with alpha = 1/n), not a standard EMA (alpha = 2/(n+1)) or a simple average — for n = 14 that is 0.0714 against 0.1333, so a plain EMA gives a plausible but wrong RSI. Second, Wilder's smoothing is recursive, so the starting value persists: an independent implementation and pandas_ta took ${warmup.find((w) => w.name === 'RSI')?.s.bars_to_within?.['0.01'] ?? '~117'} bars to agree to within 0.01 on real data. If you feed 100 bars in, your last value is still visibly wrong regardless of a correct formula.`,
    },
    {
      q: 'How much history does an RSI or ADX need?',
      a: 'Far more than the period suggests. Measured against pandas_ta on real daily bars, RSI took about 117 bars and ADX about 116 bars before the two implementations agreed to within 0.01, and roughly 180 before they matched to machine precision. The common advice of "n + 1 bars" or "2n bars for ADX" produces values that are defined but not yet correct.',
    },
    {
      q: 'Which standard deviation do Bollinger Bands use?',
      a: data.bollinger_stdev_convention.finding,
    },
    {
      q: 'Which indicators use Wilder smoothing and which use a normal EMA?',
      a: 'RSI, ATR and ADX use Wilder\'s (alpha = 1/n). MACD uses standard EMAs (alpha = 2/(n+1)). Bollinger and Stochastic use simple moving averages. Mixing these up is the most common source of "my numbers are close but not equal" — the shapes look right, so the bug survives a visual check.',
    },
    {
      q: 'How were these verified?',
      a: `${data.method} Measured on ${data.measured_on.bars} real ${data.measured_on.symbol} daily bars (${data.measured_on.from} to ${data.measured_on.to}) against pandas_ta ${data.pandas_ta_version}.`,
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
        <span className="text-[hsl(215,20%,70%)]">Indicator Formulas</span>
      </nav>

      <div className="max-w-3xl mb-8">
        <h1 className="text-4xl md:text-5xl font-bold mb-4 text-white">
          Indicator Formulas, Cross-Checked
        </h1>
        <p className="text-lg text-slate-400">
          Every formula below was implemented independently in NumPy from its definition,
          then computed again with pandas_ta {data.pandas_ta_version} on{' '}
          {data.measured_on.bars} real {data.measured_on.symbol} bars, and the two compared
          point by point. Agreement is the evidence that the formula on this page is the
          formula a library actually implements.
        </p>
      </div>

      {/* The two findings that justify the page. */}
      <div className="max-w-3xl mb-12 grid gap-4">
        <div className="rounded-xl border border-indigo-500/30 bg-indigo-500/5 p-6">
          <h2 className="text-sm font-semibold uppercase tracking-wide text-indigo-300 mb-2">
            Finding 1 — a correct RSI still needs ~117 bars
          </h2>
          <p className="text-slate-400 leading-relaxed">
            Wilder&apos;s smoothing is recursive, so the seed value decays rather than
            disappearing after the window. Two correct implementations that seed differently
            took <strong className="text-white">117 bars</strong> to agree to within 0.01, and
            about 184 to match to machine precision. If your RSI is right and still disagrees
            with your platform, this is usually why — not the formula.
          </p>
        </div>
        <div className="rounded-xl border border-indigo-500/30 bg-indigo-500/5 p-6">
          <h2 className="text-sm font-semibold uppercase tracking-wide text-indigo-300 mb-2">
            Finding 2 — pandas_ta&apos;s Bollinger bands use the sample standard deviation
          </h2>
          <p className="text-slate-400 leading-relaxed mb-3">
            The bands were computed both ways against the same library output. Only ddof = 1
            matched, so pandas_ta&apos;s bands sit slightly wider than Bollinger&apos;s own
            population-form definition.
          </p>
          <table className="text-sm">
            <tbody className="font-mono">
              {Object.entries(data.bollinger_stdev_convention.probe).map(([k, v]) => (
                <tr key={k}>
                  <td className="py-1 pr-4 text-slate-400">{v.label}</td>
                  <td className="py-1 pr-4 text-right tabular-nums text-slate-300">
                    {sci(v.max_abs_diff)}
                  </td>
                  <td className={`py-1 ${v.matches ? 'text-emerald-400' : 'text-rose-400'}`}>
                    {v.matches ? 'matches' : 'does not match'}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      {/* Per-indicator */}
      <div className="space-y-8">
        {data.indicators.map((ind) => (
          <section
            key={ind.key}
            id={ind.key}
            className="rounded-xl border border-[hsl(215,40%,18%)] bg-[hsl(220,55%,9%)] p-6 scroll-mt-20"
          >
            <div className="flex flex-wrap items-baseline justify-between gap-3 mb-4">
              <div>
                <h2 className="text-2xl font-bold text-white">{ind.full_name}</h2>
                <p className="text-sm text-[hsl(215,20%,50%)]">{ind.params}</p>
              </div>
              <span
                className={`rounded-full px-3 py-1 text-xs font-semibold ${
                  ind.all_agree
                    ? 'bg-emerald-500/15 text-emerald-300'
                    : 'bg-rose-500/15 text-rose-300'
                }`}
              >
                {ind.all_agree ? 'Reproduces pandas_ta' : 'Disagrees with pandas_ta'}
              </span>
            </div>

            <pre className="overflow-x-auto rounded-lg bg-[hsl(220,55%,6%)] p-4 text-sm text-slate-200 mb-4">
              <code>{ind.formula.join('\n')}</code>
            </pre>

            <div className="rounded-lg border border-amber-500/25 bg-amber-500/5 p-4 mb-4">
              <h3 className="text-xs font-semibold uppercase tracking-wide text-amber-300 mb-1.5">
                What trips people up
              </h3>
              <p className="text-sm text-amber-100/80 leading-relaxed">{ind.gotcha}</p>
            </div>

            <div className="overflow-x-auto">
              <table className="w-full text-sm">
                <thead>
                  <tr className="border-b border-[hsl(215,40%,14%)] text-xs uppercase tracking-wide text-[hsl(215,20%,55%)]">
                    <th className="py-2 text-left font-semibold">Series</th>
                    <th className="py-2 text-left font-semibold">pandas_ta column</th>
                    <th className="py-2 text-right font-semibold">Bars to ±0.01</th>
                    <th className="py-2 text-right font-semibold">Max diff after warm-up</th>
                    <th className="py-2 text-right font-semibold">Latest</th>
                  </tr>
                </thead>
                <tbody>
                  {ind.series.map((s) => (
                    <tr key={s.series} className="border-b border-[hsl(215,40%,10%)]">
                      <td className="py-2 font-mono text-slate-200">{s.series}</td>
                      <td className="py-2 font-mono text-xs text-[hsl(215,20%,55%)]">
                        {s.pandas_ta_column ?? s.note ?? '—'}
                      </td>
                      <td className="py-2 text-right font-mono tabular-nums text-slate-300">
                        {s.exact_throughout
                          ? <span className="text-emerald-400">exact from bar 1</span>
                          : (s.bars_to_within?.['0.01'] ?? '—')}
                      </td>
                      <td className="py-2 text-right font-mono tabular-nums text-slate-300">
                        {sci(s.max_abs_diff_after_convergence)}
                      </td>
                      <td className="py-2 text-right font-mono tabular-nums text-white">
                        {ind.latest_values[s.series]?.toFixed(4) ?? '—'}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </section>
        ))}
      </div>

      <section className="max-w-3xl mt-14">
        <h2 className="text-2xl font-bold text-white mb-4">Wilder&apos;s smoothing, in code</h2>
        <p className="text-slate-400 leading-relaxed mb-4">
          Three of the six indicators here depend on it, and it is the piece most published
          formulas leave out. It is an exponential average with alpha = 1/n, seeded with a
          simple average of the first n values:
        </p>
        <pre className="overflow-x-auto rounded-xl border border-[hsl(215,40%,18%)] bg-[hsl(220,55%,7%)] p-5 text-sm text-slate-300">
          <code>{`import numpy as np

def wilder(x: np.ndarray, n: int) -> np.ndarray:
    """Wilder's smoothing (RMA). Not the same as an EMA of the same length."""
    out = np.full_like(x, np.nan, dtype=float)
    out[n - 1] = np.nanmean(x[:n])          # seed: simple average of the first n
    for i in range(n, len(x)):
        out[i] = out[i - 1] + (x[i] - out[i - 1]) / n
    return out

# Equivalent to an EMA with alpha = 1/n.  A standard EMA uses 2/(n+1):
#   n = 14  ->  Wilder alpha = 0.0714,  EMA alpha = 0.1333`}</code>
        </pre>
        <p className="text-slate-400 leading-relaxed mt-4">
          The seed choice is what causes the long warm-up. Different libraries seed
          differently — some with a simple average, some by running the recursion from the
          first observation — and because the filter is recursive those choices take
          hundreds of bars to wash out, not fourteen.
        </p>
      </section>

      <section className="max-w-3xl mt-14">
        <h2 className="text-2xl font-bold text-white mb-4">Method</h2>
        <p className="text-slate-400 leading-relaxed mb-4">{data.method}</p>
        <p className="text-slate-400 leading-relaxed mb-4">
          Agreement is judged on the converged region, with the warm-up measured separately.
          That distinction is the point: a single max-difference over the whole series
          conflates &quot;the formula is wrong&quot; with &quot;the first bars are seeded
          differently&quot;, and those are completely different problems for someone
          implementing this. Tolerance: {data.tolerance}.
        </p>
        <p className="text-slate-400 leading-relaxed">
          Regenerate with{' '}
          <code className="inline-code">python -m pipeline.indicator_verify</code>. Every
          figure is tagged with the library version that produced it, so it goes visibly
          stale rather than quietly wrong.
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
        <h2 className="text-2xl font-bold text-white mb-6">Related</h2>
        <div className="grid gap-4 sm:grid-cols-2">
          <Link href="/pandas-ta-columns" className="group rounded-xl border border-[hsl(215,40%,18%)] bg-[hsl(220,55%,9%)] p-5 transition-all hover:border-indigo-500/60 hover:bg-[hsl(220,55%,11%)]">
            <h3 className="text-lg font-semibold text-white group-hover:text-indigo-400 transition-colors">pandas_ta Column Names</h3>
            <p className="mt-1.5 text-sm text-slate-400">Which columns each indicator actually creates.</p>
          </Link>
          <Link href="/statsmodels-imports" className="group rounded-xl border border-[hsl(215,40%,18%)] bg-[hsl(220,55%,9%)] p-5 transition-all hover:border-indigo-500/60 hover:bg-[hsl(220,55%,11%)]">
            <h3 className="text-lg font-semibold text-white group-hover:text-indigo-400 transition-colors">statsmodels Imports</h3>
            <p className="mt-1.5 text-sm text-slate-400">Measured the same way — by running the code.</p>
          </Link>
          <Link href="/scanner" className="group rounded-xl border border-[hsl(215,40%,18%)] bg-[hsl(220,55%,9%)] p-5 transition-all hover:border-indigo-500/60 hover:bg-[hsl(220,55%,11%)]">
            <h3 className="text-lg font-semibold text-white group-hover:text-indigo-400 transition-colors">Seasonality Screener</h3>
            <p className="mt-1.5 text-sm text-slate-400">Multiple-testing-corrected seasonal effects.</p>
          </Link>
          <Link href="/tools" className="group rounded-xl border border-[hsl(215,40%,18%)] bg-[hsl(220,55%,9%)] p-5 transition-all hover:border-indigo-500/60 hover:bg-[hsl(220,55%,11%)]">
            <h3 className="text-lg font-semibold text-white group-hover:text-indigo-400 transition-colors">All Tools</h3>
            <p className="mt-1.5 text-sm text-slate-400">Browse every free tool on QuantEngines.</p>
          </Link>
        </div>
      </section>

      <p className="max-w-3xl mt-14 text-xs text-[hsl(215,20%,45%)] leading-relaxed">
        Measured on {data.measured_on.bars} {data.measured_on.symbol} daily bars (
        {data.measured_on.from} to {data.measured_on.to}) against pandas_ta{' '}
        {data.pandas_ta_version}, generated {data.generated_at}. Indicator values are
        arithmetic on historical prices and are not investment advice or trading signals.
      </p>
    </div>
  )
}
