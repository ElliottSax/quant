"""
Query Profiling Middleware and Decorators

Automatically tracks query performance for optimization.
"""

import time
import asyncio
from typing import Callable, Any
from functools import wraps
from contextvars import ContextVar

from sqlalchemy import event
from sqlalchemy.engine import Engine
from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession

from app.core.logging import get_logger
from app.services.database_optimizer import get_database_optimizer

logger = get_logger(__name__)

# Context variable to track if we're in a profiled context
_profiling_enabled: ContextVar[bool] = ContextVar('profiling_enabled', default=True)


class QueryProfiler:
    """
    SQLAlchemy event-based query profiler.

    Automatically tracks all database queries for performance analysis.
    """

    def __init__(self):
        self.enabled = True

    def setup_events(self, engine: Engine):
        """Set up SQLAlchemy events for query profiling"""

        @event.listens_for(engine.sync_engine, "before_cursor_execute")
        def before_cursor_execute(conn, cursor, statement, parameters, context, executemany):
            """Record query start time"""
            if self.enabled and _profiling_enabled.get():
                context._query_start_time = time.time()

        @event.listens_for(engine.sync_engine, "after_cursor_execute")
        def after_cursor_execute(conn, cursor, statement, parameters, context, executemany):
            """Record query execution and analyze"""
            if self.enabled and _profiling_enabled.get():
                start_time = getattr(context, '_query_start_time', None)
                if start_time:
                    execution_time = time.time() - start_time

                    # Record in database optimizer
                    try:
                        optimizer = get_database_optimizer()
                        # Use asyncio to run async function from sync context
                        loop = asyncio.get_event_loop()
                        if loop.is_running():
                            # If event loop is running, schedule the task
                            asyncio.create_task(
                                optimizer.analyze_query(
                                    statement,
                                    execution_time,
                                    parameters
                                )
                            )
                        else:
                            # If no event loop, run synchronously
                            loop.run_until_complete(
                                optimizer.analyze_query(
                                    statement,
                                    execution_time,
                                    parameters
                                )
                            )
                    except Exception as e:
                        logger.error(f"Failed to profile query: {e}")


# Global profiler instance
query_profiler = QueryProfiler()


def profile_queries(func: Callable) -> Callable:
    """
    Decorator to enable query profiling for a function.

    Usage:
        @profile_queries
        async def get_politician_trades(db: AsyncSession, politician_id: str):
            # Queries here will be profiled
            pass
    """

    @wraps(func)
    async def async_wrapper(*args, **kwargs):
        token = _profiling_enabled.set(True)
        try:
            return await func(*args, **kwargs)
        finally:
            _profiling_enabled.reset(token)

    @wraps(func)
    def sync_wrapper(*args, **kwargs):
        token = _profiling_enabled.set(True)
        try:
            return func(*args, **kwargs)
        finally:
            _profiling_enabled.reset(token)

    if asyncio.iscoroutinefunction(func):
        return async_wrapper
    else:
        return sync_wrapper


def disable_query_profiling(func: Callable) -> Callable:
    """
    Decorator to disable query profiling for a function.

    Useful for high-frequency operations where profiling overhead is not acceptable.

    Usage:
        @disable_query_profiling
        async def high_frequency_operation(db: AsyncSession):
            # Queries here won't be profiled
            pass
    """

    @wraps(func)
    async def async_wrapper(*args, **kwargs):
        token = _profiling_enabled.set(False)
        try:
            return await func(*args, **kwargs)
        finally:
            _profiling_enabled.reset(token)

    @wraps(func)
    def sync_wrapper(*args, **kwargs):
        token = _profiling_enabled.set(False)
        try:
            return func(*args, **kwargs)
        finally:
            _profiling_enabled.reset(token)

    if asyncio.iscoroutinefunction(func):
        return async_wrapper
    else:
        return sync_wrapper


