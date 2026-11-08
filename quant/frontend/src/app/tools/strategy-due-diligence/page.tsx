import type { Metadata } from 'next';
import Link from 'next/link';
import StrategyDiligenceTool from './StrategyDiligenceTool';

const url = 'https://quantengines.com/tools/strategy-due-diligence';

export const metadata: Metadata = {
  title: 'Quant Strategy Due Diligence Checklist & Sharpe Check | QuantEngines',
  description:
    'Evaluate a trading strategy or quant fund with an 18-point evidence checklist and a statistical check of its Sharpe ratio. Every formula and assumption shown.',
  keywords: [
    'quant strategy due diligence',
    'strategy due diligence checklist',
    'quant fund evaluation',
    'sharpe ratio significance',
    'probabilistic sharpe ratio',
    'deflated sharpe ratio',
    'minimum track record length',
    'overfitting trading strategy',
  ],
  alternates: { canonical: url },
  openGraph: {
    title: 'Quant Strategy Due Diligence Checklist & Sharpe Check',
    description:
      'An 18-point evidence checklist and a statistical sanity check for any claimed Sharpe ratio, with every formula and assumption shown.',
    type: 'website',
    url,
  },
};

const faqs = [
  {
    q: 'What does the 95% confidence interval for the Sharpe ratio tell me?',
    a: 'It is arithmetic from the inputs you entered: per-period Sharpe plus or minus 1.96 times its standard error, scaled back to annual terms. The standard error is sqrt(D/(T minus 1)) where D is 1 minus skew times Sharpe plus ((kurtosis minus 1)/4) times Sharpe squared. If the interval includes zero, the Sharpe is not statistically distinguishable from zero at the 95% level under the stated skew and kurtosis.',
  },
  {
    q: 'What is the Probabilistic Sharpe Ratio and how is it computed?',
    a: 'PSR is from Bailey and Lopez de Prado (2012) The Sharpe Ratio Efficient Frontier. It is Phi((SR minus SRstar) times sqrt(T minus 1) over sqrt(D)), where SR is the per-period Sharpe, SRstar is the benchmark (zero here), T is the number of observations, D is the same adjustment as above, and Phi is the standard normal CDF. A modest Sharpe from a short or fat-tailed sample can have a low PSR.',
  },
  {
    q: 'What is the Deflated Sharpe Ratio and why does it adjust for trials?',
    a: 'DSR is from Bailey and Lopez de Prado (2014) The Deflated Sharpe Ratio. It is the PSR with the benchmark set to SR0, the expected maximum Sharpe from N independent trials. SR0 is sqrt(V) times ((1 minus gamma) PhiInv(1 minus 1/N) plus gamma PhiInv(1 minus 1/(N e))) with gamma the Euler-Mascheroni constant. Using DSR is a multiple-testing correction: trying many variants raises the bar for what counts as evidence.',
  },
  {
    q: 'How is the minimum track record length calculated?',
    a: 'It is 1 plus D times (PhiInv(0.95) over per-period Sharpe) squared observations, divided by periods per year for years. It answers how long a track record must be for 95% confidence that the true Sharpe exceeds zero, holding the observed Sharpe, skew and kurtosis fixed. If the per-period Sharpe is not positive, the required length is not attainable.',
  },
  {
    q: 'Why do skewness and kurtosis change the answer if they do not change the Sharpe?',
    a: 'Skew and kurtosis do not change the point estimate of Sharpe, but they widen its standard error through D. Negative skew and high kurtosis make the same Sharpe less trustworthy. This follows directly from the PSR standard-error formula and is why two strategies with the same Sharpe and track length can have very different PSRs.',
  },
  {
    q: 'Does this tool prove that a strategy works?',
    a: 'No. It only checks whether the claimed Sharpe is strong enough to be distinguished from luck and from selection bias, given the length and shape of the data. A checklist cannot establish that a return stream will continue, that costs were reported honestly, or that the data were not otherwise selected. This tool is educational and is not investment advice. Nothing here recommends buying or selling anything.',
  },
];

