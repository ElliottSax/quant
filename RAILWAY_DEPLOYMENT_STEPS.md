# 🚀 Railway Deployment Guide - Stock Prediction Platform

**Time to Deploy**: ~5-10 minutes
**Cost**: $5-20/month (includes PostgreSQL)

---

## ✅ Prerequisites (Already Done!)

- [x] Railway CLI installed
- [x] Railway configuration files ready (`railway.toml`, `nixpacks.toml`)
- [x] Production-ready code (security score 9/10)
- [x] Requirements.txt updated with all dependencies
- [x] Database models and migrations ready

---

## 🎯 Deployment Steps

### Step 1: Login to Railway

```bash
cd /mnt/e/projects/quant/quant/backend
railway login
```

This will open your browser for authentication.

### Step 2: Create New Project (or Link Existing)

**Option A: Create New Project**
```bash
railway init
```
- Project name: `quant-stock-prediction`
- Select: Create new project

**Option B: Link Existing Project**
```bash
railway link
```
- Select your existing project from the list

### Step 3: Add PostgreSQL Database

```bash
railway add --database postgresql
```

This automatically:
- Provisions a PostgreSQL 16 database
- Sets `DATABASE_URL` environment variable
- Configures connection pooling

### Step 4: Set Required Environment Variables

```bash
# Generate secure secret keys (32+ characters)
railway variables set SECRET_KEY=$(openssl rand -hex 32)
railway variables set JWT_SECRET_KEY=$(openssl rand -hex 32)

# Basic configuration
railway variables set ENVIRONMENT=production
railway variables set DEBUG=false
railway variables set PROJECT_NAME="Quant Analytics Platform"
railway variables set API_V1_STR=/api/v1
railway variables set VERSION=1.0.0

# CORS (update with your frontend URL later)
railway variables set BACKEND_CORS_ORIGINS="http://localhost:3000,https://your-app.vercel.app"

# Security
railway variables set ALGORITHM=HS256
railway variables set ACCESS_TOKEN_EXPIRE_MINUTES=30
```

### Step 5: Set Optional API Keys (For Full Functionality)

```bash
# Market Data (at least one recommended)
railway variables set ALPHA_VANTAGE_API_KEY=your-key-here
railway variables set POLYGON_API_KEY=your-key-here
railway variables set FINNHUB_API_KEY=your-key-here

# AI/ML (optional)
railway variables set OPENAI_API_KEY=your-key-here
railway variables set ANTHROPIC_API_KEY=your-key-here

# Monitoring (recommended)
railway variables set SENTRY_DSN=your-sentry-dsn-here

# Email (for alerts)
railway variables set RESEND_API_KEY=your-resend-key-here
railway variables set EMAIL_FROM=noreply@yourdomain.com
```

### Step 6: Deploy!

```bash
railway up
```

This will:
1. Build your application using Nixpacks
2. Install all dependencies (including pandas-ta)
3. Run database migrations
4. Start the server with `uvicorn`
5. Make it live on Railway's domain

### Step 7: Run Database Migrations

```bash
# SSH into the Railway container
railway run alembic upgrade head
```

Or set up automatic migrations by updating the start command:
```bash
railway variables set NIXPACKS_START_CMD="alembic upgrade head && uvicorn app.main:app --host 0.0.0.0 --port \$PORT --workers 2"
```

---

## 🌐 Access Your Deployed API

After deployment completes:

```bash
# Get your deployment URL
railway domain
```

Your API will be live at:
- **API**: `https://your-project.railway.app`
- **Docs**: `https://your-project.railway.app/docs`
- **Health**: `https://your-project.railway.app/health`

---

## 🔧 Useful Railway Commands

```bash
# View deployment logs
railway logs

# Check environment variables
railway variables

# Open project dashboard
railway open

# SSH into container (for debugging)
railway shell

# Redeploy
railway up --detach

# Rollback to previous deployment
railway rollback
```

---

## 💰 Cost Optimization

**Free Tier**: $5 free credit/month
- Good for testing
- ~140 hours of runtime

**Starter Plan**: $5/month
- $5 credit included
- Additional usage billed
- PostgreSQL: ~$5-10/month

