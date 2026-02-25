# Deploy Backend to Railway - Step by Step

## 🚀 Railway Deployment (10 minutes)

Railway is the easiest way to deploy the FastAPI backend. Free tier includes:
- ✅ $5 free credit per month
- ✅ Automatic HTTPS
- ✅ PostgreSQL database (optional)
- ✅ Environment variables
- ✅ Automatic deployments from Git

---

## Prerequisites

- [ ] GitHub account
- [ ] Railway account (sign up at railway.app)
- [ ] Finnhub API key (from Task #7)
- [ ] Code pushed to GitHub

---

## Method 1: Railway CLI (Fastest)

### Step 1: Install Railway CLI

```bash
# macOS/Linux
curl -fsSL https://railway.app/install.sh | sh

# Or with npm
npm install -g @railway/cli

# Or with Homebrew
brew install railway
```

### Step 2: Login to Railway

```bash
railway login
```

This opens a browser window to authenticate.

### Step 3: Initialize Project

```bash
cd /mnt/e/projects/quant/quant/backend

# Link to new Railway project
railway init

# Project name: quant-backend
```

### Step 4: Add Environment Variables

```bash
# Add all required variables
railway variables set PROJECT_NAME="QuantBacktestingPlatform"
railway variables set VERSION="1.0.0"
railway variables set ENVIRONMENT="production"
railway variables set API_V1_STR="/api/v1"

# Database (Railway will provide or use SQLite)
railway variables set DATABASE_URL="sqlite+aiosqlite:///./quant.db"

# Secrets (CHANGE THESE!)
railway variables set SECRET_KEY="$(openssl rand -base64 32)"
railway variables set JWT_SECRET_KEY="$(openssl rand -base64 32)"

# Finnhub API key (YOUR KEY HERE)
railway variables set FINNHUB_API_KEY="your_finnhub_key_here"

# CORS (update after frontend deployed)
railway variables set BACKEND_CORS_ORIGINS='["https://quant-frontend.vercel.app","https://your-domain.com"]'
```

### Step 5: Deploy

```bash
# Deploy the backend
railway up

# Get deployment URL
railway domain

# Expected output: https://quant-backend.railway.app
```

### Step 6: Verify Deployment

```bash
# Test health endpoint
curl https://quant-backend.railway.app/health

# Test API docs
# Visit: https://quant-backend.railway.app/docs

# Test portfolio backtesting
curl -X POST https://quant-backend.railway.app/api/v1/backtesting/portfolio/demo/run \
  -H "Content-Type: application/json" \
  -d '{
    "symbols": ["AAPL", "MSFT"],
    "start_date": "2025-06-01T00:00:00",
    "end_date": "2025-12-31T23:59:59",
    "optimization_method": "equal_weight",
    "initial_capital": 100000
  }'
```

---

## Method 2: Railway Web Interface (Easier)

### Step 1: Push Code to GitHub

```bash
cd /mnt/e/projects/quant

# If not already a git repo
git init
git add .
git commit -m "feat: Add portfolio backtesting and Finnhub integration"

# Create GitHub repo and push
gh repo create quant-backend --public --source=. --remote=origin --push

# Or manually:
# 1. Create repo on github.com
# 2. git remote add origin https://github.com/yourusername/quant-backend.git
# 3. git push -u origin main
```

### Step 2: Deploy from GitHub

1. **Visit**: https://railway.app/new
2. **Click**: "Deploy from GitHub repo"
3. **Select**: Your `quant-backend` repository
4. **Select**: `quant/backend` directory
5. **Click**: "Deploy Now"

### Step 3: Configure Environment Variables

In Railway dashboard:

1. **Click**: Your project → "Variables"
2. **Add** these variables:

```env
PROJECT_NAME=QuantBacktestingPlatform
VERSION=1.0.0
ENVIRONMENT=production
API_V1_STR=/api/v1
DATABASE_URL=sqlite+aiosqlite:///./quant.db
SECRET_KEY=your-secret-key-change-this-min-32-chars
JWT_SECRET_KEY=your-jwt-key-change-this-min-32-chars
FINNHUB_API_KEY=your_finnhub_key_here
BACKEND_CORS_ORIGINS=["https://quant-frontend.vercel.app"]
```

### Step 4: Add Custom Domain (Optional)

1. **Click**: "Settings" → "Domains"
2. **Click**: "Generate Domain"
3. **Copy**: Your Railway URL (e.g., `quant-backend.up.railway.app`)

Or add custom domain:
1. **Click**: "Custom Domain"
2. **Enter**: `api.yourdomain.com`
3. **Add DNS**: CNAME record pointing to Railway

---

## Method 3: One-Click Deploy Button

**Add this to your GitHub README**:

```markdown
[![Deploy on Railway](https://railway.app/button.svg)](https://railway.app/template/quant-backend)
```

Users can deploy with one click!

---

## 🔧 Configuration Files

### railway.toml

Already exists in `/mnt/e/projects/quant/quant/backend/railway.toml`:

```toml
[build]
builder = "nixpacks"
buildCommand = "pip install -r requirements.txt"

[deploy]
startCommand = "uvicorn app.main:app --host 0.0.0.0 --port $PORT"
healthcheckPath = "/health"
healthcheckTimeout = 100
restartPolicyType = "on_failure"
restartPolicyMaxRetries = 10
```

### nixpacks.toml

Already exists in `/mnt/e/projects/quant/quant/backend/nixpacks.toml`:

```toml
[phases.setup]
nixPkgs = ["python312", "postgresql"]

[phases.install]
cmds = ["pip install -r requirements.txt"]

[start]
cmd = "uvicorn app.main:app --host 0.0.0.0 --port $PORT"
```

**Both files are already configured - no changes needed!**

---

## 🎯 Environment Variables Reference

### Required (Minimum)

```env
PROJECT_NAME=QuantBacktestingPlatform
VERSION=1.0.0
API_V1_STR=/api/v1
ENVIRONMENT=production
SECRET_KEY=<generate-with-openssl>
JWT_SECRET_KEY=<generate-with-openssl>
DATABASE_URL=sqlite+aiosqlite:///./quant.db
```

### Recommended

```env
FINNHUB_API_KEY=<your-key>
BACKEND_CORS_ORIGINS=["https://your-frontend.vercel.app"]
SENTRY_DSN=<optional-for-monitoring>
```

### Generate Secrets

```bash
# Generate SECRET_KEY
openssl rand -base64 32

# Generate JWT_SECRET_KEY
openssl rand -base64 32
```

---

## 🚨 Troubleshooting

### Issue: Build fails with "Module not found"

**Solution**: Check `requirements.txt` includes all dependencies
```bash
cd quant/backend
pip freeze > requirements.txt
git add requirements.txt
git commit -m "Update requirements"
git push
```

### Issue: App crashes on startup

**Solution**: Check logs in Railway dashboard
```bash
railway logs
```

Common issues:
- Missing environment variables
- Database connection fails
- Port binding issues (use `$PORT` variable)

### Issue: CORS errors in frontend

**Solution**: Update `BACKEND_CORS_ORIGINS`
```bash
railway variables set BACKEND_CORS_ORIGINS='["https://your-frontend.vercel.app","https://your-domain.com"]'
```

### Issue: Finnhub not working

**Solution**: Verify API key is set
```bash
railway variables

# Should show: FINNHUB_API_KEY=xxx...
```

Test endpoint:
```bash
curl https://your-app.railway.app/api/v1/finnhub/demo/status
```

---

## ✅ Deployment Checklist

- [ ] Code pushed to GitHub
- [ ] Railway account created
- [ ] Project deployed (CLI or web)
- [ ] Environment variables configured
- [ ] Secrets generated (SECRET_KEY, JWT_SECRET_KEY)
- [ ] Finnhub API key added
- [ ] CORS origins updated
- [ ] Health check passes (`/health`)
- [ ] API docs accessible (`/docs`)
- [ ] Portfolio backtest endpoint works
- [ ] Finnhub endpoints work
- [ ] Custom domain added (optional)

---

## 📊 Deployment Costs

**Railway Free Tier**:
- ✅ $5 free credits per month
- ✅ ~500 hours runtime (enough for small app)
- ✅ 100GB bandwidth
- ✅ 1GB RAM

**Estimated usage**:
- Backend: ~$3-5/month (well within free tier)
- Database: Free (SQLite) or $5/month (PostgreSQL)

**Upgrade when needed**:
- **Starter**: $5/month (more resources)
- **Pro**: $20/month (production-ready)

---

## 🎯 Next Steps

After Railway deployment:

1. ✅ Copy Railway URL: `https://quant-backend.railway.app`
2. ➡️ **Deploy Frontend** (Task #9)
   - Use Railway URL as `NEXT_PUBLIC_API_URL`
3. ➡️ **Test End-to-End**
   - Frontend → Backend → Database
4. ➡️ **Market** (Task #10)
   - Launch on Product Hunt
   - Social media

---

## 🔗 Useful Links

- **Railway Dashboard**: https://railway.app/dashboard
- **Railway Docs**: https://docs.railway.app
- **Deployment Logs**: `railway logs`
- **Domain Settings**: Dashboard → Settings → Domains
- **Environment Vars**: Dashboard → Variables

---

**Status**: ⏳ Ready to deploy
**Time**: 10 minutes
**Cost**: FREE (Railway free tier)
**Next**: Deploy frontend to Vercel
