import type { Metadata } from 'next'
import Link from 'next/link'
import PositionSizeCalculator from './PositionSizeCalculator'

const url = 'https://quantengines.com/tools/position-size'

export const metadata: Metadata = {
  title: 'Position Size Calculator — Shares to Buy by Risk | QuantEngines',
  description:
    'Free position size calculator. Enter your account size, risk per trade, entry, and stop-loss to get the exact number of shares to buy, your total dollar risk, and position value. No signup required.',
  keywords: [
    'position size calculator',
    'position sizing calculator',
    'shares to buy calculator',
    'risk per trade calculator',
    'stop loss position size',
    'trading risk management',
    'how many shares to buy',
  ],
  alternates: { canonical: url },
  openGraph: {
    title: 'Position Size Calculator',
    description: 'Calculate the exact number of shares to buy based on your account size, risk per trade, entry, and stop-loss.',
    type: 'website',
    url,
  },
}

const faqs = [
  {
    q: 'How do you calculate position size?',
    a: 'First find your dollar risk: account size multiplied by your risk percentage (e.g. $25,000 × 1% = $250). Then find your risk per share: the absolute difference between entry and stop-loss price. Divide dollar risk by risk per share and round down to get the number of shares to buy.',
  },
  {
    q: 'What does changing the risk percentage do to the numbers?',
    a: 'The risk percentage scales the dollar risk linearly, and therefore the share count too. On a $25,000 account, 1% is $250 of dollar risk and 2% is $500, which doubles the shares for the same stop distance. The compounding effect of a losing run scales with it: ten consecutive full stop-outs at 1% leave about 90.4% of the starting balance, at 2% about 81.7%, and at 10% about 34.9%. This calculator does not suggest a percentage — enter the one you use.',
  },
  {
    q: 'Why round the number of shares down?',
    a: 'Rounding down keeps the realised dollar risk at or below the amount implied by your risk percentage. Rounding up would push it slightly above the limit. Because of the rounding, the dollar risk shown is usually a little under the target, and the gap is largest when the stop distance is wide relative to the dollar risk.',
  },
  {
    q: 'Does it work for short trades?',
    a: 'Yes. The calculator reads a stop-loss above the entry price as a short and one below the entry as a long, and labels the result accordingly. The risk per share is the absolute distance between entry and stop in both cases, so the share count is calculated the same way.',
  },
  {
    q: 'Does this calculator account for commissions or slippage?',
    a: 'No. It computes the position size implied by your entry, stop, and risk inputs, assuming a single fill at the entry price and an exit at exactly the stop price. Commissions, slippage, gaps through the stop, and financing costs are outside the calculation and would each change the realised risk.',
  },
  {
    q: 'What if the position value comes out larger than my account?',
    a: 'That happens whenever the stop is tight relative to your risk percentage, and the calculator flags it. The arithmetic is still correct — the share count risks exactly what you specified if the stop is hit — but holding that many shares would require margin, and a gap through a tight stop can cost more than the stated risk.',
  },
]

