/**
 * backtrader vs vectorbt, measured by running the same strategy through both.
 *
 * This is a query the site already surfaces for. Every article answering it compares
 * feature lists and speed; none answers the question that decides whether a backtest
 * means anything — do they agree on the result.
 *
 * The measured answer is that they agree to the cent, but only once three defaults are
 * pinned, and the decomposition shows sizing accounts for ~98% of the divergence and
 * fill timing for ~2%. Artefact: `python -m pipeline.framework_bench`.
 */

import type { Metadata } from 'next'
import Link from 'next/link'

const url = 'https://quantengines.com/backtrader-vs-vectorbt'

interface Step {
  size: number
  fill: string
  final_value: number
  total_return_pct: number
  n_trades_closed: number
}

interface Artifact {
  generated_at: string
  versions: Record<string, string>
  setup: {
    symbol: string; bars: number; from: string; to: string; strategy: string
    size_shares: number; initial_cash: number; commission: number; repeats: number
  }
  pinned: Record<string, string>
  results: {
    vectorbt: {
      final_value: number; total_return_pct: number
      n_trades_total: number; n_trades_closed: number; n_trades_open: number
      seconds_median: number; seconds_min: number
    }
    backtrader: {
      final_value: number; total_return_pct: number
      n_trades_closed: number; n_trades_open: number
      seconds_median: number; seconds_min: number
    }
  }
  decomposition: {
    steps: Record<string, Step>
    sizing_effect_pp: number
    fill_timing_effect_pp: number
    sizing_share_of_gap: number
    explanation: string
  }
  comparison: {
    final_value_diff: number
    final_value_rel_diff: number
    closed_trade_count_match: boolean
    agree: boolean
    speed_ratio_backtrader_over_vectorbt: number
  }
  caveats: Record<string, string>
}

function load(): Artifact | null {
  try {
    // eslint-disable-next-line @typescript-eslint/no-var-requires
    const d = require('../../../public/data/framework-bench.json') as Artifact
    return d?.results?.vectorbt ? d : null
  } catch {
    return null
  }
}

const data = load()

export const metadata: Metadata = {
  title: 'backtrader vs vectorbt — Do They Agree? (Measured)',
  description:
    'The same SMA crossover on the same 2,000 bars through backtrader and vectorbt. They agree to the cent — but only after pinning three defaults. Measured: position sizing causes 98% of the divergence, fill timing 2%, and vectorbt runs ~127× faster.',
  keywords: [
    'backtrader vs vectorbt',
    'vectorbt vs backtrader speed',
    'backtesting library comparison python',
    'backtrader cheat on close',
    'vectorbt from_signals size',
    'why do my backtest results differ',
  ],
  alternates: { canonical: url },
  openGraph: {
    title: 'backtrader vs vectorbt — Do They Agree?',
    description:
      'Same strategy, same bars, both libraries. Measured agreement, measured speed, and a decomposition of what actually causes backtests to differ.',
    type: 'website',
    url,
  },
}

const money = (v: number) => `$${v.toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}`

