# QuantEngines Backend API

FastAPI backend for the QuantEngines Congressional Trading Analytics Platform.

For complete project documentation, see the [main README](../../README.md).

---

## Quick Start

```bash
# Setup environment
cp .env.example .env
# Edit .env with your configuration

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run migrations
alembic upgrade head

# Start development server
uvicorn app.main:app --reload
```

API will be available at http://localhost:8000

**Interactive docs**: http://localhost:8000/docs

---

## Project Structure

```
backend/
├── app/
│   ├── api/          # API endpoints
│   ├── core/         # Core configuration
│   ├── models/       # Database models
│   ├── schemas/      # Pydantic schemas
│   ├── services/     # Business logic
│   ├── tasks/        # Celery tasks
│   └── main.py       # FastAPI app
├── tests/            # Test suite
├── alembic/          # Database migrations
├── requirements.txt  # Dependencies
└── .env.example      # Environment template
```

---

## Environment Variables

See `.env.example` for complete configuration options.

**Required**:
- `DATABASE_URL` - PostgreSQL or SQLite connection
- `SECRET_KEY` - App secret (32+ chars)
- `JWT_SECRET_KEY` - JWT secret (32+ chars)
- `REDIS_URL` - Redis connection for caching

**Optional**:
- Stock data: `POLYGON_API_KEY`, `ALPHA_VANTAGE_API_KEY`
- Email: `RESEND_API_KEY`
- Payments: `STRIPE_SECRET_KEY`
- Monitoring: `SENTRY_DSN`

---

## Running Services

```bash
# Backend API
uvicorn app.main:app --reload

# Redis (required for caching)
redis-server

# Celery worker (for data scraping)
celery -A app.tasks.scraping_tasks worker -l info

# Celery beat (scheduler)
celery -A app.tasks.scraping_tasks beat -l info
```

---

## Testing

```bash
# Run all tests
./run_comprehensive_tests.sh

# Specific test categories
pytest tests/test_api/ -v
pytest tests/test_integration/ -v
pytest tests/test_security/ -v

# With coverage
pytest --cov=app --cov-report=html
```

---

## Database Migrations

```bash
# Create migration
alembic revision --autogenerate -m "description"

# Apply migrations
alembic upgrade head

# Rollback
alembic downgrade -1

# View history
alembic history
```

---

## API Endpoints

### Authentication
- `POST /api/v1/auth/register` - Register user
- `POST /api/v1/auth/login` - Login user
- `POST /api/v1/auth/refresh` - Refresh token

### Politicians
- `GET /api/v1/politicians` - List politicians
- `GET /api/v1/politicians/{id}` - Get details
- `GET /api/v1/politicians/{id}/trades` - Get trades

### Trades
- `GET /api/v1/trades` - List trades
- `GET /api/v1/trades/{id}` - Get trade details

### Analytics
- `GET /api/v1/analytics/predictions` - ML predictions
- `GET /api/v1/analytics/discoveries` - Pattern discoveries
- `POST /api/v1/analytics/options/gamma-exposure` - Options GEX
- `GET /api/v1/analytics/sentiment/politician/{id}` - Sentiment

### Premium
- `POST /api/v1/alerts` - Create alert
- `GET /api/v1/portfolios` - List portfolios
- `GET /api/v1/subscriptions/current` - Subscription status

See http://localhost:8000/docs for complete API documentation.

---

## Development

### Code Style
- Follow PEP 8
- Use type hints
- Add docstrings for public APIs
- Write tests for new features

### Pre-commit Checks
```bash
# Format code
black app/ tests/

# Type checking
mypy app/

# Linting
flake8 app/ tests/

# Security check
bandit -r app/
```

---

## Deployment

See the main [DEPLOYMENT_GUIDE.md](../../DEPLOYMENT_GUIDE.md) for production deployment instructions.

**Quick deploy**:
```bash
./scripts/quick_deploy.sh
```

**Recommended hosting**:
- Railway ($5-20/month)
- AWS ECS
- Google Cloud Run

---

## Documentation

- [Main README](../../README.md) - Project overview
- [.env.example](.env.example) - Configuration reference
- [PRODUCTION_CHECKLIST.md](../../PRODUCTION_CHECKLIST.md) - Deployment checklist
- [API Docs](http://localhost:8000/docs) - Interactive API documentation

---

## Support

- **Issues**: https://github.com/yourusername/quant/issues
- **Email**: info@yourdomain.com

---

**Version**: 1.0.0
**Status**: Production Ready
**License**: MIT
