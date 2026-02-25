# MVP Roadmap - Government Trade Tracker
## Detailed 26-Week Implementation Plan

---

## Overview

**Mission:** Build the most transparent and statistically rigorous government trade tracking platform.

**Timeline:** 26 weeks (6 months)

**Team Size:** 1-2 developers

**Budget:** $8,400 total

**Success Metric:** 500 users, 10 premium subscribers, positive feedback

---

## Sprint Structure

- **Sprint Length:** 2 weeks
- **Total Sprints:** 13
- **Review:** End of each sprint
- **Retrospective:** End of each sprint
- **Demo:** Every other sprint

---

## Phase 0: Foundation (Sprints 1-2, Weeks 1-3)

### Sprint 1: Legal & Infrastructure (Weeks 1-2)

**Goal:** Legal protection + development environment ready

#### Week 1: Legal Setup

**Monday-Tuesday: Business Formation**
- [ ] Research LLC formation services (Recommended: Northwest Registered Agent, ZenBusiness)
- [ ] Choose business name (check availability)
- [ ] File LLC formation documents
- [ ] Apply for EIN from IRS (https://www.irs.gov/businesses/small-businesses-self-employed/apply-for-an-employer-identification-number-ein-online)
- [ ] Order: 2 days, Cost: $100-500

**Wednesday-Thursday: Legal Documents**
- [ ] Draft Terms of Service (use template + lawyer review)
  - Recommended: Termly.io templates + local lawyer
- [ ] Draft Privacy Policy (GDPR + CCPA compliant)
  - Include: data collection, usage, sharing, retention, rights
- [ ] Create cookie policy
- [ ] Create disclaimer templates for:
  - Homepage
  - Trade pages
  - Politician pages
  - Email footer
- [ ] Cost: $1,500-2,000

**Friday: Banking & Domain**
- [ ] Open business bank account (Recommended: Mercury, Brex for startups)
- [ ] Purchase domain name (Recommended: Namecheap, Cloudflare)
  - Check: .com, .io, .ai availability
  - Cost: $12-15/year
- [ ] Set up Cloudflare (free tier)
  - DNS management
  - SSL certificates
  - DDoS protection

**Deliverable:** Legal entity, bank account, domain, legal documents draft

---

#### Week 2: Development Environment

**Monday: Repository Setup**
- [ ] Create GitHub organization
- [ ] Create frontend repository (quant-frontend)
- [ ] Create backend repository (quant-backend)
- [ ] Set up branch protection (main branch)
- [ ] Configure .gitignore files
- [ ] Add README.md files
- [ ] Add LICENSE (MIT or Apache 2.0)

**Tuesday: Frontend Setup (Next.js)**
```bash
npx create-next-app@latest quant-frontend --typescript --tailwind --app --eslint
cd quant-frontend
npm install @tanstack/react-query zustand react-hook-form zod
npm install @radix-ui/react-dialog @radix-ui/react-dropdown-menu
npm install recharts date-fns
npm install -D @types/node vitest @testing-library/react
```

- [ ] Configure TypeScript (strict mode)
- [ ] Set up Tailwind CSS
- [ ] Install shadcn/ui components
- [ ] Configure ESLint + Prettier
- [ ] Set up Vitest for testing
- [ ] Create base folder structure:
```
src/
├── app/
│   ├── (marketing)/
│   │   ├── page.tsx
│   │   └── layout.tsx
│   └── api/
├── components/
│   ├── ui/
│   └── layout/
├── lib/
├── hooks/
└── types/
```

**Wednesday: Backend Setup (FastAPI)**
```bash
mkdir quant-backend && cd quant-backend
python -m venv venv
source venv/bin/activate  # or venv\Scripts\activate on Windows
pip install fastapi uvicorn sqlalchemy psycopg2-binary alembic
pip install pydantic pydantic-settings python-dotenv
pip install celery redis
pip install httpx beautifulsoup4 selenium
pip install pytest pytest-asyncio pytest-cov
pip install ruff black mypy
```

- [ ] Create base folder structure:
```
app/
├── api/
│   └── v1/
│       ├── __init__.py
│       └── routes/
├── core/
│   ├── config.py
│   ├── database.py
│   └── security.py
├── models/
├── schemas/
├── services/
├── scrapers/
└── tasks/
tests/
alembic/
```

- [ ] Configure settings with Pydantic
- [ ] Set up pytest configuration
- [ ] Configure ruff + black
- [ ] Set up mypy for type checking

**Thursday: Database Setup**
- [ ] Sign up for Supabase (free tier)
- [ ] Create new project
- [ ] Get connection string
- [ ] Install TimescaleDB extension:
```sql
CREATE EXTENSION IF NOT EXISTS timescaledb;
```
- [ ] Create initial database schema (Alembic migration):
```python
# Politicians table
# Trades table
# Users table
# Subscriptions table
```
- [ ] Test connection from backend

**Friday: Infrastructure Accounts**
- [ ] Create Vercel account
  - Connect GitHub repo
  - Configure environment variables
  - Deploy "Hello World"
- [ ] Create Railway account
  - Connect GitHub repo
  - Configure environment variables
  - Deploy FastAPI "Hello World"
- [ ] Create Sentry account
  - Get DSN keys
  - Configure error tracking
- [ ] Create PostHog account
  - Get API key
  - Configure analytics
- [ ] Create Resend account
  - Verify domain
  - Get API key

**Deliverable:** Deployable skeleton apps (frontend + backend)

---

### Sprint 2: Authentication & Core Setup (Week 3)

**Goal:** User authentication working

**Monday-Tuesday: Supabase Auth Integration**

Frontend:
- [ ] Install Supabase client: `npm install @supabase/supabase-js`
- [ ] Create Supabase client utility
- [ ] Create auth context
- [ ] Build login component
- [ ] Build signup component
- [ ] Build password reset flow
- [ ] Protected route middleware

Backend:
- [ ] Install Supabase client: `pip install supabase`
- [ ] Create auth middleware
- [ ] JWT verification
- [ ] User session management
- [ ] Role-based access control (free, premium)

**Wednesday: User Dashboard**
- [ ] Create user dashboard page
- [ ] Account settings component
- [ ] Profile update form
- [ ] Email preferences
- [ ] Delete account flow

**Thursday: Testing**
- [ ] Write tests for auth flows
- [ ] Test registration
- [ ] Test login
- [ ] Test password reset
- [ ] Test protected routes
- [ ] Test session expiration

**Friday: CI/CD Pipeline**
- [ ] GitHub Actions workflow for frontend:
  - Lint
  - Type check
  - Run tests
  - Build
  - Deploy to Vercel (preview)
- [ ] GitHub Actions workflow for backend:
  - Lint (ruff)
  - Type check (mypy)
  - Run tests
  - Build Docker image
  - Deploy to Railway (preview)

**Deliverable:** Working authentication system

**Sprint 1-2 Review:**
- Total cost: ~$2,500
- Legal entity: ✓
- Development environment: ✓
- Authentication: ✓
- Deployable apps: ✓

---

## Phase 1: Core Data Pipeline (Sprints 3-5, Weeks 4-7)

### Sprint 3: Senate Scraper (Weeks 4-5)

**Goal:** Reliable Senate trade data collection

#### Week 4: Senate Scraper Implementation

**Monday: Research & Planning**
- [ ] Analyze efdsearch.senate.gov structure
- [ ] Identify form types (PTR, Annual, Amendment)
- [ ] Map data fields
- [ ] Identify JavaScript rendering requirements
- [ ] Plan Selenium strategy

**Tuesday-Wednesday: Base Scraper**
```python
# app/scrapers/senate.py
class SenateScraper:
    def __init__(self):
        self.driver = self._setup_selenium()
        self.base_url = "https://efdsearch.senate.gov/search/"

    def scrape_recent_trades(self, days=30):
        """Scrape trades from last N days"""
        pass

    def parse_ptr_form(self, form_data):
        """Parse Periodic Transaction Report"""
        pass

    def extract_transactions(self, html):
        """Extract transaction data from form"""
        pass
```

- [ ] Set up Selenium with headless Chrome
- [ ] Implement navigation to search page
- [ ] Implement form submission
- [ ] Implement pagination handling
- [ ] Implement individual form parsing

**Thursday: Data Extraction**
- [ ] Extract senator information
- [ ] Extract transaction date
- [ ] Extract ticker symbol
- [ ] Extract transaction type (buy/sell)
- [ ] Extract amount range
- [ ] Extract asset description
- [ ] Handle missing data gracefully

**Friday: Testing & Validation**
- [ ] Test with different date ranges
- [ ] Test with different senators
- [ ] Test pagination
- [ ] Test error handling
- [ ] Validate data quality
- [ ] Write unit tests

---

#### Week 5: Data Pipeline & Storage

**Monday: Database Models**
```python
# app/models/politician.py
class Politician(Base):
    __tablename__ = "politicians"
    id = Column(UUID, primary_key=True)
    name = Column(String, nullable=False)
    chamber = Column(Enum("senate", "house"))
    party = Column(String)
    state = Column(String)
    created_at = Column(DateTime)

# app/models/trade.py
class Trade(Base):
    __tablename__ = "trades"
    id = Column(UUID, primary_key=True)
    politician_id = Column(UUID, ForeignKey("politicians.id"))
    ticker = Column(String, nullable=False)
    transaction_date = Column(Date, nullable=False)
    disclosure_date = Column(Date, nullable=False)
    transaction_type = Column(Enum("buy", "sell"))
    amount_min = Column(Numeric)
    amount_max = Column(Numeric)
    asset_description = Column(Text)
    created_at = Column(DateTime)
```

- [ ] Create Alembic migration
- [ ] Create indexes (politician_id, ticker, transaction_date)
- [ ] Create TimescaleDB hypertable for trades
- [ ] Test model relationships

**Tuesday: Data Validation**
```python
# app/services/data_validator.py
class DataValidator:
    def validate_trade(self, trade_data):
        """Validate trade data quality"""
        # Check required fields
        # Validate date formats
        # Validate ticker symbols
        # Check for duplicates
        # Validate amount ranges
        pass
```

- [ ] Implement validation logic
- [ ] Create validation tests
- [ ] Handle validation errors
- [ ] Log validation issues

**Wednesday: Celery Task Setup**
```python
# app/tasks/scraping.py
@celery.task
def scrape_senate_trades():
    """Scrape Senate trades (runs every 4 hours)"""
    scraper = SenateScraper()
    trades = scraper.scrape_recent_trades(days=1)

    for trade in trades:
        if validator.validate_trade(trade):
            db.save_trade(trade)

    return {"trades_scraped": len(trades)}
```

- [ ] Set up Redis (Railway add-on)
- [ ] Configure Celery
- [ ] Create scraping task
- [ ] Set up schedule (every 4 hours)
- [ ] Add monitoring/logging

**Thursday-Friday: Monitoring & Alerting**
- [ ] Create scraper health dashboard
- [ ] Track successful scrapes
- [ ] Track errors
- [ ] Alert on scraper failure (>4 hours)
- [ ] Create manual trigger endpoint
- [ ] Test full pipeline

**Deliverable:** Working Senate scraper with 30 days of data

---

### Sprint 4: House Scraper (Weeks 6-7)

**Goal:** Reliable House trade data collection

#### Week 6: House Scraper Implementation

**Monday: Research & Planning**
- [ ] Analyze clerk.house.gov structure
- [ ] Identify form types (FD, Amendment)
- [ ] Map data fields
- [ ] Plan scraping strategy

**Tuesday-Wednesday: Base Scraper**
```python
# app/scrapers/house.py
class HouseScraper:
    def __init__(self):
        self.base_url = "https://disclosures-clerk.house.gov/FinancialDisclosure"

    def scrape_recent_trades(self, days=30):
        """Scrape trades from last N days"""
        pass

    def parse_fd_form(self, form_data):
        """Parse Financial Disclosure form"""
        pass
```

- [ ] Implement similar to Senate scraper
- [ ] Handle House-specific quirks
- [ ] Parse PDF forms if needed (PyPDF2)
- [ ] Extract transaction data

**Thursday: Integration**
- [ ] Use same database models
- [ ] Use same validation logic
- [ ] Create Celery task
- [ ] Schedule (every 4 hours, offset from Senate)

**Friday: Testing**
- [ ] Test with different date ranges
- [ ] Test with different representatives
- [ ] Test error handling
- [ ] Validate data quality
- [ ] Write unit tests

---

#### Week 7: Historical Data & Optimization

**Monday-Tuesday: Historical Backfill**
- [ ] Create backfill script
- [ ] Scrape last 6 months (not 10 years!)
- [ ] Rate limit appropriately
- [ ] Handle errors gracefully
- [ ] Monitor progress
- [ ] Validate data quality

**Wednesday: Performance Optimization**
- [ ] Add database indexes
- [ ] Optimize queries
- [ ] Implement connection pooling
- [ ] Add query caching
- [ ] Profile slow queries

**Thursday: Data Quality Checks**
- [ ] Check for duplicates
- [ ] Check for missing data
- [ ] Validate ticker symbols
- [ ] Check date ranges
- [ ] Manual spot checks

**Friday: Backup & Recovery**
- [ ] Set up automated daily backups
- [ ] Test backup restoration
- [ ] Document recovery process
- [ ] Set up backup monitoring

**Deliverable:** 6 months of historical data, both chambers

**Sprint 3-5 Review:**
- Total trades: 5,000-10,000
- Data quality: >99%
- Scraper uptime: >95%
- Cost: ~$500

---

## Phase 2: Analytics & API (Sprints 6-7, Weeks 8-11)

### Sprint 6: Performance Analytics (Weeks 8-9)

**Goal:** Calculate meaningful statistics

#### Week 8: Price Data & Returns

**Monday: Market Data Integration**
```python
# app/services/market_data.py
import yfinance as yf  # Start with free, upgrade later

class MarketDataService:
    def get_price_data(self, ticker, start_date, end_date):
        """Get historical price data"""
        pass

    def calculate_return(self, ticker, buy_date, sell_date):
        """Calculate return for period"""
        pass

    def get_benchmark_return(self, start_date, end_date):
        """Get S&P 500 return for period"""
        pass
```

- [ ] Implement yfinance integration
- [ ] Handle missing/delisted stocks
- [ ] Cache price data (Redis)
- [ ] Handle corporate actions (splits, dividends)

**Tuesday: Return Calculations**
```python
# app/services/performance.py
class PerformanceService:
    def calculate_trade_return(self, trade):
        """
        Calculate return for a trade
        For buys: current price vs buy price
        For sells: sell price vs previous known price
        """
        pass

    def calculate_politician_returns(self, politician_id):
        """Calculate overall returns for politician"""
        pass

    def calculate_win_rate(self, politician_id):
        """Calculate percentage of profitable trades"""
        pass
```

- [ ] Implement return calculations
- [ ] Handle open positions
- [ ] Weight by position size
- [ ] Annualize returns

**Wednesday: Statistical Tests**
```python
# app/services/statistics.py
from scipy import stats

class StatisticsService:
    def t_test_vs_market(self, politician_returns, market_returns):
        """
        Test if politician returns significantly different from market
        Returns: t-statistic, p-value
        """
        t_stat, p_value = stats.ttest_ind(politician_returns, market_returns)
        return {
            "t_statistic": t_stat,
            "p_value": p_value,
            "significant": p_value < 0.05
        }

    def calculate_confidence_interval(self, returns, confidence=0.95):
        """Calculate confidence interval for returns"""
        pass
```

- [ ] Implement t-tests
- [ ] Calculate confidence intervals
- [ ] Handle small sample sizes
- [ ] Document methodology

**Thursday-Friday: Sector Analysis**
- [ ] Map tickers to sectors (using yfinance)
- [ ] Calculate sector concentrations
- [ ] Identify sector trends
- [ ] Compare to market sector weights

**Deliverable:** Working performance analytics

---

#### Week 9: API Development

**Monday-Tuesday: API Endpoints**
```python
# app/api/v1/routes/trades.py
from fastapi import APIRouter, Depends, Query

router = APIRouter()

@router.get("/trades")
async def list_trades(
    politician_id: Optional[UUID] = None,
    ticker: Optional[str] = None,
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
    limit: int = Query(default=50, le=100),
    offset: int = 0
):
    """List trades with filters"""
    pass

@router.get("/trades/{trade_id}")
async def get_trade(trade_id: UUID):
    """Get single trade detail"""
    pass

# app/api/v1/routes/politicians.py
@router.get("/politicians")
async def list_politicians(
    chamber: Optional[str] = None,
    party: Optional[str] = None,
    limit: int = Query(default=50, le=100)
):
    """List politicians with performance metrics"""
    pass

@router.get("/politicians/{politician_id}")
async def get_politician(politician_id: UUID):
    """Get politician detail with trade history"""
    pass

@router.get("/politicians/{politician_id}/performance")
async def get_politician_performance(politician_id: UUID):
    """Get detailed performance analytics"""
    pass

# app/api/v1/routes/stats.py
@router.get("/stats/leaderboard")
async def get_leaderboard(
    period: str = Query(default="30d", regex="^(7d|30d|90d|1y|all)$"),
    chamber: Optional[str] = None,
    party: Optional[str] = None
):
    """Get performance leaderboard"""
    pass
```

- [ ] Implement all endpoints
- [ ] Add input validation (Pydantic)
- [ ] Add authentication checks
- [ ] Add rate limiting

**Wednesday: Caching Strategy**
```python
# app/core/cache.py
from redis import Redis
import json

class CacheService:
    def __init__(self):
        self.redis = Redis.from_url(settings.REDIS_URL)

    def get_or_compute(self, key, compute_fn, ttl=3600):
        """Get from cache or compute and cache"""
        cached = self.redis.get(key)
        if cached:
            return json.loads(cached)

        result = compute_fn()
        self.redis.setex(key, ttl, json.dumps(result))
        return result
```

- [ ] Implement caching layer
- [ ] Define TTL strategy
  - Leaderboard: 1 hour
  - Politician detail: 4 hours
  - Trade detail: 24 hours
- [ ] Implement cache warming
- [ ] Cache invalidation on new data

**Thursday: API Documentation**
- [ ] Configure FastAPI automatic docs
- [ ] Add endpoint descriptions
- [ ] Add request/response examples
- [ ] Add authentication docs
- [ ] Test all endpoints in docs UI

**Friday: API Testing**
- [ ] Write integration tests
- [ ] Test pagination
- [ ] Test filters
- [ ] Test error handling
- [ ] Load testing (100 concurrent requests)

**Deliverable:** Production-ready API

---

### Sprint 7: Timing Analysis (Weeks 10-11)

**Goal:** Detect suspicious timing

#### Week 10: Event Detection

**Monday-Tuesday: Basic Timing Analysis**
```python
# app/services/timing_analysis.py
class TimingAnalysisService:
    def analyze_trade_timing(self, trade):
        """
        Analyze if trade timing is suspicious
        Returns timing score (0-100)
        """
        score = 0

        # Check if trade was before earnings (suspicious)
        days_to_earnings = self._days_until_earnings(trade.ticker, trade.date)
        if 0 < days_to_earnings < 14:
            score += 30

        # Check for unusual price movement after trade
        price_change_7d = self._price_change_after(trade, days=7)
        if abs(price_change_7d) > 10:  # >10% movement
            score += 40

        # Check for news correlation
        major_news = self._check_major_news(trade.ticker, trade.date, days=14)
        if major_news:
            score += 30

        return score
```

- [ ] Implement earnings calendar check (yfinance)
- [ ] Calculate price movements post-trade
- [ ] Basic news correlation (RSS feeds)
- [ ] Calculate timing scores

**Wednesday-Thursday: Statistical Validation**
- [ ] Compare to random trades
- [ ] Bootstrap confidence intervals
- [ ] Multiple hypothesis correction
- [ ] Flag statistically significant patterns

**Friday: Testing & Documentation**
- [ ] Test with known suspicious trades
- [ ] Test with normal trades
- [ ] Document methodology
- [ ] Write unit tests

---

#### Week 11: Integration & Optimization

**Monday: Integrate Timing Analysis**
- [ ] Add timing scores to trade model
- [ ] Update API endpoints to include timing data
- [ ] Cache timing analysis results
- [ ] Add timing filters to API

**Tuesday: Performance Optimization**
- [ ] Profile slow queries
- [ ] Optimize database indexes
- [ ] Optimize cache strategy
- [ ] Reduce API response times

**Wednesday: Monitoring Dashboard**
- [ ] Create internal dashboard (Grafana)
- [ ] Track API response times
- [ ] Track cache hit rates
- [ ] Track scraper health
- [ ] Track database performance

**Thursday-Friday: End-to-End Testing**
- [ ] Test complete data pipeline
- [ ] Test all API endpoints
- [ ] Test with realistic load
- [ ] Fix any bugs found
- [ ] Performance benchmarks

**Deliverable:** Complete backend with analytics

**Sprint 6-7 Review:**
- API endpoints: 10+
- Response time: <200ms (cached)
- Cache hit rate: >80%
- Test coverage: >85%
- Cost: ~$300

---

## Phase 3: Frontend MVP (Sprints 8-10, Weeks 12-16)

### Sprint 8: Core Components (Weeks 12-13)

**Goal:** Reusable UI components

#### Week 12: Design System & Base Components

**Monday: Design System**
- [ ] Define color palette
- [ ] Define typography scale
- [ ] Define spacing system
- [ ] Define breakpoints
- [ ] Configure Tailwind theme
- [ ] Set up dark mode

**Tuesday: Layout Components**
```typescript
// src/components/layout/Header.tsx
// src/components/layout/Footer.tsx
// src/components/layout/Navigation.tsx
// src/components/layout/Container.tsx
```

- [ ] Build header with navigation
- [ ] Build footer with links
- [ ] Build responsive navigation
- [ ] Build container component
- [ ] Implement dark mode toggle

**Wednesday: UI Components**
```typescript
// src/components/ui/Button.tsx
// src/components/ui/Card.tsx
// src/components/ui/Badge.tsx
// src/components/ui/Table.tsx
// src/components/ui/Input.tsx
```

- [ ] Build button variants
- [ ] Build card component
- [ ] Build badge component (party, performance)
- [ ] Build table component
- [ ] Build input components

**Thursday: Chart Components**
```typescript
// src/components/charts/PerformanceChart.tsx
// src/components/charts/SectorChart.tsx
```

- [ ] Build performance line chart
- [ ] Build sector pie chart
- [ ] Make charts responsive
- [ ] Add tooltips
- [ ] Add legends

**Friday: Testing**
- [ ] Write component tests
- [ ] Visual regression tests
- [ ] Accessibility tests
- [ ] Mobile responsive tests

---

#### Week 13: Data Components

**Monday-Tuesday: Trade Components**
```typescript
// src/components/trades/TradeCard.tsx
interface TradeCardProps {
  trade: Trade;
  showPolitician?: boolean;
}

// src/components/trades/TradeList.tsx
// src/components/trades/TradeFeed.tsx
```

- [ ] Build trade card component
  - Display politician, ticker, type, amount
  - Show return if closed
  - Timing indicator
  - Social share button
- [ ] Build trade list with pagination
- [ ] Build live trade feed
- [ ] Add filtering UI

**Wednesday-Thursday: Politician Components**
```typescript
// src/components/politicians/PoliticianCard.tsx
// src/components/politicians/PoliticianList.tsx
// src/components/politicians/PerformanceWidget.tsx
```

- [ ] Build politician card
  - Photo, name, party, state
  - Performance metrics
  - Trade count
  - Link to detail
- [ ] Build politician list with search
- [ ] Build performance widget
- [ ] Add filtering UI

**Friday: Stats Components**
```typescript
// src/components/stats/Leaderboard.tsx
// src/components/stats/StatsCard.tsx
```

- [ ] Build leaderboard component
- [ ] Build stats card component
- [ ] Add period selector
- [ ] Add filters

**Deliverable:** Complete component library

---

### Sprint 9: Main Pages (Weeks 14-15)

**Goal:** Core user-facing pages

#### Week 14: Homepage & Politician Pages

**Monday-Tuesday: Homepage**
```typescript
// src/app/(marketing)/page.tsx
export default function HomePage() {
  return (
    <>
      <Hero />
      <RecentTrades limit={10} />
      <TopPerformers period="30d" />
      <UnusualActivity />
      <EmailSignup />
    </>
  )
}
```

- [ ] Build hero section
  - Compelling headline
  - Value proposition
  - CTA to signup
- [ ] Recent trades section
- [ ] Top performers section
- [ ] Unusual activity alerts
- [ ] Email signup form
- [ ] Testimonials (future)

**Wednesday: Politician Directory**
```typescript
// src/app/(marketing)/politicians/page.tsx
```

- [ ] Searchable table
- [ ] Filter by chamber
- [ ] Filter by party
- [ ] Sort by performance
- [ ] Pagination
- [ ] Mobile responsive

**Thursday-Friday: Politician Detail**
```typescript
// src/app/(marketing)/politicians/[id]/page.tsx
```

- [ ] Politician header (photo, info)
- [ ] Performance summary
- [ ] Performance chart
- [ ] Trade history table
- [ ] Sector breakdown
- [ ] Statistical analysis
- [ ] Social share buttons
- [ ] SEO optimization (metadata)

---

#### Week 15: Leaderboard & Methodology Pages

**Monday: Leaderboard Page**
```typescript
// src/app/(marketing)/leaderboard/page.tsx
```

- [ ] Period selector (7d, 30d, 90d, 1y, all)
- [ ] Filter by chamber
- [ ] Filter by party
- [ ] Top 50 performers
- [ ] Performance metrics
- [ ] Links to politician pages

**Tuesday: Trade Detail Page**
```typescript
// src/app/(marketing)/trades/[id]/page.tsx
```

- [ ] Trade information
- [ ] Price chart with trade marker
- [ ] Performance since trade
- [ ] Timing analysis
- [ ] Related trades
- [ ] Social share

**Wednesday-Thursday: About/Methodology**
```typescript
// src/app/(marketing)/about/page.tsx
// src/app/(marketing)/methodology/page.tsx
```

- [ ] How we collect data
- [ ] How we calculate returns
- [ ] Statistical methods
- [ ] Limitations & disclaimers
- [ ] FAQ section
- [ ] Contact information

**Friday: SEO & Meta Tags**
- [ ] Add meta descriptions
- [ ] Add Open Graph tags
- [ ] Add Twitter Cards
- [ ] Add structured data (Schema.org)
- [ ] Generate sitemap
- [ ] Configure robots.txt
- [ ] Submit to Google Search Console

**Deliverable:** All core pages functional

---

### Sprint 10: Premium Features (Weeks 16)

**Goal:** Freemium functionality

**Monday-Tuesday: Pricing Page**
```typescript
// src/app/(marketing)/pricing/page.tsx
```

- [ ] Feature comparison table
- [ ] Free tier features
- [ ] Premium tier features ($9.99/mo)
- [ ] Annual discount (2 months free)
- [ ] FAQ
- [ ] CTA buttons

**Wednesday: Stripe Integration**
```typescript
// src/app/api/stripe/checkout/route.ts
// src/app/api/stripe/webhook/route.ts
```

- [ ] Create Stripe account
- [ ] Create subscription product
- [ ] Build checkout flow
- [ ] Handle webhook events
- [ ] Update user subscription status

**Thursday: User Dashboard**
```typescript
// src/app/(app)/dashboard/page.tsx
```

- [ ] Account overview
- [ ] Subscription status
- [ ] API key management (premium)
- [ ] Email preferences
- [ ] Billing history
- [ ] Manage subscription (upgrade/cancel)

**Friday: Premium Features**
- [ ] API key generation
- [ ] Rate limiting (free: 10/min, premium: 1000/day)
- [ ] Historical data access (free: 6mo, premium: all)
- [ ] Advanced filters (premium only)
- [ ] Ad removal for premium

**Deliverable:** Working freemium model

**Sprint 8-10 Review:**
- Pages: 8+ complete
- Components: 30+ tested
- Mobile responsive: ✓
- Premium integration: ✓
- Cost: ~$500

---

## Phase 4: Polish & Launch (Sprints 11-13, Weeks 17-24)

### Sprint 11: Testing & Optimization (Weeks 17-18)

**Goal:** Production-ready quality

#### Week 17: Testing

**Monday: End-to-End Testing**
```typescript
// e2e/homepage.spec.ts
import { test, expect } from '@playwright/test'

test('homepage loads and displays trades', async ({ page }) => {
  await page.goto('/')
  await expect(page.locator('h1')).toContainText('Government Trades')
  await expect(page.locator('[data-testid="trade-card"]')).toHaveCount(10)
})
```

- [ ] Install Playwright
- [ ] Write critical path tests
  - Homepage loads
  - Search works
  - Politician page loads
  - Trade detail loads
  - Signup flow
  - Login flow
  - Premium checkout

**Tuesday: Performance Testing**
- [ ] Lighthouse audit (score >90)
- [ ] Core Web Vitals
  - LCP < 2.5s
  - FID < 100ms
  - CLS < 0.1
- [ ] Bundle size optimization
- [ ] Image optimization
- [ ] Code splitting

**Wednesday: Accessibility Testing**
- [ ] WCAG 2.1 AA compliance
- [ ] Screen reader testing
- [ ] Keyboard navigation
- [ ] Color contrast
- [ ] Alt text for images
- [ ] ARIA labels

**Thursday: Security Audit**
- [ ] Run security scanner (npm audit)
- [ ] Fix critical vulnerabilities
- [ ] Review authentication flow
- [ ] Review authorization logic
- [ ] Check for XSS vulnerabilities
- [ ] Check for SQL injection
- [ ] HTTPS enforcement

**Friday: Bug Fixes**
- [ ] Fix all critical bugs
- [ ] Fix all high priority bugs
- [ ] Document known issues
- [ ] Create bug tracking system

---

#### Week 18: Optimization & Monitoring

**Monday: Performance Optimization**
- [ ] Database query optimization
- [ ] API response time optimization
- [ ] Frontend bundle size reduction
- [ ] Image lazy loading
- [ ] Implement CDN for static assets

**Tuesday: Caching Refinement**
- [ ] Review cache TTLs
- [ ] Implement cache warming
- [ ] Add cache monitoring
- [ ] Test cache invalidation

**Wednesday-Thursday: Monitoring Setup**
- [ ] Sentry error tracking
- [ ] PostHog analytics
- [ ] Vercel Analytics
- [ ] UptimeRobot (99.9% uptime monitoring)
- [ ] Create alerting rules:
  - API response time >1s
  - Error rate >1%
  - Uptime <99%
  - Scraper failure

**Friday: Load Testing**
```python
# locustfile.py
from locust import HttpUser, task, between

class WebsiteUser(HttpUser):
    wait_time = between(1, 3)

    @task(3)
    def homepage(self):
        self.client.get("/")

    @task(2)
    def politician_list(self):
        self.client.get("/politicians")

    @task(1)
    def api_trades(self):
        self.client.get("/api/v1/trades?limit=50")
```

- [ ] Install Locust
- [ ] Write load test scenarios
- [ ] Test with 100 concurrent users
- [ ] Test with 1000 concurrent users
- [ ] Identify bottlenecks
- [ ] Fix performance issues

**Deliverable:** Production-ready performance

---

### Sprint 12: Content & Marketing Prep (Weeks 19-21)

**Goal:** Marketing assets ready

#### Week 19: Content Creation

**Monday-Tuesday: Blog Posts**
- [ ] Write 10 blog posts:
  1. "How to Track Congress Stock Trades"
  2. "Nancy Pelosi's Trading Performance: Statistical Analysis"
  3. "Which Political Party Trades Better?"
  4. "Understanding P-Values in Trading Analysis"
  5. "The January Effect in Congress Trades"
  6. "How We Calculate Trading Returns"
  7. "Insider Trading Laws for Congress"
  8. "Top 10 Congressional Traders of 2024"
  9. "Statistical Significance Explained"
  10. "Walk-Forward Validation in Trading"

**Wednesday: Email Templates**
```html
<!-- Welcome email -->
<!-- Weekly digest -->
<!-- Trade alert (premium) -->
<!-- Unusual activity alert -->
<!-- Upgrade to premium -->
```

- [ ] Design email templates (Resend)
- [ ] Test email deliverability
- [ ] Set up automated emails

**Thursday: Social Media Content**
- [ ] Create 50 Twitter posts
- [ ] Create 20 LinkedIn posts
- [ ] Design shareable graphics
- [ ] Create video snippets (future)

**Friday: Press Kit**
- [ ] Write boilerplate description
- [ ] Create founder bio
- [ ] Take product screenshots
- [ ] Create logo assets
- [ ] Write FAQs for media

---

#### Week 20: SEO & Marketing Pages

**Monday-Tuesday: SEO Optimization**
- [ ] Keyword research
  - Primary: "congress stock trades", "politician trades"
  - Secondary: "insider trading congress", "senator stock trades"
  - Long-tail: "nancy pelosi stock trades", "best congressional traders"
- [ ] Optimize meta descriptions
- [ ] Add structured data
- [ ] Internal linking strategy
- [ ] Create content cluster

**Wednesday: Landing Pages**
```typescript
// src/app/(marketing)/compare/pelosi-vs-market/page.tsx
// src/app/(marketing)/compare/republicans-vs-democrats/page.tsx
```

- [ ] Create comparison pages (SEO targets)
- [ ] "Pelosi vs Market" page
- [ ] "Republicans vs Democrats" page
- [ ] "Senate vs House" page

**Thursday-Friday: Email List Building**
- [ ] Create lead magnet: "2024 Congress Trade Report"
- [ ] Build landing page
- [ ] Set up email automation
- [ ] Create welcome sequence (5 emails)

---

#### Week 21: Influencer Outreach

**Monday-Tuesday: Influencer Research**
- [ ] Identify 50 finance influencers
  - Twitter: 10K-100K followers
  - YouTube: 50K+ subscribers
  - Newsletters: 5K+ subscribers
- [ ] Create outreach spreadsheet
- [ ] Draft outreach emails

**Wednesday-Thursday: Outreach**
- [ ] Send personalized emails
- [ ] Offer free analysis
- [ ] Request feedback/review
- [ ] Follow up

**Friday: Partnerships**
- [ ] Identify potential partners
  - Trading communities
  - Finance newsletters
  - Educational platforms
- [ ] Draft partnership proposals

**Deliverable:** Marketing assets ready

---

### Sprint 13: Launch Execution (Weeks 22-24)

**Goal:** Successful public launch

#### Week 22: Soft Launch (Private Beta)

**Monday: Beta Invite List**
- [ ] Email list (100 subscribers)
- [ ] Twitter followers
- [ ] Reddit connections
- [ ] Personal network
- [ ] Target: 100 beta users

**Tuesday: Send Invites**
- [ ] Send personalized beta invites
- [ ] Set up feedback form
- [ ] Set up user interview calendar
- [ ] Monitor signups

**Wednesday-Friday: User Testing**
- [ ] Conduct 10 user interviews
- [ ] Collect feedback
- [ ] Monitor analytics
- [ ] Fix critical bugs
- [ ] Iterate on feedback

**Metrics to Track:**
- Signups
- Activation rate
- Time on site
- Feature usage
- Conversion to premium
- Retention (7-day)

---

#### Week 23: Launch Preparation

**Monday: Final Polish**
- [ ] Fix all beta feedback issues
- [ ] Final content review
- [ ] Final SEO check
- [ ] Final performance check
- [ ] Final security review

**Tuesday: Launch Assets**
- [ ] Product Hunt launch page
- [ ] Hacker News post
- [ ] Reddit posts (draft)
- [ ] Twitter announcement thread
- [ ] Press release
- [ ] Email to existing list

**Wednesday: Prepare Launch**
- [ ] Schedule Product Hunt (Tuesday 12:01 AM PST)
- [ ] Prepare social media posts
- [ ] Alert influencers
- [ ] Prepare email blast
- [ ] Set up monitoring

**Thursday-Friday: Contingency**
- [ ] Buffer for last-minute issues
- [ ] Load testing
- [ ] Backup plan if systems fail

---

#### Week 24: Public Launch Week

**Monday: Launch Day**
- [ ] Product Hunt launch (12:01 AM PST)
- [ ] Share on Twitter
- [ ] Share on LinkedIn
- [ ] Email subscribers
- [ ] Monitor analytics
- [ ] Engage with comments
- [ ] Fix any critical issues immediately

**Tuesday: Reddit Launch**
- [ ] Post to r/wallstreetbets
- [ ] Post to r/stocks
- [ ] Post to r/investing
- [ ] Engage with comments
- [ ] Monitor feedback

**Wednesday: Hacker News**
- [ ] Post "Show HN"
- [ ] Engage with comments
- [ ] Monitor traffic
- [ ] Handle technical questions

**Thursday: Press Outreach**
- [ ] Send press release
- [ ] Email finance bloggers
- [ ] Contact finance journalists
- [ ] Follow up with influencers

**Friday: Review & Optimize**
- [ ] Review launch metrics
- [ ] Analyze traffic sources
- [ ] Identify top acquisition channels
- [ ] Plan next week's activities

**Launch Week Goals:**
- 1,000+ visitors
- 100+ signups
- 5+ premium subscribers
- 10+ social shares
- 5+ backlinks
- 1+ press mention

---

## Post-Launch (Weeks 25-26)

### Week 25-26: Iterate & Optimize

**Daily:**
- [ ] Monitor analytics
- [ ] Fix bugs
- [ ] Engage with users
- [ ] Create content
- [ ] Optimize conversion

**Weekly:**
- [ ] Send newsletter
- [ ] Analyze metrics
- [ ] User interviews
- [ ] Feature prioritization
- [ ] Sprint planning

**Metrics Review:**
- Total users
- Active users (DAU/MAU)
- Premium conversions
- Churn rate
- Revenue (MRR)
- Engagement metrics
- SEO rankings
- Social growth

**Iterate Based on Data:**
- Add most requested features
- Fix biggest pain points
- Improve conversion funnel
- Expand content
- Grow user base

---

## Success Metrics by Sprint

| Sprint | Key Metric | Target |
|--------|------------|--------|
| 1-2 | Infrastructure ready | ✓ Deployed |
| 3-5 | Trades collected | 5,000+ |
| 6-7 | API response time | <200ms cached |
| 8-10 | Pages built | 8+ |
| 11 | Lighthouse score | >90 |
| 12 | Blog posts | 10 |
| 13 | Beta users | 100 |
| Launch | Total users | 500+ |
| Launch | Premium | 10+ |

---

## Budget Tracking by Phase

| Phase | Weeks | Infrastructure | Services | Marketing | Legal | Total |
|-------|-------|----------------|----------|-----------|-------|-------|
| 0 | 1-3 | $100 | $50 | $0 | $2,500 | $2,650 |
| 1 | 4-7 | $200 | $100 | $0 | $0 | $300 |
| 2 | 8-11 | $150 | $100 | $50 | $0 | $300 |
| 3 | 12-16 | $250 | $150 | $100 | $0 | $500 |
| 4 | 17-24 | $400 | $200 | $600 | $0 | $1,200 |
| **Total** | **26** | **$1,100** | **$600** | **$750** | **$2,500** | **$4,950** |

**With contingency (20%):** $5,940

**With legal:** $8,440

---

## Risk Mitigation by Sprint

### High-Risk Sprints

**Sprint 3-5 (Data Collection):**
- Risk: Scrapers break
- Mitigation: Robust error handling, monitoring, manual fallback

**Sprint 11 (Testing):**
- Risk: Critical bugs discovered
- Mitigation: Extra week for fixes, reduced scope if needed

**Sprint 13 (Launch):**
- Risk: Low user acquisition
- Mitigation: Pre-launch email list, influencer prep, backup channels

---

## Tools & Resources

### Development Tools
- **IDE:** VS Code
- **API Testing:** Postman, HTTPie
- **Database:** DBeaver, pgAdmin
- **Monitoring:** Grafana, Sentry dashboard
- **Analytics:** PostHog dashboard

### Project Management
- **Tasks:** Linear, GitHub Projects
- **Time Tracking:** Toggl
- **Documentation:** Notion
- **Communication:** Slack (if team >1)

### Learning Resources
- **FastAPI:** https://fastapi.tiangolo.com/
- **Next.js:** https://nextjs.org/docs
- **Scraping:** https://scrapethissite.com/
- **Statistics:** Khan Academy, StatQuest

---

## Weekly Checklist Template

```markdown
## Week X: [Sprint Name]

### Goals
- [ ] Goal 1
- [ ] Goal 2
- [ ] Goal 3

### Monday
- [ ] Task 1
- [ ] Task 2

### Tuesday
- [ ] Task 1
- [ ] Task 2

### Wednesday
- [ ] Task 1
- [ ] Task 2

### Thursday
- [ ] Task 1
- [ ] Task 2

### Friday
- [ ] Task 1
- [ ] Task 2
- [ ] Sprint review
- [ ] Plan next week

### Metrics
- Development hours:
- Bugs fixed:
- Features completed:
- Tests written:
- Cost this week:

### Blockers
- None / [describe]

### Next Week Focus
- [priorities]
```

---

## Remember

**This is a marathon, not a sprint.**

- Take breaks
- Avoid burnout
- Ask for help
- Celebrate small wins
- Learn from failures
- Stay focused on MVP
- Don't add scope
- Ship iteratively

**The goal is a launched product in 6 months, not a perfect product.**

---

**Good luck! 🚀**
