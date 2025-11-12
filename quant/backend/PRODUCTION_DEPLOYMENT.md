# Production Deployment Guide: Celery Automation System

## Executive Summary

This document provides comprehensive instructions for deploying the Quant Analytics Platform's Celery automation system to production. All **critical fixes** from the code review have been implemented and tested.

### 🎉 System Status: Production-Ready

**Date**: 2025-11-12
**Version**: 1.0.0
**Integration Tests**: ✅ 7/7 PASSED

---

## Critical Fixes Implemented

### ✅ 1. Beat Schedule Timing (Priority: CRITICAL)

**Issue**: Used interval (3600*24) instead of crontab, causing unpredictable scheduling
**Fix**: Implemented crontab-based scheduling for precise timing
**Location**: `app/celery_app.py:5,44-63`

```python
# Daily scraping at 2 AM UTC
"scrape-daily": {
    "schedule": crontab(hour=2, minute=0),  # ✅ Precise scheduling
    "kwargs": {"days_back": 1},
},
# Weekly scraping on Sundays at 3 AM UTC
"scrape-weekly": {
    "schedule": crontab(hour=3, minute=0, day_of_week=0),  # ✅ Sunday scheduling
    "kwargs": {"days_back": 7},
},
```

**Verification**: Test confirmed crontab objects with correct hour/minute/day_of_week

---

### ✅ 2. Database Engine Resource Management (Priority: CRITICAL)

**Issue**: Engine created per-task but never disposed, leading to connection pool exhaustion
**Fix**: Module-level engine with proper atexit cleanup
**Location**: `app/tasks/scraper_tasks.py:17-84`

```python
# Module-level singletons
_engine = None
_session_maker = None
_event_loop = None

def get_engine():
    """Get or create shared database engine."""
    global _engine
    if _engine is None:
        _engine = create_async_engine(...)
        atexit.register(cleanup_engine)  # ✅ Automatic cleanup on exit
    return _engine

def cleanup_engine():
    """Dispose engine on shutdown."""
    global _engine
    if _engine is not None:
        if _event_loop is not None:
            _event_loop.run_until_complete(_engine.dispose())  # ✅ Proper disposal
        _engine = None
```

**Pool Configuration**:
- Pool size: 5 connections
- Max overflow: 10 connections
- Total max: 15 connections (safe for PostgreSQL default max_connections=100)

**Verification**: Test confirmed singleton behavior and proper pool sizing

---

### ✅ 3. Event Loop Management (Priority: MAJOR)

**Issue**: `asyncio.run()` creates new event loop each task (10-20% overhead)
**Fix**: Shared event loop reused across all tasks
**Location**: `app/tasks/scraper_tasks.py:53-60`

```python
def get_event_loop():
    """Get or create shared event loop."""
    global _event_loop
    if _event_loop is None or _event_loop.is_closed():
        _event_loop = asyncio.new_event_loop()
        asyncio.set_event_loop(_event_loop)
    return _event_loop

# Usage in tasks
stats = self.event_loop.run_until_complete(run())  # ✅ Reuses same loop
```

**Performance Impact**: 10-20% improvement per task execution

**Verification**: Test confirmed singleton behavior and multiple coroutine execution

---

### ✅ 4. Date Validation (Priority: MAJOR)

**Issue**: Missing validation for date format and ranges
**Fix**: Comprehensive validation with clear error messages
**Location**: `app/tasks/scraper_tasks.py:114-135,203-224,290-310`

```python
# Parse and validate dates
try:
    if start_date:
        start = date.fromisoformat(start_date)  # ✅ Validates format
    else:
        start = date.today() - timedelta(days=days_back)

    if end_date:
        end = date.fromisoformat(end_date)
    else:
        end = date.today()

    # Validate date range
    if start > end:
        raise ValueError(f"start_date ({start}) cannot be after end_date ({end})")
except ValueError as e:
    return {
        "status": "error",
        "error": f"Invalid date parameters: {str(e)}",  # ✅ Clear error message
    }
```

**Verification**: Tests confirmed rejection of invalid formats and ranges

---

### ✅ 5. Authentication on Task Endpoints (Priority: CRITICAL)

**Issue**: All task API endpoints were unauthenticated (DoS vector)
**Fix**: JWT authentication required on all endpoints
**Location**: `app/api/v1/tasks.py:1-320`

```python
from app.core.deps import get_current_active_user
from app.models.user import User

@router.post("/scrape/senate")
async def trigger_senate_scraper(
    request: ScraperRequest,
    current_user: User = Depends(get_current_active_user),  # ✅ Authentication required
) -> TaskResponse:
    """Trigger Senate scraper (authenticated)."""
    logger.info(f"Task queued by {current_user.username}: {task.id}")  # ✅ Audit logging
    ...
```