export default function StrategyDueDiligencePage() {
  const webAppSchema = {
    '@context': 'https://schema.org',
    '@type': 'WebApplication',
    name: 'Strategy Due Diligence Checklist & Sharpe Check',
    url,
    applicationCategory: 'FinanceApplication',
    operatingSystem: 'Any',
    offers: { '@type': 'Offer', price: '0', priceCurrency: 'USD' },
    description:
      'An 18-point evidence checklist for trading strategies and quant funds plus a statistical sanity check for any claimed Sharpe ratio with confidence interval, Probabilistic Sharpe Ratio, Deflated Sharpe Ratio and minimum track record length.',
  };

  const faqSchema = {
    '@context': 'https://schema.org',
    '@type': 'FAQPage',
    mainEntity: faqs.map((f) => ({
      '@type': 'Question',
      name: f.q,
      acceptedAnswer: { '@type': 'Answer', text: f.a },
    })),
  };

  return (
    <div className="container mx-auto px-4 py-12">
      <script type="application/ld+json" dangerouslySetInnerHTML={{ __html: JSON.stringify(webAppSchema) }} />
      <script type="application/ld+json" dangerouslySetInnerHTML={{ __html: JSON.stringify(faqSchema) }} />

      <nav className="text-sm text-[hsl(215,20%,55%)] mb-6">
        <Link href="/tools" className="hover:text-indigo-400">Tools</Link>
        <span className="mx-2">/</span>
        <span className="text-[hsl(215,20%,70%)]">Strategy Due Diligence</span>
      </nav>

      <div className="max-w-3xl mb-10">
        <h1 className="text-4xl md:text-5xl font-bold mb-4 text-white">Quant Strategy Due Diligence</h1>
        <p className="text-lg text-slate-400 leading-relaxed">
          A two-part check for anyone evaluating a trading strategy or quant fund. First, an 18-point evidence checklist organised into five groups. Second, a statistical sanity check that asks whether the claimed Sharpe ratio is believable given the sample size, skewness and kurtosis, and how many variants were tried.
        </p>
      </div>

      <StrategyDiligenceTool />

      <section className="max-w-3xl mt-14">
        <h2 className="text-2xl font-bold text-white mb-4">How the calculation works</h2>
        <p className="text-slate-400 leading-relaxed mb-4">
          The checklist covers evidence of an edge, overfitting and selection, data and implementation, risk and capacity, and governance. Each question is phrased so that Yes is the reassuring answer. The tool reports counts of Yes, No and Unknown overall and per group, and lists the direct questions to put to the manager or author for every No or Unknown. There is no overall numeric score and no letter grade. Unknown counts as unresolved, not as a pass, and a checklist alone cannot establish that a strategy works.
        </p>
        <p className="text-slate-400 leading-relaxed mb-4">
          The sanity check annualises by the square root of periods per year, the standard scaling for i.i.d. returns. The per-period Sharpe is the annual Sharpe divided by the square root of periods per year. With T equal to years times periods per year, g3 equal to skewness and g4 equal to non-excess kurtosis, the adjustment is D equals 1 minus g3 times per-period Sharpe plus ((g4 minus 1) over 4) times per-period Sharpe squared. The standard error is the square root of D over (T minus 1). The 95 percent interval is per-period Sharpe plus or minus 1.96 times the standard error, scaled back to annual.
        </p>
        <p className="text-slate-400 leading-relaxed mb-4">
          The Probabilistic Sharpe Ratio is from Bailey and Lopez de Prado (2012). The Deflated Sharpe Ratio and the expected maximum Sharpe SR0 are from Bailey and Lopez de Prado (2014). SR0 is the expected best Sharpe from N independent trials; if the cross-trial standard deviation of annualised Sharpes is not supplied, the tool uses an estimated variance of 1 over (T minus 1), which is the sampling variance when the true Sharpe is zero under normality, and it says so. The minimum track record length is 1 plus D times (PhiInv(0.95) over per-period Sharpe) squared observations.
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
        <h2 className="text-2xl font-bold text-white mb-6">Related</h2>
        <div className="grid gap-4 sm:grid-cols-2">
          <Link href="/blog/quant-fund-evaluation-guide" className="group rounded-xl border border-[hsl(215,40%,18%)] bg-[hsl(220,55%,9%)] p-5 transition-all hover:border-indigo-500/60 hover:bg-[hsl(220,55%,11%)]">
            <h3 className="text-lg font-semibold text-white group-hover:text-indigo-400 transition-colors">Quant Fund Evaluation Guide</h3>
            <p className="mt-1.5 text-sm text-slate-400">The full due diligence framework this checklist follows.</p>
          </Link>
          <Link href="/tools/risk-adjusted-return" className="group rounded-xl border border-[hsl(215,40%,18%)] bg-[hsl(220,55%,9%)] p-5 transition-all hover:border-indigo-500/60 hover:bg-[hsl(220,55%,11%)]">
            <h3 className="text-lg font-semibold text-white group-hover:text-indigo-400 transition-colors">Risk-Adjusted Return Calculator</h3>
            <p className="mt-1.5 text-sm text-slate-400">Sharpe, Sortino, Calmar, Ulcer Index and the Probabilistic Sharpe Ratio from a return series.</p>
          </Link>
          <Link href="/tools/win-rate-significance" className="group rounded-xl border border-[hsl(215,40%,18%)] bg-[hsl(220,55%,9%)] p-5 transition-all hover:border-indigo-500/60 hover:bg-[hsl(220,55%,11%)]">
            <h3 className="text-lg font-semibold text-white group-hover:text-indigo-400 transition-colors">Win Rate Significance Calculator</h3>
            <p className="mt-1.5 text-sm text-slate-400">Check whether a win rate is signal or noise.</p>
          </Link>
          <Link href="/blog/overfitting-trading-strategies" className="group rounded-xl border border-[hsl(215,40%,18%)] bg-[hsl(220,55%,9%)] p-5 transition-all hover:border-indigo-500/60 hover:bg-[hsl(220,55%,11%)]">
            <h3 className="text-lg font-semibold text-white group-hover:text-indigo-400 transition-colors">Overfitting in Trading Strategies</h3>
            <p className="mt-1.5 text-sm text-slate-400">Why the best backtest is often the most overfit.</p>
          </Link>
          <Link href="/scanner" className="group rounded-xl border border-[hsl(215,40%,18%)] bg-[hsl(220,55%,9%)] p-5 transition-all hover:border-indigo-500/60 hover:bg-[hsl(220,55%,11%)]">
            <h3 className="text-lg font-semibold text-white group-hover:text-indigo-400 transition-colors">Scanner</h3>
            <p className="mt-1.5 text-sm text-slate-400">Browse the QuantEngines tool set.</p>
          </Link>
        </div>
      </section>

      <p className="max-w-3xl mt-14 text-xs text-[hsl(215,20%,45%)] leading-relaxed">
        This tool is educational and does not constitute investment advice. It performs arithmetic on the numbers you enter and on the answers you give. It does not evaluate any specific strategy or fund, does not recommend buying or selling anything, and a strong historical Sharpe ratio is not a guarantee of future performance.
      </p>
    </div>
  );
}
