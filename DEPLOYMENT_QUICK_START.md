# Quick Start: Deploy to Vercel in 30 Minutes

**Goal**: Get your Quant platform live and accepting payments ASAP.

---

## Prerequisites (5 minutes)

1. **GitHub account** - Push your code to GitHub first
2. **Stripe account** - Get test API keys: https://dashboard.stripe.com/test/apikeys
3. **Generate secrets**:
   ```bash
   python -c "import secrets; print(secrets.token_urlsafe(32))"  # Run 2x
   ```
   Save both keys somewhere safe!

---

## Step 1: Deploy Backend to Railway (10 minutes)

### Install & Login
```bash
npm install -g @railway/cli
railway login
```

### Create & Deploy
```bash
cd /mnt/e/projects/quant/quant/backend
railway init  # Name: "quant-backend"
railway add --database postgres
railway add --database redis
```

### Set Environment Variables
```bash
railway variables set ENVIRONMENT=production \
  DEBUG=false \
  SECRET_KEY="YOUR_FIRST_GENERATED_KEY" \
  JWT_SECRET_KEY="YOUR_SECOND_GENERATED_KEY" \
  STRIPE_SECRET_KEY="sk_test_YOUR_STRIPE_SECRET_KEY" \
  STRIPE_PUBLISHABLE_KEY="pk_test_YOUR_STRIPE_PUBLISHABLE_KEY" \
  BACKEND_CORS_ORIGINS='["http://localhost:3000"]' \
  TRUST_PROXY_HEADERS="true"
```

### Deploy
```bash
railway up
railway domain  # Copy this URL!
```

### Run Migrations
```bash
railway run bash
alembic upgrade head
exit
```

**✓ Backend URL:** `https://quant-backend-production-xxxx.up.railway.app`

---

## Step 2: Deploy Frontend to Vercel (10 minutes)

### Install & Login
```bash
npm install -g vercel
vercel login
```

### Configure
```bash
cd /mnt/e/projects/quant/quant/frontend
cp .env.production.example .env.production.local
```

Edit `.env.production.local`:
```bash
NEXT_PUBLIC_API_URL=https://YOUR-RAILWAY-URL.up.railway.app
NEXT_PUBLIC_STRIPE_PUBLISHABLE_KEY=pk_test_YOUR_KEY
```

### Deploy
```bash
vercel --prod
```

**✓ Frontend URL:** `https://quant-platform-xxxx.vercel.app`

### Update CORS in Backend
```bash
cd /mnt/e/projects/quant/quant/backend
railway variables set BACKEND_CORS_ORIGINS='["https://YOUR-VERCEL-URL.vercel.app"]'
railway up
```

---

## Step 3: Configure Stripe Webhook (5 minutes)

1. **Go to Stripe:** https://dashboard.stripe.com/test/webhooks
2. **Click "Add endpoint"**
3. **Enter URL:** `https://YOUR-RAILWAY-URL.up.railway.app/api/v1/subscriptions/webhooks/stripe`
4. **Select events:**
   - `customer.subscription.created`
   - `customer.subscription.updated`
   - `customer.subscription.deleted`
   - `invoice.payment_succeeded`
   - `invoice.payment_failed`
5. **Click "Add endpoint"**
6. **Copy webhook secret** (starts with `whsec_`)
7. **Add to Railway:**
   ```bash
   railway variables set STRIPE_WEBHOOK_SECRET="whsec_YOUR_SECRET"
   railway up
   ```

---

## Step 4: Test Everything (5 minutes)

### Test Backend
```bash
curl https://YOUR-RAILWAY-URL.up.railway.app/health
```

Should return:
```json
{
  "status": "healthy",
  "services": {
    "database": "connected",
    "cache": "connected"
  }
}
```

### Test Frontend
1. Visit: `https://YOUR-VERCEL-URL.vercel.app`
2. Sign up for an account
3. Go to pricing page
4. Click subscribe on a plan
5. Use test card: `4242 4242 4242 4242`
6. Complete checkout
7. Verify subscription activated

### Test Webhook
In Stripe Dashboard:
1. Go to Webhooks
2. Click your webhook
3. Click "Send test webhook"
4. Select `customer.subscription.created`
5. Verify response is **Success (200)**

---

## You're Live! 🎉

**Your URLs:**
- **Frontend:** `https://your-app.vercel.app`
- **Backend:** `https://your-backend.railway.app`
- **API Docs:** `https://your-backend.railway.app/api/v1/docs`

---

## Next Steps

### Switch to Live Stripe Keys (when ready)

1. Get live keys from https://dashboard.stripe.com/apikeys
2. Update Railway:
   ```bash
   railway variables set STRIPE_SECRET_KEY="sk_live_YOUR_LIVE_KEY"
   railway variables set STRIPE_PUBLISHABLE_KEY="pk_live_YOUR_LIVE_KEY"
   railway up
   ```
3. Update Vercel:
   - Dashboard > Project > Settings > Environment Variables
   - Update `NEXT_PUBLIC_STRIPE_PUBLISHABLE_KEY` to live key
   - Redeploy
4. Create live webhook in Stripe (same process as test)

### Monitoring

- **Railway Logs:** `railway logs`
- **Vercel Logs:** https://vercel.com/dashboard
- **Stripe Events:** https://dashboard.stripe.com/events

### Optional Enhancements

- **Custom Domain:** Add in Vercel Settings
- **Error Tracking:** Add Sentry DSN to environment variables
- **Analytics:** Add PostHog or Google Analytics keys
- **Email Alerts:** Add Resend API key

---

## Costs

- **Vercel:** Free (hobby tier)
- **Railway:** ~$5-20/month (based on usage)
- **Stripe:** 2.9% + $0.30 per transaction
- **Total:** ~$5-20/month until you get revenue

---

## Troubleshooting

### CORS Errors
```bash
railway variables set BACKEND_CORS_ORIGINS='["https://your-vercel-url.vercel.app"]'
railway up
```

### Webhook Not Working
- Check webhook URL is correct
- Verify webhook secret in Railway
- Check Railway logs: `railway logs`

### Build Failures
- Check Vercel deployment logs
- Verify environment variables are set
- Try clearing cache and redeploying

---

## Support

- **Full Guide:** See [VERCEL_DEPLOYMENT_GUIDE.md](VERCEL_DEPLOYMENT_GUIDE.md)
- **Checklist:** See [DEPLOYMENT_CHECKLIST.md](DEPLOYMENT_CHECKLIST.md)
- **Railway Docs:** https://docs.railway.app
- **Vercel Docs:** https://vercel.com/docs
- **Stripe Docs:** https://stripe.com/docs

---

**Total Time:** ~30 minutes
**Your platform is now live and ready to generate revenue!** 🚀
