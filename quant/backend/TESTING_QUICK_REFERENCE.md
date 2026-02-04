# Testing Quick Reference Guide

## Quick Start

```bash
# Run ALL tests with coverage
cd /mnt/e/projects/quant/quant/backend
./run_comprehensive_tests.sh

# View HTML coverage report
open htmlcov/index.html  # macOS
xdg-open htmlcov/index.html  # Linux
```

## Test Suites

### 1. Unit Tests
```bash
# All unit tests
pytest tests/test_models/ tests/test_core/ tests/test_services/ -v

# Specific module
pytest tests/test_models/test_user.py -v

# With coverage
pytest tests/test_models/ --cov=app/models --cov-report=term-missing
```

### 2. API Tests
```bash
# All API tests
pytest tests/test_api/ -v

# Specific endpoint
pytest tests/test_api/test_auth.py::TestAuthEndpoints::test_login -v
```

### 3. Integration Tests
```bash
# All integration tests
pytest tests/test_integration/ -v

# Payment workflows
pytest tests/test_integration/test_payment_workflows.py -v

# Email workflows
pytest tests/test_integration/test_email_workflows.py -v

# Alert workflows
pytest tests/test_integration/test_alert_workflows.py -v
```

### 4. Security Tests
```bash
# All security tests
pytest tests/test_security/ tests/security/ -v

# Comprehensive security suite
pytest tests/security/test_comprehensive_security.py -v

# SQL injection tests
pytest tests/security/test_sql_injection.py -v

# XSS protection tests
pytest tests/security/test_xss_protection.py -v
```

### 5. Performance Tests
```bash
# Benchmarks
pytest tests/performance/test_benchmarks.py -v

# Load testing with Locust
locust -f tests/performance/locustfile.py --host=http://localhost:8000

# Load test scenarios:
# - Web UI: http://localhost:8089
# - 10 users: --users 10 --spawn-rate 2
# - 50 users: --users 50 --spawn-rate 5
# - 100 users: --users 100 --spawn-rate 10
# - 200 users: --users 200 --spawn-rate 20

# Headless load test (5 minutes)
locust -f tests/performance/locustfile.py --host=http://localhost:8000 \
    --users 100 --spawn-rate 10 --run-time 5m --headless
```

### 6. ML Tests
```bash
# All ML tests
pytest tests/test_ml/ tests/ml/ -v

# Cyclical analysis
pytest tests/ml/test_cyclical.py -v

# Ensemble models
pytest tests/test_ml/test_ensemble.py -v
```

## Coverage Analysis

```bash
# Generate coverage report
pytest --cov=app --cov-report=html --cov-report=term-missing

# View specific file coverage
coverage report app/models/user.py

# Check coverage threshold
coverage report --fail-under=95

# Run coverage analyzer
python3 tests/test_coverage_runner.py
```

## Test Markers

```bash
# Run only fast tests
pytest -m "not slow"

# Run only integration tests
pytest -m integration

# Run only unit tests
pytest -m unit

# Skip slow tests
pytest -m "not slow" -v
```

## Debugging Tests

```bash
# Show print statements
pytest -s

# Stop on first failure
pytest -x

# Show local variables on failure
pytest -l

# Enter debugger on failure
pytest --pdb

# Verbose output
pytest -vv

# Show test durations
pytest --durations=10
```

## Common Test Commands

```bash
# Run specific test
pytest tests/test_api/test_auth.py::test_login

# Run tests matching pattern
pytest -k "test_auth"

# Run with coverage for specific module
pytest tests/test_models/ --cov=app/models

# Parallel testing (faster)
pytest -n auto  # requires pytest-xdist

# Generate XML report for CI
pytest --junit-xml=test-results.xml
```

## Coverage Reports

### Terminal Report
```bash
coverage report
```

### HTML Report
```bash
coverage html
open htmlcov/index.html
```

### JSON Report
```bash
coverage json
cat coverage.json | jq '.totals'
```

### XML Report (for CI/CD)
```bash
coverage xml
```

## Test Fixtures

Common fixtures available in `tests/conftest.py`:

- `client`: FastAPI test client
- `test_db`: Database session
- `test_user`: Authenticated user
- `test_politician`: Sample politician
- `test_trade`: Sample trade
- `premium_user`: User with premium subscription
- `admin_user`: Admin user

Usage:
```python
async def test_example(client, test_user):
    # Use client and test_user fixtures
    pass
```

## Environment Variables

```bash
# Use test database
export DATABASE_URL="postgresql://user:pass@localhost/quant_test"

# Use test cache
export REDIS_URL="redis://localhost:6379/1"

# Disable external API calls
export TESTING=true
```

## CI/CD Integration

### GitHub Actions
```yaml
- name: Run Tests
  run: |
    cd quant/backend
    pytest --cov=app --cov-report=xml --cov-report=term

- name: Upload Coverage
  uses: codecov/codecov-action@v3
  with:
    file: ./coverage.xml
```

### GitLab CI
```yaml
test:
  script:
    - cd quant/backend
    - pytest --cov=app --cov-report=term --cov-report=xml
  coverage: '/TOTAL.*\s+(\d+%)$/'
```

## Load Testing Scenarios

### Quick Load Test
```bash
locust -f tests/performance/locustfile.py --host=http://localhost:8000 \
    --users 10 --spawn-rate 2 --run-time 1m --headless
```

### Sustained Load Test
```bash
locust -f tests/performance/locustfile.py --host=http://localhost:8000 \
    --users 100 --spawn-rate 10 --run-time 30m --headless
```

### Spike Test
```bash
locust -f tests/performance/locustfile.py --host=http://localhost:8000 \
    --users 200 --spawn-rate 50 --run-time 5m --headless
```

### Stress Test
```bash
locust -f tests/performance/locustfile.py --host=http://localhost:8000 \
    --users 500 --spawn-rate 50 --run-time 10m --headless
```

## Troubleshooting

### Tests Hanging
```bash
# Add timeout
pytest --timeout=300

# Show which test is running
pytest -v --capture=no
```

### Database Issues
```bash
# Reset test database
dropdb quant_test
createdb quant_test
alembic upgrade head
```

### Import Errors
```bash
# Ensure backend is on PYTHONPATH
export PYTHONPATH=/mnt/e/projects/quant/quant/backend:$PYTHONPATH
```

### Coverage Not Updating
```bash
# Clean coverage data
coverage erase
rm -f .coverage coverage.json
rm -rf htmlcov/

# Run tests again
pytest --cov=app
```

## Best Practices

1. **Always run tests before committing**
2. **Maintain coverage above 95%**
3. **Test edge cases and error conditions**
4. **Use fixtures for common setup**
5. **Mock external services**
6. **Keep tests isolated and independent**
7. **Run security tests regularly**
8. **Perform load testing before releases**
9. **Review coverage reports weekly**
10. **Update tests when code changes**

## Quick Checklist

Before pushing code:
- [ ] All tests pass: `./run_comprehensive_tests.sh`
- [ ] Coverage >= 95%: Check HTML report
- [ ] Security tests pass: `pytest tests/test_security/`
- [ ] No new warnings: `pytest --strict-warnings`
- [ ] Load tests successful (if major changes)

## Resources

- HTML Coverage: `htmlcov/index.html`
- JSON Coverage: `coverage.json`
- Test Results: `test-results.xml`
- Locust Report: `http://localhost:8089`

## Support

For issues or questions:
1. Check test output for error messages
2. Review HTML coverage report for untested code
3. Run individual test with `-vv` for details
4. Use `--pdb` to debug failures
5. Check fixture setup in `tests/conftest.py`
