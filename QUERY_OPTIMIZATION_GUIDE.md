# Query Optimization Quick Reference Guide

## What is the N+1 Query Problem?

The N+1 query problem occurs when:
1. You fetch N records from the database (1 query)
2. For each record, you fetch related data (N additional queries)
3. Total: 1 + N queries instead of just 1 or 2

### Bad Example (N+1 Problem)
```python
# Fetches 50 trades (1 query)
trades = await db.execute(select(Trade).limit(50))

# For each trade, fetch politician (50 queries!)
for trade in trades.scalars():
    politician_name = trade.politician.name  # Lazy loading triggers query!
```
**Result**: 51 queries (1 + 50)

### Good Example (Eager Loading)
```python
# Fetches 50 trades with politicians in one query
trades = await db.execute(
    select(Trade)
    .options(joinedload(Trade.politician))  # Eager loading!
    .limit(50)
)

# Access politician data without additional queries
for trade in trades.scalars():
    politician_name = trade.politician.name  # No extra query!
```
**Result**: 1 query

## SQLAlchemy Eager Loading Strategies

### 1. `joinedload()` - SQL JOIN

**Best for**: Many-to-one relationships (Trade → Politician)

```python
from sqlalchemy.orm import joinedload

# Load trades with their politicians
query = select(Trade).options(joinedload(Trade.politician))
```

**SQL Generated**:
```sql
SELECT trades.*, politicians.*
FROM trades
JOIN politicians ON trades.politician_id = politicians.id
```

**Pros**:
- Single SQL query
- Efficient for many-to-one
- Good for small related collections

**Cons**:
- Can create large result sets (cartesian product)
- Not ideal for one-to-many with many children

### 2. `selectinload()` - Separate Query with IN

**Best for**: One-to-many relationships (Politician → Trades)

```python
from sqlalchemy.orm import selectinload

# Load politicians with all their trades
query = select(Politician).options(selectinload(Politician.trades))
```

**SQL Generated**:
```sql
-- Query 1: Load politicians
SELECT * FROM politicians WHERE ...

-- Query 2: Load all trades for those politicians
SELECT * FROM trades WHERE politician_id IN (?, ?, ?, ...)
```

**Pros**:
- Two queries regardless of collection size
- Avoids cartesian product
- Efficient for large collections

**Cons**:
- Two queries instead of one
- Slight overhead for small collections

### 3. Nested Options - Multiple Levels

```python
from sqlalchemy.orm import joinedload, selectinload

# Load trades with politicians and their other trades
query = select(Trade).options(
    joinedload(Trade.politician).selectinload(Politician.trades)
)
```

## Common Patterns in the Quant Platform

### Pattern 1: Loading Trades with Politician Info

```python
from sqlalchemy.orm import joinedload
from app.models import Trade

# ✅ GOOD: Eager load politician
trades = await db.execute(
    select(Trade)
    .options(joinedload(Trade.politician))
    .limit(50)
)

# Access politician data without N+1
for trade in trades.scalars():
    print(f"{trade.ticker} by {trade.politician.name}")
```

### Pattern 2: Loading Politicians with Trades

```python
from sqlalchemy.orm import selectinload
from app.models import Politician

# ✅ GOOD: Eager load trades collection
politicians = await db.execute(
    select(Politician)
    .options(selectinload(Politician.trades))
    .limit(10)
)

# Access trades without N+1
for politician in politicians.scalars():
    print(f"{politician.name}: {len(politician.trades)} trades")
```

### Pattern 3: Complex Queries with Joins

```python
from sqlalchemy.orm import joinedload

# ✅ GOOD: Join and eager load
recent_trades = await db.execute(
    select(Trade)
    .join(Politician)
    .where(Politician.party == 'Democrat')
    .options(joinedload(Trade.politician))
    .order_by(Trade.transaction_date.desc())
    .limit(20)
)
```

### Pattern 4: Aggregation Queries (No Eager Loading Needed)

