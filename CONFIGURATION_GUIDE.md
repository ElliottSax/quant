# Configuration Guide

This guide documents all configurable values in the Quant Analytics Platform that have been extracted from hardcoded values into centralized configuration.

## Overview

All hardcoded "magic numbers" have been moved to `/quant/backend/app/core/config.py` and are now configurable via environment variables. This improves:

- **Flexibility**: Adjust settings without code changes
- **Environment-specific configs**: Different values for dev/staging/prod
- **Security**: Sensitive timeouts and limits can be tuned per deployment
- **Maintainability**: All configuration in one place
- **Documentation**: Clear descriptions of what each value does

## Configuration Categories

### 1. Cache Settings (`CacheSettings`)

Controls cache TTL (Time To Live) values across the application.

| Setting | Environment Variable | Default | Description |
|---------|---------------------|---------|-------------|
| `DEFAULT_TTL` | `CACHE_DEFAULT_TTL` | 3600 | Default cache TTL for generic data (1 hour) |
| `FOURIER_ANALYSIS_TTL` | `CACHE_FOURIER_ANALYSIS_TTL` | 1800 | Cache duration for Fourier analysis results (30 min) |
| `PATTERN_ANALYSIS_TTL` | `CACHE_PATTERN_ANALYSIS_TTL` | 3600 | Cache duration for pattern analysis (1 hour) |
| `MARKET_DATA_TTL` | `CACHE_MARKET_DATA_TTL` | 300 | Cache duration for market data (5 min) |
| `STATS_SHORT_TTL` | `CACHE_STATS_SHORT_TTL` | 300 | Cache for short-term stats (7d data, 5 min) |
| `STATS_LONG_TTL` | `CACHE_STATS_LONG_TTL` | 3600 | Cache for long-term stats (90d, 1y data, 1 hour) |
| `PREMIUM_PATTERNS_TTL` | `CACHE_PREMIUM_PATTERNS_TTL` | 1800 | Cache for premium pattern analysis (30 min) |
| `CONGRESSIONAL_SCRAPER_TTL` | `CACHE_CONGRESSIONAL_SCRAPER_TTL` | 3600 | Cache for congressional trading data (1 hour) |
| `API_KEY_CACHE_TTL` | `CACHE_API_KEY_CACHE_TTL` | 300 | Cache for API key validation (5 min) |
| `QUERY_CACHE_TTL` | `CACHE_QUERY_CACHE_TTL` | 300 | Cache for database query results (5 min) |
| `MOBILE_SYNC_CACHE_TTL` | `CACHE_MOBILE_SYNC_CACHE_TTL` | 3600 | Cache for mobile app sync data (1 hour) |
| `ANALYTICS_ENSEMBLE_TTL` | `CACHE_ANALYTICS_ENSEMBLE_TTL` | 3600 | Cache for ML ensemble analytics (1 hour) |
| `HTTP_CACHE_MAX_AGE` | `CACHE_HTTP_CACHE_MAX_AGE` | 300 | HTTP ETag cache max-age (5 min) |
| `CORS_PREFLIGHT_MAX_AGE` | `CACHE_CORS_PREFLIGHT_MAX_AGE` | 3600 | CORS preflight cache duration (1 hour) |
| `CSRF_TOKEN_MAX_AGE` | `CACHE_CSRF_TOKEN_MAX_AGE` | 3600 | CSRF token validity period (1 hour) |

**Recommended Values:**

- **Development**: Use shorter TTLs (60-300s) to see changes quickly
- **Staging**: Use production-like values for realistic testing
- **Production**: Use longer TTLs (1800-3600s) to reduce load

**Example Configuration:**

```bash
# .env file for development
CACHE_DEFAULT_TTL=300
CACHE_MARKET_DATA_TTL=60
CACHE_FOURIER_ANALYSIS_TTL=600

# .env file for production
CACHE_DEFAULT_TTL=3600
CACHE_MARKET_DATA_TTL=300
CACHE_FOURIER_ANALYSIS_TTL=1800
```

### 2. Rate Limit Settings (`RateLimitSettings`)

Controls API rate limiting to prevent abuse and ensure fair usage.

