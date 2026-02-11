# Quick Start Guide: New Features

This guide shows you how to use the newly implemented features from Task #8.

---

## 🔑 API Key Management

### 1. Create an API Key

```python
# In your application code
from app.services.api_key_manager import api_key_manager, APIKeyPermission

# Create a new API key
key_id, secret_key = await api_key_manager.create_key(
    db=db,
    user_id="your-user-uuid",
    name="My Production API Key",
    permissions=[APIKeyPermission.READ, APIKeyPermission.WRITE],
    expires_days=90  # Optional: key expires in 90 days
)

print(f"Key ID: {key_id}")
print(f"Secret: {secret_key}")  # Save this - it won't be shown again!
```

### 2. Use an API Key

Add to your request headers:
```bash
curl -H "Authorization: Bearer qtp_YOUR_SECRET_KEY_HERE" \
     https://api.example.com/api/v1/trades
```

### 3. Rotate an API Key

```python
# Rotate (invalidate old, create new)
new_key_id, new_secret = await api_key_manager.rotate_key(
    db=db,
    key_id="old-key-id",
    user_id="your-user-uuid"
)
```

### 4. Revoke an API Key

```python
# Revoke a key
success = await api_key_manager.revoke_key(
    db=db,
    key_id="key-to-revoke",
    user_id="your-user-uuid"
)
```

### 5. List Your API Keys

```python
# Get all keys for a user
keys = await api_key_manager.list_user_keys(
    db=db,
    user_id="your-user-uuid"
)

for key in keys:
    print(f"{key.name}: {key.key_id} (active: {key.is_active})")
```

---

## 📧 Email Alerts

### 1. Configure Email

Add to `.env`:
```env
# Option 1: Resend API (Recommended)
RESEND_API_KEY=re_xxxxxxxxxxxx
EMAIL_DOMAIN=yourdomain.com

# Option 2: SMTP (Gmail example)
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_TLS=true
SMTP_USER=your_email@gmail.com
SMTP_PASSWORD=your_app_password

# Recipients for system alerts
ALERT_EMAIL=admin@example.com,devops@example.com
```

### 2. Send an Alert Email

```python
from app.services.email_service import email_service

# Send a formatted alert email
await email_service.send_alert_email(
    to_email="admin@example.com",
    title="High Error Rate Detected",
    message="The error rate on /api/v1/trades has exceeded 5%",
    severity="critical",  # info, warning, or critical
    metadata={
        "error_rate": "8.5%",
        "endpoint": "/api/v1/trades",
        "time_window": "last 5 minutes"
    }
)
```

### 3. Send a Custom Email

```python
# Send custom HTML email
await email_service.send_email(
    to_email=["user@example.com", "admin@example.com"],
    subject="Your Custom Subject",
    html_body="<h1>Hello</h1><p>This is your email content.</p>",
    text_body="Hello\n\nThis is your email content.",
    from_email="noreply@yourdomain.com"
)
```

### 4. Test Email Configuration

```bash
# Send test alert via API
curl -X POST "http://localhost:8000/api/v1/monitoring/test-alert?severity=info"
```

---

## 📱 Mobile Device Registration

### 1. Register a Device (iOS)

```http
POST /api/v1/mobile/device/register
Content-Type: application/json
Authorization: Bearer YOUR_JWT_TOKEN

{
  "device_token": "your_fcm_or_apns_token",
  "device_type": "ios",
  "app_version": "1.0.0",
  "device_model": "iPhone 14 Pro",
  "os_version": "iOS 17.2"
}
```

Response:
```json
{
  "status": "registered",
  "device_token": "your_fcm_o...",
  "message": "Device registered for push notifications"
}
```

### 2. Register a Device (Android)

```http
POST /api/v1/mobile/device/register
Content-Type: application/json

{
  "device_token": "your_fcm_token",
  "device_type": "android",
  "app_version": "1.0.0",
  "device_model": "Samsung Galaxy S23",
  "os_version": "Android 14"
}
```

### 3. Unregister a Device

