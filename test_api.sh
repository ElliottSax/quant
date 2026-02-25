#!/bin/bash

# API Testing Script
set -e

echo "=========================================="
echo "  API Testing Suite"
echo "=========================================="
echo ""

BASE_URL="http://localhost:8000/api/v1"

# Test 1: Health Check
echo "1. Testing API Health..."
echo -n "  GET /health: "
if curl -sf ${BASE_URL}/health > /dev/null; then
    echo "✓ OK"
else
    echo "✗ FAILED"
    exit 1
fi

# Test 2: Get API version
echo ""
echo "2. Testing API Info..."
curl -s ${BASE_URL}/health | python3 -m json.tool 2>/dev/null || echo "Response received but not JSON"

# Test 3: Authentication endpoint
echo ""
echo "3. Testing Authentication..."
echo -n "  POST /auth/register: "
REGISTER_RESPONSE=$(curl -s -X POST ${BASE_URL}/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "TestPassword123!",
    "full_name": "Test User"
  }' 2>&1)

if echo "$REGISTER_RESPONSE" | grep -q "email"; then
    echo "✓ OK (or user exists)"
else
    echo "Response: $REGISTER_RESPONSE"
fi

# Test 4: Login
echo -n "  POST /auth/login: "
LOGIN_RESPONSE=$(curl -s -X POST ${BASE_URL}/auth/login \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=test@example.com&password=TestPassword123!" 2>&1)

if echo "$LOGIN_RESPONSE" | grep -q "access_token"; then
    echo "✓ OK"
    ACCESS_TOKEN=$(echo "$LOGIN_RESPONSE" | python3 -c "import sys, json; print(json.load(sys.stdin)['access_token'])" 2>/dev/null || echo "")
    echo "  Access token obtained: ${ACCESS_TOKEN:0:20}..."
else
    echo "⚠ Login failed (might be expected)"
    ACCESS_TOKEN=""
fi

# Test 5: Protected endpoint
if [ -n "$ACCESS_TOKEN" ]; then
    echo ""
    echo "4. Testing Protected Endpoints..."
    echo -n "  GET /auth/me: "
    ME_RESPONSE=$(curl -s ${BASE_URL}/auth/me \
      -H "Authorization: Bearer $ACCESS_TOKEN" 2>&1)

    if echo "$ME_RESPONSE" | grep -q "email"; then
        echo "✓ OK"
    else
        echo "✗ FAILED"
    fi
fi

# Test 6: Public endpoints
echo ""
echo "5. Testing Public Endpoints..."
echo -n "  GET /politicians: "
POLITICIANS_RESPONSE=$(curl -s ${BASE_URL}/politicians?limit=5 2>&1)
if echo "$POLITICIANS_RESPONSE" | grep -q "\["; then
    echo "✓ OK"
    POLITICIAN_COUNT=$(echo "$POLITICIANS_RESPONSE" | python3 -c "import sys, json; print(len(json.load(sys.stdin)))" 2>/dev/null || echo "0")
    echo "  Found $POLITICIAN_COUNT politicians"
else
    echo "⚠ No data or failed"
fi

echo -n "  GET /trades: "
TRADES_RESPONSE=$(curl -s ${BASE_URL}/trades?limit=5 2>&1)
if echo "$TRADES_RESPONSE" | grep -q "\["; then
    echo "✓ OK"
    TRADE_COUNT=$(echo "$TRADES_RESPONSE" | python3 -c "import sys, json; print(len(json.load(sys.stdin)))" 2>/dev/null || echo "0")
    echo "  Found $TRADE_COUNT trades"
else
    echo "⚠ No data or failed"
fi

# Test 7: API Documentation
echo ""
echo "6. Testing API Documentation..."
echo -n "  GET /docs: "
if curl -sf http://localhost:8000/docs > /dev/null; then
    echo "✓ OK - Swagger UI available at http://localhost:8000/docs"
else
    echo "✗ FAILED"
fi

echo -n "  GET /redoc: "
if curl -sf http://localhost:8000/redoc > /dev/null; then
    echo "✓ OK - ReDoc available at http://localhost:8000/redoc"
else
    echo "✗ FAILED"
fi

echo ""
echo "=========================================="
echo "  API Tests Completed"
echo "=========================================="
