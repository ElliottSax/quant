"""
Caching layer for market data and backtest results
Reduces Yahoo Finance API calls and improves performance
"""

import hashlib
import json
import pickle
from typing import Optional, Any
from datetime import datetime, timedelta
from functools import wraps
import logging

logger = logging.getLogger(__name__)

# Simple in-memory cache (could be Redis in production)
_cache = {}
_cache_timestamps = {}


def get_cache_key(*args, **kwargs) -> str:
    """Generate cache key from function arguments"""
    key_data = {
        "args": args,
        "kwargs": sorted(kwargs.items())
    }
    key_string = json.dumps(key_data, sort_keys=True, default=str)
    return hashlib.md5(key_string.encode()).hexdigest()


def cache_response(ttl_seconds: int = 3600):
    """
    Cache decorator for functions
    
    Args:
        ttl_seconds: Time to live in seconds (default 1 hour)
    """
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # Generate cache key
            cache_key = f"{func.__name__}:{get_cache_key(*args, **kwargs)}"
            
            # Check cache
            if cache_key in _cache:
                cached_time = _cache_timestamps.get(cache_key)
                if cached_time and (datetime.now() - cached_time).seconds < ttl_seconds:
                    logger.debug(f"Cache HIT: {cache_key}")
                    return _cache[cache_key]
                else:
                    # Expired
                    logger.debug(f"Cache EXPIRED: {cache_key}")
                    del _cache[cache_key]
                    del _cache_timestamps[cache_key]
            
            # Cache miss - execute function
            logger.debug(f"Cache MISS: {cache_key}")
            result = await func(*args, **kwargs)
            
            # Store in cache
            _cache[cache_key] = result
            _cache_timestamps[cache_key] = datetime.now()
            
            return result
        
        return wrapper
    return decorator


class MarketDataCache:
    """Specialized cache for market data"""
    
    def __init__(self, ttl_minutes: int = 30):
        self.ttl_minutes = ttl_minutes
        self.cache = {}
        self.timestamps = {}
    
    def get_key(self, symbol: str, start_date: str, end_date: str) -> str:
        """Generate cache key for market data"""
        return f"{symbol}:{start_date}:{end_date}"
    
    def get(self, symbol: str, start_date: str, end_date: str) -> Optional[Any]:
        """Get cached market data"""
        key = self.get_key(symbol, start_date, end_date)
        
        if key in self.cache:
            cached_time = self.timestamps.get(key)
            if cached_time:
                age_minutes = (datetime.now() - cached_time).seconds / 60
                if age_minutes < self.ttl_minutes:
                    logger.info(f"Market data cache HIT: {symbol} ({age_minutes:.1f}min old)")
                    return self.cache[key]
                else:
                    # Expired
                    del self.cache[key]
                    del self.timestamps[key]
        
        logger.info(f"Market data cache MISS: {symbol}")
        return None
    
    def set(self, symbol: str, start_date: str, end_date: str, data: Any):
        """Cache market data"""
        key = self.get_key(symbol, start_date, end_date)
        self.cache[key] = data
        self.timestamps[key] = datetime.now()
        logger.info(f"Market data cached: {symbol}")
    
    def clear_expired(self):
        """Clear expired cache entries"""
        now = datetime.now()
        expired_keys = []
        
        for key, timestamp in self.timestamps.items():
            age_minutes = (now - timestamp).seconds / 60
            if age_minutes >= self.ttl_minutes:
                expired_keys.append(key)
        
        for key in expired_keys:
            del self.cache[key]
            del self.timestamps[key]
        
        if expired_keys:
            logger.info(f"Cleared {len(expired_keys)} expired cache entries")
    
    def get_stats(self) -> dict:
        """Get cache statistics"""
        total_size = sum(len(pickle.dumps(v)) for v in self.cache.values())
        
        return {
            "entries": len(self.cache),
            "size_bytes": total_size,
            "size_mb": total_size / (1024 * 1024),
            "oldest_entry": min(self.timestamps.values()) if self.timestamps else None,
            "newest_entry": max(self.timestamps.values()) if self.timestamps else None
        }


# Global market data cache
market_data_cache = MarketDataCache(ttl_minutes=30)


# Periodic cleanup (call this from a background task)
async def cleanup_caches():
    """Clean up expired cache entries"""
    market_data_cache.clear_expired()
    
    # Clean up general cache
    now = datetime.now()
    expired_keys = []
    
    for key, timestamp in _cache_timestamps.items():
        if (now - timestamp).seconds > 3600:  # 1 hour default
            expired_keys.append(key)
    
    for key in expired_keys:
        if key in _cache:
            del _cache[key]
        if key in _cache_timestamps:
            del _cache_timestamps[key]
    
    logger.info(f"Cache cleanup: removed {len(expired_keys)} expired entries")
