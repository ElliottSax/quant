# ⚡ Quick Activation Guide - Revenue Features

**Time to activate**: ~1 hour (excluding Stripe approvals)

---

## Step 1: Environment Variables (5 min)

Add to your `.env` file:

```bash
# Stripe Integration
STRIPE_SECRET_KEY=sk_test_xxxxx  # Get from https://dashboard.stripe.com
STRIPE_PUBLISHABLE_KEY=pk_test_xxxxx
STRIPE_PREMIUM_PRICE_ID=price_xxxxx  # Create in Stripe Dashboard ($29/mo)
STRIPE_ENTERPRISE_PRICE_ID=price_xxxxx  # Create in Stripe Dashboard

# Affiliate Links
AFFILIATE_IB_URL=https://www.interactivebrokers.com?ref=quant
AFFILIATE_TASTYTRADE_URL=https://www.tastytrade.com?ref=quant
AFFILIATE_TDA_URL=https://www.tdameritrade.com?ref=quant
AFFILIATE_SCHWAB_URL=https://www.schwab.com?ref=quant
AFFILIATE_FIDELITY_URL=https://www.fidelity.com?ref=quant
AFFILIATE_WEBULL_URL=https://www.webull.com?ref=quant
```

---

## Step 2: Database Migration (10 min)

```bash
cd quant/backend

# Apply migration (adds subscription fields to users table)
alembic upgrade head

# Or if using SQLite directly:
# The subscription fields are already in the User model via SQLAlchemy
```

---

## Step 3: Test Locally (15 min)

```bash
# Terminal 1: Start backend
cd quant/backend
python -m uvicorn app.main:app --reload

# Terminal 2: Test subscription endpoint
curl -X GET http://localhost:8000/api/v1/subscription/tiers

# Terminal 3: Test affiliate endpoint
curl -X GET http://localhost:8000/api/v1/affiliate/brokers/recommendations?strategy=trend

# Terminal 4: Start frontend
cd quant/frontend
npm run dev

# Visit: http://localhost:3000/pricing
```

---

## Step 4: Stripe Setup (20 min)

### Create Price IDs

1. Go to https://dashboard.stripe.com/products
2. Click "Create product"
3. Name: "Quant Premium"
   - Price: $29.00 USD
   - Recurring: Monthly
   - Copy **Price ID** → `STRIPE_PREMIUM_PRICE_ID`

4. Create another product: "Quant Enterprise"
   - Price: $99.00 USD (or create custom pricing)
   - Copy **Price ID** → `STRIPE_ENTERPRISE_PRICE_ID`

### Setup Webhooks (for production)

1. https://dashboard.stripe.com/webhooks
2. Click "Add endpoint"
3. URL: `https://yourapi.com/api/v1/webhooks/stripe`
4. Events: `customer.subscription.updated`, `customer.subscription.deleted`
5. Copy **Signing secret** → Add to `.env` as `STRIPE_WEBHOOK_SECRET`

---

## Step 5: Deploy (20 min)

```bash
# Commit changes
git add -A
git commit -m "feat: Add subscription system, affiliate integration, premium features

- Freemium tiers: Free/Premium ($29/mo)/Enterprise
- 8 affiliate brokers integrated ($40-75 per referral)
- Usage tracking and quota enforcement
- Premium feature upsell components
- Pricing page with feature comparison

This unlocks $123K+ annual revenue potential from 1,000 users."

# Push to GitHub
git push origin main

# Deploy to Railway (backend)
railway up

# Deploy to Vercel (frontend)
vercel --prod

# Or use the one-click deploy:
# Backend: https://railway.app/new?template=https://github.com/yourusername/quant
# Frontend: https://vercel.com/new/clone?repository-url=https://github.com/yourusername/quant&root-directory=quant/frontend
```

---

## Step 6: Verification (10 min)

### Backend Health Checks

```bash
# Test subscription tiers endpoint
curl -X GET https://your-api.railway.app/api/v1/subscription/tiers

# Test affiliate brokers
curl -X GET "https://your-api.railway.app/api/v1/affiliate/brokers/recommendations?strategy=trend"

# Check pricing is live
curl -X GET https://your-frontend.vercel.app/pricing
```

### Frontend Verification

1. Visit https://your-frontend.vercel.app/pricing
   - ✅ Should see 3 pricing tiers
   - ✅ Billing cycle toggle works
   - ✅ Feature comparison table visible
   - ✅ Free trial banner at top

2. Visit /backtesting/builder
   - ✅ Run a backtest
   - ✅ Check that results show broker recommendations
   - ✅ Broker cards should be clickable

---

