# MONITORING & OBSERVABILITY GUIDE

## Overview

Complete guide for production monitoring, logging, metrics, and alerting.

---

## 📊 Monitoring Stack

### Recommended Tools

1. **Application Monitoring:** Sentry (errors & performance)
2. **Metrics:** Prometheus + Grafana
3. **Logs:** ELK Stack (Elasticsearch, Logstash, Kibana) or Loki
4. **Uptime:** UptimeRobot or Pingdom
5. **APM:** New Relic, Datadog, or Open Telemetry

---

## 🔍 Application Metrics

### Custom Metrics Implementation

```python
# app/core/metrics.py
"""
Prometheus metrics for application monitoring.
"""

from prometheus_client import Counter, Histogram, Gauge, Info
from functools import wraps
import time

# HTTP Request metrics
http_requests_total = Counter(
    'http_requests_total',
    'Total HTTP requests',
    ['method', 'endpoint', 'status']
)

http_request_duration = Histogram(
    'http_request_duration_seconds',
    'HTTP request duration',
    ['method', 'endpoint']
)

# Authentication metrics
auth_attempts_total = Counter(
    'auth_attempts_total',
    'Total authentication attempts',
    ['result']  # success, failed, locked
)

auth_failures_total = Counter(
    'auth_failures_total',
    'Failed authentication attempts',
    ['reason']  # wrong_password, user_not_found, account_locked
)

# Database metrics
db_query_duration = Histogram(
    'db_query_duration_seconds',
    'Database query duration',
    ['query_type']  # select, insert, update, delete
)

db_connection_pool = Gauge(
    'db_connection_pool_size',
    'Database connection pool status',
    ['status']  # checked_out, checked_in, overflow
)

# Cache metrics
cache_hits_total = Counter(
    'cache_hits_total',
    'Total cache hits',
    ['cache_type']  # redis, memory
)

cache_misses_total = Counter(
    'cache_misses_total',
    'Total cache misses',
    ['cache_type']
)

# Business metrics
trades_processed_total = Counter(
    'trades_processed_total',
    'Total trades processed',
    ['transaction_type']  # buy, sell
)

api_errors_total = Counter(
    'api_errors_total',
    'Total API errors',
    ['error_type', 'endpoint']
)

# Application info
app_info = Info(
    'app_info',
    'Application information'
)

app_info.info({
    'version': settings.VERSION,
    'environment': settings.ENVIRONMENT,
})


def track_request_metrics(func):
    """Decorator to track HTTP request metrics."""
    @wraps(func)
    async def wrapper(*args, **kwargs):
        start_time = time.time()

        try:
            response = await func(*args, **kwargs)
            status = response.status_code
            result = 'success'
        except Exception as e:
            status = 500
            result = 'error'
            raise
        finally:
            duration = time.time() - start_time

            # Record metrics
            http_requests_total.labels(
                method='GET',  # Get from request
                endpoint=func.__name__,
                status=status
            ).inc()

            http_request_duration.labels(
                method='GET',
                endpoint=func.__name__
            ).observe(duration)

        return response

    return wrapper
```

### Add Metrics Endpoint

```python
# app/main.py

from prometheus_client import make_asgi_app

# Mount Prometheus metrics endpoint
metrics_app = make_asgi_app()
app.mount("/metrics", metrics_app)


@app.on_event("startup")
async def startup_metrics():
    """Initialize metrics on startup."""
    from app.core.metrics import db_connection_pool
    from app.core.database import get_pool_status

    # Update connection pool metrics periodically
    async def update_pool_metrics():
        while True:
            status = await get_pool_status()
            db_connection_pool.labels(status='checked_out').set(status['checked_out'])
            db_connection_pool.labels(status='checked_in').set(status['checked_in'])
            db_connection_pool.labels(status='overflow').set(status['overflow'])
            await asyncio.sleep(10)

    asyncio.create_task(update_pool_metrics())
```

---

## 📈 Prometheus Configuration

### prometheus.yml

