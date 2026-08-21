import type { Metadata } from 'next'
import Link from 'next/link'
import KellyCriterionCalculator from './KellyCriterionCalculator'

const url = 'https://quantengines.com/tools/kelly-criterion'

export const metadata: Metadata = {
  title: 'Kelly Criterion Calculator — Optimal Position Size | QuantEngines',
  description:
    'Free Kelly criterion calculator for traders. Enter your win rate and win/loss ratio to get the edge-optimal stake, plus a half-Kelly and quarter-Kelly comparison and a growth-rate chart. No signup required.',
  keywords: [
    'kelly criterion calculator',
    'kelly formula calculator',
    'optimal position size',
    'half kelly calculator',
    'kelly criterion trading',
    'kelly criterion position sizing',
    'edge based position sizing',
  ],
  alternates: { canonical: url },
  openGraph: {
    title: 'Kelly Criterion Calculator',
    description:
      'Calculate the edge-optimal stake from your win rate and win/loss ratio, with a growth-rate chart showing why fractional Kelly exists.',
    type: 'website',
    url,
  },
}

const faqs = [
  {
    q: 'What is the Kelly criterion formula?',
    a: 'f* = W − (1 − W) ÷ R, where W is your win probability (as a decimal) and R is your win/loss ratio — the average win size divided by the average loss size. f* is the fraction of your bankroll that maximizes the expected long-run geometric growth rate, derived by John Kelly in 1956 and popularized for trading and gambling by Ed Thorp.',
  },
  {
    q: 'Why use half Kelly or quarter Kelly instead of full Kelly?',
    a: 'The growth-rate curve is asymmetric around the full-Kelly point: it rises steeply on the way up to f*, then falls off faster past it. Two effects follow. First, overestimating your win rate or win/loss ratio — which real traders do, because both are estimated from a limited sample — pushes the true optimum lower than the one calculated, so full Kelly calculated from noisy inputs tends to over-bet in practice. Second, full Kelly still carries large peak-to-trough drawdowns even when the inputs are exactly right, because it maximizes growth rate, not smoothness. Half Kelly gives roughly three-quarters of the growth rate of full Kelly with roughly half the variance, which is why it is the most commonly cited compromise.',
  },
  {
    q: 'What happens if I enter a win rate below the break-even threshold?',
    a: "Kelly sizing requires a positive edge — W×R must exceed (1−W), i.e. your expected value per dollar staked must be positive. If it isn't, f* is negative, and this calculator shows a stake of $0 rather than a negative position, because the Kelly criterion has no interpretation for betting against your own edge. The break-even win probability shown is 1 ÷ (1 + R): at your win/loss ratio, that is the win rate at which f* crosses zero.",
  },
  {
    q: 'Is this the same model as the position size and risk/reward calculators?',
    a: 'No — they answer different questions. The position size calculator fixes a risk percentage you choose and computes shares from your entry and stop. The risk/reward calculator checks a single trade\'s reward-to-risk ratio. This calculator instead asks what risk percentage is edge-optimal in the first place, given your historical win rate and win/loss ratio — its output (the Kelly fraction) is a reasonable input to feed into the position size calculator\'s risk-per-trade field.',
  },
  {
    q: 'What are the limitations of this model?',
    a: 'It assumes every trade is a fixed win of R units or a fixed loss of 1 unit at a stable probability W — a two-outcome simplification of what is really a continuous distribution of trade outcomes. It also assumes W and R are known exactly, when in practice both are estimates from a finite trade history and drift over time as market conditions change. It does not account for correlated trades (multiple open positions that win or lose together), commissions, slippage, or taxes. Treat the output as a starting point for a risk framework, not a guarantee.',
  },
]

