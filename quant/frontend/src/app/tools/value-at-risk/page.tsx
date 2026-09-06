import type { Metadata } from 'next'
import Link from 'next/link'
import ValueAtRiskCalculator from './ValueAtRiskCalculator'

const url = 'https://quantengines.com/tools/value-at-risk'

export const metadata: Metadata = {
  title: 'VaR & CVaR Calculator — Value at Risk / Expected Shortfall | QuantEngines',
  description:
    'Free Value at Risk (VaR) and Conditional VaR (CVaR / Expected Shortfall) calculator. Paste a return series and get parametric and historical estimates side by side, with a fat-tail gap check. No signup required.',
  keywords: [
    'value at risk calculator',
    'var calculator',
    'conditional value at risk',
    'expected shortfall calculator',
    'cvar calculator',
    'historical var',
    'parametric var',
    'portfolio risk calculator',
  ],
  alternates: { canonical: url },
  openGraph: {
    title: 'VaR & CVaR Calculator',
    description:
      'Parametric and historical Value at Risk and Expected Shortfall, computed side by side from a pasted return series, with the gap between them surfaced as a fat-tail check.',
    type: 'website',
    url,
  },
}

const faqs = [
  {
    q: 'What is Value at Risk (VaR)?',
    a: 'VaR at confidence level c is a dollar loss threshold: over the chosen horizon, there is a (1−c) chance the portfolio loses more than the VaR figure. A 95% one-day VaR of $10,000 means a loss bigger than $10,000 is expected on roughly 5% of days, based on the return series or distributional assumption used to compute it. VaR says nothing about how much worse that 5% of outcomes could get — that is what CVaR is for.',
  },
  {
    q: 'What is Conditional VaR (CVaR) / Expected Shortfall, and how is it different from VaR?',
    a: "CVaR is the average loss in exactly the scenarios where VaR is already breached — the mean of the tail beyond the VaR threshold, not just the threshold itself. CVaR is always at least as large as VaR at the same confidence level. Two return series can share an identical VaR while having very different CVaR, if one has a hard cutoff past the threshold and the other has a long, thin tail of much larger losses — CVaR is what distinguishes them, and it's the metric Basel III capital rules moved toward for exactly this reason.",
  },
  {
    q: 'Why does this calculator show two different VaR numbers?',
    a: "Parametric VaR assumes returns are normally distributed and derives VaR from just the mean and standard deviation of the series in closed form. Historical VaR makes no distributional assumption at all — it reads the actual empirical quantile out of the returns you pasted. Real return series are usually fatter-tailed than a normal distribution (more frequent large moves than a bell curve predicts), so historical VaR often comes out larger than parametric VaR. When it does, that gap is the finding: it means the parametric number is understating real tail risk, and the historical estimate — despite being noisier at small sample sizes — is the more trustworthy one for this data.",
  },
  {
    q: 'Why is my historical VaR unreliable with a small return series?',
    a: 'A 99% VaR is, by definition, about the worst ~1% of outcomes. With 50 observations, that is half of one data point — the calculator is extrapolating a tail estimate from essentially the single worst return in your sample. This calculator surfaces the expected number of tail observations (n × (1−c)) directly and flags it explicitly when it drops below 1, rather than presenting a falsely precise percentile. More data — or a lower confidence level — narrows this.',
  },
  {
    q: 'How does this differ from the Sharpe/Sortino/Calmar calculator?',
    a: 'The Sharpe/Sortino/Calmar calculator (risk-adjusted-return) measures realized, backward-looking performance per unit of risk already taken. This calculator instead asks a forward-looking question: given this return history, how large a loss should the portfolio be prepared for over the next period, at a stated confidence level? Both read the same kind of input — a pasted return series — but answer different questions.',
  },
  {
    q: 'What are the limitations of this model?',
    a: "Parametric VaR/CVaR assume returns are i.i.d. and normally distributed — real markets exhibit volatility clustering, fat tails, and skew that this understates, which is exactly why the historical method is shown alongside it. Historical VaR/CVaR assume the future resembles the exact sample pasted in, with no adjustment for regime change, and are estimated from very few points at high confidence levels or small samples. Neither method accounts for intra-horizon rebalancing, changing position sizes, or tail correlation across a multi-asset book beyond what's already embedded in a single return series. Treat the output as a risk-communication figure, not a guarantee of maximum loss.",
  },
]

