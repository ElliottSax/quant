#!/bin/bash
# Curl Examples for Quant Backtesting API

# Set your API URL (change after Railway deployment)
API_URL="https://your-app.railway.app"

echo "🚀 Quant Backtesting API - Curl Examples"
echo "=========================================="
echo ""

# 1. Health Check
echo "1. Health Check"
echo "   curl $API_URL/health"
curl -s "$API_URL/health" | jq '.'
echo ""

# 2. List Strategies
echo "2. List Available Strategies"
echo "   curl $API_URL/api/v1/backtesting/demo/strategies"
curl -s "$API_URL/api/v1/backtesting/demo/strategies" | jq '.'
echo ""

# 3. Run Backtest
echo "3. Run Backtest for AAPL"
echo "   curl -X POST $API_URL/api/v1/backtesting/demo/run ..."
curl -X POST "$API_URL/api/v1/backtesting/demo/run" \
  -H "Content-Type: application/json" \
  -d '{
    "symbol": "AAPL",
    "start_date": "2025-06-01T00:00:00",
    "end_date": "2025-12-31T23:59:59",
    "strategy": "ma_crossover",
    "initial_capital": 100000
  }' | jq '.'
echo ""

# 4. Run Backtest with Custom Parameters
echo "4. Run Backtest with Custom Strategy Parameters"
curl -X POST "$API_URL/api/v1/backtesting/demo/run" \
  -H "Content-Type: application/json" \
  -d '{
    "symbol": "GOOGL",
    "start_date": "2025-06-01T00:00:00",
    "end_date": "2025-12-31T23:59:59",
    "strategy": "ma_crossover",
    "initial_capital": 100000,
    "strategy_params": {
      "fast_period": 10,
      "slow_period": 30
    }
  }' | jq '.total_return, .sharpe_ratio, .total_trades'
echo ""

# 5. API Documentation
echo "5. View API Documentation"
echo "   Open: $API_URL/api/v1/docs"
echo ""

echo "✅ Examples complete!"
