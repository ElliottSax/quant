# Technical Architecture
## Quant Analytics Platform - Detailed System Design

---

## Table of Contents

1. [System Overview](#system-overview)
2. [Frontend Architecture](#frontend-architecture)
3. [Backend Architecture](#backend-architecture)
4. [Database Design](#database-design)
5. [Data Pipeline](#data-pipeline)
6. [Caching Strategy](#caching-strategy)
7. [Authentication & Authorization](#authentication--authorization)
8. [API Design](#api-design)
9. [Deployment Architecture](#deployment-architecture)
10. [Monitoring & Observability](#monitoring--observability)
11. [Security](#security)
12. [Performance](#performance)
13. [Disaster Recovery](#disaster-recovery)

---

## System Overview

### High-Level Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                         User Layer                               │
│  Browser, Mobile Browser, API Clients                            │
└────────────────────────┬────────────────────────────────────────┘
                         │
┌────────────────────────▼────────────────────────────────────────┐
│                    CDN + WAF Layer                               │
│  Cloudflare (DDoS protection, SSL, caching, rate limiting)      │
└────────────────────────┬────────────────────────────────────────┘
                         │
        ┌────────────────┴────────────────┐
        │                                 │
┌───────▼───────────┐          ┌──────────▼────────────┐
│  Frontend (SSR)   │          │   Backend API         │
│  Next.js @ Vercel │          │   FastAPI @ Railway   │
│  - React 18       │◄────────►│   - Python 3.11       │
│  - TypeScript     │   API    │   - Async/await       │
│  - Tailwind CSS   │  Calls   │   - Pydantic V2       │
└────────┬──────────┘          └──────────┬────────────┘
         │                                 │
         │            ┌────────────────────┼──────────────┐
         │            │                    │              │
┌────────▼──────┐  ┌──▼─────────┐  ┌──────▼───────┐  ┌──▼──────┐
│  Supabase     │  │PostgreSQL  │  │    Redis     │  │ Celery  │
│  Auth         │  │TimescaleDB │  │    Cache     │  │ Workers │
└───────────────┘  └────────────┘  └──────────────┘  └──┬──────┘
                                                         │
                   ┌─────────────────────────────────────┘
                   │
        ┌──────────▼───────────┬─────────────────┐
        │                      │                 │
┌───────▼────────┐  ┌──────────▼──────┐  ┌──────▼────────┐
│  Web Scrapers  │  │  Market Data    │  │   Backups     │
│  - Senate      │  │  - yfinance     │  │  - Daily      │
│  - House       │  │  - Polygon.io   │  │  - S3/Supabase│
└────────────────┘  └─────────────────┘  └───────────────┘
```

### Technology Stack

**Frontend:**
- Next.js 14+ (App Router, React Server Components)
- TypeScript 5+
- Tailwind CSS 3+
- shadcn/ui components
- React Query (data fetching, caching)
- Zustand (client state management)
- Recharts (data visualization)

**Backend:**
- FastAPI (Python 3.11+)
- SQLAlchemy 2.0 (ORM)
- Pydantic V2 (validation)
- Alembic (migrations)
- Celery (task queue)
- Redis (caching, message broker)

**Database:**
- PostgreSQL 15+
- TimescaleDB extension
- Full-text search
- JSONB for flexible data

**Infrastructure:**
- Vercel (frontend hosting)
- Railway (backend hosting)
- Supabase (database, auth, storage)
- Cloudflare (CDN, DNS, WAF)
- GitHub Actions (CI/CD)

---

## Frontend Architecture

### Directory Structure

```
frontend/
├── src/
│   ├── app/                          # Next.js App Router
│   │   ├── (marketing)/             # Public pages group
│   │   │   ├── page.tsx             # Homepage
│   │   │   ├── layout.tsx           # Marketing layout
│   │   │   ├── politicians/
│   │   │   │   ├── page.tsx         # Politician directory
│   │   │   │   └── [id]/
│   │   │   │       └── page.tsx     # Politician detail
│   │   │   ├── trades/
│   │   │   │   └── [id]/
│   │   │   │       └── page.tsx     # Trade detail
│   │   │   ├── leaderboard/
│   │   │   │   └── page.tsx
│   │   │   ├── about/
│   │   │   │   └── page.tsx
│   │   │   ├── methodology/
│   │   │   │   └── page.tsx
│   │   │   └── pricing/
│   │   │       └── page.tsx
│   │   ├── (app)/                   # Protected pages group
│   │   │   ├── dashboard/
│   │   │   │   └── page.tsx
│   │   │   ├── settings/
│   │   │   │   └── page.tsx
│   │   │   └── api-keys/
│   │   │       └── page.tsx
│   │   ├── api/                     # API routes
│   │   │   ├── auth/
│   │   │   ├── stripe/
│   │   │   └── subscribe/
│   │   ├── layout.tsx               # Root layout
│   │   ├── globals.css
│   │   └── error.tsx
│   ├── components/
│   │   ├── ui/                      # shadcn/ui components
│   │   │   ├── button.tsx
│   │   │   ├── card.tsx
│   │   │   ├── table.tsx
│   │   │   ├── dialog.tsx
│   │   │   └── ...
│   │   ├── layout/                  # Layout components
│   │   │   ├── header.tsx
│   │   │   ├── footer.tsx
│   │   │   ├── navigation.tsx
│   │   │   └── container.tsx
│   │   ├── trades/                  # Trade components
│   │   │   ├── trade-card.tsx
│   │   │   ├── trade-list.tsx
│   │   │   ├── trade-feed.tsx
│   │   │   └── trade-filters.tsx
│   │   ├── politicians/             # Politician components
│   │   │   ├── politician-card.tsx
│   │   │   ├── politician-list.tsx
│   │   │   └── performance-widget.tsx
│   │   ├── charts/                  # Chart components
│   │   │   ├── performance-chart.tsx
│   │   │   ├── sector-chart.tsx
│   │   │   └── timeline-chart.tsx
│   │   └── stats/                   # Stats components
│   │       ├── leaderboard.tsx
│   │       └── stats-card.tsx
│   ├── lib/
│   │   ├── api-client.ts           # API client setup
│   │   ├── supabase.ts             # Supabase client
│   │   ├── utils.ts                # Utility functions
│   │   └── constants.ts
│   ├── hooks/
│   │   ├── use-trades.ts           # React Query hooks
│   │   ├── use-politicians.ts
│   │   ├── use-auth.ts
│   │   └── use-subscription.ts
│   ├── types/
│   │   ├── trade.ts
│   │   ├── politician.ts
│   │   ├── user.ts
│   │   └── api.ts
│   └── store/
│       ├── auth-store.ts           # Zustand stores
│       ├── filter-store.ts
│       └── ui-store.ts
├── public/
│   ├── images/
│   ├── icons/
│   └── fonts/
├── tests/
│   ├── unit/
│   ├── integration/
│   └── e2e/
├── package.json
├── tsconfig.json
├── tailwind.config.js
├── next.config.js
└── .env.local
```

### Data Fetching Strategy

**Server Components (Default):**
```typescript
// app/(marketing)/politicians/page.tsx
import { api } from '@/lib/api-client'

export default async function PoliticiansPage() {
  // Fetched on server, cached by Next.js
  const politicians = await api.politicians.list()

  return <PoliticianList politicians={politicians} />
}
```

**Client Components (Interactive):**
```typescript
// components/trades/trade-feed.tsx
'use client'

import { useQuery } from '@tanstack/react-query'
import { api } from '@/lib/api-client'

export function TradeFeed() {
  const { data, isLoading } = useQuery({
    queryKey: ['trades', 'recent'],
    queryFn: () => api.trades.recent(),
    refetchInterval: 60000, // Refetch every minute
  })

  if (isLoading) return <Skeleton />
  return <TradeList trades={data} />
}
```

### State Management

**Server State (React Query):**
- API data
- Cached queries
- Automatic refetching
- Optimistic updates

**Client State (Zustand):**
- UI state (modals, sidebars)
- Filter state
- User preferences
- Theme (dark mode)

```typescript
// store/filter-store.ts
import { create } from 'zustand'
import { persist } from 'zustand/middleware'

interface FilterState {
  chamber: string | null
  party: string | null
  dateRange: [Date, Date] | null
  setFilter: (key: string, value: any) => void
  resetFilters: () => void
}

export const useFilterStore = create<FilterState>()(
  persist(
    (set) => ({
      chamber: null,
      party: null,
      dateRange: null,
      setFilter: (key, value) => set({ [key]: value }),
      resetFilters: () => set({ chamber: null, party: null, dateRange: null }),
    }),
    {
      name: 'filter-storage',
    }
  )
)
```

### Performance Optimizations

**Code Splitting:**
```typescript
// Dynamic imports for large components
import dynamic from 'next/dynamic'

const PerformanceChart = dynamic(
  () => import('@/components/charts/performance-chart'),
  { loading: () => <ChartSkeleton /> }
)
```

**Image Optimization:**
```typescript
import Image from 'next/image'

<Image
  src="/politician.jpg"
  alt="Politician"
  width={200}
  height={200}
  loading="lazy"
  placeholder="blur"
/>
```

**Streaming:**
```typescript
// app/(marketing)/politicians/[id]/page.tsx
import { Suspense } from 'react'

export default function PoliticianPage({ params }) {
  return (
    <>
      <PoliticianHeader id={params.id} />
      <Suspense fallback={<ChartSkeleton />}>
        <PerformanceChart id={params.id} />
      </Suspense>
      <Suspense fallback={<TableSkeleton />}>
        <TradeHistory id={params.id} />
      </Suspense>
    </>
  )
}
```

---

## Backend Architecture

### Directory Structure

```
backend/
├── app/
│   ├── main.py                      # FastAPI app entry
│   ├── api/
│   │   └── v1/
│   │       ├── __init__.py
│   │       ├── router.py           # Main API router
│   │       └── routes/
│   │           ├── trades.py       # Trade endpoints
│   │           ├── politicians.py  # Politician endpoints
│   │           ├── stats.py        # Statistics endpoints
│   │           ├── users.py        # User endpoints
│   │           └── health.py       # Health check
│   ├── core/
│   │   ├── config.py               # Settings (Pydantic)
│   │   ├── database.py             # DB connection
│   │   ├── security.py             # Auth utilities
│   │   ├── cache.py                # Redis cache
│   │   └── celery_app.py           # Celery setup
│   ├── models/
│   │   ├── base.py                 # Base model
│   │   ├── politician.py           # Politician model
│   │   ├── trade.py                # Trade model
│   │   ├── user.py                 # User model
│   │   └── subscription.py         # Subscription model
│   ├── schemas/
│   │   ├── trade.py                # Pydantic schemas
│   │   ├── politician.py
│   │   ├── user.py
│   │   └── stats.py
│   ├── services/
│   │   ├── trade_service.py        # Business logic
│   │   ├── politician_service.py
│   │   ├── performance_service.py
│   │   ├── statistics_service.py
│   │   ├── market_data_service.py
│   │   └── notification_service.py
│   ├── scrapers/
│   │   ├── base.py                 # Base scraper
│   │   ├── senate_scraper.py       # Senate scraper
│   │   ├── house_scraper.py        # House scraper
│   │   └── validators.py           # Data validation
│   ├── tasks/
│   │   ├── scraping.py             # Celery scraping tasks
│   │   ├── processing.py           # Data processing tasks
│   │   └── notifications.py        # Email tasks
│   ├── middleware/
│   │   ├── auth.py                 # Auth middleware
│   │   ├── rate_limit.py           # Rate limiting
│   │   └── logging.py              # Request logging
│   └── utils/
│       ├── datetime.py
│       ├── formatting.py
│       └── validators.py
├── tests/
│   ├── unit/
│   ├── integration/
│   └── conftest.py
├── alembic/
│   ├── versions/
│   └── env.py
├── requirements.txt
├── Dockerfile
├── docker-compose.yml
└── .env
```

### FastAPI Application Setup

```python
# app/main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from app.api.v1.router import api_router
from app.core.config import settings
from app.middleware import auth, rate_limit, logging
import sentry_sdk

# Initialize Sentry
sentry_sdk.init(dsn=settings.SENTRY_DSN)

app = FastAPI(
    title="Quant Analytics API",
    description="Government trade tracking API",
    version="1.0.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc",
)

# Middleware
app.add_middleware(GZipMiddleware, minimum_size=1000)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.add_middleware(rate_limit.RateLimitMiddleware)
app.add_middleware(logging.RequestLoggingMiddleware)

# Routers
app.include_router(api_router, prefix="/api/v1")

@app.get("/health")
async def health_check():
    return {"status": "healthy"}
```

### Configuration Management

```python
# app/core/config.py
from pydantic_settings import BaseSettings
from typing import List

class Settings(BaseSettings):
    # App
    APP_NAME: str = "Quant Analytics"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = False

    # Database
    DATABASE_URL: str
    DB_POOL_SIZE: int = 20
    DB_MAX_OVERFLOW: int = 10

    # Redis
    REDIS_URL: str

    # Supabase
    SUPABASE_URL: str
    SUPABASE_KEY: str

    # Security
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    # CORS
    ALLOWED_ORIGINS: List[str] = ["http://localhost:3000"]

    # External APIs
    POLYGON_API_KEY: str | None = None
    RESEND_API_KEY: str | None = None

    # Monitoring
    SENTRY_DSN: str | None = None
    POSTHOG_API_KEY: str | None = None

    # Celery
    CELERY_BROKER_URL: str
    CELERY_RESULT_BACKEND: str

    class Config:
        env_file = ".env"
        case_sensitive = True

settings = Settings()
```

### Database Connection

```python
# app/core/database.py
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from app.core.config import settings

engine = create_engine(
    settings.DATABASE_URL,
    pool_size=settings.DB_POOL_SIZE,
    max_overflow=settings.DB_MAX_OVERFLOW,
    pool_pre_ping=True,  # Verify connections
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

def get_db():
    """Dependency for database session"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
```

---

## Database Design

### Schema

```sql
-- Enable extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "timescaledb";

-- Politicians table
CREATE TABLE politicians (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name VARCHAR(255) NOT NULL,
    chamber VARCHAR(10) NOT NULL CHECK (chamber IN ('senate', 'house')),
    party VARCHAR(50),
    state VARCHAR(2),
    bio_guide_id VARCHAR(10) UNIQUE,
    photo_url VARCHAR(500),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX idx_politicians_chamber ON politicians(chamber);
CREATE INDEX idx_politicians_party ON politicians(party);
CREATE INDEX idx_politicians_name ON politicians(name);

-- Trades table
CREATE TABLE trades (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    politician_id UUID NOT NULL REFERENCES politicians(id),
    ticker VARCHAR(10) NOT NULL,
    transaction_date DATE NOT NULL,
    disclosure_date DATE NOT NULL,
    transaction_type VARCHAR(10) NOT NULL CHECK (transaction_type IN ('buy', 'sell', 'exchange')),
    amount_min NUMERIC(12, 2),
    amount_max NUMERIC(12, 2),
    asset_description TEXT,
    comment TEXT,

    -- Performance metrics (computed)
    current_price NUMERIC(10, 2),
    price_at_trade NUMERIC(10, 2),
    return_7d NUMERIC(8, 4),
    return_30d NUMERIC(8, 4),
    return_90d NUMERIC(8, 4),

    -- Timing analysis
    timing_score INTEGER CHECK (timing_score BETWEEN 0 AND 100),
    days_to_earnings INTEGER,

    -- Metadata
    source_url VARCHAR(500),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Convert to TimescaleDB hypertable
SELECT create_hypertable('trades', 'transaction_date', if_not_exists => TRUE);

-- Indexes
CREATE INDEX idx_trades_politician ON trades(politician_id);
CREATE INDEX idx_trades_ticker ON trades(ticker);
CREATE INDEX idx_trades_date ON trades(transaction_date DESC);
CREATE INDEX idx_trades_disclosure ON trades(disclosure_date DESC);
CREATE INDEX idx_trades_type ON trades(transaction_type);
CREATE INDEX idx_trades_timing ON trades(timing_score DESC) WHERE timing_score > 70;

-- Composite indexes for common queries
CREATE INDEX idx_trades_politician_date ON trades(politician_id, transaction_date DESC);
CREATE INDEX idx_trades_ticker_date ON trades(ticker, transaction_date DESC);

-- Users table (managed by Supabase, but we track subscriptions)
CREATE TABLE user_subscriptions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL,
    tier VARCHAR(20) NOT NULL CHECK (tier IN ('free', 'premium', 'business')),
    stripe_customer_id VARCHAR(255),
    stripe_subscription_id VARCHAR(255),
    status VARCHAR(20) NOT NULL CHECK (status IN ('active', 'canceled', 'past_due')),
    current_period_end TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX idx_subscriptions_user ON user_subscriptions(user_id);
CREATE INDEX idx_subscriptions_status ON user_subscriptions(status);

-- API keys (for premium users)
CREATE TABLE api_keys (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL,
    key_hash VARCHAR(255) NOT NULL UNIQUE,
    name VARCHAR(100),
    last_used_at TIMESTAMP WITH TIME ZONE,
    rate_limit INTEGER DEFAULT 1000,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    revoked_at TIMESTAMP WITH TIME ZONE
);

CREATE INDEX idx_api_keys_user ON api_keys(user_id);
CREATE INDEX idx_api_keys_hash ON api_keys(key_hash) WHERE revoked_at IS NULL;

-- Performance summary (materialized view, refreshed daily)
CREATE MATERIALIZED VIEW politician_performance AS
SELECT
    p.id,
    p.name,
    p.chamber,
    p.party,
    COUNT(t.id) AS total_trades,
    COUNT(CASE WHEN t.transaction_type = 'buy' THEN 1 END) AS total_buys,
    COUNT(CASE WHEN t.transaction_type = 'sell' THEN 1 END) AS total_sells,
    AVG(t.return_30d) AS avg_return_30d,
    AVG(t.return_90d) AS avg_return_90d,
    STDDEV(t.return_30d) AS stddev_return_30d,
    COUNT(CASE WHEN t.return_30d > 0 THEN 1 END)::FLOAT / NULLIF(COUNT(t.return_30d), 0) AS win_rate_30d,
    MAX(t.transaction_date) AS last_trade_date,
    AVG(t.timing_score) AS avg_timing_score
FROM politicians p
LEFT JOIN trades t ON p.id = t.politician_id
GROUP BY p.id, p.name, p.chamber, p.party;

CREATE UNIQUE INDEX idx_politician_performance_id ON politician_performance(id);
CREATE INDEX idx_politician_performance_return ON politician_performance(avg_return_30d DESC);

-- Refresh function
CREATE OR REPLACE FUNCTION refresh_politician_performance()
RETURNS void AS $$
BEGIN
    REFRESH MATERIALIZED VIEW CONCURRENTLY politician_performance;
END;
$$ LANGUAGE plpgsql;
```

### Alembic Migrations

```python
# alembic/versions/001_initial.py
"""Initial migration

Revision ID: 001
Create Date: 2024-01-01
"""

from alembic import op
import sqlalchemy as sa

def upgrade():
    # Create politicians table
    op.create_table(
        'politicians',
        sa.Column('id', sa.UUID(), primary_key=True),
        sa.Column('name', sa.String(255), nullable=False),
        sa.Column('chamber', sa.String(10), nullable=False),
        sa.Column('party', sa.String(50)),
        sa.Column('state', sa.String(2)),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
    )

    # Create trades table
    # ... (similar to SQL above)

def downgrade():
    op.drop_table('trades')
    op.drop_table('politicians')
```

---

## Data Pipeline

### Scraper Architecture

```python
# app/scrapers/base.py
from abc import ABC, abstractmethod
from typing import List, Dict
import logging

class BaseScraper(ABC):
    def __init__(self):
        self.logger = logging.getLogger(self.__class__.__name__)

    @abstractmethod
    def scrape_recent(self, days: int = 30) -> List[Dict]:
        """Scrape recent trades"""
        pass

    @abstractmethod
    def scrape_historical(self, start_date, end_date) -> List[Dict]:
        """Scrape historical trades"""
        pass

    def validate_trade(self, trade: Dict) -> bool:
        """Validate trade data"""
        required_fields = ['politician_name', 'ticker', 'transaction_date', 'transaction_type']
        return all(field in trade for field in required_fields)

    def deduplicate(self, trades: List[Dict]) -> List[Dict]:
        """Remove duplicate trades"""
        seen = set()
        unique_trades = []
        for trade in trades:
            key = (trade['politician_name'], trade['ticker'], trade['transaction_date'])
            if key not in seen:
                seen.add(key)
                unique_trades.append(trade)
        return unique_trades
```

```python
# app/scrapers/senate_scraper.py
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
import time
from datetime import datetime, timedelta
from .base import BaseScraper

class SenateScraper(BaseScraper):
    BASE_URL = "https://efdsearch.senate.gov/search/"

    def __init__(self):
        super().__init__()
        self.driver = self._setup_driver()

    def _setup_driver(self):
        """Set up headless Chrome"""
        options = webdriver.ChromeOptions()
        options.add_argument('--headless')
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        return webdriver.Chrome(options=options)

    def scrape_recent(self, days: int = 30) -> List[Dict]:
        """Scrape Senate trades from last N days"""
        end_date = datetime.now().date()
        start_date = end_date - timedelta(days=days)

        self.logger.info(f"Scraping Senate trades from {start_date} to {end_date}")

        try:
            # Navigate to search page
            self.driver.get(self.BASE_URL)

            # Wait for page load
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.ID, "agreementId"))
            )

            # Accept agreement
            agree_button = self.driver.find_element(By.ID, "agreementId")
            agree_button.click()

            # Fill in date range
            start_input = self.driver.find_element(By.ID, "fromDate")
            start_input.send_keys(start_date.strftime("%m/%d/%Y"))

            end_input = self.driver.find_element(By.ID, "toDate")
            end_input.send_keys(end_date.strftime("%m/%d/%Y"))

            # Select PTR reports
            report_type = self.driver.find_element(By.ID, "reportType_PTR")
            report_type.click()

            # Submit search
            search_button = self.driver.find_element(By.ID, "searchButton")
            search_button.click()

            # Wait for results
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.CLASS_NAME, "searchResults"))
            )

            # Parse results
            trades = self._parse_results()

            self.logger.info(f"Scraped {len(trades)} Senate trades")
            return trades

        except Exception as e:
            self.logger.error(f"Error scraping Senate trades: {e}")
            return []

        finally:
            self.driver.quit()

    def _parse_results(self) -> List[Dict]:
        """Parse search results page"""
        soup = BeautifulSoup(self.driver.page_source, 'html.parser')
        trades = []

        # Find all report links
        report_links = soup.find_all('a', href=lambda x: x and 'paper' in x)

        for link in report_links:
            try:
                # Click link to open report
                report_url = link['href']
                self.driver.get(report_url)

                # Parse individual report
                report_trades = self._parse_report()
                trades.extend(report_trades)

                # Go back to results
                self.driver.back()

            except Exception as e:
                self.logger.error(f"Error parsing report: {e}")
                continue

        return trades

    def _parse_report(self) -> List[Dict]:
        """Parse individual PTR report"""
        soup = BeautifulSoup(self.driver.page_source, 'html.parser')
        trades = []

        # Extract senator info
        senator_name = soup.find('span', {'class': 'senator-name'}).text.strip()

        # Find transaction table
        table = soup.find('table', {'class': 'transactions'})
        if not table:
            return []

        rows = table.find_all('tr')[1:]  # Skip header

        for row in rows:
            cols = row.find_all('td')
            if len(cols) < 6:
                continue

            trade = {
                'politician_name': senator_name,
                'ticker': cols[0].text.strip(),
                'transaction_date': self._parse_date(cols[1].text.strip()),
                'transaction_type': self._parse_type(cols[2].text.strip()),
                'amount_min': self._parse_amount(cols[3].text.strip())[0],
                'amount_max': self._parse_amount(cols[3].text.strip())[1],
                'asset_description': cols[4].text.strip(),
                'disclosure_date': datetime.now().date(),
                'source_url': self.driver.current_url,
            }

            if self.validate_trade(trade):
                trades.append(trade)

        return trades

    def _parse_date(self, date_str: str) -> datetime.date:
        """Parse date string to date object"""
        return datetime.strptime(date_str, "%m/%d/%Y").date()

    def _parse_type(self, type_str: str) -> str:
        """Parse transaction type"""
        type_str = type_str.lower()
        if 'purchase' in type_str or 'buy' in type_str:
            return 'buy'
        elif 'sale' in type_str or 'sell' in type_str:
            return 'sell'
        else:
            return 'exchange'

    def _parse_amount(self, amount_str: str) -> tuple:
        """Parse amount range"""
        # Example: "$1,001 - $15,000"
        parts = amount_str.replace('$', '').replace(',', '').split('-')
        if len(parts) == 2:
            return (float(parts[0].strip()), float(parts[1].strip()))
        return (0, 0)
```

### Celery Tasks

```python
# app/tasks/scraping.py
from celery import Celery
from app.core.config import settings
from app.scrapers.senate_scraper import SenateScraper
from app.scrapers.house_scraper import HouseScraper
from app.services.trade_service import TradeService
import logging

celery_app = Celery(
    'tasks',
    broker=settings.CELERY_BROKER_URL,
    backend=settings.CELERY_RESULT_BACKEND
)

logger = logging.getLogger(__name__)

@celery_app.task(bind=True, max_retries=3)
def scrape_senate_trades(self):
    """Scrape Senate trades (runs every 4 hours)"""
    try:
        scraper = SenateScraper()
        trades = scraper.scrape_recent(days=1)

        trade_service = TradeService()
        saved_count = 0

        for trade in trades:
            try:
                trade_service.create_or_update_trade(trade)
                saved_count += 1
            except Exception as e:
                logger.error(f"Error saving trade: {e}")

        logger.info(f"Scraped {len(trades)} Senate trades, saved {saved_count}")
        return {"total": len(trades), "saved": saved_count}

    except Exception as e:
        logger.error(f"Error in scrape_senate_trades: {e}")
        raise self.retry(exc=e, countdown=60 * 5)  # Retry in 5 minutes

@celery_app.task(bind=True, max_retries=3)
def scrape_house_trades(self):
    """Scrape House trades (runs every 4 hours, offset from Senate)"""
    # Similar implementation
    pass

@celery_app.task
def refresh_performance_metrics():
    """Refresh materialized view (runs daily)"""
    from app.core.database import engine
    with engine.connect() as conn:
        conn.execute("SELECT refresh_politician_performance()")
    logger.info("Refreshed politician performance metrics")

@celery_app.task
def update_stock_prices():
    """Update current prices for all traded stocks (runs daily)"""
    # Implementation
    pass

# Celery Beat schedule
celery_app.conf.beat_schedule = {
    'scrape-senate-every-4-hours': {
        'task': 'app.tasks.scraping.scrape_senate_trades',
        'schedule': 60 * 60 * 4,  # 4 hours
    },
    'scrape-house-every-4-hours-offset': {
        'task': 'app.tasks.scraping.scrape_house_trades',
        'schedule': 60 * 60 * 4,  # 4 hours
        'args': (),
        'options': {'countdown': 60 * 30},  # Start 30 min after Senate
    },
    'refresh-performance-daily': {
        'task': 'app.tasks.scraping.refresh_performance_metrics',
        'schedule': 60 * 60 * 24,  # Daily
        'options': {'countdown': 60 * 60 * 2},  # 2 AM
    },
}
```

---

## Caching Strategy

```python
# app/core/cache.py
from redis import Redis
import json
import pickle
from functools import wraps
from app.core.config import settings

redis_client = Redis.from_url(settings.REDIS_URL, decode_responses=True)

class CacheService:
    """Redis caching service"""

    @staticmethod
    def get(key: str):
        """Get value from cache"""
        value = redis_client.get(key)
        if value:
            try:
                return json.loads(value)
            except json.JSONDecodeError:
                return value
        return None

    @staticmethod
    def set(key: str, value, ttl: int = 3600):
        """Set value in cache with TTL"""
        if isinstance(value, (dict, list)):
            value = json.dumps(value)
        redis_client.setex(key, ttl, value)

    @staticmethod
    def delete(key: str):
        """Delete key from cache"""
        redis_client.delete(key)

    @staticmethod
    def delete_pattern(pattern: str):
        """Delete all keys matching pattern"""
        for key in redis_client.scan_iter(match=pattern):
            redis_client.delete(key)

def cached(ttl: int = 3600, key_prefix: str = ""):
    """Decorator for caching function results"""
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # Generate cache key
            cache_key = f"{key_prefix}:{func.__name__}:{str(args)}:{str(kwargs)}"

            # Try to get from cache
            cached_result = CacheService.get(cache_key)
            if cached_result is not None:
                return cached_result

            # Compute result
            result = await func(*args, **kwargs)

            # Store in cache
            CacheService.set(cache_key, result, ttl)

            return result
        return wrapper
    return decorator
```

**Cache Strategy:**

| Data Type | TTL | Invalidation |
|-----------|-----|--------------|
| Leaderboard | 1 hour | New trades |
| Politician detail | 4 hours | New trades for politician |
| Trade detail | 24 hours | Price update |
| API responses | 5-60 min | Based on freshness needs |
| Static data | 7 days | Manual |

---

## Authentication & Authorization

```python
# app/core/security.py
from supabase import create_client
from app.core.config import settings
from fastapi import HTTPException, Security
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

supabase = create_client(settings.SUPABASE_URL, settings.SUPABASE_KEY)
security = HTTPBearer()

async def get_current_user(credentials: HTTPAuthorizationCredentials = Security(security)):
    """Get current user from JWT token"""
    token = credentials.credentials

    try:
        # Verify token with Supabase
        user = supabase.auth.get_user(token)
        return user

    except Exception:
        raise HTTPException(status_code=401, detail="Invalid authentication credentials")

async def get_current_active_user(current_user = Depends(get_current_user)):
    """Get current active user"""
    if not current_user:
        raise HTTPException(status_code=401, detail="User not found")
    return current_user

async def check_premium_user(current_user = Depends(get_current_active_user)):
    """Check if user has premium subscription"""
    # Query user_subscriptions table
    from app.services.user_service import UserService
    user_service = UserService()

    subscription = user_service.get_subscription(current_user.id)
    if not subscription or subscription.tier == 'free':
        raise HTTPException(status_code=403, detail="Premium subscription required")

    return current_user
```

**Rate Limiting:**

```python
# app/middleware/rate_limit.py
from fastapi import Request, HTTPException
from starlette.middleware.base import BaseHTTPMiddleware
from app.core.cache import redis_client
import time

class RateLimitMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        # Get client IP
        client_ip = request.client.host

        # Check if authenticated user
        auth_header = request.headers.get('Authorization')
        if auth_header:
            # Premium users: 1000 requests/day
            limit = 1000
            window = 86400  # 24 hours
        else:
            # Anonymous: 100 requests/hour
            limit = 100
            window = 3600  # 1 hour

        # Rate limit key
        key = f"rate_limit:{client_ip}:{int(time.time() / window)}"

        # Increment counter
        current = redis_client.incr(key)
        if current == 1:
            redis_client.expire(key, window)

        # Check limit
        if current > limit:
            raise HTTPException(status_code=429, detail="Rate limit exceeded")

        response = await call_next(request)
        return response
```

---

## Monitoring & Observability

**Sentry Integration:**

```python
import sentry_sdk
from sentry_sdk.integrations.fastapi import FastApiIntegration

sentry_sdk.init(
    dsn=settings.SENTRY_DSN,
    integrations=[FastApiIntegration()],
    traces_sample_rate=0.1,  # 10% of transactions
    environment="production",
)
```

**PostHog Analytics:**

```typescript
// frontend/lib/analytics.ts
import posthog from 'posthog-js'

if (typeof window !== 'undefined') {
  posthog.init(process.env.NEXT_PUBLIC_POSTHOG_KEY!, {
    api_host: 'https://app.posthog.com',
  })
}

export const analytics = {
  track: (event: string, properties?: Record<string, any>) => {
    posthog.capture(event, properties)
  },
  identify: (userId: string, traits?: Record<string, any>) => {
    posthog.identify(userId, traits)
  },
}
```

**Health Checks:**

```python
@app.get("/health")
async def health_check():
    """Comprehensive health check"""
    health = {
        "status": "healthy",
        "database": check_database(),
        "redis": check_redis(),
        "celery": check_celery(),
    }

    if not all(health.values()):
        raise HTTPException(status_code=503, detail=health)

    return health
```

---

This technical architecture provides a solid foundation for building a scalable, maintainable, and production-ready platform. The architecture prioritizes:

1. **Scalability** - Horizontal scaling, caching, async processing
2. **Reliability** - Error handling, monitoring, backups
3. **Performance** - Optimized queries, caching, CDN
4. **Security** - Authentication, authorization, rate limiting
5. **Maintainability** - Clean code, testing, documentation
