"""Query optimization utilities for database operations.

Provides tools for:
- Eager loading to prevent N+1 queries
- Query result caching
- Pagination optimization
- Query performance monitoring
"""

from typing import TypeVar, Generic, Any, Sequence
from datetime import datetime, timezone
import functools
import time

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload, joinedload
from pydantic import BaseModel

from app.core.logging import get_logger
from app.core.cache import cache_manager

logger = get_logger(__name__)

T = TypeVar("T")


class PaginatedResult(BaseModel, Generic[T]):
    """Paginated query result."""

    items: list[Any]
    total: int
    skip: int
    limit: int
    has_more: bool
    page: int = 1
    pages: int = 1


async def paginate(
    db: AsyncSession,
    query,
    skip: int = 0,
    limit: int = 20,
    max_limit: int = 100,
) -> PaginatedResult:
    """
    Paginate a SQLAlchemy query efficiently.

    Uses a single count query and applies pagination.

    Args:
        db: Database session
        query: SQLAlchemy select query
        skip: Number of records to skip
        limit: Maximum records to return
        max_limit: Maximum allowed limit

    Returns:
        PaginatedResult with items and metadata
    """
    # Enforce maximum limit
    limit = min(limit, max_limit)

    # Get total count
    count_query = select(func.count()).select_from(query.subquery())
    total_result = await db.execute(count_query)
    total = total_result.scalar() or 0

    # Apply pagination
    paginated_query = query.offset(skip).limit(limit)
    result = await db.execute(paginated_query)
    items = list(result.scalars().all())

    # Calculate pagination metadata
    has_more = (skip + len(items)) < total
    page = (skip // limit) + 1 if limit > 0 else 1
    pages = (total + limit - 1) // limit if limit > 0 else 1

    return PaginatedResult(
        items=items,
        total=total,
        skip=skip,
        limit=limit,
        has_more=has_more,
        page=page,
        pages=pages,
    )


def with_eager_loading(query, *relationships):
    """
    Add eager loading for relationships to prevent N+1 queries.

    Args:
        query: SQLAlchemy query
        relationships: Relationship attributes to eager load

    Returns:
        Query with eager loading options
    """
    for rel in relationships:
        query = query.options(selectinload(rel))
    return query


def with_joined_loading(query, *relationships):
    """
    Add joined loading for relationships (single query with JOIN).

    Use for one-to-one or small result sets.

    Args:
        query: SQLAlchemy query
        relationships: Relationship attributes to join load

    Returns:
        Query with joined loading options
    """
    for rel in relationships:
        query = query.options(joinedload(rel))
    return query


class QueryTimer:
    """Context manager for timing queries."""

    def __init__(self, query_name: str, slow_threshold_ms: float = 100):
        """
        Initialize query timer.

        Args:
            query_name: Name for logging
            slow_threshold_ms: Threshold for slow query warning
        """
        self.query_name = query_name
        self.slow_threshold_ms = slow_threshold_ms
        self.start_time = None
        self.end_time = None

    def __enter__(self):
        self.start_time = time.perf_counter()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.end_time = time.perf_counter()
        duration_ms = (self.end_time - self.start_time) * 1000

        if duration_ms > self.slow_threshold_ms:
            logger.warning(
                f"Slow query detected: {self.query_name} took {duration_ms:.2f}ms"
            )
        else:
            logger.debug(f"Query {self.query_name} completed in {duration_ms:.2f}ms")

    @property
    def duration_ms(self) -> float:
        """Get query duration in milliseconds."""
        if self.start_time and self.end_time:
            return (self.end_time - self.start_time) * 1000
        return 0


async def cached_query(
    cache_key: str,
    query_func,
    ttl_seconds: int = 300,
    skip_cache: bool = False,
):
    """
    Execute a query with caching.

    Args:
        cache_key: Unique cache key
        query_func: Async function that executes the query
        ttl_seconds: Cache TTL in seconds
        skip_cache: Skip cache and execute query directly

    Returns:
        Query result (from cache or fresh)
    """
    if skip_cache or not cache_manager.enabled:
        return await query_func()

    # Try cache first
    cached = await cache_manager.get(cache_key)
    if cached is not None:
        logger.debug(f"Cache hit for {cache_key}")
        return cached

    # Execute query
    logger.debug(f"Cache miss for {cache_key}")
    result = await query_func()

    # Cache result
    await cache_manager.set(cache_key, result, ttl=ttl_seconds)

    return result


def build_cache_key(*args, **kwargs) -> str:
    """
    Build a cache key from arguments.

    Args:
        *args: Positional arguments
        **kwargs: Keyword arguments

    Returns:
        Cache key string
    """
    parts = [str(arg) for arg in args]
    parts.extend(f"{k}={v}" for k, v in sorted(kwargs.items()))
    return ":".join(parts)


class QueryOptimizer:
    """
    Query optimizer for complex queries.

    Provides methods for optimizing database queries:
    - Batching
    - Chunked processing
    - Connection pooling hints
    """

    @staticmethod
    async def batch_load(
        db: AsyncSession,
        model,
        ids: list,
        id_field: str = "id",
        batch_size: int = 100,
    ) -> dict:
        """
        Batch load records by IDs to prevent N+1 queries.

        Args:
            db: Database session
            model: SQLAlchemy model class
            ids: List of IDs to load
            id_field: Name of ID field
            batch_size: Batch size for loading

        Returns:
            Dict mapping ID to record
        """
        if not ids:
            return {}

        results = {}
        id_attr = getattr(model, id_field)

        for i in range(0, len(ids), batch_size):
            batch_ids = ids[i:i + batch_size]
            query = select(model).where(id_attr.in_(batch_ids))
            result = await db.execute(query)

            for record in result.scalars():
                results[getattr(record, id_field)] = record

        return results

    @staticmethod
    async def chunked_process(
        db: AsyncSession,
        query,
        process_func,
        chunk_size: int = 1000,
    ):
        """
        Process large result sets in chunks.

        Args:
            db: Database session
            query: SQLAlchemy query
            process_func: Async function to process each chunk
            chunk_size: Size of each chunk

        Yields:
            Results from process_func for each chunk
        """
        offset = 0

        while True:
            chunk_query = query.offset(offset).limit(chunk_size)
            result = await db.execute(chunk_query)
            items = list(result.scalars().all())

            if not items:
                break

            yield await process_func(items)
            offset += chunk_size

            # Avoid holding too many objects in memory
            await db.flush()


# Performance monitoring decorator
def monitor_query(name: str = None, slow_threshold_ms: float = 100):
    """
    Decorator to monitor query performance.

    Args:
        name: Query name for logging (defaults to function name)
        slow_threshold_ms: Threshold for slow query warning
    """
    def decorator(func):
        query_name = name or func.__name__

        @functools.wraps(func)
        async def wrapper(*args, **kwargs):
            with QueryTimer(query_name, slow_threshold_ms) as timer:
                result = await func(*args, **kwargs)
            return result

        return wrapper
    return decorator