| Setting | Environment Variable | Default | Description |
|---------|---------------------|---------|-------------|
| `FREE_TIER_RPM` | `RATE_LIMIT_FREE_TIER_RPM` | 20 | Free tier requests per minute |
| `BASIC_TIER_RPM` | `RATE_LIMIT_BASIC_TIER_RPM` | 60 | Basic tier requests per minute |
| `PREMIUM_TIER_RPM` | `RATE_LIMIT_PREMIUM_TIER_RPM` | 200 | Premium tier requests per minute |
| `FREE_TIER_RPH` | `RATE_LIMIT_FREE_TIER_RPH` | 500 | Free tier requests per hour |
| `BASIC_TIER_RPH` | `RATE_LIMIT_BASIC_TIER_RPH` | 2000 | Basic tier requests per hour |
| `PREMIUM_TIER_RPH` | `RATE_LIMIT_PREMIUM_TIER_RPH` | 10000 | Premium tier requests per hour |
| `ANALYTICS_ENSEMBLE_LIMIT` | `RATE_LIMIT_ANALYTICS_ENSEMBLE_LIMIT` | 10 | Rate limit for ML ensemble endpoint |
| `ANALYTICS_NETWORK_LIMIT` | `RATE_LIMIT_ANALYTICS_NETWORK_LIMIT` | 5 | Rate limit for network analysis endpoint |
| `EXPORT_LIMIT` | `RATE_LIMIT_EXPORT_LIMIT` | 20 | Rate limit for data export endpoint |
| `AUTH_LOGIN_LIMIT` | `RATE_LIMIT_AUTH_LOGIN_LIMIT` | 5 | Rate limit for login (brute force protection) |
| `AUTH_REGISTER_LIMIT` | `RATE_LIMIT_AUTH_REGISTER_LIMIT` | 3 | Rate limit for registration |
| `DEFAULT_REQUESTS_PER_MINUTE` | `RATE_LIMIT_DEFAULT_REQUESTS_PER_MINUTE` | 60 | Default per-minute limit |
| `DEFAULT_REQUESTS_PER_HOUR` | `RATE_LIMIT_DEFAULT_REQUESTS_PER_HOUR` | 1000 | Default hourly limit |
| `IP_LIMIT_MAX` | `RATE_LIMIT_IP_LIMIT_MAX` | 30 | Maximum IP-based rate limit |
| `RATE_LIMIT_WINDOW_SECONDS` | `RATE_LIMIT_RATE_LIMIT_WINDOW_SECONDS` | 60 | Sliding window duration |

**Recommended Values:**

- **Development**: Higher limits for easier testing (e.g., 1000 RPM)
- **Staging**: Production-like limits
- **Production**: Conservative limits to prevent abuse

**Security Considerations:**

- `AUTH_LOGIN_LIMIT` should be low (3-5) to prevent brute force attacks
- `AUTH_REGISTER_LIMIT` should be low (2-3) to prevent spam accounts
- ML endpoints should have lower limits due to computational cost

**Example Configuration:**

```bash
# .env for production
RATE_LIMIT_FREE_TIER_RPM=20
RATE_LIMIT_AUTH_LOGIN_LIMIT=5
RATE_LIMIT_ANALYTICS_ENSEMBLE_LIMIT=10

# .env for development (more permissive)
RATE_LIMIT_FREE_TIER_RPM=100
RATE_LIMIT_AUTH_LOGIN_LIMIT=50
RATE_LIMIT_ANALYTICS_ENSEMBLE_LIMIT=100
```

### 3. Security Settings (`SecuritySettings`)

Controls security-related timeouts and limits.

| Setting | Environment Variable | Default | Description |
|---------|---------------------|---------|-------------|
| `MAX_FAILED_LOGIN_ATTEMPTS` | `SECURITY_MAX_FAILED_LOGIN_ATTEMPTS` | 5 | Failed login attempts before lockout |
| `LOCKOUT_DURATION_MINUTES` | `SECURITY_LOCKOUT_DURATION_MINUTES` | 30 | Account lockout duration |
| `DEFAULT_RETRY_COUNT` | `SECURITY_DEFAULT_RETRY_COUNT` | 3 | Default retry count for operations |
| `DEFAULT_TIMEOUT_SECONDS` | `SECURITY_DEFAULT_TIMEOUT_SECONDS` | 30 | Default timeout for operations |
| `DB_POOL_TIMEOUT_SECONDS` | `SECURITY_DB_POOL_TIMEOUT_SECONDS` | 30 | Database connection timeout |

**Recommended Values:**

- **Development**: Shorter lockouts (5-10 min) for easier testing
- **Production**: Longer lockouts (30-60 min) for better security

**Security Best Practices:**

- Keep `MAX_FAILED_LOGIN_ATTEMPTS` between 3-5
- `LOCKOUT_DURATION_MINUTES` should be at least 15-30 minutes
- Consider exponential backoff for repeated lockouts

**Example Configuration:**

```bash
# Production - strict security
SECURITY_MAX_FAILED_LOGIN_ATTEMPTS=3
SECURITY_LOCKOUT_DURATION_MINUTES=60

# Development - more permissive
SECURITY_MAX_FAILED_LOGIN_ATTEMPTS=10
SECURITY_LOCKOUT_DURATION_MINUTES=5
```

### 4. Database Settings (`DatabaseSettings`)

Controls database connection pooling and query optimization.

