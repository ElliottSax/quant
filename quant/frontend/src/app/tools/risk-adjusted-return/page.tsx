import type { Metadata } from 'next'
import Link from 'next/link'
import RiskAdjustedReturnCalculator from './RiskAdjustedReturnCalculator'

const url = 'https://quantengines.com/tools/risk-adjusted-return'

export const metadata: Metadata = {
  title: 'Sharpe, Sortino & Calmar Ratio Calculator | QuantEngines',
  description:
    'Free Sharpe ratio calculator, Sortino ratio calculator, and Calmar ratio calculator in one tool. Paste your return series and get all three risk-adjusted ratios plus an equity curve and max drawdown — with the exact conventions stated.',
  keywords: [
    'sharpe ratio calculator',
    'sortino ratio calculator',
    'calmar ratio calculator',
    'risk adjusted return calculator',
    'max drawdown calculator',
    'downside deviation calculator',
  ],
  alternates: { canonical: url },
  openGraph: {
    title: 'Sharpe, Sortino & Calmar Ratio Calculator',
    description: 'Paste a return series and get Sharpe, Sortino, and Calmar ratios, annualized volatility, and max drawdown, computed with explicitly stated conventions.',
    type: 'website',
    url,
  },
}

const faqs = [
  {
    q: 'What is a good Sharpe ratio?',
    a: 'As a rough, widely-cited guide: below 1.0 is considered subpar, 1.0-2.0 is good, 2.0-3.0 is very good, and above 3.0 is excellent — but these thresholds depend heavily on the return period and asset class, and a Sharpe ratio computed from 12 monthly returns carries far less statistical confidence than one from 5 years of daily returns. Use the win rate significance calculator\'s logic as a mental model: a great-looking ratio from a short series is weaker evidence than a good-looking ratio from a long one.',
  },
  {
    q: 'Why is my Sortino ratio different from other calculators?',
    a: "Sortino's downside deviation formula has a real ambiguity in practice: some calculators divide the sum of squared downside deviations by the count of losing periods only, others by the total period count. This calculator uses the total period count (the convention in Sortino & Price's original 1994 paper), which produces a smaller, more conservative downside deviation than the losing-periods-only version — if another calculator shows a notably higher Sortino on the same data, this is almost always why.",
  },
  {
    q: 'Why use Sortino instead of Sharpe?',
    a: "Sharpe's standard deviation penalizes upside volatility exactly as much as downside volatility — a strategy with occasional large gains looks 'riskier' by Sharpe even though large gains are not the risk anyone actually minds. Sortino only penalizes deviations below the target (the risk-free rate here), which better matches how most people intuitively think about risk.",
  },
  {
    q: "What does the Calmar ratio add that Sharpe and Sortino don't?",
    a: "Calmar uses maximum drawdown instead of a standard-deviation-based measure — the single worst peak-to-trough decline in the equity curve, which is what actually determines whether an investor can psychologically or financially tolerate holding a strategy through its worst period. A strategy can have a strong Sharpe ratio with volatility spread evenly across many small moves, yet still have a brutal single drawdown that Sharpe doesn't specifically flag — Calmar does.",
  },
  {
    q: 'How many return periods do I need for these ratios to mean anything?',
    a: "There's no universal cutoff, but the same statistical logic as the win rate significance calculator applies: a Sharpe ratio computed from 10-12 data points has enormous sampling uncertainty and can swing wildly with one or two outlier periods. As a practical floor, most practitioners want at least 30-36 periods (2.5-3 years of monthly data, or several months of daily data) before treating these ratios as more than a rough first look.",
  },
]

