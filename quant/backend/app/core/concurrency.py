"""
Concurrency control utilities for managing expensive operations.

Provides semaphores, circuit breakers, and request queuing to prevent
system overload under high concurrent request loads.
"""

import asyncio
from typing import Optional, Callable, Any
from functools import wraps
from datetime import datetime, timedelta
from enum import Enum

from app.core.logging import get_logger

logger = get_logger(__name__)


class CircuitState(str, Enum):
    """Circuit breaker states"""
    CLOSED = "closed"  # Normal operation
    OPEN = "open"  # Failures detected, requests blocked
    HALF_OPEN = "half_open"  # Testing if service recovered


class CircuitBreaker:
    """
    Circuit breaker pattern implementation.

    Prevents cascading failures by temporarily blocking requests
    when error rate exceeds threshold.
    """

    def __init__(
        self,
        failure_threshold: int = 5,
        timeout: int = 60,
        expected_exception: type = Exception
    ):
        """
        Initialize circuit breaker.

        Args:
            failure_threshold: Number of failures before opening circuit
            timeout: Seconds to wait before trying again (half-open)
            expected_exception: Exception type that counts as failure
        """
        self.failure_threshold = failure_threshold
        self.timeout = timeout
        self.expected_exception = expected_exception

        self.failure_count = 0
        self.last_failure_time: Optional[datetime] = None
        self.state = CircuitState.CLOSED

    def call(self, func: Callable) -> Callable:
        """Decorator to wrap function with circuit breaker"""
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # Check circuit state
            if self.state == CircuitState.OPEN:
                # Check if timeout has passed
                if (
                    self.last_failure_time and
                    datetime.now() - self.last_failure_time > timedelta(seconds=self.timeout)
                ):
                    logger.info(f"Circuit breaker entering HALF_OPEN state: {func.__name__}")
                    self.state = CircuitState.HALF_OPEN
                else:
                    logger.warning(f"Circuit breaker OPEN, blocking request: {func.__name__}")
                    raise Exception(
                        f"Circuit breaker is OPEN for {func.__name__}. "
                        f"Service temporarily unavailable. Try again later."
                    )

            try:
                # Execute function
                result = await func(*args, **kwargs)

                # Success - reset if in half-open
                if self.state == CircuitState.HALF_OPEN:
                    logger.info(f"Circuit breaker closing: {func.__name__}")
                    self.state = CircuitState.CLOSED
                    self.failure_count = 0

                return result

            except self.expected_exception as e:
                # Failure - increment counter
                self.failure_count += 1
                self.last_failure_time = datetime.now()

                logger.error(
                    f"Circuit breaker failure {self.failure_count}/{self.failure_threshold}: "
                    f"{func.__name__} - {e}"
                )

                # Open circuit if threshold reached
                if self.failure_count >= self.failure_threshold:
                    logger.error(f"Circuit breaker OPENING: {func.__name__}")
                    self.state = CircuitState.OPEN

                raise

        return wrapper

    def reset(self):
        """Manually reset circuit breaker"""
        self.state = CircuitState.CLOSED
        self.failure_count = 0
        self.last_failure_time = None
        logger.info("Circuit breaker manually reset")


class RequestSemaphore:
    """
    Semaphore for limiting concurrent expensive operations.

    Prevents system overload by queueing requests when limit is reached.
    """

    def __init__(self, max_concurrent: int = 5, timeout: int = 120):
        """
        Initialize request semaphore.

        Args:
            max_concurrent: Maximum concurrent requests allowed
            timeout: Maximum wait time in queue (seconds)
        """
        self.semaphore = asyncio.Semaphore(max_concurrent)
        self.timeout = timeout
        self.max_concurrent = max_concurrent
        self.active_requests = 0

    async def __aenter__(self):
        """Enter semaphore context"""
        try:
            # Wait for slot with timeout
            await asyncio.wait_for(
                self.semaphore.acquire(),
                timeout=self.timeout
            )
            self.active_requests += 1
            logger.debug(
                f"Acquired semaphore slot ({self.active_requests}/{self.max_concurrent} active)"
            )
            return self
        except asyncio.TimeoutError:
            logger.error(
                f"Semaphore timeout after {self.timeout}s "
                f"({self.active_requests}/{self.max_concurrent} active)"
            )
            raise Exception(
                f"Request queue full. Too many concurrent operations. "
                f"Please try again later."
            )

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Exit semaphore context"""
        self.semaphore.release()
        self.active_requests -= 1
        logger.debug(
            f"Released semaphore slot ({self.active_requests}/{self.max_concurrent} active)"
        )
        return False


# Global instances for different operation types
ml_semaphore = RequestSemaphore(max_concurrent=10, timeout=120)  # ML operations
network_semaphore = RequestSemaphore(max_concurrent=3, timeout=180)  # Network analysis
export_semaphore = RequestSemaphore(max_concurrent=5, timeout=60)  # Export operations

# Circuit breakers for different services
ml_circuit_breaker = CircuitBreaker(failure_threshold=5, timeout=60)
db_circuit_breaker = CircuitBreaker(failure_threshold=3, timeout=30)


def with_concurrency_limit(semaphore: RequestSemaphore):
    """
    Decorator to limit concurrent execution of a function.

    Args:
        semaphore: RequestSemaphore instance to use

    Example:
        @with_concurrency_limit(ml_semaphore)
        async def expensive_ml_operation():
            ...
    """
    def decorator(func: Callable):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            async with semaphore:
                return await func(*args, **kwargs)
        return wrapper
    return decorator


async def run_with_circuit_breaker(
    func: Callable,
    circuit_breaker: CircuitBreaker,
    *args,
    **kwargs
) -> Any:
    """
    Execute function with circuit breaker protection.

    Args:
        func: Async function to execute
        circuit_breaker: CircuitBreaker instance
        *args: Function arguments
        **kwargs: Function keyword arguments

    Returns:
        Function result
    """
    wrapped_func = circuit_breaker.call(func)
    return await wrapped_func(*args, **kwargs)
