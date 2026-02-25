# Premium Features Documentation (Task #10)

## Overview

This document describes the premium monetization features implemented in the Quant Analytics Platform.

## Features Implemented

### 1. Real-Time Trade Alerts

Alert system for monitoring trades and market conditions with flexible notification delivery.

#### Models

- **Alert**: Stores alert configurations
  - Types: `trade`, `price`, `politician_activity`, `pattern`
  - Notification channels: `email`, `webhook`, `push`, `sms`
  - Status: `active`, `paused`, `triggered`, `expired`

#### Services

- **AlertService** (`app/services/alert_service.py`)
  - `create_alert()`: Create new alerts
  - `get_user_alerts()`: Get user's alerts
  - `delete_alert()`: Delete alerts
  - `update_alert()`: Update alert configurations
  - `process_new_trade()`: Process trades against active alerts

- **AlertMatchingEngine**: Matches trades against alert conditions
- **NotificationService**: Delivers notifications via email, webhook, push

#### API Endpoints

```
POST   /api/v1/alerts                 - Create alert
GET    /api/v1/alerts                 - Get all alerts
GET    /api/v1/alerts/{id}            - Get specific alert
PATCH  /api/v1/alerts/{id}            - Update alert
DELETE /api/v1/alerts/{id}            - Delete alert
GET    /api/v1/alerts/statistics/summary - Get alert statistics
```

#### Example: Create Trade Alert

```json
POST /api/v1/alerts
{
  "name": "Large AAPL Trades",
  "alert_type": "trade",
  "conditions": {
    "ticker": "AAPL",
    "min_amount": 100000,
    "transaction_type": "buy"
  },
  "notification_channels": ["email", "webhook"],
  "webhook_url": "https://example.com/webhook"
}
```

### 2. Developer API Access with Usage Tracking

Enhanced API key system with usage tracking and rate limiting per subscription tier.

#### Models

- **APIKey**: Enhanced with usage tracking
- **UsageRecord**: Tracks API usage by user/key
- **Subscription**: Defines rate limits per tier

#### Services

- **SubscriptionService** (`app/services/subscription_service.py`)
  - `get_rate_limit()`: Get user's rate limit
  - `check_rate_limit()`: Check current usage
  - `record_usage()`: Record API calls
  - `check_premium_access()`: Verify premium status

#### Rate Limits by Tier

| Tier       | Requests/Day | Price/Month |
|------------|--------------|-------------|
| Free       | 100          | $0          |
| Basic      | 1,000        | $9.99       |
| Premium    | 10,000       | $29.99      |
| Enterprise | 100,000      | $99.99      |

#### API Endpoints

```
GET /api/v1/subscriptions/usage        - Get usage statistics
```

#### Example: Check Usage

```json
GET /api/v1/subscriptions/usage
{
  "limit": 10000,
  "used": 450,
  "remaining": 9550,
  "reset_at": "2026-02-04T00:00:00Z"
}
```

### 3. Advanced Analytics Features

Premium users get access to advanced analytics with no historical data limits.

#### Features by Tier

| Feature                  | Free | Basic | Premium |
|--------------------------|------|-------|---------|
| Historical Data Months   | 6    | 24    | Unlimited |
| Alerts                   | 1    | 10    | 50      |
| Watchlists               | 1    | 5     | 20      |
| Export Formats           | JSON | JSON, CSV | JSON, CSV, Excel, PDF |
| Advanced Analytics       | No   | Yes   | Yes     |
| Real-Time Alerts         | No   | Yes   | Yes     |
| Portfolio Tracking       | No   | No    | Yes     |

### 4. Portfolio Tracking

Track politician portfolios over time with performance metrics and risk analysis.

#### Models

- **Portfolio**: Portfolio snapshots with holdings and metrics
- **Watchlist**: Custom politician tracking lists

#### Services

- **PortfolioService** (`app/services/portfolio_service.py`)
  - `calculate_portfolio_snapshot()`: Create portfolio snapshot
  - `get_portfolio_history()`: Get historical snapshots
  - `get_portfolio_report()`: Generate comprehensive report
  - `calculate_portfolio_performance()`: Calculate performance metrics
  - `create_watchlist()`: Create watchlist
  - `get_user_watchlists()`: Get user's watchlists

