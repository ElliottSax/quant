import Link from 'next/link'

/**
 * Routes a blog reader to the tool that matches what they were reading about.
 *
 * Why this exists: an audit of all 702 articles found ZERO links to /scanner, /charts,
 * /options, /tools/* or /data-vendors, and exactly one to /backtesting. The article
 * template offered only category chips, tags, related *blog* posts and "Browse All
 * Articles" — so the blog was a closed loop and every hard-won click dead-ended in more
 * blog. Improving click-through without this converts impressions into pageviews and
 * nothing else.
 *
 * Only tools that genuinely work are listed. Nothing here points at an in-development
 * page, because sending a reader from an article to a placeholder is worse than not
 * linking at all.
 */

interface Tool {
  href: string
  title: string
  blurb: string
}

const TOOLS: Record<string, Tool> = {
  scanner: {
    href: '/scanner',
    title: 'Seasonality Screener',
    blurb: 'Monthly patterns across a fixed universe, with sample sizes and multiple-testing-corrected verdicts — including the ones that fail.',
  },
  charts: {
    href: '/charts',
    title: 'Charts',
    blurb: 'Adjusted end-of-day candles with SMA, EMA and Bollinger bands computed from the real series.',
  },
  options: {
    href: '/options',
    title: 'Options Calculator',
    blurb: 'Black–Scholes pricing and Greeks, verified against textbook values.',
  },
  backtesting: {
    href: '/backtesting/builder',
    title: 'Strategy Builder',
    blurb: 'Configure a strategy and backtest it. No signup.',
  },
  congress: {
    href: '/congress-stock-trades',
    title: 'Congressional Trade Filings',
    blurb: 'Live filings, straight from the disclosure data.',
  },
  vendors: {
    href: '/data-vendors',
    title: 'Market Data API Benchmark',
    blurb: 'We requested the same data from each provider and recorded what came back. Measured, not quoted.',
  },
  risk: {
    href: '/tools/position-size',
    title: 'Position Size Calculator',
    blurb: 'Risk-based sizing from account, risk percentage, entry and stop.',
  },
  indicators: {
    href: '/indicator-formulas',
    title: 'Indicator Formulas, Cross-Checked',
    blurb: 'RSI, ADX, ATR, MACD and Bollinger implemented independently and verified against pandas_ta on real bars — including where they disagree.',
  },
  imports: {
    href: '/statsmodels-imports',
    title: 'statsmodels Import Reference',
    blurb: 'Which import paths work, measured by executing every statement — including the three that import fine and fail later.',
  },
  fundamentals: {
    href: '/fundamentals',
    title: 'Fundamental Screener',
    blurb: 'Accruals, asset growth and net issuance for 3,000+ US filers, computed straight from SEC XBRL filings.',
  },
  rates: {
    href: '/yield-curve',
    title: 'Treasury Yield Curve',
    blurb: "Today's curve plus every sustained inversion since 1990, computed from Treasury's daily series.",
  },
  portfolio: {
    href: '/tools/max-sharpe',
    title: 'Max Sharpe Portfolio',
    blurb: 'Closed-form tangency weights from expected returns, volatilities and correlations.',
  },
}

/** First match wins, so the most specific rules must come first: an article about the
 *  RSI formula should reach the indicator reference, not the generic "python" rule. */
const RULES: Array<[RegExp, string[]]> = [
  [/congress|politician|insider/i, ['congress', 'scanner']],
  [/\b(rsi|adx|atr|macd|bollinger|stochastic|indicator|oscillator|moving average)\b/i,
    ['indicators', 'charts']],
  [/statsmodels|arima|cointegrat|johansen|adfuller|import error/i, ['imports', 'indicators']],
  [/fundamental|accrual|earnings|balance sheet|valuation|screener|xbrl|edgar|10-?k/i,
    ['fundamentals', 'scanner']],
  [/yield curve|treasury|interest rate|inversion|bond|fixed income|fed\b/i, ['rates', 'fundamentals']],
  [/portfolio|allocation|sharpe|diversif|efficient frontier|markowitz|correlation/i,
    ['portfolio', 'risk']],
  [/option|greek|volatility|black.?scholes/i, ['options', 'charts']],
  // Fund/manager due diligence is about judging performance claims, so it belongs with
  // the screener that publishes its failures and multiple-testing corrections, not with
  // the strategy builder. Matched before the backtest rule, which otherwise catches
  // these on the bare word "framework".
  [/fund (analysis|evaluation|selection)|due diligence|manager|track record|performance attribution/i,
    ['scanner', 'vendors']],
  [/backtest|vectorbt|backtrader|zipline|python|library|pandas/i, ['backtesting', 'vendors']],
  [/data|api|vendor|feed/i, ['vendors', 'charts']],
  [/risk|position siz|kelly|drawdown|money manage/i, ['risk', 'portfolio']],
  [/seasonal|mean reversion|momentum|factor|strategy|signal/i, ['scanner', 'backtesting']],
]

export function ToolCTA({ category, title }: { category?: string; title?: string }) {
  const haystack = `${category ?? ''} ${title ?? ''}`
  const picked = RULES.find(([re]) => re.test(haystack))?.[1] ?? ['scanner', 'backtesting']
  const tools = picked.map(k => TOOLS[k]).filter(Boolean).slice(0, 2)
  if (tools.length === 0) return null

  return (
    <div className="my-10 border-t border-[hsl(215,40%,16%)] pt-8">
      <h2 className="text-sm font-semibold uppercase tracking-wider text-[hsl(45,96%,58%)] mb-4">
        Try it on real data
      </h2>
      <div className="grid gap-3 sm:grid-cols-2">
        {tools.map(t => (
          <Link
            key={t.href}
            href={t.href}
            className="block rounded-lg border border-[hsl(215,40%,16%)] bg-[hsl(220,60%,5%)] p-4 hover:border-[hsl(45,96%,58%)]/40 transition-colors"
          >
            <div className="font-semibold text-white mb-1">{t.title}</div>
            <div className="text-sm text-[hsl(210,20%,65%)]">{t.blurb}</div>
          </Link>
        ))}
      </div>
      <p className="text-xs text-[hsl(215,20%,50%)] mt-3">
        Free, no signup. We compute and display; we never recommend.
      </p>
    </div>
  )
}
