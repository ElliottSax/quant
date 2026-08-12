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
