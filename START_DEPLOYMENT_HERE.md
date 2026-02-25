# 🚀 START HERE: Deploy Quant Platform

**Time:** 30 minutes | **Cost:** $5-10/month | **Revenue Potential:** $1-10k/month

---

## ✅ Pre-Flight Check

Run this first:
```bash
/mnt/e/projects/quant/scripts/verify_production_ready.sh
```

**Expected:** ✅ PERFECT! No errors or warnings.

---

## 📋 What You Need

### Accounts (Free to Create)
- [ ] Railway - https://railway.app
- [ ] Vercel - https://vercel.com
- [ ] Stripe - https://stripe.com

### Secrets (Generate Now)
```bash
# Run this twice, save both outputs
python -c "import secrets; print(secrets.token_urlsafe(32))"
```
- Save first as: `SECRET_KEY`
- Save second as: `JWT_SECRET_KEY`

### Stripe Keys
- Go to: https://dashboard.stripe.com/test/apikeys
- Copy: Secret Key (`sk_test_...`)
- Copy: Publishable Key (`pk_test_...`)

---

## 🎯 Choose Your Path

### Fast Track (30 minutes)
```bash
# Read this file:
/mnt/e/projects/quant/DEPLOYMENT_QUICK_START.md
```
Copy-paste commands, minimal explanation.

### Detailed Guide (45 minutes)
```bash
# Read this file:
/mnt/e/projects/quant/DEPLOYMENT_CHECKLIST.md
```
Step-by-step with verification at each stage.

### Complete Reference (1-2 hours)
```bash
# Read this file:
/mnt/e/projects/quant/VERCEL_DEPLOYMENT_GUIDE.md
```
Full explanations, troubleshooting, architecture.

---

## ⚡ Quick Start (Copy-Paste)

### 1. Backend (Railway) - 15 min

```bash
# Install & login
npm install -g @railway/cli
railway login

# Create project
cd /mnt/e/projects/quant/quant/backend
railway init  # Name: quant-backend
railway add --database postgres
railway add --database redis

# Set variables (replace YOUR_* with actual values)
railway variables set \
  ENVIRONMENT=production \
  DEBUG=false \
  SECRET_KEY="YOUR_FIRST_GENERATED_KEY" \
  JWT_SECRET_KEY="YOUR_SECOND_GENERATED_KEY" \
  STRIPE_SECRET_KEY="sk_test_YOUR_STRIPE_KEY" \
  STRIPE_PUBLISHABLE_KEY="pk_test_YOUR_STRIPE_KEY" \
  BACKEND_CORS_ORIGINS='["http://localhost:3000"]' \
  TRUST_PROXY_HEADERS="true"

# Deploy
railway up
railway domain  # SAVE THIS URL!

# Run migrations
railway run alembic upgrade head
```

**✓ Backend URL:** (save for next step)

### 2. Frontend (Vercel) - 10 min

```bash
# Install & login
npm install -g vercel
vercel login

# Configure
cd /mnt/e/projects/quant/quant/frontend
cp .env.production.example .env.production.local

# Edit .env.production.local with:
# NEXT_PUBLIC_API_URL=https://YOUR-RAILWAY-URL.up.railway.app
# NEXT_PUBLIC_STRIPE_PUBLISHABLE_KEY=pk_test_YOUR_KEY

# Deploy
vercel --prod  # SAVE THE URL!
```

**✓ Frontend URL:** (save for next step)

### 3. Update CORS (1 min)

```bash
cd /mnt/e/projects/quant/quant/backend
railway variables set BACKEND_CORS_ORIGINS='["https://YOUR-VERCEL-URL.vercel.app"]'
railway up
```

### 4. Stripe Webhook (5 min)

1. Go to: https://dashboard.stripe.com/test/webhooks
2. Click "Add endpoint"
3. URL: `https://YOUR-RAILWAY-URL.up.railway.app/api/v1/subscriptions/webhooks/stripe`
4. Events: `customer.subscription.*` and `invoice.payment_*`
5. Save, then copy webhook secret (`whsec_...`)
6. Run:
```bash
railway variables set STRIPE_WEBHOOK_SECRET="whsec_YOUR_SECRET"
railway up
```

