"""
Performance Optimization Module
Provides query optimization, caching strategies, and performance monitoring
"""

import time
import hashlib
import json
from typing import Any, Optional, Callable, Dict, List
from functools import wraps
import asyncio
from datetime import datetime, timedelta

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload, joinedload

from app.core.cache import cache_service
from app.core.logging import get_logger
from app.core.monitoring import monitoring_service

logger = get_logger(__name__)


class QueryOptimizer:
    """SQL query optimization utilities"""

    @staticmethod
    def add_eager_loading(query, *relationships):
        """Add eager loading for relationships"""
        for rel in relationships:
            query = query.options(selectinload(rel))
        return query

    @staticmethod
    def add_joined_loading(query, *relationships):
        """Add joined loading for relationships"""
        for rel in relationships:
            query = query.options(joinedload(rel))
        return query

    @staticmethod
    def add_pagination(query, page: int = 1, page_size: int = 100):
        """Add pagination to query"""
        offset = (page - 1) * page_size
        return query.offset(offset).limit(page_size)

    @staticmethod
    async def count_query(db: AsyncSession, query):
        """Get count for a query efficiently"""
        count_query = select(func.count()).select_from(query.subquery())
        result = await db.execute(count_query)
        return result.scalar()


class CachingStrategy:
    """Advanced caching strategies"""

    @staticmethod
    def generate_cache_key(prefix: str, **kwargs) -> str:
        """Generate cache key from parameters"""
        # Sort kwargs for consistent key generation
        sorted_kwargs = sorted(kwargs.items())
        key_data = f"{prefix}:{json.dumps(sorted_kwargs, sort_keys=True)}"
        # Use hash for long keys
        if len(key_data) > 200:
            key_hash = hashlib.md5(key_data.encode()).hexdigest()
            return f"{prefix}:{key_hash}"
        return key_data

    @staticmethod
    async def get_or_compute(
        key: str,
        compute_func: Callable,
        ttl: int = 3600,
        force_refresh: bool = False
    ) -> Any:
        """
        Get from cache or compute and cache
        """
        # Try cache first
        if not force_refresh:
            cached = await cache_service.get(key)
            if cached is not None:
                monitoring_service.track_cache_hit()
                return cached

        # Cache miss - compute value
        monitoring_service.track_cache_miss()

        # Handle both sync and async functions
        if asyncio.iscoroutinefunction(compute_func):
            value = await compute_func()
        else:
            value = compute_func()

        # Cache the result
        await cache_service.set(key, value, ttl=ttl)

        return value

    @staticmethod
    async def invalidate_pattern(pattern: str):
        """Invalidate cache keys matching pattern"""
        await cache_service.delete_pattern(pattern)


class PerformanceMonitor:
    """Performance monitoring and profiling"""

    def __init__(self):
        self.slow_query_threshold = 1.0  # seconds
        self.slow_request_threshold = 2.0  # seconds

    async def log_slow_query(self, query_name: str, duration: float, params: Dict = None):
        """Log slow database query"""
        if duration > self.slow_query_threshold:
            logger.warning(
                f"Slow query detected: {query_name}",
                extra={
                    'query_name': query_name,
                    'duration_seconds': duration,
                    'params': params
                }
            )

            # Send alert for very slow queries
            if duration > self.slow_query_threshold * 3:
                from app.core.alerts import alerting, AlertSeverity
                await alerting.send_alert(
                    title="Very Slow Query",
                    message=f"{query_name} took {duration:.2f}s",
                    severity=AlertSeverity.WARNING,
                    metadata={'query': query_name, 'duration': duration}
                )

    async def log_slow_request(self, endpoint: str, duration: float):
        """Log slow API request"""
        if duration > self.slow_request_threshold:
            logger.warning(
                f"Slow request detected: {endpoint}",
                extra={
                    'endpoint': endpoint,
                    'duration_seconds': duration
                }
            )

            # Send alert for very slow requests
            if duration > self.slow_request_threshold * 2:
                from app.core.alerts import alerting
                await alerting.alert_slow_response(endpoint, duration)


performance_monitor = PerformanceMonitor()