export default function KellyCriterionPage() {
  const webAppSchema = {
    '@context': 'https://schema.org',
    '@type': 'WebApplication',
    name: 'Kelly Criterion Calculator',
    url,
    applicationCategory: 'FinanceApplication',
    operatingSystem: 'Any',
    offers: { '@type': 'Offer', price: '0', priceCurrency: 'USD' },
    description:
      'Calculate the edge-optimal position size from win probability and win/loss ratio using the Kelly criterion, with fractional-Kelly comparison and a growth-rate chart.',
  }

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
      <script type="application/ld+json" dangerouslySetInnerHTML={{ __html: JSON.stringify(webAppSchema) }} />
      <script type="application/ld+json" dangerouslySetInnerHTML={{ __html: JSON.stringify(faqSchema) }} />

      {/* Breadcrumb */}
      <nav className="text-sm text-[hsl(215,20%,55%)] mb-6">
        <Link href="/tools" className="hover:text-indigo-400">Tools</Link>
        <span className="mx-2">/</span>
        <span className="text-[hsl(215,20%,70%)]">Kelly Criterion Calculator</span>
      </nav>

      {/* Header */}
      <div className="max-w-3xl mb-10">
        <h1 className="text-4xl md:text-5xl font-bold mb-4 text-white">Kelly Criterion Calculator</h1>
        <p className="text-lg text-slate-400">
          Enter your win probability and win/loss ratio to get the edge-optimal bankroll fraction —
          then see exactly why most traders who use it stake a fraction of that number, with a
          growth-rate chart computed from the same two inputs. No trade history is read; everything
          is arithmetic over the numbers you type in.
        </p>
      </div>

      {/* Calculator */}
      <KellyCriterionCalculator />

      {/* Explainer */}
      <section className="max-w-3xl mt-14">
        <h2 className="text-2xl font-bold text-white mb-4">How the calculation works</h2>
        <p className="text-slate-400 leading-relaxed mb-4">
          The Kelly criterion answers a specific question: given a repeated bet with a known edge,
          what fraction of the bankroll staked each time maximizes the expected long-run growth
          rate? John Kelly derived the answer in 1956 for a two-outcome bet — win R units or lose 1
          unit, with probability W of winning:
        </p>
        <div className="rounded-lg border border-[hsl(215,40%,18%)] bg-[hsl(220,55%,7%)] p-4 font-mono text-sm text-slate-300 mb-4">
          f* = W − (1 − W) ÷ R
        </div>
        <p className="text-slate-400 leading-relaxed mb-4">
          Worked through with the default inputs: a 55% win rate and a 1.5 win/loss ratio gives f*
          = 0.55 − 0.45 ÷ 1.5 = 0.55 − 0.30 = 0.25, or 25% of the account per trade at full Kelly.
          At half Kelly (the default fraction here) that becomes 12.5% — $3,125 on a $25,000
          account.
        </p>
        <p className="text-slate-400 leading-relaxed mb-4">
          The expected growth rate at any staked fraction f follows from the same two inputs:
          growth(f) = W·ln(1 + f·R) + (1 − W)·ln(1 − f). This is what the chart plots from 0% to
          200% of full Kelly. It peaks exactly at f*, confirming the formula, and the curve is
          visibly steeper past the peak than before it — the mathematical reason overshooting full
          Kelly costs more growth than undershooting it by the same amount.
        </p>
        <p className="text-slate-400 leading-relaxed">
          Kelly sizing requires W×R &gt; (1 − W) — a positive expected value per dollar staked. When
          it doesn't hold, f* is negative and the calculator reports a $0 stake rather than a
          negative position, since betting against your own edge has no Kelly interpretation.
        </p>
      </section>

      {/* FAQ */}
      <section className="max-w-3xl mt-14">
        <h2 className="text-2xl font-bold text-white mb-6">Frequently asked questions</h2>
        <div className="space-y-4">
          {faqs.map((f) => (
            <details key={f.q} className="group rounded-xl border border-[hsl(215,40%,18%)] bg-[hsl(220,55%,9%)] p-5">
              <summary className="cursor-pointer text-white font-semibold list-none flex justify-between items-center">
                {f.q}
                <span className="text-indigo-400 group-open:rotate-45 transition-transform">+</span>
              </summary>
              <p className="mt-3 text-slate-400 leading-relaxed">{f.a}</p>
            </details>
          ))}
        </div>
      </section>

      {/* Related tools */}
      <section className="max-w-3xl mt-14">
        <h2 className="text-2xl font-bold text-white mb-6">Related tools</h2>
        <div className="grid gap-4 sm:grid-cols-2">
          <Link href="/tools/position-size" className="group rounded-xl border border-[hsl(215,40%,18%)] bg-[hsl(220,55%,9%)] p-5 transition-all hover:border-indigo-500/60 hover:bg-[hsl(220,55%,11%)]">
            <h3 className="text-lg font-semibold text-white group-hover:text-indigo-400 transition-colors">Position Size Calculator</h3>
            <p className="mt-1.5 text-sm text-slate-400">Turn a chosen risk percentage — including a Kelly fraction — into a share count.</p>
          </Link>
          <Link href="/tools/risk-reward" className="group rounded-xl border border-[hsl(215,40%,18%)] bg-[hsl(220,55%,9%)] p-5 transition-all hover:border-indigo-500/60 hover:bg-[hsl(220,55%,11%)]">
            <h3 className="text-lg font-semibold text-white group-hover:text-indigo-400 transition-colors">Risk/Reward Ratio Calculator</h3>
            <p className="mt-1.5 text-sm text-slate-400">Check a single trade's reward-to-risk ratio and breakeven win rate.</p>
          </Link>
          <Link href="/tools/win-rate-significance" className="group rounded-xl border border-[hsl(215,40%,18%)] bg-[hsl(220,55%,9%)] p-5 transition-all hover:border-indigo-500/60 hover:bg-[hsl(220,55%,11%)]">
            <h3 className="text-lg font-semibold text-white group-hover:text-indigo-400 transition-colors">Win Rate Significance Calculator</h3>
            <p className="mt-1.5 text-sm text-slate-400">Check your win rate is real edge, not noise, before sizing a position on it.</p>
          </Link>
          <Link href="/backtesting" className="group rounded-xl border border-[hsl(215,40%,18%)] bg-[hsl(220,55%,9%)] p-5 transition-all hover:border-indigo-500/60 hover:bg-[hsl(220,55%,11%)]">
            <h3 className="text-lg font-semibold text-white group-hover:text-indigo-400 transition-colors">Backtesting Engine</h3>
            <p className="mt-1.5 text-sm text-slate-400">Measure your actual win rate and win/loss ratio from historical data instead of guessing.</p>
          </Link>
          <Link href="/tools" className="group rounded-xl border border-[hsl(215,40%,18%)] bg-[hsl(220,55%,9%)] p-5 transition-all hover:border-indigo-500/60 hover:bg-[hsl(220,55%,11%)]">
            <h3 className="text-lg font-semibold text-white group-hover:text-indigo-400 transition-colors">All Trading Tools</h3>
            <p className="mt-1.5 text-sm text-slate-400">Browse every free tool on QuantEngines.</p>
          </Link>
        </div>
      </section>

      <p className="max-w-3xl mt-14 text-xs text-[hsl(215,20%,45%)] leading-relaxed">
        This calculator performs and displays arithmetic on the inputs you provide, using the
        two-outcome Kelly model. It is not investment advice, does not estimate your win rate or
        win/loss ratio for you, and makes no claim about how a position sized this way would
        perform on future trades.
      </p>
    </div>
  )
}