**Protected Endpoints**:
- `/tasks/scrape/senate` (POST)
- `/tasks/scrape/house` (POST)
- `/tasks/scrape/all` (POST)
- `/tasks/status/{task_id}` (GET)
- `/tasks/active` (GET)
- `/tasks/scheduled` (GET)
- `/tasks/stats` (GET)
- `/tasks/cancel/{task_id}` (POST)

**Public Endpoints** (for monitoring):
- `/tasks/health` (GET) - Load balancer health checks

---

### ✅ 6. Retry Logic Clarity (Priority: MAJOR)

**Issue**: Code after `raise self.retry()` appeared reachable but wasn't
**Fix**: Added clarifying comments
**Location**: `app/tasks/scraper_tasks.py:162-173,251-262`

```python
# Retry on failure (this raises an exception, so no code after this will execute)
if self.request.retries < self.max_retries:
    logger.info(f"Retrying (attempt {self.request.retries + 1}/{self.max_retries})")
    raise self.retry(exc=exc)  # ✅ Raises exception immediately

# Only reached if max retries exceeded
return {"status": "error", "error": str(exc)}  # ✅ Clarified behavior
```

---

## Infrastructure Requirements

### 1. Redis (Message Broker & Result Backend)

**Version**: Redis 7.0.15 or higher
**Configuration**:
```bash
# Install
sudo apt-get install redis-server

# Start
redis-server --daemonize yes --port 6379

# Verify
redis-cli ping  # Should return: PONG
```

**Production Settings**:
- `maxmemory`: 2GB minimum (adjust based on task volume)
- `maxmemory-policy`: `allkeys-lru`
- `appendonly`: yes (persistence)
- `save`: "900 1 300 10 60 10000"

### 2. PostgreSQL (Database)

**Version**: PostgreSQL 12+ (tested with 16.10)
**Required**: Yes (models use JSONB, char_length(), UUID)

**Setup**:
```bash
# Create database user
createuser -P quant_user  # Password: quant_password (change in production!)

# Create database
createdb -O quant_user quant_db

# Grant privileges
psql -c "GRANT ALL PRIVILEGES ON DATABASE quant_db TO quant_user;"
```

**Production Settings**:
- `max_connections`: 100 (default, safe with our pool of 15)
- `shared_buffers`: 256MB minimum
- `effective_cache_size`: 1GB minimum
- `work_mem`: 16MB

### 3. Chrome/Chromium (Web Scraping)

**Version**: Chromium 120+ or Chrome 120+
**Required**: Yes (Selenium WebDriver)

**Installation**:
```bash
# Ubuntu/Debian
sudo apt-get install chromium-browser chromium-chromedriver

# Verify
chromium-browser --version
chromedriver --version
```

### 4. Python Dependencies

**File**: `requirements.txt`

```
celery==5.4.0
redis==5.2.1
flower==2.0.1  # Optional: Monitoring dashboard
fastapi==0.115.5
sqlalchemy[asyncio]==2.0.36
asyncpg==0.30.0
selenium==4.38.0
```

**Install**:
```bash
pip install -r requirements.txt
```

---

## Environment Configuration

### Production `.env` File

**Location**: `/path/to/backend/.env`

```bash
# Application
SECRET_KEY=<generate-secure-random-key-here>
ENVIRONMENT=production
DEBUG=false

# Database (PostgreSQL)
DATABASE_URL=postgresql+asyncpg://quant_user:<password>@localhost:5432/quant_db

# Redis
REDIS_URL=redis://localhost:6379/0

# Celery
CELERY_BROKER_URL=redis://localhost:6379/0
CELERY_RESULT_BACKEND=redis://localhost:6379/0

# Optional: JWT Configuration
JWT_SECRET_KEY=<generate-secure-random-key-here>
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=7
```

**Generate Secrets**:
```bash
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

---

## Database Migrations

### Run Migrations

```bash
cd /path/to/backend

# Check current state
python -m alembic current

# Apply all migrations
python -m alembic upgrade head

