# Running the Improved Quant Platform

## Quick Start

### Option 1: Using Docker (Recommended)

```bash
# Start all services with improvements
docker-compose -f docker-test-improvements.yml up

# The API will be available at:
# http://localhost:8000
# API Docs: http://localhost:8000/api/v1/docs
```

### Option 2: Local Development

```bash
# 1. Setup Python virtual environment
cd quant/backend
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# 2. Install dependencies
pip install -r requirements.txt

# 3. Set environment variables
export ENVIRONMENT=development
export SECRET_KEY="your-secret-key-at-least-32-characters-long"
export DATABASE_URL="postgresql://quant_user:quant_password@localhost:5432/quant_db"
export REDIS_URL="redis://localhost:6379/0"
export PROJECT_NAME="Quant Analytics Platform"
export VERSION="1.0.0"
export API_V1_STR="/api/v1"

# 4. Start the server
uvicorn app.main:app --reload --port 8000
```

## Testing the Improvements

### 1. Configuration Validation
On startup, you'll see validation messages:
```
✅ Configuration validation passed
```

### 2. Enhanced Rate Limiting
Test with multiple requests:
```bash
# Will show rate limit headers in response
curl -I http://localhost:8000/api/v1/politicians

# Headers include:
# X-RateLimit-Limit: 60
# X-RateLimit-Remaining: 59
# X-RateLimit-Reset: 1234567890
```

### 3. Audit Logging
Check logs for audit events:
```bash
# Login attempt will be logged
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"test","password":"test"}'

# Look for: "Audit Event: {event_type: login_failed...}"
```

### 4. OpenAPI Documentation
Visit: http://localhost:8000/api/v1/docs

You'll see:
- Detailed schemas with examples
- Request/response models
- Field descriptions and validations

### 5. Optimized Queries
Analytics endpoints now use:
- Batch loading
- Eager loading with joinedload/selectinload
- Aggregated queries
- No N+1 queries

## Features Implemented

### 🔐 Security Enhancements
- **Per-user rate limiting** with tiers (Free: 20/min, Basic: 60/min, Premium: 200/min)
- **Audit logging** for all sensitive operations
- **Config validation** on startup
- **IP anonymization** in logs (192.168.*.*)

### 🚀 Performance Optimizations
- **N+1 query prevention** with eager loading
- **Batch operations** for multiple entities
- **Redis caching** for expensive operations
- **Sliding window** rate limiting algorithm

### 📚 Documentation
- **OpenAPI schemas** with examples
- **Pydantic models** with validation
- **Comprehensive docstrings**
- **API versioning** (/api/v1)

### 🔍 Monitoring
- **Audit trail** for compliance
- **Rate limit metrics** in headers
- **Security event tracking**
- **Performance monitoring hooks**

## Environment Variables

### Required
- `SECRET_KEY`: Min 32 characters, no common patterns
- `DATABASE_URL`: PostgreSQL connection string
- `ENVIRONMENT`: development/production/test

### Optional
- `REDIS_URL`: For caching and rate limiting
- `SENTRY_DSN`: Error tracking
- `DEBUG`: Must be False in production

## API Endpoints

### Authentication
- `POST /api/v1/auth/register` - User registration (with audit)
- `POST /api/v1/auth/login` - Login (with audit)
- `POST /api/v1/auth/refresh` - Refresh token
- `GET /api/v1/auth/me` - Current user info

### Analytics (Rate Limited)
- `GET /api/v1/analytics/ensemble/{politician_id}` - ML predictions (10 req/min)
- `GET /api/v1/analytics/correlation/pairwise` - Correlation analysis
- `GET /api/v1/analytics/network/analysis` - Network metrics (5 req/min)

## Troubleshooting

### Config Validation Errors
```bash
# Check your environment variables
python -c "from app.core.config_validator import get_config_status; print(get_config_status())"
```

### Rate Limiting Issues
- Check Redis connection
- Verify tier assignment
- Review endpoint-specific limits

### Audit Logging
- Logs are in both database and application logs
- Check `audit_logs` table
- Review app.log for audit events

## Next Steps

1. **Production Deployment**
   - Set `ENVIRONMENT=production`
   - Configure real PostgreSQL and Redis
   - Set strong `SECRET_KEY`
   - Enable Sentry monitoring

2. **Customize Rate Limits**
   - Edit `endpoint_limits` in `rate_limit_enhanced.py`
   - Adjust tier limits in `RateLimitTier.LIMITS`
   - Configure per-user tiers in database

3. **Extend Audit Logging**
   - Add more event types in `AuditEventType`
   - Implement retention policies
   - Create audit reports

4. **Monitor Performance**
   - Check query performance with logging
   - Monitor cache hit rates
   - Track rate limit violations