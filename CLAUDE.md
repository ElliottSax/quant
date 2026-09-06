# ⚠️ FOLLOW-UP — 2026-09-06 — 4 congress-* posts noindexed for fabricated
# named-legislator dollar figures — HUMAN ACTION NEEDED ⚠️
# ============================================================
# The 2026-09-05/06 congress-* prune (see follow-up below) only checked for
# template duplication, not factual accuracy. A dedicated pass re-read the
# bank-crisis, healthcare/FDA, and AI-investment posts that survived that
# prune and found hyper-precise dollar figures / realized-gain figures
# attributed to real, named sitting members of Congress, with no supporting
# record. Checked against this site's own real STOCK Act data source
# (src/lib/congress-trades.ts, FMP API parsing efdsearch.senate.gov +
# disclosures-clerk.house.gov, the feed behind /congress-stock-trades/
# late-filers): actual Periodic Transaction Reports disclose amounts only as
# broad ranges (e.g. "$1,001 - $15,000") and never report realized gains,
# win rates, or briefing dates. None of these specific figures are
# supported by that data or any other checkable public record.
#
# Followed the site's own precedent (mean-reversion-trading-strategy.md,
# noindexed 2026-08-19 for invented backtest numbers) rather than deleting:
# noindexed via src/lib/noindex-drafts.ts (excluded from index/sitemap/RSS,
# served `robots: noindex, follow`) so the underlying analysis survives for
# a human fact-check/rewrite, pending Elliott's decision to fix or delete.
#
# Noindexed (content/blog/):
#   - congress-bank-stock-trades-during-crisis.md — Sen. Tim Scott (R-SC):
#     "$8.2M in JPMorgan, BAC, GS", "Sold $1.98M in regional banks",
#     "Sidestepped $1.8M+ in losses"; Rep. Patrick McHenry (R-NC): "$3.4M in
#     major banks", "$847K in regional banks", sold "$806K" — plus an
#     invented Fed "confidential briefing to Banking Committee: February 1
#     (morning)" timeline with no source.
#   - congress-healthcare-stock-trades-analysis.md — Rep. John Boozman
#     (R-AR): "$412,000... win rate 81.6%"; Sen. Patty Murray (D-WA):
#     "$348,000... win rate 73.8%". PTRs never report realized gains or win
#     rates.
#   - congress-pharmaceutical-trades-before-votes.md — Rep. J. French Hill
#     (R-AR): "$1.2 million in Eli Lilly", "$800K in Merck", "$600K in
#     Pfizer", "Total pharmaceutical profit Q1 2026: $187,400"; Rep. Greg
#     Walden (R-OR): "$1.8 million... $1.4 million... $1.1 million", profit
#     "$234,100" — plus an unsourced "Trial data briefing: January 6
#     (before public release)" claim.
#   - congress-ai-stock-investments-2026.md — invented private-placement
#     allocations presented as fact: "$67 million in preferred stock" in an
#     OpenAI Series C round, "$43 million" in an Anthropic Series D round,
#     plus per-event profit figures ("$37.2 million", "$9.98 million",
#     "$10.45 million") tied to specific hearing dates. No individual is
#     named here (unlike the other three), but no disclosed mechanism gives
#     Congress members private funding-round allocations and no PTR data
#     supports any of it.
#
# NOT fixed, flagged for a follow-up pass (same defect, same "named
# legislator + fabricated P&L" pattern, but outside the 3 topical angles
# this pass was scoped to — still live and indexed):
#   - congress-semiconductor-stock-trades.md — Rep. Greg Walden, Rep. Tom
#     Emmer, Sen. Ron Johnson, each with fabricated holdings/profit figures.
#   - congress-big-tech-antitrust-trading.md — Rep. Ken Buck, Rep. Jerry
#     Nadler, each with fabricated purchase/profit figures.
#
# tsc --noEmit clean. Pushed as a fast-forward. See git log for the commit
# with the full per-post breakdown.
# ============================================================