export default function RiskAdjustedReturnPage() {
  const webAppSchema = {
    '@context': 'https://schema.org',
    '@type': 'WebApplication',
    name: 'Sharpe, Sortino & Calmar Ratio Calculator',
    url,
    applicationCategory: 'FinanceApplication',
    operatingSystem: 'Any',
    offers: { '@type': 'Offer', price: '0', priceCurrency: 'USD' },
    description:
      'Paste a periodic return series and get Sharpe, Sortino, and Calmar ratios, annualized volatility, and max drawdown, with an equity curve chart.',
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
        <span className="text-[hsl(215,20%,70%)]">Sharpe, Sortino &amp; Calmar Ratio Calculator</span>
      </nav>

      <div className="max-w-3xl mb-10">
        <h1 className="text-4xl md:text-5xl font-bold mb-4 text-white">Sharpe, Sortino &amp; Calmar Ratio Calculator</h1>
        <p className="text-lg text-slate-400">
          Paste a period-over-period return series — from a backtest, a live strategy, or a fund's
          reported monthly returns — and get all three standard risk-adjusted ratios, annualized
          volatility, and max drawdown in one place, with every convention (sample vs. population
          standard deviation, downside-deviation denominator) stated explicitly.
        </p>
      </div>

      <RiskAdjustedReturnCalculator />

      <section className="max-w-3xl mt-14">
        <h2 className="text-2xl font-bold text-white mb-4">How the calculation works</h2>
        <p className="text-slate-400 leading-relaxed mb-4">
          Sharpe (Sharpe, 1966) divides the average excess return over the risk-free rate by the
          standard deviation of that excess return, then scales by the square root of the number of
          periods per year to annualize — the standard scaling for i.i.d. returns, since mean scales
          linearly with time while standard deviation scales with its square root.
        </p>
        <p className="text-slate-400 leading-relaxed mb-4">
          Sortino (Sortino &amp; Price, 1994) uses the same numerator but replaces total standard
          deviation with downside deviation: only periods where the excess return falls below the
          target (0, i.e. matching the risk-free rate) contribute to the sum of squares, and that
          sum is divided by the FULL period count — not just the count of losing periods, a
          distinction that materially changes the number and is a common source of disagreement
          between calculators.
        </p>
        <p className="text-slate-400 leading-relaxed">
          Calmar (Young, 1991) divides the compound annual growth rate of the full entered series by
          its maximum drawdown — the largest peak-to-trough decline in the compounded equity curve,
          computed by tracking the running peak and the percentage below it at every period.
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
          <Link href="/tools/win-rate-significance" className="group rounded-xl border border-[hsl(215,40%,18%)] bg-[hsl(220,55%,9%)] p-5 transition-all hover:border-indigo-500/60 hover:bg-[hsl(220,55%,11%)]">
            <h3 className="text-lg font-semibold text-white group-hover:text-indigo-400 transition-colors">Win Rate Significance Calculator</h3>
            <p className="mt-1.5 text-sm text-slate-400">Check whether a win rate is real edge or noise before trusting these ratios.</p>
          </Link>
          <Link href="/tools/kelly-criterion" className="group rounded-xl border border-[hsl(215,40%,18%)] bg-[hsl(220,55%,9%)] p-5 transition-all hover:border-indigo-500/60 hover:bg-[hsl(220,55%,11%)]">
            <h3 className="text-lg font-semibold text-white group-hover:text-indigo-400 transition-colors">Kelly Criterion Calculator</h3>
            <p className="mt-1.5 text-sm text-slate-400">Turn a win rate and win/loss ratio into an edge-optimal stake.</p>
          </Link>
          <Link href="/backtesting" className="group rounded-xl border border-[hsl(215,40%,18%)] bg-[hsl(220,55%,9%)] p-5 transition-all hover:border-indigo-500/60 hover:bg-[hsl(220,55%,11%)]">
            <h3 className="text-lg font-semibold text-white group-hover:text-indigo-400 transition-colors">Backtesting Engine</h3>
            <p className="mt-1.5 text-sm text-slate-400">Generate a real return series to paste in here.</p>
          </Link>
          <Link href="/tools" className="group rounded-xl border border-[hsl(215,40%,18%)] bg-[hsl(220,55%,9%)] p-5 transition-all hover:border-indigo-500/60 hover:bg-[hsl(220,55%,11%)]">
            <h3 className="text-lg font-semibold text-white group-hover:text-indigo-400 transition-colors">All Trading Tools</h3>
            <p className="mt-1.5 text-sm text-slate-400">Browse every free tool on QuantEngines.</p>
          </Link>
        </div>
      </section>

      <p className="max-w-3xl mt-14 text-xs text-[hsl(215,20%,45%)] leading-relaxed">
        This calculator performs arithmetic on the return series you paste in. It is not investment
        advice, does not evaluate any specific strategy or fund, and a strong historical ratio is
        not a guarantee of future performance.
      </p>
    </div>
  )
}
