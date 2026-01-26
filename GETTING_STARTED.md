# Getting Started Guide

**Welcome to the Quant Trading Platform!** 🚀

This guide will get you up and running in 10 minutes.

---

## 🎯 Quick Start (5 Minutes)

### Prerequisites
- Python 3.10+ installed
- Git installed
- 4GB RAM minimum

### 1. Clone and Setup

```bash
# Clone the repository
git clone <your-repo-url>
cd quant/quant/backend

# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Configure Environment

```bash
# Copy example environment file
cp .env.example .env

# Edit .env with your settings (or use defaults)
nano .env  # or vim, code, etc.
```

Minimum required settings:
```bash
# .env
ENVIRONMENT=development
DEBUG=true
SECRET_KEY=your-secret-key-here-change-this-in-production
DATABASE_URL=sqlite+aiosqlite:///./quant.db

# Optional: Add free API keys for more data sources
# ALPHA_VANTAGE_API_KEY=your_key_here
# FINNHUB_API_KEY=your_key_here
```

### 3. Initialize Database

```bash
# Run database migrations
alembic upgrade head

# Optional: Seed with sample data
python scripts/seed_data.py
```

### 4. Start the Server

```bash
# Start the backend
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Server will start at http://localhost:8000
```

### 5. Test It Works

Open your browser or use curl:

```bash
# Check health
curl http://localhost:8000/health

# Get platform stats
curl http://localhost:8000/api/v1/stats/overview

# Get a stock quote (free, no auth needed)
curl http://localhost:8000/api/v1/market-data/public/quote/AAPL

# View interactive API docs
open http://localhost:8000/api/v1/docs
```

**That's it! You're running!** ✅

---

## 📚 Next Steps

### 1. Create an Account

```bash
# Register a user
curl -X POST http://localhost:8000/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "your@email.com",
    "username": "yourname",
    "password": "SecurePassword123!"
  }'

# Login to get token
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "your@email.com",
    "password": "SecurePassword123!"
  }'

# Save the access_token from response
export TOKEN="your_access_token_here"
```

### 2. Explore the API

```bash
# Get authenticated stats
curl http://localhost:8000/api/v1/stats/leaderboard \
  -H "Authorization: Bearer $TOKEN"

# Get market data
curl http://localhost:8000/api/v1/market-data/quote/GOOGL \
  -H "Authorization: Bearer $TOKEN"

# Get historical data
curl "http://localhost:8000/api/v1/market-data/historical/AAPL?start_date=2026-01-01T00:00:00Z" \
  -H "Authorization: Bearer $TOKEN"
```

### 3. Add Discovery Integration (Optional)

If you have the discovery project running:

```bash
# Check discovery status
curl http://localhost:8000/api/v1/discovery/status

# Get ML predictions
curl http://localhost:8000/api/v1/discovery/predictions?limit=10
```

### 4. Read the Docs

- **API Documentation**: [API_DOCUMENTATION.md](API_DOCUMENTATION.md)
- **API Schemas**: [API_SCHEMAS.md](API_SCHEMAS.md)
- **Quick Start**: [API_QUICK_START.md](API_QUICK_START.md)
- **Free Data Sources**: [FREE_DATA_SOURCES_GUIDE.md](FREE_DATA_SOURCES_GUIDE.md)
- **Performance**: [PERFORMANCE_BENCHMARKS.md](PERFORMANCE_BENCHMARKS.md)

---

## 🧪 Run Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=app --cov-report=html

# View coverage report
open htmlcov/index.html

# Run specific test file
pytest tests/test_api/test_stats.py

# Run performance tests
pytest tests/performance/test_benchmarks.py --benchmark-only
```

---

## 🚀 Deploy to Production

See [WEEK_5_PLAN.md](WEEK_5_PLAN.md) for deployment options:

- **Railway** (Easiest): One-click deploy
- **Heroku** (Easy): Git push to deploy
- **DigitalOcean** (Simple): Managed services
- **AWS** (Scalable): Full control

Quick Railway deployment:
```bash
npm install -g @railway/cli
railway login
railway init
railway up
```

---

## 📊 Project Structure

```
quant/
├── backend/
│   ├── app/
│   │   ├── api/           # API endpoints
│   │   ├── core/          # Core functionality
│   │   ├── models/        # Database models
│   │   ├── services/      # Business logic
│   │   └── main.py        # FastAPI app
│   ├── tests/             # Test suite
│   ├── alembic/           # Database migrations
│   └── requirements.txt   # Dependencies
├── frontend/              # Frontend (if applicable)
├── docs/                  # Documentation
└── infrastructure/        # Deployment configs
```

---

## 🔑 Environment Variables

### Required
```bash
ENVIRONMENT=development|production|test
DEBUG=true|false
SECRET_KEY=your-secret-key
DATABASE_URL=your-database-url
```

### Optional - Free APIs
```bash
# Market Data (all free tiers)
ALPHA_VANTAGE_API_KEY=your_key
FINNHUB_API_KEY=your_key
POLYGON_API_KEY=your_key
IEX_API_KEY=your_key
```