# ⚠️ FOLLOW-UP — 2026-09-06 — both dormant clusters resolved: DELETED ⚠️
# ============================================================
# Revisited the two dormant clusters flagged below. Read both DORMANT.md
# files and every file inside before deciding.
#
# _dormant-quant-backend-stub/: confirmed it was exactly what its DORMANT.md
# said -- one 372-byte stale orchestration CLAUDE.md, zero code, a one-char
# collision with the real quant/backend/. git rm -r'd. Easy call.
#
# content/_dormant-articles/ (8 files): the original audit's claim that
# algorithmic-execution-system-v2.md "reads as real, non-templated content"
# did NOT hold up on an actual read. All 8 files -- that one included --
# open with the identical boilerplate sentence ("...is a systematic
# quantitative trading approach based on statistical analysis, historical
# backtesting, and algorithmic execution...") with only the strategy name
# swapped in, carry the same spammy clickbait meta_description pattern
# ("Act now", "Discover. Discover", "Limited time"), and present specific,
# clearly-fabricated backtest numbers (exact trade counts, per-trade P&L,
# a fictional October 2025 sample month) as if they were real results --
# the same pattern already caught and noindexed elsewhere on this site
# (mean-reversion-trading-strategy.md, flagged 2026-09-05 for "invented
# numbers" presented as a real backtest). This is the same generator output
# as the already-deleted generated-articles/ and posts/, just missed by the
# first pass. Nothing in the directory cleared the bar for content/blog/;
# publishing any of it would add to, not fix, the site's known
# scaled-content risk (the 50+ templated congress-* posts already flagged
# for pruning). git rm -r'd the whole directory -- no file moved.
#
# tsc --noEmit clean afterward. Pushed as a fast-forward (no divergence).
# ============================================================

# ⚠️ SESSION CHECKPOINT — 2026-09-06 — dead-code/bloat cleanup ⚠️
# ============================================================
# Independently re-verified a prior audit's dead-code/bloat findings (did not
# trust it blindly), then acted only on what I could personally confirm:
#
# Deleted (confirmed zero references anywhere, git rm -r, commit e1b5d15):
# app/blog/ (185 root-level orphan files), generated-articles/ (128 templated
# files), posts/ (25 BookCLI-generated files), marketing/ (358 files incl.
# marketing/blog + an orphaned sitemap.xml), and 110 loose .md files sitting
# inside quant/frontend/src/app/blog/ itself (inert next to page.tsx/
# [slug]/page.tsx, which read content/blog/ one level up, not this folder).
#
# Renamed + flagged dormant at the time (naming-collision clusters that
# could have been unfinished-but-wanted work): content/articles/ ->
# content/_dormant-articles/, and root quant-backend/ ->
# _dormant-quant-backend-stub/. Both later reviewed and DELETED -- see the
# follow-up checkpoint above for the reasoning.
#
# Explicitly left alone: quant/backend/app/api/v1/subscription.py -- also
# confirmed dead (never imported by api/v1/__init__.py; only the plural
# subscriptions.py is registered) and confirmed to be the literal cause of
# frontend calls to /api/v1/subscription/* 404ing in production today
# (settings/subscription/page.tsx and settings/referral/page.tsx both call
# the singular path). Not touched because it sits inside the paused
# free-forever-vs-paid pricing decision below -- Elliott said hold off
# without his sign-off, and fixing this audit pass didn't require touching it.
# Also left the 203 root *.md status/report files alone (too many to verify
# individually this pass).
#
# Verified: npx tsc --noEmit clean (node_modules reinstalled -- had been
# cleared repo-wide during the disk-space emergency). Pushed straight to
# main (autopublish branch was main + 2 commits, fast-forwarded); new
# production deploy confirmed Ready and aliased to quantengines.com; curled
# homepage, /blog, a live post, and /congress-stock-trades/late-filers, all
# HTTP 200.
# ============================================================

# ⚠️ SESSION CHECKPOINT — 2026-09-05 — READ THIS FIRST, IT SUPERSEDES BELOW ⚠️
# ============================================================
# A long session today audited + fixed this site and 3 siblings
# (affiliate/calc/credit). Read this before assuming the goals/priorities
# below are current.
# ============================================================

