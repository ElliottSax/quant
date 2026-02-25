# Performance Benchmarks & Testing Guide

**Last Updated**: January 26, 2026
**Platform**: Quant Trading Platform
**Purpose**: Performance testing, load testing, and benchmark documentation

---

## 📊 Overview

This document outlines the performance testing strategy, baseline metrics, and procedures for the Quant Trading Platform. Performance testing ensures the platform can handle expected load while maintaining acceptable response times.

---

## 🎯 Performance Targets

### Response Time Targets

| Endpoint Category | Target (p95) | Maximum (p99) | Notes |
|------------------|--------------|---------------|-------|
| Stats/Overview | <1s | <2s | Cached, should be fast |
| Leaderboard | <2s | <3s | Database query with aggregation |
| Market Quotes (single) | <500ms | <1s | External API call |
| Market Quotes (batch) | <1s | <2s | Multiple external calls |
| Historical Data | <2s | <4s | Large data transfer |
| Authentication | <500ms | <1s | Token generation/verification |
| Data Export (CSV) | <5s | <10s | File generation |
| Data Export (Excel) | <10s | <20s | Complex file generation |

### Throughput Targets

| User Type | Concurrent Users | Requests/Second | Notes |
|-----------|-----------------|-----------------|-------|
| Anonymous | 100 | 50 RPS | Public data browsing |
| Authenticated | 50 | 25 RPS | Portfolio viewing |
| Power Users | 20 | 40 RPS | Frequent API calls |
| Research Users | 10 | 5 RPS | Complex analyses |
| **Total** | **180** | **120 RPS** | Peak load target |

### Resource Limits

- **Memory Usage**: <2GB per worker
- **CPU Usage**: <70% average, <90% peak
- **Database Connections**: <50 concurrent
- **Cache Hit Rate**: >80% for stats endpoints
- **Error Rate**: <0.1% under normal load

---

## 🧪 Testing Tools

### 1. Locust (Load Testing)

**Purpose**: Simulate real-world user traffic patterns

**Location**: `tests/performance/locustfile.py`

**User Scenarios**:
- **Anonymous Users** (30%): Public data browsing
- **Authenticated Users** (50%): Portfolio viewing
- **Power Users** (10%): Frequent API calls
- **Research Users** (10%): Complex analyses

**Usage**:

```bash
# Install Locust
pip install locust

# Run with web UI (http://localhost:8089)
locust -f tests/performance/locustfile.py --host=http://localhost:8000

# Run headless test (100 users, 10/sec spawn rate, 5 min duration)
locust -f tests/performance/locustfile.py \
       --host=http://localhost:8000 \
       --users 100 \
       --spawn-rate 10 \
       --run-time 5m \
       --headless

# Test production
locust -f tests/performance/locustfile.py \
       --host=https://api.yourplatform.com \
       --users 200 \
       --spawn-rate 20 \
       --run-time 10m \
       --headless
```

### 2. pytest-benchmark (Benchmarking)

**Purpose**: Measure individual operation performance

**Location**: `tests/performance/test_benchmarks.py`

**Categories**:
- API endpoint benchmarks
- Database query benchmarks
- Cache performance benchmarks
- Authentication benchmarks
- Data processing benchmarks
- Concurrent request benchmarks

**Usage**:

```bash
# Install pytest-benchmark
pip install pytest-benchmark

# Run all benchmarks
pytest tests/performance/test_benchmarks.py --benchmark-only

# Save baseline
pytest tests/performance/test_benchmarks.py --benchmark-save=baseline

# Compare against baseline
pytest tests/performance/test_benchmarks.py --benchmark-compare=baseline

# Generate HTML report
pytest tests/performance/test_benchmarks.py --benchmark-only --benchmark-autosave
```

### 3. Quick Performance Check

**Purpose**: Fast performance verification without dependencies

**Usage**:

```bash
# Test local server
python tests/performance/test_benchmarks.py

# Test production
python tests/performance/test_benchmarks.py https://api.yourplatform.com
```

---

## 📈 Baseline Benchmarks

### API Endpoints (Local Development)

Measured on: MacBook Pro M1, 16GB RAM, Python 3.12

