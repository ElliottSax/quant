# 🚀 Deploy Your App NOW - Copy & Paste Commands

## Option 1: Fully Automated (Railway + Vercel) - 2 minutes

**Open your terminal** and run these commands:

```bash
cd /mnt/e/projects/quant

# Step 1: Authenticate (opens browser - one time only)
railway login
vercel login

# Step 2: Deploy everything
./deploy.sh
```

**That's it!** Your app will be live at:
- Backend: `https://*.railway.app`
- Frontend: `https://*.vercel.app`

---

## Option 2: Railway Web Interface (No CLI) - 5 minutes

### Deploy Backend

1. **Push to GitHub first**:
```bash
cd /mnt/e/projects/quant
git add .
git commit -m "feat: Complete portfolio backtesting platform"
git push origin main
```

2. **Visit Railway**: https://railway.app/new

3. **Click**: "Deploy from GitHub repo"

4. **Select**: `quant` repository

5. **Root Directory**: `quant/backend`

6. **Add Environment Variables**:
```env
PROJECT_NAME=QuantBacktestingPlatform
VERSION=1.0.0
API_V1_STR=/api/v1
ENVIRONMENT=production
DATABASE_URL=sqlite+aiosqlite:///./quant.db
FINNHUB_API_KEY=d6fl2j9r01qqnmbp36ogd6fl2j9r01qqnmbp36p0
BACKEND_CORS_ORIGINS=["*"]
```

7. **Generate secrets** (click "Generate" next to each):
   - SECRET_KEY
   - JWT_SECRET_KEY

8. **Click**: "Deploy"

9. **Copy your backend URL**: e.g., `https://quant-backend.railway.app`

### Deploy Frontend

1. **Visit Vercel**: https://vercel.com/new

2. **Click**: "Import Git Repository"

3. **Select**: `quant` repository

4. **Root Directory**: `quant/frontend`

5. **Framework Preset**: Next.js (auto-detected)

6. **Add Environment Variable**:
```env
NEXT_PUBLIC_API_URL=https://your-backend.railway.app/api/v1
```
*(Replace with your actual Railway URL from step 9 above)*

7. **Click**: "Deploy"

8. **Done!** Your frontend is live at `https://quant-frontend.vercel.app`

### Update CORS

1. Go back to **Railway dashboard**
2. Click your backend project → **Variables**
3. Update `BACKEND_CORS_ORIGINS`:
```json
["https://quant-frontend.vercel.app","https://*.vercel.app"]
```

---

## Option 3: Docker Local Deploy - Test before cloud

```bash
cd /mnt/e/projects/quant

# Build and run
docker-compose -f docker-compose.deploy.yml up -d

# Your app is running at:
# Backend: http://localhost:8000
# Frontend: http://localhost:3000
# API Docs: http://localhost:8000/docs

# Test it works, then deploy to Railway/Vercel
```

---

## Option 4: GitHub Actions (Auto-deploy on push)

Already configured! Just need to add secrets:

### Get Your Tokens

```bash
# Railway token
railway login
railway token

# Vercel token  
vercel login
vercel whoami --token

# Vercel org/project IDs
cd quant/frontend
vercel link
# Copy the org and project IDs from output
```

### Add Secrets to GitHub

1. Go to: https://github.com/your-username/quant/settings/secrets/actions

2. Click "New repository secret" and add:

| Secret Name | Value |
|------------|-------|
| `RAILWAY_TOKEN` | (from `railway token`) |
| `VERCEL_TOKEN` | (from `vercel whoami --token`) |
| `VERCEL_ORG_ID` | (from `vercel link`) |
| `VERCEL_PROJECT_ID` | (from `vercel link`) |

3. **Push to main** and it auto-deploys:
```bash
git push origin main
```

---

## Which Option Should I Choose?

| Option | Time | Best For |
|--------|------|----------|
| **Option 1** | 2 min | If you're comfortable with CLI |
| **Option 2** | 5 min | If you prefer web interfaces |
| **Option 3** | 3 min | Testing locally first |
| **Option 4** | 10 min setup | Continuous deployment |

**Recommendation**: Try **Option 1** first (fastest). If it doesn't work, use **Option 2**.

---

## After Deployment

### Test Your App

1. **Backend API Docs**:
   ```
   https://your-backend.railway.app/docs
   ```

2. **Test Real-Time Quote**:
   ```
   https://your-backend.railway.app/api/v1/finnhub/demo/quote/AAPL
   ```

3. **Frontend**:
   ```
   https://your-frontend.vercel.app
   ```

4. **Run Portfolio Backtest**:
   - Go to frontend URL
   - Navigate to "Portfolio Backtesting"
   - Add symbols: AAPL, MSFT, GOOGL
   - Select optimization method
   - Click "Run Backtest"

### Share Your URLs

```bash
echo "🎉 My Quant Trading Platform is LIVE!"
echo ""
echo "📊 Try it: https://your-frontend.vercel.app"
echo "📖 API Docs: https://your-backend.railway.app/docs"
echo ""
echo "Features:"
echo "✅ Portfolio backtesting with 5 optimization methods"
echo "✅ Real-time stock quotes (Finnhub)"
echo "✅ News sentiment analysis"
echo "✅ Advanced visualizations"
echo "✅ Efficient frontier analysis"
```

---

## Troubleshooting

### "Module not found" errors

```bash
# Backend
cd quant/backend
pip install -r requirements.txt

# Frontend
cd quant/frontend
npm install
```

### Can't connect to backend from frontend

Check CORS settings in Railway dashboard:
```json
BACKEND_CORS_ORIGINS=["https://your-frontend.vercel.app","https://*.vercel.app"]
```

### Finnhub API not working

Verify in Railway dashboard → Variables:
```
FINNHUB_API_KEY=d6fl2j9r01qqnmbp36ogd6fl2j9r01qqnmbp36p0
```

### Still stuck?

```bash
# Check if services are installed
which railway
which vercel

# Install if missing
npm install -g @railway/cli vercel
```

---

## Next Steps

1. ✅ Deploy app
2. ✅ Test all features
3. 📱 Launch on Product Hunt (see `MARKETING_LAUNCH_GUIDE.md`)
4. 💰 Add monetization ($29/mo premium tier)
5. 📈 Scale to 1,000+ users

**Estimated Time to Live**: 2-10 minutes depending on option chosen

**Ready? Pick an option above and deploy! 🚀**
