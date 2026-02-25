# Vercel Deployment Guide - Quant Platform

**Status**: Ready for Production Deployment
**Last Updated**: February 11, 2026
**Estimated Time**: 30-45 minutes

---

## Architecture Overview

The Quant platform uses a **split deployment** architecture:

- **Frontend (Next.js)**: Deployed to **Vercel** (optimized for Next.js)
- **Backend (FastAPI)**: Deployed to **Railway** or **Render** (Python support)
- **Database**: PostgreSQL on Railway/Render or Supabase
- **Redis**: Upstash or Railway Redis

```
┌─────────────┐      HTTPS       ┌──────────────┐
│   Vercel    │ ────────────────> │   Railway    │
│  (Frontend) │      API Calls    │  (Backend)   │
└─────────────┘                   └──────────────┘
                                         │
                                         ├─> PostgreSQL
                                         └─> Redis
```

---

## Table of Contents

1. [Pre-Deployment Checklist](#pre-deployment-checklist)
2. [Step 1: Deploy Backend (Railway)](#step-1-deploy-backend-railway)
3. [Step 2: Deploy Frontend (Vercel)](#step-2-deploy-frontend-vercel)
4. [Step 3: Configure Stripe Webhooks](#step-3-configure-stripe-webhooks)
5. [Step 4: Post-Deployment Verification](#step-4-post-deployment-verification)
6. [Troubleshooting](#troubleshooting)
7. [Production Checklist](#production-checklist)

---

## Pre-Deployment Checklist

### Required Accounts

- [ ] **GitHub Account** (to connect repositories)
- [ ] **Vercel Account** (free tier works) - https://vercel.com
- [ ] **Railway Account** (free trial, then $5/month) - https://railway.app
- [ ] **Stripe Account** (for payments) - https://stripe.com
- [ ] **Sentry Account** (optional, for error tracking) - https://sentry.io

### Required API Keys & Secrets

Generate these before starting:

```bash
# Generate secure secrets (run 2x for different keys)
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

- [ ] `SECRET_KEY` (32+ characters)
- [ ] `JWT_SECRET_KEY` (32+ characters, different from SECRET_KEY)
- [ ] Stripe Live API Keys (get from Stripe Dashboard)
- [ ] Stripe Webhook Secret (will get after creating webhook)

### Optional but Recommended

- [ ] **Polygon.io API Key** (free tier) - for stock data
- [ ] **Alpha Vantage API Key** (free tier) - for stock data
- [ ] **Resend API Key** (100 emails/day free) - for email alerts
- [ ] **Sentry DSN** (error tracking)

---

## Step 1: Deploy Backend (Railway)

### 1.1 Install Railway CLI

```bash
npm install -g @railway/cli
```

### 1.2 Login to Railway

```bash
railway login
```

### 1.3 Create New Project

```bash
# Navigate to backend directory
cd /mnt/e/projects/quant/quant/backend

# Initialize Railway project
railway init
# Name it: "quant-backend" or similar
```

### 1.4 Add PostgreSQL Database

```bash
railway add --database postgres
```

Railway will automatically:
- Create a PostgreSQL database
- Set `DATABASE_URL` environment variable

### 1.5 Add Redis (Optional but Recommended)

```bash
railway add --database redis
```

This sets `REDIS_URL` automatically.

### 1.6 Set Environment Variables

```bash
# Core Settings
railway variables set ENVIRONMENT=production
railway variables set DEBUG=false
railway variables set PROJECT_NAME="Quant Platform"
railway variables set VERSION="1.0.0"
railway variables set API_V1_STR="/api/v1"

# Security (use your generated keys)
railway variables set SECRET_KEY="YOUR_GENERATED_SECRET_KEY_HERE"
railway variables set JWT_SECRET_KEY="YOUR_GENERATED_JWT_KEY_HERE"
railway variables set ALGORITHM="HS256"
railway variables set ACCESS_TOKEN_EXPIRE_MINUTES="30"

# CORS (will update with Vercel URL later)
railway variables set BACKEND_CORS_ORIGINS='["https://your-app.vercel.app"]'

# Stripe (use test keys first, then live keys)
railway variables set STRIPE_SECRET_KEY="sk_test_your_test_key"
railway variables set STRIPE_PUBLISHABLE_KEY="pk_test_your_test_key"
# Will set STRIPE_WEBHOOK_SECRET after creating webhook

# Market Data (optional)
railway variables set POLYGON_API_KEY="your_polygon_key"
railway variables set ALPHA_VANTAGE_API_KEY="your_alpha_vantage_key"

# Monitoring (optional)
railway variables set SENTRY_DSN="your_sentry_dsn"
railway variables set SENTRY_ENVIRONMENT="production"

# Email (optional)
railway variables set RESEND_API_KEY="re_your_resend_key"
railway variables set EMAIL_FROM="noreply@yourdomain.com"

# Rate Limiting
railway variables set RATE_LIMIT_FREE="100"
railway variables set RATE_LIMIT_BASIC="1000"
railway variables set RATE_LIMIT_PREMIUM="10000"

# Security
railway variables set TRUST_PROXY_HEADERS="true"
railway variables set TRUSTED_PROXIES='["0.0.0.0/0"]'
```

### 1.7 Deploy Backend

```bash
# Deploy from backend directory
cd /mnt/e/projects/quant/quant/backend
railway up
```

### 1.8 Generate Public Domain

```bash
railway domain
# This creates a public URL like: quant-backend-production.up.railway.app
```

**Save this URL!** You'll need it for:
- Frontend API connection
- Stripe webhook configuration

### 1.9 Verify Backend Deployment

```bash
# Get your Railway URL
BACKEND_URL=$(railway domain)

# Test health endpoint
curl https://$BACKEND_URL/health

# Expected response:
# {
#   "status": "healthy",
#   "environment": "production",
#   "services": {
#     "database": "connected",
#     "cache": "connected"
#   }
# }
```

### 1.10 Run Database Migrations

```bash
# SSH into Railway container
railway run bash

# Run migrations
alembic upgrade head

# Exit
exit
```

---

## Step 2: Deploy Frontend (Vercel)

### 2.1 Install Vercel CLI

```bash
npm install -g vercel
```

### 2.2 Login to Vercel

```bash
vercel login
```

### 2.3 Configure Frontend Environment

Create `.env.production.local` in `/mnt/e/projects/quant/quant/frontend/`:

```bash
cd /mnt/e/projects/quant/quant/frontend

# Copy example file
cp .env.production.example .env.production.local

# Edit with your values
nano .env.production.local
```

**Required values:**

```bash
# Use your Railway backend URL
NEXT_PUBLIC_API_URL=https://quant-backend-production.up.railway.app
NEXT_PUBLIC_API_VERSION=v1

# Stripe publishable key (safe for client-side)
NEXT_PUBLIC_STRIPE_PUBLISHABLE_KEY=pk_test_your_test_key

# Optional: Analytics
NEXT_PUBLIC_POSTHOG_KEY=phc_your_key
NEXT_PUBLIC_GA_MEASUREMENT_ID=G-XXXXXXXXXX

# Optional: Sentry
NEXT_PUBLIC_SENTRY_DSN=https://xxx@xxx.ingest.sentry.io/xxx
```

### 2.4 Deploy to Vercel

```bash
# From frontend directory
cd /mnt/e/projects/quant/quant/frontend

# Deploy (first time - follow prompts)
vercel

# Follow the prompts:
# ? Set up and deploy "~/projects/quant/quant/frontend"? [Y/n] Y
# ? Which scope? (Your account)
# ? Link to existing project? [y/N] n
# ? What's your project's name? quant-platform
# ? In which directory is your code located? ./
# ? Want to override the settings? [y/N] n
```

### 2.5 Set Production Environment Variables in Vercel

After initial deployment, set environment variables in Vercel Dashboard:

1. Go to https://vercel.com/dashboard
2. Select your project (`quant-platform`)
3. Go to **Settings** > **Environment Variables**
4. Add these variables (for **Production** environment):

```
NEXT_PUBLIC_API_URL=https://your-railway-backend-url.up.railway.app
NEXT_PUBLIC_API_VERSION=v1
NEXT_PUBLIC_STRIPE_PUBLISHABLE_KEY=pk_test_your_test_key
NEXT_PUBLIC_ENABLE_PREMIUM=true
NEXT_PUBLIC_ENABLE_BACKTESTING=true
```

### 2.6 Deploy to Production

```bash
# Deploy to production
vercel --prod
```

### 2.7 Get Your Vercel URL

Vercel will provide a URL like:
- `https://quant-platform.vercel.app` (production)
- `https://quant-platform-git-main-yourname.vercel.app` (preview)

**Save this URL!**

### 2.8 Update Backend CORS Settings

Now update your backend to allow requests from your Vercel frontend:

```bash
# In Railway, update CORS
railway variables set BACKEND_CORS_ORIGINS='["https://quant-platform.vercel.app","https://quant-platform-git-main-yourname.vercel.app"]'

# Redeploy backend
railway up
```

---

## Step 3: Configure Stripe Webhooks

### 3.1 Create Webhook Endpoint in Stripe

1. Go to https://dashboard.stripe.com/webhooks
2. Click **Add endpoint**
3. Set **Endpoint URL**:
   ```
   https://your-railway-backend-url.up.railway.app/api/v1/subscriptions/webhooks/stripe
   ```
4. Select **Events to send**:
   - `customer.subscription.created`
   - `customer.subscription.updated`
   - `customer.subscription.deleted`
   - `invoice.payment_succeeded`
   - `invoice.payment_failed`
5. Click **Add endpoint**

### 3.2 Get Webhook Signing Secret

1. After creating the webhook, click on it
2. Click **Reveal** under **Signing secret**
3. Copy the secret (starts with `whsec_`)

### 3.3 Add Webhook Secret to Backend

```bash
# Set webhook secret in Railway
railway variables set STRIPE_WEBHOOK_SECRET="whsec_your_signing_secret_here"

# Redeploy backend
railway up
```

### 3.4 Test Webhook

1. In Stripe Dashboard, go to your webhook
2. Click **Send test webhook**
3. Select `customer.subscription.created`
4. Click **Send test webhook**
5. Check that it shows **Success** (200 OK)

---

## Step 4: Post-Deployment Verification

### 4.1 Test Frontend

```bash
# Visit your Vercel URL
open https://quant-platform.vercel.app

# Check:
# - [ ] Homepage loads
# - [ ] Login/Signup works
# - [ ] API calls to backend work (check Network tab)
# - [ ] No CORS errors in console
```

### 4.2 Test Backend API

```bash
BACKEND_URL="https://your-railway-url.up.railway.app"

# Test health
curl $BACKEND_URL/health

# Test API docs
open $BACKEND_URL/api/v1/docs
```

### 4.3 Test Stripe Integration

1. Go to your frontend: `https://your-app.vercel.app/pricing`
2. Click **Subscribe** on a plan
3. Use Stripe test card: `4242 4242 4242 4242`
4. Check:
   - [ ] Checkout session created
   - [ ] Redirected to Stripe checkout
   - [ ] After payment, redirected back to app
   - [ ] Subscription activated in your app
   - [ ] Webhook received in Stripe Dashboard

### 4.4 Test Backtesting (if enabled)

1. Go to `/backtest/new`
2. Enter a stock symbol (e.g., `AAPL`)
3. Select a strategy (e.g., `MA Crossover`)
4. Run backtest
5. Check results page loads with:
   - [ ] Performance metrics
   - [ ] Equity curve chart
   - [ ] Trade list

### 4.5 Monitor Errors

Check Sentry (if configured):
- https://sentry.io/organizations/your-org/issues/

Check Railway logs:
```bash
railway logs
```

Check Vercel logs:
- https://vercel.com/yourname/quant-platform/deployments

---

## Production Checklist

### Security

- [ ] All secrets use environment variables (not hardcoded)
- [ ] `SECRET_KEY` and `JWT_SECRET_KEY` are strong (32+ chars)
- [ ] CORS configured correctly (only your Vercel domain)
- [ ] Stripe webhook secret configured
- [ ] HTTPS enabled (automatic on Vercel/Railway)
- [ ] Security headers configured (in `vercel.json` and `next.config.js`)
- [ ] Rate limiting enabled in backend

### Monitoring

- [ ] Sentry configured for error tracking
- [ ] Railway logs monitored
- [ ] Vercel logs monitored
- [ ] Health check endpoint working (`/health`)
- [ ] Stripe webhook events logging correctly

### Performance

- [ ] Redis caching enabled
- [ ] Database connection pooling configured
- [ ] Static assets cached (Vercel CDN)
- [ ] Image optimization enabled (Next.js)
- [ ] API response times < 500ms

### Payments

- [ ] Stripe products created in Dashboard
- [ ] Stripe prices configured (monthly/yearly)
- [ ] Webhook endpoint verified
- [ ] Test payment completed successfully
- [ ] Subscription tier enforcement working
- [ ] Invoice emails sent (configure in Stripe)

### Data & Backups

- [ ] Database backups enabled (Railway auto-backups)
- [ ] Migration scripts ready
- [ ] Seed data loaded (if needed)
- [ ] Data retention policy defined

### Frontend

- [ ] Environment variables set in Vercel
- [ ] Build succeeds without errors
- [ ] All pages render correctly
- [ ] Mobile responsive
- [ ] SEO meta tags configured
- [ ] Analytics tracking working

### Backend

- [ ] Environment variables set in Railway
- [ ] Database migrations run
- [ ] Health check returns 200
- [ ] API documentation accessible (`/api/v1/docs`)
- [ ] Background tasks running (Celery, if configured)

---

## Troubleshooting

### Frontend can't connect to Backend (CORS errors)

**Problem:** Browser console shows CORS errors.

**Solution:**
```bash
# Update backend CORS settings
railway variables set BACKEND_CORS_ORIGINS='["https://your-vercel-url.vercel.app"]'
railway up
```

### Stripe webhook not working

**Problem:** Webhook shows failed events in Stripe Dashboard.

**Checklist:**
1. Verify webhook URL is correct: `https://backend-url/api/v1/subscriptions/webhooks/stripe`
2. Check `STRIPE_WEBHOOK_SECRET` is set in Railway
3. Check Railway logs for errors: `railway logs`
4. Verify backend is accessible: `curl https://backend-url/health`

### Database connection errors

**Problem:** Backend shows database connection errors.

**Solution:**
```bash
# Check DATABASE_URL is set
railway variables

# If using Railway Postgres, it should be auto-set
# If using external DB, set manually:
railway variables set DATABASE_URL="postgresql+asyncpg://user:pass@host:5432/db"
```

### Build failures on Vercel

**Problem:** Vercel deployment fails during build.

**Solutions:**
1. Check build logs in Vercel Dashboard
2. Verify `package.json` has correct scripts:
   ```json
   {
     "scripts": {
       "build": "next build",
       "start": "next start"
     }
   }
   ```
3. Check TypeScript errors: `npm run type-check`
4. Clear Vercel cache: Redeploy with **Clear Cache** option

### API requests timing out

**Problem:** Frontend requests to backend timeout.

**Checklist:**
1. Check backend is running: `curl https://backend-url/health`
2. Check Railway logs: `railway logs`
3. Increase timeout in frontend API client (default: 30s)
4. Check database connection pool settings

---

## Updating Your Deployment

### Update Frontend

```bash
cd /mnt/e/projects/quant/quant/frontend

# Make your changes, then:
git add .
git commit -m "Update frontend"
git push

# Vercel auto-deploys on git push (if connected to GitHub)
# OR deploy manually:
vercel --prod
```

### Update Backend

```bash
cd /mnt/e/projects/quant/quant/backend

# Make your changes, then:
railway up

# OR connect to GitHub for auto-deploys
```

### Database Migrations

```bash
# Create migration
alembic revision --autogenerate -m "description"

# Apply to production
railway run alembic upgrade head
```

---

## Cost Estimate

### Free Tier (Starting Out)

- **Vercel**: Free (100GB bandwidth, unlimited deployments)
- **Railway**: Free trial ($5 credit), then ~$5-10/month
- **Supabase** (optional): Free (500MB database, 2GB bandwidth)
- **Upstash Redis** (optional): Free (10k commands/day)
- **Resend Email**: Free (100 emails/day)
- **Sentry**: Free (5k events/month)

**Total:** $0/month (trial), then $5-10/month

### Growth Stage (100-1000 users)

- **Vercel**: Free or Pro $20/month (if you need more)
- **Railway**: ~$20-50/month (depends on usage)
- **Supabase**: Free or Pro $25/month
- **Stripe**: 2.9% + $0.30 per transaction
- **Email**: $10-20/month (for more emails)

**Total:** $30-100/month + payment processing fees

---

## Getting Help

### Railway Support
- Dashboard: https://railway.app/dashboard
- Docs: https://docs.railway.app
- Discord: https://discord.gg/railway

### Vercel Support
- Dashboard: https://vercel.com/dashboard
- Docs: https://vercel.com/docs
- Discord: https://vercel.com/discord

### Stripe Support
- Dashboard: https://dashboard.stripe.com
- Docs: https://stripe.com/docs
- Support: https://support.stripe.com

---

## Next Steps After Deployment

1. **Test Everything** - Run through all user flows
2. **Set Up Monitoring** - Configure Sentry, set up alerts
3. **Configure DNS** - Point your domain to Vercel (optional)
4. **Switch to Live Stripe Keys** - When ready for real payments
5. **Marketing** - Share your platform!
6. **Monitor Performance** - Check Railway/Vercel metrics
7. **Iterate** - Deploy updates based on user feedback

---

## Production-Ready Checklist

Before announcing your platform:

- [ ] All environment variables configured correctly
- [ ] Test payment flow completed successfully
- [ ] Stripe webhook verified
- [ ] Error monitoring configured (Sentry)
- [ ] Database backups enabled
- [ ] Security headers in place
- [ ] CORS configured correctly
- [ ] Rate limiting enabled
- [ ] Health checks passing
- [ ] Test user accounts created
- [ ] Terms of Service & Privacy Policy pages
- [ ] Support email configured
- [ ] Analytics tracking working

---

**Your Quant Platform is now live and revenue-ready!** 🚀

**Frontend:** `https://your-app.vercel.app`
**Backend:** `https://your-backend.railway.app`
**API Docs:** `https://your-backend.railway.app/api/v1/docs`
