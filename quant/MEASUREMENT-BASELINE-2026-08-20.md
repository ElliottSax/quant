# Measurement baseline — 2026-08-20

A dated record of what was true before this session's changes, so their effect can be
measured rather than assumed. Re-pull Search Console after ~14 and ~28 days and compare
against the numbers below.

The point of writing this down is that "traffic went up" is not evidence a change worked.
Several things shipped at once here, and one of them (the sitemap) plausibly dominates
everything else. Without a baseline and a per-change prediction, any later improvement
gets attributed to whichever change is most memorable.

## Baseline (Search Console, 90 days to 2026-08-18)

| Measure | Value |
|---|---|
| `/scanner` — the one real tool | 13 clicks / 184 impressions = **7.1% CTR** |
| Blog corpus (700 posts) | 11 clicks / 9,352 impressions = **0.12% CTR** |
| Ratio | the tool converted ~**60×** better than the articles |
| Links from blog posts to any tool | **0** (1 to `/backtesting`) |
| Page-1 queries (pos ≤ 10.5) with zero clicks | 23 queries, 173 impressions |
| Largest single impression pool | `/blog/quant-fund-evaluation-guide` — 2,637 impressions, 1 click, position 33 |

Top zero-click queries, all developer-intent rather than trader-intent:
`from statsmodels.tsa.api import arima` (132 impressions, position 8–10), pandas_ta column
names, `coint_johansen`, `maximize (w^t mu)/sqrt(w^t sigma w)` (positions 5.0 and 7.7),
`backtrader vs vectorbt`.

**Google Analytics was not readable** at baseline: the Admin API was not enabled and the
service account was never granted on the properties. The APIs are now enabled; the grant
remains outstanding, so there is still no engagement baseline. Any GA4 comparison starts
from the date of the grant, not from here.

## What changed, and what each change predicts

Ordered by expected effect. The first is the one to attribute cautiously, because it is
large, site-wide, and lands at the same time as everything else.

### 1. The sitemap was never being served (highest expected effect)

`public/sitemap.xml`, last written 2026-07-18, was shadowing `src/app/sitemap.ts` — Next.js
serves `public/` at the same path and the static file wins. Google was receiving **148
URLs** against the **493** the route generates, so roughly 345 indexable articles were
never advertised, and the file listed `/signals`, which carries `robots:noindex`.

*Predicts:* a rise in **indexed pages** and **total impressions** as previously
unadvertised articles enter the index, over weeks rather than days. It predicts little
about CTR. If impressions rise and clicks do not, that is this change working and the
content still not converting — not a failure of the content work below.

### 2. Six new tools targeting measured queries

`/tools/max-sharpe`, `/fundamentals`, `/yield-curve`, `/cot-report`,
`/statsmodels-imports`, `/indicator-formulas`.

*Predicts:* impressions on the specific baseline queries above. The cleanest test is
`/statsmodels-imports` against `from statsmodels.tsa.api import arima` — 132 impressions
at position 8–10 with **zero** clicks. A page built to answer that exact traceback should
move both position and CTR. If it does not, the hypothesis that this audience is
developers wanting a one-line answer is wrong, and the remaining tool work should stop.

### 3. Blog metadata repaired

Descriptions: 252 usable of 458 → **453 of 458**. Titles over the rendered limit: 130 → 0.

*Predicts:* **CTR** improvement on already-ranking pages, with impressions roughly flat.
This is the only change that isolates cleanly, because it alters what a searcher sees in
the result without altering the page's relevance. Compare CTR on the six Phase 1 pages
listed in the plan against their baseline.

### 4. Fabricated content removed

266 fabricated return claims across 109 articles; investment advice and insider-trading
assertions removed from 4; 20 fabricated author bios deleted.

*Predicts:* nothing measurable in the short term, and possibly a small **loss** of traffic
where a promissory headline was doing the converting. It was done because the claims were
false and sat next to broker links, not to raise traffic. Do not judge it on traffic.

### 5. 43 near-duplicate articles noindexed

Indexable posts 458 → 415; sitemap 493 → 450.

*Predicts:* a **fall** in indexed page count, which is the intended outcome and must not
be read as a regression. It predicts flat-to-slightly-positive clicks: the removed pages
were 0.98–0.995 identical to a page that remains.

## How to re-measure

```
GCP_SERVICE_ACCOUNT='<json>' python calc/scripts/gsc_pull_performance.py
GCP_SERVICE_ACCOUNT='<json>' python calc/scripts/ga4_pull_performance.py   # after the grant
```

Then compare, in this order:

1. **Indexed page count** (Search Console → Pages). Expect up from the sitemap fix, offset
   by −43 from the noindex pass.
2. **Impressions**, total and on the named queries above.
3. **CTR on the six Phase 1 pages**, which is the isolated test of the metadata work.
4. **Clicks**, last — it is the noisiest number at this traffic level, and at 24 clicks per
   90 days across the whole site, a change of a few clicks is not a signal.

## Caveats on any conclusion drawn

- Baseline click volume is **24 clicks per 90 days** site-wide. Almost no change will be
  statistically distinguishable from noise in clicks alone. Impressions and position are
  the usable signals at this scale.
- Several changes shipped the same day, so per-change attribution is weak by construction.
  The per-change predictions above exist to make attribution *possible*, not certain: if
  impressions rise but the named queries do not move, that points at the sitemap rather
  than the tools.
- Indexing changes from a sitemap fix take weeks. A 14-day read is early; 28 days is the
  first fair one.
