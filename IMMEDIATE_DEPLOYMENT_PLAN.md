# IMMEDIATE DEPLOYMENT PLAN - Congressional Trading Analytics Platform
**Date Created:** February 14, 2026
**Estimated Time to Live:** 30-45 minutes
**Revenue Potential:** $1,450-$9,900 MRR

---

## PLATFORM STATUS: ✅ 100% PRODUCTION READY

Verification Complete: All checks passed ✓
- 10 database migrations ready
- Stripe webhook security verified
- Security headers configured
- Rate limiting implemented
- CORS properly configured
- All dependencies installed

---

## DEPLOYMENT CHECKLIST

### Prerequisites (5 minutes)
- [ ] Generate 2 secret keys: `python -c "import secrets; print(secrets.token_urlsafe(32))"`
- [ ] Create Railway account: https://railway.app
- [ ] Create Vercel account: https://vercel.com
- [ ] Get Stripe test keys: https://dashboard.stripe.com/test/apikeys
- [ ] Install Railway CLI: `npm install -g @railway/cli`
- [ ] Install Vercel CLI: `npm install -g vercel`

### STEP 1: Deploy Backend to Railway (15 minutes)

```bash
# Navigate to backend
cd /mnt/e/projects/quant/quant/backend

# Login to Railway
railway login

# Initialize project
railway init
# Name it: "quant-congressional-backend"

# Add databases
railway add --database postgres
railway add --database redis

# Set environment variables (replace YOUR_* with actual values)
railway variables set \
  ENVIRONMENT=production \
  DEBUG=false \
  PROJECT_NAME="Congressional Trading Analytics" \
  API_V1_STR="/api/v1" \
  SECRET_KEY="YOUR_FIRST_SECRET_KEY_HERE" \
  JWT_SECRET_KEY="YOUR_SECOND_SECRET_KEY_HERE" \
  ALGORITHM="HS256" \
  STRIPE_SECRET_KEY="sk_test_YOUR_STRIPE_SECRET" \
  STRIPE_PUBLISHABLE_KEY="pk_test_YOUR_STRIPE_PUBLISHABLE" \
  BACKEND_CORS_ORIGINS='["http://localhost:3000"]' \
  TRUST_PROXY_HEADERS="true" \
  ACCESS_TOKEN_EXPIRE_MINUTES="30" \
  REFRESH_TOKEN_EXPIRE_DAYS="7"

# Deploy backend
railway up

# Generate and save domain
railway domain
# SAVE THIS URL! Example: https://quant-congressional-backend-production-xxxx.up.railway.app

# Run database migrations
railway run bash
alembic upgrade head
exit

# Test backend health
curl https://YOUR-RAILWAY-URL.up.railway.app/health
# Expected: {"status":"healthy","services":{"database":"connected","cache":"connected"}}
```

**Backend URL:** `_________________________________` (write it here!)

### STEP 2: Deploy Frontend to Vercel (10 minutes)

```bash
# Navigate to frontend
cd /mnt/e/projects/quant/quant/frontend

# Create production environment file
cat > .env.production.local << EOF
NEXT_PUBLIC_API_URL=https://YOUR-RAILWAY-URL.up.railway.app
NEXT_PUBLIC_STRIPE_PUBLISHABLE_KEY=pk_test_YOUR_STRIPE_KEY
NODE_ENV=production
EOF

# Login to Vercel
vercel login

# Deploy to production
vercel --prod

# SAVE THE URL! Example: https://quant-analytics-xxxx.vercel.app
```

**Frontend URL:** `_________________________________` (write it here!)

**IMPORTANT:** Also set environment variables in Vercel dashboard:
1. Go to https://vercel.com/dashboard
2. Select your project
3. Settings > Environment Variables > Production
4. Add:
   - `NEXT_PUBLIC_API_URL` = Your Railway URL
   - `NEXT_PUBLIC_STRIPE_PUBLISHABLE_KEY` = Your Stripe key

### STEP 3: Update CORS (2 minutes)

```bash
cd /mnt/e/projects/quant/quant/backend

# Update CORS with your Vercel URL
railway variables set BACKEND_CORS_ORIGINS='["https://YOUR-VERCEL-URL.vercel.app"]'

# Redeploy
railway up
```

### STEP 4: Configure Stripe Webhooks (5 minutes)

1. Go to https://dashboard.stripe.com/test/webhooks
2. Click **"Add endpoint"**
3. Enter endpoint URL:
   ```
   https://YOUR-RAILWAY-URL.up.railway.app/api/v1/subscriptions/webhooks/stripe
   ```