### Optional - Features
```bash
# Email (for notifications)
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your@email.com
SMTP_PASSWORD=your_password

# Monitoring
SENTRY_DSN=your_sentry_dsn

# Redis (for production)
REDIS_URL=redis://localhost:6379/0
```

---

## 💡 Common Tasks

### Add a New Endpoint

1. Create endpoint in `app/api/v1/your_endpoint.py`
2. Add router to `app/api/v1/__init__.py`
3. Add tests in `tests/test_api/test_your_endpoint.py`
4. Update API documentation

### Add a Database Model

1. Create model in `app/models/your_model.py`
2. Create migration: `alembic revision --autogenerate -m "Add your_model"`
3. Review migration in `alembic/versions/`
4. Apply migration: `alembic upgrade head`

### Add a Service

1. Create service in `app/services/your_service.py`
2. Add business logic
3. Add tests in `tests/test_services/`
4. Use in endpoints via dependency injection

---

## 🐛 Troubleshooting

### Database Issues

```bash
# Reset database
rm quant.db
alembic upgrade head

# Check current version
alembic current

# View migration history
alembic history
```

### Port Already in Use

```bash
# Find process using port 8000
lsof -ti:8000

# Kill the process
kill -9 $(lsof -ti:8000)

# Or use different port
uvicorn app.main:app --port 8001
```

### Import Errors

```bash
# Make sure virtual environment is activated
source venv/bin/activate

# Reinstall dependencies
pip install -r requirements.txt

# Check Python path
echo $PYTHONPATH
```

### Module Not Found

```bash
# Add current directory to Python path
export PYTHONPATH="${PYTHONPATH}:$(pwd)"

# Or run from backend directory
cd quant/backend
python -m uvicorn app.main:app
```

---

## 🎓 Learning Resources

### API Development
- **FastAPI Docs**: https://fastapi.tiangolo.com
- **Pydantic**: https://pydantic-docs.helpmanual.io
- **SQLAlchemy**: https://docs.sqlalchemy.org

### Testing
- **pytest**: https://docs.pytest.org
- **pytest-asyncio**: https://pytest-asyncio.readthedocs.io
- **pytest-benchmark**: https://pytest-benchmark.readthedocs.io

### Deployment
- **Railway**: https://docs.railway.app
- **Heroku**: https://devcenter.heroku.com
- **DigitalOcean**: https://docs.digitalocean.com

---

## 📞 Getting Help

### Documentation
1. Check [API_DOCUMENTATION.md](API_DOCUMENTATION.md)
2. Check [FREE_DATA_SOURCES_GUIDE.md](FREE_DATA_SOURCES_GUIDE.md)
3. Check interactive docs at `/api/v1/docs`

### Common Questions
- **How do I get free data?** - See [FREE_DATA_SOURCES_GUIDE.md](FREE_DATA_SOURCES_GUIDE.md)
- **How do I deploy?** - See [WEEK_5_PLAN.md](WEEK_5_PLAN.md)
- **How do I add features?** - See example endpoints in `app/api/v1/`

### Issues
- Check existing issues on GitHub
- Create new issue with:
  - Environment details
  - Steps to reproduce
  - Expected vs actual behavior
  - Error messages/logs

---

## ✅ Checklist

### Initial Setup
- [ ] Python 3.10+ installed
- [ ] Repository cloned
- [ ] Virtual environment created
- [ ] Dependencies installed
- [ ] .env file configured
- [ ] Database initialized
- [ ] Server starts successfully

### First API Call
- [ ] Health check works
- [ ] Can get stock quote
- [ ] Can view API docs
- [ ] Can register user
- [ ] Can login and get token

### Ready for Development
- [ ] Tests run successfully
- [ ] Can create new endpoints
- [ ] Can modify database models
- [ ] Documentation reviewed
- [ ] Free data sources working

### Ready for Production
- [ ] All tests passing
- [ ] Security audit complete
- [ ] Performance tested
- [ ] Monitoring configured
- [ ] Deployment tested

---

## 🎉 You're Ready!

You now have:
- ✅ Platform running locally
- ✅ Free market data access
- ✅ ML predictions (if discovery is set up)
- ✅ Complete API documentation
- ✅ Test suite
- ✅ Production deployment plan

**Happy coding!** 🚀

---

## 📖 Quick Reference

```bash
# Start server
uvicorn app.main:app --reload

# Run tests
pytest

# Run tests with coverage
pytest --cov=app

# Run performance tests
pytest tests/performance/ --benchmark-only

# Database migration
alembic upgrade head

# Create new migration
alembic revision --autogenerate -m "Description"

# Interactive API docs
open http://localhost:8000/api/v1/docs

# Get stock quote
curl http://localhost:8000/api/v1/market-data/public/quote/AAPL
```

---

**Last Updated**: January 26, 2026
**Platform Version**: 1.0.0
**Status**: Production Ready ✅
