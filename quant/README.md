# Quant Analytics Platform

> Track government stock trades with statistical rigor

A modern, full-stack platform for tracking and analyzing Congressional stock trades using institutional-grade quantitative methods.

## 🚀 Quick Start

### Prerequisites

- **Node.js** 18+ and npm
- **Python** 3.11+
- **Docker** and Docker Compose
- **Git**

### Local Development Setup

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd quant
   ```

2. **Set up environment variables**
   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```

3. **Start the infrastructure (Docker)**
   ```bash
   npm run docker:up
   ```

   This starts:
   - PostgreSQL with TimescaleDB (port 5432)
   - Redis (port 6379)
   - Backend API (port 8000)
   - Celery worker

4. **Install frontend dependencies**
   ```bash
   cd frontend
   npm install
   cd ..
   ```

5. **Install backend dependencies**
   ```bash
   cd backend
   pip install -r requirements.txt
   cd ..
   ```

6. **Run database migrations**
   ```bash
   cd backend
   alembic upgrade head
   cd ..
   ```

7. **Start development servers**
   ```bash
   npm run dev
   ```

   This starts:
   - Frontend: http://localhost:3000
   - Backend API: http://localhost:8000
   - API Docs: http://localhost:8000/api/v1/docs

## 📁 Project Structure

```
quant/
├── frontend/                 # Next.js 14 frontend
│   ├── src/
│   │   ├── app/             # Next.js App Router pages
│   │   ├── components/      # React components
│   │   ├── lib/             # Utilities and API client
│   │   └── types/           # TypeScript types
│   ├── public/              # Static assets
│   └── package.json
│
├── backend/                 # FastAPI backend
│   ├── app/
│   │   ├── api/v1/         # API endpoints
│   │   ├── core/           # Config, database
│   │   ├── models/         # SQLAlchemy models
│   │   ├── schemas/        # Pydantic schemas
│   │   ├── scrapers/       # Web scrapers
│   │   ├── tasks/          # Celery tasks
│   │   └── utils/          # Utilities
│   ├── alembic/            # Database migrations
│   ├── tests/              # Tests
│   ├── Dockerfile
│   └── requirements.txt
│
├── infrastructure/
│   └── docker/
│       ├── docker-compose.yml
│       └── init-db.sql
│
├── docs/                    # Documentation (from planning)
├── .env.example
├── .gitignore
├── package.json
└── README.md
```

## 🛠️ Technology Stack

### Frontend
- **Framework:** Next.js 14 (App Router)
- **Language:** TypeScript
- **Styling:** Tailwind CSS
- **State Management:** Zustand + React Query
- **Charts:** Recharts
- **Authentication:** Supabase Auth

### Backend
- **Framework:** FastAPI
- **Language:** Python 3.11
- **ORM:** SQLAlchemy 2.0
- **Validation:** Pydantic V2
- **Task Queue:** Celery
- **Caching:** Redis

### Database
- **Primary:** PostgreSQL 15
- **Extension:** TimescaleDB (time-series optimization)
- **Migrations:** Alembic

### Infrastructure
- **Containerization:** Docker + Docker Compose
- **Frontend Hosting:** Vercel
- **Backend Hosting:** Railway
- **Database Hosting:** Supabase

## 📦 Available Scripts

### Root Level
```bash
npm run dev              # Start both frontend and backend
npm run docker:up        # Start Docker services
npm run docker:down      # Stop Docker services
npm run docker:logs      # View Docker logs
npm run test             # Run all tests
npm run lint             # Run linting
npm run format           # Format code
```

### Frontend
```bash
cd frontend
npm run dev              # Start Next.js dev server
npm run build            # Build for production
npm run start            # Start production server
npm run lint             # Run ESLint
npm run type-check       # TypeScript type checking
```

### Backend
```bash
cd backend
uvicorn app.main:app --reload    # Start FastAPI dev server
pytest                           # Run tests
black app/                       # Format code
ruff check app/                  # Lint code
alembic revision --autogenerate  # Create migration
alembic upgrade head             # Run migrations
```

## 🗃️ Database Schema

### Politicians
- `id` (UUID, PK)
- `name` (VARCHAR)
- `chamber` (VARCHAR) - 'senate' or 'house'
- `party` (VARCHAR)
- `state` (VARCHAR)
- `bioguide_id` (VARCHAR, unique)
- `created_at`, `updated_at` (TIMESTAMP)