export default function ValueAtRiskPage() {
  const webAppSchema = {
    '@context': 'https://schema.org',
    '@type': 'WebApplication',
    name: 'VaR & CVaR Calculator',
    url,
    applicationCategory: 'FinanceApplication',
    operatingSystem: 'Any',
    offers: { '@type': 'Offer', price: '0', priceCurrency: 'USD' },
    description:
      'Calculate parametric and historical Value at Risk (VaR) and Conditional VaR (CVaR / Expected Shortfall) from a pasted return series and portfolio value.',
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
        <span className="text-[hsl(215,20%,70%)]">VaR & CVaR Calculator</span>
      </nav>

      {/* Header */}
      <div className="max-w-3xl mb-10">
        <h1 className="text-4xl md:text-5xl font-bold mb-4 text-white">Value at Risk (VaR) & CVaR Calculator</h1>
        <p className="text-lg text-slate-400">
          Paste a periodic return series and a portfolio value to get Value at Risk and Conditional
          VaR (Expected Shortfall) computed two ways — a parametric (normal-distribution) estimate
          and a historical (empirical) estimate — side by side, so a gap between them is a signal
          instead of hidden behind one number. No trade history or market data is read; everything
          is arithmetic over the numbers you type in.
        </p>
      </div>

      {/* Calculator */}
      <ValueAtRiskCalculator />

      {/* Explainer */}
      <section className="max-w-3xl mt-14">
        <h2 className="text-2xl font-bold text-white mb-4">How the calculation works</h2>
        <p className="text-slate-400 leading-relaxed mb-4">
          Parametric (variance-covariance) VaR assumes periodic returns are i.i.d. normal with mean
          μ and standard deviation σ, estimated from the pasted series (Jorion, 2006):
        </p>
        <div className="rounded-lg border border-[hsl(215,40%,18%)] bg-[hsl(220,55%,7%)] p-4 font-mono text-sm text-slate-300 mb-4">
          VaR_c = (z_c · σ − μ) · √t · V₀
        </div>
        <p className="text-slate-400 leading-relaxed mb-4">
          where z_c = Φ⁻¹(c) is the standard-normal quantile at confidence c (1.2816 / 1.6449 /
          2.3263 for 90% / 95% / 99%) and √t scales the one-period estimate to a t-period horizon,
          the same square-root-of-time convention used elsewhere on this site for annualization.
          The parametric CVaR follows from the standard truncated-normal tail-mean identity
          (McNeil, Frey & Embrechts, 2015, Prop. 2.16):
        </p>
        <div className="rounded-lg border border-[hsl(215,40%,18%)] bg-[hsl(220,55%,7%)] p-4 font-mono text-sm text-slate-300 mb-4">
          CVaR_c = (σ · φ(z_c) / (1 − c) − μ) · √t · V₀
        </div>
        <p className="text-slate-400 leading-relaxed mb-4">
          Historical VaR skips the normality assumption entirely and reads the (1−c) quantile
          straight out of the empirical return series, using linear-interpolation quantile
          estimation ("Type 7" — Hyndman &amp; Fan, 1996 — the default in R's <code>quantile()</code> and
          NumPy's <code>np.percentile</code>):
        </p>
        <div className="rounded-lg border border-[hsl(215,40%,18%)] bg-[hsl(220,55%,7%)] p-4 font-mono text-sm text-slate-300 mb-4">
          VaR_c = −Q₍₁₋c₎(returns) · V₀
        </div>
        <p className="text-slate-400 leading-relaxed">
          Historical CVaR (Rockafellar &amp; Uryasev, 2000) is the mean of every observed return at or
          below that threshold, negated and scaled by portfolio value. Because it makes no
          distributional assumption, historical VaR/CVaR is only as good as the sample pasted in —
          the calculator surfaces exactly how many observations landed in the tail so that isn't
          hidden.
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
          <Link href="/tools/risk-adjusted-return" className="group rounded-xl border border-[hsl(215,40%,18%)] bg-[hsl(220,55%,9%)] p-5 transition-all hover:border-indigo-500/60 hover:bg-[hsl(220,55%,11%)]">
            <h3 className="text-lg font-semibold text-white group-hover:text-indigo-400 transition-colors">Sharpe / Sortino / Calmar Calculator</h3>
            <p className="mt-1.5 text-sm text-slate-400">Realized risk-adjusted performance from the same kind of pasted return series.</p>
          </Link>
          <Link href="/tools/max-sharpe" className="group rounded-xl border border-[hsl(215,40%,18%)] bg-[hsl(220,55%,9%)] p-5 transition-all hover:border-indigo-500/60 hover:bg-[hsl(220,55%,11%)]">
            <h3 className="text-lg font-semibold text-white group-hover:text-indigo-400 transition-colors">Max Sharpe Ratio Portfolio</h3>
            <p className="mt-1.5 text-sm text-slate-400">Tangency portfolio weights from expected returns and a covariance matrix.</p>
          </Link>
          <Link href="/tools/kelly-criterion" className="group rounded-xl border border-[hsl(215,40%,18%)] bg-[hsl(220,55%,9%)] p-5 transition-all hover:border-indigo-500/60 hover:bg-[hsl(220,55%,11%)]">
            <h3 className="text-lg font-semibold text-white group-hover:text-indigo-400 transition-colors">Kelly Criterion Calculator</h3>
            <p className="mt-1.5 text-sm text-slate-400">Edge-optimal position size from win rate and win/loss ratio.</p>
          </Link>
          <Link href="/backtesting" className="group rounded-xl border border-[hsl(215,40%,18%)] bg-[hsl(220,55%,9%)] p-5 transition-all hover:border-indigo-500/60 hover:bg-[hsl(220,55%,11%)]">
            <h3 className="text-lg font-semibold text-white group-hover:text-indigo-400 transition-colors">Backtesting Engine</h3>
            <p className="mt-1.5 text-sm text-slate-400">Generate a real return series from historical data instead of guessing one.</p>
          </Link>
          <Link href="/tools" className="group rounded-xl border border-[hsl(215,40%,18%)] bg-[hsl(220,55%,9%)] p-5 transition-all hover:border-indigo-500/60 hover:bg-[hsl(220,55%,11%)]">
            <h3 className="text-lg font-semibold text-white group-hover:text-indigo-400 transition-colors">All Trading Tools</h3>
            <p className="mt-1.5 text-sm text-slate-400">Browse every free tool on QuantEngines.</p>
          </Link>
        </div>
      </section>

      <p className="max-w-3xl mt-14 text-xs text-[hsl(215,20%,45%)] leading-relaxed">
        This calculator performs and displays arithmetic on the inputs you provide, using the
        parametric-normal and historical-empirical VaR/CVaR models. It is not investment advice,
        does not read live market data or your positions, and makes no claim about a portfolio's
        future losses beyond what the entered return series and stated assumptions imply.
      </p>
    </div>
  )
}
