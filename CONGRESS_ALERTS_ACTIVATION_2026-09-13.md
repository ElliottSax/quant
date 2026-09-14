# Congress Trading Alerts — Activation Report & Setup Plan
**Date**: 2026-09-13  
**Status**: Code Complete (commit be8a84c), Infrastructure Pending  
**Live URL**: https://quantengines.com/congress-alerts  

---

## EXECUTIVE SUMMARY

The Congress Trading Alerts paid tier is **fully coded and ready to activate**, but requires:
1. **Supabase project** (for subscriber/filter storage)
2. **Stripe products & API keys** (for Pro tier billing)
3. **Environment variables** (set in Vercel & GitHub Actions secrets)
4. **SQL schema deployment** (run `congress_alerts.sql` once)
5. **Webhook configuration** (Stripe → quantengines.com/api/congress-alerts/webhook)

**Timeline**: All configuration steps can complete in under 30 minutes once accounts are provisioned.

---

## CURRENT INFRASTRUCTURE STATUS

### What's Already Set (Verified Live)
| Service | Status | Notes |
|---------|--------|-------|
| Resend | ✅ Active | API key already in Vercel (`RESEND_API_KEY`) |
| Financial Modeling Prep | ✅ Active | `FMP_API_KEY` in Vercel, powers both free congress browser + paid alerts |
| Next.js App | ✅ Deployed | quantengines.com on Vercel (quant-analytics-frontend project) |
| Free Tier UI | ✅ Live | `/congress-alerts` page, form components, signup flow |
| Digest Script | ✅ Coded | `quant/scripts/congress_alerts_digest.py` ready to schedule |
| GitHub Actions Workflow | ✅ Coded | `.github/workflows/congress-alerts-digest.yml` ready (13:00 UTC daily) |

### What's Missing (Blocks Go-Live)
| Component | What's Needed | Why It Matters |
|-----------|---------------|-----------------|
| **Supabase Project** | New PostgreSQL instance | Stores subscriber emails, subscription tiers, filter preferences |
| **Stripe Products** | 2 price objects (monthly $9, yearly $79) | Enables Pro tier checkout & subscription management |
| **Stripe API Keys** | Secret + Publishable keys | Authenticates checkout & webhook handlers |
| **Webhook Secret** | Stripe signing key | Validates paid subscription confirmations |
| **Vercel Env Vars** | 7 new variables (see checklist below) | Connects Next.js routes to Stripe/Supabase |
| **GitHub Secrets** | 3 repo secrets for the digest cron | Powers daily/weekly email delivery |

---

## STEP-BY-STEP ACTIVATION PLAN

### Step 1: Create Supabase Project (5 min)

**Action**: Create a new free Supabase project via https://supabase.com/dashboard