def cached(ttl: int = 3600, key_prefix: str = "cached"):
    """
    Decorator for caching function results

    Args:
        ttl: Time to live in seconds
        key_prefix: Prefix for cache key
    """
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # Generate cache key from function name and arguments
            cache_key = CachingStrategy.generate_cache_key(
                f"{key_prefix}:{func.__name__}",
                args=str(args),
                kwargs=kwargs
            )

            # Try to get from cache
            result = await CachingStrategy.get_or_compute(
                cache_key,
                lambda: func(*args, **kwargs),
                ttl=ttl
            )

            return result

        return wrapper
    return decorator


def timed(operation_name: str = None):
    """
    Decorator to time function execution
    """
    def decorator(func):
        op_name = operation_name or func.__name__

        @wraps(func)
        async def async_wrapper(*args, **kwargs):
            start_time = time.time()
            try:
                result = await func(*args, **kwargs)
                duration = time.time() - start_time

                logger.info(f"{op_name} completed in {duration:.3f}s")

                # Check for slow operations
                if duration > 1.0:
                    await performance_monitor.log_slow_query(op_name, duration)

                return result
            except Exception as e:
                duration = time.time() - start_time
                logger.error(f"{op_name} failed after {duration:.3f}s: {e}")
                raise

        @wraps(func)
        def sync_wrapper(*args, **kwargs):
            start_time = time.time()
            try:
                result = func(*args, **kwargs)
                duration = time.time() - start_time

                logger.info(f"{op_name} completed in {duration:.3f}s")

                return result
            except Exception as e:
                duration = time.time() - start_time
                logger.error(f"{op_name} failed after {duration:.3f}s: {e}")
                raise

        if asyncio.iscoroutinefunction(func):
            return async_wrapper
        else:
            return sync_wrapper

    return decorator


class BatchProcessor:
    """Batch processing utilities for performance"""

    @staticmethod
    async def process_in_batches(
        items: List[Any],
        process_func: Callable,
        batch_size: int = 100
    ) -> List[Any]:
        """
        Process items in batches
        """
        results = []

        for i in range(0, len(items), batch_size):
            batch = items[i:i + batch_size]

            if asyncio.iscoroutinefunction(process_func):
                batch_results = await process_func(batch)
            else:
                batch_results = process_func(batch)

            results.extend(batch_results)

        return results

    @staticmethod
    async def parallel_process(
        items: List[Any],
        process_func: Callable,
        max_concurrent: int = 10
    ) -> List[Any]:
        """
        Process items in parallel with concurrency limit
        """
        semaphore = asyncio.Semaphore(max_concurrent)

        async def process_with_semaphore(item):
            async with semaphore:
                if asyncio.iscoroutinefunction(process_func):
                    return await process_func(item)
                else:
                    return process_func(item)

        tasks = [process_with_semaphore(item) for item in items]
        return await asyncio.gather(*tasks)


class ConnectionPoolMonitor:
    """Monitor database connection pool"""

    def __init__(self, engine):
        self.engine = engine

    def get_pool_status(self) -> Dict[str, Any]:
        """Get connection pool status"""
        pool = self.engine.pool

        return {
            'size': pool.size(),
            'checked_in': pool.checkedin(),
            'checked_out': pool.checkedout(),
            'overflow': pool.overflow(),
            'max_overflow': pool._max_overflow,
            'pool_size': pool._pool.maxsize if hasattr(pool, '_pool') else None,
            'utilization_percent': (pool.checkedout() / pool.size() * 100) if pool.size() > 0 else 0
        }

    async def check_pool_health(self) -> bool:
        """Check if pool is healthy"""
        status = self.get_pool_status()

        # Alert if pool is heavily utilized
        if status['utilization_percent'] > 80:
            logger.warning(
                "High database connection pool utilization",
                extra=status
            )
            return False

        return True


# Performance optimization helpers
async def optimize_bulk_insert(db: AsyncSession, model_class, records: List[Dict]):
    """Optimized bulk insert"""
    if not records:
        return []

    # Use bulk insert for better performance
    instances = [model_class(**record) for record in records]
    db.add_all(instances)
    await db.flush()

    return instances


async def optimize_bulk_update(db: AsyncSession, model_class, updates: List[Dict]):
    """Optimized bulk update"""
    if not updates:
        return

    # Use bulk update mapping for better performance
    await db.execute(
        model_class.__table__.update(),
        updates
    )
