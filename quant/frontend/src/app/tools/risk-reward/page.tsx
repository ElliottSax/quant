import type { Metadata } from 'next'
import Link from 'next/link'
import RiskRewardCalculator from './RiskRewardCalculator'

const url = 'https://quantengines.com/tools/risk-reward'

export const metadata: Metadata = {
  title: 'Risk/Reward Ratio Calculator — R:R & Breakeven Win Rate | QuantEngines',
  description:
    'Free risk/reward ratio calculator. Enter entry, stop-loss, and target to get your R:R ratio, percentage gain and loss, and the breakeven win rate you need to be profitable. No signup required.',
  keywords: [
    'risk reward ratio calculator',
    'risk reward calculator',
    'r:r calculator',
    'breakeven win rate calculator',
    'trading risk reward',
    'reward to risk ratio',
    'stop loss target calculator',
  ],
  alternates: { canonical: url },
  openGraph: {
    title: 'Risk/Reward Ratio Calculator',
    description: 'Calculate the risk/reward ratio and breakeven win rate of any trade from your entry, stop-loss, and target.',
    type: 'website',
    url,
  },
}

const faqs = [
  {
    q: 'How is the risk/reward ratio calculated?',
    a: 'Risk is the distance from your entry price to your stop-loss. Reward is the distance from your entry to your target. The ratio is reward divided by risk, shown as 1 : X. For example, an entry of $100, stop of $95, and target of $115 gives $5 of risk and $15 of reward, a 1 : 3 ratio.',
  },
  {
    q: 'What is a good risk/reward ratio?',
    a: 'Many traders look for at least 1 : 2, meaning they aim to make twice what they risk. A 1 : 3 ratio is common for swing setups. The higher the ratio, the lower the win rate you need to stay profitable.',
  },
  {
    q: 'What is the breakeven win rate?',
    a: 'It is the win percentage at which your winners exactly offset your losers over many trades. It equals 1 ÷ (1 + R:R) as a percentage. A 1 : 3 ratio has a 25% breakeven win rate, so winning more than a quarter of trades at that ratio is profitable before costs.',
  },
  {
    q: 'Do I have to enter a position size?',
    a: 'No. Position size is optional. Leave it blank to see per-share and percentage figures only, or enter a share count to also see your total dollar risk and dollar reward.',
  },
]

export default function RiskRewardPage() {
  const webAppSchema = {
    '@context': 'https://schema.org',
    '@type': 'WebApplication',
    name: 'Risk/Reward Ratio Calculator',
    url,
    applicationCategory: 'FinanceApplication',
    operatingSystem: 'Any',
    offers: { '@type': 'Offer', price: '0', priceCurrency: 'USD' },
    description:
      'Calculate the risk/reward ratio, percentage gain and loss, and breakeven win rate of a trade from entry, stop-loss, and target prices.',
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
        <span className="text-[hsl(215,20%,70%)]">Risk/Reward Ratio Calculator</span>
      </nav>

      {/* Header */}
      <div className="max-w-3xl mb-10">
        <h1 className="text-4xl md:text-5xl font-bold mb-4 text-white">Risk/Reward Ratio Calculator</h1>
        <p className="text-lg text-slate-400">
          Score any trade before you take it. Enter your entry, stop-loss, and target to see the
          risk/reward ratio, the percentage you stand to gain or lose, and the win rate you need
          just to break even.
        </p>
      </div>

      {/* Calculator */}
      <RiskRewardCalculator />

      {/* Explainer */}
      <section className="max-w-3xl mt-14">
        <h2 className="text-2xl font-bold text-white mb-4">Why risk/reward matters</h2>
        <p className="text-slate-400 leading-relaxed mb-4">
          The risk/reward ratio compares how much you can lose against how much you can make on a
          trade. It works hand in hand with your win rate: a favorable ratio means you can lose
          more trades than you win and still come out ahead.
        </p>
        <ol className="text-slate-400 leading-relaxed space-y-2 mb-4 list-decimal pl-5">
          <li><strong className="text-slate-200">Risk</strong> = | entry price − stop-loss price |</li>
          <li><strong className="text-slate-200">Reward</strong> = | target price − entry price |</li>
          <li><strong className="text-slate-200">R:R ratio</strong> = reward ÷ risk</li>
          <li><strong className="text-slate-200">Breakeven win rate</strong> = 1 ÷ (1 + R:R)</li>
        </ol>
        <p className="text-slate-400 leading-relaxed">
          With an entry of $100, a stop at $95, and a target of $115, you risk $5 to make $15 — a
          1 : 3 ratio. At that ratio you only need to win 25% of your trades to break even, so a
          strategy that wins even a third of the time can be comfortably profitable.
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
            <p className="mt-1.5 text-sm text-slate-400">Find how many shares to buy based on your risk per trade.</p>
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
