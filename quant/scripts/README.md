# Deployment Scripts

This directory contains automated scripts for deploying and managing the Quant Analytics Platform in production.

## Scripts Overview

### 🚀 Deployment Scripts

#### `quick_deploy.sh` - Interactive Deployment Wizard
First-time deployment helper with step-by-step guidance.

```bash
./scripts/quick_deploy.sh
```

**Features:**
- Checks prerequisites
- Guides through service setup
- Generates secret keys
- Deploys backend and frontend
- Sets up monitoring
- Runs smoke tests

**Use when:** First deployment or setting up new environment

---

#### `deploy.sh` - Automated Production Deployment
Fully automated deployment with pre-flight checks.

```bash
# Deploy to production
./scripts/deploy.sh production

# Deploy to staging
./scripts/deploy.sh staging
```

**What it does:**
1. Validates environment and credentials
2. Runs all tests
3. Checks database migrations
4. Deploys to Railway
5. Runs database migrations
6. Executes smoke tests
7. Creates git tag
8. Sends Slack notification

**Use when:** Regular deployments after initial setup

---

### 🔄 Rollback Scripts

#### `rollback.sh` - Emergency Rollback
Rolls back to a previous deployment.

```bash
# Interactive - shows recent tags
./scripts/rollback.sh production

# Rollback to specific tag
./scripts/rollback.sh production deploy-production-20240115-120000
```

**What it does:**
1. Creates backup of current state
2. Checks out target version
3. Rolls back Railway deployment
4. Optionally rolls back database
5. Runs smoke tests
6. Creates rollback tag

**Use when:** Deployment issues or critical bugs

---

### 📊 Monitoring Scripts

#### `setup_monitoring.sh` - Monitoring Stack Setup
Sets up and tests monitoring services.

```bash
./scripts/setup_monitoring.sh
```

**What it does:**
1. Validates Sentry configuration
2. Starts Prometheus
3. Starts Grafana
4. Tests alert webhooks
5. Creates health check script
6. Generates dashboard URLs

**Use when:** Initial setup or monitoring troubleshooting

---

### 🧪 Testing Scripts

#### `smoke_test.py` - Production Health Tests
Comprehensive smoke tests for deployed application.

```bash
# Basic tests
python scripts/smoke_test.py --url https://api.yourdomain.com

# Verbose output
python scripts/smoke_test.py --url https://api.yourdomain.com --verbose

# Test local development
python scripts/smoke_test.py --url http://localhost:8000
```

**Tests performed:**
- ✓ Root endpoint accessibility
- ✓ Health check with service status
- ✓ API documentation availability
- ✓ Database connectivity
- ✓ Redis cache connectivity
- ✓ Metrics endpoint
- ✓ CORS headers
- ✓ Security headers
- ✓ Response time (<2s)
- ✓ SSL certificate (HTTPS)

**Exit codes:**
- `0` - All tests passed
- `1` - One or more tests failed

**Use when:** After deployment, in CI/CD, troubleshooting

---

## Quick Reference

### First Time Deployment

```bash
# 1. Interactive wizard (recommended for first time)
./scripts/quick_deploy.sh

# OR manual steps:

# 2. Set up environment
cp .env.example .env.production
# Edit .env.production with your values

# 3. Deploy
./scripts/deploy.sh production

# 4. Verify
python scripts/smoke_test.py --url https://api.yourdomain.com
```

### Regular Deployment

```bash
# After code changes
git add .
git commit -m "feat: your changes"
git push

# Deploy to production
./scripts/deploy.sh production
```

### Emergency Rollback

```bash
# Rollback to previous version
./scripts/rollback.sh production

# Or to specific tag
./scripts/rollback.sh production deploy-production-20240115-120000
```

### Health Check

```bash
# Quick health check
python scripts/smoke_test.py --url https://api.yourdomain.com

# Detailed health check
python scripts/smoke_test.py --url https://api.yourdomain.com --verbose
```

## Prerequisites

### Required Tools
- Bash (for shell scripts)
- Python 3.11+ (for smoke tests)
- Railway CLI: `npm i -g @railway/cli`
- Vercel CLI: `npm i -g vercel`
- Git

