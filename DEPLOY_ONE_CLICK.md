# 🚀 One-Click Deployment

## Deploy Backend to Railway

**Click this button:**

[![Deploy on Railway](https://railway.app/button.svg)](https://railway.app/template/Z8qV3D?referralCode=bonus)

Or visit: https://railway.app/new/template/Z8qV3D

**Manual Railway Deploy:**
1. Go to: https://railway.app/new
2. Select "Deploy from GitHub repo"
3. Choose: `ElliottSax/quant`
4. Root directory: `quant/backend`
5. Click "Deploy Now"

**Railway will auto-configure from `railway.toml`**

---

## Deploy Frontend to Vercel

**Click this button:**

[![Deploy with Vercel](https://vercel.com/button)](https://vercel.com/new/clone?repository-url=https://github.com/ElliottSax/quant&project-name=quant-frontend&root-directory=quant/frontend)

Or visit this direct link:
```
https://vercel.com/new/clone?repository-url=https://github.com/ElliottSax/quant&project-name=quant-frontend&root-directory=quant/frontend
```

**Vercel will auto-configure from `vercel.json`**

---

## Environment Variables (Auto-configured)

### Backend (Railway) - Already in railway.toml:
- ✅ PROJECT_NAME
- ✅ ENVIRONMENT  
- ✅ FINNHUB_API_KEY
- ✅ DATABASE_URL
- ✅ CORS settings

### Frontend (Vercel) - Already in vercel.json:
- ✅ NEXT_PUBLIC_API_URL

**Note**: After backend deploys, update frontend's `NEXT_PUBLIC_API_URL` with actual Railway URL.

---

## Post-Deployment

1. **Get your backend URL** from Railway dashboard
2. **Update Vercel** environment variable:
   - Go to Vercel project → Settings → Environment Variables
   - Update `NEXT_PUBLIC_API_URL` to: `https://your-railway-url.railway.app/api/v1`
3. **Redeploy frontend** in Vercel

---

## Test Your Deployment

**Backend Health Check:**
```bash
curl https://your-backend.railway.app/health
```

**API Documentation:**
```
https://your-backend.railway.app/docs
```

**Frontend:**
```
https://your-frontend.vercel.app
```

**Test Finnhub:**
```bash
curl https://your-backend.railway.app/api/v1/finnhub/demo/quote/AAPL
```

---

## Deployment Time

- Railway: ~3-5 minutes
- Vercel: ~2-3 minutes
- Total: ~8 minutes

**Status**: Ready to deploy! Click the buttons above. 🚀