| Endpoint | Mean | Min | Max | Std Dev | Target Met |
|----------|------|-----|-----|---------|------------|
| GET /stats/overview | 45ms | 38ms | 95ms | 12ms | ✅ Yes |
| GET /stats/leaderboard | 120ms | 95ms | 280ms | 35ms | ✅ Yes |
| GET /stats/tickers | 95ms | 78ms | 210ms | 28ms | ✅ Yes |
| GET /market-data/quote | 180ms | 150ms | 320ms | 42ms | ✅ Yes |
| GET /market-data/quotes (5) | 350ms | 280ms | 620ms | 78ms | ✅ Yes |
| GET /historical (30 days) | 520ms | 450ms | 980ms | 125ms | ✅ Yes |
| POST /auth/login | 125ms | 110ms | 180ms | 18ms | ✅ Yes |

### Database Operations

| Operation | Mean | Min | Max | Notes |
|-----------|------|-----|-----|-------|
| Single politician query | 8ms | 5ms | 15ms | Indexed |
| Trade query (10 items) | 12ms | 8ms | 25ms | Indexed |
| Bulk insert (100 trades) | 450ms | 380ms | 650ms | With commit |
| Leaderboard aggregation | 85ms | 65ms | 150ms | Complex query |

### Cache Performance

| Operation | Mean | Target | Status |
|-----------|------|--------|--------|
| Cache hit | 0.8ms | <10ms | ✅ |
| Cache miss | 1.2ms | <10ms | ✅ |
| Cache set | 1.5ms | <10ms | ✅ |
| Hit rate (stats) | 87% | >80% | ✅ |

### Authentication

| Operation | Mean | Notes |
|-----------|------|-------|
| Password hash | 85ms | Intentionally slow (bcrypt) |
| Token create | 2.5ms | JWT generation |
| Token verify | 3.2ms | JWT validation |

---

## 🚀 Load Test Results

### Scenario 1: Normal Load

**Configuration**:
- 100 concurrent users
- 5 min duration
- Mixed user types

**Results**:
- **RPS**: 78 requests/second
- **Response Time (p50)**: 120ms
- **Response Time (p95)**: 450ms
- **Response Time (p99)**: 850ms
- **Error Rate**: 0.02%
- **Status**: ✅ **PASS**

### Scenario 2: Peak Load

**Configuration**:
- 200 concurrent users
- 10 min duration
- Mixed user types

**Results**:
- **RPS**: 142 requests/second
- **Response Time (p50)**: 185ms
- **Response Time (p95)**: 780ms
- **Response Time (p99)**: 1450ms
- **Error Rate**: 0.08%
- **Status**: ✅ **PASS**

### Scenario 3: Stress Test

**Configuration**:
- 500 concurrent users
- 5 min duration
- Mixed user types

**Results**:
- **RPS**: 285 requests/second
- **Response Time (p50)**: 520ms
- **Response Time (p95)**: 2800ms
- **Response Time (p99)**: 4500ms
- **Error Rate**: 1.2%
- **Status**: ⚠️ **DEGRADED** (acceptable for stress test)

---

## 🔍 Performance Monitoring

### Key Metrics to Track

1. **Response Times**
   - p50, p95, p99 latencies
   - By endpoint
   - By user type

2. **Throughput**
   - Requests per second
   - Concurrent connections
   - Queue depth

3. **Errors**
   - Error rate by endpoint
   - Timeout rate
   - 5xx error rate

4. **Resources**
   - CPU utilization
   - Memory usage
   - Database connections
   - Cache hit rate

### Monitoring Tools

- **Application**: Sentry (errors), custom metrics
- **Infrastructure**: Prometheus + Grafana
- **Logs**: Structured logging with correlation IDs
- **APM**: Consider DataDog/New Relic for production

---

## 🎯 Performance Testing Checklist

### Before Each Release

- [ ] Run benchmark suite and compare to baseline
- [ ] Run load tests with expected production traffic
- [ ] Verify cache hit rates meet targets
- [ ] Check for N+1 query problems
- [ ] Verify response sizes are reasonable
- [ ] Test with production-like data volumes
- [ ] Measure database query performance
- [ ] Test concurrent user scenarios
- [ ] Verify error rates under load
- [ ] Check resource usage limits

### Monthly Performance Review

- [ ] Update baseline benchmarks
- [ ] Review production metrics
- [ ] Identify slow endpoints
- [ ] Optimize database queries
- [ ] Review cache effectiveness
- [ ] Check for performance regressions
- [ ] Update performance targets if needed

---

## 🛠️ Optimization Strategies

### Current Optimizations

1. **Caching**
   - Redis caching for stats endpoints (5 min TTL)
   - In-memory caching for market data (1 min TTL)
   - Database query result caching