```yaml
global:
  scrape_interval: 15s
  evaluation_interval: 15s

# Alertmanager configuration
alerting:
  alertmanagers:
    - static_configs:
        - targets:
            - alertmanager:9093

# Load rules once and periodically evaluate them
rule_files:
  - "alerts.yml"

scrape_configs:
  # Backend API
  - job_name: 'quant-backend'
    static_configs:
      - targets: ['backend:8000']
    metrics_path: '/metrics'
    scrape_interval: 10s

  # PostgreSQL
  - job_name: 'postgres'
    static_configs:
      - targets: ['postgres-exporter:9187']

  # Redis
  - job_name: 'redis'
    static_configs:
      - targets: ['redis-exporter:9121']

  # Node exporter (system metrics)
  - job_name: 'node'
    static_configs:
      - targets: ['node-exporter:9100']
```

### alerts.yml

```yaml
groups:
  - name: backend_alerts
    interval: 30s
    rules:
      # High error rate
      - alert: HighErrorRate
        expr: rate(http_requests_total{status=~"5.."}[5m]) > 0.05
        for: 2m
        labels:
          severity: critical
        annotations:
          summary: "High error rate detected"
          description: "Error rate is {{ $value | humanizePercentage }}"

      # High response time
      - alert: HighResponseTime
        expr: histogram_quantile(0.95, rate(http_request_duration_seconds_bucket[5m])) > 1.0
        for: 5m
        labels:
          severity: warning
        annotations:
          summary: "High API response time"
          description: "95th percentile response time: {{ $value }}s"

      # Database connection pool exhaustion
      - alert: DatabasePoolExhausted
        expr: db_connection_pool{status="overflow"} > 30
        for: 2m
        labels:
          severity: critical
        annotations:
          summary: "Database connection pool near exhaustion"
          description: "Overflow connections: {{ $value }}"

      # High authentication failure rate
      - alert: HighAuthFailureRate
        expr: rate(auth_failures_total[5m]) > 10
        for: 2m
        labels:
          severity: warning
        annotations:
          summary: "High authentication failure rate"
          description: "Possible brute force attack: {{ $value }} failures/sec"

      # Cache miss rate too high
      - alert: HighCacheMissRate
        expr: |
          rate(cache_misses_total[5m]) /
          (rate(cache_hits_total[5m]) + rate(cache_misses_total[5m])) > 0.8
        for: 5m
        labels:
          severity: warning
        annotations:
          summary: "High cache miss rate"
          description: "Cache effectiveness: {{ $value | humanizePercentage }}"

      # Service down
      - alert: ServiceDown
        expr: up{job="quant-backend"} == 0
        for: 1m
        labels:
          severity: critical
        annotations:
          summary: "Backend service is down"
          description: "Backend has been down for more than 1 minute"

  - name: database_alerts
    interval: 30s
    rules:
      # Database down
      - alert: DatabaseDown
        expr: up{job="postgres"} == 0
        for: 1m
        labels:
          severity: critical
        annotations:
          summary: "PostgreSQL is down"

      # High database query time
      - alert: SlowDatabaseQueries
        expr: histogram_quantile(0.95, rate(db_query_duration_seconds_bucket[5m])) > 1.0
        for: 5m
        labels:
          severity: warning
        annotations:
          summary: "Slow database queries detected"
          description: "95th percentile query time: {{ $value }}s"

  - name: redis_alerts
    interval: 30s
    rules:
      # Redis down
      - alert: RedisDown
        expr: up{job="redis"} == 0
        for: 1m
        labels:
          severity: high
        annotations:
          summary: "Redis is down"

      # Redis memory high
      - alert: RedisMemoryHigh
        expr: redis_memory_used_bytes / redis_memory_max_bytes > 0.9
        for: 5m
        labels:
          severity: warning
        annotations:
          summary: "Redis memory usage high"
          description: "Redis using {{ $value | humanizePercentage }} of available memory"
```

---

## 📊 Grafana Dashboards

### Backend API Dashboard

