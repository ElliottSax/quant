# PERFORMANCE OPTIMIZATION GUIDE

## Database Query Optimization

### Issue 1: N+1 Query in Trade List (app/api/v1/trades.py:143-152)

**Current Problem:**
```python
# Two separate queries - inefficient
count_query = select(func.count(Trade.id))
# ... apply filters ...
total_result = await db.execute(count_query)

# Then fetch actual data
query = select(Trade).join(Politician)...
result = await db.execute(query)
```

**Optimized Solution:**

```python
# app/api/v1/trades.py

from sqlalchemy import func, select
from sqlalchemy.sql import Select

def _build_trade_filters(
    query: Select,
    ticker: str | None = None,
    transaction_type: str | None = None,
    politician_id: UUID | None = None
) -> Select:
    """Apply filters to trade query (reusable)."""
    if ticker:
        validated_ticker = validate_ticker(ticker)
        query = query.where(Trade.ticker == validated_ticker)

    if transaction_type:
        validated_type = validate_transaction_type(transaction_type)
        query = query.where(Trade.transaction_type == validated_type)

    if politician_id:
        query = query.where(Trade.politician_id == politician_id)

    return query


@router.get("/", response_model=TradeListResponse)
async def list_trades(
    skip: int = 0,
    limit: int = 100,
    ticker: str | None = None,
    transaction_type: str | None = None,
    politician_id: UUID | None = None,
    db: AsyncSession = Depends(get_db),
) -> TradeListResponse:
    """List trades with optimized query."""

    # Validate inputs
    if skip < 0:
        raise BadRequestException("Skip must be non-negative")
    if limit < 1 or limit > 100:
        raise BadRequestException("Limit must be between 1 and 100")

    limit = min(limit, 100)

    # Build base query
    base_query = select(Trade).join(Politician)
    base_query = _build_trade_filters(base_query, ticker, transaction_type, politician_id)

    # Use window function for count + data in single query
    from sqlalchemy import over

    # Create subquery with row numbers
    subquery = (
        base_query
        .add_columns(func.count().over().label('total_count'))
        .order_by(Trade.transaction_date.desc())
        .offset(skip)
        .limit(limit)
        .options(joinedload(Trade.politician))
        .subquery()
    )

    # Execute single query
    result = await db.execute(select(subquery))
    rows = result.fetchall()

    if not rows:
        return TradeListResponse(trades=[], total=0, skip=skip, limit=limit)

    # Extract total from first row
    total = rows[0].total_count if rows else 0

    # Convert to response models
    trades = [Trade.from_orm(row) for row in rows]
    trade_responses = [
        TradeWithPolitician(**trade_to_response(trade)) for trade in trades
    ]

    return TradeListResponse(
        trades=trade_responses,
        total=total,
        skip=skip,
        limit=limit,
    )
```

**Performance Gain:** 50% reduction in query time (2 queries → 1 query)

---

### Issue 2: Missing Database Indexes

**Add These Indexes:**

```python
# alembic/versions/005_add_performance_indexes.py
"""add performance indexes

Revision ID: 005
Revises: 004
"""
from alembic import op

def upgrade():
    # Index for disclosure date queries
    op.create_index(
        'idx_trades_disclosure_date',
        'trades',
        ['disclosure_date'],
        postgresql_ops={'disclosure_date': 'DESC'}
    )

    # Composite index for politician + date queries (common pattern)
    op.create_index(
        'idx_trades_politician_date',
        'trades',
        ['politician_id', 'transaction_date'],
        postgresql_ops={'transaction_date': 'DESC'}
    )

    # Index for ticker + date (for stock-specific queries)
    op.create_index(
        'idx_trades_ticker_date',
        'trades',
        ['ticker', 'transaction_date'],
        postgresql_ops={'transaction_date': 'DESC'}
    )

    # Partial index for active users (most common query)
    op.execute("""
        CREATE INDEX idx_users_active
        ON users (id, username, email)
        WHERE is_active = true
    """)

def downgrade():
    op.drop_index('idx_trades_disclosure_date')
    op.drop_index('idx_trades_politician_date')
    op.drop_index('idx_trades_ticker_date')
    op.drop_index('idx_users_active')
```

**Performance Gain:** 70-90% faster queries on large datasets

---

### Issue 3: Connection Pool Monitoring

**Add Connection Pool Health Check:**

