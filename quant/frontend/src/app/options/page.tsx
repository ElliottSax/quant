import type { Metadata } from 'next'
import Link from 'next/link'
import OptionsCalculator from './OptionsCalculator'

const url = 'https://quantengines.com/options'

export const metadata: Metadata = {
  title: 'Black-Scholes Options Calculator — Price & Greeks | QuantEngines',
  description:
    'Free Black-Scholes options calculator. Enter spot, strike, expiry, volatility, and rate to get the theoretical value plus delta, gamma, vega, theta, and rho. Runs entirely on your inputs, no signup required.',
  keywords: [
    'black scholes calculator',
    'options calculator',
    'option greeks calculator',
    'delta gamma vega theta calculator',
    'option pricing calculator',
    'theoretical option value',
  ],
  alternates: { canonical: url },
  openGraph: {
    title: 'Black-Scholes Options Calculator',
    description:
      'Price a European call or put and see all five Greeks, computed from the inputs you supply.',
    type: 'website',
    url,
  },
}

const faqs = [
  {
    q: 'Where does this calculator get its data?',
    a: 'It does not use any market data. Every figure on the page is computed from the spot price, strike, days to expiry, volatility, and risk-free rate you type in. That means you can check the output against any Black-Scholes reference, and it also means the volatility used is the one you chose, not one observed in the market.',
  },
  {
    q: 'How accurate is the pricing?',
    a: 'For the standard reference case of spot 100, strike 100, rate 5%, volatility 20%, and one year to expiry, it returns a call value of $10.4506 and a put value of $5.5735, matching published Black-Scholes values. Call and put outputs satisfy put-call parity to floating-point precision, and the Greeks match numerical differentiation of the price to at least six decimal places.',
  },
  {
    q: 'Does it handle American options or dividends?',
    a: 'No. This is the European, non-dividend-paying Black-Scholes model. American options carry early-exercise value and dividend-paying underlyings need an adjusted model, so the value shown here will differ from the traded price in both cases.',
  },
  {
    q: 'What units are the Greeks in?',
    a: 'Delta is the change in option value per $1 change in spot, and gamma the change in delta per $1 change in spot. Vega is per one percentage point of volatility, rho is per one percentage point of interest rate, and theta is per calendar day. All values are per share; a standard US equity contract covers 100 shares.',
  },
  {
    q: 'What is the difference between the two P/L lines?',
    a: 'The "at expiry" line is the payoff once all time value has gone: intrinsic value minus the premium. The "today" line is the Black-Scholes value at that spot price with the days to expiry, volatility, and rate you entered left unchanged, minus the premium. The two converge as days to expiry approaches zero.',
  },
]

export default function OptionsPage() {
  const webAppSchema = {
    '@context': 'https://schema.org',
    '@type': 'WebApplication',
    name: 'Black-Scholes Options Calculator',
    url,
    applicationCategory: 'FinanceApplication',
    operatingSystem: 'Any',
    offers: { '@type': 'Offer', price: '0', priceCurrency: 'USD' },
    description:
      'Calculate the Black-Scholes theoretical value and the Greeks of a European call or put from spot, strike, expiry, volatility, and risk-free rate.',
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
    <div className="space-y-8">
      <script type="application/ld+json" dangerouslySetInnerHTML={{ __html: JSON.stringify(webAppSchema) }} />
      <script type="application/ld+json" dangerouslySetInnerHTML={{ __html: JSON.stringify(faqSchema) }} />

      <nav className="text-sm text-[hsl(215,20%,55%)]">
        <Link href="/tools" className="hover:text-indigo-400">Tools</Link>
        <span className="mx-2">/</span>
        <span className="text-[hsl(215,20%,70%)]">Options Calculator</span>
      </nav>

      <div className="max-w-3xl">
        <h1 className="text-4xl font-bold mb-3 gradient-text">Black-Scholes Options Calculator</h1>
        <p className="text-muted-foreground text-lg">
          Theoretical value and the full set of Greeks for a European call or put, computed from
          the inputs you supply. No market data is used and none is displayed — change any input
          and every figure below recalculates from the formula.
        </p>
      </div>

      <OptionsCalculator />

      {/* FAQ */}
      <section className="max-w-3xl pt-6">
        <h2 className="text-2xl font-bold mb-6">Frequently asked questions</h2>
        <div className="space-y-4">
          {faqs.map((f) => (
            <details key={f.q} className="group glass-strong rounded-xl p-5">
              <summary className="cursor-pointer font-semibold list-none flex justify-between items-center gap-4">
                {f.q}
                <span className="text-indigo-400 group-open:rotate-45 transition-transform shrink-0">+</span>
              </summary>
              <p className="mt-3 text-muted-foreground leading-relaxed">{f.a}</p>
            </details>
          ))}
        </div>
      </section>

      {/* Related tools */}
      <section className="max-w-3xl">
        <h2 className="text-2xl font-bold mb-6">Related tools</h2>
        <div className="grid gap-4 sm:grid-cols-2">
          <Link href="/tools/position-size" className="group glass-strong rounded-xl p-5 transition-all hover:border-indigo-500/60">
            <h3 className="text-lg font-semibold group-hover:text-indigo-400 transition-colors">Position Size Calculator</h3>
            <p className="mt-1.5 text-sm text-muted-foreground">Work out a share count from account size, risk per trade, entry, and stop.</p>
          </Link>
          <Link href="/tools/risk-reward" className="group glass-strong rounded-xl p-5 transition-all hover:border-indigo-500/60">
            <h3 className="text-lg font-semibold group-hover:text-indigo-400 transition-colors">Risk/Reward Ratio Calculator</h3>
            <p className="mt-1.5 text-sm text-muted-foreground">Reward-to-risk ratio and the breakeven win rate it implies.</p>
          </Link>
          <Link href="/backtesting" className="group glass-strong rounded-xl p-5 transition-all hover:border-indigo-500/60">
            <h3 className="text-lg font-semibold group-hover:text-indigo-400 transition-colors">Backtesting Engine</h3>
            <p className="mt-1.5 text-sm text-muted-foreground">Test a strategy against historical market data.</p>
          </Link>
          <Link href="/tools" className="group glass-strong rounded-xl p-5 transition-all hover:border-indigo-500/60">
            <h3 className="text-lg font-semibold group-hover:text-indigo-400 transition-colors">All Trading Tools</h3>
            <p className="mt-1.5 text-sm text-muted-foreground">Browse every free tool on QuantEngines.</p>
          </Link>
        </div>
      </section>

      <p className="text-xs text-[hsl(215,20%,45%)] max-w-3xl leading-relaxed">
        This calculator performs and displays arithmetic on the inputs you provide. It is not
        investment advice, does not recommend any option, strike, or position, and makes no claim
        about what any option is worth in the market or how any trade will perform.
      </p>
    </div>
  )
}