```json
{
  "dashboard": {
    "title": "Quant Analytics - Backend API",
    "panels": [
      {
        "title": "Request Rate",
        "targets": [
          {
            "expr": "rate(http_requests_total[5m])",
            "legendFormat": "{{method}} {{endpoint}}"
          }
        ]
      },
      {
        "title": "Response Time (p95)",
        "targets": [
          {
            "expr": "histogram_quantile(0.95, rate(http_request_duration_seconds_bucket[5m]))",
            "legendFormat": "{{endpoint}}"
          }
        ]
      },
      {
        "title": "Error Rate",
        "targets": [
          {
            "expr": "rate(http_requests_total{status=~\"5..\"}[5m])",
            "legendFormat": "{{endpoint}}"
          }
        ]
      },
      {
        "title": "Database Connection Pool",
        "targets": [
          {
            "expr": "db_connection_pool",
            "legendFormat": "{{status}}"
          }
        ]
      },
      {
        "title": "Cache Hit Rate",
        "targets": [
          {
            "expr": "rate(cache_hits_total[5m]) / (rate(cache_hits_total[5m]) + rate(cache_misses_total[5m]))",
            "legendFormat": "Hit Rate"
          }
        ]
      }
    ]
  }
}
```

---

## 🔔 Alerting Channels

### Slack Integration

```python
# app/core/alerting.py
"""
Alerting integrations for critical events.
"""

import httpx
from app.core.config import settings
from app.core.logging import get_logger

logger = get_logger(__name__)


async def send_slack_alert(
    title: str,
    message: str,
    severity: str = "info",
    channel: str = "#alerts"
):
    """
    Send alert to Slack.

    Args:
        title: Alert title
        message: Alert message
        severity: Alert severity (info, warning, critical)
        channel: Slack channel
    """
    if not settings.SLACK_WEBHOOK_URL:
        logger.warning("Slack webhook not configured")
        return

    colors = {
        "info": "#36a64f",
        "warning": "#ff9900",
        "critical": "#ff0000"
    }

    payload = {
        "channel": channel,
        "username": "Quant Analytics Monitor",
        "icon_emoji": ":robot_face:",
        "attachments": [
            {
                "color": colors.get(severity, "#36a64f"),
                "title": title,
                "text": message,
                "footer": f"Environment: {settings.ENVIRONMENT}",
                "ts": int(datetime.utcnow().timestamp())
            }
        ]
    }

    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                settings.SLACK_WEBHOOK_URL,
                json=payload,
                timeout=5.0
            )
            response.raise_for_status()
            logger.info(f"Slack alert sent: {title}")
    except Exception as e:
        logger.error(f"Failed to send Slack alert: {e}")


async def send_pagerduty_alert(
    title: str,
    message: str,
    severity: str = "error"
):
    """
    Send alert to PagerDuty.

    Args:
        title: Alert title
        message: Alert description
        severity: Alert severity
    """
    if not settings.PAGERDUTY_INTEGRATION_KEY:
        logger.warning("PagerDuty not configured")
        return

    payload = {
        "routing_key": settings.PAGERDUTY_INTEGRATION_KEY,
        "event_action": "trigger",
        "payload": {
            "summary": title,
            "severity": severity,
            "source": "quant-analytics-backend",
            "custom_details": {
                "message": message,
                "environment": settings.ENVIRONMENT
            }
        }
    }

    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                "https://events.pagerduty.com/v2/enqueue",
                json=payload,
                timeout=5.0
            )
            response.raise_for_status()
            logger.info(f"PagerDuty alert sent: {title}")
    except Exception as e:
        logger.error(f"Failed to send PagerDuty alert: {e}")
```

### Use in Application

```python
# app/core/exceptions.py

async def critical_error_handler(request: Request, exc: Exception):
    """Handle critical errors and send alerts."""
    from app.core.alerting import send_slack_alert, send_pagerduty_alert

    # Log error
    logger.error(f"Critical error: {exc}", exc_info=True)

    # Send alerts
    await send_slack_alert(
        title="Critical Error in Production",
        message=f"Error: {str(exc)}\nPath: {request.url.path}",
        severity="critical"
    )

    # Send PagerDuty for production
    if settings.ENVIRONMENT == "production":
        await send_pagerduty_alert(
            title="Production Error",
            message=str(exc),
            severity="error"
        )

    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error"}
    )
```