## Status: this is the BEST-PERFORMING site in the portfolio
Real organic search traffic at 59.2% engagement (highest of any channel on
any of the 4 sites), disproportionate AI-assistant (ChatGPT/Gemini/Copilot)
referral traffic at 39.6% engagement, real product usage of /scanner and
/charts, 100/100 PageSpeed score. The winning pattern is proven: specific,
practitioner-level content with real code/real numbers (not "intro to
trading" filler) — do not deviate from this into generic content.

## ⚠️ PENDING DECISION — do not touch subscription/pricing code without checking in
`app/pricing/page.tsx` publicly commits to "Open Beta - Free Forever / No
paywalls" — a deliberate product decision. Meanwhile `quant/backend/app/api/v1/
subscriptions.py` has a fully-built Stripe integration never wired to the
frontend, and the frontend/backend/docs describe THREE mutually inconsistent
API contracts for it (frontend calls singular `/subscription/*`, backend
router is plural `/subscriptions/*`, `HYBRID_MODEL_SETUP.md` describes a third
shape entirely) — there is no single coherent thing to "just wire up."
Elliott has said to hold off on this pending a real decision: keep free-forever
and clean up the dead Stripe code, or reverse the pricing-page copy first and
reconcile one consistent contract before touching checkout. `SubscriptionStatus.tsx`
got one trivial type-completeness commit today (`price: undefined` on two tier
configs) that was confirmed to add zero new gating/billing behavior — nothing
else in this area should be touched without Elliott's explicit sign-off.

## What shipped today
- Fixed hardcoded GA4 ID (was G-PHX6T0R1Y1 baked into layout.tsx) to read from
  NEXT_PUBLIC_GA_MEASUREMENT_ID like the other 3 sites; Vercel env var set.
- Fixed a real registration bug: `api.auth.register()`'s signature was
  `(email, password, name)` but the call site passed `(name, email, password)`
  — would have silently put a user's plaintext password into a `name` field.
  Also discovered login/profile pages were calling methods (`api.login()` etc.)
  that didn't exist on the API client at all — genuinely broken in production
  before today's fix.
- Real TypeScript/schema-drift fixes across fraud-detection/payouts-adjacent
  code, verified via an independently re-run typecheck, not just trusted.
- Added inline contextual links from top-performing posts into /scanner,
  /charts, /backtesting/builder, then did a full audit: 199 more posts got a
  real, single, contextual tool link (out of 355 candidates reviewed — ~156
  correctly skipped as thin filler with no on-topic match). Added HowTo schema
  sitewide for "Step N" structured posts (a real bug — code-block comments
  being misread as headings — was caught and fixed during this).
- 3 new articles with genuinely *measured* results (not fabricated): actual
  Numba/vectorization benchmarks, an actual measured 11% equity-curve swing
  from a VectorBT API gotcha.
- **Found `mean-reversion-trading-strategy.md` is currently noindexed
  (`src/lib/noindex-drafts.ts`) for unresolved fabricated first-person backtest
  claims** ("we tested 1,247 variations..." with invented numbers) — this was
  cited earlier in the session as a "proven top-performing post" before this
  was known; it is NOT one to link more traffic toward until the fabrication
  is fixed or the post is rewritten honestly.
- New shareable feature: `/congress-stock-trades/late-filers` — a real,
  data-backed (FMP API disclosure dates) STOCK Act late-filing leaderboard,
  with honest on-page caveats (not a legal violation determination, doesn't
  cover full career history). Built for genuine backlink/share potential.

## Where to look for more context
GA4 property ID: 526411775. Vercel project name: "quant-analytics-frontend".
Distribution research done this session recommends submitting a real
congressional-trading finding to Quantocracy and pitching PyQuant News/
Quantified Strategies directly — see conversation history or ask Elliott.

---

# Quant - No-Code Backtesting Platform
No-code web GUI for backtesting. Stocks, options, crypto, forex.
## Goal: Revenue-generating SaaS or affiliate traffic driver
1. Assess current codebase
2. Core backtesting engine (VectorBT)
3. Strategy builder UI (drag-and-drop or form-based)
4. Data ingestion: Yahoo Finance, Alpha Vantage
5. Results visualization with interactive charts
6. Portfolio-level backtesting
7. Deploy preview
## Communication
- Coordinate with quant-backend and discovery
- Update /mnt/e/projects/.agent-bus/status/quant.md each cycle
