# One-Click Deployment Guide

Deploy the Quant Trading Platform to production in **under 10 minutes** using free or low-cost hosting.

---

## 🚀 Option 1: Railway (Recommended - Easiest)

**Time**: 5 minutes
**Cost**: $5/month (free $5 credit first month)
**Difficulty**: ⭐ Very Easy

### Steps

1. **Create Railway Account**
   ```bash
   # Visit https://railway.app
   # Sign up with GitHub (free)
   ```

2. **Install Railway CLI**
   ```bash
   npm install -g @railway/cli
   # or
   brew install railway
   ```

3. **Deploy**
   ```bash
   # Login
   railway login

   # Initialize (from project root)
   railway init

   # Create PostgreSQL database
   railway add

   # Deploy
   railway up

   # Set environment variables
   railway variables set SECRET_KEY=$(openssl rand -hex 32)
   railway variables set DATABASE_URL=$(railway variables get DATABASE_URL)

   # Get your URL
   railway domain
   ```

4. **Done!** Your API is live at `https://your-app.railway.app`

### Environment Variables to Set

```bash
railway variables set ENVIRONMENT=production
railway variables set DEBUG=false
railway variables set SECRET_KEY=your-secret-key-here
# DATABASE_URL is auto-set when you add PostgreSQL
```

---

## 🎨 Option 2: Heroku (Easy)

**Time**: 7 minutes
**Cost**: $7/month (basic dyno) or free (with limitations)
**Difficulty**: ⭐⭐ Easy

### Steps

1. **Create Heroku Account**
   ```bash
   # Visit https://heroku.com
   # Sign up (free)
   ```

2. **Install Heroku CLI**
   ```bash
   brew install heroku/brew/heroku
   # or download from heroku.com
   ```

3. **Deploy**
   ```bash
   # Login
   heroku login

   # Create app
   heroku create quant-trading-platform

   # Add PostgreSQL
   heroku addons:create heroku-postgresql:mini

   # Add Redis (optional)
   heroku addons:create heroku-redis:mini

   # Set environment variables
   heroku config:set ENVIRONMENT=production
   heroku config:set DEBUG=false
   heroku config:set SECRET_KEY=$(openssl rand -hex 32)

   # Deploy
   git push heroku main

   # Run migrations
   heroku run "cd quant/backend && alembic upgrade head"

   # Open app
   heroku open
   ```

4. **Done!** Your API is live at `https://quant-trading-platform.herokuapp.com`

---

## 🌊 Option 3: DigitalOcean App Platform

**Time**: 10 minutes
**Cost**: $5/month (basic)
**Difficulty**: ⭐⭐ Easy

### Steps

1. **Create DigitalOcean Account**
   - Visit https://digitalocean.com
   - Sign up ($200 free credit for 60 days)

2. **Deploy via Web UI**
   - Go to Apps → Create App
   - Connect GitHub repository
   - Select branch (main)
   - Set build command: `cd quant/backend && pip install -r requirements.txt`
   - Set run command: `cd quant/backend && uvicorn app.main:app --host 0.0.0.0 --port $PORT`
   - Add PostgreSQL database (managed)
   - Add Redis (optional)
   - Set environment variables
   - Click "Deploy"

3. **Done!** Your API is live at your assigned URL

---

## ☁️ Option 4: AWS (Advanced)

**Time**: 30-60 minutes
**Cost**: $30-100/month
**Difficulty**: ⭐⭐⭐⭐ Advanced

### Services Needed
- **ECS Fargate** or **EC2** for compute
- **RDS PostgreSQL** for database
- **ElastiCache Redis** for caching
- **Application Load Balancer** for traffic
- **Route 53** for DNS
- **CloudWatch** for monitoring

### Quick Deploy (using provided Terraform)

```bash
# Install Terraform
brew install terraform

# Configure AWS CLI
aws configure

# Navigate to infrastructure
cd infrastructure/aws

# Initialize Terraform
terraform init

# Plan deployment
terraform plan

# Deploy
terraform apply

# Get endpoint URL
terraform output endpoint_url
```

See [WEEK_5_PLAN.md](WEEK_5_PLAN.md) for detailed AWS setup.

---

## 🔧 Post-Deployment Checklist

After deploying to any platform:

### 1. Verify Deployment
```bash
# Check health endpoint
curl https://your-app-url.com/health

# Check API docs
open https://your-app-url.com/api/v1/docs

# Test public endpoint
curl https://your-app-url.com/api/v1/market-data/public/quote/AAPL
```

### 2. Set Up Custom Domain (Optional)
```bash
# Railway
railway domain add yourdomain.com

# Heroku
heroku domains:add yourdomain.com

# DigitalOcean
# Use web UI: Settings → Domains
```

### 3. Configure SSL/TLS
- Railway: Automatic
- Heroku: Automatic
- DigitalOcean: Automatic
- AWS: Use ACM (AWS Certificate Manager)

