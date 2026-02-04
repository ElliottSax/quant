"""
Monitoring Middleware

Automatically tracks request metrics for all endpoints.
"""

import time
import traceback
from typing import Callable
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp

from app.core.monitoring import monitoring_service
from app.core.logging import get_logger

logger = get_logger(__name__)


class MonitoringMiddleware(BaseHTTPMiddleware):
    """
    Middleware to track HTTP request metrics.

    Tracks:
    - Request count by method, endpoint, status
    - Request duration
    - Active requests
    - Errors
    """

    def __init__(self, app: ASGIApp):
        super().__init__(app)

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """Process request and track metrics"""

        # Track active requests
        monitoring_service.active_requests.inc()

        # Start timer
        start_time = time.time()

        # Get endpoint path (remove query params)
        endpoint = request.url.path
        method = request.method

        response = None
        status_code = 500  # Default to error

        try:
            # Process request
            response = await call_next(request)
            status_code = response.status_code

            return response

        except Exception as e:
            # Track error
            error_type = type(e).__name__
            monitoring_service.track_error(error_type, endpoint)

            logger.error(
                f"Request failed: {method} {endpoint}",
                exc_info=True,
                extra={
                    "method": method,
                    "endpoint": endpoint,
                    "error_type": error_type,
                    "traceback": traceback.format_exc()
                }
            )

            # Re-raise exception
            raise

        finally:
            # Calculate duration
            duration = time.time() - start_time

            # Track metrics
            monitoring_service.track_request(method, endpoint, status_code)

            monitoring_service.request_duration.labels(
                method=method,
                endpoint=endpoint
            ).observe(duration)

            # Decrement active requests
            monitoring_service.active_requests.dec()

            # Log slow requests
            if duration > 1.0:  # Slow request threshold: 1 second
                logger.warning(
                    f"Slow request: {method} {endpoint} took {duration:.2f}s",
                    extra={
                        "method": method,
                        "endpoint": endpoint,
                        "duration": duration,
                        "status_code": status_code
                    }
                )