#### API Endpoints

```
POST   /api/v1/portfolios/watchlists              - Create watchlist
GET    /api/v1/portfolios/watchlists              - Get watchlists
GET    /api/v1/portfolios/watchlists/{id}         - Get specific watchlist
PATCH  /api/v1/portfolios/watchlists/{id}         - Update watchlist
DELETE /api/v1/portfolios/watchlists/{id}         - Delete watchlist
GET    /api/v1/portfolios/{politician_id}/snapshot - Get portfolio snapshot
GET    /api/v1/portfolios/{politician_id}/history  - Get portfolio history
GET    /api/v1/portfolios/{politician_id}/report   - Get portfolio report
GET    /api/v1/portfolios/performance/calculate    - Calculate performance
```

#### Example: Create Watchlist

```json
POST /api/v1/portfolios/watchlists
{
  "name": "Tech-Focused Politicians",
  "politician_ids": ["uuid1", "uuid2", "uuid3"],
  "description": "Politicians trading tech stocks"
}
```

### 5. Stripe Integration

Full Stripe integration for subscription management and billing.

#### Models

- **Subscription**: Stores subscription details with Stripe IDs
  - `stripe_customer_id`
  - `stripe_subscription_id`
  - `stripe_price_id`

#### Services

- **StripeService** (`app/services/subscription_service.py`)
  - `create_customer()`: Create Stripe customer
  - `create_subscription()`: Create Stripe subscription
  - `handle_webhook()`: Handle Stripe webhook events

#### Subscription Plans

| Plan       | Monthly | Yearly (2 months free) |
|------------|---------|------------------------|
| Basic      | $9.99   | $99.90                 |
| Premium    | $29.99  | $299.90                |
| Enterprise | $99.99  | $999.90                |

#### API Endpoints

```
GET  /api/v1/subscriptions/current      - Get current subscription
GET  /api/v1/subscriptions/plans        - Get available plans
POST /api/v1/subscriptions/subscribe    - Create subscription
POST /api/v1/subscriptions/cancel       - Cancel subscription
GET  /api/v1/subscriptions/features     - Get available features
GET  /api/v1/subscriptions/check-access/{feature} - Check feature access
POST /api/v1/subscriptions/webhooks/stripe - Stripe webhook handler
```

#### Example: Subscribe to Premium

```json
POST /api/v1/subscriptions/subscribe
{
  "tier": "premium",
  "billing_cycle": "monthly"
}
```

#### Webhook Events Handled

- `customer.subscription.created`
- `customer.subscription.updated`
- `customer.subscription.deleted`
- `invoice.payment_succeeded`
- `invoice.payment_failed`

## Database Schema

### New Tables

1. **alerts**: Alert configurations and status
2. **portfolios**: Portfolio snapshots over time
3. **watchlists**: Custom politician tracking lists
4. **subscriptions**: User subscription details
5. **usage_records**: API usage tracking

### Migration

```bash
# Run migration to create premium feature tables
cd quant/backend
alembic upgrade head
```

## Setup Instructions

### 1. Install Dependencies

```bash
pip install stripe>=7.0.0
```

### 2. Configure Stripe

Add to `.env`:

```bash
# Stripe Configuration
STRIPE_SECRET_KEY=sk_test_xxx
STRIPE_PUBLISHABLE_KEY=pk_test_xxx
STRIPE_WEBHOOK_SECRET=whsec_xxx
```

### 3. Create Stripe Products

In Stripe Dashboard:

1. Create products for each tier (Basic, Premium, Enterprise)
2. Create prices for monthly and yearly billing
3. Update price IDs in `subscription_service.py`

### 4. Run Database Migration

```bash
cd quant/backend
alembic upgrade head
```

### 5. Test Premium Features

```bash
# Run tests
pytest tests/test_premium_features.py -v
```

## Usage Examples

### Create Alert for New Trades

```python
from app.services.alert_service import alert_service

alert = await alert_service.create_alert(
    db=db,
    user_id=user_id,
    name="Nancy Pelosi AAPL Trades",
    alert_type=AlertType.TRADE,
    conditions={
        "politician_id": "uuid",
        "ticker": "AAPL",
        "min_amount": 50000
    },
    notification_channels=["email", "webhook"],
    webhook_url="https://example.com/webhook"
)
```

