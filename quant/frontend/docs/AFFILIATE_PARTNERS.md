# Affiliate partners: how a link goes live (quantengines.com)

Status when this was written (2026-10-04): **0 programs approved**. Nothing renders and the
disclosure page says the site carries no affiliate links. Nothing here earns until you paste an
approved tracking URL.

## What you paste

Set these in Vercel for the `quant-analytics-frontend` project (Production), then redeploy.
Each value is the **full tracking URL** from the partner's affiliate dashboard (https only).

| Env var | Partner | Where the URL comes from |
|---|---|---|
| `AFFILIATE_URL_IBKR` | Interactive Brokers | Interactive Brokers affiliate/referral program page after approval |
| `AFFILIATE_URL_M1` | M1 Finance | M1 partner/referral dashboard after approval |
| `AFFILIATE_URL_FMP` | Financial Modeling Prep | FMP affiliate dashboard after approval |

Rules the code enforces (see `src/lib/affiliate-partners.ts`):

- No variable, or an invalid value (not https, localhost/IP, credentials in the URL, or a
  placeholder like `quant2024`, `TODO`, `example`, `your_id`): **the block renders nothing** and
  the disclosure page keeps its "no affiliate links" wording.
- A valid value: the partner appears in the "Tools we link to" block on `/data-vendors` with
  `rel="sponsored noopener noreferrer"`, an "Affiliate link" marker and the commission
  disclosure, and `/affiliate-disclosure` switches to wording that names the partner. Clicks are
  reported to GA4 as `affiliate_click` through `window.trackAffiliateClick`.
- Add a new partner by adding an entry to `PARTNERS` in `src/lib/affiliate-partners.ts`
  (one factual line of description, no ratings, bonuses or performance claims; the test enforces
  that) and an env var.

The older broker block (`BrokerRecommendations`) stays off unless
`NEXT_PUBLIC_BROKER_AFFILIATES_ENABLED=1`, and its backend list still carries placeholder ids:
do not turn that flag on.

## Before the first link goes live

1. The partner has approved the site (the application is the blocker, not this code).
2. Read the partner's program terms for disclosure wording and add anything they require.
3. Set the env var, redeploy, open `/data-vendors` and `/affiliate-disclosure`, click the link
   once in a private window, and confirm the partner dashboard registers the click.

Tests: `npm run test` (`src/lib/__tests__/affiliate-partners.test.ts`).
