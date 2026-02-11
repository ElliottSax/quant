# Migration Guide: TODO Implementations

This guide helps you migrate your existing quant platform to use the new features from Task #8.

---

## 🚀 Quick Migration (5 Minutes)

### 1. Update Environment Variables

Add to your `.env` file:

```env
# Email Configuration (Choose one or both)
RESEND_API_KEY=                  # Get from https://resend.com
EMAIL_DOMAIN=yourdomain.com
ALERT_EMAIL=admin@example.com

# OR SMTP
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_TLS=true
SMTP_USER=your_email@gmail.com
SMTP_PASSWORD=your_app_password

# News APIs (Optional)
NEWSAPI_KEY=                     # Get from https://newsapi.org
ALPHA_VANTAGE_API_KEY=          # Get from https://alphavantage.co

# Alerting (Optional)
SLACK_WEBHOOK_URL=
ALERT_WEBHOOK_URL=
```

### 2. Run Database Migration

```bash
cd quant/backend
alembic upgrade head
```

### 3. Restart Application

```bash
# Development
uvicorn app.main:app --reload

# Production
systemctl restart quant-api
```

---

## 📊 Full Migration (30 Minutes)

### Step 1: Backup Database

```bash
# PostgreSQL
pg_dump quant_db > backup_before_migration.sql

# SQLite
cp quant_dev.db quant_dev.db.backup
```

### Step 2: Update Dependencies (if needed)

Check if you have all required packages:

```bash
cd quant/backend
pip install httpx  # For email and news APIs
```

### Step 3: Review Configuration

#### Option A: Resend (Recommended)

1. Sign up at https://resend.com
2. Add domain in dashboard
3. Get API key
4. Add to `.env`:
```env
RESEND_API_KEY=re_xxxxxxxxxxxx
EMAIL_DOMAIN=yourdomain.com
```

#### Option B: SMTP (Gmail)

1. Enable 2FA on Google account
2. Generate app password
3. Add to `.env`:
```env
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_TLS=true
SMTP_USER=your_email@gmail.com
SMTP_PASSWORD=your_16_char_app_password
```

#### Option C: SMTP (SendGrid)

```env
SMTP_HOST=smtp.sendgrid.net
SMTP_PORT=587
SMTP_USER=apikey
SMTP_PASSWORD=your_sendgrid_api_key
```

### Step 4: Run Migration

```bash
cd quant/backend

# Check current migration status
alembic current

# Show migration to be applied
alembic show add_api_keys_devices

# Apply migration
alembic upgrade head

# Verify tables created
alembic current
```

Expected output:
```
INFO  [alembic.runtime.migration] Running upgrade  -> add_api_keys_devices
```

### Step 5: Verify Database

```bash
# PostgreSQL
psql -d quant_db -c "\dt" | grep -E "api_keys|mobile_devices"

# Should show:
# api_keys
# mobile_devices
```

### Step 6: Test Email

```python
# Create test script: test_email.py
import asyncio
from app.services.email_service import email_service

async def test():
    result = await email_service.send_email(
        to_email="your_email@example.com",
        subject="Test Email - TODO Migration",
        html_body="<h1>Success!</h1><p>Email service is working.</p>",
        text_body="Success! Email service is working."
    )
    print(f"Email sent: {result}")

asyncio.run(test())
```

```bash
python test_email.py
```

### Step 7: Test API Key Creation

```python
# Create test script: test_api_key.py
import asyncio
from app.core.database import get_db
from app.services.api_key_manager import api_key_manager, APIKeyPermission

async def test():
    async for db in get_db():
        # Create test user first (replace with actual user ID)
        user_id = "your-test-user-uuid"

        key_id, secret = await api_key_manager.create_key(
            db=db,
            user_id=user_id,
            name="Test Migration Key",
            permissions=[APIKeyPermission.READ],
            expires_days=7
        )

        print(f"Created API key:")
        print(f"  Key ID: {key_id}")
        print(f"  Secret: {secret}")
        print(f"\nSave the secret - it won't be shown again!")

        # Test validation
        metadata = await api_key_manager.validate_key(db, secret)
        print(f"\nValidation: {'SUCCESS' if metadata else 'FAILED'}")

asyncio.run(test())
```

---

## 🔄 Rollback Plan

If something goes wrong:

### 1. Rollback Database

```bash
cd quant/backend
alembic downgrade -1
```

### 2. Restore from Backup

```bash
# PostgreSQL
psql quant_db < backup_before_migration.sql

# SQLite
cp quant_dev.db.backup quant_dev.db
```

### 3. Revert Code Changes

```bash
git checkout HEAD~1
```

---

## 🔧 Common Issues & Solutions

### Issue 1: Email Not Sending

**Symptom**: Emails not arriving

**Solutions**:
```bash
# Check configuration
python -c "from app.core.config import settings; print(f'Resend: {bool(settings.RESEND_API_KEY)}'); print(f'SMTP: {bool(settings.SMTP_HOST)}')"

# Check logs
tail -f logs/app.log | grep -i email

# Test email directly
curl -X POST "http://localhost:8000/api/v1/monitoring/test-alert?severity=info"
```

### Issue 2: Migration Fails

**Symptom**: `alembic upgrade` fails

**Solutions**:
```bash
# Check database connection
psql -d quant_db -c "SELECT 1"

# Check Alembic version table
psql -d quant_db -c "SELECT * FROM alembic_version"

# Force migration revision
alembic stamp head

# Retry
alembic upgrade head
```