| Setting | Environment Variable | Default | Description |
|---------|---------------------|---------|-------------|
| `POOL_SIZE` | `DATABASE_POOL_SIZE` | 20 | Base connection pool size |
| `MAX_OVERFLOW` | `DATABASE_MAX_OVERFLOW` | 40 | Maximum overflow connections |
| `POOL_RECYCLE_SECONDS` | `DATABASE_POOL_RECYCLE_SECONDS` | 3600 | Connection recycle interval (1 hour) |
| `DEFAULT_QUERY_CHUNK_SIZE` | `DATABASE_DEFAULT_QUERY_CHUNK_SIZE` | 1000 | Default batch query chunk size |

**Recommended Values:**

- **Small deployment**: `POOL_SIZE=5`, `MAX_OVERFLOW=10`
- **Medium deployment**: `POOL_SIZE=20`, `MAX_OVERFLOW=40` (default)
- **Large deployment**: `POOL_SIZE=50`, `MAX_OVERFLOW=100`

**Performance Tuning:**

- Increase `POOL_SIZE` if you see "connection pool exhausted" errors
- `MAX_OVERFLOW` should be 2x `POOL_SIZE` for burst traffic
- `POOL_RECYCLE_SECONDS` prevents stale connections

**Example Configuration:**

```bash
# High-traffic production
DATABASE_POOL_SIZE=50
DATABASE_MAX_OVERFLOW=100
DATABASE_POOL_RECYCLE_SECONDS=1800

# Low-traffic development
DATABASE_POOL_SIZE=5
DATABASE_MAX_OVERFLOW=10
```

### 5. Performance Settings (`PerformanceSettings`)

Controls performance-related timeouts, compression, and optimization settings.

| Setting | Environment Variable | Default | Description |
|---------|---------------------|---------|-------------|
| `MIN_COMPRESS_SIZE_BYTES` | `PERFORMANCE_MIN_COMPRESS_SIZE_BYTES` | 500 | Minimum response size for compression |
| `GZIP_COMPRESSION_LEVEL` | `PERFORMANCE_GZIP_COMPRESSION_LEVEL` | 6 | GZip compression level (1-9) |
| `RATE_LIMIT_CLEANUP_INTERVAL_SECONDS` | `PERFORMANCE_RATE_LIMIT_CLEANUP_INTERVAL_SECONDS` | 300 | Cleanup interval for rate limit data |
| `DEFAULT_MAX_TOKENS` | `PERFORMANCE_DEFAULT_MAX_TOKENS` | 1000 | Default max tokens for AI responses |
| `ML_TASK_TIME_LIMIT_SECONDS` | `PERFORMANCE_ML_TASK_TIME_LIMIT_SECONDS` | 14400 | Hard limit for ML tasks (4 hours) |
| `ML_TASK_SOFT_TIME_LIMIT_SECONDS` | `PERFORMANCE_ML_TASK_SOFT_TIME_LIMIT_SECONDS` | 10800 | Soft limit for ML tasks (3 hours) |
| `MARKET_INTERVAL_5MIN` | `PERFORMANCE_MARKET_INTERVAL_5MIN` | 300 | 5-minute market data interval |
| `MARKET_INTERVAL_30MIN` | `PERFORMANCE_MARKET_INTERVAL_30MIN` | 1800 | 30-minute market data interval |
| `MARKET_INTERVAL_1HOUR` | `PERFORMANCE_MARKET_INTERVAL_1HOUR` | 3600 | 1-hour market data interval |
| `DEFAULT_NUM_SIMULATIONS` | `PERFORMANCE_DEFAULT_NUM_SIMULATIONS` | 10000 | Default Monte Carlo simulations |
| `DEFAULT_INITIAL_CAPITAL` | `PERFORMANCE_DEFAULT_INITIAL_CAPITAL` | 10000.0 | Default backtesting capital |
| `MIN_TRADES_FOR_ANALYSIS` | `PERFORMANCE_MIN_TRADES_FOR_ANALYSIS` | 50 | Minimum trades for valid analysis |
| `MOBILE_SYNC_INTERVAL_SECONDS` | `PERFORMANCE_MOBILE_SYNC_INTERVAL_SECONDS` | 300 | Mobile app sync interval |

**Recommended Values:**

- `GZIP_COMPRESSION_LEVEL`: 4-6 for balanced performance/compression
- `MIN_COMPRESS_SIZE_BYTES`: 500-1000 bytes
- `DEFAULT_NUM_SIMULATIONS`: 10000 for accuracy, 1000 for speed

**Performance vs Quality Trade-offs:**

| Setting | Fast (lower quality) | Balanced | Accurate (slower) |
|---------|---------------------|----------|-------------------|
| `GZIP_COMPRESSION_LEVEL` | 1-3 | 6 | 9 |
| `DEFAULT_NUM_SIMULATIONS` | 1000 | 10000 | 100000 |
| `ML_TASK_TIME_LIMIT_SECONDS` | 1800 | 14400 | 28800 |

