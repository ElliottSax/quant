"""
Redis caching utilities for pattern analysis results.

Caches expensive ML computations to improve API response times.
"""

import json
import hashlib
from typing import Any, Optional, Callable
from functools import wraps
from datetime import datetime, date
from decimal import Decimal

import redis.asyncio as redis
from app.core.config import settings
from app.core.logging import get_logger

logger = get_logger(__name__)


class CacheJSONEncoder(json.JSONEncoder):
    """Custom JSON encoder for cache serialization (safer than pickle)"""

    def default(self, obj):
        if isinstance(obj, datetime):
            return {"__type__": "datetime", "value": obj.isoformat()}
        if isinstance(obj, date):
            return {"__type__": "date", "value": obj.isoformat()}
        if isinstance(obj, Decimal):
            return {"__type__": "decimal", "value": str(obj)}
        if hasattr(obj, "__dict__"):
            return {"__type__": "object", "value": obj.__dict__}
        return super().default(obj)


def cache_json_decoder(obj: dict) -> Any:
    """Custom JSON decoder for cache deserialization"""
    if "__type__" in obj:
        type_name = obj["__type__"]
        value = obj["value"]
        if type_name == "datetime":
            return datetime.fromisoformat(value)
        if type_name == "date":
            return date.fromisoformat(value)
        if type_name == "decimal":
            return Decimal(value)
        if type_name == "object":
            return value
    return obj


class CacheManager:
    """Manager for Redis caching operations"""

    def __init__(self):
        self.redis_client: Optional[redis.Redis] = None
        # Enable caching in production AND development for testing
        self.enabled = settings.ENVIRONMENT in ["production", "development"]

    async def connect(self):
        """Connect to Redis"""
        if not self.enabled:
            logger.info("Cache disabled in non-production environment")
            return

        try:
            # Use settings for Redis ML configuration
            config = settings.redis_ml_config
            self.redis_client = redis.Redis(**config)
            await self.redis_client.ping()
            logger.info("Connected to Redis cache")
        except Exception as e:
            logger.warning(f"Failed to connect to Redis: {e}. Caching disabled.")
            self.redis_client = None
            self.enabled = False

    async def close(self):
        """Close Redis connection"""
        if self.redis_client:
            await self.redis_client.close()
            logger.info("Redis connection closed")

    def _make_key(self, prefix: str, **kwargs) -> str:
        """Generate cache key from parameters using SHA256 for security"""
        # Sort kwargs for consistent keys
        sorted_params = sorted(kwargs.items())
        param_str = json.dumps(sorted_params, sort_keys=True, default=str)
        param_hash = hashlib.sha256(param_str.encode()).hexdigest()[:32]
        return f"{prefix}:{param_hash}"

    async def get(self, key: str) -> Optional[Any]:
        """Get value from cache using JSON (safer than pickle)"""
        if not self.enabled or not self.redis_client:
            return None

        try:
            value = await self.redis_client.get(key)
            if value:
                logger.debug(f"Cache hit: {key}")
                return json.loads(value, object_hook=cache_json_decoder)
            logger.debug(f"Cache miss: {key}")
            return None
        except Exception as e:
            logger.error(f"Cache get error: {e}")
            return None

    async def set(self, key: str, value: Any, ttl: int = 3600):
        """Set value in cache with TTL using JSON (safer than pickle)"""
        if not self.enabled or not self.redis_client:
            return

        try:
            serialized = json.dumps(value, cls=CacheJSONEncoder)
            await self.redis_client.setex(key, ttl, serialized)
            logger.debug(f"Cache set: {key} (TTL: {ttl}s)")
        except Exception as e:
            logger.error(f"Cache set error: {e}")

    async def delete(self, key: str):
        """Delete key from cache"""
        if not self.enabled or not self.redis_client:
            return

        try:
            await self.redis_client.delete(key)
            logger.debug(f"Cache delete: {key}")
        except Exception as e:
            logger.error(f"Cache delete error: {e}")

    async def delete_pattern(self, pattern: str):
        """Delete all keys matching pattern"""
        if not self.enabled or not self.redis_client:
            return

        try:
            keys = []
            async for key in self.redis_client.scan_iter(match=pattern):
                keys.append(key)

            if keys:
                await self.redis_client.delete(*keys)
                logger.info(f"Deleted {len(keys)} keys matching {pattern}")
        except Exception as e:
            logger.error(f"Cache delete pattern error: {e}")


# Global cache instance
cache_manager = CacheManager()


def cached(prefix: str, ttl: int = 3600):
    """
    Decorator to cache function results.

    Args:
        prefix: Cache key prefix
        ttl: Time to live in seconds (default: 1 hour)

    Example:
        @cached("fourier", ttl=1800)
        async def analyze_fourier(politician_id: str):
            ...
    """
    def decorator(func: Callable):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # Generate cache key
            cache_key = cache_manager._make_key(
                prefix,
                args=args,
                kwargs=kwargs
            )

            # Try to get from cache
            cached_result = await cache_manager.get(cache_key)
            if cached_result is not None:
                return cached_result

            # Execute function
            result = await func(*args, **kwargs)

            # Store in cache
            await cache_manager.set(cache_key, result, ttl)

            return result
        return wrapper
    return decorator


async def invalidate_politician_cache(politician_id: str):
    """Invalidate all cached results for a politician"""
    patterns = [
        f"fourier:*{politician_id}*",
        f"hmm:*{politician_id}*",
        f"dtw:*{politician_id}*",
        f"comprehensive:*{politician_id}*"
    ]

    for pattern in patterns:
        await cache_manager.delete_pattern(pattern)

    logger.info(f"Invalidated cache for politician {politician_id}")


# Alias for backward compatibility with services that import cache_result
cache_result = cached
