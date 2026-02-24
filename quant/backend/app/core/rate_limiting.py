"""Rate limiting for prediction endpoints."""

import time
from typing import Dict, Optional
from collections import defaultdict
from datetime import datetime, timedelta
from fastapi import HTTPException, Request, status

from app.core.config import settings
from app.core.logging import get_logger

logger = get_logger(__name__)


class RateLimiter:
    """
    Simple in-memory rate limiter for prediction endpoints.

    For production, consider using Redis-based rate limiting for distributed systems.
    """

    def __init__(self):
        # Storage: {user_id/ip: {endpoint: [(timestamp, count)]}}
        self._requests: Dict[str, Dict[str, list]] = defaultdict(lambda: defaultdict(list))
        self._cleanup_interval = 300  # Clean up old entries every 5 minutes
        self._last_cleanup = time.time()

    def _cleanup_old_entries(self):
        """Remove entries older than the rate limit window."""
        current_time = time.time()

        if current_time - self._last_cleanup < self._cleanup_interval:
            return

        cutoff_time = current_time - settings.rate_limit.RATE_LIMIT_WINDOW_SECONDS

        for user_key in list(self._requests.keys()):
            for endpoint in list(self._requests[user_key].keys()):
                # Filter out old requests
                self._requests[user_key][endpoint] = [
                    (ts, count) for ts, count in self._requests[user_key][endpoint]
                    if ts > cutoff_time
                ]

                # Remove empty endpoint entries
                if not self._requests[user_key][endpoint]:
                    del self._requests[user_key][endpoint]

            # Remove empty user entries
            if not self._requests[user_key]:
                del self._requests[user_key]

        self._last_cleanup = current_time
        logger.debug(f"Rate limiter cleanup complete. Active users: {len(self._requests)}")

    def check_rate_limit(
        self,
        identifier: str,
        endpoint: str,
        limit_per_minute: int,
        limit_per_hour: Optional[int] = None
    ) -> tuple[bool, Optional[str]]:
        """
        Check if request is within rate limits.

        Args:
            identifier: User ID or IP address
            endpoint: Endpoint identifier
            limit_per_minute: Maximum requests per minute
            limit_per_hour: Maximum requests per hour (optional)

        Returns:
            (allowed: bool, error_message: Optional[str])
        """
        self._cleanup_old_entries()

        current_time = time.time()
        user_requests = self._requests[identifier][endpoint]

        # Check per-minute limit
        minute_ago = current_time - 60
        minute_count = sum(
            count for ts, count in user_requests
            if ts > minute_ago
        )

        if minute_count >= limit_per_minute:
            retry_after = int(60 - (current_time - user_requests[-1][0]))
            return False, f"Rate limit exceeded: {limit_per_minute} requests per minute. Retry after {retry_after}s"

        # Check per-hour limit if specified
        if limit_per_hour:
            hour_ago = current_time - 3600
            hour_count = sum(
                count for ts, count in user_requests
                if ts > hour_ago
            )

            if hour_count >= limit_per_hour:
                return False, f"Hourly rate limit exceeded: {limit_per_hour} requests per hour"

        # Record this request
        user_requests.append((current_time, 1))

        return True, None


# Global rate limiter instance
rate_limiter = RateLimiter()


async def check_prediction_rate_limit(request: Request, user_id: Optional[str] = None):
    """
    FastAPI dependency for checking prediction endpoint rate limits.

    Uses user_id if authenticated, otherwise uses IP address.
    Different tiers have different limits based on user subscription.
    """
    # Determine identifier (user_id or IP)
    identifier = user_id if user_id else request.client.host

    # Determine endpoint
    endpoint = request.url.path

    # Determine limits based on user tier
    # For now, use default limits. In production, query user's subscription tier
    limit_per_minute = settings.rate_limit.FREE_TIER_RPM
    limit_per_hour = settings.rate_limit.FREE_TIER_RPH

    # TODO: Query user's subscription tier and adjust limits
    # if user_id:
    #     user_tier = await get_user_tier(user_id)
    #     if user_tier == "premium":
    #         limit_per_minute = settings.rate_limit.PREMIUM_TIER_RPM
    #         limit_per_hour = settings.rate_limit.PREMIUM_TIER_RPH

    # Check rate limit
    allowed, error_msg = rate_limiter.check_rate_limit(
        identifier=identifier,
        endpoint=endpoint,
        limit_per_minute=limit_per_minute,
        limit_per_hour=limit_per_hour
    )

    if not allowed:
        logger.warning(f"Rate limit exceeded for {identifier} on {endpoint}")
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail=error_msg,
            headers={"Retry-After": "60"}
        )

    return True
