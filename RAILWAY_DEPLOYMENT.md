# Railway Deployment - Step-by-Step Guide

**Platform**: Railway
**Time**: 5-10 minutes
**Cost**: $5/month (includes $5 credit)
**Difficulty**: ⭐ Very Easy

---

## ✅ Pre-Deployment Check

First, verify everything is ready:

```bash
cd /mnt/e/projects/quant/quant/backend
python3 scripts/pre_deployment_check.py
```

**Expected**: "🎉 DEPLOYMENT READY! All critical checks passed."

---

## 🚀 Option 1: Automated Deployment Script (Recommended)

### Step 1: Run Deployment Script

```bash
cd /mnt/e/projects/quant
./deploy.sh
```

### Step 2: Select Railway

When prompted, enter **1** for Railway.

### Step 3: Follow the Prompts

The script will:
- Check for Railway CLI (install if needed)
- Open browser for authentication
- Guide you through project setup
- Configure database and environment
- Deploy automatically

---

## 🛠️ Option 2: Manual Railway Deployment

If the automated script has issues, follow these manual steps:

### Step 1: Install Railway CLI

**On macOS/Linux**:
```bash
npm install -g @railway/cli
```

**Or with Homebrew**:
```bash
brew install railway
```

**On Windows (WSL)**:
```bash
npm install -g @railway/cli
```

### Step 2: Verify Installation

```bash
railway --version
```

Should show: `railway version X.X.X`

### Step 3: Login to Railway

```bash
railway login
```

This will:
1. Open your browser
2. Prompt you to sign in (or create account)
3. Use GitHub, Google, or Email
4. Return to terminal when complete

**First time?** You'll get $5 free credit!

### Step 4: Initialize Project

```bash
cd /mnt/e/projects/quant
railway init
```

You'll be prompted:
- **Create new project or use existing?** → Create new
- **Project name**: `quant-trading-platform` (or your choice)

### Step 5: Add PostgreSQL Database

```bash
railway add
```

Select: **PostgreSQL**

This creates a managed PostgreSQL database and sets `DATABASE_URL` automatically.

### Step 6: Set Environment Variables

Generate a secure secret key:
```bash
python3 -c "import secrets; print(secrets.token_urlsafe(32))"
```

Copy the output, then:
```bash
railway variables set ENVIRONMENT=production
railway variables set DEBUG=false
railway variables set SECRET_KEY=<paste-your-secret-key-here>
```

**Optional** - Add Sentry for monitoring:
```bash
railway variables set SENTRY_DSN=your-sentry-dsn
```

### Step 7: Deploy Application

```bash
railway up
```

This will:
- Upload your code
- Install dependencies from requirements.txt
- Run database migrations
- Start the application

**Wait time**: 2-3 minutes for first deployment.

### Step 8: Get Your Domain

```bash
railway domain
```

This assigns a public URL like: `https://quant-trading-platform.railway.app`

**Want a custom domain?**
```bash
railway domain add yourdomain.com
```

Then add DNS records as instructed.

---

## ✅ Post-Deployment Verification

### Step 1: Test Health Endpoint

```bash
# Replace with your actual URL
curl https://your-app.railway.app/health
```

**Expected**: `{"status":"healthy","service":"quant-trading-platform"}`

### Step 2: Check API Documentation

Open in browser:
```
https://your-app.railway.app/api/v1/docs
```

You should see the Swagger UI with all 43+ endpoints.

### Step 3: Test Public Endpoint

```bash
curl https://your-app.railway.app/api/v1/market-data/public/quote/AAPL
```

Should return stock data for Apple.

### Step 4: Run Verification Script

```bash
cd /mnt/e/projects/quant/quant/backend
python3 scripts/verify_deployment.py https://your-app.railway.app
```

**Expected**: "🎉 ALL TESTS PASSED! Deployment is healthy."

---

## 📊 Railway Dashboard

### View Your Deployment

1. Go to: https://railway.app/dashboard
2. Click on your project
3. View:
   - Deployment status
   - Logs
   - Metrics
   - Database
   - Environment variables

### Check Logs

In terminal:
```bash
railway logs
```

Or in dashboard: Click project → Deployments → View Logs

### Monitor Resources

Dashboard shows:
- CPU usage
- Memory usage
- Network traffic
- Database size

---

## 🔧 Common Configuration

### Environment Variables You May Want

**Monitoring** (optional):
```bash
railway variables set SENTRY_DSN=your-sentry-dsn
railway variables set SENTRY_ENVIRONMENT=production
```

**Email** (optional):
```bash
railway variables set SMTP_HOST=smtp.gmail.com
railway variables set SMTP_PORT=587
railway variables set SMTP_USER=your-email@gmail.com
railway variables set SMTP_PASSWORD=your-app-password
```

**API Keys** (optional - free tiers):
```bash
railway variables set ALPHA_VANTAGE_API_KEY=your-key
railway variables set FINNHUB_API_KEY=your-key
```

### View All Variables

```bash
railway variables
```

### Update a Variable

```bash
railway variables set KEY=new-value
```

Variables update automatically - no redeployment needed.

---

## 🔄 Deploying Updates

After making code changes:

