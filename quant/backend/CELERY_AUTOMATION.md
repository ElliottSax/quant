# Celery Task Automation for Congressional Trading Scrapers

Complete guide for automated scraping using Celery task queues.

---

## Table of Contents

1. [Overview](#overview)
2. [Architecture](#architecture)
3. [Installation](#installation)
4. [Configuration](#configuration)
5. [Running Workers](#running-workers)
6. [API Endpoints](#api-endpoints)
7. [Monitoring](#monitoring)
8. [Production Deployment](#production-deployment)
9. [Troubleshooting](#troubleshooting)

---

## Overview

The Celery task system provides:
- **Automated Scheduling**: Daily and weekly scraping via Celery Beat
- **Background Processing**: Non-blocking scraper execution
- **Retry Logic**: Automatic retry on failure (3 attempts, 5 min delay)
- **Task Monitoring**: API endpoints and Flower dashboard
- **Scalability**: Multiple workers can run in parallel

### Scheduled Tasks

1. **Daily Scraping**: Runs at 2 AM UTC daily (1 day back)
2. **Weekly Full Sync**: Runs Sunday 3 AM UTC (7 days back)
3. **Health Check**: Every 5 minutes

---

## Architecture

```
┌─────────────────┐
│  FastAPI App    │
│  (API Endpoint) │
└────────┬────────┘
         │ Triggers
         ▼
┌─────────────────┐      ┌──────────────┐
│  Celery Worker  │◄─────┤ Redis Broker │
│  (Task Executor)│      └──────────────┘
└────────┬────────┘
         │ Runs
         ▼
┌─────────────────┐      ┌──────────────┐
│  Scraper Tasks  │─────►│  PostgreSQL  │
│  (Senate/House) │      │  (Results)   │
└─────────────────┘      └──────────────┘
         ▲
         │ Schedules
┌─────────────────┐
│  Celery Beat    │
│  (Scheduler)    │
└─────────────────┘
```

### Components

1. **Celery Worker**: Executes scraper tasks in background
2. **Celery Beat**: Schedules periodic tasks
3. **Redis**: Message broker for task queue
4. **Flower**: Web-based monitoring dashboard (optional)
5. **FastAPI**: REST API for manual task triggers

---

## Installation

### Prerequisites

```bash
# Redis server (required)
sudo apt-get install redis-server
sudo systemctl start redis
sudo systemctl enable redis

# Verify Redis
redis-cli ping  # Should return "PONG"
```

### Python Dependencies

Already included in `requirements.txt`:

```bash
pip install celery>=5.4.0 flower>=2.0.0
```

---

## Configuration

### Environment Variables

Add to `.env`:

```bash
# Redis/Celery
REDIS_URL=redis://localhost:6379/0
CELERY_BROKER_URL=redis://localhost:6379/0
CELERY_RESULT_BACKEND=redis://localhost:6379/0

# Flower (optional - for monitoring dashboard)
FLOWER_PASSWORD=your_secure_password_here
```

### Celery Configuration

Located in `app/celery_app.py`:

- **Task Timeout**: 1 hour hard limit, 55 minutes soft limit
- **Worker Restart**: After 10 tasks (prevents memory leaks)
- **Task Prefetch**: 1 task at a time (sequential processing)
- **Result Expiration**: 24 hours

---

## Running Workers

### Development Mode

#### 1. Start Redis

```bash
redis-server
# Or use system service:
sudo systemctl start redis
```

#### 2. Start Celery Worker

```bash
cd quant/backend
source venv/bin/activate

# Using startup script (recommended)
./scripts/start_celery_worker.sh

# Or manually
celery -A app.celery_app worker --loglevel=INFO --concurrency=2
```

#### 3. Start Celery Beat (for scheduled tasks)

```bash
# In separate terminal
cd quant/backend
source venv/bin/activate

# Using startup script (recommended)
./scripts/start_celery_beat.sh

# Or manually
celery -A app.celery_app beat --loglevel=INFO
```

#### 4. Start Flower Dashboard (optional)

```bash
# In separate terminal
cd quant/backend
source venv/bin/activate

celery -A app.celery_app flower --port=5555
# Access at: http://localhost:5555
```

### Expected Output

**Worker**:
```
[2025-11-12 10:00:00,000: INFO/MainProcess] Connected to redis://localhost:6379/0
[2025-11-12 10:00:00,010: INFO/MainProcess] mingle: all alone
[2025-11-12 10:00:00,020: INFO/MainProcess] celery@hostname ready.
```

**Beat**:
```
[2025-11-12 10:00:00,000: INFO/MainProcess] beat: Starting...
[2025-11-12 10:00:00,010: INFO/MainProcess] Scheduler: Sending due task scrape-daily
```

---

## API Endpoints

All endpoints are under `/api/v1/tasks`:

### Trigger Scraper Tasks

**Senate Only**:
```bash
POST /api/v1/tasks/scrape/senate
Content-Type: application/json

{
  "days_back": 7,
  "start_date": null,  // Optional: "2024-01-01"
  "end_date": null     // Optional: "2024-01-31"
}

Response:
{
  "task_id": "abc123...",
  "status": "queued",
  "message": "Senate scraper task has been queued"
}
```

**House Only**:
```bash
POST /api/v1/tasks/scrape/house
Content-Type: application/json

{
  "days_back": 7
}
```

**Both Chambers**:
```bash
POST /api/v1/tasks/scrape/all
Content-Type: application/json

{
  "days_back": 30
}
```

### Monitor Tasks

**Get Task Status**:
```bash
GET /api/v1/tasks/status/{task_id}

Response:
{
  "task_id": "abc123...",
  "status": "SUCCESS",  // Or "PENDING", "STARTED", "FAILURE"
  "result": {
    "status": "success",
    "chamber": "senate",
    "stats": {
      "total": 150,
      "saved": 145,
      "skipped": 3,
      "errors": 2
    }
  }
}
```

**Active Tasks**:
```bash
GET /api/v1/tasks/active

Response:
{
  "active_tasks": [
    {
      "worker": "celery@hostname",
      "task_id": "abc123...",
      "task_name": "app.tasks.scraper_tasks.scrape_senate",
      "args": [],
      "kwargs": {"days_back": 7}
    }
  ],
  "worker_count": 1
}
```

**Scheduled Tasks**:
```bash
GET /api/v1/tasks/scheduled

Response:
{
  "scheduled_tasks": [...],
  "worker_count": 1
}
```

**Worker Statistics**:
```bash
GET /api/v1/tasks/stats

Response:
{
  "status": "ok",
  "workers": {
    "celery@hostname": {
      "pool_size": 2,
      "active_tasks": 1,
      "total_tasks": {...}
    }
  },
  "worker_count": 1
}
```

**Cancel Task**:
```bash
POST /api/v1/tasks/cancel/{task_id}

Response:
{
  "status": "cancelled",
  "task_id": "abc123...",
  "message": "Task has been cancelled"
}
```

**Health Check**:
```bash
GET /api/v1/tasks/health

Response:
{
  "status": "healthy",  // Or "unhealthy"
  "message": "Task system is operational",
  "workers": 1
}
```

---

## Monitoring

### Using Flower Dashboard

Flower provides a web-based monitoring dashboard:

```bash
# Start Flower
celery -A app.celery_app flower --port=5555

# Access dashboard
http://localhost:5555
```

**Features**:
- Real-time task monitoring
- Task history and statistics
- Worker information
- Task retry and termination
- Resource usage graphs

### Using CLI

```bash
# List active tasks
celery -A app.celery_app inspect active

# List scheduled tasks
celery -A app.celery_app inspect scheduled

# Worker statistics
celery -A app.celery_app inspect stats

# Registered tasks
celery -A app.celery_app inspect registered

# Purge all tasks
celery -A app.celery_app purge
```

### Logs

**Worker Logs**:
```bash
# Console output
# Or if running as systemd service:
sudo journalctl -u celery-worker -f
tail -f /var/log/celery/worker.log
```

**Beat Logs**:
```bash
sudo journalctl -u celery-beat -f
tail -f /var/log/celery/beat.log
```

---

## Production Deployment

### Using Systemd Services

#### 1. Install Services

```bash
cd quant/backend
sudo ./deployment/install_systemd_services.sh
```

This installs:
- `celery-worker.service`: Background task executor
- `celery-beat.service`: Task scheduler
- `celery-flower.service`: Monitoring dashboard (optional)

#### 2. Start Services

```bash
# Start worker
sudo systemctl start celery-worker

# Start beat scheduler
sudo systemctl start celery-beat

# Start Flower (optional)
sudo systemctl start celery-flower

# Enable on boot
sudo systemctl enable celery-worker celery-beat celery-flower
```

#### 3. Check Status

```bash
# Worker status
sudo systemctl status celery-worker

# Beat status
sudo systemctl status celery-beat

# Flower status
sudo systemctl status celery-flower
```

#### 4. View Logs

```bash
# Worker logs
sudo journalctl -u celery-worker -f

# Beat logs
sudo journalctl -u celery-beat -f

# Or file logs
tail -f /var/log/celery/worker.log
tail -f /var/log/celery/beat.log
```

### Service Management

```bash
# Restart services
sudo systemctl restart celery-worker
sudo systemctl restart celery-beat

# Stop services
sudo systemctl stop celery-worker
sudo systemctl stop celery-beat

# Reload configuration (graceful)
sudo systemctl reload celery-worker
```

### Scaling Workers

To run multiple workers:

```bash
# Copy and rename service file
sudo cp /etc/systemd/system/celery-worker.service /etc/systemd/system/celery-worker@.service

# Start multiple instances
sudo systemctl start celery-worker@1
sudo systemctl start celery-worker@2
sudo systemctl start celery-worker@3
```

---

## Troubleshooting

### Worker Won't Start

**Error**: "Cannot connect to Redis"

```bash
# Check Redis is running
systemctl status redis
redis-cli ping

# Check Redis URL in .env
echo $REDIS_URL

# Test connection
redis-cli -u $REDIS_URL ping
```

**Error**: "Database connection failed"

```bash
# Verify DATABASE_URL
echo $DATABASE_URL

# Test connection
psql $DATABASE_URL -c "SELECT 1;"
```

### Tasks Not Executing

**Check worker is running**:
```bash
celery -A app.celery_app inspect active
# Should show worker hostname
```

**Check task is registered**:
```bash
celery -A app.celery_app inspect registered
# Should list: app.tasks.scraper_tasks.scrape_senate, etc.
```

**Check task queue**:
```bash
redis-cli LLEN celery
# Shows number of queued tasks
```

**Purge stuck tasks**:
```bash
celery -A app.celery_app purge
```

### Beat Not Scheduling

**Check beat is running**:
```bash
ps aux | grep celery | grep beat
```

**Remove stale schedule**:
```bash
rm celerybeat-schedule.db
sudo systemctl restart celery-beat
```

**View beat schedule**:
```bash
celery -A app.celery_app inspect scheduled
```

### Task Failures

**View task result**:
```bash
# In Python
from celery.result import AsyncResult
result = AsyncResult('task-id-here')
print(result.status)
print(result.result)
print(result.traceback)
```

**Common issues**:
1. **Chrome not found**: Install chromium-browser
2. **Database timeout**: Increase task_soft_time_limit
3. **Memory leak**: Reduce worker_max_tasks_per_child

### High Memory Usage

**Restart workers periodically**:
```bash
# Already configured: max_tasks_per_child=10
```

**Monitor memory**:
```bash
# Worker memory usage
ps aux | grep celery | awk '{print $6/1024 " MB - " $11}'
```

**Adjust concurrency**:
```bash
# Reduce concurrent tasks
celery -A app.celery_app worker --concurrency=1
```

---

## Task Development

### Creating New Tasks

```python
from app.celery_app import celery_app

@celery_app.task(
    name="app.tasks.my_task",
    bind=True,
    max_retries=3,
    default_retry_delay=300,
)
def my_task(self, arg1, arg2):
    """My custom task."""
    try:
        # Task logic here
        result = do_something(arg1, arg2)
        return {"status": "success", "result": result}
    except Exception as exc:
        if self.request.retries < self.max_retries:
            raise self.retry(exc=exc)
        return {"status": "error", "error": str(exc)}
```

### Adding to Beat Schedule

Edit `app/celery_app.py`:

```python
celery_app.conf.beat_schedule.update({
    "my-periodic-task": {
        "task": "app.tasks.my_task",
        "schedule": 3600,  # Every hour
        "kwargs": {"arg1": "value1"},
    },
})
```

### Testing Tasks Locally

```python
# Direct execution (synchronous)
from app.tasks.scraper_tasks import scrape_senate
result = scrape_senate(days_back=1)
print(result)

# Async execution (requires worker)
task = scrape_senate.delay(days_back=1)
print(f"Task ID: {task.id}")
print(f"Status: {task.status}")
result = task.get(timeout=3600)  # Wait for completion
print(result)
```

---

## Performance Tuning

### Worker Settings

```bash
# More concurrent tasks (more memory)
--concurrency=4

# Fewer tasks per worker (less memory leaks)
--max-tasks-per-child=5

# Prefetch more tasks (faster throughput)
--prefetch-multiplier=2
```

### Task Settings

```python
# Longer timeout for slow scrapers
task_time_limit=7200  # 2 hours
task_soft_time_limit=6900  # 1h 55min

# More aggressive retries
max_retries=5
default_retry_delay=60  # 1 minute
```

### Redis Optimization

```bash
# Increase Redis maxmemory
redis-cli CONFIG SET maxmemory 2gb
redis-cli CONFIG SET maxmemory-policy allkeys-lru
```

---

## Security Considerations

1. **Redis Authentication**: Use password protection
   ```bash
   # In redis.conf
   requirepass your_secure_password

   # In .env
   REDIS_URL=redis://:your_secure_password@localhost:6379/0
   ```

2. **Flower Access Control**: Enable basic auth
   ```bash
   celery -A app.celery_app flower --basic_auth=admin:password
   ```

3. **Task Argument Sanitization**: Validate all inputs

4. **Result Backend Security**: Use encrypted connection for production

---

## Next Steps

1. ✅ Install Redis and start worker
2. ✅ Test manual task triggers via API
3. ✅ Set up systemd services for production
4. ✅ Configure Flower dashboard
5. ✅ Set up monitoring and alerting
6. ⏭️ **Phase 3**: Data enrichment and analytics
