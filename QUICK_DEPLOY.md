# 🚀 Quick Deploy Guide

Deploy your Quant Trading Platform in **5 minutes**.

---

## Step 1: Pre-Check (30 seconds)

```bash
cd quant/backend
python3 scripts/pre_deployment_check.py
```

**Expected**: "🎉 DEPLOYMENT READY!"

---

## Step 2: Deploy (4 minutes)

```bash
./deploy.sh
```

Select **option 1** (Railway) and follow prompts.

---

## Step 3: Verify (30 seconds)

```bash
python3 quant/backend/scripts/verify_deployment.py https://your-app.railway.app
```

**Expected**: "🎉 ALL TESTS PASSED!"

---

## Done! 🎉

Your API is live at: `https://your-app.railway.app`

**API Docs**: `https://your-app.railway.app/api/v1/docs`

---

## Quick Test

```bash
curl https://your-app.railway.app/health
curl https://your-app.railway.app/api/v1/market-data/public/quote/AAPL
```

---

**Total Time**: ~5 minutes
**Cost**: $5/month
**Difficulty**: ⭐ Very Easy

See `DEPLOYMENT_GUIDE.md` for more options.