export default function PositionSizePage() {
  const webAppSchema = {
    '@context': 'https://schema.org',
    '@type': 'WebApplication',
    name: 'Position Size Calculator',
    url,
    applicationCategory: 'FinanceApplication',
    operatingSystem: 'Any',
    offers: { '@type': 'Offer', price: '0', priceCurrency: 'USD' },
    description:
      'Calculate the exact number of shares to buy based on account size, risk per trade, entry price, and stop-loss.',
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
        <span className="text-[hsl(215,20%,70%)]">Position Size Calculator</span>
      </nav>

      {/* Header */}
      <div className="max-w-3xl mb-10">
        <h1 className="text-4xl md:text-5xl font-bold mb-4 text-white">Position Size Calculator</h1>
        <p className="text-lg text-slate-400">
          Work out the share count implied by your account size, the percentage of it you are
          willing to risk, your entry price, and your stop-loss. Everything is computed from those
          four numbers alone — no market data is used and none is shown, so you can check every
          figure by hand.
        </p>
      </div>

      {/* Calculator */}
      <PositionSizeCalculator />

      {/* Explainer */}
      <section className="max-w-3xl mt-14">
        <h2 className="text-2xl font-bold text-white mb-4">How the calculation works</h2>
        <p className="text-slate-400 leading-relaxed mb-4">
          Position sizing inverts the usual question. Rather than picking a share count and seeing
          what it costs if the stop is hit, you fix the loss you are willing to take and let that
          determine the share count. Four steps, all of them arithmetic:
        </p>
        <ol className="text-slate-400 leading-relaxed space-y-2 mb-4 list-decimal pl-5">
          <li><strong className="text-slate-200">Dollar risk</strong> = account size × (risk % ÷ 100)</li>
          <li><strong className="text-slate-200">Risk per share</strong> = | entry price − stop-loss price |</li>
          <li><strong className="text-slate-200">Shares</strong> = floor(dollar risk ÷ risk per share)</li>
          <li><strong className="text-slate-200">Position value</strong> = shares × entry price</li>
        </ol>
        <p className="text-slate-400 leading-relaxed mb-4">
          Worked through with the default inputs: a $25,000 account at 1% per trade gives $250 of
          dollar risk. An entry of $50 against a stop at $48 puts $2 of risk on each share, so
          $250 ÷ $2 = 125 shares. That is a $6,250 position, 25% of the account, and exactly $250
          is lost if the stop fills at $48.
        </p>
        <p className="text-slate-400 leading-relaxed mb-4">
          The absolute value in step two is what makes the calculation direction-agnostic. A stop
          at $52 against the same $50 entry is a short with the same $2 of risk per share and the
          same 125 shares; the page labels the result long or short from the position of the stop
          relative to the entry.
        </p>
        <p className="text-slate-400 leading-relaxed">
          Two things the arithmetic cannot promise. The floor in step three means the realised risk
          is usually a little under the target rather than exactly on it. And the $250 figure holds
          only if the exit actually fills at the stop price — a gap through the stop is a larger
          loss than the calculation shows.
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
            <p className="mt-1.5 text-sm text-slate-400">Check the R:R and breakeven win rate of a trade before you take it.</p>
          </Link>
          <Link href="/options" className="group rounded-xl border border-[hsl(215,40%,18%)] bg-[hsl(220,55%,9%)] p-5 transition-all hover:border-indigo-500/60 hover:bg-[hsl(220,55%,11%)]">
            <h3 className="text-lg font-semibold text-white group-hover:text-indigo-400 transition-colors">Options Calculator</h3>
            <p className="mt-1.5 text-sm text-slate-400">Price options and analyze the Greeks with Black-Scholes.</p>
          </Link>
          <Link href="/backtesting" className="group rounded-xl border border-[hsl(215,40%,18%)] bg-[hsl(220,55%,9%)] p-5 transition-all hover:border-indigo-500/60 hover:bg-[hsl(220,55%,11%)]">
            <h3 className="text-lg font-semibold text-white group-hover:text-indigo-400 transition-colors">Backtesting Engine</h3>
            <p className="mt-1.5 text-sm text-slate-400">Test your strategy against historical market data.</p>
          </Link>
          <Link href="/tools" className="group rounded-xl border border-[hsl(215,40%,18%)] bg-[hsl(220,55%,9%)] p-5 transition-all hover:border-indigo-500/60 hover:bg-[hsl(220,55%,11%)]">
            <h3 className="text-lg font-semibold text-white group-hover:text-indigo-400 transition-colors">All Trading Tools</h3>
            <p className="mt-1.5 text-sm text-slate-400">Browse every free tool on QuantEngines.</p>
          </Link>
        </div>
      </section>

      <p className="max-w-3xl mt-14 text-xs text-[hsl(215,20%,45%)] leading-relaxed">
        This calculator performs and displays arithmetic on the inputs you provide. It is not
        investment advice, does not recommend a risk percentage, a share count, or any trade, and
        makes no claim about how a trade sized this way would perform.
      </p>
    </div>
  )
}