1. Log in to Supabase dashboard (or sign up if needed)
2. Click **New Project**
3. Fill in:
   - **Project name**: `quant-congress-alerts` (or any name)
   - **Database password**: Generate a strong password (save it, you'll need it once)
   - **Region**: US East (us-east-1) recommended for lowest latency
   - **Pricing Plan**: Free tier is fine (enough for thousands of subscribers)
4. Wait for provisioning (2-3 minutes)
5. Once created, copy these values:
   - **Project URL**: Shows in dashboard overview, format: `https://xxxxxxxxxxxxx.supabase.co`
   - **Service Role Key**: Settings → API → `service_role` (labeled "secret", starts with `eyJ`)
   - **Anon Key**: Settings → API → `anon` (for reference, not used by this feature)

**⚠️ Critical**: Do NOT share the Service Role Key publicly. It bypasses Row Level Security.

---

### Step 2: Deploy SQL Schema (2 min)

**Action**: Run `quant/frontend/supabase/congress_alerts.sql` against the new project

**Option A — Via Supabase Web Dashboard** (easiest):
1. Open the new Supabase project
2. Go to **SQL Editor** (left sidebar)
3. Click **New Query**
4. Copy the entire contents of `quant/frontend/supabase/congress_alerts.sql`
5. Paste into the editor
6. Click **Run**
7. Confirm: You should see two new tables in **Table Editor** → `congress_alert_subscribers` and `congress_alert_filters`

**Option B — Via Supabase CLI** (if installed):
```bash
supabase db execute -f quant/frontend/supabase/congress_alerts.sql \
  --project-ref YOUR_PROJECT_ID
```

---

### Step 3: Create Stripe Products & Prices (10 min)

**Action**: Create two price objects in Stripe Dashboard for the Pro tier

1. Log in to Stripe Dashboard (https://dashboard.stripe.com/)
2. Navigate to **Products** (left sidebar)
3. Click **+ Add Product**
4. Create **Product 1: Congress Alerts Pro**
   - **Name**: `Congress Alerts Pro`
   - **Description**: `Congress Trading Alerts - Daily digest, 25 filters`
   - **Type**: Recurring (not one-time)
   - **Recurring billing period**: Monthly
   - **Price**: $9.00 USD
   - Leave other fields as default
   - Click **Save product**
5. You now have a **Monthly Price ID** (shown on the product page, format: `price_xxxxx`)
   - **Copy this value** and save it as `STRIPE_CONGRESS_ALERTS_PRICE_MONTHLY`

6. Click **+ Add price** (on the same product page)
   - **Billing period**: Yearly
   - **Price**: $79.00 USD
   - Click **Save**
   - **Copy the Yearly Price ID** and save it as `STRIPE_CONGRESS_ALERTS_PRICE_YEARLY`

**Verify**: You should now see both prices listed under the Congress Alerts Pro product.

---

### Step 4: Set Up Stripe Webhook (5 min)

**Action**: Register the webhook endpoint in Stripe Dashboard

1. Stripe Dashboard → **Developers** (top-right)
2. Click **Webhooks** (left sidebar)
3. Click **+ Add endpoint**
4. **Endpoint URL**: `https://quantengines.com/api/congress-alerts/webhook`
5. **Events to send**: 
   - Check `checkout.session.completed`
   - Check `invoice.payment_succeeded` (for renewal confirmations)
   - Uncheck everything else
6. Click **Add endpoint**
7. You now have a **Signing Secret** (shown on the webhook details page, starts with `whsec_`)
   - **Copy this value** and save it as `STRIPE_CONGRESS_ALERTS_WEBHOOK_SECRET`

**Test**: After setting environment variables (Step 5), you can test via Stripe Dashboard → **Send test event** → select the endpoint and event type.

---

### Step 5: Add Environment Variables to Vercel (5 min)

**Action**: Set 7 new environment variables in the Vercel project

Run these commands from the quant directory:

```bash
cd /c/projects/quant

# Supabase configuration
vercel env add SUPABASE_URL
# Paste: https://xxxxxxxxxxxxx.supabase.co (from Step 1)

vercel env add SUPABASE_SERVICE_ROLE_KEY
# Paste: eyJ... (from Step 1, Settings → API → service_role)

# Stripe configuration  
vercel env add STRIPE_SECRET_KEY
# Paste: sk_live_... (from Stripe Dashboard → Developers → API Keys)

vercel env add STRIPE_CONGRESS_ALERTS_PRICE_MONTHLY
# Paste: price_xxxxx (from Step 3, Monthly price ID)

vercel env add STRIPE_CONGRESS_ALERTS_PRICE_YEARLY
# Paste: price_xxxxx (from Step 3, Yearly price ID)

vercel env add STRIPE_CONGRESS_ALERTS_WEBHOOK_SECRET
# Paste: whsec_... (from Step 4)

# Email configuration (may already exist, verify)
vercel env add RESEND_FROM
# Paste: QuantEngines Congress Alerts <alerts@quantengines.com>
```

**Verify in Vercel**:
```bash
vercel env list
```
You should see all 7 new variables listed (values shown as "Encrypted").

---

### Step 6: Add GitHub Actions Secrets (3 min)

**Action**: Set 3 repo secrets for the digest cron workflow

1. Go to GitHub repo settings: https://github.com/ElliottSax/quant
2. Navigate to **Secrets and variables** → **Actions**
3. Click **New repository secret** and add these three:

| Secret Name | Value |
|-------------|-------|
| `SUPABASE_URL` | Same as Vercel: `https://xxxxxxxxxxxxx.supabase.co` |
| `SUPABASE_SERVICE_ROLE_KEY` | Same as Vercel: `eyJ...` (service_role key) |
| `FMP_API_KEY` | Already set (or copy from Vercel env) |

**Note**: `RESEND_API_KEY` is inherited from the repo's other workflows, so it should already be present. If missing, add it too.

---

### Step 7: Deploy to Production (1 min)

**Action**: Verify code is current, then trigger deployment

```bash
cd /c/projects/quant
git status
# Should show clean tree or only unrelated changes
git log --oneline | head -1
# Should show be8a84c or a later commit
```

Vercel auto-deploys on every push to `main`. If there have been commits since be8a84c:
- Deployment should be live (check https://quantengines.com/congress-alerts in browser)
- If needed, manually trigger via Vercel Dashboard → **Deployments** → **Redeploy**

---

## CONFIGURATION CHECKLIST

### Stripe API Keys (from Dashboard → Developers → API Keys)

```
STRIPE_SECRET_KEY=sk_live_........................
# (live mode, not test mode — use test mode for testing first if desired)
```

**Get your keys**:
1. Stripe Dashboard → **Developers** (top-right)
2. Click **API Keys**
3. Copy **Secret key** (starts with `sk_live_` or `sk_test_`)
4. If you want to test first, use `sk_test_` keys (separate from production)

---

### Vercel Environment Variables Summary

```bash
# Required for Congress Alerts
SUPABASE_URL=https://xxxxxxxxxxxxx.supabase.co
SUPABASE_SERVICE_ROLE_KEY=eyJ...
STRIPE_SECRET_KEY=sk_live_...
STRIPE_CONGRESS_ALERTS_PRICE_MONTHLY=price_...
STRIPE_CONGRESS_ALERTS_PRICE_YEARLY=price_...
STRIPE_CONGRESS_ALERTS_WEBHOOK_SECRET=whsec_...
RESEND_FROM=QuantEngines Congress Alerts <alerts@quantengines.com>

# Already set (no action needed)
FMP_API_KEY=... (reused from congress-trades browser)
RESEND_API_KEY=... (reused from newsletter route)
NEXT_PUBLIC_GA_MEASUREMENT_ID=...
```

---

### GitHub Secrets Summary

```
SUPABASE_URL=https://xxxxxxxxxxxxx.supabase.co
SUPABASE_SERVICE_ROLE_KEY=eyJ...
FMP_API_KEY=... (copy from Vercel if missing)
```

The `.github/workflows/congress-alerts-digest.yml` workflow will pick these up automatically.

---

## WHAT EACH COMPONENT DOES

### Frontend UI (`/congress-alerts`)
- **File**: `quant/frontend/src/app/congress-alerts/page.tsx`
- **Signup Form**: `quant/frontend/src/app/congress-alerts/CongressAlertsSignupForm.tsx`
- Shows pricing: Free weekly (1 filter) vs Pro ($9/mo or $79/yr, 25 filters)
- Collects email + filters, submits to `/api/congress-alerts/signup`

### API Routes

| Route | Method | Purpose |
|-------|--------|---------|
| `/api/congress-alerts/signup` | POST | Create free subscriber or start Pro checkout |
| `/api/congress-alerts/webhook` | POST | Receive Stripe payment confirmations |
| `/api/congress-alerts/manage/[token]` | GET/POST | Self-serve filter management & cancellation |
| `/api/congress-alerts/portal` | GET | Redirect to Stripe Customer Portal |

### Database Schema

**congress_alert_subscribers**
- `email`: Unique subscriber email
- `tier`: 'free' or 'pro'
- `status`: 'active', 'pending' (checkout in progress), 'canceled', or 'past_due'
- `stripe_customer_id`: Linked Stripe customer (null for free)
- `stripe_subscription_id`: Active subscription (null for free)
- `manage_token`: Token for self-serve email links
- `last_digest_sent_at`: Cursor for digest scheduling

**congress_alert_filters**
- `subscriber_id`: FK to subscribers
- `ticker`: Stock ticker (e.g., "AAPL") — optional
- `member_name`: Congress member name — optional  
- `chamber`: "House" or "Senate" — optional
- Row must have at least one non-null field

### Digest Script (`quant/scripts/congress_alerts_digest.py`)
- Scheduled by GitHub Actions cron (13:00 UTC daily)
- Fetches new trades from Financial Modeling Prep
- Queries all subscribers via Supabase
- For each subscriber, finds matching trades against saved filters
- Sends email via Resend if new matches found
- Updates `last_digest_sent_at` cursor

**Free subscribers**: Email at most once per 7 days  
**Pro subscribers**: Email daily (if new matches)

---

## TESTING CHECKLIST (Post-Deployment)

### Pre-Launch Tests

- [ ] **Supabase**: Login to dashboard, verify `congress_alert_subscribers` & `congress_alert_filters` tables exist
- [ ] **Stripe**: Verify both products (monthly + yearly) exist with correct prices
- [ ] **Vercel**: Confirm all 7 environment variables set (`vercel env list`)
- [ ] **UI**: Visit https://quantengines.com/congress-alerts, page loads, form visible
- [ ] **Free signup**: Enter email, click "Get Weekly Alerts", success message appears
- [ ] **Free subscriber created**: Query Supabase SQL → `SELECT * FROM congress_alert_subscribers WHERE email = 'test@example.com'` → should see tier='free', status='active'

### Pro Tier Tests (Use Stripe Test Mode First)

- [ ] **Switch to test keys**: Use `sk_test_` Stripe secret key + test product/prices for testing
- [ ] **Pro checkout**: On the form, select Pro plan, click "Get Pro", redirected to Stripe Checkout
- [ ] **Stripe Checkout**: Page loads, shows price, accepts test card `4242 4242 4242 4242` (exp: any future date, CVC: any 3 digits)
- [ ] **Webhook received**: After payment, check Stripe Dashboard → Webhooks → view the event → should show success
- [ ] **Supabase updated**: Query → `SELECT * FROM congress_alert_subscribers WHERE email='test@example.com'` → should see tier='pro', status='active' (or 'pending' briefly before webhook)
- [ ] **Manage link**: Check email received from Resend with digest + manage link
- [ ] **Manage page**: Click link in email, filters management page loads, can add/edit/delete filters

### Digest Cron Tests

- [ ] **Trigger manually**: GitHub Actions → congress-alerts-digest workflow → Run workflow → check logs
- [ ] **Free digest sent**: Free subscriber gets email after workflow completes (once per 7 days rule observed)
- [ ] **Pro digest sent**: Pro subscriber gets email (daily if new matches)
- [ ] **Filter matching**: Update filters in manage page, verify next digest honors new filters

### Live Mode Activation

Once tests pass:
1. In Stripe Dashboard, **switch back to live keys** (`sk_live_`)
2. Update Vercel `STRIPE_SECRET_KEY` with live secret key
3. Stripe webhook will auto-send live events to the same endpoint
4. First real paying customer creates a subscription → verify Supabase + email

---

## PRICING & COMPETITIVE CONTEXT

**Model**: Free tier + paid add-on (does NOT gate the free backtesting tool or congress-trades browser)

| Tier | Price | Features | Freshness |
|------|-------|----------|-----------|
| **Free** | $0 | Weekly email, 1 saved filter | Same-day to next-day after FMP update |
| **Pro** | $9/mo | Daily email, 25 saved filters | Same-day to next-day after FMP update |
| **Pro** | $79/yr | (same as monthly, better value) | Same-day to next-day after FMP update |

**Why this pricing**:
- **Quiver Quantitative**: ~$25–30/mo for congress alerts + other data
- **Unusual Whales**: $50+/mo for options flow bundle (congress alerts bundled in)
- **Capitol Trades**: Free (no alerts)
- **QuantEngines Congress Alerts**: $9/mo (alerts only, undercuts both)

**Honest freshness**: 
- STOCK Act members have up to 45 days to file after a trade
- FMP's feed updates daily, not real-time
- Alerts are same-day to next-day after FMP has the data (not faster)
- Page copy + digest emails explicitly state these limits

---

## KNOWN ISSUES & NOTES

### Existing Supabase Project (No Longer Available)
The old Supabase project (`jznljskfvhlqlshofkvd`) referenced in the codebase no longer exists. The newsletter route was updated to use Resend instead (see `frontend/src/app/api/newsletter/route.ts` comments). The new Congress Alerts feature has no dependency on this; it requires a fresh Supabase project.

### Dead Stripe Code in Backend
`quant/backend/app/api/v1/subscriptions.py` contains unused Stripe code for the core backtesting tool. It is NOT involved in Congress Alerts — this feature has its own, separate Stripe integration. See CLAUDE.md for the history of that paused decision.

### GitHub Actions Workflow Location
The digest workflow is at `.github/workflows/congress-alerts-digest.yml` (repo root), NOT `quant/.github/workflows/` — GitHub Actions only scans the root directory. See the workflow file's header comment for context.

---

## ESTIMATED TIMELINE

| Step | Time | Notes |
|------|------|-------|
| Create Supabase project | 5 min | Mostly waiting for provisioning |
| Deploy SQL schema | 2 min | Copy/paste + run one query |
| Create Stripe products | 10 min | Two price objects, copy price IDs |
| Set up webhook | 5 min | Register endpoint + copy signing secret |
| Add Vercel vars | 5 min | Run `vercel env add` commands |
| Add GitHub secrets | 3 min | Paste 3 secrets in settings |
| Test & deploy | 10 min | Verify UI, test free + pro flows |
| **Total** | **~40 min** | All parallelizable after Supabase provisioning |

---

## NEXT STEPS

**To activate Congress Alerts**:

1. ✅ Code is complete (commit be8a84c is live)
2. ⏳ **Run the 7-step setup plan above** (Steps 1–7)
3. ✅ Existing deployment at quantengines.com will auto-pick up new env vars
4. ✅ Test free + pro signup flows
5. ✅ Watch GitHub Actions → congress-alerts-digest run at 13:00 UTC daily

**For outreach** (once live):
- See `OUTREACH_DRAFTS.md` — ready-to-send pitches to Quantocracy, PyQuant News, Quantified Strategies
- Re-pull fresh numbers from `/congress-stock-trades/late-filers` before sending
- Elliott to review + send (no automation set up for outreach)

---

## CONTACT / QUESTIONS

All code, schema, and configurations are documented inline in the repo:
- Feature overview: `quant/frontend/src/app/congress-alerts/` + `quant/frontend/src/lib/congress-alerts.ts`
- API routes: `quant/frontend/src/app/api/congress-alerts/`
- Digest script: `quant/scripts/congress_alerts_digest.py`
- Workflow: `.github/workflows/congress-alerts-digest.yml`
- Database schema: `quant/frontend/supabase/congress_alerts.sql`

All variables and secrets are listed in their respective `.env.production.example` files.
