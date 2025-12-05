# ⚡ Quick Deploy Guide
## Deploy in 10 Minutes with Your Credentials

**Prerequisites**: You have credentials from Supabase, Upstash, and Cloudflare R2

---

## 🚂 Part 1: Deploy Backend to Railway (5 min)

### Step 1: Install & Login

```bash
# Install Railway CLI
npm install -g @railway/cli

# Login to Railway
railway login
```

### Step 2: Deploy Backend

```bash
# Navigate to backend
cd quant/backend

# Initialize Railway project
railway init

# When prompted:
# - Create new project: Yes
# - Project name: quant-backend
# - Environment: production

# Set all environment variables
railway variables set SECRET_KEY="5fSHEsLC9QtzZknTXCC3pZ3lLakOrp9IUQp/ZpaC4Bs="
railway variables set DATABASE_URL="YOUR_SUPABASE_URL_HERE"
railway variables set REDIS_URL="YOUR_UPSTASH_URL_HERE"
railway variables set REDIS_ML_URL="YOUR_UPSTASH_URL_HERE"
railway variables set AWS_ACCESS_KEY_ID="YOUR_R2_ACCESS_KEY"
railway variables set AWS_SECRET_ACCESS_KEY="YOUR_R2_SECRET_KEY"
railway variables set AWS_S3_ENDPOINT_URL="YOUR_R2_ENDPOINT"
railway variables set ENVIRONMENT="production"
railway variables set DEBUG="false"
railway variables set API_V1_STR="/api/v1"
railway variables set PROJECT_NAME="Quant Analytics Platform"
railway variables set BACKEND_CORS_ORIGINS="http://localhost:3000"

# Deploy!
railway up

# Get your Railway URL
railway status
# Copy the URL (e.g., https://quant-backend-production.railway.app)
```

### Step 3: Run Database Migrations

```bash
# Still in quant/backend directory
railway run alembic upgrade head
```

### Step 4: Test Backend

```bash
# Replace with your actual Railway URL
curl https://your-railway-url.railway.app/health

# Should return: {"status":"healthy",...}
```

**✅ Backend deployed! Save your Railway URL.**

---

## ▲ Part 2: Deploy Frontend to Vercel (3 min)

### Step 1: Install & Login

```bash
# Install Vercel CLI
npm install -g vercel

# Login to Vercel
vercel login
```

### Step 2: Deploy Frontend

```bash
# Navigate to frontend
cd ../../quant/frontend

# Create production env file
echo "NEXT_PUBLIC_API_URL=https://your-railway-url.railway.app" > .env.production
echo "NODE_ENV=production" >> .env.production

# Replace "your-railway-url.railway.app" with your actual Railway URL

# Deploy to Vercel
vercel --prod

# Follow prompts:
# - Set up and deploy? Yes
# - Which scope? (Your account)
# - Link to existing project? No
# - Project name? quant-frontend
# - Directory? ./
# - Override settings? No

# Get your Vercel URL (e.g., https://quant-frontend.vercel.app)
vercel inspect
```

**✅ Frontend deployed! Save your Vercel URL.**

---

## 🔧 Part 3: Update CORS (2 min)

```bash
# Go back to backend
cd ../backend

# Update CORS with your Vercel URL
railway variables set BACKEND_CORS_ORIGINS="https://your-vercel-url.vercel.app,http://localhost:3000"

# Replace "your-vercel-url.vercel.app" with your actual Vercel URL

# Redeploy backend
railway up --detach
```

---

## ✅ Part 4: Test Everything (2 min)

### Test Backend API:
```bash
# Health check
curl https://your-railway-url.railway.app/health

# API docs (open in browser)
open https://your-railway-url.railway.app/api/v1/docs
```

### Test Frontend:
```bash
# Open in browser
open https://your-vercel-url.vercel.app

# Try:
# 1. Register a new account
# 2. Login
# 3. Navigate around
```

### Test Integration:
```bash
# Register user via API
curl -X POST https://your-railway-url.railway.app/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "username": "testuser",
    "password": "TestPassword123"
  }'

# Should return user object with id, email, username
```

---

## 🎉 Done!

Your app is now live at:
- **Frontend**: https://your-vercel-url.vercel.app
- **Backend**: https://your-railway-url.railway.app
- **API Docs**: https://your-railway-url.railway.app/api/v1/docs

**Monthly Cost**: $0 🎊

---

## 📊 Monitor Your Deployments

### Railway Dashboard:
- https://railway.app/dashboard
- View logs: `railway logs`
- View metrics: Check dashboard

### Vercel Dashboard:
- https://vercel.com/dashboard
- View logs: `vercel logs`
- View analytics: Check dashboard

### Supabase Dashboard:
- https://supabase.com/dashboard
- View database tables
- Monitor storage usage (stay under 500MB)

### Upstash Dashboard:
- https://console.upstash.com
- Monitor command count (stay under 10K/day)
- View metrics

---

## 🔄 Future Deployments

After initial setup, deploying updates is EASY:

```bash
# Backend updates - just push to git
cd quant/backend
git add .
git commit -m "Update backend"
git push
# Railway auto-deploys! ✨

# Frontend updates - just push to git
cd ../frontend
git add .
git commit -m "Update frontend"
git push
# Vercel auto-deploys! ✨
```

**Or redeploy manually:**
```bash
# Backend
cd quant/backend
railway up

# Frontend
cd ../frontend
vercel --prod
```

---

## 🆘 Troubleshooting

### Backend not deploying:
```bash
railway logs --tail
# Check for errors

# Common fixes:
railway variables set DATABASE_URL="correct-url"
railway up
```

### Frontend not loading:
```bash
vercel logs
# Check for errors

# Common fix:
vercel env add NEXT_PUBLIC_API_URL production
vercel --prod
```

### CORS errors:
```bash
# Update backend CORS
cd quant/backend
railway variables set BACKEND_CORS_ORIGINS="https://your-vercel-url.vercel.app,http://localhost:3000"
railway up --detach
```

---

## 📝 What's Next?

- [ ] Configure custom domain (optional)
- [ ] Setup monitoring alerts
- [ ] Add more users
- [ ] Monitor free tier usage
- [ ] Configure backups (Supabase auto-backs up 7 days)

---

**Total Deployment Time**: ~10 minutes
**Monthly Cost**: $0
**Supports**: ~10,000 users/month

🎊 **Congratulations! You're running on free infrastructure!** 🎊
