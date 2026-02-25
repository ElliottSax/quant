"""
Exception Handling Patterns and Best Practices

This module documents the standard exception handling patterns used throughout
the quant project. Follow these patterns for consistent, maintainable error handling.

Author: Development Team
Last Updated: 2026-02-03
"""

import logging
from typing import Optional, Any, Dict
from contextlib import contextmanager
import traceback
from functools import wraps
import httpx
from fastapi import HTTPException
from sqlalchemy.exc import SQLAlchemyError, IntegrityError, OperationalError
from pydantic import ValidationError


logger = logging.getLogger(__name__)


# ==================== COMMON EXCEPTION TYPES ====================

"""
Use these specific exception types instead of bare 'Exception':

API/Network Errors:
- httpx.HTTPError: Base class for all HTTP errors
- httpx.RequestError: Failed to send request
- httpx.TimeoutException: Request timeout
- httpx.HTTPStatusError: Non-2xx status code
- ConnectionError: Network connection failed

Data Validation:
- ValueError: Invalid value or type
- TypeError: Wrong type
- KeyError: Missing dictionary key
- IndexError: Invalid list/array index
- AttributeError: Missing attribute
- ValidationError: Pydantic validation failed

Database:
- SQLAlchemyError: Base database error
- IntegrityError: Constraint violation (unique, foreign key, etc.)
- OperationalError: Database connection/operation error

File/IO:
- FileNotFoundError: File doesn't exist
- PermissionError: No permission to access resource
- IOError: General IO error

JSON:
- json.JSONDecodeError: Invalid JSON

Async:
- asyncio.TimeoutError: Async operation timeout
- asyncio.CancelledError: Task was cancelled

Business Logic:
- HTTPException: FastAPI HTTP exception (for API endpoints)
- Custom exceptions: Create specific exceptions for domain errors
"""


# ==================== PATTERN 1: API/External Service Calls ====================

async def example_api_call_pattern(url: str) -> Dict[str, Any]:
    """
    Pattern for external API calls with specific exception handling.

    Use this pattern when calling external APIs or services.
    """
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.get(url)
            response.raise_for_status()
            return response.json()

    except httpx.TimeoutException as e:
        logger.error(f"API request timeout for {url}: {e}", exc_info=True)
        raise HTTPException(
            status_code=504,
            detail="External service request timed out"
        )

    except httpx.HTTPStatusError as e:
        logger.error(
            f"API returned error status {e.response.status_code} for {url}: {e}",
            exc_info=True
        )
        raise HTTPException(
            status_code=502,
            detail=f"External service error: {e.response.status_code}"
        )

    except httpx.RequestError as e:
        logger.error(f"API request failed for {url}: {e}", exc_info=True)
        raise HTTPException(
            status_code=503,
            detail="Failed to connect to external service"
        )

    except (ValueError, KeyError) as e:
        logger.error(f"Invalid API response from {url}: {e}", exc_info=True)
        raise HTTPException(
            status_code=502,
            detail="External service returned invalid data"
        )


# ==================== PATTERN 2: Data Validation ====================

def example_data_validation_pattern(data: Dict[str, Any]) -> Any:
    """
    Pattern for data validation with specific exception handling.

    Use this pattern when parsing and validating user input or external data.
    """
    try:
        # Validate required fields
        if 'symbol' not in data:
            raise KeyError("Missing required field: symbol")

        # Validate types
        price = float(data['price'])
        if price <= 0:
            raise ValueError(f"Price must be positive, got {price}")

        return {"symbol": data['symbol'].upper(), "price": price}

    except KeyError as e:
        logger.warning(f"Missing required field in data: {e}")
        raise ValueError(f"Missing required field: {e}")

    except (ValueError, TypeError) as e:
        logger.warning(f"Invalid data format: {e}")
        raise ValueError(f"Invalid data format: {e}")

    except ValidationError as e:
        logger.warning(f"Pydantic validation failed: {e}")
        raise ValueError(f"Validation error: {e}")


# ==================== PATTERN 3: Database Operations ====================