```python
from sqlalchemy import func

# ✅ GOOD: No eager loading needed for aggregations
trade_counts = await db.execute(
    select(
        Politician.name,
        func.count(Trade.id).label('trade_count')
    )
    .join(Trade)
    .group_by(Politician.id, Politician.name)
)
# No N+1 issue - we're only selecting aggregated data
```

## Using the Query Profiler Decorators

### Decorator 1: Log Slow Queries

```python
from app.core.query_profiler import log_slow_queries

@router.get("/trades")
@log_slow_queries(threshold_ms=100.0)
async def list_trades(db: AsyncSession = Depends(get_db)):
    """Will log warning if endpoint takes > 100ms"""
    result = await db.execute(
        select(Trade).options(joinedload(Trade.politician))
    )
    return result.scalars().all()
```

**Output when slow**:
```
WARNING: Slow endpoint: list_trades took 250.5ms (threshold: 100ms)
```

### Decorator 2: Detect N+1 Problems

```python
from app.core.query_profiler import detect_n_plus_one

@router.get("/politicians-with-trades")
@detect_n_plus_one
async def get_politicians_with_trades(db: AsyncSession = Depends(get_db)):
    """Will warn if too many queries are executed"""
    politicians = await db.execute(
        select(Politician).options(selectinload(Politician.trades))
    )
    return politicians.scalars().all()
```

**Output when N+1 detected**:
```
WARNING: Potential N+1 detected in get_politicians_with_trades: 51 queries executed
HINT: Consider using joinedload() or selectinload() for relationships
```

### Decorator 3: Combine Both

```python
from app.core.query_profiler import log_slow_queries, detect_n_plus_one

@router.get("/analytics/trading-network")
@log_slow_queries(threshold_ms=200.0)
@detect_n_plus_one
async def analyze_trading_network(
    min_trades: int = 50,
    db: AsyncSession = Depends(get_db)
):
    """Monitor both speed and query count"""
    politicians = await db.execute(
        select(Politician)
        .join(Trade)
        .group_by(Politician.id)
        .having(func.count(Trade.id) >= min_trades)
        .options(selectinload(Politician.trades))
    )
    return politicians.scalars().all()
```

## Decision Tree: Which Eager Loading Strategy?

```
┌─────────────────────────────────────┐
│ Need to load related data?          │
└──────────────┬──────────────────────┘
               │
               ├── Many-to-One (Trade → Politician)
               │   └─→ Use joinedload()
               │       select(Trade).options(joinedload(Trade.politician))
               │
               ├── One-to-Many (Politician → Trades)
               │   │
               │   ├── Small collection (<20 items)
               │   │   └─→ Use joinedload()
               │   │
               │   └── Large collection (>20 items)
               │       └─→ Use selectinload()
               │           select(Politician).options(selectinload(Politician.trades))
               │
               └── Aggregation query (count, sum, avg)
                   └─→ No eager loading needed
                       Aggregations don't access object relationships
```

## Common Mistakes to Avoid

### ❌ Mistake 1: Forgetting Eager Loading
```python
# BAD: Will cause N+1
trades = await db.execute(select(Trade).limit(50))
for trade in trades.scalars():
    print(trade.politician.name)  # 50 additional queries!
```

### ✅ Fix 1: Add Eager Loading
```python
# GOOD: Single query
trades = await db.execute(
    select(Trade)
    .options(joinedload(Trade.politician))
    .limit(50)
)
for trade in trades.scalars():
    print(trade.politician.name)  # No additional queries!
```

### ❌ Mistake 2: Using joinedload() for Large Collections
```python
# BAD: Creates huge result set
politicians = await db.execute(
    select(Politician)
    .options(joinedload(Politician.trades))  # Cartesian product!
    .limit(10)
)
# If each politician has 1000 trades, you get 10,000 rows!
```

### ✅ Fix 2: Use selectinload() for Large Collections
```python
# GOOD: Two queries, no cartesian product
politicians = await db.execute(
    select(Politician)
    .options(selectinload(Politician.trades))  # Separate query
    .limit(10)
)
# Query 1: 10 politicians
# Query 2: All their trades (single IN query)
```