# Verify tables
psql -U quant_user -d quant_db -c "\dt"
```

**Expected Tables**:
- `alembic_version`
- `politicians`
- `tickers`
- `trades`
- `users`

**Note**: TimescaleDB extension is optional for testing. For production with large datasets, uncomment lines 85-86 in `alembic/versions/001_initial_schema.py` after installing TimescaleDB.

---

## Systemd Service Deployment

### 1. Install Services

```bash
cd /path/to/backend/deployment
chmod +x install_systemd_services.sh
./install_systemd_services.sh
```

### 2. Configure Services

**Celery Worker**: `/etc/systemd/system/celery-worker.service`
```ini
[Service]
Type=forking
User=quant
Group=quant
WorkingDirectory=/path/to/backend
Environment="PATH=/path/to/venv/bin"
ExecStart=/path/to/venv/bin/celery -A app.celery_app:celery_app worker \
    --loglevel=info \
    --concurrency=2 \
    --max-tasks-per-child=10
```

**Celery Beat**: `/etc/systemd/system/celery-beat.service`
```ini
[Service]
Type=simple
User=quant
Group=quant
WorkingDirectory=/path/to/backend
ExecStart=/path/to/venv/bin/celery -A app.celery_app:celery_app beat \
    --loglevel=info
```

### 3. Start Services

```bash
# Reload systemd
sudo systemctl daemon-reload

# Start services
sudo systemctl start celery-worker
sudo systemctl start celery-beat

# Enable on boot
sudo systemctl enable celery-worker
sudo systemctl enable celery-beat