async def example_database_pattern(db_session, query_data: Dict) -> Any:
    """
    Pattern for database operations with specific exception handling.

    Use this pattern for all database operations.
    """
    try:
        # Perform database operation
        result = await db_session.execute(query_data)
        await db_session.commit()
        return result

    except IntegrityError as e:
        await db_session.rollback()
        logger.error(f"Database integrity error: {e}", exc_info=True)
        raise HTTPException(
            status_code=409,
            detail="Database constraint violation (duplicate or invalid reference)"
        )

    except OperationalError as e:
        await db_session.rollback()
        logger.error(f"Database operational error: {e}", exc_info=True)
        raise HTTPException(
            status_code=503,
            detail="Database operation failed"
        )

    except SQLAlchemyError as e:
        await db_session.rollback()
        logger.error(f"Database error: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail="Database error occurred"
        )


# ==================== PATTERN 4: WebSocket Operations ====================

async def example_websocket_send_pattern(websocket, message: Dict):
    """
    Pattern for WebSocket send operations.

    Use this pattern when sending WebSocket messages.
    """
    from starlette.websockets import WebSocketState, WebSocketDisconnect

    try:
        if websocket.client_state == WebSocketState.CONNECTED:
            await websocket.send_json(message)

    except WebSocketDisconnect:
        # Expected when client disconnects - not an error
        logger.info("WebSocket client disconnected")
        raise  # Re-raise to trigger cleanup

    except (ConnectionError, OSError) as e:
        # Network-level errors
        logger.warning(f"WebSocket connection error: {e}")
        raise WebSocketDisconnect()

    except (ValueError, TypeError) as e:
        # Message serialization errors
        logger.error(f"WebSocket message serialization error: {e}", exc_info=True)
        # Don't disconnect - log and continue


# ==================== PATTERN 5: File Operations ====================

def example_file_operation_pattern(file_path: str) -> str:
    """
    Pattern for file operations with specific exception handling.

    Use this pattern when reading/writing files.
    """
    try:
        with open(file_path, 'r') as f:
            content = f.read()
        return content

    except FileNotFoundError as e:
        logger.error(f"File not found: {file_path}: {e}")
        raise HTTPException(
            status_code=404,
            detail=f"File not found: {file_path}"
        )

    except PermissionError as e:
        logger.error(f"Permission denied for file: {file_path}: {e}")
        raise HTTPException(
            status_code=403,
            detail=f"Permission denied: {file_path}"
        )

    except IOError as e:
        logger.error(f"IO error reading file {file_path}: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail="Failed to read file"
        )


# ==================== PATTERN 6: Background Tasks & Async ====================

async def example_background_task_pattern():
    """
    Pattern for background tasks with graceful error handling.

    Use this pattern for background tasks and long-running operations.
    """
    try:
        # Perform long-running operation
        result = await asyncio.wait_for(
            some_async_operation(),
            timeout=60.0
        )
        return result

    except asyncio.TimeoutError:
        logger.warning("Background task timed out after 60s")
        # Don't raise - log and continue or retry
        return None

    except asyncio.CancelledError:
        logger.info("Background task was cancelled")
        # Clean up and re-raise
        await cleanup_resources()
        raise

    except (ConnectionError, OSError) as e:
        logger.error(f"Network error in background task: {e}", exc_info=True)
        # Retry logic here
        return None


# ==================== PATTERN 7: Fallback Pattern ====================

async def example_fallback_pattern(primary_source: str) -> Any:
    """
    Pattern for operations with fallback options.

    Use this pattern when you have multiple data sources or fallback logic.
    """
    # Try primary source
    try:
        return await fetch_from_primary(primary_source)

    except (httpx.RequestError, httpx.TimeoutException) as e:
        logger.warning(
            f"Primary source {primary_source} failed: {e}, trying fallback"
        )
        # Don't log full stack trace for expected fallback scenarios

    except (KeyError, ValueError) as e:
        logger.warning(
            f"Invalid data from primary source {primary_source}: {e}, trying fallback"
        )

    # Try fallback source
    try:
        return await fetch_from_fallback()

    except (httpx.RequestError, httpx.TimeoutException, KeyError, ValueError) as e:
        logger.error(
            f"Fallback also failed: {e}, returning mock data",
            exc_info=True  # Log full stack trace only for final failure
        )
        return generate_mock_data()


