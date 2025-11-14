#!/bin/bash

# Final Comprehensive Production Test
echo "=========================================="
echo " PRODUCTION READINESS TEST"
echo "=========================================="
echo ""

PASSED=0
FAILED=0

test_pass() {
    echo "  ✓ $1"
    ((PASSED++))
}

test_fail() {
    echo "  ✗ $1"
    ((FAILED++))
}

# Section 1: Infrastructure
echo "1. INFRASTRUCTURE"
echo "-------------------"

if docker ps | grep -q quant-postgres; then test_pass "PostgreSQL running"; else test_fail "PostgreSQL not running"; fi
if docker ps | grep -q quant-mlflow; then test_pass "MLFlow running"; else test_fail "MLFlow not running"; fi
if docker ps | grep -q quant-minio; then test_pass "MinIO running"; else test_fail "MinIO not running"; fi
if docker ps | grep -q quant-redis-ml; then test_pass "Redis-ML running"; else test_fail "Redis-ML not running"; fi
if docker ps | grep -q quant-backend; then test_pass "Backend API running"; else test_fail "Backend API not running"; fi

echo ""
echo "2. SERVICE HEALTH"
echo "-------------------"

# Backend Health
if curl -sf http://localhost:8000/health > /dev/null; then
    HEALTH=$(curl -s http://localhost:8000/health)
    test_pass "Backend API healthy"
    echo "    Response: $HEALTH"
else
    test_fail "Backend API not responding"
fi

# MLFlow Health
if curl -sf http://localhost:5000/health > /dev/null; then
    test_pass "MLFlow healthy"
else
    test_fail "MLFlow not responding"
fi

# MinIO Health
if curl -sf http://localhost:9000/minio/health/live > /dev/null; then
    test_pass "MinIO healthy"
else
    test_fail "MinIO not responding"
fi

# Database Connectivity
if docker exec quant-postgres pg_isready -U postgres > /dev/null 2>&1; then
    test_pass "PostgreSQL accepting connections"
else
    test_fail "PostgreSQL not accepting connections"
fi

echo ""
echo "3. API ENDPOINTS"
echo "-------------------"

# Root endpoint
if curl -sf http://localhost:8000/ > /dev/null; then
    test_pass "Root endpoint accessible"
else
    test_fail "Root endpoint failed"
fi

# Health endpoint
if curl -sf http://localhost:8000/health | grep -q "healthy"; then
    test_pass "Health endpoint working"
else
    test_fail "Health endpoint failed"
fi

# API Documentation
if curl -sf http://localhost:8000/api/v1/docs > /dev/null; then
    test_pass "Swagger docs accessible (http://localhost:8000/api/v1/docs)"
else
    test_fail "Swagger docs not accessible"
fi

# OpenAPI schema
if curl -sf http://localhost:8000/api/v1/openapi.json > /dev/null; then
    test_pass "OpenAPI schema available"
else
    test_fail "OpenAPI schema not available"
fi

echo ""
echo "4. DATABASE"
echo "-------------------"

# Check databases exist
DATABASES=$(docker exec quant-postgres psql -U postgres -lqt | cut -d \| -f 1 | grep -w quant | wc -l)
if [ "$DATABASES" -gt 0 ]; then
    test_pass "Quant database exists"
else
    test_fail "Quant database missing"
fi

# Check user exists
if docker exec quant-postgres psql -U postgres -c "\du" | grep -q quant_user; then
    test_pass "Database user configured"
else
    test_fail "Database user missing"
fi

echo ""
echo "5. ML INFRASTRUCTURE"
echo "-------------------"

# MLFlow UI
if curl -sf http://localhost:5000 > /dev/null; then
    test_pass "MLFlow UI accessible (http://localhost:5000)"
else
    test_fail "MLFlow UI not accessible"
fi

# MinIO Console
if curl -sf http://localhost:9001 > /dev/null; then
    test_pass "MinIO Console accessible (http://localhost:9001)"
else
    test_fail "MinIO Console not accessible"
fi

# Check volumes
VOLUMES=$(docker volume ls | grep docker_ | wc -l)
if [ "$VOLUMES" -ge 5 ]; then
    test_pass "All volumes created ($VOLUMES volumes)"
else
    test_fail "Missing volumes (found $VOLUMES)"
fi

echo ""
echo "6. RESOURCE USAGE"
echo "-------------------"
docker stats --no-stream --format "  {{.Name}}: CPU={{.CPUPerc}} MEM={{.MemUsage}}" \
    quant-mlflow quant-minio quant-redis-ml quant-postgres quant-backend

echo ""
echo "=========================================="
echo " SUMMARY"
echo "=========================================="
echo "Passed: $PASSED"
echo "Failed: $FAILED"
echo ""

if [ $FAILED -eq 0 ]; then
    echo "✓ ALL TESTS PASSED - PRODUCTION READY"
    echo ""
    echo "Access Points:"
    echo "  - Backend API:      http://localhost:8000"
    echo "  - API Docs:         http://localhost:8000/docs"
    echo "  - MLFlow UI:        http://localhost:5000"
    echo "  - MinIO Console:    http://localhost:9001"
    echo "                      (user: minioadmin / pass: minioadmin)"
    echo ""
    exit 0
else
    echo "✗ SOME TESTS FAILED - REVIEW BEFORE PRODUCTION"
    exit 1
fi