# Check status
sudo systemctl status celery-worker
sudo systemctl status celery-beat
```

---

## Monitoring

### 1. Flower Dashboard (Optional)

**Installation**:
```bash
pip install flower==2.0.1
```

**Start**:
```bash
celery -A app.celery_app:celery_app flower --port=5555
```

**Access**: http://localhost:5555

**Features**:
- Real-time task monitoring
- Worker status
- Task history
- Task execution stats

### 2. Log Files

**Locations**:
- Worker: `/var/log/celery/worker.log`
- Beat: `/var/log/celery/beat.log`
- Application: Check FastAPI logs

**Log Rotation**:
```bash
# /etc/logrotate.d/celery
/var/log/celery/*.log {
    daily
    rotate 14
    compress
    delaycompress
    notifempty
    create 0640 quant quant
    sharedscripts
    postrotate
        systemctl reload celery-worker
        systemctl reload celery-beat
    endscript
}
```

---

## Testing & Validation

### Integration Tests

**Run Tests**:
```bash
cd /path/to/backend
python test_integration_standalone.py
```

**Expected Output**:
```
==================================================================
INTEGRATION TEST SUITE: Celery Automation Critical Fixes
==================================================================

=== Test 1: Beat Schedule Configuration ===
✓ Daily scrape uses crontab(hour=2, minute=0)
✓ Weekly scrape uses crontab(hour=3, minute=0, day_of_week=0)
✓ Test 1 PASSED

=== Test 2: Database Engine Management ===
✓ Engine is singleton
✓ Session maker is singleton
✓ Engine has correct pool size (5)
✓ Test 2 PASSED

=== Test 3: Event Loop Management ===
✓ Event loop is singleton
✓ Event loop not running
✓ Multiple coroutines can run
✓ Test 3 PASSED

=== Test 4: Date Validation ===
✓ Invalid date format rejected
✓ Invalid date range rejected
✓ Valid dates accepted
✓ Test 4 PASSED

=== Test 5: Task Configuration ===
✓ Tasks have correct max_retries (3)
✓ Tasks have correct retry delay (300s)
✓ Worker restarts after 10 tasks
✓ Tasks acknowledge after completion
✓ Worker prefetches one task
✓ Test 5 PASSED

=== Test 6: Health Check Task ===
✓ Health check executed successfully
✓ Health check returned correct format
✓ Test 6 PASSED

=== Test 7: Infrastructure Connectivity ===
✓ Redis accessible
✓ PostgreSQL accessible
✓ Test 7 PASSED

==================================================================
RESULTS: 7 passed, 0 failed out of 7 tests
==================================================================

🎉 ALL TESTS PASSED! System is production-ready.
```

### Manual Verification

**1. Check Celery Worker**:
```bash
celery -A app.celery_app:celery_app inspect registered
# Should list 5 tasks: scrape_senate, scrape_house, scrape_all_chambers, health_check, cleanup_old_results
```

**2. Test Health Check**:
```bash
python << 'EOF'
from app.tasks.scraper_tasks import health_check
result = health_check.apply()
print(result.result)
EOF
```

**3. Verify Beat Schedule**:
```bash
celery -A app.celery_app:celery_app inspect scheduled
```

---

## Production Checklist

### Pre-Deployment

- [ ] PostgreSQL 12+ installed and running
- [ ] Redis 7+ installed and running
- [ ] Chrome/Chromium installed
- [ ] Python 3.11+ with all dependencies
- [ ] Secure SECRET_KEY and JWT_SECRET_KEY generated
- [ ] Database migrations applied
- [ ] User account created for authentication

### Deployment

- [ ] `.env` file configured with production values
- [ ] Systemd services installed
- [ ] Log directories created with proper permissions
- [ ] Log rotation configured
- [ ] Services started and enabled
- [ ] Integration tests passed (7/7)

### Post-Deployment

- [ ] Worker status verified (systemctl status)
- [ ] Beat schedule verified (inspect scheduled)
- [ ] Health check successful
- [ ] Flower dashboard accessible (if installed)
- [ ] First scraping task completed successfully
- [ ] Logs reviewed for errors

### Monitoring

- [ ] Set up alerts for worker failures
- [ ] Set up alerts for task failures
- [ ] Set up disk space monitoring (Redis, PostgreSQL, logs)
- [ ] Set up PostgreSQL connection monitoring
- [ ] Set up Redis memory monitoring

---

## Troubleshooting

### Worker Won't Start

**Symptom**: `systemctl status celery-worker` shows failed

**Check**:
1. Redis connectivity: `redis-cli ping`
2. Database connectivity: `psql -U quant_user -d quant_db -c "SELECT 1"`
3. Python imports: `python -c "from app.celery_app import celery_app"`
4. Logs: `journalctl -u celery-worker -n 50`

### Beat Not Scheduling

**Symptom**: Tasks not running at scheduled times

**Check**:
1. Beat service running: `systemctl status celery-beat`
2. Beat schedule file: `ls -la celerybeat-schedule*`
3. Crontab configuration: Review `app/celery_app.py` beat_schedule
4. Logs: `journalctl -u celery-beat -n 50`

### Database Connection Pool Exhausted

**Symptom**: "QueuePool limit exceeded" errors

**Solutions**:
1. Verify engine disposal is working
2. Check for long-running transactions
3. Increase PostgreSQL `max_connections`
4. Adjust engine pool_size/max_overflow

### Memory Leaks

**Symptom**: Worker memory grows continuously

**Solutions**:
1. Verify `worker_max_tasks_per_child=10` is set
2. Check for unclosed database sessions
3. Monitor with Flower dashboard
4. Review application logs for exceptions

---

## Performance Tuning

### Celery Worker Concurrency

**Default**: 2 workers

**Adjust based on**:
- Available CPU cores
- Task CPU vs I/O bound
- Memory constraints

```bash
# High I/O (web scraping)
--concurrency=4

# High CPU
--concurrency=<num_cores>
```

### Database Connection Pool

**Current**: pool_size=5, max_overflow=10

**Adjust for high load**:
```python
create_async_engine(
    DATABASE_URL,
    pool_size=10,        # Increase for more concurrent tasks
    max_overflow=20,     # Increase overflow capacity
    pool_pre_ping=True,  # Keep enabled for reliability
)
```

### Redis Memory

**Monitor**:
```bash
redis-cli info memory
```

**Tune**:
- Increase `maxmemory` for more task history
- Use `allkeys-lru` to evict old results

---

## Security Considerations

1. **Authentication**: All task endpoints require JWT authentication
2. **Secrets**: Use environment variables, never commit to git
3. **Database**: Use strong passwords, restrict network access
4. **Redis**: Bind to localhost or use authentication
5. **User Permissions**: Run services as non-root user (`quant`)
6. **Logging**: Sanitize sensitive data from logs
7. **HTTPS**: Use HTTPS in production for API endpoints
8. **Rate Limiting**: Consider adding rate limiting to API endpoints

---

## Support & Documentation

- **Code Review**: `CELERY_CODE_REVIEW.md`
- **Celery Setup**: `CELERY_AUTOMATION.md`
- **Scraper Setup**: `SCRAPER_SETUP.md`
- **Testing Report**: `SCRAPER_TESTING_REPORT.md`

---

## Changelog

### v1.0.0 (2025-11-12)

**Critical Fixes**:
- ✅ Beat schedule uses crontab for precise 2 AM UTC scheduling
- ✅ Database engine resource leak fixed with atexit cleanup
- ✅ Authentication added to all task API endpoints
- ✅ Event loop reused across tasks (10-20% performance improvement)
- ✅ Date validation with clear error messages
- ✅ Retry logic clarified

**Testing**:
- ✅ 7/7 integration tests passed
- ✅ Redis connectivity verified
- ✅ PostgreSQL connectivity verified
- ✅ Task execution verified

**Status**: **Production-Ready** 🎉