---

## 📝 Structured Logging

### Enhanced Logging with Context

```python
# app/core/logging_enhanced.py
"""
Enhanced structured logging with request context.
"""

import logging
import json
from contextvars import ContextVar
from datetime import datetime
from typing import Any, Dict

# Context vars for request tracking
request_id_var: ContextVar[str] = ContextVar('request_id', default='')
user_id_var: ContextVar[str] = ContextVar('user_id', default='')


class StructuredFormatter(logging.Formatter):
    """JSON formatter for structured logs."""

    def format(self, record: logging.LogRecord) -> str:
        """Format log record as JSON."""
        log_data = {
            "timestamp": datetime.utcnow().isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "request_id": request_id_var.get(),
            "user_id": user_id_var.get(),
        }

        # Add exception info if present
        if record.exc_info:
            log_data["exception"] = self.formatException(record.exc_info)

        # Add custom fields
        if hasattr(record, 'extra'):
            log_data.update(record.extra)

        return json.dumps(log_data)


# Middleware to set request context
class LoggingContextMiddleware(BaseHTTPMiddleware):
    """Add request context to logs."""

    async def dispatch(self, request: Request, call_next):
        """Add request ID and user ID to logging context."""
        # Generate or get request ID
        request_id = request.headers.get('X-Request-ID', str(uuid.uuid4()))
        request_id_var.set(request_id)

        # Get user ID if authenticated
        user_id = getattr(request.state, 'user_id', '')
        user_id_var.set(user_id)

        response = await call_next(request)
        response.headers['X-Request-ID'] = request_id

        return response


# Usage example
logger = logging.getLogger(__name__)
logger.info(
    "User action performed",
    extra={
        "action": "login",
        "ip_address": "1.2.3.4",
        "success": True
    }
)
# Output: {"timestamp": "2025-01-01T00:00:00", "level": "INFO",
#          "request_id": "abc-123", "user_id": "user-456",
#          "action": "login", ...}
```

---

## 🔍 Distributed Tracing

### OpenTelemetry Integration

```python
# app/core/tracing.py
"""
OpenTelemetry distributed tracing.
"""

from opentelemetry import trace
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from opentelemetry.instrumentation.sqlalchemy import SQLAlchemyInstrumentor
from opentelemetry.instrumentation.redis import RedisInstrumentor


def setup_tracing(app: FastAPI):
    """Configure OpenTelemetry tracing."""
    # Create tracer provider
    provider = TracerProvider()
    trace.set_tracer_provider(provider)

    # Configure exporter (Jaeger, Zipkin, or custom)
    otlp_exporter = OTLPSpanExporter(
        endpoint=settings.OTEL_EXPORTER_ENDPOINT,
        insecure=settings.ENVIRONMENT != "production"
    )

    # Add span processor
    provider.add_span_processor(BatchSpanProcessor(otlp_exporter))

    # Instrument FastAPI
    FastAPIInstrumentor.instrument_app(app)

    # Instrument database
    SQLAlchemyInstrumentor().instrument(engine=engine)

    # Instrument Redis
    RedisInstrumentor().instrument()


# Use in application
from opentelemetry import trace

tracer = trace.get_tracer(__name__)

@router.get("/trades")
async def get_trades():
    with tracer.start_as_current_span("get_trades"):
        # Your code here
        with tracer.start_as_current_span("database_query"):
            results = await db.execute(query)

        with tracer.start_as_current_span("process_results"):
            processed = process_results(results)

        return processed
```

---

## 📊 Health Checks

### Comprehensive Health Check