export default function BacktraderVsVectorbtPage() {
  if (!data) {
    return (
      <div className="container mx-auto px-4 py-12">
        <h1 className="text-4xl font-bold mb-4 text-white">backtrader vs vectorbt</h1>
        <div className="max-w-3xl rounded-xl border border-amber-500/30 bg-amber-500/5 p-6">
          <h2 className="text-xl font-bold text-white mb-2">Benchmark data is not available</h2>
          <p className="text-slate-400">
            The measured artefact has not been published. This page will not compare the two
            libraries from documentation — running them is the only thing that makes the
            comparison worth reading.
          </p>
        </div>
      </div>
    )
  }

  const { results: r, decomposition: dc, comparison: cmp, setup } = data
  const steps: Array<[string, string, Step]> = [
    ['defaults', 'backtrader defaults', dc.steps.defaults],
    ['size_pinned_only', 'Sizing pinned only', dc.steps.size_pinned_only],
    ['fully_pinned', 'Sizing + fills pinned', dc.steps.fully_pinned],
  ]

  const faqs = [
    {
      q: 'Do backtrader and vectorbt give the same result?',
      a: `On this test, yes — exactly. Both report ${money(r.vectorbt.final_value)} final equity and ${r.vectorbt.n_trades_closed} closed trades on the same ${setup.bars.toLocaleString()} bars, a relative difference of ${cmp.final_value_rel_diff.toExponential(1)}. But that agreement is manufactured: it required pinning position sizing, fill timing and commission. Run either library on its own defaults and the results do not match.`,
    },
    {
      q: 'Why do my backtest results differ between libraries?',
      a: `Almost always position sizing, not the engine. Measured here by changing one default at a time: sizing accounted for ${dc.sizing_effect_pp.toFixed(2)} percentage points of the gap (${(dc.sizing_share_of_gap * 100).toFixed(0)}%) and fill timing for ${dc.fill_timing_effect_pp.toFixed(2)}pp. backtrader's default stake is 1 share; vectorbt's default invests available cash. Comparing those is comparing two different strategies, not two engines.`,
    },
    {
      q: 'How much faster is vectorbt?',
      a: `About ${cmp.speed_ratio_backtrader_over_vectorbt.toFixed(0)}× on this test — ${(r.vectorbt.seconds_median * 1000).toFixed(1)} ms against ${(r.backtrader.seconds_median * 1000).toFixed(0)} ms, median of ${setup.repeats} runs. That is a property of the architecture: vectorbt is vectorised over NumPy arrays while backtrader steps bar by bar. The gap widens with more bars and more parameter combinations, which is why vectorbt is the usual choice for parameter sweeps.`,
    },
    {
      q: 'Which should I use?',
      a: 'They are not really competing for the same job. vectorbt is far faster and suits vectorised signal research and large parameter sweeps. backtrader is event-driven, which lets a strategy react bar by bar and express order types, broker behaviour and portfolio logic that a vectorised engine cannot represent naturally. Speed is only a tiebreak once both can express the strategy you actually want to test.',
    },
    {
      q: 'Why did the trade counts look different at first?',
      a: data.caveats.trade_count_definition,
    },
    {
      q: 'What does "cheat on close" mean in backtrader?',
      a: 'It makes an order fill at the close of the bar that generated the signal, instead of the open of the next bar. It is set with cerebro.broker.set_coc(True). It is used here only to match vectorbt\'s convention so the two are comparable — it is not a realistic execution assumption, since it fills at a price known only after the bar has closed.',
    },
  ]

  const faqSchema = {
    '@context': 'https://schema.org',
    '@type': 'FAQPage',
    mainEntity: faqs.map(f => ({
      '@type': 'Question', name: f.q,
      acceptedAnswer: { '@type': 'Answer', text: f.a },
    })),
  }

  return (
    <div className="container mx-auto px-4 py-12">
      <script type="application/ld+json" dangerouslySetInnerHTML={{ __html: JSON.stringify(faqSchema) }} />

      <nav className="text-sm text-[hsl(215,20%,55%)] mb-6">
        <Link href="/tools" className="hover:text-indigo-400">Tools</Link>
        <span className="mx-2">/</span>
        <span className="text-[hsl(215,20%,70%)]">backtrader vs vectorbt</span>
      </nav>

      <div className="max-w-3xl mb-8">
        <h1 className="text-4xl md:text-5xl font-bold mb-4 text-white">
          backtrader vs vectorbt: do they agree?
        </h1>
        <p className="text-lg text-slate-400">
          Comparisons of these two libraries list features and quote speed. Neither answers
          the question that decides whether a backtest means anything. So the same strategy
          was run on the same {setup.bars.toLocaleString()} bars through both, and the
          results compared.
        </p>
      </div>

      {/* The answer */}
      <div className="max-w-3xl mb-12 rounded-xl border border-emerald-500/30 bg-emerald-500/5 p-6">
        <h2 className="text-sm font-semibold uppercase tracking-wide text-emerald-300 mb-3">
          The answer
        </h2>
        <p className="text-slate-300 leading-relaxed mb-4">
          They agree <strong className="text-white">exactly</strong> — both report{' '}
          <span className="font-mono text-white">{money(r.vectorbt.final_value)}</span> and{' '}
          {r.vectorbt.n_trades_closed} closed trades, a relative difference of{' '}
          {cmp.final_value_rel_diff.toExponential(1)}.
        </p>
        <p className="text-slate-400 leading-relaxed">
          That agreement is manufactured. It required pinning three defaults, and the
          practical lesson is the opposite of reassuring: a backtest result is a property of
          the harness as much as of the strategy. On their own defaults, the same strategy
          returns{' '}
          <span className="font-mono text-amber-300">{dc.steps.defaults.total_return_pct.toFixed(2)}%</span> or{' '}
          <span className="font-mono text-emerald-300">{dc.steps.fully_pinned.total_return_pct.toFixed(2)}%</span>.
        </p>
      </div>

      {/* Decomposition — the real finding */}
      <section className="mb-14">
        <h2 className="text-2xl font-bold text-white mb-2">What actually causes the difference</h2>
        <p className="text-slate-400 mb-6 max-w-3xl">
          Changing one default at a time, in backtrader, on identical bars. This
          decomposition matters: the end-to-end gap looks like an engine disagreement and is
          almost entirely a position-sizing setting.
        </p>
        <div className="overflow-x-auto rounded-xl border border-[hsl(215,40%,18%)]">
          <table className="w-full text-sm">
            <thead className="bg-[hsl(220,55%,7%)]">
              <tr>
                {['Configuration', 'Size', 'Fill', 'Final equity', 'Return', 'Trades'].map((h, i) => (
                  <th key={h} className={`px-3 py-2 text-xs font-semibold uppercase tracking-wide text-[hsl(215,20%,60%)] whitespace-nowrap ${i === 0 ? 'text-left' : 'text-right'}`}>
                    {h}
                  </th>
                ))}
              </tr>
            </thead>
            <tbody>
              {steps.map(([key, label, s]) => (
                <tr key={key} className="border-t border-[hsl(215,40%,12%)]">
                  <td className="px-3 py-3 text-slate-200">{label}</td>
                  <td className="px-3 py-3 text-right font-mono tabular-nums text-slate-300">{s.size}</td>
                  <td className="px-3 py-3 text-right text-xs text-[hsl(215,20%,55%)] whitespace-nowrap">{s.fill}</td>
                  <td className="px-3 py-3 text-right font-mono tabular-nums text-slate-200">{money(s.final_value)}</td>
                  <td className={`px-3 py-3 text-right font-mono tabular-nums ${key === 'defaults' ? 'text-amber-300' : 'text-emerald-300'}`}>
                    {s.total_return_pct.toFixed(2)}%
                  </td>
                  <td className="px-3 py-3 text-right font-mono tabular-nums text-[hsl(215,20%,55%)]">{s.n_trades_closed}</td>
                </tr>
              ))}
              <tr className="border-t border-[hsl(215,40%,18%)] bg-[hsl(220,55%,7%)]">
                <td className="px-3 py-3 text-slate-200">vectorbt, same pinned settings</td>
                <td className="px-3 py-3 text-right font-mono tabular-nums text-slate-300">{setup.size_shares}</td>
                <td className="px-3 py-3 text-right text-xs text-[hsl(215,20%,55%)]">signal bar close</td>
                <td className="px-3 py-3 text-right font-mono tabular-nums text-white">{money(r.vectorbt.final_value)}</td>
                <td className="px-3 py-3 text-right font-mono tabular-nums text-emerald-300">{r.vectorbt.total_return_pct.toFixed(2)}%</td>
                <td className="px-3 py-3 text-right font-mono tabular-nums text-[hsl(215,20%,55%)]">{r.vectorbt.n_trades_closed}</td>
              </tr>
            </tbody>
          </table>
        </div>
        <div className="mt-5 grid gap-4 sm:grid-cols-3 max-w-3xl">
          <div className="rounded-xl border border-[hsl(215,40%,18%)] bg-[hsl(220,55%,9%)] p-5">
            <div className="font-mono text-2xl font-bold tabular-nums text-white">
              {dc.sizing_effect_pp > 0 ? '+' : ''}{dc.sizing_effect_pp.toFixed(2)}pp
            </div>
            <div className="mt-1 text-xs text-[hsl(215,20%,55%)]">from position sizing</div>
          </div>
          <div className="rounded-xl border border-[hsl(215,40%,18%)] bg-[hsl(220,55%,9%)] p-5">
            <div className="font-mono text-2xl font-bold tabular-nums text-white">
              {dc.fill_timing_effect_pp > 0 ? '+' : ''}{dc.fill_timing_effect_pp.toFixed(2)}pp
            </div>
            <div className="mt-1 text-xs text-[hsl(215,20%,55%)]">from fill timing</div>
          </div>
          <div className="rounded-xl border border-[hsl(215,40%,18%)] bg-[hsl(220,55%,9%)] p-5">
            <div className="font-mono text-2xl font-bold tabular-nums text-white">
              {(dc.sizing_share_of_gap * 100).toFixed(0)}%
            </div>
            <div className="mt-1 text-xs text-[hsl(215,20%,55%)]">of the gap is sizing</div>
          </div>
        </div>
        <p className="mt-4 max-w-3xl text-sm text-[hsl(215,20%,50%)]">{dc.explanation}</p>
      </section>

      {/* Speed, second */}
      <section className="mb-14">
        <h2 className="text-2xl font-bold text-white mb-2">Speed</h2>
        <p className="text-slate-400 mb-5 max-w-3xl">
          Median of {setup.repeats} runs on the same bars. Reported second on purpose: a fast
          number that disagrees with a slow one is not obviously the better number.
        </p>
        <div className="grid gap-4 sm:grid-cols-2 max-w-2xl">
          {([['vectorbt', r.vectorbt], ['backtrader', r.backtrader]] as const).map(([name, res]) => (
            <div key={name} className="rounded-xl border border-[hsl(215,40%,18%)] bg-[hsl(220,55%,9%)] p-5">
              <div className="flex items-baseline justify-between">
                <h3 className="font-semibold text-white">{name}</h3>
                <span className="text-xs text-[hsl(215,20%,50%)]">v{data.versions[name]}</span>
              </div>
              <div className="mt-2 font-mono text-3xl font-bold tabular-nums text-white">
                {(res.seconds_median * 1000).toFixed(1)}<span className="text-lg text-[hsl(215,20%,55%)]"> ms</span>
              </div>
              <div className="mt-1 text-xs text-[hsl(215,20%,50%)]">
                fastest of {setup.repeats}: {(res.seconds_min * 1000).toFixed(1)} ms
              </div>
            </div>
          ))}
        </div>
        <p className="mt-4 max-w-3xl text-sm text-[hsl(215,20%,50%)]">
          backtrader is {cmp.speed_ratio_backtrader_over_vectorbt.toFixed(0)}× slower here.
          That is architecture, not inefficiency: vectorbt operates on whole NumPy arrays
          while backtrader steps bar by bar, and stepping is what allows a strategy to react
          to its own fills. {data.caveats.speed_is_secondary}
        </p>
      </section>

      <section className="max-w-3xl mb-14">
        <h2 className="text-2xl font-bold text-white mb-4">What was pinned, and why</h2>
        <div className="space-y-4">
          {Object.entries(data.pinned).map(([k, v]) => (
            <div key={k}>
              <h3 className="text-sm font-semibold text-slate-200 mb-1">
                {k.replace(/_/g, ' ').replace(/^./, c => c.toUpperCase())}
              </h3>
              <p className="text-sm text-slate-400 leading-relaxed">{v}</p>
            </div>
          ))}
        </div>
      </section>

      <section className="max-w-3xl mb-14">
        <h2 className="text-2xl font-bold text-white mb-4">The harness</h2>
        <pre className="overflow-x-auto rounded-xl border border-[hsl(215,40%,18%)] bg-[hsl(220,55%,7%)] p-5 text-sm text-slate-300">
          <code>{`# Both libraries receive the SAME entry/exit arrays, computed once.
# Letting each compute its own indicator would make an indicator
# difference look like a backtest difference.

pf = vbt.Portfolio.from_signals(
    close=df["close"], entries=entries, exits=exits,
    size=${setup.size_shares}, size_type="amount",
    init_cash=${setup.initial_cash}, fees=${setup.commission}, freq="1D",
)

cerebro.broker.setcash(${setup.initial_cash})
cerebro.broker.setcommission(commission=${setup.commission})
cerebro.broker.set_coc(True)   # fill at the signal bar's close, like vectorbt
# ...and self.buy(size=${setup.size_shares}) rather than backtrader's default 1 share`}</code>
        </pre>
        <p className="text-slate-400 leading-relaxed mt-4">
          Measured on {setup.bars.toLocaleString()} {setup.symbol} bars ({setup.from} to{' '}
          {setup.to}), {setup.strategy}. Versions:{' '}
          {Object.entries(data.versions).map(([k, v]) => `${k} ${v}`).join(', ')}. Regenerate
          with <code className="inline-code">python -m pipeline.framework_bench</code>.
        </p>
      </section>

      <section className="max-w-3xl mb-14">
        <h2 className="text-2xl font-bold text-white mb-4">Limitations</h2>
        <div className="space-y-4">
          {Object.entries(data.caveats).map(([k, v]) => (
            <div key={k}>
              <h3 className="text-sm font-semibold text-slate-200 mb-1">
                {k.replace(/_/g, ' ').replace(/^./, c => c.toUpperCase())}
              </h3>
              <p className="text-sm text-slate-400 leading-relaxed">{v}</p>
            </div>
          ))}
        </div>
      </section>

      <section className="max-w-3xl mb-14">
        <h2 className="text-2xl font-bold text-white mb-6">Frequently asked questions</h2>
        <div className="space-y-4">
          {faqs.map(f => (
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
          <Link href="/indicator-formulas" className="group rounded-xl border border-[hsl(215,40%,18%)] bg-[hsl(220,55%,9%)] p-5 transition-all hover:border-indigo-500/60 hover:bg-[hsl(220,55%,11%)]">
            <h3 className="text-lg font-semibold text-white group-hover:text-indigo-400 transition-colors">Indicator Formulas, Cross-Checked</h3>
            <p className="mt-1.5 text-sm text-slate-400">The same two-implementation discipline, applied to indicators.</p>
          </Link>
          <Link href="/data-vendors" className="group rounded-xl border border-[hsl(215,40%,18%)] bg-[hsl(220,55%,9%)] p-5 transition-all hover:border-indigo-500/60 hover:bg-[hsl(220,55%,11%)]">
            <h3 className="text-lg font-semibold text-white group-hover:text-indigo-400 transition-colors">Market Data API Benchmark</h3>
            <p className="mt-1.5 text-sm text-slate-400">Measured vendor coverage, adjustment correctness and licence terms.</p>
          </Link>
          <Link href="/backtesting/builder" className="group rounded-xl border border-[hsl(215,40%,18%)] bg-[hsl(220,55%,9%)] p-5 transition-all hover:border-indigo-500/60 hover:bg-[hsl(220,55%,11%)]">
            <h3 className="text-lg font-semibold text-white group-hover:text-indigo-400 transition-colors">Strategy Builder</h3>
            <p className="mt-1.5 text-sm text-slate-400">Configure and backtest a strategy without writing code.</p>
          </Link>
          <Link href="/tools" className="group rounded-xl border border-[hsl(215,40%,18%)] bg-[hsl(220,55%,9%)] p-5 transition-all hover:border-indigo-500/60 hover:bg-[hsl(220,55%,11%)]">
            <h3 className="text-lg font-semibold text-white group-hover:text-indigo-400 transition-colors">All Tools</h3>
            <p className="mt-1.5 text-sm text-slate-400">Browse every free tool on QuantEngines.</p>
          </Link>
        </div>
      </section>

      <p className="max-w-3xl mt-14 text-xs text-[hsl(215,20%,45%)] leading-relaxed">
        Generated {data.generated_at}. This is a comparison of software behaviour on
        historical data. The strategy shown is a test fixture, not a recommendation, and its
        return over this sample is not a forecast of anything.
      </p>
    </div>
  )
}