# ==================== WHEN TO USE 'Exception' ====================

"""
Only use bare 'except Exception' in these specific scenarios:

1. Top-level error handlers (main function, API router exception handlers)
2. Plugin/extension systems where you can't predict exception types
3. Cleanup in finally blocks where any error should be logged but not propagate
4. Background worker loops that should never crash

ALWAYS add a comment explaining why the broad exception is necessary.
"""

async def example_acceptable_broad_exception():
    """
    Example where broad 'Exception' is acceptable.
    """
    while True:  # Background worker loop
        try:
            await process_queue_item()

        except Exception as e:  # Broad exception acceptable here
            # We use Exception here because we want the worker to never crash,
            # regardless of what error occurs in process_queue_item()
            logger.error(
                f"Unexpected error in worker loop: {e}",
                exc_info=True,
                extra={
                    "error_type": type(e).__name__,
                    "correlation_id": "worker-1"
                }
            )
            await asyncio.sleep(5)  # Back off before retry


# ==================== LOGGING BEST PRACTICES ====================

"""
Logging Guidelines:

1. Use appropriate log levels:
   - ERROR: Something failed that requires attention
   - WARNING: Something unexpected but handled (fallback, retry)
   - INFO: Normal operations (connections, important state changes)
   - DEBUG: Detailed debugging information

2. Include context in log messages:
   - What operation was being performed
   - Relevant identifiers (symbol, user_id, request_id)
   - Error details

3. Use exc_info=True for stack traces:
   - Always use for ERROR level when catching exceptions
   - Rarely use for WARNING (only unexpected scenarios)
   - Never use for INFO/DEBUG

4. Add structured logging context:
   logger.error("msg", exc_info=True, extra={
       "correlation_id": request_id,
       "user_id": user.id,
       "symbol": symbol
   })

5. Never log sensitive data:
   - Passwords, tokens, API keys
   - Personal information (PII)
   - Credit card numbers
"""


# ==================== HELPER UTILITIES ====================

def get_exception_context(exception: Exception) -> Dict[str, Any]:
    """
    Extract useful context from an exception for logging.

    Args:
        exception: The exception to extract context from

    Returns:
        Dictionary with exception details
    """
    return {
        "exception_type": type(exception).__name__,
        "exception_message": str(exception),
        "exception_module": exception.__class__.__module__,
        "traceback": traceback.format_exc()
    }


@contextmanager
def log_exceptions(operation: str, correlation_id: Optional[str] = None):
    """
    Context manager for consistent exception logging.

    Usage:
        with log_exceptions("fetch_market_data", correlation_id=request_id):
            data = await fetch_data()
    """
    try:
        yield
    except Exception as e:
        logger.error(
            f"Error in {operation}: {e}",
            exc_info=True,
            extra={
                "operation": operation,
                "correlation_id": correlation_id,
                **get_exception_context(e)
            }
        )
        raise


def safe_async_handler(correlation_id_key: str = "request_id"):
    """
    Decorator for async handlers that ensures proper exception logging.

    Usage:
        @safe_async_handler()
        async def my_handler(request: Request):
            ...
    """
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            correlation_id = kwargs.get(correlation_id_key)
            try:
                return await func(*args, **kwargs)
            except HTTPException:
                # Don't wrap HTTPException - let it propagate
                raise
            except Exception as e:
                logger.error(
                    f"Unhandled error in {func.__name__}: {e}",
                    exc_info=True,
                    extra={
                        "function": func.__name__,
                        "correlation_id": correlation_id,
                        **get_exception_context(e)
                    }
                )
                raise HTTPException(
                    status_code=500,
                    detail="Internal server error"
                )
        return wrapper
    return decorator


# ==================== EXAMPLE: Async operation placeholder ====================
async def some_async_operation():
    """Placeholder for example"""
    await asyncio.sleep(1)
    return "result"

async def cleanup_resources():
    """Placeholder for example"""
    pass

async def fetch_from_primary(source: str):
    """Placeholder for example"""
    pass

async def fetch_from_fallback():
    """Placeholder for example"""
    pass

def generate_mock_data():
    """Placeholder for example"""
    return {}

async def process_queue_item():
    """Placeholder for example"""
    pass
