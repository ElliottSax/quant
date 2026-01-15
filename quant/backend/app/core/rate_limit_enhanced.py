"""
Enhanced rate limiting with per-user and per-IP limits.

Features:
- Per-user rate limiting with different tiers
- IP-based rate limiting for anonymous users
- Configurable limits for different endpoints
- Redis-backed for distributed systems
- Automatic cleanup of expired keys
"""

from typing import Optional, Dict, Any
from datetime import datetime, timedelta, timezone
from fastapi import Request, HTTPException, status
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
import redis.asyncio as redis
import hashlib
import json
import ipaddress

from app.core.config import settings
from app.core.logging import get_logger

logger = get_logger(__name__)


def is_trusted_proxy(ip: str) -> bool:
    """Check if IP is in the trusted proxy list."""
    if not settings.TRUST_PROXY_HEADERS:
        return False

    try:
        client_ip = ipaddress.ip_address(ip)
        for trusted in settings.TRUSTED_PROXIES:
            if "/" in trusted:
                # CIDR notation
                if client_ip in ipaddress.ip_network(trusted, strict=False):
                    return True
            else:
                if client_ip == ipaddress.ip_address(trusted):
                    return True
    except ValueError:
        return False

    return False


class RateLimitTier:
    """Rate limit tiers for different user types"""
    FREE = "free"
    BASIC = "basic"
    PREMIUM = "premium"
    UNLIMITED = "unlimited"

    # Limits per tier (requests per minute)
    LIMITS = {
        FREE: 20,
        BASIC: 60,
        PREMIUM: 200,
        UNLIMITED: float('inf')
    }

    # Hourly limits
    HOURLY_LIMITS = {
        FREE: 500,
        BASIC: 2000,
        PREMIUM: 10000,
        UNLIMITED: float('inf')
    }


# Security-sensitive endpoints that should fail-closed on rate limiter errors
FAIL_CLOSED_ENDPOINTS = {
    "/api/v1/auth/login",
    "/api/v1/auth/register",
    "/api/v1/auth/refresh",
    "/api/v1/auth/change-password",
}


