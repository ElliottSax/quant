# Task #10: Premium Features - Quick Start

## Overview

Premium monetization system with alerts, API tracking, portfolio monitoring, and Stripe billing.

## Installation (5 minutes)

```bash
# 1. Install dependencies
cd quant/backend
pip install stripe>=7.0.0

# 2. Configure Stripe
echo "STRIPE_SECRET_KEY=sk_test_your_key" >> .env
echo "STRIPE_PUBLISHABLE_KEY=pk_test_your_key" >> .env
echo "STRIPE_WEBHOOK_SECRET=whsec_your_secret" >> .env

# 3. Run migration
alembic upgrade head

# 4. Start server
uvicorn app.main:app --reload

# 5. Test
pytest tests/test_premium_features.py -v
```

## Quick Test

```bash
# Create alert
curl -X POST http://localhost:8000/api/v1/alerts \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Test Alert",
    "alert_type": "trade",
    "conditions": {"ticker": "AAPL"},
    "notification_channels": ["email"]
  }'

# Check usage
curl http://localhost:8000/api/v1/subscriptions/usage \
  -H "Authorization: Bearer <token>"

# Create watchlist
curl -X POST http://localhost:8000/api/v1/portfolios/watchlists \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "My List",
    "politician_ids": ["uuid1", "uuid2"]
  }'
```

## Subscription Tiers

| Tier | Price | API Limit | Alerts |
|------|-------|-----------|--------|
| Free | $0 | 100/day | 1 |
| Basic | $9.99 | 1,000/day | 10 |
| Premium | $29.99 | 10,000/day | 50 |
| Enterprise | $99.99 | 100,000/day | ∞ |

## API Endpoints

**Alerts**: `/api/v1/alerts`
**Subscriptions**: `/api/v1/subscriptions`
**Portfolios**: `/api/v1/portfolios`

**Docs**: http://localhost:8000/api/v1/docs

## Files Created

- 3 Models (`app/models/`)
- 3 Services (`app/services/`)
- 3 API files (`app/api/v1/`)
- 1 Migration (`alembic/versions/`)
- 1 Test file (`tests/`)
- 4 Docs

## Status: ✅ COMPLETE

All requirements met. Production-ready. Ready to deploy.

## Documentation

- Full Guide: `PREMIUM_FEATURES_DOCUMENTATION.md`
- Complete Report: `TASK_10_FINAL_REPORT.md`
- Implementation: `TASK_10_IMPLEMENTATION_SUMMARY.md`

## Support

- API Docs: `/api/v1/docs`
- Tests: `pytest tests/test_premium_features.py -v`
- Verify: `python3 verify_premium_features.py`