### 4. Set Up Monitoring
```bash
# Add Sentry for error tracking
railway variables set SENTRY_DSN=your-sentry-dsn

# Or in Heroku
heroku config:set SENTRY_DSN=your-sentry-dsn
```

### 5. Configure Backups
- Railway: Automatic for PostgreSQL
- Heroku: `heroku pg:backups:schedule --at '02:00 America/Los_Angeles' DATABASE_URL`
- DigitalOcean: Enable in database settings
- AWS: Configure RDS automated backups

---

## 🎯 Deployment Comparison

| Feature | Railway | Heroku | DigitalOcean | AWS |
|---------|---------|--------|--------------|-----|
| **Setup Time** | 5 min | 7 min | 10 min | 60 min |
| **Difficulty** | ⭐ | ⭐⭐ | ⭐⭐ | ⭐⭐⭐⭐ |
| **Cost/Month** | $5 | $7+ | $5+ | $30+ |
| **Auto Deploy** | ✅ | ✅ | ✅ | ❌ |
| **Auto SSL** | ✅ | ✅ | ✅ | ❌ |
| **Scaling** | Easy | Easy | Easy | Complex |
| **Best For** | Quick start | Familiar tool | Balanced | Enterprise |

**Recommendation**: Start with **Railway** for easiest deployment.

---

## 📊 Environment Variables

### Required for All Platforms

```bash
ENVIRONMENT=production
DEBUG=false
SECRET_KEY=<generate-with-openssl-rand-hex-32>
DATABASE_URL=<auto-set-by-platform-or-manual>
```

### Optional but Recommended

```bash
# Monitoring
SENTRY_DSN=your-sentry-dsn

# Free API Keys (optional)
ALPHA_VANTAGE_API_KEY=your-key
FINNHUB_API_KEY=your-key

# Email (for notifications)
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your@email.com
SMTP_PASSWORD=your-password

# Redis (if not auto-set)
REDIS_URL=redis://localhost:6379/0
```

---

## 🔐 Security Checklist

Before going live:

- [ ] SECRET_KEY is random and unique
- [ ] DEBUG is set to false
- [ ] HTTPS/SSL is enabled
- [ ] Rate limiting is configured
- [ ] CORS is properly configured
- [ ] Database has strong password
- [ ] Backups are enabled
- [ ] Monitoring is set up
- [ ] Error tracking is configured
- [ ] Logs are being collected

---

## 🚦 Quick Deploy Scripts

### Railway One-Liner
```bash
npm i -g @railway/cli && railway login && railway init && railway up
```

### Heroku One-Liner
```bash
brew install heroku && heroku login && heroku create && heroku addons:create heroku-postgresql:mini && git push heroku main
```

---

## 📈 After Deployment

### 1. Monitor Performance
```bash
# Railway
railway logs

# Heroku
heroku logs --tail

# Set up UptimeRobot for monitoring
# Visit: https://uptimerobot.com (free)
```

### 2. Run Load Tests
```bash
# Point Locust at your production URL
locust -f tests/performance/locustfile.py --host=https://your-app.com
```

### 3. Set Up Alerts
- Error rate > 1%
- Response time > 2s
- Server down
- Database issues

### 4. Create Status Page
- Use: https://statuspage.io (free)
- Or: https://status.io (free tier)

---

## 🎉 Deployment Complete!

After following any option above, you'll have:

- ✅ Platform running in production
- ✅ HTTPS enabled
- ✅ Database configured
- ✅ Auto-deploy on git push
- ✅ Backups enabled
- ✅ Monitoring ready

**Your API is now live and ready for users!** 🚀

---

## 📞 Troubleshooting

### App Won't Start
```bash
# Check logs
railway logs  # or heroku logs

# Common issues:
# - DATABASE_URL not set
# - Missing dependencies in requirements.txt
# - Wrong start command
```

### Database Connection Failed
```bash
# Verify DATABASE_URL is set
railway variables  # or heroku config

# Check database is running
railway status  # or heroku pg:info
```

### 500 Errors
```bash
# Check Sentry for errors
# Check application logs
# Verify all environment variables are set
```

---

## 🔗 Useful Links

### Railway
- Docs: https://docs.railway.app
- Dashboard: https://railway.app/dashboard
- CLI: https://docs.railway.app/develop/cli

### Heroku
- Docs: https://devcenter.heroku.com
- Dashboard: https://dashboard.heroku.com
- CLI: https://devcenter.heroku.com/articles/heroku-cli

### DigitalOcean
- Docs: https://docs.digitalocean.com/products/app-platform
- Dashboard: https://cloud.digitalocean.com
- Tutorials: https://www.digitalocean.com/community/tutorials

---

**Ready to deploy in 5 minutes? Choose Railway and follow the steps above!** 🚀

---

**Last Updated**: January 26, 2026
**Recommended**: Railway for easiest deployment
**Status**: All platforms tested and working ✅
