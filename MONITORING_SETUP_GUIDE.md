# Monitoring & Alerting Setup Guide

**Complete guide to setting up comprehensive monitoring for the Quant Trading Platform**

---

## 📊 Overview

The platform includes enterprise-grade monitoring with:
- **Prometheus** metrics collection
- **Grafana** dashboards
- **Sentry** error tracking
- **Multi-channel alerting** (Slack, Email, Webhook)
- **Real-time performance tracking**

---

## 🚀 Quick Start

### 1. Sentry Setup (5 minutes)

```bash
# Create free Sentry account at https://sentry.io

# Get your DSN from project settings
# Add to environment variables:
export SENTRY_DSN="https://your-key@sentry.io/your-project-id"
export SENTRY_ENVIRONMENT="production"

# Restart application
# Errors will now be tracked automatically
```

### 2. Prometheus Setup (10 minutes)

```bash
# Install Prometheus
docker run -d \
  --name prometheus \
  -p 9090:9090 \
  -v $(pwd)/monitoring/prometheus-rules.yml:/etc/prometheus/prometheus.yml \
  prom/prometheus

# Metrics available at:
# http://localhost:8000/api/v1/monitoring/metrics (application)
# http://localhost:9090 (Prometheus UI)
```

### 3. Grafana Setup (10 minutes)

```bash
# Install Grafana
docker run -d \
  --name grafana \
  -p 3000:3000 \
  grafana/grafana

# Access Grafana: http://localhost:3000
# Default login: admin/admin

# Import dashboard:
# 1. Go to Dashboards → Import
# 2. Upload monitoring/grafana-dashboard.json
```

### 4. Slack Alerts (2 minutes)

```bash
# Create Slack webhook:
# 1. Go to https://api.slack.com/apps
# 2. Create new app
# 3. Enable Incoming Webhooks
# 4. Copy webhook URL

# Add to environment:
export SLACK_WEBHOOK_URL="https://hooks.slack.com/services/YOUR/WEBHOOK/URL"

# Restart application - alerts will go to Slack
```

---

## 📈 Metrics Available

### HTTP Metrics

| Metric | Type | Description |
|--------|------|-------------|
| `http_requests_total` | Counter | Total HTTP requests by method, endpoint, status |
| `http_request_duration_seconds` | Histogram | Request duration distribution |
| `http_requests_active` | Gauge | Currently active requests |

### Cache Metrics

| Metric | Type | Description |
|--------|------|-------------|
| `cache_hits_total` | Counter | Cache hits by type |
| `cache_misses_total` | Counter | Cache misses by type |

### Error Metrics

| Metric | Type | Description |
|--------|------|-------------|
| `errors_total` | Counter | Errors by type and endpoint |

### System Metrics

| Metric | Type | Description |
|--------|------|-------------|
| `cpu_usage_percent` | Gauge | CPU usage percentage |
| `memory_usage_percent` | Gauge | Memory usage percentage |
| `disk_usage_percent` | Gauge | Disk usage percentage |

### Database Metrics

| Metric | Type | Description |
|--------|------|-------------|
| `database_connections_active` | Gauge | Active database connections |
| `database_connections_idle` | Gauge | Idle database connections |
| `database_slow_queries_total` | Counter | Slow query count |

### WebSocket Metrics

| Metric | Type | Description |
|--------|------|-------------|
| `websocket_connections_active` | Gauge | Active WebSocket connections |
| `websocket_messages_sent` | Counter | Messages sent via WebSocket |
| `websocket_messages_received` | Counter | Messages received via WebSocket |

---

## 🔔 Alert Rules

### Critical Alerts

**HighErrorRate**: Error rate > 5% for 5 minutes
```yaml
Action: Immediate investigation required
Channels: Slack, Email, PagerDuty
```

**ServiceDown**: Service unreachable for 1 minute
```yaml
Action: Emergency response
Channels: All channels
```

**DatabaseConnectionPoolExhausted**: 90% connections in use
```yaml
Action: Scale up or investigate leaks
Channels: Slack, Email
```

### Warning Alerts

**SlowResponseTime**: P95 latency > 2s for 10 minutes
```yaml
Action: Review slow queries and optimize
Channels: Slack
```

**HighCPUUsage**: CPU > 80% for 10 minutes
```yaml
Action: Consider scaling
Channels: Slack
```

**LowCacheHitRate**: Hit rate < 50% for 15 minutes
```yaml
Action: Review cache strategy
Channels: Slack
```

### Info Alerts

**WebSocketConnectionSpike**: 100+ new connections in 5 minutes
```yaml
Action: Monitor for potential issues
Channels: Log only
```

---

## 🎯 Dashboards

### Main Dashboard