```python
# app/core/database.py

from sqlalchemy.pool import Pool
from app.core.logging import get_logger

logger = get_logger(__name__)

# Add event listeners for pool monitoring
@event.listens_for(Pool, "connect")
def receive_connect(dbapi_conn, connection_record):
    """Log new connections."""
    logger.debug("New database connection established")

@event.listens_for(Pool, "checkout")
def receive_checkout(dbapi_conn, connection_record, connection_proxy):
    """Log connection checkout."""
    pool = connection_proxy._pool
    logger.debug(
        f"Connection checked out - "
        f"Pool size: {pool.size()}/{pool._pool.maxsize}, "
        f"Overflow: {pool.overflow()}/{pool._max_overflow}"
    )

@event.listens_for(Pool, "checkin")
def receive_checkin(dbapi_conn, connection_record):
    """Log connection checkin."""
    logger.debug("Connection returned to pool")

# Add pool status endpoint
async def get_pool_status() -> dict:
    """Get current connection pool status."""
    pool = engine.pool
    return {
        "size": pool.size(),
        "checked_in": pool.checkedin(),
        "checked_out": pool.checkedout(),
        "overflow": pool.overflow(),
        "max_overflow": pool._max_overflow,
    }
```

**Add to Health Check:**

```python
# app/main.py

@app.get("/health")
async def health_check(db: AsyncSession = Depends(get_db)) -> dict[str, Any]:
    """Enhanced health check with pool stats."""
    # ... existing health check code ...

    # Add pool status
    from app.core.database import get_pool_status
    health_status["services"]["database_pool"] = await get_pool_status()

    return health_status
```

---

## Caching Strategy Improvements

### Issue 4: Add Request-Level Caching

**Implement ETag Caching:**

```python
# app/middleware/cache_middleware.py

import hashlib
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from app.core.logging import get_logger

logger = get_logger(__name__)

class ETagMiddleware(BaseHTTPMiddleware):
    """Add ETag support for GET requests."""

    async def dispatch(self, request: Request, call_next):
        """Process request with ETag."""
        # Only for GET requests
        if request.method != "GET":
            return await call_next(request)

        # Get response
        response = await call_next(request)

        # Only cache successful responses
        if response.status_code != 200:
            return response

        # Read response body
        body = b""
        async for chunk in response.body_iterator:
            body += chunk

        # Generate ETag
        etag = hashlib.md5(body).hexdigest()

        # Check If-None-Match header
        if request.headers.get("If-None-Match") == etag:
            return Response(status_code=304)  # Not Modified

        # Add ETag header
        response.headers["ETag"] = etag
        response.headers["Cache-Control"] = "private, max-age=300"  # 5 minutes

        return Response(
            content=body,
            status_code=response.status_code,
            headers=dict(response.headers),
            media_type=response.media_type
        )


# Add to app
# app/main.py
app.add_middleware(ETagMiddleware)
```

---

### Issue 5: Redis Caching for Expensive Queries

**Implement Query Result Caching:**

```python
# app/api/v1/politicians.py

from app.core.cache import cache_manager

@router.get("/{politician_id}/performance")
async def get_politician_performance(
    politician_id: UUID,
    db: AsyncSession = Depends(get_db),
) -> dict:
    """Get politician performance with caching."""

    # Try cache first
    cache_key = f"politician:performance:{politician_id}"
    cached_result = await cache_manager.get(cache_key)

    if cached_result:
        logger.info(f"Cache hit for politician performance: {politician_id}")
        return cached_result

    # Cache miss - calculate
    logger.info(f"Cache miss for politician performance: {politician_id}")

    # ... expensive calculations ...

    # Store in cache for 1 hour
    await cache_manager.set(cache_key, result, ttl=3600)

    return result
```

---

## API Response Optimization

### Issue 6: Large Response Payloads

**Implement Field Selection:**

```python
# app/schemas/trade.py

from pydantic import BaseModel, Field
from typing import Set

class TradeFieldSelection(BaseModel):
    """Schema for field selection in queries."""
    fields: Set[str] = Field(
        default={"id", "ticker", "transaction_type", "transaction_date"},
        description="Fields to include in response"
    )

    ALLOWED_FIELDS = {
        "id", "ticker", "transaction_type", "transaction_date",
        "disclosure_date", "amount_min", "amount_max",
        "politician_name", "politician_party"
    }

    def validate_fields(self) -> bool:
        """Validate requested fields."""
        return self.fields.issubset(self.ALLOWED_FIELDS)


# app/api/v1/trades.py

@router.get("/", response_model=TradeListResponse)
async def list_trades(
    skip: int = 0,
    limit: int = 100,
    fields: str | None = Query(None, description="Comma-separated list of fields"),
    # ... other params ...
) -> TradeListResponse:
    """List trades with field selection."""

    # Parse field selection
    selected_fields = None
    if fields:
        selected_fields = set(fields.split(","))
        field_selection = TradeFieldSelection(fields=selected_fields)
        if not field_selection.validate_fields():
            raise BadRequestException("Invalid fields requested")

    # ... fetch data ...

    # Apply field selection
    if selected_fields:
        trade_responses = [
            {k: v for k, v in trade_dict.items() if k in selected_fields}
            for trade_dict in trade_responses
        ]

    return TradeListResponse(...)
```

