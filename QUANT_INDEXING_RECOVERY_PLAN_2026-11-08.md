# quantengines.com indexing recovery plan (draft, 2026-11-08)

Status: DRAFT for Elliott's approval. No site changes made.

## Evidence
- Weekly GSC impressions: 2,550 (wk Aug 10) -> 8 (wk Nov 2). Slow decay, no technical fault.
- Sitemap: 539 URLs = 381 /blog, 121 /congress-stock-trades, 8 /tools, ~29 other.
- URL Inspection sample (6): homepage indexed; blog = "Crawled - currently not indexed" (last crawl Aug); congress pages = "Discovered - currently not indexed".
- Earlier GSC finding: only unique tools (e.g. /scanner) convert; saturated blog topics don't.

## Already done in earlier sessions (per quant/CLAUDE.md, 2026-09-05/06)
- Deleted ~800 files of generated/orphan content (generated-articles, posts, marketing, dormant clusters).
- noindexed 6 congress-* posts with fabricated named-legislator figures, plus mean-reversion-trading-strategy.md (via src/lib/noindex-drafts.ts, which already excludes pages from index/sitemap/RSS).
- Added 199 contextual tool links to blog posts; built /congress-stock-trades/late-filers (real FMP data).
- The Sept note said quant was the best-performing site (59% engagement organic). GSC now shows impressions collapsing since Aug, so that status is stale. Reconcile against GA4 (property 526411775) before acting.
- So step 2 below should reuse noindex-drafts.ts, not a new mechanism. The sitemap still lists 381 /blog + 121 congress URLs, so the pruning has not reached the sitemap for the bulk of them.

## Diagnosis
Google sees 500+ near-templated pages on a young domain and declines to index them. More pages make this worse (crawl budget and a low site-wide quality signal).

## Plan
1. **Shrink the sitemap to the pages worth indexing.** Keep: home, /scanner, /tools/*, /backtesting, /strategies, /yield-curve, /politicians, /pandas-ta-columns, /statsmodels-imports, pricing, and the ~20 best blog posts (pick by GSC impressions + uniqueness). Remove the rest from sitemap.xml.
2. **noindex the thin blog posts** (~360) and the per-ticker /congress-stock-trades/[ticker] pages except the top ~15 tickers by search interest. Do not delete: keeps internal links working and lets us re-promote later.
3. **Make /congress-stock-trades a real tool, not 121 stubs**: one hub page with filter/search by member and ticker, updated data, a "last trade filed" freshness line, and unique commentary. Only index member/ticker pages that have 5+ trades.
4. **Internal linking**: home and /tools link to the kept pages; every kept blog post links to a relevant tool.
5. **Re-submit** the trimmed sitemap; use URL Inspection "request indexing" on the 10-20 best pages (manual, rate-limited).
6. **Measure** weekly via the GSC query used on 2026-11-08; success = indexed share of kept pages > 80% and impressions trending up within 6-8 weeks.

## Risks / notes
- Reversible: noindex + sitemap trim are config changes, no content deleted.
- Do not run `git add -A` in this repo (concurrent agents; see memory).
- Needs Elliott's go-ahead before any deploy; deploys read local disk for some sibling sites, verify quant's deploy path first.

## Open decisions for Elliott
- OK to noindex ~360 blog posts and ~100 ticker pages?
- Which tool should be the flagship (congress trades tracker vs /scanner)?