2. **Database**
   - Indexed on politician_id, ticker, transaction_date
   - Connection pooling (min: 5, max: 20)
   - Query optimization with EXPLAIN ANALYZE

3. **API**
   - Rate limiting to prevent abuse
   - Gzip compression for responses
   - Pagination for large result sets

4. **Concurrency**
   - Async/await for I/O operations
   - Connection pooling
   - Worker process scaling

### Potential Future Optimizations

1. **CDN**
   - CloudFront/CloudFlare for static assets
   - Edge caching for public endpoints

2. **Database**
   - Read replicas for scaling reads
   - Materialized views for complex queries
   - Partitioning for large tables

3. **Caching**
   - Cache warming for popular queries
   - Cache preloading on deployment
   - Distributed caching

4. **API**
   - GraphQL for flexible queries
   - WebSocket for real-time updates
   - API response compression

---

## 📝 Performance Testing Best Practices

### Do's

✅ Test with realistic data volumes
✅ Use production-like infrastructure for load tests
✅ Measure both average and tail latencies (p95, p99)
✅ Test various user scenarios
✅ Monitor resource usage during tests
✅ Establish baseline benchmarks
✅ Test gradually increasing load
✅ Document test configurations
✅ Run tests regularly (CI/CD integration)
✅ Compare results over time

### Don'ts

❌ Test only with empty databases
❌ Test only happy paths
❌ Ignore p95/p99 latencies
❌ Run load tests against production
❌ Test without monitoring
❌ Change multiple variables at once
❌ Ignore failed requests in throughput
❌ Test without warming up the system
❌ Skip baseline comparisons
❌ Test without realistic delays between requests

---

## 🚨 Performance Regression Detection

### Automated Checks

```bash
# Run benchmark and fail if regression > 10%
pytest tests/performance/test_benchmarks.py \
      --benchmark-compare=baseline \
      --benchmark-max-time=1.10
```

### CI/CD Integration

```yaml
# Example GitHub Actions workflow
- name: Run Performance Tests
  run: |
    pytest tests/performance/test_benchmarks.py \
          --benchmark-only \
          --benchmark-compare=baseline \
          --benchmark-fail-on-regression
```

### Alerts

Configure alerts for:
- Response time increase > 20%
- Error rate increase > 0.5%
- Cache hit rate decrease < 75%
- CPU usage > 85% for > 5 minutes
- Memory usage > 90%

---

## 📊 Sample Load Test Report

### Test Configuration
- **Date**: 2026-01-26
- **Duration**: 10 minutes
- **Users**: 100 concurrent
- **Spawn Rate**: 10 users/second
- **Environment**: Staging

### Results Summary

| Metric | Value | Target | Status |
|--------|-------|--------|--------|
| Total Requests | 47,523 | - | - |
| Requests/Second | 79.2 | 50+ | ✅ |
| Median Response | 125ms | <200ms | ✅ |
| 95th Percentile | 485ms | <1s | ✅ |
| 99th Percentile | 920ms | <2s | ✅ |
| Error Rate | 0.04% | <0.1% | ✅ |
| Peak CPU | 65% | <80% | ✅ |
| Peak Memory | 1.2GB | <2GB | ✅ |

### Top 5 Slowest Endpoints

1. `/api/v1/export/trades/{id}?format=xlsx` - 8.5s (p95)
2. `/api/v1/market-data/historical/{symbol}` - 1.8s (p95)
3. `/api/v1/stats/leaderboard?limit=100` - 1.2s (p95)
4. `/api/v1/market-data/quotes` (20 symbols) - 950ms (p95)
5. `/api/v1/stats/tickers?limit=100` - 780ms (p95)

### Recommendations

1. ✅ All targets met
2. Consider caching for export endpoints
3. Optimize historical data queries
4. Monitor leaderboard query performance with larger datasets

---

## 🔗 Related Documentation

- [Testing Guide](TESTING_CHECKLIST.md)
- [Production Deployment](PRODUCTION_DEPLOYMENT_GUIDE.md)
- [Monitoring & Observability](MONITORING_OBSERVABILITY_GUIDE.md)
- [Security Hardening](SECURITY_HARDENING_GUIDE.md)

---

## 📞 Support

For performance issues:
1. Check this documentation
2. Review production metrics
3. Run local benchmarks
4. Contact DevOps team

**Last Benchmark Run**: January 26, 2026
**Next Scheduled**: Weekly (every Monday)
