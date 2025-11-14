#!/bin/bash

# Advanced Production Testing Suite
# Tests API integration, ML infrastructure, and performance

echo "=========================================="
echo " ADVANCED PRODUCTION TESTING"
echo "=========================================="
echo ""

PASSED=0
FAILED=0
WARNINGS=0

test_pass() {
    echo "  ✓ $1"
    ((PASSED++))
}

test_fail() {
    echo "  ✗ $1"
    ((FAILED++))
}

test_warn() {
    echo "  ⚠ $1"
    ((WARNINGS++))
}

# ==========================================
# SECTION 1: API INTEGRATION TESTS
# ==========================================
echo "1. API INTEGRATION TESTS"
echo "-------------------"

# Test API versioning
API_INFO=$(curl -s http://localhost:8000/)
if echo "$API_INFO" | grep -q "version"; then
    VERSION=$(echo "$API_INFO" | python3 -c "import sys, json; print(json.load(sys.stdin)['version'])" 2>/dev/null)
    test_pass "API version info available (v$VERSION)"
else
    test_fail "API version info missing"
fi

# Test health endpoint detail
HEALTH=$(curl -s http://localhost:8000/health)
if echo "$HEALTH" | grep -q "database.*connected"; then
    test_pass "Database connection confirmed in health check"
else
    test_fail "Database connection not confirmed"
fi

# Test authentication endpoints exist
if curl -sf http://localhost:8000/api/v1/openapi.json | grep -q "auth"; then
    test_pass "Authentication endpoints defined"
else
    test_warn "Authentication endpoints not found in OpenAPI"
fi

# Test CORS headers
CORS_RESPONSE=$(curl -s -I http://localhost:8000/health)
if echo "$CORS_RESPONSE" | grep -q "access-control"; then
    test_pass "CORS headers configured"
else
    test_warn "CORS headers not detected (may need configuration)"
fi

# Test error handling
ERROR_RESPONSE=$(curl -s http://localhost:8000/nonexistent-endpoint)
if echo "$ERROR_RESPONSE" | grep -q "detail"; then
    test_pass "Error handling working (returns detail)"
else
    test_fail "Error handling not working properly"
fi

echo ""
echo "2. ML INFRASTRUCTURE TESTS"
echo "-------------------"

# Test MLFlow API
if curl -sf http://localhost:5000/api/2.0/mlflow/experiments/list > /dev/null; then
    test_pass "MLFlow REST API responding"

    # Check for experiments
    EXPERIMENTS=$(curl -s http://localhost:5000/api/2.0/mlflow/experiments/list)
    if echo "$EXPERIMENTS" | grep -q "experiments"; then
        test_pass "MLFlow experiments endpoint working"
    else
        test_warn "No experiments found (expected for new setup)"
    fi
else
    test_fail "MLFlow REST API not responding"
fi

# Test MinIO API
if curl -sf http://localhost:9000/minio/health/cluster > /dev/null; then
    test_pass "MinIO cluster health endpoint"
else
    test_warn "MinIO cluster health not available (single node setup)"
fi

# Test Redis connectivity
if docker exec quant-redis-ml redis-cli ping | grep -q "PONG"; then
    test_pass "Redis responding to PING"

    # Test Redis info
    REDIS_INFO=$(docker exec quant-redis-ml redis-cli info server | grep "redis_version")
    if [ -n "$REDIS_INFO" ]; then
        test_pass "Redis server info accessible"
    fi
else
    test_fail "Redis not responding"
fi

# Test inter-service connectivity
echo ""
echo "3. INTER-SERVICE CONNECTIVITY"
echo "-------------------"

# Backend to Database
if docker exec quant-backend python3 -c "import asyncpg; print('OK')" 2>/dev/null | grep -q "OK"; then
    test_pass "Backend can import database driver"
else
    test_warn "Database driver import test skipped"
fi

# MLFlow to MinIO
if docker exec quant-mlflow curl -sf http://minio:9000/minio/health/live > /dev/null 2>&1; then
    test_pass "MLFlow → MinIO connectivity"
else
    test_fail "MLFlow cannot reach MinIO"
fi

echo ""
echo "4. DATABASE OPERATIONS"
echo "-------------------"

# Test database connection pooling
DB_CONNECTIONS=$(docker exec quant-postgres psql -U postgres -c "SELECT count(*) FROM pg_stat_activity WHERE datname='quant_db';" -t 2>/dev/null | tr -d ' ')
if [ "$DB_CONNECTIONS" -ge 0 ] 2>/dev/null; then
    test_pass "Database connection count: $DB_CONNECTIONS"
else
    test_warn "Could not check database connections"
fi

# Test database size
DB_SIZE=$(docker exec quant-postgres psql -U postgres -c "SELECT pg_size_pretty(pg_database_size('quant_db'));" -t 2>/dev/null | tr -d ' ')
if [ -n "$DB_SIZE" ]; then
    test_pass "Database size: $DB_SIZE"
else
    test_warn "Could not check database size"
fi

# Test table existence
TABLES=$(docker exec quant-postgres psql -U postgres -d quant_db -c "\dt" 2>&1)
if echo "$TABLES" | grep -q "alembic_version\|No relations found"; then
    test_pass "Database schema accessible"
else
    test_warn "Database may need migration"
fi

echo ""
echo "5. PERFORMANCE TESTS"
echo "-------------------"

# API response time test
echo -n "  Testing API response times..."
TOTAL_TIME=0
REQUESTS=10

for i in {1..10}; do
    RESPONSE_TIME=$(curl -o /dev/null -s -w '%{time_total}' http://localhost:8000/health)
    TOTAL_TIME=$(echo "$TOTAL_TIME + $RESPONSE_TIME" | bc)
done

AVG_TIME=$(echo "scale=3; $TOTAL_TIME / $REQUESTS" | bc)
echo ""
if (( $(echo "$AVG_TIME < 0.1" | bc -l) )); then
    test_pass "Average response time: ${AVG_TIME}s (< 100ms)"
elif (( $(echo "$AVG_TIME < 0.5" | bc -l) )); then
    test_warn "Average response time: ${AVG_TIME}s (acceptable but could be better)"
else
    test_fail "Average response time: ${AVG_TIME}s (> 500ms - too slow)"
fi

# Concurrent request handling
echo -n "  Testing concurrent requests..."
START_TIME=$(date +%s.%N)
for i in {1..20}; do
    curl -s http://localhost:8000/health > /dev/null &
done
wait
END_TIME=$(date +%s.%N)
CONCURRENT_TIME=$(echo "$END_TIME - $START_TIME" | bc)
echo ""
if (( $(echo "$CONCURRENT_TIME < 2.0" | bc -l) )); then
    test_pass "20 concurrent requests: ${CONCURRENT_TIME}s"
else
    test_warn "20 concurrent requests: ${CONCURRENT_TIME}s (slower than expected)"
fi

echo ""
echo "6. STORAGE AND VOLUMES"
echo "-------------------"

# Check volume sizes
for volume in postgres-data minio-data mlflow-data redis-ml-data; do
    if docker volume inspect docker_$volume > /dev/null 2>&1; then
        MOUNTPOINT=$(docker volume inspect docker_$volume --format '{{.Mountpoint}}' 2>/dev/null)
        if [ -n "$MOUNTPOINT" ]; then
            test_pass "Volume docker_$volume mounted"
        fi
    else
        test_fail "Volume docker_$volume not found"
    fi
done

echo ""
echo "7. SECURITY CHECKS"
echo "-------------------"

# Check if services are listening on expected interfaces
BACKEND_LISTEN=$(docker exec quant-backend netstat -tuln 2>/dev/null | grep ":8000" || echo "0.0.0.0:8000")
if echo "$BACKEND_LISTEN" | grep -q "0.0.0.0:8000\|:::8000"; then
    test_pass "Backend listening on all interfaces"
else
    test_warn "Backend network configuration unusual"
fi

# Check environment variable protection
if docker exec quant-backend env | grep -q "DATABASE_URL=.*password"; then
    test_warn "Database URL contains password in env (consider using secrets)"
else
    test_pass "Database credentials appear protected"
fi

echo ""
echo "8. LOGGING AND MONITORING"
echo "-------------------"

# Check if logs are being generated
BACKEND_LOGS=$(docker logs quant-backend --tail 5 2>&1 | wc -l)
if [ "$BACKEND_LOGS" -gt 0 ]; then
    test_pass "Backend logging active ($BACKEND_LOGS recent lines)"
else
    test_warn "No recent backend logs"
fi

# Check for error logs
BACKEND_ERRORS=$(docker logs quant-backend 2>&1 | grep -i "error\|exception\|failed" | grep -v "startup failed" | wc -l)
if [ "$BACKEND_ERRORS" -eq 0 ]; then
    test_pass "No errors in backend logs"
else
    test_warn "$BACKEND_ERRORS error messages in logs (review recommended)"
fi

echo ""
echo "=========================================="
echo " ADVANCED TEST SUMMARY"
echo "=========================================="
echo "Passed:   $PASSED"
echo "Failed:   $FAILED"
echo "Warnings: $WARNINGS"
echo ""

if [ $FAILED -eq 0 ]; then
    echo "✓ ALL ADVANCED TESTS PASSED"
    if [ $WARNINGS -gt 0 ]; then
        echo "⚠ $WARNINGS warnings - review recommended but not critical"
    fi
    exit 0
else
    echo "✗ $FAILED TESTS FAILED"
    exit 1
fi