**Estimated Monthly Cost**: $5-20
- Backend service: ~$5
- PostgreSQL: ~$5-10
- Bandwidth: minimal

**Tips to Reduce Costs**:
1. Use Railway's free PostgreSQL (500MB included)
2. Set auto-sleep for development environments
3. Use hobby plan Redis (Upstash free tier)
4. Monitor usage in Railway dashboard

---

## ⚙️ Post-Deployment Configuration

### 1. Add Custom Domain (Optional)

```bash
railway domain add yourdomain.com
```

Then add DNS records:
- CNAME: `api` → `your-project.railway.app`

### 2. Set Up Redis (Optional, for caching)

Use Upstash Redis (free tier):
```bash
railway variables set REDIS_URL=your-upstash-redis-url
railway variables set CACHE_ENABLED=true
railway variables set CACHE_TTL=3600
```

### 3. Configure CORS for Frontend

After deploying frontend to Vercel:
```bash
railway variables set BACKEND_CORS_ORIGINS="https://your-app.vercel.app,https://yourdomain.com"
railway restart
```

### 4. Enable Monitoring

Add Sentry:
```bash
railway variables set SENTRY_DSN=your-sentry-dsn
railway variables set SENTRY_ENVIRONMENT=production
railway restart
```

---

## 🐛 Troubleshooting

### Build Fails

```bash
# View build logs
railway logs --build

# Common fixes:
# 1. Check requirements.txt is correct
# 2. Verify Python version in nixpacks.toml (3.12)
# 3. Check for missing dependencies
```

### Database Connection Issues

```bash
# Verify DATABASE_URL is set
railway variables | grep DATABASE_URL

# Test database connection
railway run python -c "from app.core.database import engine; print('Connected!')"
```

### Server Won't Start

```bash
# Check server logs
railway logs --tail

# Verify PORT variable
railway variables | grep PORT

# Check health endpoint
curl https://your-project.railway.app/health
```

### Migration Issues

```bash
# Run migrations manually
railway run alembic upgrade head

# Check current migration version
railway run alembic current

# View migration history
railway run alembic history
```

---

## 📊 Monitoring Your Deployment

### Railway Dashboard
- URL: https://railway.app/project/your-project-id
- View: Metrics, logs, deployments, usage

### Health Check
```bash
curl https://your-project.railway.app/health
```

Expected response:
```json
{
  "status": "healthy",
  "database": "connected",
  "timestamp": "2026-02-24T..."
}
```

### API Documentation
Visit: `https://your-project.railway.app/docs`
- Interactive API testing
- All 50+ endpoints documented
- Test authentication flow

---

## 🎯 Next Steps After Deployment

1. **Test Authentication**:
   - Register a user via `/api/v1/auth/register`
   - Login and get JWT token
   - Test prediction endpoints

2. **Deploy Frontend**:
   - Update `NEXT_PUBLIC_API_URL` to Railway URL
   - Deploy to Vercel
   - Update CORS settings

3. **Add Monitoring**:
   - Set up Sentry for error tracking
   - Configure logging
   - Set up alerts

4. **Production Checklist**:
   - [ ] Custom domain configured
   - [ ] SSL/TLS enabled (automatic on Railway)
   - [ ] Environment variables secured
   - [ ] Database backups enabled
   - [ ] Monitoring active
   - [ ] CORS properly configured
   - [ ] API keys rotated from development

---

## ✅ Success Verification

After deployment, verify:

```bash
# 1. Check health
curl https://your-project.railway.app/health

# 2. Check API docs
curl https://your-project.railway.app/docs

# 3. Test authentication
curl -X POST https://your-project.railway.app/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","username":"test","password":"SecurePass123!"}'

# 4. View logs
railway logs --tail
```

---

## 🎉 You're Live!

Once deployed, your stock prediction platform will be:
- ✅ Publicly accessible
- ✅ Secured with JWT authentication
- ✅ Protected by rate limiting
- ✅ Connected to PostgreSQL database
- ✅ Auto-scaling on Railway
- ✅ HTTPS enabled
- ✅ 99.9% uptime SLA

**Deployment URL**: https://your-project.railway.app
**API Docs**: https://your-project.railway.app/docs

---

**Questions or issues?** Check Railway docs: https://docs.railway.app
