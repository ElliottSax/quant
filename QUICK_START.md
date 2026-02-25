# Quant Analytics Platform - Quick Start Guide

**Version:** 1.0.0
**Status:** 95%+ Operational ✅
**Last Updated:** 2025-11-26

---

## 🚀 Platform Overview

A comprehensive quantitative trading analytics platform featuring:
- Real-time trading signals with 10+ technical indicators
- Backtesting engine with realistic market simulation
- Portfolio optimization using Modern Portfolio Theory
- Sentiment analysis with AI integration
- Automated reporting and email delivery
- Interactive data visualizations

---

## ✅ Current Status

**All Systems Operational:**
- ✅ Backend API: http://localhost:8000
- ✅ Frontend: http://localhost:3000
- ✅ PostgreSQL: localhost:5432
- ✅ Redis: localhost:6380
- ✅ MLflow: localhost:5000
- ✅ MinIO: localhost:9000-9001

---

## 🎯 Quick Access

### Frontend Pages
```
✅ Home:         http://localhost:3000/
✅ Dashboard:    http://localhost:3000/dashboard
✅ Discoveries:  http://localhost:3000/discoveries
✅ Politicians:  http://localhost:3000/politicians
🟡 Signals:      http://localhost:3000/signals (reload if 404)
🟡 Backtesting:  http://localhost:3000/backtesting (reload if 404)
```

### Backend API
```
✅ Health:       http://localhost:8000/health
✅ API Docs:     http://localhost:8000/docs
✅ OpenAPI:      http://localhost:8000/openapi.json
✅ Auth:         http://localhost:8000/api/v1/auth/login
```

---

## 🔧 Services Management

### Check Service Status
```bash
# Backend health
curl http://localhost:8000/health

# Frontend
curl -I http://localhost:3000

# Infrastructure
docker ps | grep quant

# Ports in use
lsof -i :8000  # Backend
lsof -i :3000  # Frontend
lsof -i :5432  # PostgreSQL
lsof -i :6380  # Redis
```

### Start Services

**Backend:**
```bash
cd /mnt/e/projects/quant/quant/backend

# Set environment variables
export SECRET_KEY="wR33Elo9wMAOIOHxyToVy8RE7c83SFuW6J0kfeY_jMo"
export DATABASE_URL="postgresql://quant_user:quant_password@localhost:5432/quant_db"
export REDIS_URL="redis://localhost:6380/0"
export ENVIRONMENT="development"
export DEBUG="true"

# Start server
python3 -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload

# Or use the startup script
./start_backend.sh
```

**Frontend:**
```bash
cd /mnt/e/projects/quant/quant/frontend
npm run dev
```

**Infrastructure (if not running):**
```bash
cd /mnt/e/projects/quant
docker-compose up -d
```

### Stop Services

```bash
# Stop backend
pkill -f uvicorn

# Stop frontend (Ctrl+C in terminal or)
pkill -f "next dev"

# Stop Docker services
docker-compose down
```

---

## 🧪 Testing

### Run Comprehensive Tests
```bash
cd /mnt/e/projects/quant
python3 comprehensive_test.py
```

**Test Coverage:**
- Infrastructure health checks (4 tests)
- Python dependencies (11 tests)
- File structure validation (7 tests)
- API endpoint testing (3+ tests)
- Frontend page testing (5 tests)

**Expected Results:**
- Total: 30 tests
- Pass rate: 95%+
- Reports: `test_report.json`, `TEST_REPORT.md`

### Manual API Testing
```bash
# Health check
curl http://localhost:8000/health

# List all endpoints
curl http://localhost:8000/openapi.json | python3 -m json.tool

# Test authentication (get token)
curl -X POST "http://localhost:8000/api/v1/auth/login?username=admin&password=admin"

# Use token for protected endpoints
TOKEN="your_token_here"
curl -H "Authorization: Bearer $TOKEN" http://localhost:8000/api/v1/protected
```

---

## 📊 Key Features

### 1. Trading Signals
**Location:** `app/services/signal_generator.py` (550 lines)