## Step 7: Monitor & Optimize (Ongoing)

### Key Metrics to Watch

```bash
# Daily Active Users
SELECT COUNT(DISTINCT user_id) FROM backtest_results
WHERE created_at > NOW() - INTERVAL '1 day'

# Subscription Conversions
SELECT
  subscription_tier,
  COUNT(*) as count,
  ROUND(100.0 * COUNT(*) / SUM(COUNT(*)) OVER (), 1) as pct
FROM users
GROUP BY subscription_tier

# Affiliate Clicks
SELECT
  broker,
  COUNT(*) as clicks,
  COUNT(DISTINCT user_id) as unique_users
FROM affiliate_clicks
GROUP BY broker
```

### Setup Monitoring

```bash
# Watch Stripe events in real-time
stripe listen --forward-to localhost:8000/api/v1/webhooks/stripe

# Monitor affiliate conversions
# → Add analytics to track which brokers convert best

# A/B test pricing
# → Try different prices ($19, $29, $39) and measure conversion
```

---

## Step 8: Marketing Activation (1 hour)

### Email Campaign
```
Subject: "Try Premium Free for 7 Days"
Body: "
Your favorite backtesting platform just got better!

New Premium Features:
✓ 50+ backtests/month (vs 5 free)
✓ All professional strategies unlocked
✓ Advanced portfolio optimization
✓ Email alerts & notifications

👉 Start your 7-day free trial: [CTA Button]
"
```

### Social Posts
```
"🎉 Just launched Premium tier!

✅ $29/month for unlimited backtesting
✅ $0/month free tier for learning
✅ 7-day trial = no credit card needed

Plus: We partnered with 8 major brokers
Open an account through us → we get $50 commission
(You get nothing extra, but you're supporting our platform!)

[Link to Pricing Page]
"
```

### Blog Post
```
Title: "Introducing Quant Premium - Unlock Professional Backtesting"

Outline:
1. What changed
2. Feature comparison (Free vs Premium vs Enterprise)
3. Who should upgrade
4. How to start free trial
5. FAQ about pricing
6. Testimonials (or get some!)
```

---

## Revenue Activation Timeline

| Time | Action | Impact |
|------|--------|--------|
| Day 1 | Deploy code | Features live |
| Day 2 | Email free users | 5-10% trial conversions |
| Day 3 | Social announcement | 20-50 new trials |
| Day 7 | First trial conversions | $0-50 MRR |
| Week 2 | Affiliate conversions | First $500-1000 |
| Month 1 | Stabilize | $1-5K MRR |
| Month 3 | Optimize | $5-10K MRR |

---

## Troubleshooting

### "Stripe API key invalid"
```bash
# Check env var is set correctly
echo $STRIPE_SECRET_KEY

# Make sure it starts with: sk_test_ or sk_live_
```

### "Broker recommendations not showing"
```bash
# Check API endpoint works
curl -X GET "http://localhost:8000/api/v1/affiliate/brokers/recommendations?strategy=trend"

# Check frontend network tab for 200 response
```

### "Subscription quota not enforcing"
```bash
# Check backtest endpoint has quota middleware
# Look for: check_backtest_quota in backtesting.py

# Test quota:
1. Run 6 backtests on free tier
2. 6th should fail with 429 (Too Many Requests)
```

### "Trial not starting"
```bash
# Check user has trial_used=False
SELECT email, trial_used, subscription_tier FROM users WHERE email='test@example.com'

# If trial_used=True, can't start trial again
# This is by design (one trial per account)
```

---

## Success Metrics (First Month)

✅ **Goal**: 10-20 new premium subscriptions
- 10 × $29 × 30 days = **$8,700 MRR potential**

✅ **Goal**: 50+ affiliate referral signups
- 50 × $50 avg commission = **$2,500 one-time**

✅ **Goal**: <1 day to deploy + activate
- Setup Stripe: 20 min
- Deploy: 20 min
- Test: 15 min
- Marketing: 1 hour

---

## What's Next?

1. **Week 1**: Get first 5 paid customers
2. **Week 2**: Optimize pricing page (A/B test)
3. **Week 3**: Add email alerts (premium feature)
4. **Week 4**: Launch affiliate program (brokers promote us)
5. **Month 2**: Scale to $5K MRR
6. **Month 3**: Add more brokers and payment methods

---

## Support & Questions

- **Stripe docs**: https://stripe.com/docs
- **Quant API docs**: http://localhost:8000/docs
- **GitHub issues**: github.com/yourrepo/quant/issues

---

**You're now a SaaS! 🎉**

Revenue features are ready to launch. Deploy today, optimize for next month.

Good luck! 🚀
