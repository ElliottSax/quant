"""Rate limiting middleware."""

import time
from collections import defaultdict
from typing import Callable

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.status import HTTP_429_TOO_MANY_REQUESTS

from app.core.logging import get_logger

logger = get_logger(__name__)


class RateLimitMiddleware(BaseHTTPMiddleware):
    """
    Simple in-memory rate limiting middleware.

    For production, consider using Redis for distributed rate limiting.
    """

    def __init__(
        self,
        app,
        requests_per_minute: int = 60,
        requests_per_hour: int = 1000,
    ):
        super().__init__(app)
        self.requests_per_minute = requests_per_minute
        self.requests_per_hour = requests_per_hour

        # Storage: {client_ip: [(timestamp, endpoint), ...]}
        self.request_log: dict[str, list[tuple[float, str]]] = defaultdict(list)

        # Cleanup interval (seconds)
        self.last_cleanup = time.time()
        self.cleanup_interval = 300  # 5 minutes

    def _cleanup_old_requests(self) -> None:
        """Remove requests older than 1 hour."""
        current_time = time.time()

        # Only cleanup every cleanup_interval seconds
        if current_time - self.last_cleanup < self.cleanup_interval:
            return

        cutoff_time = current_time - 3600  # 1 hour ago

        for client_ip in list(self.request_log.keys()):
            self.request_log[client_ip] = [
                (timestamp, endpoint)
                for timestamp, endpoint in self.request_log[client_ip]
                if timestamp > cutoff_time
            ]

            # Remove empty entries
            if not self.request_log[client_ip]:
                del self.request_log[client_ip]

        self.last_cleanup = current_time

    def _get_client_ip(self, request: Request) -> str:
        """Extract client IP from request."""
        # Check for forwarded header (when behind proxy)
        forwarded = request.headers.get("X-Forwarded-For")
        if forwarded:
            return forwarded.split(",")[0].strip()

        # Check for real IP header
        real_ip = request.headers.get("X-Real-IP")
        if real_ip:
            return real_ip

        # Fall back to direct client
        if request.client:
            return request.client.host

        return "unknown"

    def _is_rate_limited(self, client_ip: str, endpoint: str) -> tuple[bool, str]:
        """
        Check if client has exceeded rate limits.

        Returns:
            Tuple of (is_limited, reason)
        """
        current_time = time.time()
        client_requests = self.request_log[client_ip]

        # Check per-minute limit
        minute_ago = current_time - 60
        minute_requests = [
            (t, e) for t, e in client_requests if t > minute_ago and e == endpoint
        ]

        if len(minute_requests) >= self.requests_per_minute:
            return True, f"Rate limit exceeded: {self.requests_per_minute} requests per minute"

        # Check per-hour limit
        hour_ago = current_time - 3600
        hour_requests = [
            (t, e) for t, e in client_requests if t > hour_ago
        ]

        if len(hour_requests) >= self.requests_per_hour:
            return True, f"Rate limit exceeded: {self.requests_per_hour} requests per hour"

        return False, ""

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """Process request with rate limiting."""
        # Skip rate limiting for health checks and root endpoint
        if request.url.path in ["/", "/health", "/api/v1/docs", "/api/v1/openapi.json"]:
            return await call_next(request)

        # Cleanup old requests periodically
        self._cleanup_old_requests()

        # Get client identifier
        client_ip = self._get_client_ip(request)
        endpoint = request.url.path

        # Check rate limit
        is_limited, reason = self._is_rate_limited(client_ip, endpoint)

        if is_limited:
            logger.warning(
                f"Rate limit exceeded for {client_ip} on {endpoint}",
                extra={"client_ip": client_ip, "endpoint": endpoint},
            )
            return Response(
                content=f'{{"detail": "{reason}"}}',
                status_code=HTTP_429_TOO_MANY_REQUESTS,
                media_type="application/json",
                headers={
                    "Retry-After": "60",  # Suggest retry after 60 seconds
                    "X-RateLimit-Limit": str(self.requests_per_minute),
                    "X-RateLimit-Remaining": "0",
                },
            )

        # Record this request
        current_time = time.time()
        self.request_log[client_ip].append((current_time, endpoint))

        # Process request
        response = await call_next(request)

        # Add rate limit headers to response
        minute_ago = current_time - 60
        recent_requests = [
            (t, e)
            for t, e in self.request_log[client_ip]
            if t > minute_ago and e == endpoint
        ]
        remaining = max(0, self.requests_per_minute - len(recent_requests))

        response.headers["X-RateLimit-Limit"] = str(self.requests_per_minute)
        response.headers["X-RateLimit-Remaining"] = str(remaining)

        return response