**Technical Indicators:**
- RSI (Relative Strength Index)
- MACD (Moving Average Convergence Divergence)
- Bollinger Bands
- SMA/EMA (Simple/Exponential Moving Averages)
- ATR (Average True Range)
- Volume analysis
- Momentum indicators

**API Endpoints:**
```bash
# Generate signal for a symbol
curl -X POST http://localhost:8000/api/v1/signals/generate \
  -H "Content-Type: application/json" \
  -d '{"symbol": "AAPL", "timeframe": "1d"}'

# WebSocket real-time streaming
ws://localhost:8000/api/v1/signals/ws/AAPL
```

**Frontend:** http://localhost:3000/signals

---

### 2. Backtesting Engine
**Location:** `app/services/backtesting.py` (650 lines)

**Features:**
- Realistic market simulation with slippage
- Order types: Market, Limit, Stop, Stop-Limit
- Performance metrics: Sharpe, Sortino, Max Drawdown, Profit Factor
- Position tracking with P&L
- Commission and fee modeling

**API Endpoints:**
```bash
# Run backtest
curl -X POST http://localhost:8000/api/v1/backtesting/run \
  -H "Content-Type: application/json" \
  -d '{
    "symbol": "AAPL",
    "start_date": "2023-01-01",
    "end_date": "2024-01-01",
    "initial_capital": 100000,
    "strategy": "rsi_crossover"
  }'
```

**Frontend:** http://localhost:3000/backtesting

---

### 3. Portfolio Optimization
**Location:** `app/services/portfolio_optimization.py` (530 lines)

**Strategies:**
1. Max Sharpe Ratio
2. Min Volatility
3. Max Return
4. Risk Parity
5. Efficient Frontier
6. Max Diversification

**API Endpoints:**
```bash
# Optimize portfolio
curl -X POST http://localhost:8000/api/v1/portfolio/optimize \
  -H "Content-Type: application/json" \
  -d '{
    "symbols": ["AAPL", "GOOGL", "MSFT"],
    "objective": "max_sharpe",
    "risk_tolerance": 0.15
  }'

# Generate efficient frontier
curl -X POST http://localhost:8000/api/v1/portfolio/efficient-frontier \
  -H "Content-Type: application/json" \
  -d '{"symbols": ["AAPL", "GOOGL", "MSFT"]}'
```

---

### 4. Market Data Integration
**Location:** `app/services/market_data.py` (380 lines)

**Data Sources:**
- Yahoo Finance (yfinance) - Primary
- Alpha Vantage - Ready
- Polygon.io - Ready
- IEX Cloud - Ready
- Mock data - Fallback

**API Endpoints:**
```bash
# Get real-time quote
curl http://localhost:8000/api/v1/market-data/quote/AAPL

# Get historical data
curl "http://localhost:8000/api/v1/market-data/historical/AAPL?start=2024-01-01&end=2024-12-01"

# Get company info
curl http://localhost:8000/api/v1/market-data/info/AAPL
```

---

### 5. Sentiment Analysis
**Location:** `app/services/sentiment_analysis.py` (450 lines)

**Data Sources:**
- News articles
- Social media
- Financial reports
- Analyst ratings

**Features:**
- AI-powered sentiment scoring
- Keyword fallback analysis
- Historical tracking
- Correlation with price movements

**API Endpoints:**
```bash
# Analyze current sentiment
curl http://localhost:8000/api/v1/sentiment/analyze/AAPL

# Get historical sentiment
curl "http://localhost:8000/api/v1/sentiment/history/AAPL?days=30"
```

---

### 6. Automated Reporting
**Location:** `app/services/reporting.py` (380 lines)

**Report Types:**
- Daily summary
- Weekly performance
- Monthly analysis
- Portfolio snapshot

**Output Formats:**
- JSON
- Markdown
- HTML
- Plain text

