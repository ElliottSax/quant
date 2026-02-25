# 🌐 Deploy via Railway Web Interface

**No CLI token needed - 2-minute deployment**

---

## Step 1: Go to Railway

**Click this link**: https://railway.app/new

---

## Step 2: Deploy from GitHub

1. Click **"Deploy from GitHub repo"**
2. Select repository: **`ElliottSax/quant`**
3. Railway will scan and find: `quant/backend`

---

## Step 3: Configure (Optional)

Railway auto-detects:
- ✅ `railway.toml` - deployment config
- ✅ `nixpacks.toml` - Python 3.12 build
- ✅ Start command: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`

Add these environment variables (or use defaults):
```
PROJECT_NAME=QuantBacktesting
VERSION=1.0.0
ENVIRONMENT=production
DATABASE_URL=sqlite+aiosqlite:///./quant.db
```

Railway will auto-generate:
- `SECRET_KEY`
- `JWT_SECRET_KEY`
- `PORT`

---

## Step 4: Click Deploy

**That's it!** ✅

Railway will:
- Build your app (2-3 minutes)
- Run health checks
- Provide a live URL

---

## Step 5: Get Your URL

After deployment completes:
1. Click on your service
2. Go to "Settings" → "Domains"
3. Copy your Railway URL (e.g., `quant-backend-production.up.railway.app`)

---

## Step 6: Test

```bash
# Replace with your actual URL
export API_URL="https://your-app.up.railway.app"

curl $API_URL/health
curl $API_URL/api/v1/backtesting/demo/strategies
```

---

**Total Time**: 2 minutes clicking + 3 minutes building = **5 minutes total**

**Click to deploy now**: https://railway.app/new
