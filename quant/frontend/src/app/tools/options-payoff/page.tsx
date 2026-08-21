import type { Metadata } from 'next'
import Link from 'next/link'
import OptionsPayoffBuilder from './OptionsPayoffBuilder'

const url = 'https://quantengines.com/tools/options-payoff'

export const metadata: Metadata = {
  title: 'Multi-Leg Options Payoff Calculator — Iron Condor, Spreads & More | QuantEngines',
  description:
    'Free multi-leg options payoff diagram builder. Model iron condors, spreads, straddles, and strangles up to 6 legs — get max profit, max loss, and exact breakevens computed from the strikes and premiums you enter.',
  keywords: [
    'options payoff calculator',
    'iron condor payoff calculator',
    'multi-leg options calculator',
    'options spread calculator',
    'options strategy payoff diagram',
    'straddle strangle calculator',
  ],
  alternates: { canonical: url },
  openGraph: {
    title: 'Multi-Leg Options Payoff Calculator',
    description: 'Model any combination of calls and puts and see the exact payoff diagram, max profit, max loss, and breakevens at expiration.',
    type: 'website',
    url,
  },
}

const faqs = [
  {
    q: 'How is max profit and max loss calculated for a multi-leg strategy?',
    a: 'The combined payoff of any set of calls and puts is piecewise-linear, with kinks only at each leg\'s strike price. That means the maximum and minimum can only occur at $0, at one of the strikes, or — if the combined position still has a nonzero slope beyond the highest strike (e.g. a naked long or short call) — extend to infinity in that direction. This calculator evaluates the payoff at every strike and at $0, then checks the slope past the highest strike to determine whether profit or loss is capped or unlimited, and reports the true maximum or minimum rather than an approximation.',
  },
  {
    q: 'Why does an iron condor have two breakeven prices?',
    a: "An iron condor's payoff is flat (at max profit) between the two short strikes, then slopes down on both sides toward the long strikes. It crosses zero once on the way down through the put side and once on the way up through the call side — this calculator solves both breakevens exactly using the piecewise-linear structure, not by scanning a chart and eyeballing where it crosses.",
  },
  {
    q: 'Does this account for time value before expiration?',
    a: 'The payoff diagram and max profit/loss/breakeven figures are at-expiration only — pure intrinsic value, no time decay. A position can be worth less or more than its expiration payoff before expiry due to time value; use the Black-Scholes calculator to price an individual leg at a specific number of days to expiry.',
  },
  {
    q: 'What does "1 contract = 100 shares" mean for my numbers?',
    a: 'A single options contract controls 100 shares of the underlying by market convention, so a $2.00 premium per share costs $200 per contract, and a strategy with 2 contracts doubles every dollar figure. This calculator scales every leg by quantity x 100 automatically — enter contract counts, not share counts.',
  },
  {
    q: 'Why is my long call showing unlimited max profit?',
    a: "A long call's payoff keeps rising for every dollar the underlying rises above the strike, with no cap — that is genuinely unlimited, which is what \"Unlimited\" in the max profit field means. Spreads cap this by adding a short leg at a higher strike, which is why a bull call spread shows a specific dollar max profit instead.",
  },
]