```python
# app/api/v1/health.py
"""
Comprehensive health check endpoints.
"""

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db

router = APIRouter()


@router.get("/health/liveness")
async def liveness():
    """
    Kubernetes liveness probe.

    Returns 200 if application is running.
    """
    return {"status": "alive"}


@router.get("/health/readiness")
async def readiness(db: AsyncSession = Depends(get_db)):
    """
    Kubernetes readiness probe.

    Returns 200 if application is ready to serve traffic.
    """
    checks = {
        "database": False,
        "redis": False,
    }

    # Check database
    try:
        from sqlalchemy import text
        await db.execute(text("SELECT 1"))
        checks["database"] = True
    except:
        pass

    # Check Redis
    try:
        from app.core.cache import cache_manager
        if cache_manager.redis_client:
            await cache_manager.redis_client.ping()
            checks["redis"] = True
    except:
        pass

    # Ready if all critical services are up
    is_ready = checks["database"]  # Redis is optional

    status_code = 200 if is_ready else 503

    return {
        "status": "ready" if is_ready else "not_ready",
        "checks": checks
    }, status_code


@router.get("/health/startup")
async def startup():
    """
    Kubernetes startup probe.

    Returns 200 when application has finished starting up.
    """
    # Check if initialization is complete
    return {"status": "started"}
```

---

## 📈 Performance Monitoring

### APM Integration (Sentry)

```python
# app/core/monitoring.py

import sentry_sdk
from sentry_sdk.integrations.fastapi import FastApiIntegration
from sentry_sdk.integrations.sqlalchemy import SqlalchemyIntegration
from sentry_sdk.integrations.redis import RedisIntegration


def setup_sentry():
    """Configure Sentry for error tracking and performance monitoring."""
    if not settings.SENTRY_DSN:
        return

    sentry_sdk.init(
        dsn=settings.SENTRY_DSN,
        environment=settings.ENVIRONMENT,
        release=settings.VERSION,

        # Performance monitoring
        traces_sample_rate=0.1 if settings.ENVIRONMENT == "production" else 1.0,

        # Integrations
        integrations=[
            FastApiIntegration(),
            SqlalchemyIntegration(),
            RedisIntegration(),
        ],

        # Send PII (be careful with this in production)
        send_default_pii=False,

        # Performance profiles
        profiles_sample_rate=0.1,

        # Before send hook to filter sensitive data
        before_send=filter_sensitive_data,
    )


def filter_sensitive_data(event, hint):
    """Filter sensitive data from Sentry events."""
    # Remove passwords from request data
    if 'request' in event and 'data' in event['request']:
        data = event['request']['data']
        if isinstance(data, dict):
            for key in ['password', 'token', 'secret', 'api_key']:
                if key in data:
                    data[key] = '***REDACTED***'

    return event
```

---

## 📊 Monitoring Checklist

### Essential Metrics to Track

- [ ] **Request metrics**: Rate, latency, error rate
- [ ] **Database**: Query time, connection pool, slow queries
- [ ] **Cache**: Hit rate, memory usage
- [ ] **Authentication**: Success/failure rate, account lockouts
- [ ] **Business metrics**: Trades processed, user signups
- [ ] **Infrastructure**: CPU, memory, disk, network
- [ ] **Errors**: Error rate by type, endpoint
- [ ] **External services**: API response times, error rates

### Essential Alerts

- [ ] Service down (> 1 minute)
- [ ] High error rate (> 5%)
- [ ] High response time (p95 > 1s)
- [ ] Database connection pool exhaustion
- [ ] Redis memory high (> 90%)
- [ ] Disk space low (< 10%)
- [ ] High authentication failure rate (possible attack)
- [ ] SSL certificate expiring (< 30 days)

---

## 🚀 Quick Start

```bash
# 1. Start monitoring stack
docker-compose -f monitoring/docker-compose.yml up -d

# 2. Access dashboards
# Grafana: http://localhost:3000 (admin/admin)
# Prometheus: http://localhost:9090

# 3. Import dashboards
# Import monitoring/grafana/dashboards/*.json

# 4. Configure alerts
# Edit prometheus/alerts.yml
# Configure alertmanager/config.yml

# 5. Test alerts
curl http://localhost:8000/test-error-alert
```

---

## 📚 Resources

- Prometheus: https://prometheus.io/docs/
- Grafana: https://grafana.com/docs/
- OpenTelemetry: https://opentelemetry.io/docs/
- Sentry: https://docs.sentry.io/