**API Endpoints:**
```bash
# Generate daily report
curl -X POST http://localhost:8000/api/v1/reports/daily

# Schedule weekly report
curl -X POST http://localhost:8000/api/v1/reports/schedule \
  -H "Content-Type: application/json" \
  -d '{
    "report_type": "weekly",
    "recipients": ["user@example.com"],
    "schedule": "monday_9am"
  }'
```

---

### 7. Email Delivery
**Location:** `app/services/email_service.py` (350+ lines)

**Providers Supported:**
- SMTP (Gmail, Outlook, etc.)
- SendGrid
- AWS SES
- Mailgun

**Configuration:**
```python
# SMTP (Gmail example)
export SMTP_HOST="smtp.gmail.com"
export SMTP_PORT="587"
export SMTP_USER="your-email@gmail.com"
export SMTP_PASSWORD="your-app-password"

# SendGrid
export SENDGRID_API_KEY="your-api-key"

# AWS SES
# Configure AWS credentials

# Mailgun
export MAILGUN_API_KEY="your-api-key"
export MAILGUN_DOMAIN="your-domain.com"
```

---

### 8. Celery Background Tasks
**Location:** `app/tasks/scheduled_reports.py` (250+ lines)

**Start Celery Worker:**
```bash
cd /mnt/e/projects/quant/quant/backend
celery -A app.tasks.scheduled_reports worker --loglevel=info
```

**Start Celery Beat (Scheduler):**
```bash
celery -A app.tasks.scheduled_reports beat --loglevel=info
```

**Scheduled Tasks:**
- Daily reports (configurable time)
- Weekly reports (Monday morning)
- Monthly reports (1st of month)
- Signal alerts (real-time)

---

### 9. Interactive Charts
**Location:** `quant/frontend/src/components/charts/`

**Components:**
- `PriceChart.tsx` - OHLCV line chart
- `PortfolioChart.tsx` - Allocation pie chart
- `EfficientFrontierChart.tsx` - Risk/return scatter plot
- `EquityCurveChart.tsx` - Equity curve with returns

**Technology:** Recharts (React charting library)

---

## 🐛 Troubleshooting

### Backend Won't Start

**Problem:** `ModuleNotFoundError: No module named 'hmmlearn'`

**Solution:**
```bash
pip3 install --break-system-packages hmmlearn scikit-learn statsmodels email-validator
```

**Problem:** `SECRET_KEY contains insecure pattern`

**Solution:** Use the provided secure key:
```bash
export SECRET_KEY="wR33Elo9wMAOIOHxyToVy8RE7c83SFuW6J0kfeY_jMo"
```

**Problem:** `Address already in use` (port 8000)

**Solution:**
```bash
# Kill existing process
pkill -f uvicorn
# Or find and kill specific PID
lsof -i :8000
kill -9 <PID>
```

---

### Frontend Pages Show 404

**Problem:** `/signals` or `/backtesting` return 404

**Solution:** Clear Next.js cache and rebuild:
```bash
cd /mnt/e/projects/quant/quant/frontend
rm -rf .next
npm run dev
```

---

### Database Connection Issues

**Problem:** Can't connect to PostgreSQL

**Solution:**
```bash
# Check if PostgreSQL is running
docker ps | grep quant-postgres

# Start if not running
docker start quant-postgres

# Test connection
psql -h localhost -p 5432 -U quant_user -d quant_db
# Password: quant_password
```

---

### Redis Connection Issues

**Problem:** Can't connect to Redis

**Solution:**
```bash
# Check if Redis is running
docker ps | grep quant-redis

# Start if not running
docker start quant-redis-ml

# Test connection
redis-cli -p 6380 ping
# Should return: PONG
```

---

## 📚 Documentation

### Available Documents
```
QUICK_START.md                      - This file
DEBUG_REPORT.md                     - Technical debugging guide
TEST_AND_DEBUG_SUMMARY.md           - Test results summary
FINAL_TEST_STATUS.md                - Current platform status
comprehensive_test.py               - Automated test suite
```

### API Documentation
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc
- OpenAPI JSON: http://localhost:8000/openapi.json

---

## 🔐 Security Notes

### Development vs Production

