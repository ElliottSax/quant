import type { Metadata } from 'next'
import Link from 'next/link'
import WinRateSignificanceCalculator from './WinRateSignificanceCalculator'

const url = 'https://quantengines.com/tools/win-rate-significance'

export const metadata: Metadata = {
  title: 'Win Rate Significance Calculator — Is It Skill or Luck? | QuantEngines',
  description:
    'Free win rate significance calculator. Enter your wins and total trades to get a Wilson score confidence interval and exact binomial p-value — find out if your win rate is statistically distinguishable from chance.',
  keywords: [
    'win rate significance calculator',
    'is my trading strategy statistically significant',
    'binomial test calculator trading',
    'win rate confidence interval',
    'trading edge statistical significance',
    'sample size trading strategy',
  ],
  alternates: { canonical: url },
  openGraph: {
    title: 'Win Rate Significance Calculator',
    description: 'Find out whether your win rate is statistically distinguishable from chance, with a Wilson score confidence interval and exact binomial p-value.',
    type: 'website',
    url,
  },
}

const faqs = [
  {
    q: 'Is a 60% win rate over 20 trades statistically significant?',
    a: 'No. At 12 wins out of 20 trades, the 95% Wilson confidence interval runs from roughly 38% to 78% — comfortably including 50%, so a fair coin could easily have produced this result. The exact two-sided binomial p-value against a 50% baseline is about 0.50 (far above the conventional 0.05 threshold). Small samples produce wide intervals; a 60% win rate needs several hundred trades before it reliably excludes 50%.',
  },
  {
    q: 'Why use the Wilson score interval instead of the normal approximation?',
    a: 'The standard "Wald" interval (p̂ ± z·√(p̂(1−p̂)/n)) has poor coverage for small samples and for win rates near 0% or 100% — it can produce nonsensical bounds like a negative lower limit. The Wilson score interval (Wilson, 1927) corrects for this and is the interval statisticians generally recommend for binomial proportions at any sample size (Brown, Cai & DasGupta, Statistical Science, 2001). This calculator always uses Wilson, never Wald.',
  },
  {
    q: 'What does the p-value actually mean here?',
    a: 'It is the probability of seeing a result at least as extreme as your observed win rate, if the baseline rate you tested against were actually true. A p-value of 0.13 means: if your true win rate really were the baseline, you\'d see a result this extreme (or more extreme) about 13% of the time by chance alone — not rare enough to conclude your edge is real rather than noise, by the conventional 5% threshold.',
  },
  {
    q: 'What baseline should I test against?',
    a: "50% tests whether you're better than a coin flip, which is a low bar for a directional strategy. A more useful test is your breakeven win rate — the win rate your risk/reward ratio requires just to break even, which the risk/reward calculator computes for you. Testing against your breakeven rate answers the real question: is my edge distinguishable from exactly breaking even?",
  },
  {
    q: 'How many trades do I need before a win rate becomes meaningful?',
    a: 'It depends on how far your observed rate is from the baseline — a large edge shows up with fewer trades than a small one — but confidence intervals narrow with the square root of sample size, not linearly, so going from 25 to 100 trades only halves the interval width, not quarters it. As a reference point, distinguishing a 55% win rate from 50% at 95% confidence typically needs several hundred trades; distinguishing 70% from 50% needs far fewer, as the "70/100 vs. 50%" example on this page shows.',
  },
]

