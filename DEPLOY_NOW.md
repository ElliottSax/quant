# 🚀 Deploy Quant Backtesting - NOW

**30-second programmatic deployment**

---

## Step 1: Get Railway Token (15 seconds)

1. Visit: **https://railway.app/account/tokens**
2. Click **"Create Token"**  
3. Copy the token

---

## Step 2: Deploy (15 seconds + 3-5min build)

```bash
cd /mnt/e/projects/quant/quant/backend

# Set your token
export RAILWAY_TOKEN=railway_token_xxxxxxxxxxxxxxxxxxxxx

# Deploy!
./deploy_railway.sh
```

**Done!** ✅

---

## What Happens Automatically

The script will:
- ✅ Check Railway authentication
- ✅ Initialize Railway project `quant-backend`
- ✅ Set all environment variables
- ✅ Generate secure SECRET_KEY and JWT_SECRET_KEY  
- ✅ Deploy code to Railway
- ✅ Provide your live URL

**Time**: 3-5 minutes total

---

## Your Live API

After deployment:
```
Railway URL: https://quant-backend-production.up.railway.app

Test:
  curl https://your-url.railway.app/health
  curl https://your-url.railway.app/api/v1/backtesting/demo/strategies
  
Docs:
  https://your-url.railway.app/api/v1/docs
```

---

## Alternative: Python Script

```bash
export RAILWAY_TOKEN=your_token_here
python3 deploy_railway_api.py
```

---

## Full Documentation

- **Quick Start**: `PROGRAMMATIC_DEPLOYMENT.md`
- **Deployment Guide**: `DEPLOY_TO_RAILWAY_NOW.md`
- **Deployment Status**: `DEPLOYMENT_READY.md`

---

**Ready? Run this now:**

```bash
cd /mnt/e/projects/quant/quant/backend
export RAILWAY_TOKEN=your_token_here
./deploy_railway.sh
```

🚀 **Live in 5 minutes!**