### Required Python Packages
```bash
pip install requests
```

### Make Scripts Executable

```bash
chmod +x scripts/*.sh
```

## Environment Variables

All deployment scripts read from `.env.production`:

### Critical Variables
```env
# Railway
RAILWAY_TOKEN=your-railway-token

# Production URLs
PRODUCTION_API_URL=https://api.yourdomain.com
PRODUCTION_FRONTEND_URL=https://yourdomain.com
PRODUCTION_DATABASE_URL=postgresql://...

# Monitoring
SENTRY_DSN=https://...
SLACK_WEBHOOK_URL=https://hooks.slack.com/...
```

## Script Features

### Error Handling
All scripts include:
- Pre-flight checks
- Validation of prerequisites
- Error detection and reporting
- Automatic cleanup on failure
- Colored output for clarity

### Safety Features
- Production deployments require confirmation
- Automatic backups before changes
- Rollback on failure
- Smoke tests after deployment
- Git tagging for version tracking

### Logging
- Colored terminal output
- Detailed error messages
- Progress indicators
- Success/failure notifications

## Troubleshooting

### Script Won't Run
```bash
# Make executable
chmod +x scripts/script-name.sh

# Check for line endings (Windows)
dos2unix scripts/script-name.sh
```

### Railway CLI Not Found
```bash
npm i -g @railway/cli
railway login
```

### Smoke Tests Failing
```bash
# Check if API is up
curl https://api.yourdomain.com/health

# Check Railway logs
railway logs --environment production

# Run with verbose output
python scripts/smoke_test.py --url https://api.yourdomain.com --verbose
```

### Deployment Failing
```bash
# Check Railway status
railway status

# View logs
railway logs --tail 100

# Verify environment variables
railway variables --environment production
```

## Best Practices

### Before Deployment
1. Run tests locally: `pytest`
2. Review changes: `git diff`
3. Update changelog
4. Notify team of deployment window

### During Deployment
1. Use `deploy.sh` for consistency
2. Monitor logs in real-time
3. Keep Slack/email open for alerts
4. Have rollback plan ready

### After Deployment
1. Run smoke tests immediately
2. Monitor for 15-30 minutes
3. Check Sentry for errors
4. Review Grafana dashboards
5. Test critical user flows

### Never Do This
- ❌ Deploy on Friday evening
- ❌ Deploy without testing
- ❌ Deploy without backup
- ❌ Skip smoke tests
- ❌ Deploy when tired
- ❌ Deploy alone (have someone on standby)

## CI/CD Integration

These scripts are designed to work with GitHub Actions:

```yaml
# .github/workflows/deploy-production.yml
- name: Run smoke tests
  run: python scripts/smoke_test.py --url ${{ secrets.PRODUCTION_API_URL }}

# .github/workflows/deploy-production.yml
- name: Deploy to production
  run: ./scripts/deploy.sh production
```

## Customization

### Adding Custom Checks

Edit `smoke_test.py` to add new tests:

```python
def test_custom_endpoint(session, base_url, verbose):
    """Test custom functionality."""
    response = session.get(f"{base_url}/api/v1/custom")
    if response.status_code != 200:
        return False, f"Status: {response.status_code}"
    return True, "Custom test passed"

# Add to tests list in run_all_tests()
```

### Adding Custom Deployment Steps

Edit `deploy.sh` to add steps:

```bash
# Add before deployment
log_info "Running custom pre-deployment tasks..."
# Your commands here

# Add after deployment
log_info "Running custom post-deployment tasks..."
# Your commands here
```

## Getting Help

If scripts aren't working:

1. Check this README
2. Review script output carefully
3. Check environment variables
4. Review Railway/Vercel logs
5. See DEPLOYMENT_GUIDE.md
6. Open GitHub issue

## Contributing

When adding new scripts:

1. Follow existing naming conventions
2. Add proper error handling
3. Include colored output
4. Add to this README
5. Test thoroughly before committing

---

**Last Updated:** 2024-01-15
**Maintainer:** DevOps Team
