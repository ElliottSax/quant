# Deployment Guide - Quant Analytics Platform

Complete guide for deploying the Quant Analytics Platform to production.

## Table of Contents

- [Prerequisites](#prerequisites)
- [Hosting Options](#hosting-options)
- [Environment Setup](#environment-setup)
- [Deployment Steps](#deployment-steps)
- [Post-Deployment](#post-deployment)
- [Rollback Procedures](#rollback-procedures)
- [Troubleshooting](#troubleshooting)

## Prerequisites

Before deploying, ensure you have:

### Required Tools
- [x] Git installed
- [x] Python 3.11+ installed
- [x] Node.js 18+ installed
- [x] Railway CLI: `npm i -g @railway/cli`
- [x] Vercel CLI: `npm i -g vercel`

### Required Accounts
- [x] GitHub account (for code repository)
- [x] Railway account (backend hosting) - https://railway.app
- [x] Vercel account (frontend hosting) - https://vercel.com
- [x] Supabase account (database) - https://supabase.com
- [x] Sentry account (error tracking) - https://sentry.io
- [x] Cloudflare account (DNS/SSL) - https://cloudflare.com

### API Keys Needed
- [x] Polygon.io API key (market data)
- [x] Alpha Vantage API key (market data)
- [x] SendGrid API key (emails)
- [x] Slack webhook URL (alerts)

## Hosting Options

### Recommended: Managed Services (Easiest)

**Best for:** Quick deployment, minimal DevOps

| Service | Purpose | Cost |
|---------|---------|------|
| Railway | Backend API + Celery | $5-20/month |
| Vercel | Frontend (Next.js) | Free - $20/month |
| Supabase | PostgreSQL + Auth | Free - $25/month |
| Redis Cloud | Cache + Queue | Free - $7/month |

**Total:** ~$10-70/month depending on usage

### Alternative: Self-Hosted (More Control)

**Best for:** Cost optimization, full control

| Service | Purpose | Cost |
|---------|---------|------|
| DigitalOcean Droplet | All services | $12-48/month |
| Hetzner Cloud | All services | €5-20/month |
| AWS Lightsail | All services | $10-40/month |

## Environment Setup

### 1. Database Setup (Supabase)

1. Create new project at [supabase.com](https://supabase.com)

2. Enable TimescaleDB extension:
   ```sql
   CREATE EXTENSION IF NOT EXISTS timescaledb CASCADE;
   ```

3. Get connection details:
   - Go to Settings → Database
   - Copy connection string
   - Note down the direct connection URI

4. Update `.env.production`:
   ```env
   DATABASE_URL=postgresql://postgres:[PASSWORD]@db.[PROJECT].supabase.co:5432/postgres
   SUPABASE_URL=https://[PROJECT].supabase.co
   SUPABASE_ANON_KEY=[YOUR_KEY]
   SUPABASE_SERVICE_KEY=[YOUR_KEY]
   ```

### 2. Redis Setup (Railway)

1. Go to Railway dashboard
2. Click "New Project" → "Provision Redis"
3. Copy connection string
4. Update `.env.production`:
   ```env
   REDIS_URL=redis://default:[PASSWORD]@[HOST]:[PORT]
   ```

### 3. Sentry Setup (Error Tracking)

1. Create account at [sentry.io](https://sentry.io)
2. Create new project (Python/FastAPI)
3. Copy DSN (Data Source Name)
4. Update `.env.production`:
   ```env
   SENTRY_DSN=https://[KEY]@o[ORG].ingest.sentry.io/[PROJECT]
   SENTRY_ENVIRONMENT=production
   ```

### 4. Secret Keys Generation

Generate secure keys:

```bash
# SECRET_KEY (64 chars)
python -c "import secrets; print(secrets.token_urlsafe(64))"

# JWT_SECRET_KEY (64 chars)
python -c "import secrets; print(secrets.token_urlsafe(64))"
```

Update `.env.production` with generated keys.

### 5. Email Setup (SendGrid)

1. Create account at [sendgrid.com](https://sendgrid.com)
2. Create API key (Settings → API Keys)
3. Verify sender domain (Settings → Sender Authentication)
4. Update `.env.production`:
   ```env
   SENDGRID_API_KEY=SG.[YOUR_KEY]
   EMAIL_FROM=noreply@yourdomain.com
   ```

## Deployment Steps

### Step 1: Prepare Code

```bash
# Clone repository
git clone https://github.com/yourorg/quant.git
cd quant

# Install dependencies
cd backend
pip install -r requirements.production.txt

cd ../frontend
npm install
```

### Step 2: Configure Environment Variables

```bash
# Copy production template
cp .env.example .env.production

# Edit with your values
nano .env.production

# IMPORTANT: Never commit this file!
# It's already in .gitignore
```

### Step 3: Deploy Backend to Railway

#### Option A: Using Railway CLI

```bash
# Login to Railway
railway login

# Link to project (or create new)
railway link

# Set environment to production
railway environment production

# Upload environment variables
railway variables --environment production < .env.production

# Deploy backend
cd backend
railway up

# Check deployment status
railway status

# View logs
railway logs
```

#### Option B: Using Railway Dashboard

1. Go to [railway.app/dashboard](https://railway.app/dashboard)
2. Click "New Project" → "Deploy from GitHub"
3. Select your repository
4. Choose "backend" directory
5. Add environment variables from `.env.production`
6. Click "Deploy"

### Step 4: Run Database Migrations

```bash
# Set database URL
export DATABASE_URL="your-production-database-url"

# Run migrations
cd backend
alembic upgrade head

# Verify
alembic current
```

### Step 5: Deploy Frontend to Vercel

#### Option A: Using Vercel CLI

```bash
# Login to Vercel
vercel login

# Deploy
cd frontend
vercel --prod

# Set environment variables
vercel env add NEXT_PUBLIC_API_URL production
vercel env add NEXT_PUBLIC_SUPABASE_URL production
vercel env add NEXT_PUBLIC_SUPABASE_ANON_KEY production

# Redeploy with env vars
vercel --prod
```

#### Option B: Using Vercel Dashboard

1. Go to [vercel.com](https://vercel.com)
2. Click "Add New" → "Project"
3. Import from GitHub
4. Select "frontend" directory
5. Add environment variables
6. Click "Deploy"

### Step 6: Configure Domain & SSL

#### Using Cloudflare (Recommended)

1. Add domain to Cloudflare
2. Update nameservers at registrar
3. Add DNS records:
   ```
   A     @              [Vercel IP]
   A     www            [Vercel IP]
   CNAME api            [Railway URL]
   CNAME grafana        [Grafana URL]
   ```
4. Enable SSL (Flexible or Full)
5. Update CORS origins in `.env.production`

### Step 7: Set Up CI/CD

#### GitHub Secrets

Add these secrets to your GitHub repository:

Settings → Secrets → Actions → New repository secret

```
RAILWAY_TOKEN              # From Railway settings
VERCEL_TOKEN               # From Vercel settings
VERCEL_ORG_ID             # From Vercel settings
VERCEL_PROJECT_ID         # From Vercel settings
PRODUCTION_DATABASE_URL   # Your database URL
PRODUCTION_API_URL        # Your API URL
PRODUCTION_FRONTEND_URL   # Your frontend URL
SLACK_WEBHOOK_URL         # Your Slack webhook
CODECOV_TOKEN             # Optional: for coverage
```

#### Enable Workflows

The workflows are already configured in `.github/workflows/`:
- `test.yml` - Runs on every PR
- `deploy-production.yml` - Runs on push to main
- `database-migration.yml` - Manual trigger

They will run automatically when code is pushed.

### Step 8: Configure Monitoring

#### Prometheus + Grafana

See [monitoring/README.md](./monitoring/README.md) for detailed setup.

Quick setup:
```bash
# Using Docker Compose
docker-compose -f docker-compose.production.yml up -d prometheus grafana

# Or use Grafana Cloud (recommended)
# 1. Sign up at grafana.com
# 2. Add Prometheus data source
# 3. Import dashboards from monitoring/grafana/dashboards/
```

#### Alerting

1. Configure Slack webhook in `.env.production`
2. Test alerts:
   ```bash
   curl -X POST $SLACK_WEBHOOK_URL \
     -H 'Content-Type: application/json' \
     -d '{"text":"Test alert from Quant Platform"}'
   ```
3. Verify alert rules in Prometheus

## Post-Deployment

### Smoke Tests

Run automated smoke tests:

```bash
python scripts/smoke_test.py --url https://api.yourdomain.com --verbose
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

### Manual Testing Checklist

- [ ] Visit https://yourdomain.com
- [ ] Create test account
- [ ] Login successfully
- [ ] View dashboard
- [ ] Check API docs: https://api.yourdomain.com/api/v1/docs
- [ ] Test search functionality
- [ ] Verify data is loading
- [ ] Check mobile responsiveness
- [ ] Test logout

### Monitoring Setup

- [ ] Verify Sentry is receiving events
- [ ] Check Grafana dashboards are populated
- [ ] Confirm Prometheus is scraping metrics
- [ ] Test alert notifications
- [ ] Review application logs

### Performance Optimization

```bash
# Enable production optimizations
# Already configured in .env.production

# Verify settings
curl https://api.yourdomain.com/health | jq .

# Check response times
curl -w "@curl-format.txt" -o /dev/null -s https://api.yourdomain.com/
```

### Security Checklist

- [ ] SSL/TLS enabled (A+ rating on SSL Labs)
- [ ] Security headers configured
- [ ] CORS properly restricted
- [ ] Rate limiting enabled
- [ ] Secrets rotated from defaults
- [ ] Database credentials secured
- [ ] API keys in environment variables (not code)
- [ ] Admin endpoints protected
- [ ] Error messages don't leak sensitive info

## Rollback Procedures

### Automatic Rollback (Railway)

Railway automatically keeps previous deployments:

```bash
# List recent deployments
railway deployments

# Rollback to previous
railway rollback
```

### Manual Rollback

```bash
# Using the rollback script
./scripts/rollback.sh production deploy-production-20240115-143000

# Or manually
git checkout [TAG]
railway up --environment production
python scripts/smoke_test.py --url https://api.yourdomain.com
```

### Database Rollback

```bash
# Show current revision
alembic current

# Show migration history
alembic history

# Downgrade to specific revision
alembic downgrade [REVISION]

# Downgrade one step
alembic downgrade -1
```

### Emergency Rollback Procedure

If something goes critically wrong:

1. **Immediate Actions** (< 5 minutes)
   ```bash
   # Rollback application
   railway rollback --environment production

   # Notify team
   curl -X POST $SLACK_WEBHOOK_URL \
     -d '{"text":"🚨 EMERGENCY ROLLBACK IN PROGRESS"}'
   ```

2. **Stabilization** (< 15 minutes)
   ```bash
   # Check health
   python scripts/smoke_test.py --url https://api.yourdomain.com

   # Review logs
   railway logs --environment production

   # Check Sentry for errors
   open https://sentry.io/organizations/yourorg/issues/
   ```

3. **Post-Mortem** (< 24 hours)
   - Document what went wrong
   - Identify root cause
   - Create prevention plan
   - Update deployment checklist

## Troubleshooting

### Deployment Fails

**Error: "Railway deployment failed"**

```bash
# Check logs
railway logs --environment production

# Common issues:
# 1. Build error - check requirements.txt
# 2. Missing env var - check railway variables
# 3. Port conflict - ensure using $PORT

# Fix and redeploy
railway up --environment production
```

**Error: "Database connection failed"**

```bash
# Test connection
psql $DATABASE_URL

# Check firewall rules
# Supabase: Settings → Database → Connection Pooling

# Verify DATABASE_URL format
echo $DATABASE_URL
```

### Application Not Responding

```bash
# Check if service is running
railway status

# View recent logs
railway logs --tail 100

# Check health endpoint
curl https://api.yourdomain.com/health

# Restart service
railway restart
```

### High Error Rate

```bash
# Check Sentry
open https://sentry.io

# Check logs
railway logs --environment production | grep ERROR

# Check Prometheus alerts
open http://your-prometheus-url:9090/alerts

# Check database
psql $DATABASE_URL -c "SELECT version();"
```

### Slow Performance

```bash
# Check response times
curl -w "@curl-format.txt" -o /dev/null -s https://api.yourdomain.com/

# Check database queries
# In Grafana, view "Database Performance" dashboard

# Check Redis
redis-cli -u $REDIS_URL ping

# Scale up if needed
# Railway: Settings → Resources → Increase
```

### SSL Certificate Issues

```bash
# Check SSL status
curl -vI https://api.yourdomain.com 2>&1 | grep -i ssl

# Test with SSL Labs
open https://www.ssllabs.com/ssltest/analyze.html?d=yourdomain.com

# Cloudflare: Ensure SSL mode is "Full"
# Vercel: SSL is automatic

# Force HTTPS redirect (if needed)
# Already configured in middleware
```

### Database Migration Failed

```bash
# Check current state
alembic current

# View migration history
alembic history

# Try manual migration
alembic upgrade head --sql > migration.sql
psql $DATABASE_URL -f migration.sql

# If stuck, stamp current version
alembic stamp head
```

## Production Checklist

Before marking deployment complete:

### Pre-Deployment
- [ ] All tests passing
- [ ] Code reviewed and approved
- [ ] Environment variables configured
- [ ] Database backed up
- [ ] Maintenance window scheduled
- [ ] Team notified
- [ ] Rollback plan ready

### During Deployment
- [ ] Backend deployed successfully
- [ ] Frontend deployed successfully
- [ ] Database migrations applied
- [ ] Smoke tests passed
- [ ] No errors in Sentry
- [ ] Metrics flowing to Prometheus

### Post-Deployment
- [ ] All services healthy
- [ ] Key features working
- [ ] Performance acceptable
- [ ] No spike in errors
- [ ] Monitoring configured
- [ ] Alerts working
- [ ] Documentation updated
- [ ] Team notified of completion

## Best Practices

1. **Always Deploy During Low Traffic**
   - Best: Late night or early morning
   - Avoid: Business hours or high-traffic times

2. **Deploy Small Changes**
   - Easier to debug if something breaks
   - Faster rollback if needed
   - Less risk overall

3. **Monitor After Deployment**
   - Watch for 15-30 minutes
   - Check error rates
   - Verify key functionality
   - Review user feedback

4. **Use Feature Flags**
   - Deploy code but keep features off
   - Gradually enable for users
   - Quick disable if issues

5. **Automate Everything**
   - Use CI/CD pipelines
   - Automated tests
   - Automated rollback
   - Reduce human error

6. **Have a Buddy**
   - Never deploy alone
   - Someone to help if issues
   - Fresh eyes on problems
   - Faster resolution

## Resources

- [Railway Documentation](https://docs.railway.app)
- [Vercel Documentation](https://vercel.com/docs)
- [Supabase Documentation](https://supabase.com/docs)
- [Sentry Documentation](https://docs.sentry.io)
- [FastAPI Deployment](https://fastapi.tiangolo.com/deployment/)
- [Next.js Deployment](https://nextjs.org/docs/deployment)

## Support

For deployment issues:
1. Check this guide first
2. Review error logs
3. Search GitHub issues
4. Contact DevOps team
5. Create incident ticket

---

**Last Updated:** 2024-01-15

**Maintainers:** DevOps Team

**Questions?** Open an issue or contact support@yourdomain.com