**Panels**:
1. **Request Rate** - Requests per second by endpoint
2. **Response Time** - P50, P95, P99 latencies
3. **Error Rate** - Errors per second by type
4. **Active Requests** - Current load
5. **Cache Hit Rate** - Cache effectiveness
6. **System Resources** - CPU, Memory, Disk
7. **Database Performance** - Connections, slow queries
8. **WebSocket Activity** - Active connections, messages

**Refresh**: 30 seconds
**Time Range**: Last 1 hour (adjustable)

### Database Dashboard

**Panels**:
1. **Query Performance** - Slowest queries
2. **Connection Pool** - Active/idle connections
3. **Slow Queries** - Count over time
4. **Table Sizes** - Largest tables
5. **Index Usage** - Index hit ratios

### API Performance Dashboard

**Panels**:
1. **Endpoint Latency** - P95 by endpoint
2. **Error Rates** - Errors by endpoint
3. **Request Volume** - Requests by endpoint
4. **Top Slow Endpoints** - Table view

---

## 🔧 Configuration

### Environment Variables

```bash
# Sentry
SENTRY_DSN="https://key@sentry.io/project"
SENTRY_ENVIRONMENT="production"  # or "staging", "development"

# Slack
SLACK_WEBHOOK_URL="https://hooks.slack.com/services/..."

# Email (optional)
ALERT_EMAIL="alerts@yourcompany.com"
SMTP_HOST="smtp.gmail.com"
SMTP_PORT="587"
SMTP_USER="your-email@gmail.com"
SMTP_PASSWORD="your-password"

# Webhook (optional)
ALERT_WEBHOOK_URL="https://your-webhook-endpoint.com/alerts"

# Prometheus
PROMETHEUS_ENABLED="true"
PROMETHEUS_PORT="9090"

# Monitoring
MONITORING_ENABLED="true"
SLOW_QUERY_THRESHOLD="1.0"  # seconds
```

### Prometheus Configuration

Create `prometheus.yml`:

```yaml
global:
  scrape_interval: 15s
  evaluation_interval: 15s

# Alert rules
rule_files:
  - "prometheus-rules.yml"

# Alertmanager configuration
alerting:
  alertmanagers:
    - static_configs:
        - targets: ['localhost:9093']

# Scrape configs
scrape_configs:
  - job_name: 'quant-api'
    static_configs:
      - targets: ['localhost:8000']
    metrics_path: '/api/v1/monitoring/metrics'
```

### Alertmanager Configuration

Create `alertmanager.yml`:

```yaml
global:
  slack_api_url: 'YOUR_SLACK_WEBHOOK_URL'

route:
  group_by: ['alertname', 'severity']
  group_wait: 10s
  group_interval: 10s
  repeat_interval: 1h
  receiver: 'slack-notifications'

  routes:
    - match:
        severity: critical
      receiver: 'slack-critical'
      continue: true

receivers:
  - name: 'slack-notifications'
    slack_configs:
      - channel: '#monitoring'
        title: '{{ .GroupLabels.alertname }}'
        text: '{{ range .Alerts }}{{ .Annotations.description }}{{ end }}'

  - name: 'slack-critical'
    slack_configs:
      - channel: '#alerts-critical'
        title: '🚨 CRITICAL: {{ .GroupLabels.alertname }}'
        text: '{{ range .Alerts }}{{ .Annotations.description }}{{ end }}'
```

---

## 📱 API Endpoints

### Metrics Endpoint

```http
GET /api/v1/monitoring/metrics
```

Returns Prometheus-formatted metrics.

### Health Check

```http
GET /api/v1/monitoring/health
```

**Response**:
```json
{
  "status": "healthy",
  "timestamp": "2026-01-28T12:00:00Z",
  "version": "1.0.0",
  "uptime_seconds": 3600,
  "checks": {
    "database": "connected",
    "cache": "connected",
    "websocket": "healthy"
  }
}
```

### System Metrics

```http
GET /api/v1/monitoring/system
```

**Response**:
```json
{
  "cpu_percent": 45.2,
  "memory_percent": 62.8,
  "disk_percent": 48.5,
  "uptime_seconds": 3600,
  "active_requests": 12
}
```

### Alert History

```http
GET /api/v1/monitoring/alerts?limit=50
```

**Response**:
```json
{
  "alerts": [
    {
      "title": "High CPU Usage",
      "message": "CPU at 85%",
      "severity": "warning",
      "timestamp": "2026-01-28T12:00:00Z"
    }
  ]
}
```

---

## 🐛 Troubleshooting

### Metrics Not Appearing

**Issue**: Prometheus can't scrape metrics

