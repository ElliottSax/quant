#!/bin/bash

# Comprehensive Test Suite Runner
# Runs all tests and generates coverage reports

set -e

echo "========================================="
echo "Comprehensive Test Suite for Quant API"
echo "========================================="
echo ""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Change to backend directory
cd "$(dirname "$0")"

# Clean previous coverage data
echo "🧹 Cleaning previous coverage data..."
rm -f .coverage coverage.json
rm -rf htmlcov/

# Run unit tests
echo ""
echo "📝 Running Unit Tests..."
echo "========================"
python3 -m pytest tests/test_models/ tests/test_core/ tests/test_services/ \
    -v --tb=short \
    --cov=app \
    --cov-append \
    --cov-report=term-missing \
    -m "not slow" || echo -e "${YELLOW}Some unit tests failed${NC}"

# Run API tests
echo ""
echo "🌐 Running API Tests..."
echo "======================="
python3 -m pytest tests/test_api/ \
    -v --tb=short \
    --cov=app \
    --cov-append \
    --cov-report=term-missing \
    -m "not slow" || echo -e "${YELLOW}Some API tests failed${NC}"

# Run integration tests
echo ""
echo "🔗 Running Integration Tests..."
echo "==============================="
python3 -m pytest tests/test_integration/ \
    -v --tb=short \
    --cov=app \
    --cov-append \
    --cov-report=term-missing || echo -e "${YELLOW}Some integration tests failed${NC}"

# Run security tests
echo ""
echo "🔒 Running Security Tests..."
echo "============================"
python3 -m pytest tests/test_security/ tests/security/ \
    -v --tb=short \
    --cov=app \
    --cov-append \
    --cov-report=term-missing || echo -e "${YELLOW}Some security tests failed${NC}"

# Run performance tests (benchmarks only, not load tests)
echo ""
echo "⚡ Running Performance Benchmarks..."
echo "==================================="
python3 -m pytest tests/performance/test_benchmarks.py \
    -v --tb=short \
    --cov=app \
    --cov-append \
    --cov-report=term-missing || echo -e "${YELLOW}Some performance tests failed${NC}"

# Run ML tests
echo ""
echo "🤖 Running ML Tests..."
echo "====================="
python3 -m pytest tests/test_ml/ tests/ml/ \
    -v --tb=short \
    --cov=app \
    --cov-append \
    --cov-report=term-missing || echo -e "${YELLOW}Some ML tests failed${NC}"

# Generate final coverage reports
echo ""
echo "📊 Generating Coverage Reports..."
echo "================================="
python3 -m pytest --cov=app \
    --cov-report=html \
    --cov-report=json \
    --cov-report=term-missing \
    --collect-only > /dev/null 2>&1 || true

# Display coverage summary
echo ""
echo "📈 Coverage Summary"
echo "==================="
python3 -m coverage report --skip-empty

# Calculate coverage percentage
COVERAGE=$(python3 -m coverage report | grep TOTAL | awk '{print $4}' | sed 's/%//')

echo ""
echo "========================================="
if (( $(echo "$COVERAGE >= 95" | bc -l) )); then
    echo -e "${GREEN}✅ Coverage Goal Met: ${COVERAGE}% >= 95%${NC}"
    EXIT_CODE=0
elif (( $(echo "$COVERAGE >= 90" | bc -l) )); then
    echo -e "${YELLOW}⚠️  Almost There: ${COVERAGE}% (Need ${NC}$(echo "95 - $COVERAGE" | bc)${YELLOW}% more)${NC}"
    EXIT_CODE=1
else
    echo -e "${RED}❌ Coverage Goal Not Met: ${COVERAGE}% < 95%${NC}"
    echo -e "${RED}   Need to increase coverage by $(echo "95 - $COVERAGE" | bc)%${NC}"
    EXIT_CODE=1
fi

echo ""
echo "📁 Detailed HTML report: htmlcov/index.html"
echo "📄 JSON report: coverage.json"
echo "========================================="

exit $EXIT_CODE