### Issue 3: API Keys Not Validating

**Symptom**: API key validation returns None

**Solutions**:
```python
# Check database
from app.models.api_key import APIKey
from app.core.database import get_db
from sqlalchemy import select

async for db in get_db():
    result = await db.execute(select(APIKey))
    keys = result.scalars().all()
    print(f"Total API keys: {len(keys)}")
    for key in keys:
        print(f"  - {key.key_id}: active={key.is_active}")
```

### Issue 4: News API Rate Limit

**Symptom**: NewsAPI returns 429 error

**Solutions**:
- Free tier: 100 requests/day
- Implement caching:
```python
from app.core.cache import cache_result

@cache_result(ttl=3600)  # Cache for 1 hour
async def get_news(symbol):
    # Your news fetching code
    pass
```

---

## 📈 Performance Optimization

### 1. Enable Redis Caching

```env
REDIS_URL=redis://localhost:6379/0
REDIS_ENABLED=true
```

### 2. Configure Cache TTLs

The following are already configured:

```python
API_KEY_CACHE_TTL = 300      # 5 minutes
ANALYTICS_ENSEMBLE_TTL = 3600 # 1 hour
MOBILE_SYNC_CACHE_TTL = 3600  # 1 hour
```

### 3. Database Connection Pooling

Already configured in `settings.database`:

```python
POOL_SIZE = 20
MAX_OVERFLOW = 40
POOL_RECYCLE_SECONDS = 3600
```

---

## 🔒 Security Checklist

After migration, verify:

- [ ] SECRET_KEY is at least 32 characters
- [ ] HTTPS enabled in production
- [ ] CORS origins restricted (no `*`)
- [ ] Database credentials rotated
- [ ] API keys hashed (SHA-256)
- [ ] Email credentials secured (app passwords)
- [ ] Sentry configured for error tracking
- [ ] Rate limiting enabled

Run security audit:
```bash
curl -H "Authorization: Bearer ADMIN_TOKEN" \
  http://localhost:8000/api/v1/admin/security/security-audit
```

---

## 📊 Monitoring After Migration

### 1. Check Health Endpoint

```bash
curl http://localhost:8000/api/v1/monitoring/health | jq
```

Expected:
```json
{
  "status": "healthy",
  "checks": {
    "database": {
      "status": "connected",
      "response_time_ms": 12.45
    }
  }
}
```

### 2. Monitor Email Sending

```bash
# Watch logs for email activity
tail -f logs/app.log | grep -E "Email sent|Email failed"
```

### 3. Track API Key Usage

```bash
# Query database
psql -d quant_db -c "
  SELECT
    key_id,
    name,
    total_requests,
    last_used_at,
    is_active
  FROM api_keys
  ORDER BY last_used_at DESC
  LIMIT 10;
"
```

### 4. Monitor Mobile Device Registrations

```bash
psql -d quant_db -c "
  SELECT
    device_type,
    COUNT(*) as count,
    MAX(last_active_at) as last_active
  FROM mobile_devices
  GROUP BY device_type;
"
```

---

## 🎯 Post-Migration Tasks

### Week 1

- [ ] Monitor error rates
- [ ] Check email delivery rates
- [ ] Verify API key creation/validation
- [ ] Test mobile device registration
- [ ] Review database performance

### Week 2

- [ ] Analyze API key usage patterns
- [ ] Optimize email templates
- [ ] Review news API costs
- [ ] Consider paid API plans if needed

### Month 1

- [ ] Review security audit
- [ ] Rotate API keys
- [ ] Clean up inactive devices
- [ ] Optimize database indexes
- [ ] Plan for scaling

---

## 📚 Additional Resources

### Documentation

- [Task 8 Completion Summary](./TASK_8_TODO_COMPLETION_SUMMARY.md)
- [Quick Start Guide](./QUICK_START_NEW_FEATURES.md)
- API documentation: http://localhost:8000/docs

### External Services

- **Resend**: https://resend.com/docs
- **NewsAPI**: https://newsapi.org/docs
- **Alpha Vantage**: https://www.alphavantage.co/documentation
- **Alembic**: https://alembic.sqlalchemy.org

### Support

For issues:
1. Check logs: `tail -f logs/app.log`
2. Review error tracking (Sentry if configured)
3. Check health endpoint: `/api/v1/monitoring/health`
4. Run security audit: `/api/v1/admin/security/security-audit`

---

## ✅ Migration Checklist

- [ ] Backup database
- [ ] Update `.env` file
- [ ] Install dependencies
- [ ] Run migration (`alembic upgrade head`)
- [ ] Verify tables created
- [ ] Test email service
- [ ] Test API key creation
- [ ] Test mobile registration
- [ ] Check health endpoint
- [ ] Monitor logs for 24 hours
- [ ] Run security audit
- [ ] Update documentation
- [ ] Train team on new features

---

## 🎉 Success Criteria

Your migration is successful when:

1. ✅ All 2 new tables created (api_keys, mobile_devices)
2. ✅ Email alerts working
3. ✅ API keys can be created and validated
4. ✅ Mobile devices can register
5. ✅ Health check shows database response time
6. ✅ No errors in logs
7. ✅ All existing features still working

---

*Migration guide for Task #8: TODO Implementations*
*Last updated: 2026-02-03*