4. Select events to listen for:
   - `customer.subscription.created`
   - `customer.subscription.updated`
   - `customer.subscription.deleted`
   - `invoice.payment_succeeded`
   - `invoice.payment_failed`
5. Click **"Add endpoint"**
6. Click endpoint to view signing secret (starts with `whsec_`)
7. Add to Railway:
   ```bash
   railway variables set STRIPE_WEBHOOK_SECRET="whsec_YOUR_SECRET"
   railway up
   ```

### STEP 5: Test Everything (5 minutes)

**Backend Test:**
```bash
# Health check
curl https://YOUR-RAILWAY-URL.up.railway.app/health

# API docs
open https://YOUR-RAILWAY-URL.up.railway.app/api/v1/docs
```

**Frontend Test:**
1. Visit `https://YOUR-VERCEL-URL.vercel.app`
2. Check browser console for errors
3. Sign up for test account
4. Navigate to pricing page
5. Click subscribe to Premium plan
6. Use test card: `4242 4242 4242 4242`, any future date, any CVC
7. Complete checkout
8. Verify subscription activated

**Stripe Webhook Test:**
1. Go to Stripe Dashboard > Webhooks
2. Click your webhook
3. Click "Send test webhook"
4. Select `customer.subscription.created`
5. Verify response shows **Success (200)**

---

## PRICING TIERS (Ready to Go)

### Free Tier
- Last 30 days of trades
- Basic trade filtering
- 100 API calls/month
- Email support

### Premium - $29/month
- Full historical data (2012+)
- Advanced ML predictions
- Real-time alerts (email)
- Portfolio tracking
- 10,000 API calls/month
- Priority email support

### Professional - $99/month
- Everything in Premium
- API access with webhooks
- Custom watchlists (unlimited)
- Advanced analytics
- Backtesting framework
- 100,000 API calls/month
- Priority support + Slack

### Enterprise - Custom
- Dedicated infrastructure
- White-label options
- Custom integrations
- Unlimited API calls
- SLA guarantee
- Dedicated account manager

---

## REVENUE PROJECTIONS

### Conservative (Month 3)
- 500 free users
- 50 Premium ($29) = $1,450/mo
- 5 Professional ($99) = $495/mo
- **Total MRR: $1,945**

### Moderate (Month 6)
- 2,000 free users
- 200 Premium ($29) = $5,800/mo
- 20 Professional ($99) = $1,980/mo
- 2 Enterprise ($500) = $1,000/mo
- **Total MRR: $8,780**

### Optimistic (Month 12)
- 10,000 free users
- 500 Premium ($29) = $14,500/mo
- 100 Professional ($99) = $9,900/mo
- 10 Enterprise ($500) = $5,000/mo
- **Total MRR: $29,400**

---

## LAUNCH SEQUENCE (Next 7 Days)

### Day 1 (Today): Deploy
- [ ] Complete deployment steps above
- [ ] Test all functionality
- [ ] Invite 5 friends to beta test
- [ ] Monitor logs for errors

### Day 2: Product Hunt Launch
- [ ] Submit to Product Hunt (12:01 AM PST Tuesday)
- [ ] Rally support from network
- [ ] Respond to every comment
- [ ] Share on Twitter/LinkedIn
- **Goal:** Top 5 product of the day, 200+ upvotes

### Day 3: Reddit + Social
- [ ] Post in r/wallstreetbets, r/stocks, r/investing
- [ ] Share interesting data findings (not promotional)
- [ ] Engage in comments
- **Goal:** 2,000+ visitors from Reddit

### Day 4: Hacker News
- [ ] Submit "Show HN" post
- [ ] Focus on technical implementation
- [ ] Engage in technical discussions
- **Goal:** Front page, 1,000+ visitors

### Day 5-7: Press & Influencer
- [ ] Email financial journalists
- [ ] Reach out to finance influencers
- [ ] Guest post on finance blogs
- [ ] Share first user success story
- **Goal:** 3+ media mentions, 5+ influencer shares

---

## MARKETING MATERIALS (Ready to Use)

Located in `/mnt/e/projects/quant/marketing/`:
- ✅ Landing page copy
- ✅ Email sequences (5 emails)
- ✅ Social media content (50+ posts)
- ✅ Pricing page copy
- ✅ Press kit
- ✅ Launch announcement
- ✅ Partner outreach templates

