# Monitoring Setup Guide

Complete monitoring stack for the Quant Analytics Platform using Prometheus, Grafana, and Sentry.

## Table of Contents

- [Overview](#overview)
- [Architecture](#architecture)
- [Setup Instructions](#setup-instructions)
- [Sentry Integration](#sentry-integration)
- [Prometheus Configuration](#prometheus-configuration)
- [Grafana Dashboards](#grafana-dashboards)
- [Alert Configuration](#alert-configuration)
- [Troubleshooting](#troubleshooting)

## Overview

The monitoring stack provides:

- **Real-time metrics** - Performance, errors, system health
- **Error tracking** - Full stack traces with Sentry
- **Alerting** - Slack/email notifications for critical issues
- **Dashboards** - Visual monitoring with Grafana
- **Logs** - Centralized logging with structured JSON

## Architecture

```
┌─────────────┐
│   FastAPI   │──► Prometheus Metrics (/api/v1/metrics)
│  Backend    │──► Sentry (Errors)
└─────────────┘──► JSON Logs
       │
       ▼
┌─────────────┐
│ Prometheus  │──► Scrapes metrics every 15s
│             │──► Evaluates alert rules
└─────────────┘
       │
       ▼
┌─────────────┐
│  Grafana    │──► Visualizes metrics
│             │──► Custom dashboards
└─────────────┘
       │
       ▼
┌─────────────┐
│   Alerts    │──► Slack notifications
│             │──► Email notifications
└─────────────┘
```

## Setup Instructions

### 1. Sentry Setup

#### Create Sentry Account

1. Go to [sentry.io](https://sentry.io) and sign up
2. Create a new project
3. Select "Python" → "FastAPI"
4. Copy your DSN (looks like: `https://abc123@o0000.ingest.sentry.io/0000`)

#### Configure Sentry

Add to `.env.production`:

```env
SENTRY_DSN=https://YOUR_KEY@o0000000.ingest.sentry.io/0000000
SENTRY_ENVIRONMENT=production
SENTRY_TRACES_SAMPLE_RATE=0.1
SENTRY_PROFILES_SAMPLE_RATE=0.1
```

#### Test Sentry Integration

```bash
# In Python console
import sentry_sdk
sentry_sdk.init(dsn="YOUR_DSN")
sentry_sdk.capture_message("Test message")
```

Check Sentry dashboard for the test message.

### 2. Prometheus Setup

#### Local Development

Prometheus is included in `docker-compose.production.yml`:

```bash
docker-compose -f docker-compose.production.yml up prometheus
```

Access Prometheus UI at: http://localhost:9090

#### Production Deployment

For Railway/DigitalOcean, use Prometheus Cloud or self-host:

```bash
# Download Prometheus
wget https://github.com/prometheus/prometheus/releases/download/v2.45.0/prometheus-2.45.0.linux-amd64.tar.gz
tar xvfz prometheus-*.tar.gz
cd prometheus-*

# Copy our config
cp monitoring/prometheus/prometheus.yml .
cp monitoring/prometheus/alerts.yml .

# Run Prometheus
./prometheus --config.file=prometheus.yml
```

#### Configure Metrics Endpoint

The backend exposes metrics at `/api/v1/metrics`:

```python
# app/api/v1/metrics.py
from prometheus_client import generate_latest, CONTENT_TYPE_LATEST

@router.get("/metrics")
async def metrics():
    return Response(generate_latest(), media_type=CONTENT_TYPE_LATEST)
```

### 3. Grafana Setup

#### Local Development

```bash
docker-compose -f docker-compose.production.yml up grafana
```

Access Grafana at: http://localhost:3001

Default credentials:
- Username: `admin`
- Password: Set via `GRAFANA_ADMIN_PASSWORD` env var

#### Production Deployment

Option 1: Use Grafana Cloud (Recommended)
1. Sign up at [grafana.com](https://grafana.com)
2. Create a new stack
3. Add Prometheus as data source
4. Import dashboards from `monitoring/grafana/dashboards/`

Option 2: Self-host Grafana
```bash
docker run -d \
  -p 3000:3000 \
  --name=grafana \
  -v grafana-storage:/var/lib/grafana \
  -e "GF_SECURITY_ADMIN_PASSWORD=YOUR_PASSWORD" \
  grafana/grafana
```

#### Import Dashboards

1. Navigate to Dashboards → Import
2. Upload JSON files from `monitoring/grafana/dashboards/`
3. Select Prometheus data source

### 4. Configure Alerting

#### Slack Integration

1. Create a Slack webhook:
   - Go to https://api.slack.com/apps
   - Create new app → Incoming Webhooks
   - Activate and create webhook
   - Copy webhook URL

2. Add to `.env.production`:
```env
SLACK_WEBHOOK_URL=https://hooks.slack.com/services/YOUR/WEBHOOK/URL
```

3. Test webhook:
```bash
curl -X POST -H 'Content-type: application/json' \
  --data '{"text":"Test alert from Quant Platform"}' \
  YOUR_WEBHOOK_URL
```

#### Email Alerts

Configure in `prometheus/alertmanager.yml`:

```yaml
receivers:
  - name: 'email'
    email_configs:
      - to: 'alerts@yourdomain.com'
        from: 'prometheus@yourdomain.com'
        smarthost: 'smtp.sendgrid.net:587'
        auth_username: 'apikey'
        auth_password: 'YOUR_SENDGRID_KEY'
```

### 5. Health Check Endpoint

The backend includes a comprehensive health check at `/health`:

```bash
curl https://api.yourdomain.com/health
```

Response:
```json
{
  "status": "healthy",
  "environment": "production",
  "version": "1.0.0",
  "timestamp": "2024-01-15T10:30:00Z",
  "services": {
    "database": "connected",
    "cache": "connected",
    "token_blacklist": "connected"
  }
}
```

### 6. Logging Configuration

Structured JSON logging is configured in `app/core/logging.py`:

```python
# View logs
docker-compose logs -f backend

# Search logs
docker-compose logs backend | grep ERROR

# Export logs
docker-compose logs backend > logs.txt
```

## Prometheus Configuration

### Metrics Collected

#### Application Metrics
- `http_requests_total` - Total HTTP requests
- `http_request_duration_seconds` - Request duration histogram
- `http_requests_in_progress` - Current requests being processed
- `database_query_duration_seconds` - Database query time
- `cache_hits_total` / `cache_misses_total` - Cache performance

#### System Metrics
- `process_cpu_seconds_total` - CPU usage
- `process_resident_memory_bytes` - Memory usage
- `process_open_fds` - Open file descriptors

#### Custom Metrics
- `user_registrations_total` - User signups
- `trades_scraped_total` - Trades collected
- `api_calls_total` - External API calls

### Adding Custom Metrics

```python
from prometheus_client import Counter, Histogram

# Define metric
trades_counter = Counter(
    'trades_scraped_total',
    'Total trades scraped',
    ['source', 'politician']
)

# Use in code
trades_counter.labels(source='senate', politician='john_doe').inc()
```

## Grafana Dashboards

### Available Dashboards

1. **Application Overview** (`application-overview.json`)
   - Request rate and latency
   - Error rates
   - Active users
   - Cache hit rate

2. **Database Performance** (create from template)
   - Query performance
   - Connection pool usage
   - Slow queries
   - Lock contention

3. **System Resources** (create from template)
   - CPU, Memory, Disk usage
   - Network I/O
   - Process counts

### Creating Custom Dashboards

1. In Grafana, click "+" → Dashboard
2. Add panel with PromQL query:
```promql
# Request rate by endpoint
rate(http_requests_total[5m])

# P95 latency
histogram_quantile(0.95, rate(http_request_duration_seconds_bucket[5m]))

# Error rate
rate(http_requests_total{status=~"5.."}[5m]) / rate(http_requests_total[5m])
```

3. Save dashboard and export JSON
4. Commit to `monitoring/grafana/dashboards/`

## Alert Configuration

### Alert Rules

Defined in `prometheus/alerts.yml`:

- **HighErrorRate** - Error rate > 1% for 5 minutes
- **SlowResponseTime** - P95 latency > 1s for 5 minutes
- **APIServiceDown** - Service unavailable for 2 minutes
- **DatabaseConnectionErrors** - Any DB errors in 5 minutes
- **HighMemoryUsage** - Memory > 80% for 5 minutes
- **LowDiskSpace** - Disk < 20% free

### Alert Thresholds

Customize in `.env.production`:

```env
ALERT_ERROR_RATE_THRESHOLD=0.01        # 1%
ALERT_RESPONSE_TIME_THRESHOLD=1000     # 1 second
ALERT_MEMORY_THRESHOLD=80              # 80%
ALERT_DISK_THRESHOLD=20                # 20%
```

### Testing Alerts

Trigger test alert:

```python
# Cause high error rate
for i in range(1000):
    raise Exception("Test error")
```

Check:
1. Prometheus Alerts page: http://localhost:9090/alerts
2. Slack channel for notification
3. Email inbox

## Troubleshooting

### Prometheus Not Scraping Metrics

**Problem**: No data in Prometheus

**Solution**:
```bash
# Check if metrics endpoint is accessible
curl http://localhost:8000/api/v1/metrics

# Check Prometheus targets
# Go to http://localhost:9090/targets
# All targets should show "UP"

# Check Prometheus logs
docker-compose logs prometheus
```

### Grafana Not Showing Data

**Problem**: Dashboards are empty

**Solution**:
1. Check Prometheus data source configuration
2. Test connection: Configuration → Data Sources → Prometheus → Test
3. Verify PromQL queries in Explore view
4. Check time range (last 1 hour by default)

### Sentry Not Receiving Errors

**Problem**: Errors not appearing in Sentry

**Solution**:
```bash
# Verify DSN is set
echo $SENTRY_DSN

# Check network connectivity
curl https://sentry.io

# Test Sentry integration
python scripts/test_sentry.py

# Check backend logs for Sentry errors
docker-compose logs backend | grep -i sentry
```

### Alerts Not Firing

**Problem**: No notifications despite issues

**Solution**:
1. Check alert rules are loaded: http://localhost:9090/alerts
2. Verify alert conditions are met
3. Check Alertmanager is running and configured
4. Test webhook URL manually
5. Check Slack/email credentials

### High Memory Usage

**Problem**: Prometheus using too much memory

**Solution**:
```yaml
# Reduce retention in prometheus.yml
--storage.tsdb.retention.time=15d

# Reduce scrape interval
scrape_interval: 30s
```

### Missing Metrics

**Problem**: Expected metrics not appearing

**Solution**:
```python
# Register metrics at startup
from prometheus_client import REGISTRY
print(list(REGISTRY._collector_to_names.values()))

# Check metric is being updated
# Add debug logging
logger.info(f"Incrementing metric: {metric_name}")
```

## Best Practices

1. **Metric Naming**
   - Use snake_case
   - Include units in name (e.g., `_seconds`, `_bytes`)
   - Use `_total` suffix for counters

2. **Label Cardinality**
   - Keep labels low cardinality (< 1000 unique values)
   - Don't use user IDs as labels
   - Use label values that make sense to aggregate

3. **Dashboard Organization**
   - One dashboard per service/component
   - Include SLIs (error rate, latency, throughput)
   - Add annotations for deployments

4. **Alert Fatigue**
   - Only alert on actionable issues
   - Use appropriate severity levels
   - Include runbook links in alerts
   - Set reasonable thresholds

5. **Data Retention**
   - Production: 30 days (default)
   - Development: 7 days
   - Archive historical data to S3

## Resources

- [Prometheus Documentation](https://prometheus.io/docs/)
- [Grafana Documentation](https://grafana.com/docs/)
- [Sentry FastAPI Integration](https://docs.sentry.io/platforms/python/guides/fastapi/)
- [PromQL Cheat Sheet](https://promlabs.com/promql-cheat-sheet/)

## Support

For monitoring issues:
1. Check this README
2. Review Prometheus/Grafana logs
3. Search [GitHub Issues](https://github.com/yourorg/quant/issues)
4. Contact DevOps team

---

Last Updated: 2024-01-15