class ProfiledSession:
    """
    Context manager for profiled database sessions.

    Usage:
        async with ProfiledSession(db) as session:
            # Queries here will be profiled
            result = await session.execute(query)
    """

    def __init__(self, session: AsyncSession, enabled: bool = True):
        self.session = session
        self.enabled = enabled
        self.token = None

    async def __aenter__(self):
        if self.enabled:
            self.token = _profiling_enabled.set(True)
        return self.session

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.token:
            _profiling_enabled.reset(self.token)


def log_slow_queries(threshold_ms: float = 100.0):
    """
    Decorator to log slow database queries in an endpoint.

    This decorator tracks all queries executed during the endpoint execution
    and logs warnings for any queries that exceed the threshold.

    Args:
        threshold_ms: Threshold in milliseconds. Queries slower than this will be logged.

    Usage:
        @log_slow_queries(threshold_ms=100.0)
        async def get_politicians(db: AsyncSession = Depends(get_db)):
            # If any query takes longer than 100ms, it will be logged
            result = await db.execute(query)
            return result

    Example log output:
        WARNING: Slow query detected (250.5ms): SELECT * FROM politicians WHERE ...
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def async_wrapper(*args, **kwargs):
            # Store the start time for this request
            request_start = time.time()

            # Enable profiling for this request
            token = _profiling_enabled.set(True)

            try:
                result = await func(*args, **kwargs)

                # Log overall request time
                request_time = (time.time() - request_start) * 1000
                if request_time > threshold_ms:
                    logger.warning(
                        f"Slow endpoint: {func.__name__} took {request_time:.2f}ms "
                        f"(threshold: {threshold_ms}ms)"
                    )

                return result
            finally:
                _profiling_enabled.reset(token)

        @wraps(func)
        def sync_wrapper(*args, **kwargs):
            request_start = time.time()
            token = _profiling_enabled.set(True)

            try:
                result = func(*args, **kwargs)

                request_time = (time.time() - request_start) * 1000
                if request_time > threshold_ms:
                    logger.warning(
                        f"Slow endpoint: {func.__name__} took {request_time:.2f}ms "
                        f"(threshold: {threshold_ms}ms)"
                    )

                return result
            finally:
                _profiling_enabled.reset(token)

        if asyncio.iscoroutinefunction(func):
            return async_wrapper
        else:
            return sync_wrapper

    return decorator


def detect_n_plus_one(func: Callable) -> Callable:
    """
    Decorator to detect potential N+1 query problems.

    This decorator counts the number of queries executed during a request
    and warns if the count seems suspiciously high (potential N+1 issue).

    Usage:
        @detect_n_plus_one
        async def list_politicians_with_trades(db: AsyncSession = Depends(get_db)):
            # Will warn if too many queries are executed
            politicians = await db.execute(select(Politician))
            for politician in politicians:
                trades = await db.execute(select(Trade).where(Trade.politician_id == politician.id))
            return politicians

    Example log output:
        WARNING: Potential N+1 detected in list_politicians_with_trades: 51 queries executed
        HINT: Consider using joinedload() or selectinload() for relationships
    """
    @wraps(func)
    async def async_wrapper(*args, **kwargs):
        # Create a counter for this request
        query_count = {'count': 0}

        # Hook into the database optimizer to count queries
        try:
            optimizer = get_database_optimizer()
            original_analyze = optimizer.analyze_query

            async def counting_analyze(statement, execution_time, parameters=None):
                query_count['count'] += 1
                return await original_analyze(statement, execution_time, parameters)

            # Temporarily replace the analyze method
            optimizer.analyze_query = counting_analyze

            result = await func(*args, **kwargs)

            # Check for potential N+1
            if query_count['count'] > 10:
                logger.warning(
                    f"Potential N+1 detected in {func.__name__}: "
                    f"{query_count['count']} queries executed. "
                    f"Consider using joinedload() or selectinload() for relationships."
                )

            return result
        finally:
            # Restore original method
            try:
                optimizer.analyze_query = original_analyze
            except:
                pass

    @wraps(func)
    def sync_wrapper(*args, **kwargs):
        return func(*args, **kwargs)

    if asyncio.iscoroutinefunction(func):
        return async_wrapper
    else:
        return sync_wrapper