```bash
# Commit changes
git add .
git commit -m "Your changes"
git push origin main

# Deploy to Railway
railway up
```

Or enable **auto-deploy**:
1. Railway Dashboard → Project → Settings
2. Connect GitHub repository
3. Enable "Deploy on Push"
4. Now `git push` automatically deploys!

---

## 💰 Billing & Cost

### Free Credit
- New accounts: $5 free credit
- Lasts ~1 month with basic usage

### Pricing After Free Credit
- **Developer Plan**: $5/month
- Includes:
  - Unlimited projects
  - 500 GB bandwidth
  - 8 GB RAM
  - PostgreSQL database
  - Custom domains

### Monitor Usage
Dashboard → Usage → See current usage

### Set Budget Alert
Dashboard → Settings → Billing → Set limit

---

## 🐛 Troubleshooting

### Issue: "railway: command not found"

**Solution**:
```bash
npm install -g @railway/cli
# or
brew install railway
```

### Issue: Login fails

**Solution**:
- Check your internet connection
- Try: `railway logout` then `railway login`
- Clear browser cache and retry

### Issue: Database connection error

**Solution**:
```bash
# Check DATABASE_URL is set
railway variables

# Restart the deployment
railway up --detach
```

### Issue: Build fails

**Solution**:
```bash
# Check logs
railway logs

# Common causes:
# - Missing dependency in requirements.txt
# - Python version mismatch (check runtime.txt)
# - Database migration error (check alembic)
```

### Issue: App not responding

**Solution**:
```bash
# Check deployment status
railway status

# View logs
railway logs --tail 100

# Restart
railway up --detach
```

### Issue: 500 errors

**Solution**:
```bash
# Check logs for errors
railway logs | grep ERROR

# Verify environment variables
railway variables

# Check Sentry (if configured) for detailed errors
```

---

## 📈 Performance Optimization

### Enable Redis (Optional)

For better caching:
```bash
railway add
# Select: Redis
```

Then set:
```bash
railway variables set REDIS_URL=$(railway variables get REDIS_URL)
```

### Scale Up (If Needed)

Dashboard → Project → Settings → Resources
- Increase memory (if seeing OOM errors)
- Increase CPU (if seeing slow responses)

---

## 🔐 Security Checklist

After deployment:

- [ ] SECRET_KEY is unique and secure
- [ ] DEBUG is set to false
- [ ] DATABASE_URL is using SSL
- [ ] HTTPS is enabled (automatic on Railway)
- [ ] Environment variables are not committed to git
- [ ] Monitoring is set up (Sentry)
- [ ] Backups are enabled (automatic for PostgreSQL)

---

## 🎯 Quick Reference

### Essential Commands

```bash
# Login
railway login

# Deploy
railway up

# View logs
railway logs

# View variables
railway variables

# Get domain
railway domain

# Project status
railway status

# Open in browser
railway open
```

### Important URLs

- **Dashboard**: https://railway.app/dashboard
- **Docs**: https://docs.railway.app
- **Status**: https://status.railway.app
- **Discord**: https://discord.gg/railway

---

## ✅ Deployment Checklist

- [ ] Railway CLI installed
- [ ] Logged in to Railway
- [ ] Project initialized
- [ ] PostgreSQL database added
- [ ] Environment variables set (ENVIRONMENT, DEBUG, SECRET_KEY)
- [ ] Application deployed (railway up)
- [ ] Domain assigned
- [ ] Health check passed
- [ ] API docs accessible
- [ ] Verification script passed
- [ ] Logs reviewed (no errors)
- [ ] Monitoring configured (optional)

---

## 🎉 Success!

Once all steps are complete, you'll have:

✅ Live API at: `https://your-app.railway.app`
✅ API Docs at: `https://your-app.railway.app/api/v1/docs`
✅ Managed PostgreSQL database
✅ Automatic HTTPS
✅ Auto-scaling
✅ 99.9% uptime SLA

**Cost**: $5/month (after free credit)

---

## 📞 Need Help?

### Railway Support
- **Discord**: https://discord.gg/railway
- **Docs**: https://docs.railway.app
- **Twitter**: @Railway

### Project Documentation
- **DEPLOYMENT_READY.md** - Quick checklist
- **FINAL_STATUS.md** - Project summary
- **API_DOCUMENTATION.md** - API reference

---

## 🚀 Next Steps After Deployment

1. **Set up monitoring**
   - Create Sentry account (free tier)
   - Add SENTRY_DSN to Railway variables

2. **Configure custom domain** (optional)
   - Purchase domain
   - Add to Railway: `railway domain add yourdomain.com`
   - Update DNS records

3. **Enable backups** (automatic on Railway)
   - Dashboard → Database → Backups
   - Verify daily backups are running

4. **Monitor performance**
   - Check Dashboard → Metrics
   - Set up alerts for errors/downtime
   - Review logs regularly

5. **Test premium features**
   - Create test user
   - Test premium endpoints
   - Verify analytics work

---

**Ready to deploy?** Run `./deploy.sh` and select option 1 (Railway)!

---

*Last Updated: January 26, 2026*
*Deployment Time: 5-10 minutes*
*Cost: $5/month*