### Trades (TimescaleDB Hypertable)
- `id` (UUID, PK)
- `politician_id` (UUID, FK)
- `ticker` (VARCHAR)
- `transaction_type` (VARCHAR) - 'buy' or 'sell'
- `amount_min`, `amount_max` (DECIMAL)
- `transaction_date` (DATE) - partition key for TimescaleDB
- `disclosure_date` (DATE)
- `source_url` (TEXT)
- `raw_data` (JSONB)
- `created_at` (TIMESTAMP)

### Tickers
- `symbol` (VARCHAR, PK)
- `company_name` (VARCHAR)
- `sector`, `industry` (VARCHAR)
- `last_updated` (TIMESTAMP)

## 🔌 API Endpoints

Base URL: `http://localhost:8000/api/v1`

### Trades
- `GET /trades/` - List all trades
- `GET /trades/{id}` - Get trade details
- `GET /trades/recent` - Get recent trades

### Politicians
- `GET /politicians/` - List all politicians
- `GET /politicians/{id}` - Get politician details

### Stats
- `GET /stats/leaderboard` - Get performance leaderboard
- `GET /stats/sectors` - Get sector statistics

### Documentation
- `GET /api/v1/docs` - Swagger UI
- `GET /api/v1/redoc` - ReDoc

## 🧪 Testing

### Backend Tests
```bash
cd backend
pytest                      # Run all tests
pytest -v                   # Verbose output
pytest --cov=app           # With coverage report
pytest tests/test_api/     # Specific test directory
```

### Frontend Tests
```bash
cd frontend
npm test                   # Run tests
npm test -- --coverage    # With coverage
```

## 🚢 Deployment

### Frontend (Vercel)
1. Connect GitHub repository to Vercel
2. Set environment variables
3. Deploy automatically on push to main

### Backend (Railway)
1. Connect GitHub repository to Railway
2. Set environment variables
3. Deploy automatically on push to main

### Database (Supabase)
1. Create new Supabase project
2. Enable TimescaleDB extension
3. Update connection string in environment

## 📊 Development Workflow

1. **Create a new feature branch**
   ```bash
   git checkout -b feature/your-feature
   ```

2. **Make changes and test locally**
   ```bash
   npm run dev
   npm run test
   ```

3. **Create database migration if needed**
   ```bash
   cd backend
   alembic revision --autogenerate -m "description"
   alembic upgrade head
   ```

4. **Commit and push**
   ```bash
   git add .
   git commit -m "feat: your feature description"
   git push origin feature/your-feature
   ```

5. **Create pull request**
   - CI/CD will run tests automatically
   - Deploy to staging for review

## 🐛 Troubleshooting

### Docker Issues
```bash
# Reset everything
npm run docker:down
docker volume prune
npm run docker:up
```

### Database Connection Issues
```bash
# Check if PostgreSQL is running
docker ps | grep postgres

# Connect to database
docker exec -it quant-postgres psql -U quant_user -d quant_db
```

### Frontend Build Issues
```bash
cd frontend
rm -rf .next node_modules
npm install
npm run dev
```

### Backend Issues
```bash
cd backend
# Check if all dependencies are installed
pip install -r requirements.txt

# Check database connection
python -c "from app.core.database import engine; print('OK')"
```

## 📚 Documentation

- [Production Guide](../PRODUCTION_GUIDE_V2.md) - Comprehensive implementation plan
- [Technical Architecture](../TECHNICAL_ARCHITECTURE.md) - Detailed system design
- [Production Plan](../PRODUCTION_PLAN.md) - Current execution strategy
- [API Documentation](http://localhost:8000/api/v1/docs) - Interactive API docs (when running)

## 🎯 Next Steps

**Phase 0 - Foundation** (CURRENT):
- [x] Project structure setup
- [x] Frontend initialized (Next.js)
- [x] Backend initialized (FastAPI)
- [x] Docker Compose configuration
- [x] Database models created
- [x] Alembic migrations setup
- [ ] Run initial migration
- [ ] Test full stack integration
- [ ] Deploy to staging

**Phase 1 - Core Data Pipeline** (NEXT):
- [ ] Build Senate scraper
- [ ] Build House scraper
- [ ] Implement data validation
- [ ] Set up Celery tasks
- [ ] Integrate market data API

## 📝 License

Proprietary - All rights reserved

## 👥 Team

- Solo developer using Claude Code

---

**Status:** Phase 0 - Foundation (Week 1, Day 1 Complete)

Last Updated: 2025-11-10
