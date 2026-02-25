# 🚀 Deploy to Railway - One-Click Guide

**Status**: ✅ Code pushed to GitHub
**Commit**: `a041817` - Railway deployment config + backtesting demo endpoints
**Time to Deploy**: 5 minutes

**Latest Update**: Railway config files created (railway.toml + nixpacks.toml)

---

## 🎯 Quick Deploy (Web Interface)

### Step 1: Open Railway Dashboard
Click here: **https://railway.app/new**

### Step 2: Deploy from GitHub
1. Click **"Deploy from GitHub repo"**
2. Select: **`ElliottSax/quant`**
3. Railway will detect the configuration automatically

### Step 3: Configure Environment
Railway will auto-detect `railway.toml` and `nixpacks.toml`.

Add these environment variables in Railway dashboard:
```
PROJECT_NAME=QuantBacktesting
VERSION=1.0.0
API_V1_STR=/api/v1
ENVIRONMENT=production
DATABASE_URL=<Railway will auto-provide if you add PostgreSQL>
SECRET_KEY=<Railway will auto-generate>
JWT_SECRET_KEY=<Railway will auto-generate>
```

### Step 4: Add PostgreSQL (Optional)
- Click **"+ New"** → **"Database"** → **"PostgreSQL"**
- Railway will automatically set `DATABASE_URL`

Or use SQLite for demo:
```
DATABASE_URL=sqlite+aiosqlite:///./quant.db
```

### Step 5: Deploy!
- Click **"Deploy"**
- Wait 2-3 minutes for build
- Get your URL: `https://your-app.up.railway.app`

---

## 🧪 Test Your Deployment

```bash
# Test strategies endpoint
curl https://your-app.up.railway.app/api/v1/backtesting/demo/strategies

# Test backtest endpoint
curl -X POST https://your-app.up.railway.app/api/v1/backtesting/demo/run \
  -H "Content-Type: application/json" \
  -d '{
    "symbol": "AAPL",
    "start_date": "2025-06-01T00:00:00",
    "end_date": "2025-12-31T23:59:59",
    "strategy": "simple_ma_crossover",
    "initial_capital": 100000
  }'
```

**Expected**: JSON response with real backtest results!

---

## 🔧 Alternative: CLI Deployment

### 1. Login to Railway
```bash
railway login
```

### 2. Initialize Project
```bash
cd /mnt/e/projects/quant/quant/backend
railway init
```

### 3. Deploy
```bash
railway up
```

### 4. Set Variables
```bash
railway variables set PROJECT_NAME=QuantBacktesting
railway variables set VERSION=1.0.0
railway variables set ENVIRONMENT=production
```

### 5. Open Dashboard
```bash
railway open
```

---

## 📊 What Gets Deployed

### Backend (`quant/backend/`)
- ✅ FastAPI application
- ✅ Demo backtesting endpoints
- ✅ Yahoo Finance integration
- ✅ Async SQLite or PostgreSQL
- ✅ 2 uvicorn workers

### Configuration Files
- ✅ `railway.toml` - Railway config
- ✅ `nixpacks.toml` - Build config
- ✅ `requirements.txt` - Python dependencies

### Endpoints Live
- `/health` - Health check
- `/api/v1/backtesting/demo/strategies` - List strategies
- `/api/v1/backtesting/demo/run` - Run backtest
- `/docs` - API documentation

---

## 🌐 Update Frontend

After backend is deployed, update frontend:

### File: `quant/frontend/.env.local`
```bash
NEXT_PUBLIC_API_URL=https://your-app.up.railway.app/api/v1
```

### Deploy Frontend to Vercel
```bash
cd quant/frontend
vercel deploy --prod
```

Or use Vercel GitHub integration for auto-deploy!

---

## ✅ Verification Checklist

After deployment:
- [ ] Backend URL is live
- [ ] `/health` returns {"status": "healthy"}
- [ ] `/demo/strategies` returns strategy list
- [ ] `/demo/run` returns backtest results
- [ ] Frontend connects to backend
- [ ] Real Yahoo Finance data working

---

## 💰 Railway Pricing

**Starter Plan**: $5/month
- 500 hours execution time
- 8GB RAM
- 100GB bandwidth
- Perfect for demo/MVP

**Pro Plan**: $20/month
- Unlimited execution
- More resources
- Custom domains

---

## 🐛 Troubleshooting

### Build Fails
Check Railway logs:
```bash
railway logs
```

Common issues:
- Missing requirements.txt → Already included ✅
- Wrong Python version → Set to 3.12 in nixpacks.toml ✅
- Import errors → Fixed in code ✅

### Database Connection Error
If using PostgreSQL:
```bash
# Railway auto-provides this:
railway variables
# Should show DATABASE_URL
```

If using SQLite (demo):
```bash
railway variables set DATABASE_URL="sqlite+aiosqlite:///./quant.db"
```

### App Won't Start
Check port binding:
```bash
# Railway sets $PORT automatically
# Our start command uses it:
uvicorn app.main:app --host 0.0.0.0 --port $PORT
```

---

## 🎉 Success!

Once deployed:
1. ✅ Backend is live with real market data
2. ✅ Demo endpoints work without auth
3. ✅ Yahoo Finance integration functional
4. ✅ Ready for frontend connection
5. ✅ Revenue-generating demo mode active

**Next**: Connect frontend and start getting users! 💰

---

## 📚 Documentation

- **Railway Docs**: https://docs.railway.app
- **Backend Code**: `/mnt/e/projects/quant/quant/backend/`
- **Integration Guide**: `/mnt/e/projects/quant/INTEGRATION_SUMMARY.md`

---

**Deployment prepared by**: Claude Sonnet 4.5
**Code pushed**: commit `585720b`
**Ready to deploy**: ✅ YES

🚀 **Click the Railway link above and deploy in 5 minutes!**
