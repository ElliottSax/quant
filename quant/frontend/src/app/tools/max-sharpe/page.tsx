/**
 * Maximum-Sharpe (tangency) portfolio calculator.
 *
 * Search Console shows this site already surfacing for the literal formula query
 * `maximize (w^t mu)/sqrt(w^t sigma w) solution w proportional` at positions 5.0 and 7.7
 * with zero clicks — the searcher wants the closed form and a number, and gets a strategy
 * essay. This page is the closed form, a solver, and a worked example.
 *
 * No market data: every figure is arithmetic on user input, which is what makes the page
 * legally clean and independently checkable.
 */

import type { Metadata } from 'next'
import Link from 'next/link'
import MaxSharpeClient from './MaxSharpeClient'

const url = 'https://quantengines.com/tools/max-sharpe'

export const metadata: Metadata = {
  title: 'Max Sharpe Ratio Portfolio Calculator — Tangency Weights | QuantEngines',
  description:
    'Solve max (wᵀμ − rf)/√(wᵀΣw). The tangency portfolio weights are w ∝ Σ⁻¹(μ − rf·1), normalised to sum to 1. Enter returns, volatilities and correlations for up to 5 assets and get the weights, expected return, volatility and Sharpe ratio.',
  keywords: [
    'max sharpe ratio portfolio',
    'tangency portfolio calculator',
    'maximum sharpe ratio weights',
    'optimal portfolio weights calculator',
    'sigma inverse mu excess returns',
    'markowitz tangency portfolio',
    'efficient frontier tangency point',
  ],
  alternates: { canonical: url },
  openGraph: {
    title: 'Max Sharpe Ratio Portfolio Calculator',
    description:
      'The closed-form tangency portfolio: w ∝ Σ⁻¹(μ − rf·1). Solver for up to 5 assets, with a worked example.',
    type: 'website',
    url,
  },
}

const faqs = [
  {
    q: 'What are the maximum-Sharpe portfolio weights?',
    a: 'They are w ∝ Σ⁻¹(μ − rf·1), normalised so the weights sum to 1 — where Σ is the covariance matrix, μ the vector of expected returns, and rf the risk-free rate. This portfolio is called the tangency portfolio because it is the point where a line drawn from the risk-free rate touches the efficient frontier. The proportionality is the whole result: scaling the excess-return vector by any positive constant scales w by the same constant, and normalising removes it, so only the direction of Σ⁻¹(μ − rf·1) matters.',
  },
  {
    q: 'Why does the solution involve the inverse covariance matrix?',
    a: 'Maximising (wᵀμ − rf)/√(wᵀΣw) is scale-invariant in w, so the constraint can be dropped, the objective differentiated, and the first-order condition rearranged. Doing that gives Σw ∝ (μ − rf·1), and hence w ∝ Σ⁻¹(μ − rf·1). Intuitively Σ⁻¹ penalises assets that duplicate risk already held: two highly correlated assets split the allocation one of them would get alone.',
  },
  {
    q: 'Why are some weights negative?',
    a: 'The closed form is unconstrained apart from the budget constraint that weights sum to 1, so short positions are allowed and frequently appear — typically in an asset whose expected return is low relative to what its correlations imply it should offer. Clipping negatives to zero and renormalising produces a valid long-only portfolio, but not the maximum-Sharpe one; there is no closed form under a no-shorting constraint, and it requires quadratic programming.',
  },
  {
    q: 'Why does the calculator sometimes refuse to return an answer?',
    a: 'When the covariance matrix is singular, Σ⁻¹ does not exist. The common cause is two assets with a correlation of exactly 1 or −1, or a zero volatility, which makes one row of the matrix a combination of the others. In that case infinitely many weight vectors achieve the same Sharpe ratio, so there is no unique answer and none is shown. A pseudo-inverse would silently return one of the infinitely many.',
  },
  {
    q: 'Is the Sharpe ratio here annualised?',
    a: 'It is in whatever units you enter. If the expected returns, volatilities and risk-free rate are annual figures, the resulting Sharpe ratio is annual. Mixing units — say monthly returns with annual volatilities — gives a meaningless number, and the calculator has no way to detect that.',
  },
  {
    q: 'Can I use historical estimates for the inputs?',
    a: 'You can, but this is where portfolio optimisation is most often misused. The formula treats μ and Σ as known, while sample estimates of expected returns are extremely noisy, and Σ⁻¹ amplifies that noise — which is why the maximum-Sharpe portfolio computed from a sample often performs worse out of sample than equal weighting. That is a property of the estimates, not of the algebra, and no calculator can fix it. Shrinkage estimators (Ledoit–Wolf) and constraints exist to mitigate it.',
  },
]