export default function WinRateSignificancePage() {
  const webAppSchema = {
    '@context': 'https://schema.org',
    '@type': 'WebApplication',
    name: 'Win Rate Significance Calculator',
    url,
    applicationCategory: 'FinanceApplication',
    operatingSystem: 'Any',
    offers: { '@type': 'Offer', price: '0', priceCurrency: 'USD' },
    description:
      'Calculate a Wilson score confidence interval and exact binomial test p-value for a trading win rate, to check whether it is statistically distinguishable from chance or a chosen baseline.',
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
        <span className="text-[hsl(215,20%,70%)]">Win Rate Significance Calculator</span>
      </nav>

      {/* Header */}
      <div className="max-w-3xl mb-10">
        <h1 className="text-4xl md:text-5xl font-bold mb-4 text-white">Win Rate Significance Calculator</h1>
        <p className="text-lg text-slate-400">
          Enter your wins and total trades to see whether your win rate is actually distinguishable
          from chance — or from any baseline you choose — using a Wilson score confidence interval
          and an exact binomial test. The question this site exists to ask about every pattern,
          applied to your own trade record.
        </p>
      </div>

      {/* Calculator */}
      <WinRateSignificanceCalculator />

      {/* Explainer */}
      <section className="max-w-3xl mt-14">
        <h2 className="text-2xl font-bold text-white mb-4">Why win rates need error bars</h2>
        <p className="text-slate-400 leading-relaxed mb-4">
          A strategy that wins 58% of 100 trades sounds like a real edge. Run the exact binomial
          test against a 50% baseline and the two-sided p-value comes out to about 0.13 — meaning a
          coin-flip strategy would produce a result at least this extreme roughly one time in eight,
          just from sampling noise. That's not proof of no edge, but it's nowhere near strong enough
          evidence to call it skill rather than luck.
        </p>
        <p className="text-slate-400 leading-relaxed mb-4">
          The same 58% win rate over 1,000 trades tells a very different story: the 95% confidence
          interval narrows from roughly 48%–67% (at n=100) to about 55%–61% (at n=1,000), and now
          excludes 50% entirely. Same win rate, opposite conclusion — because sample size, not the
          headline percentage, is what determines whether a win rate means anything.
        </p>
        <p className="text-slate-400 leading-relaxed">
          This is the same statistical discipline the site applies to seasonal patterns and
          congressional trades: a win rate without a sample size and a confidence interval is not
          evidence, it's a headline.
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
          <Link href="/tools/risk-reward" className="group rounded-xl border border-[hsl(215,40%,18%)] bg-[hsl(220,55%,9%)] p-5 transition-all hover:border-indigo-500/60 hover:bg-[hsl(220,55%,11%)]">
            <h3 className="text-lg font-semibold text-white group-hover:text-indigo-400 transition-colors">Risk/Reward Ratio Calculator</h3>
            <p className="mt-1.5 text-sm text-slate-400">Find your breakeven win rate — a better baseline to test against than 50%.</p>
          </Link>
          <Link href="/tools/kelly-criterion" className="group rounded-xl border border-[hsl(215,40%,18%)] bg-[hsl(220,55%,9%)] p-5 transition-all hover:border-indigo-500/60 hover:bg-[hsl(220,55%,11%)]">
            <h3 className="text-lg font-semibold text-white group-hover:text-indigo-400 transition-colors">Kelly Criterion Calculator</h3>
            <p className="mt-1.5 text-sm text-slate-400">Turn a genuinely significant win rate into an edge-optimal stake.</p>
          </Link>
          <Link href="/backtesting" className="group rounded-xl border border-[hsl(215,40%,18%)] bg-[hsl(220,55%,9%)] p-5 transition-all hover:border-indigo-500/60 hover:bg-[hsl(220,55%,11%)]">
            <h3 className="text-lg font-semibold text-white group-hover:text-indigo-400 transition-colors">Backtesting Engine</h3>
            <p className="mt-1.5 text-sm text-slate-400">Get a real win/loss count from historical data instead of guessing.</p>
          </Link>
          <Link href="/tools" className="group rounded-xl border border-[hsl(215,40%,18%)] bg-[hsl(220,55%,9%)] p-5 transition-all hover:border-indigo-500/60 hover:bg-[hsl(220,55%,11%)]">
            <h3 className="text-lg font-semibold text-white group-hover:text-indigo-400 transition-colors">All Trading Tools</h3>
            <p className="mt-1.5 text-sm text-slate-400">Browse every free tool on QuantEngines.</p>
          </Link>
        </div>
      </section>

      <p className="max-w-3xl mt-14 text-xs text-[hsl(215,20%,45%)] leading-relaxed">
        This calculator performs a Wilson score interval and an exact binomial test on the win/loss
        counts you provide. It is not investment advice, does not evaluate any specific strategy or
        trade, and a statistically significant win rate is not a guarantee of future performance.
      </p>
    </div>
  )
}
