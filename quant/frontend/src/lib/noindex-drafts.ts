// ---------------------------------------------------------------------------
// Unfinished drafts: excluded from the blog index, the sitemap and the RSS feed,
// and served with `robots: noindex, follow`.
// ---------------------------------------------------------------------------
//
// HOW THIS SET WAS MEASURED (2026-08, against 615 files in content/blog/)
//
// Every article body was stripped of fenced code blocks (```...```), indented
// code blocks, inline code (`...`) and markdown link/image targets — this step
// is essential, because the overwhelming majority of raw `[...]` matches in
// these articles are legitimate pandas/numpy code (`df['Close']`) or maths
// notation (`E[(R - mu)^2]`, LaTeX `\left[...\right]`), not placeholders.
//
// What remained was prose-level template placeholders that render verbatim on
// the live page. 36 articles carry them, in two disjoint groups:
//
//   * 11 articles (the `status: template` group below) containing the
//     market-analysis skeleton: `[specific conditions]`, `[list specific
//     catalysts]`, `[Specific allocation recommendations]`,
//     `[Bloomberg/Reuters/Fred/etc.]`, `[Date]`, `[Company 1]`, `[source]`,
//     `[High/Medium/Low]` and ~40 more — 3 occurrences of each per file.
//     These 11 also declare `status: template` in frontmatter; nothing in the
//     codebase read that field before this change, so they were listed and
//     indexed like finished posts.
//
//   * 25 forex articles containing `[specific market mechanics based on
//     timeframe]` in the opening section. These do NOT declare
//     `status: template`, so the frontmatter check alone would not catch them.
//
// The two groups do not overlap (11 + 25 = 36).
//
// `status: template` is honoured independently in the content parsers, so any
// article that gains that field later is excluded automatically without needing
// an entry here.
//
// REVERTING: this file is purely additive. Deleting it (and the
// `isNoindexDraft` call sites) restores the previous behaviour of publishing
// every .md file. Removing a single slug from the set re-publishes just that
// article — do that once its placeholders are filled in.
// ---------------------------------------------------------------------------

export const NOINDEX_DRAFT_SLUGS: ReadonlySet<string> = new Set([
  // ---------------------------------------------------------------------------
  // 13 articles asserting FIRST-PERSON RESEARCH THAT WAS NEVER RUN (measured 2026-08-19)
  // ---------------------------------------------------------------------------
  //
  // These do not contain placeholders; they read as finished, confident writing.
  // The problem is that they claim original empirical work in the site's own voice
  // and report specific results from it: "we tested 1,247 variations of moving
  // average crossover strategies" on S&P 500 futures, "We backtested a stat arb
  // strategy on 10 crypto pairs", "Our analysis reveals ... the accuracy of the
  // signal increases to 81.2%". No such backtests exist anywhere in this repo, and
  // until 2026-08-18 the platform had no persisted market data at all to run them on.
  //
  // This is the same defect class as the fabricated tool pages, in prose: a number
  // presented as measured when nothing measured it. It is arguably worse here,
  // because a reader has no way to tell a written claim from a computed one.
  //
  // HOW THE SET WAS MEASURED, and why it is 13 and not 88:
  //   * fenced/indented/inline code was stripped first — the same discipline the
  //     placeholder pass used — because "we tested" inside a docstring or a quoted
  //     example is not a claim the site is making.
  //   * the pattern matched only FIRST-PERSON assertions of having done the work
  //     ("we tested/backtested/analysed", "our backtest/analysis shows"). A crude
  //     grep returns 88 files, but most are instructional prose addressed to the
  //     reader ("if your backtest shows a Sharpe above 2.0..."), which is fine.
  //   * every one of the 18 surviving matches was then read in context.
  //
  // DELIBERATELY EXCLUDED, after reading it: `overfitting-trading-strategies` uses
  // "given that we tested N variations, what is the probability that the best Sharpe
  // exceeds a threshold by chance" — a hypothetical inside an explanation of the
  // deflated Sharpe ratio, not a claim about work we did. It stays indexed.
  //
  // Noindex is a stop-gap, not a fix. These articles remain readable and still
  // contain the invented figures; the real repair is to rewrite the claims or run
  // the backtests. Removing a slug re-publishes that article.
  'breakout-trading-strategy',
  'cerebras-backtesting-bollinger-bands-efficiently',
  'cerebras-backtesting-macd-crossovers-using-machine-learning',
  'cerebras-guide-to-statistical-arbitrage-on-crypto',
  'cerebras-improving-algorithmic-trading-efficiently',
  'cerebras-improving-bollinger-bands-on-forex',
  'cerebras-improving-rsi-strategies-on-forex',
  'congress-insider-selling-signals',
  'macd-trading-strategy',
  'mean-reversion-trading-strategy',
  'momentum-trading-strategy-guide',
  'pairs-trading-strategy-guide',
  'rsi-trading-strategy-guide',

  // -- 25 forex articles: unresolved `[specific market mechanics based on timeframe]`
  '01-forex-scalping-strategy-5',
  '02-best-forex-day-trading',
  '03-forex-swing-trading-strategies',
  '04-price-action-forex-trading',
  '05-forex-trend-following-strategy',
  '06-forex-range-trading-strategy',
  '07-forex-breakout-trading-strategy',
  '08-best-forex-news-trading',
  '09-forex-carry-trade-strategy',
  '10-forex-grid-trading-strategy',
  '11-forex-hedging-strategies-risk',
  '12-best-forex-pair-correlation',
  '13-forex-fibonacci-trading-strategy',
  '14-forex-candlestick-patterns-strategy',
  '15-best-forex-moving-average',
  '16-forex-macd-trading-strategy',
  '17-forex-rsi-trading-strategy',
  '18-best-forex-bollinger-bands',
  '19-forex-stochastic-oscillator-strategy',
  '20-forex-ichimoku-cloud-trading',
  '21-best-forex-elliott-wave',
  '22-forex-harmonic-patterns-trading',
  '23-forex-supply-and-demand',
  '24-best-forex-position-trading',
  '25-forex-automated-trading-strategy',

  // -- 11 market-analysis articles: full template skeleton + `status: template`
  'bond-market-analysis-2026-yield-curves-credit-spreads-and-fixed-income-strategy',
  'commodity-market-analysis-2026-gold-oil-and-agricultural-trends',
  'consumer-discretionary-market-trends-2026-spending-patterns-and-retail-evolution',
  'correlation-trading-strategies-exploiting-market-relationships-for-profit',
  'cryptocurrency-market-trends-bitcoin-ethereum-and-digital-asset-adoption',
  'dividend-investing-market-analysis-high-yield-opportunities-in-2026',
  'economic-indicators-explained-a-traders-guide-to-data-driven-decisions',
  'emerging-markets-analysis-2026-growth-opportunities-and-geopolitical-risks',
  'energy-sector-market-analysis-2026-transition-to-renewables-and-oil-market-dynam',
  'esg-investing-market-trends-sustainable-finance-and-impact-investing-growth',
  'financial-sector-market-analysis-2026-banking-trends-and-fintech-disruption',
])

/**
 * True when an article must be kept out of the index, the sitemap and the feed.
 *
 * `status` is the article's frontmatter `status` field (pass '' when unknown);
 * any article marked `template` is excluded regardless of the slug list.
 */
export function isNoindexDraft(slug: string, status?: string): boolean {
  if (NOINDEX_DRAFT_SLUGS.has(slug)) return true
  return (status ?? '').trim().toLowerCase() === 'template'
}