---

## MONITORING & METRICS

### Daily Monitoring (First Week)
```bash
# Check Railway logs
railway logs

# Check Vercel deployment
vercel logs

# Check Stripe dashboard
open https://dashboard.stripe.com/test/events
```

### Key Metrics to Track
- **Signups:** Target 50/day after launch week
- **Conversion rate:** 5-10% free to premium
- **Churn:** <5% monthly
- **API usage:** Growing 20%+ monthly
- **Support tickets:** <10/week

---

## SWITCHING TO LIVE STRIPE KEYS (After Testing)

**Only after thoroughly testing with test keys!**

1. Get live keys from https://dashboard.stripe.com/apikeys
2. Update Railway:
   ```bash
   railway variables set \
     STRIPE_SECRET_KEY="sk_live_YOUR_LIVE_KEY" \
     STRIPE_PUBLISHABLE_KEY="pk_live_YOUR_LIVE_KEY"
   railway up
   ```
3. Update Vercel (Dashboard > Environment Variables):
   - Update `NEXT_PUBLIC_STRIPE_PUBLISHABLE_KEY` to live key
   - Redeploy
4. Create live webhook in Stripe (same process as test)
5. Update `STRIPE_WEBHOOK_SECRET` in Railway

---

## TROUBLESHOOTING

### CORS Errors in Frontend
```bash
railway variables set BACKEND_CORS_ORIGINS='["https://your-vercel-url.vercel.app"]'
railway up
```

### Webhook Not Working
1. Check URL is correct: `https://YOUR-RAILWAY-URL.up.railway.app/api/v1/subscriptions/webhooks/stripe`
2. Verify webhook secret in Railway: `railway variables`
3. Check Railway logs: `railway logs`
4. Test webhook in Stripe Dashboard

### Database Connection Issues
```bash
# Check database status
railway run bash
alembic current
exit
```

### Build Failures
- Check Vercel deployment logs in dashboard
- Verify all environment variables are set
- Clear Vercel cache: Settings > Data Cache > Clear

---

## COSTS

### Monthly Hosting Costs

**Month 1 (Low Traffic):**
- Railway: $5-10
- Vercel: $0 (free tier)
- **Total: $5-10/month**

**Month 3 (500 users):**
- Railway: $15-20
- Vercel: $0-20
- **Total: $15-40/month**

**Month 6 (2,000 users):**
- Railway: $30-50
- Vercel: $20
- **Total: $50-70/month**

**Break-even:** ~15-20 Premium subscribers

---

## SUCCESS CRITERIA

### Week 1
- ✅ Platform deployed successfully
- ✅ 100+ signups
- ✅ 5+ premium trials
- ✅ No critical bugs
- ✅ Product Hunt top 10

### Month 1
- ✅ 500+ signups
- ✅ 25+ paying customers
- ✅ $750+ MRR
- ✅ 3+ press mentions

### Month 3
- ✅ 2,000+ signups
- ✅ 100+ paying customers
- ✅ $3,000+ MRR
- ✅ Break-even or profitable

---

## IMMEDIATE NEXT STEPS

1. **RIGHT NOW:** Generate secret keys
2. **Next 15 min:** Deploy backend to Railway
3. **Next 10 min:** Deploy frontend to Vercel
4. **Next 5 min:** Configure Stripe webhooks
5. **Next 5 min:** Test everything end-to-end
6. **Tomorrow:** Product Hunt launch
7. **This week:** Social media + press push

---

## SUPPORT RESOURCES

- **Deployment Guide:** `/mnt/e/projects/quant/DEPLOYMENT_QUICK_START.md`
- **Checklist:** `/mnt/e/projects/quant/DEPLOYMENT_CHECKLIST.md`
- **Marketing Materials:** `/mnt/e/projects/quant/marketing/`
- **Railway Docs:** https://docs.railway.app
- **Vercel Docs:** https://vercel.com/docs
- **Stripe Webhooks:** https://stripe.com/docs/webhooks

---

## DEPLOYMENT COMPLETED ✓

**Backend URL:** `_________________________________`
**Frontend URL:** `_________________________________`
**Deployment Date:** `_________________________________`
**First Payment Date:** `_________________________________`

---

**THIS PLATFORM IS 100% READY TO GENERATE REVENUE**

Time to deploy: 30-45 minutes
Time to first customer: 1-7 days
Time to profitability: 30-60 days

**LET'S GO! 🚀**
