#!/bin/bash

# Production Testing Suite for Quant Trading Platform
# Tests all services, APIs, and infrastructure

set -e

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Counters
PASSED=0
FAILED=0
WARNINGS=0

echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}  Production Testing Suite${NC}"
echo -e "${BLUE}========================================${NC}"
echo ""

# Test function
test_service() {
    local name=$1
    local test_command=$2
    local description=$3

    echo -ne "Testing ${description}... "
    if eval "$test_command" > /dev/null 2>&1; then
        echo -e "${GREEN}✓ PASS${NC}"
        ((PASSED++))
        return 0
    else
        echo -e "${RED}✗ FAIL${NC}"
        ((FAILED++))
        return 1
    fi
}

# Test with output
test_with_output() {
    local name=$1
    local test_command=$2
    local description=$3

    echo -e "\n${YELLOW}Testing ${description}...${NC}"
    if output=$(eval "$test_command" 2>&1); then
        echo -e "${GREEN}✓ PASS${NC}"
        echo "$output"
        ((PASSED++))
        return 0
    else
        echo -e "${RED}✗ FAIL${NC}"
        echo "$output"
        ((FAILED++))
        return 1
    fi
}

echo -e "${BLUE}1. Docker Infrastructure Tests${NC}"
echo "================================"

test_service "docker" "docker --version" "Docker installation"
test_service "docker-compose" "docker-compose --version" "Docker Compose installation"
test_service "docker-running" "docker ps > /dev/null" "Docker daemon running"

echo ""
echo -e "${BLUE}2. ML Services Health Checks${NC}"
echo "================================"

test_service "mlflow" "curl -sf http://localhost:5000/health" "MLFlow tracking server"
test_service "minio-live" "curl -sf http://localhost:9000/minio/health/live" "MinIO liveness"
test_service "minio-ready" "curl -sf http://localhost:9000/minio/health/ready" "MinIO readiness"
test_service "redis-ml" "redis-cli -p 6380 ping | grep -q PONG" "Redis ML cache"

echo ""
echo -e "${BLUE}3. Database Health Checks${NC}"
echo "================================"

test_service "postgres" "docker exec quant-postgres pg_isready -U postgres" "PostgreSQL"
test_service "postgres-quant-db" "docker exec quant-postgres psql -U postgres -lqt | cut -d \| -f 1 | grep -qw quant" "Quant database exists"

echo ""
echo -e "${BLUE}4. Container Status Checks${NC}"
echo "================================"

EXPECTED_CONTAINERS=("quant-mlflow" "quant-minio" "quant-redis-ml" "quant-postgres")

for container in "${EXPECTED_CONTAINERS[@]}"; do
    test_service "$container" "docker ps --filter name=$container --filter status=running | grep -q $container" "Container: $container"
done

echo ""
echo -e "${BLUE}5. Network Connectivity Tests${NC}"
echo "================================"

# Test inter-container networking
test_service "minio-from-mlflow" "docker exec quant-mlflow curl -sf http://minio:9000/minio/health/live" "MLFlow → MinIO connectivity"

echo ""
echo -e "${BLUE}6. Storage and Volumes${NC}"
echo "================================"

# Check volumes exist
EXPECTED_VOLUMES=("postgres-data" "minio-data" "redis-ml-data" "mlflow-data")

for volume in "${EXPECTED_VOLUMES[@]}"; do
    test_service "$volume" "docker volume inspect docker_$volume > /dev/null" "Volume: $volume"
done

echo ""
echo -e "${BLUE}7. Port Accessibility${NC}"
echo "================================"

test_service "port-5000" "nc -z localhost 5000" "Port 5000 (MLFlow)"
test_service "port-9000" "nc -z localhost 9000" "Port 9000 (MinIO API)"
test_service "port-9001" "nc -z localhost 9001" "Port 9001 (MinIO Console)"
test_service "port-6380" "nc -z localhost 6380" "Port 6380 (Redis ML)"
test_service "port-5432" "nc -z localhost 5432" "Port 5432 (PostgreSQL)"

echo ""
echo -e "${BLUE}8. Service Response Times${NC}"
echo "================================"

# MLFlow response time
mlflow_time=$(curl -o /dev/null -s -w '%{time_total}' http://localhost:5000/health)
echo -e "MLFlow response time: ${mlflow_time}s"
if (( $(echo "$mlflow_time < 1.0" | bc -l) )); then
    echo -e "${GREEN}✓ PASS${NC} (< 1s)"
    ((PASSED++))
else
    echo -e "${YELLOW}⚠ WARN${NC} (> 1s)"
    ((WARNINGS++))
fi

# MinIO response time
minio_time=$(curl -o /dev/null -s -w '%{time_total}' http://localhost:9000/minio/health/live)
echo -e "MinIO response time: ${minio_time}s"
if (( $(echo "$minio_time < 1.0" | bc -l) )); then
    echo -e "${GREEN}✓ PASS${NC} (< 1s)"
    ((PASSED++))
else
    echo -e "${YELLOW}⚠ WARN${NC} (> 1s)"
    ((WARNINGS++))
fi

echo ""
echo -e "${BLUE}9. Resource Usage${NC}"
echo "================================"

# Check container resource usage
docker stats --no-stream --format "table {{.Name}}\t{{.CPUPerc}}\t{{.MemUsage}}" \
    quant-mlflow quant-minio quant-redis-ml quant-postgres 2>/dev/null || echo "Unable to get stats"

echo ""
echo -e "${BLUE}10. Log Health Checks${NC}"
echo "================================"

# Check for errors in logs
echo "Checking MLFlow logs for errors..."
if docker logs quant-mlflow --tail 50 2>&1 | grep -i "error\|failed\|exception" | grep -v "No module named 'psycopg2'" > /tmp/mlflow_errors.txt; then
    echo -e "${YELLOW}⚠ WARN${NC} - Found errors in MLFlow logs:"
    cat /tmp/mlflow_errors.txt
    ((WARNINGS++))
else
    echo -e "${GREEN}✓ PASS${NC} - No critical errors in MLFlow logs"
    ((PASSED++))
fi

echo ""
echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}  Test Summary${NC}"
echo -e "${BLUE}========================================${NC}"
echo -e "${GREEN}Passed:   $PASSED${NC}"
echo -e "${RED}Failed:   $FAILED${NC}"
echo -e "${YELLOW}Warnings: $WARNINGS${NC}"
echo ""

if [ $FAILED -eq 0 ]; then
    echo -e "${GREEN}✓ All critical tests passed!${NC}"
    echo -e "${GREEN}System is ready for production${NC}"
    exit 0
else
    echo -e "${RED}✗ Some tests failed${NC}"
    echo -e "${YELLOW}Please review failures before deploying to production${NC}"
    exit 1
fi