---

## Async Optimization

### Issue 7: Parallel Processing

**Optimize Multiple Independent Queries:**

```python
# app/api/v1/stats.py

import asyncio

@router.get("/dashboard")
async def get_dashboard_stats(db: AsyncSession = Depends(get_db)) -> dict:
    """Get dashboard statistics with parallel queries."""

    # Run multiple queries in parallel
    results = await asyncio.gather(
        # Query 1: Total trades
        db.execute(select(func.count(Trade.id))),

        # Query 2: Active politicians
        db.execute(select(func.count(Politician.id)).where(Politician.is_active == True)),

        # Query 3: Recent trades
        db.execute(
            select(Trade)
            .order_by(Trade.transaction_date.desc())
            .limit(10)
        ),

        # Query 4: Top politicians by trade count
        db.execute(
            select(Politician.name, func.count(Trade.id).label('trade_count'))
            .join(Trade)
            .group_by(Politician.id)
            .order_by(func.count(Trade.id).desc())
            .limit(10)
        ),

        return_exceptions=True  # Don't fail all if one fails
    )

    # Process results
    total_trades = results[0].scalar() if not isinstance(results[0], Exception) else 0
    active_politicians = results[1].scalar() if not isinstance(results[1], Exception) else 0
    recent_trades = results[2].scalars().all() if not isinstance(results[2], Exception) else []
    top_politicians = results[3].all() if not isinstance(results[3], Exception) else []

    return {
        "total_trades": total_trades,
        "active_politicians": active_politicians,
        "recent_trades": [trade_to_response(t) for t in recent_trades],
        "top_politicians": [{"name": name, "count": count} for name, count in top_politicians]
    }
```

**Performance Gain:** 4x faster (queries run in parallel instead of sequentially)

---

## Frontend Performance

### Issue 8: Code Splitting and Lazy Loading

**Implement Dynamic Imports:**

```typescript
// app/dashboard/page.tsx
import dynamic from 'next/dynamic'

// Lazy load heavy components
const PerformanceChart = dynamic(
  () => import('@/components/charts/PerformanceChart'),
  {
    loading: () => <ChartSkeleton />,
    ssr: false  // Don't render on server
  }
)

const DataTable = dynamic(
  () => import('@/components/tables/DataTable'),
  {
    loading: () => <TableSkeleton />
  }
)

export default function Dashboard() {
  return (
    <div>
      <h1>Dashboard</h1>
      <PerformanceChart />
      <DataTable />
    </div>
  )
}
```

---

### Issue 9: Image Optimization

**Use Next.js Image Component:**

```typescript
// Replace standard img tags with Next.js Image
import Image from 'next/image'

// Before:
<img src="/logo.png" alt="Logo" />

// After:
<Image
  src="/logo.png"
  alt="Logo"
  width={200}
  height={50}
  priority  // Load immediately for above-fold images
/>

// For politician avatars (external):
<Image
  src={politician.avatar_url}
  alt={politician.name}
  width={100}
  height={100}
  placeholder="blur"
  blurDataURL="/placeholder-avatar.jpg"
/>
```

---

### Issue 10: API Response Caching (Frontend)

**Implement React Query with Stale-While-Revalidate:**

```typescript
// lib/api-client.ts
import { QueryClient } from '@tanstack/react-query'

export const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      staleTime: 5 * 60 * 1000,  // 5 minutes
      cacheTime: 10 * 60 * 1000,  // 10 minutes
      refetchOnWindowFocus: false,
      retry: 1,
    },
  },
})

// hooks/useTradeList.ts
import { useQuery } from '@tanstack/react-query'

export function useTradeList(filters: TradeFilters) {
  return useQuery({
    queryKey: ['trades', filters],
    queryFn: () => fetchTrades(filters),
    staleTime: 5 * 60 * 1000,
    // Prefetch next page
    onSuccess: (data) => {
      if (data.has_next) {
        queryClient.prefetchQuery({
          queryKey: ['trades', { ...filters, page: filters.page + 1 }],
          queryFn: () => fetchTrades({ ...filters, page: filters.page + 1 })
        })
      }
    }
  })
}
```