**Example Configuration:**

```bash
# Fast, lower resource usage
PERFORMANCE_GZIP_COMPRESSION_LEVEL=4
PERFORMANCE_DEFAULT_NUM_SIMULATIONS=1000

# High quality, more resources
PERFORMANCE_GZIP_COMPRESSION_LEVEL=9
PERFORMANCE_DEFAULT_NUM_SIMULATIONS=50000
```

## Accessing Configuration in Code

All configuration is accessible via the `settings` object:

```python
from app.core.config import settings

# Cache settings
ttl = settings.cache.DEFAULT_TTL
fourier_ttl = settings.cache.FOURIER_ANALYSIS_TTL

# Rate limit settings
free_limit = settings.rate_limit.FREE_TIER_RPM
login_limit = settings.rate_limit.AUTH_LOGIN_LIMIT

# Security settings
max_attempts = settings.security.MAX_FAILED_LOGIN_ATTEMPTS
lockout_duration = settings.security.LOCKOUT_DURATION_MINUTES

# Database settings
pool_size = settings.database.POOL_SIZE

# Performance settings
compression = settings.performance.GZIP_COMPRESSION_LEVEL
```

## Migration Notes

### Breaking Changes

None - all defaults match previous hardcoded values. Existing code will work without changes.

### Backward Compatibility

All configuration classes use the exact same default values as the previous hardcoded constants. This means:

- No changes required to existing code
- All tests will continue to pass
- Optional migration to new config over time

### Updating Code (Optional)

While not required, you can gradually update code to use the new config:

**Before:**
```python
@cached("fourier", ttl=1800)
async def analyze_fourier(...):
    ...
```

**After:**
```python
@cached("fourier", ttl=settings.cache.FOURIER_ANALYSIS_TTL)
async def analyze_fourier(...):
    ...
```

## Environment-Specific Configuration

### Development (.env.development)

```bash
# Shorter caches for faster development
CACHE_DEFAULT_TTL=60
CACHE_MARKET_DATA_TTL=30

# More permissive rate limits
RATE_LIMIT_FREE_TIER_RPM=1000
RATE_LIMIT_AUTH_LOGIN_LIMIT=100

# Shorter lockouts
SECURITY_MAX_FAILED_LOGIN_ATTEMPTS=10
SECURITY_LOCKOUT_DURATION_MINUTES=5

# Smaller pools
DATABASE_POOL_SIZE=5
DATABASE_MAX_OVERFLOW=10
```

### Staging (.env.staging)

```bash
# Production-like settings but slightly more permissive
CACHE_DEFAULT_TTL=1800
RATE_LIMIT_FREE_TIER_RPM=30
SECURITY_MAX_FAILED_LOGIN_ATTEMPTS=5
DATABASE_POOL_SIZE=15
```

### Production (.env.production)

```bash
# Optimized for security and performance
CACHE_DEFAULT_TTL=3600
CACHE_MARKET_DATA_TTL=300

# Strict rate limits
RATE_LIMIT_FREE_TIER_RPM=20
RATE_LIMIT_AUTH_LOGIN_LIMIT=5

# Strong security
SECURITY_MAX_FAILED_LOGIN_ATTEMPTS=3
SECURITY_LOCKOUT_DURATION_MINUTES=60

# Large pools for high traffic
DATABASE_POOL_SIZE=50
DATABASE_MAX_OVERFLOW=100
```

## Testing Configuration

For automated tests, you can override settings:

```python
from app.core.config import settings

# Temporarily override for testing
original_ttl = settings.cache.DEFAULT_TTL
settings.cache.DEFAULT_TTL = 1  # Very short for tests

# ... run tests ...

# Restore
settings.cache.DEFAULT_TTL = original_ttl
```

Or use environment variables in test setup:

```bash
# pytest.ini or test environment
CACHE_DEFAULT_TTL=1
RATE_LIMIT_FREE_TIER_RPM=10000
SECURITY_MAX_FAILED_LOGIN_ATTEMPTS=100
```

## Monitoring Configuration

Key metrics to monitor:

1. **Cache hit rate** - if low, increase TTL values
2. **Rate limit rejections** - if high, may need to increase limits
3. **Database pool exhaustion** - increase `POOL_SIZE` if occurring
4. **Account lockouts** - adjust `MAX_FAILED_LOGIN_ATTEMPTS` if too frequent

## Summary

All configuration is now:

✅ Centralized in `/quant/backend/app/core/config.py`
✅ Environment-variable configurable
✅ Well-documented with defaults
✅ Backward compatible with existing code
✅ Type-safe with Pydantic validation

This improves maintainability, security, and flexibility of the application.