### 5. Test (5 min)

```bash
# Test backend
curl https://YOUR-RAILWAY-URL.up.railway.app/health

# Test frontend
open https://YOUR-VERCEL-URL.vercel.app

# Test payment
# 1. Sign up on your site
# 2. Go to /pricing
# 3. Subscribe with card: 4242 4242 4242 4242
# 4. Verify subscription works
```

---

## ✅ Success Checklist

- [ ] Backend health check returns `{"status": "healthy"}`
- [ ] Frontend loads without errors
- [ ] No CORS errors in browser console
- [ ] Can sign up for account
- [ ] Can complete test payment
- [ ] Stripe webhook shows "Success (200)"

---

## 🎉 You're Live!

**Your URLs:**
- Frontend: `https://YOUR-APP.vercel.app`
- Backend: `https://YOUR-BACKEND.railway.app`
- API Docs: `https://YOUR-BACKEND.railway.app/api/v1/docs`

---

## 📊 What's Next?

### Today
- [ ] Test all features thoroughly
- [ ] Monitor logs: `railway logs`
- [ ] Share with friends for testing

### This Week
- [ ] Fix any bugs found
- [ ] Improve onboarding
- [ ] Prepare marketing materials

### Week 2
- [ ] Switch to live Stripe keys
- [ ] Announce launch
- [ ] Start marketing

---

## 💰 Revenue Timeline

- **Day 1:** Deploy (today!)
- **Day 1-3:** First signups
- **Day 7-14:** First payment
- **Month 1-2:** $1,000 MRR
- **Month 6-12:** $10,000 MRR

---

## 🆘 Need Help?

### Troubleshooting

**CORS errors:**
```bash
railway variables set BACKEND_CORS_ORIGINS='["https://YOUR-URL.vercel.app"]'
railway up
```

**Webhook not working:**
- Check URL is correct
- Verify secret: `railway variables`
- Check logs: `railway logs`

**Build failures:**
- Check Vercel deployment logs
- Verify all env variables set
- Clear cache and redeploy

### Documentation

- **Quick answers:** `/mnt/e/projects/quant/DEPLOYMENT_INDEX.md`
- **Full guide:** `/mnt/e/projects/quant/VERCEL_DEPLOYMENT_GUIDE.md`
- **Checklist:** `/mnt/e/projects/quant/DEPLOYMENT_CHECKLIST.md`

### Support

- **Railway:** https://docs.railway.app
- **Vercel:** https://vercel.com/docs
- **Stripe:** https://stripe.com/docs

---

## 💡 Pro Tips

1. **Use test mode first** - Test everything before switching to live Stripe keys
2. **Monitor costs** - Set up alerts in Railway dashboard
3. **Check logs daily** - First week, monitor for errors
4. **Backup before changes** - Railway has auto-backups, but be safe
5. **Start with free tier** - Vercel free tier is generous

---

## 📈 Cost Breakdown

**Month 1:**
- Vercel: $0 (free)
- Railway: $5-10
- Total: $5-10

**At 100 users:**
- Hosting: ~$20-30/month
- Revenue: ~$400/month
- **Profit: ~$370/month**

**At 1,000 users:**
- Hosting: ~$50-100/month
- Revenue: ~$4,000/month
- **Profit: ~$3,900/month**

---

## 🎯 Your Mission

1. ✅ Run verification script
2. ✅ Get required accounts
3. ✅ Generate secrets
4. ✅ Deploy backend (15 min)
5. ✅ Deploy frontend (10 min)
6. ✅ Configure Stripe (5 min)
7. ✅ Test everything (5 min)
8. ✅ Start getting revenue!

---

**Total Time: 30-45 minutes**

**Start now:** Open `DEPLOYMENT_QUICK_START.md` and begin!

---

**Status:** ✅ READY
**Stripe:** ✅ SECURE
**Docs:** ✅ COMPLETE

**LET'S DEPLOY!** 🚀