**Current Setup (Development):**
- DEBUG mode enabled
- Hardcoded credentials in scripts
- No HTTPS
- Permissive CORS

**For Production:**
1. Set `ENVIRONMENT=production`
2. Use environment variables for all secrets
3. Enable HTTPS
4. Configure proper CORS origins
5. Use strong database passwords
6. Rotate SECRET_KEY regularly
7. Enable rate limiting
8. Set up monitoring and logging

### Environment Variables

**Required:**
```bash
SECRET_KEY="<32+ character random string>"
DATABASE_URL="postgresql://user:pass@host:port/db"
REDIS_URL="redis://host:port/db"
ENVIRONMENT="production"
DEBUG="false"
```

**Optional:**
```bash
SMTP_HOST="smtp.gmail.com"
SMTP_USER="your-email@gmail.com"
SMTP_PASSWORD="your-app-password"
SENDGRID_API_KEY="..."
AWS_ACCESS_KEY_ID="..."
AWS_SECRET_ACCESS_KEY="..."
```

---

## 📈 Performance Tips

### Backend Optimization
1. Enable Redis caching for frequently accessed data
2. Use database connection pooling
3. Implement query optimization
4. Enable gzip compression
5. Use async/await throughout

### Frontend Optimization
1. Implement code splitting
2. Use Next.js Image optimization
3. Enable static generation where possible
4. Implement virtual scrolling for large lists
5. Lazy load charts and heavy components

---

## 🚀 Next Steps

### Immediate Actions (Optional)
1. Clear Next.js cache to fix remaining 404s
2. Restart backend to load newest endpoints
3. Configure email service for reports
4. Set up Celery for scheduled tasks

### Short Term Enhancements
1. Add authentication/authorization
2. Implement user management
3. Add more data providers
4. Create custom trading strategies
5. Add real-time WebSocket updates

### Long Term Goals
1. Deploy to production (AWS/GCP/Azure)
2. Add monitoring (Prometheus/Grafana)
3. Implement A/B testing
4. Add machine learning models
5. Create mobile app

---

## 💡 Useful Commands

### Development Workflow
```bash
# Start all services
docker-compose up -d
cd quant/backend && python3 -m uvicorn app.main:app --reload &
cd quant/frontend && npm run dev &

# Run tests
python3 comprehensive_test.py

# Check logs
docker logs quant-postgres
docker logs quant-redis-ml
docker logs quant-mlflow

# Database migrations (if using Alembic)
alembic upgrade head

# Generate new migration
alembic revision --autogenerate -m "description"
```

### Data Operations
```bash
# Access PostgreSQL
docker exec -it quant-postgres psql -U quant_user -d quant_db

# Access Redis
docker exec -it quant-redis-ml redis-cli

# View MLflow UI
open http://localhost:5000

# Access MinIO console
open http://localhost:9001
```

---

## 🎯 Platform Statistics

**Code Base:**
- Total Lines: ~8,500+
- Backend Files: 27
- Frontend Files: 20+
- Test Files: 4
- Documentation: 8 files

**Features:**
- API Endpoints: 50+
- Frontend Pages: 7
- Chart Components: 4
- Background Tasks: 5+
- Data Providers: 4

**Test Coverage:**
- Automated Tests: 30
- Pass Rate: 95%+
- Categories: 5

---

## 📞 Support

### Issue Reporting
1. Check this guide first
2. Review `DEBUG_REPORT.md` for common issues
3. Run `comprehensive_test.py` to diagnose
4. Check service logs
5. Document error messages and steps to reproduce

### Resources
- API Docs: http://localhost:8000/docs
- Source Code: /mnt/e/projects/quant
- Test Reports: test_report.json, TEST_REPORT.md
- Debug Reports: DEBUG_REPORT.md, TEST_AND_DEBUG_SUMMARY.md

---

**Platform Status:** ✅ 95%+ Operational
**Ready for:** Development, Testing, Production (after security hardening)
**Last Tested:** 2025-11-26

---

*Quick Start Guide - Quant Analytics Platform v1.0.0*
