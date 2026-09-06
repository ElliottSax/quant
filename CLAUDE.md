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
# Renamed + flagged dormant, NOT deleted (naming-collision clusters that
# could be unfinished-but-wanted work; each has a DORMANT.md explaining the
# open decision): content/articles/ -> content/_dormant-articles/ (sits
# beside the live content/blog/, one file is real non-templated content),
# and root quant-backend/ -> _dormant-quant-backend-stub/ (one-character
# collision with the real quant/backend/, contains only a stale
# orchestration CLAUDE.md, no code).
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
