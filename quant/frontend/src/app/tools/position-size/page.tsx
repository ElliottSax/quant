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
    q: 'What is a good risk per trade percentage?',
    a: 'Most risk-management frameworks suggest risking 1% to 2% of your account on any single trade. Risking 1% means a string of losing trades has a far smaller impact on your capital than risking 5% or 10% per trade.',
  },
  {
    q: 'Why round the number of shares down?',
    a: 'Rounding down guarantees your actual dollar risk stays at or below the amount you intended to risk. Rounding up would push your risk slightly above your limit.',
  },
  {
    q: 'Does this calculator account for commissions or slippage?',
    a: 'No. It gives you the theoretical position size from your entry, stop, and risk inputs. Real fills, commissions, and slippage can shift your true risk slightly, so treat the output as a close starting point.',
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
          Find the exact number of shares to buy so a losing trade costs you no more than you
          intend to risk. Enter your account size, risk per trade, entry price, and stop-loss —
          the math updates instantly.
        </p>
      </div>

      {/* Calculator */}
      <PositionSizeCalculator />

      {/* Explainer */}
      <section className="max-w-3xl mt-14">
        <h2 className="text-2xl font-bold text-white mb-4">How position sizing works</h2>
        <p className="text-slate-400 leading-relaxed mb-4">
          Position sizing is the single biggest lever in risk management. Instead of guessing how
          many shares to buy, you let your maximum acceptable loss decide the size for you. The
          formula is simple:
        </p>
        <ol className="text-slate-400 leading-relaxed space-y-2 mb-4 list-decimal pl-5">
          <li><strong className="text-slate-200">Dollar risk</strong> = account size × (risk % ÷ 100)</li>
          <li><strong className="text-slate-200">Risk per share</strong> = | entry price − stop-loss price |</li>
          <li><strong className="text-slate-200">Shares to buy</strong> = floor(dollar risk ÷ risk per share)</li>
        </ol>
        <p className="text-slate-400 leading-relaxed mb-4">
          For example, on a $25,000 account risking 1% per trade, your dollar risk is $250. Buying
          at $50 with a stop at $48 puts $2 of risk on each share, so you can buy 125 shares — a
          $6,250 position, or 25% of the account, while still only risking $250 if the stop is hit.
        </p>
        <p className="text-slate-400 leading-relaxed">
          Keeping risk constant across trades means no single loss can badly damage your account,
          and it lets you compare very different setups on equal footing.
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
    </div>
  )
}
