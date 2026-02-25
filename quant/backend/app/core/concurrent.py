"""
Concurrency utilities for running ML tasks without blocking the event loop.

Provides wrappers for running CPU-intensive ML computations concurrently
using asyncio.to_thread() to prevent blocking the async event loop.

Author: Claude
"""

import asyncio
from functools import wraps
from typing import Callable, Any
import logging

logger = logging.getLogger(__name__)


def run_in_thread(func: Callable) -> Callable:
    """
    Decorator to run a function in a separate thread using asyncio.to_thread().

    This prevents CPU-intensive operations from blocking the async event loop,
    allowing multiple requests to be processed concurrently.

    Usage:
        @run_in_thread
        def cpu_intensive_function(data):
            # Heavy computation here
            return result

    Args:
        func: Function to run in a thread

    Returns:
        Async wrapper function
    """
    @wraps(func)
    async def wrapper(*args, **kwargs):
        logger.debug(f"Running {func.__name__} in thread pool")
        return await asyncio.to_thread(func, *args, **kwargs)

    return wrapper


async def run_ml_tasks_parallel(*tasks):
    """
    Run multiple ML tasks in parallel using asyncio.gather().

    This allows multiple CPU-intensive operations to run concurrently
    without blocking each other.

    Usage:
        results = await run_ml_tasks_parallel(
            analyze_fourier(...),
            analyze_hmm(...),
            analyze_dtw(...)
        )

    Args:
        *tasks: Async tasks to run in parallel

    Returns:
        Tuple of results from all tasks
    """
    logger.debug(f"Running {len(tasks)} ML tasks in parallel")
    try:
        results = await asyncio.gather(*tasks, return_exceptions=True)

        # Check for exceptions
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                logger.error(f"Task {i} failed: {result}", exc_info=result)

        return results
    except Exception as e:
        logger.error(f"Parallel ML tasks failed: {e}", exc_info=True)
        raise
