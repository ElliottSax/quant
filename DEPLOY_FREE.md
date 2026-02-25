# 🆓 100% FREE Deployment (No Credit Card Required)

Railway paused free trials, so here are **truly free** alternatives:

---

## Option 1: Render (Recommended) ⭐

**100% FREE** - No credit card required!

### Deploy Backend

**One-Click Deploy**:  
https://render.com/deploy?repo=https://github.com/ElliottSax/quant

Or **Manual**:
1. Visit: https://render.com/
2. Sign up (free account)
3. Click "New" → "Web Service"
4. Connect GitHub → Select `ElliottSax/quant`
5. Settings:
   - **Name**: `quant-backend`
   - **Root Directory**: `quant/backend`
   - **Runtime**: Python 3
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
6. Add Environment Variables (click "Add Environment Variable"):
   ```
   PROJECT_NAME=QuantBacktestingPlatform
   VERSION=1.0.0
   API_V1_STR=/api/v1
   ENVIRONMENT=production
   DATABASE_URL=sqlite+aiosqlite:///./quant.db
   FINNHUB_API_KEY=d6fl2j9r01qqnmbp36ogd6fl2j9r01qqnmbp36p0
   BACKEND_CORS_ORIGINS=["*"]
   ```
7. Click "Create Web Service"

**Result**: `https://quant-backend.onrender.com`

**Note**: Free tier spins down after 15 min inactivity. First request may take 30s to wake up.

---

### Deploy Frontend (Vercel - Still Free!)

Vercel is still 100% free, no changes:

**One-Click Deploy**:  
https://vercel.com/new/clone?repository-url=https://github.com/ElliottSax/quant&project-name=quant-frontend&root-directory=quant/frontend

Or **Manual**:
1. Visit: https://vercel.com/
2. Click "Add New" → "Project"
3. Import `ElliottSax/quant`
4. Settings:
   - **Root Directory**: `quant/frontend`
   - **Framework**: Next.js (auto-detected)
5. Environment Variable:
   ```
   NEXT_PUBLIC_API_URL=https://quant-backend.onrender.com/api/v1
   ```
6. Click "Deploy"

**Result**: `https://quant-frontend.vercel.app`

---

## Option 2: Fly.io (Also Free)

**Free tier**: 3 shared-cpu VMs, 3GB storage

### Backend Deploy
```bash
# Install Fly CLI
curl -L https://fly.io/install.sh | sh

# Login
fly auth login

# Deploy backend
cd /mnt/e/projects/quant/quant/backend
fly launch --name quant-backend --region ord

# Set environment variables
fly secrets set \
  PROJECT_NAME=QuantBacktestingPlatform \
  ENVIRONMENT=production \
  FINNHUB_API_KEY=d6fl2j9r01qqnmbp36ogd6fl2j9r01qqnmbp36p0 \
  BACKEND_CORS_ORIGINS='["*"]'

# Deploy
fly deploy
```

**Result**: `https://quant-backend.fly.dev`

### Frontend (Vercel same as above)

---

## Option 3: Local Docker (Free, Instant)

**Deploy on your own machine** (great for testing):

```bash
cd /mnt/e/projects/quant

# Start everything
docker-compose -f docker-compose.deploy.yml up -d

# Your app is running:
# Backend: http://localhost:8000
# API Docs: http://localhost:8000/docs
# Test: http://localhost:8000/api/v1/finnhub/demo/quote/AAPL
```

Then expose via:
- **ngrok** (free): `ngrok http 8000`
- **Cloudflare Tunnel** (free): `cloudflared tunnel`

---

## Option 4: PythonAnywhere (Backend Only)

**Free tier**: Python web apps

1. Visit: https://www.pythonanywhere.com/
2. Sign up (free account)
3. Upload your code
4. Configure WSGI
5. Add environment variables

---

## Option 5: Railway (Requires Credit Card)

If you add a credit card, Railway gives you **$5/month credit**:

1. Visit: https://railway.app/
2. Add payment method (no charge, just verification)
3. Get $5 free credit
4. Deploy: https://railway.app/new?template=https://github.com/ElliottSax/quant

**$5 credit covers ~1000 hours** (full month 24/7)

---

## Comparison

| Platform | Backend | Frontend | Credit Card | Free Tier |
|----------|---------|----------|-------------|-----------|
| **Render** | ✅ Free | ➡️ Vercel | ❌ No | 750 hrs/mo |
| **Vercel** | ❌ No | ✅ Free | ❌ No | Unlimited |
| **Fly.io** | ✅ Free | ➡️ Vercel | ❌ No | 3 VMs |
| **Railway** | ⚠️ $5 credit | ➡️ Vercel | ✅ Yes | $5/mo |
| **Docker** | ✅ Local | ✅ Local | ❌ No | Unlimited |

---

## Recommended: Render + Vercel

**Total Cost**: $0  
**Credit Card**: Not required  
**Deployment Time**: 10 minutes  

### Quick Deploy
1. **Backend**: https://render.com/deploy?repo=https://github.com/ElliottSax/quant
2. **Frontend**: https://vercel.com/new/clone?repository-url=https://github.com/ElliottSax/quant&project-name=quant-frontend&root-directory=quant/frontend

---

## After Deployment

### Update Frontend API URL
After Render backend deploys:
1. Get your Render URL: `https://quant-backend.onrender.com`
2. Update Vercel environment variable:
   - Go to Vercel dashboard → Settings → Environment Variables
   - Update `NEXT_PUBLIC_API_URL` to: `https://quant-backend.onrender.com/api/v1`
3. Redeploy frontend

### Update CORS
In Render dashboard:
1. Go to Environment tab
2. Update `BACKEND_CORS_ORIGINS`:
   ```json
   ["https://quant-frontend.vercel.app","https://*.vercel.app"]
   ```

---

## Performance Notes

**Render Free Tier**:
- ✅ Full HTTPS
- ✅ Automatic deploys from GitHub
- ✅ Environment variables
- ⚠️ Spins down after 15 min inactivity
- ⚠️ First request after spin-down: ~30s wake time

**Solutions for spin-down**:
1. Use a free uptime monitor (UptimeRobot, Pingdom)
2. Upgrade to Render paid plan ($7/mo for always-on)
3. Use Fly.io instead (no spin-down on free tier)

---

## Deploy NOW (Free)

**Backend (Render)**:  
https://render.com/deploy?repo=https://github.com/ElliottSax/quant

**Frontend (Vercel)**:  
https://vercel.com/new/clone?repository-url=https://github.com/ElliottSax/quant&project-name=quant-frontend&root-directory=quant/frontend

**Total Time**: 10 minutes  
**Total Cost**: $0  
**Credit Card**: Not needed  

🚀 Deploy now!