export default function OptionsPayoffPage() {
  const webAppSchema = {
    '@context': 'https://schema.org',
    '@type': 'WebApplication',
    name: 'Multi-Leg Options Payoff Calculator',
    url,
    applicationCategory: 'FinanceApplication',
    operatingSystem: 'Any',
    offers: { '@type': 'Offer', price: '0', priceCurrency: 'USD' },
    description:
      'Model any combination of calls and puts and get max profit, max loss, and exact breakevens at expiration, with a payoff diagram.',
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

      <nav className="text-sm text-[hsl(215,20%,55%)] mb-6">
        <Link href="/tools" className="hover:text-indigo-400">Tools</Link>
        <span className="mx-2">/</span>
        <span className="text-[hsl(215,20%,70%)]">Multi-Leg Options Payoff Calculator</span>
      </nav>

      <div className="max-w-3xl mb-10">
        <h1 className="text-4xl md:text-5xl font-bold mb-4 text-white">Multi-Leg Options Payoff Calculator</h1>
        <p className="text-lg text-slate-400">
          Build any combination of calls and puts — spreads, straddles, strangles, iron condors —
          and get the exact max profit, max loss, and breakevens at expiration, solved from the
          piecewise-linear structure of the payoff rather than approximated from a chart.
        </p>
      </div>

      <OptionsPayoffBuilder />

      <section className="max-w-3xl mt-14">
        <h2 className="text-2xl font-bold text-white mb-4">How the calculation works</h2>
        <p className="text-slate-400 leading-relaxed mb-4">
          Each leg's payoff at expiry is textbook intrinsic value minus (long) or plus (short) its
          premium: max(S − K, 0) for a call, max(K − S, 0) for a put. Summed across legs, the result
          is piecewise-linear with a kink at every strike — which means the maximum, minimum, and
          every zero-crossing can be solved exactly rather than estimated: evaluate the sum at $0
          and at each strike, then check whether the combined slope beyond the highest strike is
          zero (capped), positive (unlimited profit), or negative (unlimited loss).
        </p>
        <p className="text-slate-400 leading-relaxed">
          Worked through the default bull call spread (long 100-strike call at $5, short 110-strike
          call at $2): net debit is $300. At $0 both legs are worth their premium only, at the
          100-strike the long call is worthless and the short is still worthless, at the 110-strike
          the long call is worth $1,000 and the short still worthless — evaluating the sum at each
          point and checking the flat slope beyond 110 (a call spread caps out) gives max profit of
          $700 and max loss of $300, with a single breakeven at $103.
        </p>
      </section>

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

      <section className="max-w-3xl mt-14">
        <h2 className="text-2xl font-bold text-white mb-6">Related tools</h2>
        <div className="grid gap-4 sm:grid-cols-2">
          <Link href="/options" className="group rounded-xl border border-[hsl(215,40%,18%)] bg-[hsl(220,55%,9%)] p-5 transition-all hover:border-indigo-500/60 hover:bg-[hsl(220,55%,11%)]">
            <h3 className="text-lg font-semibold text-white group-hover:text-indigo-400 transition-colors">Black-Scholes Options Calculator</h3>
            <p className="mt-1.5 text-sm text-slate-400">Price a single leg and see all five Greeks before expiration.</p>
          </Link>
          <Link href="/tools/risk-reward" className="group rounded-xl border border-[hsl(215,40%,18%)] bg-[hsl(220,55%,9%)] p-5 transition-all hover:border-indigo-500/60 hover:bg-[hsl(220,55%,11%)]">
            <h3 className="text-lg font-semibold text-white group-hover:text-indigo-400 transition-colors">Risk/Reward Ratio Calculator</h3>
            <p className="mt-1.5 text-sm text-slate-400">Check the reward-to-risk ratio of any trade before you take it.</p>
          </Link>
          <Link href="/tools/kelly-criterion" className="group rounded-xl border border-[hsl(215,40%,18%)] bg-[hsl(220,55%,9%)] p-5 transition-all hover:border-indigo-500/60 hover:bg-[hsl(220,55%,11%)]">
            <h3 className="text-lg font-semibold text-white group-hover:text-indigo-400 transition-colors">Kelly Criterion Calculator</h3>
            <p className="mt-1.5 text-sm text-slate-400">Size a position from your win rate and win/loss ratio.</p>
          </Link>
          <Link href="/tools" className="group rounded-xl border border-[hsl(215,40%,18%)] bg-[hsl(220,55%,9%)] p-5 transition-all hover:border-indigo-500/60 hover:bg-[hsl(220,55%,11%)]">
            <h3 className="text-lg font-semibold text-white group-hover:text-indigo-400 transition-colors">All Trading Tools</h3>
            <p className="mt-1.5 text-sm text-slate-400">Browse every free tool on QuantEngines.</p>
          </Link>
        </div>
      </section>

      <p className="max-w-3xl mt-14 text-xs text-[hsl(215,20%,45%)] leading-relaxed">
        This calculator performs closed-form arithmetic on the strikes, premiums, and quantities you
        enter. It is not investment advice, does not recommend any strategy or strike, and the
        expiration payoff shown does not include commissions, assignment risk, or early exercise.
      </p>
    </div>
  )
}
