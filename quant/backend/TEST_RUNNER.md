# Backend Testing Guide

## Overview

This guide covers running the test suite for the hybrid revenue model subscription system.

## Test Files

### 1. `tests/test_subscription_system.py`
Unit tests for subscription management:
- Tier configuration validation
- Subscription creation and lifecycle
- Trial period functionality
- Referral system
- Hybrid model fields
- Integration flows

### 2. `tests/test_stripe_webhooks.py`
Tests for Stripe webhook handling:
- Event structure validation
- Event processing
- Security and validation
- Error handling
- Full subscription lifecycle

### 3. `tests/test_subscription_api.py`
API endpoint integration tests:
- GET /subscription/tiers
- GET /subscription/status
- POST /subscription/upgrade
- POST /subscription/downgrade
- GET /subscription/referral/code
- POST /subscription/referral/track

## Setup

### Prerequisites
```bash
pip install pytest pytest-asyncio
```

### Database
Tests use in-memory SQLite database for isolation.

## Running Tests

### Run All Tests
```bash
pytest tests/ -v
```

### Run Specific Test File
```bash
pytest tests/test_subscription_system.py -v
```

### Run Specific Test Class
```bash
pytest tests/test_subscription_system.py::TestSubscriptionTiers -v
```

### Run Specific Test
```bash
pytest tests/test_subscription_system.py::TestSubscriptionTiers::test_tier_config_exists -v
```

### Run with Coverage
```bash
pip install pytest-cov
pytest tests/ --cov=app --cov-report=html
```

## Test Categories

### Unit Tests
Test individual components in isolation:
```bash
pytest tests/test_subscription_system.py -v
```

### Webhook Tests
Test Stripe event handling:
```bash
pytest tests/test_stripe_webhooks.py -v
```

### API Tests
Test REST endpoints:
```bash
pytest tests/test_subscription_api.py -v
```

## Test Scenarios

### Subscription Lifecycle

#### Free → Starter Upgrade
1. User on free tier with ads
2. Clicks upgrade button
3. Redirected to Stripe checkout
4. Completes payment
5. Webhook updates user.subscription_tier = "starter"
6. Ads disabled (ad_free = true)

**Test Command:**
```bash
pytest tests/test_subscription_system.py::TestSubscriptionIntegration::test_full_upgrade_flow -v
```

#### Trial Period
1. User starts 7-day trial
2. User has access to premium features
3. Trial countdown shown on dashboard
4. Day 7: Trial expires
5. User downgraded to free
6. Trial can only be used once

**Test Command:**
```bash
pytest tests/test_subscription_system.py::TestTrialPeriod -v
```

#### Referral System
1. User A gets referral code
2. User A shares code with User B
3. User B signs up with code
4. User B verified email
5. User A receives $10 credit
6. User B sees referred_by_user_id = User A

**Test Command:**
```bash
pytest tests/test_subscription_system.py::TestReferralSystem -v
```

#### Webhook Processing
1. Stripe sends subscription.created event
2. Webhook verified and authenticated
3. Database updated with subscription
4. User tier updated
5. Confirmation logged

**Test Command:**
```bash
pytest tests/test_stripe_webhooks.py::TestWebhookProcessing -v
```

## Manual Testing Checklist

### Subscription Flow
- [ ] Visit /pricing page
- [ ] See 3 subscription tiers with prices
- [ ] Billing toggle shows monthly/annual
- [ ] Click "Upgrade to Starter"
- [ ] Redirected to Stripe Checkout
- [ ] Complete test payment (4242 4242 4242 4242)
- [ ] Webhook received and processed
- [ ] User tier updated to "starter"
- [ ] Ad banner hidden (ad_free = true)

### Referral System
- [ ] Visit /dashboard/referral
- [ ] See referral code
- [ ] Copy code button works
- [ ] Share button works
- [ ] Credit balance displays correctly
- [ ] Create test referral
- [ ] Verify $10 credit awarded

### Trial Period
- [ ] Click "Start Free Trial" button
- [ ] trial_starts_at and trial_ends_at set
- [ ] Premium features accessible
- [ ] Countdown timer shows on dashboard
- [ ] After 7 days: Downgraded to free
- [ ] Ads return

## Debugging Tests

### Verbose Output
```bash
pytest tests/ -vv -s
```

### Stop on First Failure
```bash
pytest tests/ -x
```

### Show Local Variables on Failure
```bash
pytest tests/ -l
```

### Enable Logging
```bash
pytest tests/ --log-cli-level=DEBUG
```

## Coverage Goals

Aim for >80% code coverage:
```bash
pytest tests/ --cov=app --cov-report=term-missing
```

Target coverage by module:
- `app/models/subscription.py` - 95%+
- `app/services/subscription_service.py` - 90%+
- `app/api/v1/subscription.py` - 85%+
- `app/api/v1/subscriptions.py` - 85%+

## CI/CD Integration

### GitHub Actions Example
```yaml
name: Run Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - uses: actions/setup-python@v2
        with:
          python-version: 3.11
      - run: pip install -r requirements.txt
      - run: pytest tests/ -v --cov=app
```

## Troubleshooting

### Test Hangs
- Check for infinite loops in async code
- Verify database connections close properly
- Use `-x` flag to stop at first failure

### Import Errors
- Ensure backend is in PYTHONPATH
- Run from project root: `pytest tests/`
- Check `__init__.py` files exist

### Database Errors
- Tests use in-memory SQLite
- No need for external database
- Each test gets fresh database

### Async Issues
- Use `@pytest.mark.asyncio` decorator
- Ensure `pytest-asyncio` installed
- Use `async with` for context managers

## Performance Testing

### Load Testing Subscription Endpoints
```bash
# Install locust
pip install locust

# Create locustfile.py and run
locust -f locustfile.py --host=http://localhost:8000
```

### Stress Testing Webhook Processing
```bash
# Send 100 webhook events in sequence
for i in {1..100}; do
    curl -X POST http://localhost:8000/api/v1/subscriptions/webhooks/stripe \
      -H "Content-Type: application/json" \
      -d @webhook_event.json
done
```

## Reports

### Generate HTML Coverage Report
```bash
pytest tests/ --cov=app --cov-report=html
open htmlcov/index.html
```

### Generate JUnit XML Report
```bash
pytest tests/ --junitxml=report.xml
```

## Next Steps

1. **Run All Tests**
   ```bash
   pytest tests/ -v
   ```

2. **Fix Any Failing Tests**
   - Check error message
   - Review test code
   - Update implementation if needed

3. **Achieve Coverage Target**
   ```bash
   pytest tests/ --cov=app --cov-report=term-missing
   ```

4. **Integrate with CI/CD**
   - Add GitHub Actions workflow
   - Run tests on every push

5. **Monitor Test Health**
   - Weekly test runs
   - Track flaky tests
   - Update tests as code changes
