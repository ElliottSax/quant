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
  // Machine-generated bulk, noindexed 2026-08-19 (site-quality, not per-article)
  // ---------------------------------------------------------------------------
  //
  // Google assesses quality in aggregate. 653 indexable pages of which ~200 are
  // permutation filler drags on the 40-60 genuinely good articles that earn all of
  // this site's traffic. Measured: /scanner converts at 7.1% CTR while the whole blog
  // corpus manages 0.12% across 9,352 impressions.
  //
  //   * 5 LLM PROCESS ARTIFACTS published as posts — delivery summaries and generation
  //     reports, with titles like "Web3/DeFi Articles Generation - Delivery Summary".
  //   * 177 `haiku-*` — an {indicator A} x {indicator B} x {asset class} matrix. All
  //     share ONE meta description that renders on the page ("This article provides
  //     valuable insights and information."), titles are YAML-corrupted and truncated
  //     mid-phrase, one is "Combining MACD and MACD", and the model name is in the
  //     public URL because the route resolves by filename.
  //   * 18 `cerebras-*` — the same matrix under a different prefix.
  //
  // Noindex rather than delete: reversible, and preserves any inbound links. The real
  // repair is to replace them with pages this audience actually searches for.
  // -- 5 process artifacts
  'defi-articles-delivery-summary',
  'defi-articles-index',
  'forex-articles-generation-report',
  'generation-report-20260316',
  'generation-report-final',
  // -- 177 haiku-* permutation matrix
  'haiku-combining-fibonacci-retracement-and-bollinger-bands-for-us-treasuries-full',
  'haiku-combining-fibonacci-retracement-and-money-flow-index-for-commodities-full',
  'haiku-combining-fibonacci-retracement-and-parabolic-sar-for-crypto-markets-full',
  'haiku-combining-fibonacci-retracement-and-parabolic-sar-for-us-treasuries-full-c',
  'haiku-combining-heikin-ashi-and-atr-for-forex-pairs-full-code',
  'haiku-combining-heikin-ashi-and-atr-for-volatility-products-full-code',
  'haiku-combining-heikin-ashi-and-bollinger-bands-for-volatility-products-full-cod',
  'haiku-combining-heikin-ashi-and-chaikin-oscillator-for-options-full-code',
  'haiku-combining-heikin-ashi-and-moving-average-for-forex-pairs-full-code',
  'haiku-combining-heikin-ashi-and-parabolic-sar-for-sp-500-stocks-full-code',
  'haiku-combining-heikin-ashi-and-rsi-for-etfs-full-code',
  'haiku-combining-ichimoku-cloud-and-bollinger-bands-for-emerging-markets-full-cod',
  'haiku-combining-ichimoku-cloud-and-chaikin-oscillator-for-us-treasuries-full-cod',
  'haiku-combining-ichimoku-cloud-and-macd-for-commodities-full-code',
  'haiku-combining-ichimoku-cloud-and-macd-for-futures-full-code',
  'haiku-combining-keltner-channel-and-chaikin-oscillator-for-futures-full-code',
  'haiku-combining-keltner-channel-and-macd-for-commodities-full-code',
  'haiku-combining-keltner-channel-and-macd-for-forex-pairs-full-code',
  'haiku-combining-macd-and-bollinger-bands-for-emerging-markets-full-code',
  'haiku-combining-macd-and-bollinger-bands-for-options-full-code',
  'haiku-combining-macd-and-macd-for-volatility-products-full-code',
  'haiku-combining-macd-and-money-flow-index-for-sp-500-stocks-full-code',
  'haiku-combining-macd-and-parabolic-sar-for-options-full-code',
  'haiku-combining-moving-average-and-chaikin-oscillator-for-crypto-markets-full-co',
  'haiku-combining-moving-average-and-chaikin-oscillator-for-etfs-full-code',
  'haiku-combining-moving-average-and-money-flow-index-for-commodities-full-code',
  'haiku-combining-moving-average-and-money-flow-index-for-small-cap-stocks-full-co',
  'haiku-combining-obv-and-macd-for-options-full-code',
  'haiku-combining-obv-and-macd-for-sp-500-stocks-full-code',
  'haiku-combining-obv-and-money-flow-index-for-etfs-full-code',
  'haiku-combining-obv-and-volume-profile-for-options-full-code',
  'haiku-combining-stochastic-oscillator-and-money-flow-index-for-crypto-markets-fu',
  'haiku-combining-stochastic-oscillator-and-money-flow-index-for-futures-full-code',
  'haiku-combining-williams-r-and-parabolic-sar-for-us-treasuries-full-code',
  'haiku-commodities-regime-detection-for-earnings-momentum-with-bayesian-optimizat',
  'haiku-commodities-regime-detection-for-scalping-with-xgboost',
  'haiku-correlation-management-framework-for-intraday-trend-following-systems',
  'haiku-correlation-management-framework-for-tick-level-momentum-systems',
  'haiku-correlation-management-framework-for-weekly-factor-rotation-systems',
  'haiku-cost-analysis-breakout-transaction-costs-on-small-cap-stocks',
  'haiku-cost-analysis-breakout-transaction-costs-on-us-treasuries',
  'haiku-cost-analysis-calendar-spread-transaction-costs-on-commodities',
  'haiku-cost-analysis-calendar-spread-transaction-costs-on-emerging-markets',
  'haiku-cost-analysis-calendar-spread-transaction-costs-on-futures',
  'haiku-cost-analysis-cross-sectional-momentum-transaction-costs-on-commodities',
  'haiku-cost-analysis-cross-sectional-momentum-transaction-costs-on-emerging-marke',
  'haiku-cost-analysis-earnings-momentum-transaction-costs-on-etfs',
  'haiku-cost-analysis-factor-rotation-transaction-costs-on-emerging-markets',
  'haiku-cost-analysis-gap-trading-transaction-costs-on-commodities',
  'haiku-cost-analysis-gap-trading-transaction-costs-on-us-treasuries',
  'haiku-cost-analysis-market-making-transaction-costs-on-options',
  'haiku-cost-analysis-market-making-transaction-costs-on-small-cap-stocks',
  'haiku-cost-analysis-mean-reversion-transaction-costs-on-small-cap-stocks',
  'haiku-cost-analysis-mean-reversion-transaction-costs-on-volatility-products',
  'haiku-cost-analysis-momentum-transaction-costs-on-crypto-markets',
  'haiku-cost-analysis-momentum-transaction-costs-on-forex-pairs',
  'haiku-cost-analysis-pairs-trading-transaction-costs-on-futures',
  'haiku-cost-analysis-pairs-trading-transaction-costs-on-sp-500-stocks',
  'haiku-cost-analysis-pairs-trading-transaction-costs-on-volatility-products',
  'haiku-cost-analysis-scalping-transaction-costs-on-crypto-markets',
  'haiku-cost-analysis-scalping-transaction-costs-on-sp-500-stocks',
  'haiku-cost-analysis-sector-rotation-transaction-costs-on-small-cap-stocks',
  'haiku-cost-analysis-statistical-arbitrage-transaction-costs-on-commodities',
  'haiku-cost-analysis-swing-trading-transaction-costs-on-forex-pairs',
  'haiku-cost-analysis-swing-trading-transaction-costs-on-options',
  'haiku-cost-analysis-trend-following-transaction-costs-on-forex-pairs',
  'haiku-cost-analysis-trend-following-transaction-costs-on-sp-500-stocks',
  'haiku-cost-analysis-volatility-trading-transaction-costs-on-crypto-markets',
  'haiku-cost-analysis-volatility-trading-transaction-costs-on-options',
  'haiku-cost-analysis-volatility-trading-transaction-costs-on-sp-500-stocks',
  'haiku-crypto-markets-regime-detection-for-earnings-momentum-with-reinforcement-l',
  'haiku-crypto-markets-regime-detection-for-pairs-trading-with-genetic-algorithms',
  'haiku-crypto-markets-regime-detection-for-pairs-trading-with-gradient-boosting',
  'haiku-daily-earnings-momentum-with-correlation-management-risk-adjusted-returns',
  'haiku-daily-mean-reversion-with-cvar-optimization-risk-adjusted-returns',
  'haiku-daily-momentum-with-position-sizing-risk-adjusted-returns',
  'haiku-daily-momentum-with-volatility-targeting-risk-adjusted-returns',
  'haiku-daily-pairs-trading-with-cvar-optimization-risk-adjusted-returns',
  'haiku-daily-pairs-trading-with-value-at-risk-risk-adjusted-returns',
  'haiku-daily-scalping-with-value-at-risk-risk-adjusted-returns',
  'haiku-daily-sector-rotation-with-risk-parity-risk-adjusted-returns',
  'haiku-daily-statistical-arbitrage-with-max-diversification-risk-adjusted-returns',
  'haiku-daily-swing-trading-with-correlation-management-risk-adjusted-returns',
  'haiku-daily-swing-trading-with-kelly-criterion-risk-adjusted-returns',
  'haiku-daily-swing-trading-with-position-sizing-risk-adjusted-returns',
  'haiku-donchian-channel-divergence-strategy-for-small-cap-stocks-4-hour-backtest',
  'haiku-donchian-channel-divergence-strategy-for-small-cap-stocks-monthly-backtest',
  'haiku-donchian-channel-divergence-strategy-for-sp-500-stocks-tick-level-backtest',
  'haiku-donchian-channel-signal-quality-on-commodities-statistical-analysis',
  'haiku-donchian-channel-signal-quality-on-crypto-markets-statistical-analysis',
  'haiku-drawdown-control-framework-for-tick-level-calendar-spread-systems',
  'haiku-drawdown-control-framework-for-tick-level-earnings-momentum-systems',
  'haiku-drawdown-control-framework-for-weekly-momentum-systems',
  'haiku-earnings-momentum-backtest-forex-pairs-tick-level-results-2026',
  'haiku-earnings-momentum-backtest-sp-500-stocks-monthly-results-2026',
  'haiku-emerging-markets-regime-detection-for-mean-reversion-with-bayesian-optimiz',
  'haiku-emerging-markets-regime-detection-for-swing-trading-with-reinforcement-lea',
  'haiku-etfs-regime-detection-for-market-making-with-gradient-boosting',
  'haiku-etfs-regime-detection-for-statistical-arbitrage-with-bayesian-optimization',
  'haiku-etfs-regime-detection-for-statistical-arbitrage-with-genetic-algorithms',
  'haiku-feature-engineering-for-gradient-boosting-in-scalping-on-crypto-markets',
  'haiku-from-theory-to-production-scalping-on-crypto-markets',
  'haiku-optimizing-pairs-trading-parameters-with-gradient-boosting',
  'haiku-optimizing-pairs-trading-parameters-with-lstm-neural-networks',
  'haiku-optimizing-pairs-trading-parameters-with-support-vector-machines',
  'haiku-optimizing-pairs-trading-parameters-with-xgboost',
  'haiku-optimizing-scalping-parameters-with-gradient-boosting',
  'haiku-optimizing-scalping-parameters-with-random-forest',
  'haiku-optimizing-scalping-parameters-with-support-vector-machines',
  'haiku-optimizing-scalping-parameters-with-xgboost',
  'haiku-optimizing-sector-rotation-parameters-with-xgboost',
  'haiku-optimizing-statistical-arbitrage-parameters-with-ensemble-methods',
  'haiku-optimizing-statistical-arbitrage-parameters-with-gradient-boosting',
  'haiku-optimizing-statistical-arbitrage-parameters-with-support-vector-machines',
  'haiku-optimizing-statistical-arbitrage-parameters-with-xgboost',
  'haiku-optimizing-swing-trading-parameters-with-gradient-boosting',
  'haiku-optimizing-swing-trading-parameters-with-random-forest',
  'haiku-optimizing-swing-trading-parameters-with-reinforcement-learning',
  'haiku-optimizing-swing-trading-parameters-with-support-vector-machines',
  'haiku-optimizing-swing-trading-parameters-with-xgboost',
  'haiku-optimizing-trend-following-parameters-with-ensemble-methods',
  'haiku-optimizing-trend-following-parameters-with-lstm-neural-networks',
  'haiku-optimizing-trend-following-parameters-with-reinforcement-learning',
  'haiku-optimizing-volatility-trading-parameters-with-ensemble-methods',
  'haiku-optimizing-volatility-trading-parameters-with-reinforcement-learning',
  'haiku-optimizing-volatility-trading-parameters-with-support-vector-machines',
  'haiku-order-flow-analysis-enhancing-high-frequency-market-making-with-aroon-indi',
  'haiku-order-flow-analysis-enhancing-intraday-reversal-with-point-and-figure-on-v',
  'haiku-order-flow-analysis-enhancing-intraday-reversal-with-tick-volume-on-nikkei',
  'haiku-order-flow-analysis-enhancing-microstructure-alpha-with-anchored-vwap-on-c',
  'haiku-order-flow-analysis-enhancing-microstructure-alpha-with-supertrend-on-crud',
  'haiku-order-flow-analysis-enhancing-order-flow-imbalance-with-order-book-depth-o',
  'haiku-order-flow-analysis-enhancing-overnight-returns-with-commodity-channel-ind',
  'haiku-order-flow-analysis-enhancing-overnight-returns-with-ease-of-movement-on-g',
  'haiku-order-flow-analysis-enhancing-overnight-returns-with-market-profile-on-fts',
  'haiku-order-flow-analysis-enhancing-overnight-returns-with-supertrend-on-eurusd',
  'haiku-order-flow-analysis-enhancing-relative-value-with-aroon-indicator-on-vix-d',
  'haiku-order-flow-analysis-enhancing-relative-value-with-point-and-figure-on-russ',
  'haiku-order-flow-analysis-enhancing-relative-value-with-supertrend-on-russell-20',
  'haiku-order-flow-analysis-enhancing-sentiment-based-with-ease-of-movement-on-fts',
  'haiku-order-flow-analysis-enhancing-smart-beta-with-elder-ray-on-russell-2000',
  'haiku-order-flow-analysis-enhancing-statistical-momentum-with-point-and-figure-o',
  'haiku-order-flow-analysis-enhancing-volatility-surface-arbitrage-with-cumulative',
  'haiku-order-flow-analysis-enhancing-volatility-surface-arbitrage-with-ease-of-mo',
  'haiku-order-flow-analysis-enhancing-volatility-surface-arbitrage-with-force-inde',
  'haiku-pairs-trading-on-emerging-markets-weekly-performance-analysis',
  'haiku-paper-trading-framework-carry-trade-with-dynamic-hedging-on-russell-2000',
  'haiku-paper-trading-framework-carry-trade-with-dynamic-hedging-on-treasury-yield',
  'haiku-paper-trading-framework-contrarian-with-dynamic-hedging-on-bitcoinethereum',
  'haiku-paper-trading-framework-contrarian-with-risk-budgeting-on-gold-futures',
  'haiku-paper-trading-framework-dispersion-trading-with-black-litterman-on-treasur',
  'haiku-paper-trading-framework-dispersion-trading-with-expected-shortfall-on-gold',
  'haiku-paper-trading-framework-dispersion-trading-with-tail-risk-hedging-on-eurus',
  'haiku-paper-trading-framework-event-driven-with-dynamic-hedging-on-nasdaq-100',
  'haiku-paper-trading-framework-high-frequency-market-making-with-hierarchical-ris',
  'haiku-paper-trading-framework-intraday-reversal-with-risk-budgeting-on-crude-oil',
  'haiku-paper-trading-framework-microstructure-alpha-with-tail-risk-hedging-on-fts',
  'haiku-paper-trading-framework-order-flow-imbalance-with-black-litterman-on-eurus',
  'haiku-paper-trading-framework-order-flow-imbalance-with-maximum-sharpe-on-eurusd',
  'haiku-paper-trading-framework-overnight-returns-with-dynamic-hedging-on-bitcoine',
  'haiku-paper-trading-framework-seasonal-pattern-with-black-litterman-on-nikkei-22',
  'haiku-paper-trading-framework-seasonal-pattern-with-hierarchical-risk-parity-on',
  'haiku-paper-trading-framework-sentiment-based-with-maximum-sharpe-on-gold-future',
  'haiku-paper-trading-framework-sentiment-based-with-regime-conditional-sizing-on',
  'haiku-paper-trading-framework-sentiment-based-with-risk-budgeting-on-treasury-yi',
  'haiku-paper-trading-framework-smart-beta-with-black-litterman-on-gold-futures',
  'haiku-paper-trading-framework-smart-beta-with-dynamic-hedging-on-bitcoinethereum',
  'haiku-paper-trading-framework-smart-beta-with-risk-budgeting-on-ftse-100',
  'haiku-paper-trading-framework-statistical-momentum-with-expected-shortfall-on-go',
  'haiku-paper-trading-framework-volatility-surface-arbitrage-with-maximum-sharpe-o',
  'haiku-paper-trading-framework-volatility-surface-arbitrage-with-regime-condition',
  'haiku-production-grade-contrarian-system-agricultural-commodities-with-ease-of-m',
  'haiku-production-grade-contrarian-system-eurusd-with-supertrend-2026',
  'haiku-production-grade-contrarian-system-treasury-yield-curve-with-delta-diverge',
  'haiku-production-grade-contrarian-system-treasury-yield-curve-with-market-profil',
  'haiku-production-grade-cross-asset-momentum-system-dax-40-with-footprint-charts',
  'haiku-production-grade-cross-asset-momentum-system-dax-40-with-point-and-figure',
  // -- 12 cerebras-* permutation matrix
  'cerebras-automating-bollinger-bands-for-beginners',
  'cerebras-automating-mean-reversion-on-forex',
  'cerebras-automating-momentum-trading-for-beginners',
  'cerebras-backtesting-bollinger-bands-safely',
  'cerebras-backtesting-macd-crossovers-for-beginners',
  'cerebras-backtesting-rsi-strategies-using-machine-learning',
  'cerebras-guide-to-macd-crossovers-using-machine-learning',
  'cerebras-guide-to-mean-reversion-safely',
  'cerebras-guide-to-position-sizing-safely',
  'cerebras-guide-to-risk-management-on-crypto',
  'cerebras-improving-bollinger-bands-with-high-success-rate',
  'cerebras-improving-statistical-arbitrage-safely',

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

  // -- 43 near-duplicate articles (measured 2026-08-20). Nine clusters whose members
  // are 0.98-0.995 identical line-for-line -- the same body with the H1 and opening
  // sentence swapped. 'Average True Range for Dynamic Position Sizing' and
  // 'Automating RSI Strategies Safely' are 382 lines each and differ on two of them,
  // and neither body discusses its own subject. The LONGEST member of each cluster is
  // deliberately left indexed so the topic still has a page and inbound links survive;
  // only the copies are listed here.
  //
  // Clusters at 0.949 (the options-strategy family) are NOT listed: they share a
  // template but each covers a genuinely different strategy and answers a different
  // query, mentioning its own subject 20-33 times against 5-6 for the group below.
  '09-crypto-futures-trading-strategies-advanced',
  '10-crypto-scalping-strategies-quick-profits',
  '11-crypto-options-trading-hedging',
  '13-crypto-portfolio-diversification',
  '14-crypto-technical-analysis-strategies',
  '15-crypto-market-making-strategies',
  '16-dollar-cost-averaging-crypto-strategy',
  '19-crypto-tax-optimization-strategies',
  '20-risk-management-crypto-trading',
  'automating-risk-management-using-machine-learning',
  'automating-risk-management-with-high-success-rate',
  'automating-rsi-strategies-for-beginners',
  'automating-rsi-strategies-in-python',
  'automating-rsi-strategies-safely',
  'automating-statistical-arbitrage-in-python',
  'automating-statistical-arbitrage-on-crypto',
  'automating-statistical-arbitrage-on-forex',
  'automating-statistical-arbitrage-safely',
  'average-directional-index',
  'average-true-range',
  'backtesting-algorithmic-trading-on-crypto',
  'backtesting-algorithmic-trading-safely',
  'backtesting-algorithmic-trading-using-machine-learning',
  'backtesting-bollinger-bands-efficiently',
  'backtesting-bollinger-bands-for-beginners',
  'backtesting-bollinger-bands-in-python',
  'defi-article-02-how-to-stake-ethereum-for-passive-income',
  'defi-article-03-best-decentralized-exchanges-dex-guide-2026',
  'defi-article-05-best-defi-lending-protocols-comparison-2026',
  'defi-article-06-how-to-earn-yield-on-stablecoins-safely',
  'defi-article-07-best-liquid-staking-tokens-2026-guide',
  'defi-article-09-how-to-use-uniswap-for-liquidity-provision',
  'defi-article-10-best-yield-aggregators-defi-2026',
  'defi-article-11-how-to-bridge-crypto-between-chains-safely',
  'defi-article-12-best-crypto-wallets-for-defi-2026-guide',
  'defi-article-13-impermanent-loss-calculator-and-strategies',
  'defi-article-14-best-layer-2-defi-protocols-2026',
  'defi-article-15-how-to-minimize-gas-fees-defi-transactions',
  'defi-article-16-best-defi-governance-tokens-to-stake',
  'defi-article-17-flash-loan-arbitrage-strategies-defi-2026',
  'defi-article-18-how-to-use-aave-lending-borrowing-protocol',
  'defi-article-19-best-defi-portfolio-tracking-tools-2026',
  'defi-article-20-defi-taxes-guide-complete-strategy-2026',
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
