# Quick Start - Production Deployment

Get your Quant Analytics Platform deployed to production in 30 minutes.

## TL;DR

```bash
# 1. Setup
cp .env.example .env.production
# Edit .env.production with your credentials

# 2. Deploy (interactive)
./scripts/quick_deploy.sh

# 3. Verify
python scripts/smoke_test.py --url https://api.yourdomain.com
```

## Prerequisites (5 minutes)

### Create Accounts
1. **Railway** - https://railway.app (Backend hosting)
2. **Vercel** - https://vercel.com (Frontend hosting)
3. **Supabase** - https://supabase.com (Database)
4. **Sentry** - https://sentry.io (Error tracking)

### Install Tools
```bash
# Railway CLI
npm i -g @railway/cli

# Vercel CLI
npm i -g vercel
```

## Step 1: Configure Environment (10 minutes)

### Copy template
```bash
cp .env.example .env.production
```

### Generate secrets
```bash
# Generate SECRET_KEY
python -c "import secrets; print(secrets.token_urlsafe(64))"

# Generate JWT_SECRET_KEY
python -c "import secrets; print(secrets.token_urlsafe(64))"
```

### Get credentials

#### Supabase (Database)
1. Create new project
2. Go to Settings → Database
3. Copy connection string
4. Add to `.env.production` as `DATABASE_URL`

#### Railway (Redis)
1. Create new project
2. Add Redis service
3. Copy connection URL
4. Add to `.env.production` as `REDIS_URL`

#### Sentry (Errors)
1. Create new project (FastAPI)
2. Copy DSN
3. Add to `.env.production` as `SENTRY_DSN`

#### SendGrid (Email - Optional)
1. Create API key
2. Add to `.env.production` as `SENDGRID_API_KEY`

## Step 2: Deploy Backend (5 minutes)

```bash
# Login to Railway
railway login

# Deploy
cd backend
railway up

# Set environment variables
railway variables --environment production < ../.env.production
```

## Step 3: Setup Database (3 minutes)

```bash
# Enable TimescaleDB in Supabase
# Go to SQL Editor, run:
CREATE EXTENSION IF NOT EXISTS timescaledb CASCADE;

# Run migrations
export DATABASE_URL="your-database-url"
cd backend
alembic upgrade head
```

## Step 4: Deploy Frontend (5 minutes)

```bash
# Login to Vercel
vercel login

# Deploy
cd frontend
vercel --prod

# Set environment variables
vercel env add NEXT_PUBLIC_API_URL production
# Enter: https://your-backend-url.railway.app

vercel env add NEXT_PUBLIC_SUPABASE_URL production
# Enter: https://your-project.supabase.co

vercel env add NEXT_PUBLIC_SUPABASE_ANON_KEY production
# Enter: your-anon-key
```

## Step 5: Verify Deployment (2 minutes)

```bash
# Run smoke tests
python scripts/smoke_test.py --url https://your-backend-url.railway.app --verbose
```

Expected output:
```
✓ PASS Root Endpoint
✓ PASS Health Check
✓ PASS API Documentation
✓ PASS Database Connectivity
✓ PASS Cache Connectivity
✓ PASS Metrics Endpoint
✓ PASS CORS Headers
✓ PASS Security Headers
✓ PASS Response Time
✓ PASS SSL Certificate

✅ ALL SMOKE TESTS PASSED
```

## Step 6: Setup Monitoring (Optional - 5 minutes)

```bash
./scripts/setup_monitoring.sh
```

## Done! 🎉

Your platform is now live at:
- **Frontend:** https://your-project.vercel.app
- **Backend:** https://your-backend-url.railway.app
- **API Docs:** https://your-backend-url.railway.app/api/v1/docs

## Next Steps

### Immediate
- [ ] Test user registration
- [ ] Test login
- [ ] Check Sentry for errors
- [ ] Monitor for first hour

### Short-term
- [ ] Configure custom domain
- [ ] Set up SSL with Cloudflare
- [ ] Import Grafana dashboards
- [ ] Set up Slack alerts
- [ ] Test rollback procedure

### Ongoing
- [ ] Monitor error rates
- [ ] Review performance metrics
- [ ] Keep dependencies updated
- [ ] Regular security audits

## Common Issues

### "Database connection failed"
```bash
# Check DATABASE_URL format
echo $DATABASE_URL

# Test connection
psql $DATABASE_URL -c "SELECT 1;"

# Verify Supabase firewall allows Railway IPs
```

### "Railway deployment failed"
```bash
# Check logs
railway logs

# Common issues:
# - Missing environment variables
# - Invalid requirements.txt
# - Port not set to $PORT
```

### "Smoke tests failing"
```bash
# Check if backend is running
curl https://your-backend-url.railway.app/health

# Check Railway logs
railway logs

# Verify environment variables
railway variables
```

## Troubleshooting

For detailed troubleshooting, see:
- [DEPLOYMENT_GUIDE.md](./DEPLOYMENT_GUIDE.md) - Complete guide
- [monitoring/README.md](./monitoring/README.md) - Monitoring setup
- [scripts/README.md](./scripts/README.md) - Script documentation

## Cost Estimate

Starting cost: **$5-20/month**
- Railway: $5+ (usage-based)
- Vercel: $0 (hobby plan)
- Supabase: $0 (free tier)
- Redis Cloud: $0 (free tier)
- Sentry: $0 (free tier)

## Support

Need help?
1. Check [DEPLOYMENT_GUIDE.md](./DEPLOYMENT_GUIDE.md)
2. Review error logs
3. Search GitHub issues
4. Open new issue with details

## Alternative: Automated Deployment

Use the interactive wizard:

```bash
./scripts/quick_deploy.sh
```

This will guide you through:
1. ✓ Checking prerequisites
2. ✓ Setting up environment
3. ✓ Generating secrets
4. ✓ Deploying backend
5. ✓ Running migrations
6. ✓ Deploying frontend
7. ✓ Setting up monitoring
8. ✓ Running smoke tests

---

**Time to production: ~30 minutes**

Ready to deploy? Let's go! 🚀
