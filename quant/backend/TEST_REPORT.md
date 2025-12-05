# Platform Test Report
**Date:** 2025-11-26T16:59:19.983856
**Total Tests:** 30
**Pass Rate:** 24/30 (80.0%)

## File Structure

| Test | Status | Message |
|------|--------|----------|
| main.py | ✅ pass | Exists (6872 bytes) |
| __init__.py | ✅ pass | Exists (1394 bytes) |
| signal_generator.py | ✅ pass | Exists (16424 bytes) |
| backtesting.py | ✅ pass | Exists (17994 bytes) |
| email_service.py | ✅ pass | Exists (10252 bytes) |
| page.tsx | ✅ pass | Exists (10985 bytes) |
| PriceChart.tsx | ✅ pass | Exists (1700 bytes) |

## Dependencies

| Test | Status | Message |
|------|--------|----------|
| fastapi package | ✅ pass | FastAPI framework |
| uvicorn package | ✅ pass | ASGI server |
| sqlalchemy package | ✅ pass | ORM |
| redis package | ✅ pass | Redis client |
| pandas package | ✅ pass | Data analysis |
| numpy package | ✅ pass | Numerical computing |
| yfinance package | ✅ pass | Market data |
| scipy package | ✅ pass | Scientific computing |
| celery package | ✅ pass | Task queue |
| httpx package | ✅ pass | HTTP client |
| pydantic package | ✅ pass | Data validation |

## Infrastructure

| Test | Status | Message |
|------|--------|----------|
| quant-postgres container | ✅ pass | Running (port 5432) |
| quant-redis-ml container | ✅ pass | Running (port 6380) |
| quant-mlflow container | ✅ pass | Running (port 5000) |
| quant-minio container | ✅ pass | Running (port 9000) |

## Backend API

| Test | Status | Message |
|------|--------|----------|
| Health check | ⏭️ skip | Backend not running |
| API documentation | ⏭️ skip | Backend not running |
| Auth endpoint (should fail without token) | ⏭️ skip | Backend not running |

## Frontend

| Test | Status | Message |
|------|--------|----------|
| Home page | ✅ pass | Loaded successfully (9187 bytes) |
| Dashboard page | ✅ pass | Loaded successfully (10024 bytes) |
| Signals page | ❌ fail | Status 404 |
| Backtesting page | ❌ fail | Status 404 |
| Discoveries page | ❌ fail | HTTPConnectionPool(host='localhost', port=3000): Read timed out. (read timeout=10) |