class EnhancedRateLimiter:
    """
    Enhanced rate limiter with per-user and per-IP limits.
    Uses sliding window algorithm for accurate rate limiting.
    """
    
    def __init__(
        self,
        redis_client: Optional[redis.Redis] = None,
        default_limit: int = 60,
        window_seconds: int = 60,
        enable_user_limits: bool = True,
        enable_ip_limits: bool = True
    ):
        """
        Initialize rate limiter.
        
        Args:
            redis_client: Redis client for distributed rate limiting
            default_limit: Default requests per window
            window_seconds: Time window in seconds
            enable_user_limits: Enable per-user rate limiting
            enable_ip_limits: Enable per-IP rate limiting
        """
        self.redis_client = redis_client
        self.default_limit = default_limit
        self.window_seconds = window_seconds
        self.enable_user_limits = enable_user_limits
        self.enable_ip_limits = enable_ip_limits
        
        # Endpoint-specific limits
        self.endpoint_limits = {
            "/api/v1/analytics/ensemble": 10,  # ML endpoints are expensive
            "/api/v1/analytics/network": 5,
            "/api/v1/export": 20,
            "/api/v1/auth/login": 5,  # Prevent brute force
            "/api/v1/auth/register": 3,
        }
    
    async def _get_redis(self) -> redis.Redis:
        """Get or create Redis connection."""
        if not self.redis_client:
            self.redis_client = await redis.from_url(
                settings.REDIS_URL,
                encoding="utf-8",
                decode_responses=True
            )
        return self.redis_client
    
    def _get_identifier(self, request: Request) -> tuple[str, str]:
        """
        Get user and IP identifiers from request.

        Only trusts proxy headers if request comes from a trusted proxy
        to prevent IP spoofing attacks.

        Returns:
            Tuple of (user_id, ip_address)
        """
        # Get user ID from request state (set by auth middleware)
        user_id = getattr(request.state, "user_id", None)

        # Get direct client IP
        direct_ip = request.client.host if request.client else "unknown"
        ip = direct_ip

        # Only trust proxy headers if request comes from a trusted proxy
        if is_trusted_proxy(direct_ip):
            if "X-Forwarded-For" in request.headers:
                # Take the first (client) IP from the chain
                forwarded_ips = request.headers["X-Forwarded-For"].split(",")
                ip = forwarded_ips[0].strip()
            elif "X-Real-IP" in request.headers:
                ip = request.headers["X-Real-IP"].strip()
        elif "X-Forwarded-For" in request.headers or "X-Real-IP" in request.headers:
            # Log potential spoofing attempt (but don't use the spoofed IP)
            logger.warning(
                f"Proxy headers present from untrusted source {direct_ip}, ignoring"
            )

        return user_id, ip
    
    def _get_user_tier(self, user_id: Optional[str]) -> str:
        """
        Get user's rate limit tier.
        
        In production, this would query the database.
        """
        if not user_id:
            return RateLimitTier.FREE
        
        # TODO: Query database for user subscription tier
        # For now, return basic tier for authenticated users
        return RateLimitTier.BASIC
    
    def _get_limit_for_endpoint(self, path: str, tier: str) -> int:
        """
        Get rate limit for specific endpoint and tier.
        
        Args:
            path: Request path
            tier: User tier
            
        Returns:
            Requests allowed per window
        """
        # Check for endpoint-specific limit
        for endpoint_pattern, limit in self.endpoint_limits.items():
            if path.startswith(endpoint_pattern):
                # Adjust limit based on tier
                tier_multiplier = {
                    RateLimitTier.FREE: 1,
                    RateLimitTier.BASIC: 2,
                    RateLimitTier.PREMIUM: 5,
                    RateLimitTier.UNLIMITED: float('inf')
                }.get(tier, 1)
                
                return int(limit * tier_multiplier)
        
        # Return tier default
        return RateLimitTier.LIMITS.get(tier, self.default_limit)
    
    async def check_rate_limit(
        self,
        request: Request
    ) -> tuple[bool, Dict[str, Any]]:
        """
        Check if request should be rate limited.
        
        Args:
            request: FastAPI request
            
        Returns:
            Tuple of (is_allowed, metadata)
        """
        user_id, ip = self._get_identifier(request)
        path = request.url.path
        
        # Get user tier and limit
        tier = self._get_user_tier(user_id)
        limit = self._get_limit_for_endpoint(path, tier)
        
        # Unlimited tier bypasses rate limiting
        if tier == RateLimitTier.UNLIMITED:
            return True, {"tier": tier, "limit": "unlimited"}
        
        # Get Redis client
        redis_client = await self._get_redis()
        
        # Create keys for rate limiting
        now = datetime.now(timezone.utc)
        window_start = now - timedelta(seconds=self.window_seconds)
        
        # User-based rate limiting
        if self.enable_user_limits and user_id:
            key = f"rate_limit:user:{user_id}:{path}"
            user_allowed, user_meta = await self._check_sliding_window(
                redis_client, key, limit, now, window_start
            )
            
            if not user_allowed:
                return False, {
                    "tier": tier,
                    "limit": limit,
                    "remaining": user_meta["remaining"],
                    "reset": user_meta["reset"],
                    "type": "user"
                }
        
        # IP-based rate limiting
        if self.enable_ip_limits:
            # Hash IP for privacy
            ip_hash = hashlib.sha256(ip.encode()).hexdigest()[:16]
            key = f"rate_limit:ip:{ip_hash}:{path}"
            
            # Lower limit for IP-based (prevents abuse)
            ip_limit = min(limit // 2, 30) if not user_id else limit
            
            ip_allowed, ip_meta = await self._check_sliding_window(
                redis_client, key, ip_limit, now, window_start
            )
            
            if not ip_allowed:
                return False, {
                    "tier": "anonymous" if not user_id else tier,
                    "limit": ip_limit,
                    "remaining": ip_meta["remaining"],
                    "reset": ip_meta["reset"],
                    "type": "ip"
                }
        
        # Calculate remaining requests
        if user_id:
            key = f"rate_limit:user:{user_id}:{path}"
        else:
            ip_hash = hashlib.sha256(ip.encode()).hexdigest()[:16]
            key = f"rate_limit:ip:{ip_hash}:{path}"
        
        count = await redis_client.zcount(
            key,
            window_start.timestamp(),
            now.timestamp()
        )
        
        return True, {
            "tier": tier,
            "limit": limit,
            "remaining": max(0, limit - count),
            "reset": (now + timedelta(seconds=self.window_seconds)).timestamp()
        }
    
    async def _check_sliding_window(
        self,
        redis_client: redis.Redis,
        key: str,
        limit: int,
        now: datetime,
        window_start: datetime
    ) -> tuple[bool, Dict[str, Any]]:
        """
        Check rate limit using sliding window algorithm.
        
        Args:
            redis_client: Redis client
            key: Redis key for rate limiting
            limit: Request limit
            now: Current time
            window_start: Window start time
            
        Returns:
            Tuple of (is_allowed, metadata)
        """
        pipe = redis_client.pipeline()
        
        # Remove old entries
        pipe.zremrangebyscore(key, 0, window_start.timestamp())
        
        # Count requests in window
        pipe.zcount(key, window_start.timestamp(), now.timestamp())
        
        # Execute pipeline
        results = await pipe.execute()
        count = results[1]
        
        if count >= limit:
            # Calculate reset time
            oldest_timestamp = await redis_client.zrange(
                key, 0, 0, withscores=True
            )
            
            if oldest_timestamp:
                reset_time = oldest_timestamp[0][1] + self.window_seconds
            else:
                reset_time = now.timestamp() + self.window_seconds
            
            return False, {
                "remaining": 0,
                "reset": reset_time
            }
        
        # Add current request
        await redis_client.zadd(key, {str(now.timestamp()): now.timestamp()})
        
        # Set expiry
        await redis_client.expire(key, self.window_seconds * 2)
        
        return True, {
            "remaining": limit - count - 1,
            "reset": (now + timedelta(seconds=self.window_seconds)).timestamp()
        }


class EnhancedRateLimitMiddleware(BaseHTTPMiddleware):
    """
    Middleware for enhanced rate limiting.
    """
    
    def __init__(self, app, rate_limiter: Optional[EnhancedRateLimiter] = None):
        super().__init__(app)
        self.rate_limiter = rate_limiter or EnhancedRateLimiter()
    
    async def dispatch(self, request: Request, call_next):
        """
        Process request with rate limiting.
        """
        # Skip rate limiting for health checks and docs
        skip_paths = ["/health", "/docs", "/redoc", "/openapi.json"]
        if any(request.url.path.startswith(p) for p in skip_paths):
            return await call_next(request)
        
        # Check rate limit
        try:
            is_allowed, metadata = await self.rate_limiter.check_rate_limit(request)
            
            if not is_allowed:
                logger.warning(
                    f"Rate limit exceeded: {metadata.get('type')} "
                    f"tier={metadata.get('tier')} path={request.url.path}"
                )
                
                # Return 429 with rate limit headers
                return JSONResponse(
                    status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                    content={
                        "detail": "Rate limit exceeded",
                        "limit": metadata.get("limit"),
                        "remaining": metadata.get("remaining", 0),
                        "reset": metadata.get("reset"),
                        "tier": metadata.get("tier")
                    },
                    headers={
                        "X-RateLimit-Limit": str(metadata.get("limit", 0)),
                        "X-RateLimit-Remaining": str(metadata.get("remaining", 0)),
                        "X-RateLimit-Reset": str(metadata.get("reset", 0)),
                        "Retry-After": str(
                            max(1, int(metadata.get("reset", 0) - datetime.now(timezone.utc).timestamp()))
                        )
                    }
                )
            
            # Process request
            response = await call_next(request)
            
            # Add rate limit headers
            response.headers["X-RateLimit-Limit"] = str(metadata.get("limit", 0))
            response.headers["X-RateLimit-Remaining"] = str(metadata.get("remaining", 0))
            response.headers["X-RateLimit-Reset"] = str(metadata.get("reset", 0))
            
            return response
            
        except Exception as e:
            logger.error(f"Rate limiter error: {e}", exc_info=True)

            # Fail-closed for security-sensitive endpoints in production only
            # In development/test, we fail-open to allow testing without Redis
            if (
                request.url.path in FAIL_CLOSED_ENDPOINTS
                and settings.ENVIRONMENT == "production"
            ):
                logger.warning(f"Rate limiter failed in production, blocking sensitive endpoint: {request.url.path}")
                return JSONResponse(
                    status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                    content={
                        "detail": "Rate limiting service unavailable, please try again later"
                    }
                )

            # Fail-open for non-sensitive endpoints and non-production environments
            return await call_next(request)