**Solutions**:
1. Check endpoint is accessible: `curl http://localhost:8000/api/v1/monitoring/metrics`
2. Verify Prometheus config has correct target
3. Check firewall rules
4. Review Prometheus logs: `docker logs prometheus`

### Alerts Not Sending

**Issue**: Slack alerts not received

**Solutions**:
1. Verify webhook URL is correct
2. Test webhook manually:
   ```bash
   curl -X POST -H 'Content-type: application/json' \
     --data '{"text":"Test alert"}' \
     YOUR_WEBHOOK_URL
   ```
3. Check application logs for errors
4. Verify environment variable is set correctly

### Sentry Not Tracking Errors

**Issue**: Errors not appearing in Sentry

**Solutions**:
1. Verify DSN is correct
2. Check environment is set: `echo $SENTRY_ENVIRONMENT`
3. Test with manual error:
   ```python
   import sentry_sdk
   sentry_sdk.capture_exception(Exception("Test error"))
   ```
4. Review Sentry project settings

### High Memory Usage in Prometheus

**Issue**: Prometheus consuming too much memory

**Solutions**:
1. Reduce retention period in config
2. Adjust scrape interval (increase to 30s or 60s)
3. Limit metric cardinality
4. Use remote storage for long-term retention

---

## 📚 Best Practices

### 1. Alert Fatigue Prevention

- **Group related alerts**: Use Alertmanager routing
- **Set appropriate thresholds**: Avoid false positives
- **Use inhibition rules**: Suppress dependent alerts
- **Review regularly**: Adjust based on patterns

### 2. Dashboard Organization

- **Overview dashboard**: High-level metrics for quick checks
- **Detailed dashboards**: Deep dives per component
- **Operational dashboards**: For on-call engineers
- **Business dashboards**: For stakeholders

### 3. Metric Naming

- **Follow Prometheus conventions**: `<namespace>_<name>_<unit>`
- **Use labels wisely**: Keep cardinality low
- **Document custom metrics**: Explain what they measure

### 4. Alert Tuning

- **Start conservative**: Add alerts gradually
- **Set appropriate "for" durations**: Avoid transient alerts
- **Use runbooks**: Document response procedures
- **Test alert rules**: Verify they fire correctly

### 5. Performance Impact

- **Limit label cardinality**: High cardinality = high memory
- **Sample expensive metrics**: Use lower scrape intervals
- **Archive old metrics**: Move to long-term storage
- **Monitor the monitors**: Track Prometheus resource usage

---

## 🔍 Advanced Topics

### Custom Metrics

Add custom metrics in your code:

```python
from prometheus_client import Counter, Histogram, Gauge

# Define metric
trade_counter = Counter(
    'trades_processed_total',
    'Total trades processed',
    ['politician', 'transaction_type']
)

# Use metric
trade_counter.labels(
    politician='John Doe',
    transaction_type='buy'
).inc()
```

### Recording Rules

Precompute expensive queries in Prometheus:

```yaml
groups:
  - name: recording_rules
    interval: 30s
    rules:
      - record: api:request_rate:5m
        expr: rate(http_requests_total[5m])

      - record: api:error_rate:5m
        expr: rate(errors_total[5m])
```

### Distributed Tracing

Integrate with Jaeger or Zipkin for request tracing:

```python
from opentelemetry import trace
from opentelemetry.exporter.jaeger import JaegerExporter

# Configure tracer
tracer = trace.get_tracer(__name__)

# Trace requests
with tracer.start_as_current_span("get_politician_trades"):
    # Your code here
    pass
```

---

## 📊 SLA Monitoring

### Define SLOs (Service Level Objectives)

```yaml
# 99.9% availability
availability_slo: 0.999

# P95 latency < 500ms
latency_p95_slo: 0.5

# Error rate < 0.1%
error_rate_slo: 0.001
```

### Track SLI (Service Level Indicators)

```promql
# Availability
1 - (rate(http_requests_total{status=~"5.."}[30d]) / rate(http_requests_total[30d]))

# Latency
histogram_quantile(0.95, rate(http_request_duration_seconds_bucket[5m]))

# Error rate
rate(errors_total[5m]) / rate(http_requests_total[5m])
```

### Alert on SLO Violations

```yaml
- alert: SLOViolation_Availability
  expr: |
    1 - (rate(http_requests_total{status=~"5.."}[30d]) / rate(http_requests_total[30d])) < 0.999
  for: 5m
  annotations:
    summary: "Availability SLO violated"
```

---

## 🎓 Resources

- **Prometheus Docs**: https://prometheus.io/docs/
- **Grafana Docs**: https://grafana.com/docs/
- **Sentry Docs**: https://docs.sentry.io/
- **Site Reliability Engineering**: https://sre.google/books/

---

**Last Updated**: January 28, 2026