```http
DELETE /api/v1/mobile/device/unregister?device_token=your_fcm_token
```

### 4. Update Device Info

Just register again with the same token - it will update:
```http
POST /api/v1/mobile/device/register
{
  "device_token": "same_token",
  "device_type": "ios",
  "app_version": "1.1.0",  # Updated version
  ...
}
```

---

## 📰 News Sentiment Analysis

### 1. Configure News APIs

Add to `.env`:
```env
# NewsAPI (100 requests/day free)
NEWSAPI_KEY=your_newsapi_key

# Alpha Vantage (25 requests/day free)
ALPHA_VANTAGE_API_KEY=your_alpha_vantage_key
```

Get keys:
- NewsAPI: https://newsapi.org
- Alpha Vantage: https://www.alphavantage.co

### 2. Analyze Stock Sentiment

```python
from app.services.sentiment_analysis import get_sentiment_analyzer, SentimentSource

# Get analyzer instance
analyzer = get_sentiment_analyzer()

# Analyze a stock
sentiment = await analyzer.analyze_symbol(
    symbol="AAPL",
    sources=[SentimentSource.NEWS],
    limit_per_source=10
)

print(f"Overall Score: {sentiment.overall_score}")  # -1 to 1
print(f"Category: {sentiment.overall_category}")    # very_negative to very_positive
print(f"Confidence: {sentiment.confidence}")        # 0 to 1
print(f"Positive: {sentiment.positive_count}")
print(f"Negative: {sentiment.negative_count}")
print(f"Neutral: {sentiment.neutral_count}")
```

### 3. Example Output

```python
{
  "symbol": "AAPL",
  "overall_score": 0.65,
  "overall_category": "positive",
  "confidence": 0.82,
  "timestamp": "2026-02-03T12:00:00Z",
  "source_breakdown": {
    "news": 0.65
  },
  "total_sources": 10,
  "positive_count": 7,
  "negative_count": 1,
  "neutral_count": 2
}
```

---

## 🏥 Health Monitoring

### 1. Check System Health

```bash
curl http://localhost:8000/api/v1/monitoring/health
```

Response includes database response time:
```json
{
  "status": "healthy",
  "timestamp": "2026-02-03T12:00:00Z",
  "checks": {
    "database": {
      "status": "connected",
      "response_time_ms": 12.45
    },
    "cache": {
      "status": "connected",
      "type": "redis"
    },
    "system": {
      "status": "healthy",
      "cpu_percent": 15.2,
      "memory_percent": 42.8
    }
  }
}
```

### 2. View Recent Alerts

```bash
curl http://localhost:8000/api/v1/monitoring/alerts?limit=10&severity=critical
```

---

## 🔐 Admin Features

### 1. List All API Keys (Admin)

```bash
curl -H "Authorization: Bearer ADMIN_JWT_TOKEN" \
     "http://localhost:8000/api/v1/admin/security/api-keys?limit=50"
```

### 2. Filter API Keys

```bash
# By user
curl -H "Authorization: Bearer ADMIN_JWT_TOKEN" \
     "http://localhost:8000/api/v1/admin/security/api-keys?user_id=USER_UUID"

# Active keys only
curl -H "Authorization: Bearer ADMIN_JWT_TOKEN" \
     "http://localhost:8000/api/v1/admin/security/api-keys?is_active=true"
```

### 3. Run Security Audit

```bash
curl -H "Authorization: Bearer ADMIN_JWT_TOKEN" \
     "http://localhost:8000/api/v1/admin/security/security-audit"
```

---

## 🗄️ Database Setup

### 1. Run Migration

```bash
cd quant/backend
alembic upgrade head
```

### 2. Verify Tables

```bash
# Check tables created
psql -d quant_db -c "\dt"

# Expected output:
# api_keys
# mobile_devices
# ... other tables
```

### 3. Check Indexes

```bash
psql -d quant_db -c "\di api_keys"
psql -d quant_db -c "\di mobile_devices"
```

---

## 🧪 Testing