### ❌ Mistake 3: Eager Loading Aggregation Results
```python
# BAD: Unnecessary eager loading for aggregation
trade_counts = await db.execute(
    select(Politician, func.count(Trade.id))
    .join(Trade)
    .group_by(Politician.id)
    .options(selectinload(Politician.trades))  # Not needed!
)
```

### ✅ Fix 3: Skip Eager Loading for Aggregations
```python
# GOOD: No eager loading for aggregations
trade_counts = await db.execute(
    select(Politician.name, func.count(Trade.id))
    .join(Trade)
    .group_by(Politician.id, Politician.name)
    # No .options() needed - not accessing relationships
)
```

## Testing for N+1 Issues

### Test 1: Enable SQL Logging
```python
import logging

# In development
logging.getLogger('sqlalchemy.engine').setLevel(logging.INFO)

# You'll see all SQL queries in the console
```

### Test 2: Count Queries in Tests
```python
from app.core.query_profiler import detect_n_plus_one

@detect_n_plus_one
async def test_trades_endpoint(client):
    response = await client.get("/api/v1/trades?limit=50")
    assert response.status_code == 200
    # Decorator will warn if > 10 queries executed
```

### Test 3: Profile Endpoint Performance
```python
from app.core.query_profiler import log_slow_queries

@log_slow_queries(threshold_ms=50.0)
async def test_trades_performance(client):
    response = await client.get("/api/v1/trades?limit=100")
    assert response.status_code == 200
    # Decorator will warn if > 50ms
```

## Performance Benchmarks

### Example: Fetching 50 Trades with Politicians

| Method | Queries | Time | Notes |
|--------|---------|------|-------|
| No eager loading (N+1) | 51 | 110ms | ❌ Inefficient |
| joinedload() | 1 | 15ms | ✅ Optimal |
| selectinload() | 2 | 18ms | ✅ Good alternative |

### Example: Fetching 10 Politicians with 100 Trades Each

| Method | Queries | Time | Notes |
|--------|---------|------|-------|
| No eager loading (N+1) | 11 | 80ms | ❌ Inefficient |
| joinedload() | 1 | 120ms | ⚠️ Cartesian product (10×100 rows) |
| selectinload() | 2 | 25ms | ✅ Optimal |

## Cheat Sheet

### Import Statements
```python
from sqlalchemy.orm import joinedload, selectinload
from app.core.query_profiler import log_slow_queries, detect_n_plus_one
```

### Quick Copy-Paste Templates

#### Many-to-One (Trade → Politician)
```python
trades = await db.execute(
    select(Trade)
    .options(joinedload(Trade.politician))
    .limit(50)
)
```

#### One-to-Many (Politician → Trades)
```python
politicians = await db.execute(
    select(Politician)
    .options(selectinload(Politician.trades))
    .limit(10)
)
```

#### With Decorators
```python
@router.get("/endpoint")
@log_slow_queries(threshold_ms=100.0)
@detect_n_plus_one
async def my_endpoint(db: AsyncSession = Depends(get_db)):
    result = await db.execute(query)
    return result.scalars().all()
```

## Additional Resources

- SQLAlchemy Relationship Loading: https://docs.sqlalchemy.org/en/20/orm/loading_relationships.html
- Query Profiler Source: `/quant/backend/app/core/query_profiler.py`
- N+1 Fixes Report: `/N_PLUS_ONE_FIXES_REPORT.md`
- Test Script: `/test_n_plus_one_fixes.py`

## Summary

✅ **Always** use eager loading when accessing relationships
✅ **Use** `joinedload()` for many-to-one relationships
✅ **Use** `selectinload()` for one-to-many relationships
✅ **Skip** eager loading for aggregation queries
✅ **Test** with decorators: `@log_slow_queries` and `@detect_n_plus_one`
✅ **Monitor** query counts in development with SQL logging

🎯 **Goal**: Keep query count constant regardless of result set size!
