# Deployment Checklist - Quant Platform

**Use this checklist to ensure a smooth production deployment.**

---

## Phase 1: Pre-Deployment (15 mins)

### Generate Secrets

```bash
# Generate 2 different secure keys (copy both)
python -c "import secrets; print('SECRET_KEY=' + secrets.token_urlsafe(32))"
python -c "import secrets; print('JWT_SECRET_KEY=' + secrets.token_urlsafe(32))"
```

- [ ] `SECRET_KEY` generated (32+ chars)
- [ ] `JWT_SECRET_KEY` generated (32+ chars, different)
- [ ] Both saved in password manager

### Get API Keys

- [ ] **Stripe Account** created (https://stripe.com)
  - [ ] Test API keys obtained
  - [ ] Live API keys ready (will activate later)
- [ ] **Railway Account** created (https://railway.app)
- [ ] **Vercel Account** created (https://vercel.com)

### Optional API Keys

- [ ] Polygon.io API key (free tier for stock data)
- [ ] Alpha Vantage API key (free tier for stock data)
- [ ] Resend API key (free 100 emails/day)
- [ ] Sentry DSN (error tracking)

---

## Phase 2: Backend Deployment (15 mins)

### Railway Setup

```bash
# Install CLI
npm install -g @railway/cli

# Login
railway login
```

- [ ] Railway CLI installed
- [ ] Logged into Railway

### Create Project

```bash
cd /mnt/e/projects/quant/quant/backend
railway init
```

- [ ] Railway project created
- [ ] Project named (e.g., "quant-backend")

### Add Databases

```bash
railway add --database postgres
railway add --database redis
```

- [ ] PostgreSQL added (DATABASE_URL auto-set)
- [ ] Redis added (REDIS_URL auto-set)

### Set Environment Variables

Copy and run these commands with YOUR values:

```bash
# Core
railway variables set ENVIRONMENT=production
railway variables set DEBUG=false
railway variables set PROJECT_NAME="Quant Platform"
railway variables set API_V1_STR="/api/v1"

# Security
railway variables set SECRET_KEY="PASTE_YOUR_SECRET_KEY_HERE"
railway variables set JWT_SECRET_KEY="PASTE_YOUR_JWT_SECRET_KEY_HERE"
railway variables set ALGORITHM="HS256"

# Stripe (test keys first)
railway variables set STRIPE_SECRET_KEY="sk_test_PASTE_HERE"
railway variables set STRIPE_PUBLISHABLE_KEY="pk_test_PASTE_HERE"

# CORS (will update later)
railway variables set BACKEND_CORS_ORIGINS='["https://localhost:3000"]'

# Optional
railway variables set POLYGON_API_KEY="your_key_here"
railway variables set RESEND_API_KEY="re_your_key_here"
railway variables set SENTRY_DSN="your_sentry_dsn_here"

# Security
railway variables set TRUST_PROXY_HEADERS="true"
```

- [ ] All required variables set
- [ ] Optional variables set (if using)

### Deploy Backend

```bash
railway up
railway domain
```

- [ ] Backend deployed successfully
- [ ] Public domain generated (save URL: `________________`)

### Run Migrations

```bash
railway run bash
alembic upgrade head
exit
```

- [ ] Database migrations completed

### Test Backend

```bash
# Replace with your Railway URL
curl https://YOUR-RAILWAY-URL.up.railway.app/health
```

**Expected Response:**
```json
{
  "status": "healthy",
  "environment": "production",
  "services": {
    "database": "connected",
    "cache": "connected"
  }
}
```

- [ ] Health check returns 200 OK
- [ ] Database status: "connected"
- [ ] Cache status: "connected"

---

## Phase 3: Frontend Deployment (10 mins)

### Vercel Setup

```bash
# Install CLI
npm install -g vercel

# Login
vercel login
```

- [ ] Vercel CLI installed
- [ ] Logged into Vercel

### Configure Environment

```bash
cd /mnt/e/projects/quant/quant/frontend
cp .env.production.example .env.production.local
```

Edit `.env.production.local` with:
```bash
NEXT_PUBLIC_API_URL=https://YOUR-RAILWAY-URL.up.railway.app
NEXT_PUBLIC_STRIPE_PUBLISHABLE_KEY=pk_test_YOUR_KEY
```

- [ ] `.env.production.local` created
- [ ] Railway backend URL added
- [ ] Stripe publishable key added

### Deploy to Vercel

```bash
vercel
# Follow prompts, then:
vercel --prod
```

- [ ] Vercel project created
- [ ] Production deployment successful
- [ ] Vercel URL obtained (save URL: `________________`)

### Set Environment Variables in Vercel

1. Go to https://vercel.com/dashboard
2. Select your project
3. Settings > Environment Variables
4. Add for **Production**:
   - `NEXT_PUBLIC_API_URL` = Your Railway URL
   - `NEXT_PUBLIC_STRIPE_PUBLISHABLE_KEY` = Your Stripe key

- [ ] Environment variables set in Vercel Dashboard
- [ ] Redeployed after setting variables

### Update Backend CORS

```bash
# Update with YOUR Vercel URL
railway variables set BACKEND_CORS_ORIGINS='["https://your-app.vercel.app"]'
railway up
```

- [ ] CORS updated with Vercel URL
- [ ] Backend redeployed

### Test Frontend

Visit: `https://your-app.vercel.app`

- [ ] Homepage loads
- [ ] No console errors
- [ ] API calls work (check Network tab)
- [ ] Login/signup pages render

---

## Phase 4: Stripe Webhook (5 mins)

### Create Webhook

1. Go to https://dashboard.stripe.com/webhooks
2. Click **Add endpoint**
3. Enter URL: `https://YOUR-RAILWAY-URL.up.railway.app/api/v1/subscriptions/webhooks/stripe`
4. Select events:
   - `customer.subscription.created`
   - `customer.subscription.updated`
   - `customer.subscription.deleted`
   - `invoice.payment_succeeded`
   - `invoice.payment_failed`
5. Click **Add endpoint**

- [ ] Webhook endpoint created in Stripe
- [ ] Events selected

### Get Signing Secret

1. Click on webhook
2. Click **Reveal** under Signing secret
3. Copy secret (starts with `whsec_`)

- [ ] Webhook signing secret copied

### Add to Backend

```bash
railway variables set STRIPE_WEBHOOK_SECRET="whsec_YOUR_SECRET_HERE"
railway up
```

- [ ] Webhook secret added to Railway
- [ ] Backend redeployed

### Test Webhook

In Stripe Dashboard:
1. Go to webhook
2. Click **Send test webhook**
3. Select `customer.subscription.created`
4. Click **Send test webhook**

- [ ] Test webhook sent
- [ ] Response shows **Success (200)**

---

## Phase 5: Final Testing (10 mins)

### Test Complete Flow

1. **Visit frontend:** `https://your-app.vercel.app`
2. **Sign up** for an account
3. **Go to pricing page:** `/pricing`
4. **Click subscribe** on a plan
5. **Complete checkout** with test card: `4242 4242 4242 4242`
6. **Verify subscription** activated

- [ ] User signup works
- [ ] Pricing page loads
- [ ] Stripe checkout opens
- [ ] Test payment succeeds
- [ ] Subscription activates
- [ ] User has premium access

### Test Backend Endpoints

```bash
BACKEND_URL="https://YOUR-RAILWAY-URL.up.railway.app"

# API docs
open $BACKEND_URL/api/v1/docs

# Test authenticated endpoint (need token)
# Get token by logging in via frontend, then:
curl -H "Authorization: Bearer YOUR_TOKEN" \
  $BACKEND_URL/api/v1/subscriptions/current
```

- [ ] API docs load (`/api/v1/docs`)
- [ ] Authenticated endpoints work
- [ ] Rate limiting works

### Test Backtesting (if enabled)

1. Go to `/backtest/new`
2. Enter symbol: `AAPL`
3. Select strategy: `MA Crossover`
4. Run backtest

- [ ] Backtest page loads
- [ ] Stock data fetches (Yahoo Finance)
- [ ] Results page shows metrics
- [ ] Charts render

---

## Phase 6: Monitoring & Security (5 mins)

### Error Tracking

If using Sentry:
```bash
# Backend
railway variables set SENTRY_DSN="your_sentry_dsn"

# Frontend (in Vercel Dashboard)
NEXT_PUBLIC_SENTRY_DSN="your_sentry_dsn"
```

- [ ] Sentry configured (if using)
- [ ] Test error logged to Sentry

### Check Logs

```bash
# Railway logs
railway logs

# Vercel logs
# Visit: https://vercel.com/yourname/project/deployments
```

- [ ] No critical errors in Railway logs
- [ ] No critical errors in Vercel logs

### Security Headers

Check: https://securityheaders.com/?q=https://your-app.vercel.app

- [ ] Security headers present (should get A or A+)
- [ ] HTTPS enabled (automatic)
- [ ] CSP headers configured

### Rate Limiting

Test by making 100+ requests rapidly:

```bash
for i in {1..100}; do
  curl https://YOUR-BACKEND-URL.up.railway.app/api/v1/subscriptions/plans
done
```

- [ ] Rate limiting triggers (429 response)
- [ ] Error message is helpful

---

## Phase 7: Go Live (Production Keys)

### Switch to Live Stripe Keys

**ONLY AFTER TESTING EVERYTHING WITH TEST KEYS**

1. Get live keys from Stripe Dashboard
2. Update Railway:
   ```bash
   railway variables set STRIPE_SECRET_KEY="sk_live_YOUR_LIVE_KEY"
   railway variables set STRIPE_PUBLISHABLE_KEY="pk_live_YOUR_LIVE_KEY"
   railway up
   ```
3. Update Vercel:
   - Dashboard > Environment Variables
   - Update `NEXT_PUBLIC_STRIPE_PUBLISHABLE_KEY` to live key
   - Redeploy

4. Update webhook to use live mode:
   - Stripe Dashboard > Webhooks
   - Toggle to **Live mode**
   - Update webhook secret in Railway

- [ ] Live Stripe keys active
- [ ] Test payment with real card
- [ ] Money appears in Stripe balance
- [ ] Webhook works in live mode

### Final Production Checks

- [ ] All test data removed
- [ ] Admin accounts created
- [ ] Support email configured
- [ ] Terms of Service page live
- [ ] Privacy Policy page live
- [ ] Contact page working

---

## Post-Launch Monitoring

### Daily Checks (First Week)

- [ ] Check Railway logs for errors
- [ ] Check Vercel deployment status
- [ ] Check Stripe Dashboard for payments
- [ ] Check Sentry for errors (if configured)
- [ ] Monitor user signups

### Weekly Checks

- [ ] Review performance metrics
- [ ] Check database size (Railway)
- [ ] Review costs (Railway, Vercel, Stripe)
- [ ] Backup database (Railway auto-backups)

---

## Rollback Plan

If something goes wrong:

### Rollback Frontend

```bash
# In Vercel Dashboard:
# Deployments > Select previous deployment > Promote to Production
```

### Rollback Backend

```bash
# Redeploy previous commit
git checkout PREVIOUS_COMMIT
railway up
git checkout main
```

### Emergency Shutdown

```bash
# Scale down backend
railway down

# Disable Vercel deployment
# Dashboard > Settings > Deployment Protection
```

---

## Support Resources

- **Railway Docs:** https://docs.railway.app
- **Vercel Docs:** https://vercel.com/docs
- **Stripe Docs:** https://stripe.com/docs
- **FastAPI Docs:** https://fastapi.tiangolo.com
- **Next.js Docs:** https://nextjs.org/docs

---

## Success Metrics

### Technical

- [ ] Uptime > 99%
- [ ] API response time < 500ms
- [ ] Zero critical errors in production
- [ ] Database backups running

### Business

- [ ] First paying customer within 2 weeks
- [ ] $1,000 MRR within 2 months
- [ ] < 5% churn rate
- [ ] > 10% free-to-paid conversion

---

**Deployment Status:**

- [ ] Backend deployed: `________________`
- [ ] Frontend deployed: `________________`
- [ ] Stripe configured: Yes / No
- [ ] Webhooks working: Yes / No
- [ ] Monitoring active: Yes / No
- [ ] Live keys enabled: Yes / No
- [ ] First payment received: Yes / No

**Deployed by:** ________________
**Date:** ________________
**Go-live date:** ________________

---

**Ready to launch!** 🚀
