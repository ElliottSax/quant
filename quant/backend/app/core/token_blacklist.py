"""
Token blacklist for invalidating JWT tokens on logout/password change.

Uses Redis to store blacklisted tokens until they expire naturally.
"""

from datetime import datetime, timedelta, timezone
from typing import Optional
import redis.asyncio as redis

from app.core.config import settings
from app.core.logging import get_logger
from jose import jwt

logger = get_logger(__name__)


class TokenBlacklist:
    """Manages blacklisted JWT tokens in Redis"""

    def __init__(self):
        self.redis_client: Optional[redis.Redis] = None
        self.enabled = settings.ENVIRONMENT in ["production", "development"]

    async def connect(self):
        """Connect to Redis"""
        if not self.enabled:
            logger.info("Token blacklist disabled in test environment")
            return

        try:
            # Use settings for Redis configuration
            self.redis_client = await redis.from_url(
                settings.REDIS_URL,
                encoding="utf-8",
                decode_responses=True
            )
            await self.redis_client.ping()
            logger.info("Token blacklist connected to Redis")
        except Exception as e:
            logger.warning(f"Failed to connect to Redis for blacklist: {e}")
            self.redis_client = None
            self.enabled = False

    async def close(self):
        """Close Redis connection"""
        if self.redis_client:
            await self.redis_client.close()
            logger.info("Token blacklist Redis connection closed")

    async def blacklist_token(self, token: str) -> bool:
        """
        Add token to blacklist.

        Args:
            token: JWT token to blacklist

        Returns:
            True if successfully blacklisted
        """
        if not self.enabled or not self.redis_client:
            logger.warning("Token blacklist not available")
            return False

        try:
            # Decode token to get expiration
            payload = jwt.decode(
                token,
                settings.SECRET_KEY,
                algorithms=[settings.ALGORITHM],
                options={"verify_exp": False}  # Don't verify exp since we just need it
            )

            exp_timestamp = payload.get("exp")
            if not exp_timestamp:
                logger.warning("Token has no expiration, cannot blacklist")
                return False

            exp_datetime = datetime.fromtimestamp(exp_timestamp, tz=timezone.utc)
            now = datetime.now(timezone.utc)

            # Only blacklist if not already expired
            if exp_datetime <= now:
                logger.debug("Token already expired, no need to blacklist")
                return True

            # Calculate TTL (time until token expires)
            ttl = int((exp_datetime - now).total_seconds())

            # Store in Redis with TTL matching token expiration
            key = f"blacklist:{token}"
            await self.redis_client.setex(key, ttl, "1")

            logger.info(f"Token blacklisted for {ttl} seconds")
            return True

        except Exception as e:
            logger.error(f"Failed to blacklist token: {e}")
            return False

    async def is_blacklisted(self, token: str) -> bool:
        """
        Check if token is blacklisted.

        Args:
            token: JWT token to check

        Returns:
            True if blacklisted
        """
        if not self.enabled or not self.redis_client:
            return False

        try:
            key = f"blacklist:{token}"
            exists = await self.redis_client.exists(key)
            return bool(exists)
        except Exception as e:
            logger.error(f"Failed to check blacklist: {e}")
            # Fail open - don't block valid tokens if Redis is down
            return False

    async def blacklist_user_tokens(self, user_id: str) -> bool:
        """
        Blacklist all tokens for a user (e.g., on password change).

        Since we don't track all user tokens, we add user to a blacklist
        with a TTL matching the refresh token expiration.

        Args:
            user_id: User ID to blacklist

        Returns:
            True if successful
        """
        if not self.enabled or not self.redis_client:
            logger.warning("Token blacklist not available")
            return False

        try:
            # Blacklist user for duration of longest token (refresh token)
            ttl = settings.REFRESH_TOKEN_EXPIRE_DAYS * 86400  # Convert to seconds

            key = f"user_blacklist:{user_id}"
            await self.redis_client.setex(key, ttl, "1")

            logger.info(f"All tokens for user {user_id} blacklisted for {ttl} seconds")
            return True

        except Exception as e:
            logger.error(f"Failed to blacklist user tokens: {e}")
            return False

    async def is_user_blacklisted(self, user_id: str) -> bool:
        """
        Check if all user tokens are blacklisted.

        Args:
            user_id: User ID to check

        Returns:
            True if user is blacklisted
        """
        if not self.enabled or not self.redis_client:
            return False

        try:
            key = f"user_blacklist:{user_id}"
            exists = await self.redis_client.exists(key)
            return bool(exists)
        except Exception as e:
            logger.error(f"Failed to check user blacklist: {e}")
            return False


# Global instance
token_blacklist = TokenBlacklist()