### Check User's Rate Limit

```python
from app.services.subscription_service import subscription_service

usage = await subscription_service.check_rate_limit(db, user_id)
print(f"Used: {usage['used']}/{usage['limit']}")
```

### Create Watchlist

```python
from app.services.portfolio_service import portfolio_service

watchlist = await portfolio_service.create_watchlist(
    db=db,
    user_id=user_id,
    name="Senate Finance Committee",
    politician_ids=["uuid1", "uuid2", "uuid3"]
)
```

### Subscribe User to Premium

```python
from app.services.subscription_service import stripe_service

result = await stripe_service.create_subscription(
    db=db,
    user_id=user_id,
    tier=SubscriptionTier.PREMIUM,
    billing_cycle="monthly"
)
```

## Testing

### Unit Tests

```bash
# Run all premium feature tests
pytest tests/test_premium_features.py -v

# Run specific test class
pytest tests/test_premium_features.py::TestAlertService -v

# Run with coverage
pytest tests/test_premium_features.py --cov=app.services --cov-report=html
```

### Integration Tests

```bash
# Test alert creation and matching
pytest tests/test_premium_features.py::TestAlertService::test_create_alert -v

# Test subscription upgrade
pytest tests/test_premium_features.py::TestSubscriptionService::test_upgrade_subscription -v

# Test portfolio tracking
pytest tests/test_premium_features.py::TestPortfolioService::test_create_watchlist -v
```

## Security Considerations

### 1. Authorization

All premium endpoints require:
- Valid JWT token
- Active premium subscription
- Rate limit checks

### 2. API Key Security

- API keys hashed before storage
- Rate limiting per key
- Automatic key rotation support

### 3. Webhook Security

- Stripe signature verification
- HTTPS-only webhook endpoints
- Webhook event logging

### 4. Data Privacy

- User data isolated by user_id
- Encrypted sensitive fields
- GDPR-compliant data retention

## Performance Optimizations

### 1. Caching

- Alert conditions cached (TTL: 5 minutes)
- Rate limits cached (TTL: 1 minute)
- Portfolio snapshots cached (TTL: 1 hour)

### 2. Database Indexes

- `alerts`: user_id, alert_type, status
- `subscriptions`: user_id, tier, status
- `usage_records`: user_id, usage_date, resource_type
- `portfolios`: politician_id, snapshot_date

### 3. Batch Processing

- Bulk alert matching for new trades
- Batch usage record insertion
- Aggregated usage queries

## Monitoring

### Metrics to Track

1. **Subscription Metrics**
   - Active subscriptions by tier
   - Churn rate
   - MRR (Monthly Recurring Revenue)

2. **Usage Metrics**
   - API calls per tier
   - Rate limit violations
   - Feature adoption rates

3. **Alert Metrics**
   - Alerts created/triggered
   - Notification delivery success rate
   - Alert response time

4. **Performance Metrics**
   - Alert matching latency
   - Portfolio calculation time
   - API response times

## Troubleshooting

### Common Issues

1. **Stripe webhook not working**
   - Check webhook secret in .env
   - Verify webhook endpoint is HTTPS
   - Check Stripe dashboard for failed events

2. **Rate limit not enforced**
   - Verify subscription exists for user
   - Check usage record creation
   - Verify rate limit middleware enabled

3. **Alerts not triggering**
   - Check alert status (must be ACTIVE)
   - Verify alert conditions match
   - Check notification service logs

## Future Enhancements

### Planned Features

1. **SMS Alerts**: Twilio integration for SMS notifications
2. **Push Notifications**: Mobile push notification support
3. **Advanced Reporting**: PDF report generation with charts
4. **API Analytics**: Detailed API usage analytics dashboard
5. **Team Accounts**: Multi-user enterprise accounts
6. **Custom Webhooks**: Webhook retry logic and management UI

## Support

For questions or issues:
- Documentation: `/api/v1/docs`
- GitHub Issues: [repository issues]
- Support Email: support@quantplatform.com

## License

Proprietary - All rights reserved