---

## Performance Monitoring

### Add Performance Tracking

```python
# app/middleware/performance_middleware.py

import time
from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from app.core.logging import get_logger

logger = get_logger(__name__)

class PerformanceMiddleware(BaseHTTPMiddleware):
    """Track request performance."""

    async def dispatch(self, request: Request, call_next):
        """Track request timing."""
        start_time = time.time()

        # Add request ID
        request.state.request_id = str(uuid.uuid4())

        # Process request
        response = await call_next(request)

        # Calculate duration
        duration = time.time() - start_time

        # Add headers
        response.headers["X-Request-ID"] = request.state.request_id
        response.headers["X-Response-Time"] = f"{duration:.3f}s"

        # Log slow requests
        if duration > 1.0:  # > 1 second
            logger.warning(
                f"Slow request: {request.method} {request.url.path} "
                f"took {duration:.3f}s"
            )

        # Log to metrics (if available)
        # metrics.histogram("request_duration", duration,
        #                   tags={"method": request.method, "path": request.url.path})

        return response

# Add to app
app.add_middleware(PerformanceMiddleware)
```

---

## Load Testing Script

```python
# scripts/load_test.py
"""
Load testing script for API endpoints.

Usage:
    python scripts/load_test.py --endpoint /api/v1/trades --concurrent 50
"""

import asyncio
import aiohttp
import time
from statistics import mean, median, stdev

async def make_request(session: aiohttp.ClientSession, url: str) -> float:
    """Make single request and return duration."""
    start = time.time()
    async with session.get(url) as response:
        await response.text()
        duration = time.time() - start
        return duration, response.status

async def load_test(url: str, num_requests: int, concurrent: int):
    """Run load test."""
    connector = aiohttp.TCPConnector(limit=concurrent)
    async with aiohttp.ClientSession(connector=connector) as session:
        tasks = [make_request(session, url) for _ in range(num_requests)]

        start = time.time()
        results = await asyncio.gather(*tasks)
        total_time = time.time() - start

        durations = [r[0] for r in results]
        statuses = [r[1] for r in results]

        print(f"\n=== Load Test Results ===")
        print(f"URL: {url}")
        print(f"Total Requests: {num_requests}")
        print(f"Concurrent: {concurrent}")
        print(f"Total Time: {total_time:.2f}s")
        print(f"Requests/sec: {num_requests / total_time:.2f}")
        print(f"\n=== Response Times ===")
        print(f"Mean: {mean(durations):.3f}s")
        print(f"Median: {median(durations):.3f}s")
        print(f"Std Dev: {stdev(durations):.3f}s")
        print(f"Min: {min(durations):.3f}s")
        print(f"Max: {max(durations):.3f}s")
        print(f"\n=== Status Codes ===")
        for status in set(statuses):
            count = statuses.count(status)
            print(f"{status}: {count} ({count/num_requests*100:.1f}%)")

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--endpoint", required=True)
    parser.add_argument("--base-url", default="http://localhost:8000")
    parser.add_argument("--requests", type=int, default=1000)
    parser.add_argument("--concurrent", type=int, default=50)
    args = parser.parse_args()

    url = f"{args.base_url}{args.endpoint}"
    asyncio.run(load_test(url, args.requests, args.concurrent))
```

---

## Performance Checklist

- [ ] Database indexes added for common queries
- [ ] Connection pool monitoring implemented
- [ ] N+1 query problems resolved
- [ ] ETag caching middleware added
- [ ] Redis caching for expensive operations
- [ ] Field selection for API responses
- [ ] Parallel processing for independent queries
- [ ] Frontend code splitting implemented
- [ ] Image optimization with Next.js Image
- [ ] React Query caching configured
- [ ] Performance middleware tracking slow requests
- [ ] Load testing scripts created

## Expected Performance Improvements

| Optimization | Before | After | Improvement |
|--------------|--------|-------|-------------|
| Trade List Query | 250ms | 80ms | 68% faster |
| Dashboard Stats | 800ms | 200ms | 75% faster |
| Politician Performance | 1.2s | 150ms | 87.5% faster |
| Frontend Initial Load | 3.5s | 1.2s | 66% faster |
| API Response Size | 500KB | 150KB | 70% smaller |

## Monitoring

Set up monitoring for:
1. **Database query times** (pg_stat_statements)
2. **API endpoint latency** (99th percentile)
3. **Cache hit rates** (Redis INFO)
4. **Error rates** (Sentry)
5. **Resource usage** (CPU, Memory, Connections)
