#!/bin/bash

# Comprehensive Production Testing
set -e

echo "=========================================="
echo "  Comprehensive Production Testing"
echo "=========================================="
echo ""

# Test 1: Docker Services
echo "1. Checking Docker Services..."
docker ps --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}" | grep quant

echo ""
echo "2. Testing Service Health..."

# MLFlow
echo -n "  MLFlow (port 5000): "
if curl -sf http://localhost:5000/health > /dev/null; then
    echo "✓ OK"
else
    echo "✗ FAILED"
fi

# MinIO
echo -n "  MinIO (port 9000): "
if curl -sf http://localhost:9000/minio/health/live > /dev/null; then
    echo "✓ OK"
else
    echo "✗ FAILED"
fi

# Redis
echo -n "  Redis-ML (port 6380): "
if redis-cli -p 6380 ping > /dev/null 2>&1; then
    echo "✓ OK"
else
    echo "✗ FAILED"
fi

# PostgreSQL
echo -n "  PostgreSQL (port 5432): "
if docker exec quant-postgres pg_isready -U postgres > /dev/null 2>&1; then
    echo "✓ OK"
else
    echo "✗ FAILED"
fi

echo ""
echo "3. Checking Docker Volumes..."
docker volume ls | grep docker_ | awk '{print "  - " $2}'

echo ""
echo "4. Resource Usage..."
docker stats --no-stream --format "table {{.Name}}\t{{.CPUPerc}}\t{{.MemUsage}}" \
    quant-mlflow quant-minio quant-redis-ml quant-postgres

echo ""
echo "5. Network Connectivity..."
echo -n "  MLFlow → MinIO: "
if docker exec quant-mlflow curl -sf http://minio:9000/minio/health/live > /dev/null 2>&1; then
    echo "✓ OK"
else
    echo "✗ FAILED"
fi

echo ""
echo "6. Database Check..."
docker exec quant-postgres psql -U postgres -c "SELECT datname FROM pg_database WHERE datname IN ('quant', 'mlflow');"

echo ""
echo "=========================================="
echo "  All Tests Completed"
echo "=========================================="