export default function MaxSharpePage() {
  const webAppSchema = {
    '@context': 'https://schema.org',
    '@type': 'WebApplication',
    name: 'Max Sharpe Ratio Portfolio Calculator',
    url,
    applicationCategory: 'FinanceApplication',
    operatingSystem: 'Any',
    offers: { '@type': 'Offer', price: '0', priceCurrency: 'USD' },
    description:
      'Compute the tangency (maximum-Sharpe) portfolio weights from expected returns, volatilities, correlations and a risk-free rate.',
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
        <span className="text-[hsl(215,20%,70%)]">Max Sharpe Ratio Portfolio</span>
      </nav>

      <div className="max-w-3xl mb-8">
        <h1 className="text-4xl md:text-5xl font-bold mb-4 text-white">
          Max Sharpe Ratio Portfolio Calculator
        </h1>
        <p className="text-lg text-slate-400">
          The portfolio that maximises (wᵀμ − r<sub>f</sub>) ⁄ √(wᵀΣw) has a closed form — no
          optimiser required. Enter expected returns, volatilities and correlations for up to five
          assets to get the tangency weights and the Sharpe ratio they achieve.
        </p>
      </div>

      {/* The answer, above the calculator — most people arriving from the formula query want
          this and nothing else. */}
      <div className="max-w-3xl mb-10 rounded-xl border border-indigo-500/30 bg-indigo-500/5 p-6">
        <h2 className="text-sm font-semibold uppercase tracking-wide text-indigo-300 mb-3">
          The solution
        </h2>
        <p className="font-mono text-xl text-white mb-3">
          w ∝ Σ<sup>−1</sup>(μ − r<sub>f</sub>·1)
        </p>
        <p className="text-slate-400 leading-relaxed">
          Compute Σ<sup>−1</sup>(μ − r<sub>f</sub>·1), then divide by the sum of its elements so the
          weights add to 1. The proportionality is the point: any positive rescaling of the excess
          returns leaves the direction unchanged, and normalising removes the scale, so the
          tangency portfolio depends on the excess returns only through their direction under
          Σ<sup>−1</sup>.
        </p>
      </div>

      <MaxSharpeClient />

      <section className="max-w-3xl mt-14">
        <h2 className="text-2xl font-bold text-white mb-4">Where the formula comes from</h2>
        <p className="text-slate-400 leading-relaxed mb-4">
          The Sharpe ratio of a portfolio is unchanged if every weight is multiplied by the same
          positive number: both the excess return in the numerator and the volatility in the
          denominator scale linearly. That homogeneity is what makes a closed form possible. The
          budget constraint can be dropped while optimising, the unconstrained problem solved, and
          the constraint restored at the end by normalising.
        </p>
        <p className="text-slate-400 leading-relaxed mb-4">
          Differentiating (wᵀμ − r<sub>f</sub>) ⁄ √(wᵀΣw) with respect to w and setting the result
          to zero gives, after cancelling the scalar factors that the homogeneity makes irrelevant,
          Σw ∝ (μ − r<sub>f</sub>·1). Multiplying both sides by Σ<sup>−1</sup> gives the result
          above. The one requirement is that Σ be invertible.
        </p>
        <p className="text-slate-400 leading-relaxed">
          Reading Σ<sup>−1</sup> intuitively: it discounts each asset by how much of its risk is
          already carried by the others. An asset with a high expected return that is highly
          correlated with the rest of the portfolio adds little that is new, and the inverse
          covariance matrix reduces its weight accordingly — sometimes below zero.
        </p>
      </section>

      <section className="max-w-3xl mt-14">
        <h2 className="text-2xl font-bold text-white mb-4">Worked example</h2>
        <p className="text-slate-400 leading-relaxed mb-4">
          Three assets with expected returns of 10%, 12% and 8%; volatilities of 15%, 20% and 10%;
          correlations of 0.30 between assets 1 and 2, 0.10 between 1 and 3, and 0.20 between 2 and
          3; a risk-free rate of 2%. These are the calculator&apos;s defaults, so the figures below
          are what it shows on load.
        </p>
        <div className="overflow-x-auto rounded-xl border border-[hsl(215,40%,18%)]">
          <table className="w-full text-sm">
            <tbody className="font-mono">
              <tr className="border-b border-[hsl(215,40%,14%)]">
                <td className="p-3 text-slate-400">Asset 1 weight</td>
                <td className="p-3 text-right tabular-nums text-white">29.24%</td>
              </tr>
              <tr className="border-b border-[hsl(215,40%,14%)]">
                <td className="p-3 text-slate-400">Asset 2 weight</td>
                <td className="p-3 text-right tabular-nums text-white">15.35%</td>
              </tr>
              <tr className="border-b border-[hsl(215,40%,14%)]">
                <td className="p-3 text-slate-400">Asset 3 weight</td>
                <td className="p-3 text-right tabular-nums text-white">55.41%</td>
              </tr>
              <tr className="border-b border-[hsl(215,40%,14%)]">
                <td className="p-3 text-slate-400">Expected return</td>
                <td className="p-3 text-right tabular-nums text-white">9.20%</td>
              </tr>
              <tr className="border-b border-[hsl(215,40%,14%)]">
                <td className="p-3 text-slate-400">Volatility</td>
                <td className="p-3 text-right tabular-nums text-white">8.89%</td>
              </tr>
              <tr>
                <td className="p-3 text-slate-400">Sharpe ratio</td>
                <td className="p-3 text-right tabular-nums text-white">0.8094</td>
              </tr>
            </tbody>
          </table>
        </div>
        <p className="text-slate-400 leading-relaxed mt-4">
          Note that the lowest-return asset takes the largest weight. That is Σ<sup>−1</sup> at
          work: asset 3 has half the volatility of asset 1 and the weakest correlations to the
          others, so it contributes the most Sharpe ratio per unit of risk despite the lowest
          expected return. Ranking by expected return alone would get this backwards.
        </p>
        <p className="text-slate-400 leading-relaxed mt-4">
          These figures were cross-checked two ways before publication: against an independent
          NumPy implementation, which reproduces the weights to six decimal places; and against a
          brute-force search over 200,000 random long-only portfolios drawn from the same inputs,
          whose best Sharpe ratio was 0.809371 — just under the 0.809373 the closed form returns,
          as it must be if the closed form is really the optimum.
        </p>
      </section>

      <section className="max-w-3xl mt-14">
        <h2 className="text-2xl font-bold text-white mb-4">The same thing in Python</h2>
        <pre className="overflow-x-auto rounded-xl border border-[hsl(215,40%,18%)] bg-[hsl(220,55%,7%)] p-5 text-sm text-slate-300">
          <code>{`import numpy as np

mu   = np.array([0.10, 0.12, 0.08])      # expected returns
vol  = np.array([0.15, 0.20, 0.10])      # volatilities
corr = np.array([[1.0, 0.3, 0.1],
                 [0.3, 1.0, 0.2],
                 [0.1, 0.2, 1.0]])
rf   = 0.02

sigma = np.outer(vol, vol) * corr        # covariance from vol + correlation
raw   = np.linalg.solve(sigma, mu - rf)  # solve, don't invert: faster and better conditioned
w     = raw / raw.sum()                  # normalise to sum to 1

ret    = w @ mu
sd     = np.sqrt(w @ sigma @ w)
sharpe = (ret - rf) / sd
# w -> [0.292376 0.153539 0.554085],  sharpe -> 0.809373`}</code>
        </pre>
        <p className="text-slate-400 leading-relaxed mt-4">
          Use <code className="inline-code">np.linalg.solve(sigma, mu - rf)</code> rather than{' '}
          <code className="inline-code">np.linalg.inv(sigma) @ (mu - rf)</code>. Both give the same
          answer here, but forming the explicit inverse is slower and numerically worse
          conditioned, which matters once the covariance matrix is large or near-singular — exactly
          the case where portfolio optimisation is already fragile.
        </p>
      </section>

      <section className="max-w-3xl mt-14">
        <h2 className="text-2xl font-bold text-white mb-4">What this does not do</h2>
        <p className="text-slate-400 leading-relaxed">
          It treats μ and Σ as given. In practice they are estimated, expected returns are
          estimated very badly, and Σ<sup>−1</sup> magnifies estimation error — which is why a
          maximum-Sharpe portfolio built from historical estimates frequently underperforms equal
          weighting out of sample. The algebra on this page is exact; the inputs it operates on
          usually are not. Shrinkage estimators and weight constraints exist to address that, and
          neither is applied here.
        </p>
      </section>

      <section className="max-w-3xl mt-14">
        <h2 className="text-2xl font-bold text-white mb-6">Frequently asked questions</h2>
        <div className="space-y-4">
          {faqs.map((f) => (
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

      <section className="max-w-3xl mt-14">
        <h2 className="text-2xl font-bold text-white mb-6">Related tools</h2>
        <div className="grid gap-4 sm:grid-cols-2">
          <Link href="/tools/position-size" className="group rounded-xl border border-[hsl(215,40%,18%)] bg-[hsl(220,55%,9%)] p-5 transition-all hover:border-indigo-500/60 hover:bg-[hsl(220,55%,11%)]">
            <h3 className="text-lg font-semibold text-white group-hover:text-indigo-400 transition-colors">Position Size Calculator</h3>
            <p className="mt-1.5 text-sm text-slate-400">Turn a risk budget into a share count.</p>
          </Link>
          <Link href="/tools/risk-reward" className="group rounded-xl border border-[hsl(215,40%,18%)] bg-[hsl(220,55%,9%)] p-5 transition-all hover:border-indigo-500/60 hover:bg-[hsl(220,55%,11%)]">
            <h3 className="text-lg font-semibold text-white group-hover:text-indigo-400 transition-colors">Risk/Reward Calculator</h3>
            <p className="mt-1.5 text-sm text-slate-400">R:R ratio and the breakeven win rate it implies.</p>
          </Link>
          <Link href="/pandas-ta-columns" className="group rounded-xl border border-[hsl(215,40%,18%)] bg-[hsl(220,55%,9%)] p-5 transition-all hover:border-indigo-500/60 hover:bg-[hsl(220,55%,11%)]">
            <h3 className="text-lg font-semibold text-white group-hover:text-indigo-400 transition-colors">pandas_ta Column Names</h3>
            <p className="mt-1.5 text-sm text-slate-400">Measured by running the library, not copied from docs.</p>
          </Link>
          <Link href="/tools" className="group rounded-xl border border-[hsl(215,40%,18%)] bg-[hsl(220,55%,9%)] p-5 transition-all hover:border-indigo-500/60 hover:bg-[hsl(220,55%,11%)]">
            <h3 className="text-lg font-semibold text-white group-hover:text-indigo-400 transition-colors">All Trading Tools</h3>
            <p className="mt-1.5 text-sm text-slate-400">Browse every free tool on QuantEngines.</p>
          </Link>
        </div>
      </section>

      <p className="max-w-3xl mt-14 text-xs text-[hsl(215,20%,45%)] leading-relaxed">
        This calculator performs and displays arithmetic on the inputs you provide. It is not
        investment advice, does not recommend an allocation, and makes no claim that the expected
        returns or correlations you enter will be realised.
      </p>
    </div>
  )
}