### Test Email Service

```python
# Test Resend
from app.services.email_service import email_service

result = await email_service.send_email(
    to_email="test@example.com",
    subject="Test Email",
    html_body="<h1>Test</h1>",
    text_body="Test"
)
print(f"Email sent: {result}")
```

### Test API Key

```python
# Create test key
key_id, secret = await api_key_manager.create_key(
    db=db,
    user_id=user.id,
    name="Test Key",
    permissions=[APIKeyPermission.READ]
)

# Validate it
metadata = await api_key_manager.validate_key(
    db=db,
    key=secret,
    required_permission=APIKeyPermission.READ
)
assert metadata is not None
```

### Test Device Registration

```bash
curl -X POST http://localhost:8000/api/v1/mobile/device/register \
  -H "Content-Type: application/json" \
  -d '{
    "device_token": "test_token_123",
    "device_type": "ios",
    "app_version": "1.0.0"
  }'
```

---

## 🚀 Production Deployment

### 1. Environment Variables

Create production `.env`:
```env
# Required
RESEND_API_KEY=re_prod_xxxxxxxxxxxx
EMAIL_DOMAIN=yourdomain.com
ALERT_EMAIL=alerts@yourdomain.com

# Optional but recommended
NEWSAPI_KEY=your_key
ALPHA_VANTAGE_API_KEY=your_key
SLACK_WEBHOOK_URL=https://hooks.slack.com/...
ALERT_WEBHOOK_URL=https://your-webhook.com

# SMTP Fallback
SMTP_HOST=smtp.sendgrid.net
SMTP_PORT=587
SMTP_USER=apikey
SMTP_PASSWORD=your_sendgrid_key
```

### 2. Run Migrations

```bash
alembic upgrade head
```

### 3. Verify Configuration

```bash
# Check health
curl https://your-api.com/api/v1/monitoring/health

# Test alert
curl -X POST https://your-api.com/api/v1/monitoring/test-alert
```

### 4. Monitor Logs

```bash
# Check for email sending
grep "Email sent successfully" app.log

# Check for API key usage
grep "API key usage" app.log

# Check for device registrations
grep "Device registered" app.log
```

---

## 📊 Rate Limits

### Free Tier Limits

- **NewsAPI**: 100 requests/day
- **Alpha Vantage**: 25 requests/day
- **Resend**: 100 emails/day, 3,000/month

### Recommendations

1. Cache sentiment analysis results
2. Batch email sending when possible
3. Consider paid plans for production
4. Implement request queuing for news APIs

---

## 🐛 Troubleshooting

### Email Not Sending

```python
# Check configuration
from app.core.config import settings

print(f"Resend configured: {bool(settings.RESEND_API_KEY)}")
print(f"SMTP configured: {bool(settings.SMTP_HOST)}")
print(f"Alert email: {settings.ALERT_EMAIL}")
```

### API Key Not Validating

```python
# Check key hash
from app.services.api_key_manager import api_key_manager

key_hash = api_key_manager.hash_key("qtp_your_key")
print(f"Hash: {key_hash}")

# Check database
from app.models.api_key import APIKey
result = await db.execute(select(APIKey).where(APIKey.key_hash == key_hash))
key = result.scalar_one_or_none()
print(f"Found: {key is not None}")
```

### News API Not Working

```python
# Test NewsAPI directly
import httpx

async with httpx.AsyncClient() as client:
    response = await client.get(
        "https://newsapi.org/v2/everything",
        params={
            "q": "AAPL",
            "apiKey": "your_key"
        }
    )
    print(response.json())
```

---

## 📚 Additional Resources

- **Resend Docs**: https://resend.com/docs
- **NewsAPI Docs**: https://newsapi.org/docs
- **Alpha Vantage Docs**: https://www.alphavantage.co/documentation
- **FCM Setup**: https://firebase.google.com/docs/cloud-messaging
- **APNS Setup**: https://developer.apple.com/documentation/usernotifications

---

*Last Updated: 2026-02-03*
