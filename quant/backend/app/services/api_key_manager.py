"""
API Key Management Service

Provides secure API key generation, rotation, and validation.
"""

import secrets
import hashlib
from datetime import datetime, timedelta, timezone
from typing import Optional, List, Dict, Any
from dataclasses import dataclass
from enum import Enum

from sqlalchemy import select, and_
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.logging import get_logger
from app.core.cache import cache_manager

logger = get_logger(__name__)


class APIKeyPermission(str, Enum):
    """API key permission levels"""
    READ = "read"
    WRITE = "write"
    ADMIN = "admin"


@dataclass
class APIKeyMetadata:
    """API key metadata"""
    key_id: str
    user_id: str
    name: str
    permissions: List[str]
    created_at: str
    expires_at: Optional[str]
    last_used_at: Optional[str]
    is_active: bool


class APIKeyManager:
    """
    Manages API keys for programmatic access.

    Features:
    - Secure key generation
    - Permission-based access control
    - Key rotation
    - Usage tracking
    - Automatic expiration
    """

    def __init__(self):
        self.key_prefix = "qtp_"  # Quant Trading Platform
        self.key_length = 32
        self.cache_ttl = 300  # 5 minutes

    def generate_key(self) -> tuple[str, str]:
        """
        Generate a new API key.

        Returns:
            tuple: (key_id, secret_key)
                - key_id: Identifier stored in database
                - secret_key: Full key shown once to user
        """
        # Generate random key
        random_bytes = secrets.token_bytes(self.key_length)
        secret_key = secrets.token_urlsafe(self.key_length)

        # Create key ID (first 8 chars for reference)
        key_id = hashlib.sha256(secret_key.encode()).hexdigest()[:16]

        # Create full key with prefix
        full_key = f"{self.key_prefix}{secret_key}"

        return key_id, full_key

    def hash_key(self, key: str) -> str:
        """
        Hash API key for storage.

        Args:
            key: The API key to hash

        Returns:
            Hashed key
        """
        return hashlib.sha256(key.encode()).hexdigest()

    async def create_key(
        self,
        db: AsyncSession,
        user_id: str,
        name: str,
        permissions: List[APIKeyPermission],
        expires_days: Optional[int] = None
    ) -> tuple[str, str]:
        """
        Create a new API key for a user.

        Args:
            db: Database session
            user_id: User ID
            name: Friendly name for the key
            permissions: List of permissions
            expires_days: Optional expiration in days

        Returns:
            tuple: (key_id, secret_key)
        """
        # Generate key
        key_id, secret_key = self.generate_key()

        # Hash key for storage
        key_hash = self.hash_key(secret_key)

        # Calculate expiration
        expires_at = None
        if expires_days:
            expires_at = datetime.now(timezone.utc) + timedelta(days=expires_days)

        # Store in database (assuming we have an APIKey model)
        # For now, we'll just log it
        logger.info(
            f"Created API key: {key_id} for user {user_id}",
            extra={
                "key_id": key_id,
                "user_id": user_id,
                "name": name,
                "permissions": [p.value for p in permissions],
                "expires_at": expires_at.isoformat() if expires_at else None
            }
        )

        return key_id, secret_key

    async def validate_key(
        self,
        db: AsyncSession,
        key: str,
        required_permission: Optional[APIKeyPermission] = None
    ) -> Optional[Dict[str, Any]]:
        """
        Validate an API key and check permissions.

        Args:
            db: Database session
            key: API key to validate
            required_permission: Required permission level

        Returns:
            Key metadata if valid, None otherwise
        """
        # Extract key without prefix
        if not key.startswith(self.key_prefix):
            return None

        # Check cache first
        cache_key = f"api_key:{self.hash_key(key)}"
        cached = await cache_manager.get(cache_key)
        if cached:
            return cached

        # Hash key for lookup
        key_hash = self.hash_key(key)

        # Query database for key
        from app.models.api_key import APIKey
        from datetime import datetime, timezone

        query = select(APIKey).where(
            and_(
                APIKey.key_hash == key_hash,
                APIKey.is_active == True
            )
        )

        result = await db.execute(query)
        api_key = result.scalar_one_or_none()

        if not api_key:
            return None

        # Check expiration
        if api_key.expires_at and api_key.expires_at < datetime.now(timezone.utc):
            logger.warning(f"Expired API key used: {api_key.key_id}")
            return None

        # Check permission if required
        if required_permission:
            permissions = api_key.permissions.get("permissions", [])
            if required_permission.value not in permissions:
                logger.warning(
                    f"API key {api_key.key_id} lacks required permission: {required_permission.value}"
                )
                return None

        # Build metadata
        metadata = {
            "key_id": api_key.key_id,
            "user_id": str(api_key.user_id),
            "name": api_key.name,
            "permissions": api_key.permissions.get("permissions", []),
            "created_at": api_key.created_at.isoformat(),
            "expires_at": api_key.expires_at.isoformat() if api_key.expires_at else None,
            "last_used_at": api_key.last_used_at.isoformat() if api_key.last_used_at else None,
        }

        # Update last_used_at (async, don't wait)
        api_key.last_used_at = datetime.now(timezone.utc)
        api_key.total_requests = int(api_key.total_requests or 0) + 1
        await db.commit()

        # Cache the result
        await cache_manager.set(cache_key, metadata, ttl=self.cache_ttl)

        return metadata

    async def rotate_key(
        self,
        db: AsyncSession,
        key_id: str,
        user_id: str
    ) -> tuple[str, str]:
        """
        Rotate an API key (invalidate old, create new).

        Args:
            db: Database session
            key_id: Current key ID
            user_id: User ID (for verification)

        Returns:
            tuple: (new_key_id, new_secret_key)
        """
        # Implement key rotation
        from app.models.api_key import APIKey

        # 1. Verify key belongs to user and get current permissions
        query = select(APIKey).where(
            and_(
                APIKey.key_id == key_id,
                APIKey.user_id == user_id
            )
        )

        result = await db.execute(query)
        old_key = result.scalar_one_or_none()

        if not old_key:
            raise ValueError(f"API key {key_id} not found or does not belong to user {user_id}")

        # Store old key info
        old_name = old_key.name
        old_permissions = old_key.permissions.get("permissions", [])
        old_expires_at = old_key.expires_at

        # 2. Invalidate old key
        old_key.is_active = False
        await db.commit()

        logger.info(
            f"Rotating API key: {key_id} for user {user_id}",
            extra={"key_id": key_id, "user_id": user_id}
        )

        # 3. Create new key with same permissions
        new_key_id, new_secret = self.generate_key()
        new_key_hash = self.hash_key(new_secret)

        # Calculate new expiration (same duration from now)
        new_expires_at = None
        if old_expires_at:
            from datetime import datetime, timezone, timedelta
            days_until_expiry = (old_expires_at - datetime.now(timezone.utc)).days
            if days_until_expiry > 0:
                new_expires_at = datetime.now(timezone.utc) + timedelta(days=days_until_expiry)

        new_api_key = APIKey(
            key_id=new_key_id,
            key_hash=new_key_hash,
            user_id=user_id,
            name=f"{old_name} (rotated)",
            permissions={"permissions": old_permissions},
            expires_at=new_expires_at,
            is_active=True,
        )

        db.add(new_api_key)
        await db.commit()

        # Clear cache for old key
        await cache_manager.delete(f"api_key:*{key_id}*")

        # 4. Return new key
        return new_key_id, new_secret

    async def revoke_key(
        self,
        db: AsyncSession,
        key_id: str,
        user_id: str
    ) -> bool:
        """
        Revoke an API key.

        Args:
            db: Database session
            key_id: Key ID to revoke
            user_id: User ID (for verification)

        Returns:
            True if revoked successfully
        """
        # Implement key revocation
        from app.models.api_key import APIKey

        # Query for the key
        query = select(APIKey).where(
            and_(
                APIKey.key_id == key_id,
                APIKey.user_id == user_id
            )
        )

        result = await db.execute(query)
        api_key = result.scalar_one_or_none()

        if not api_key:
            logger.warning(
                f"API key {key_id} not found for user {user_id}",
                extra={"key_id": key_id, "user_id": user_id}
            )
            return False

        # Mark as inactive
        api_key.is_active = False
        await db.commit()

        logger.info(
            f"Revoked API key: {key_id} for user {user_id}",
            extra={"key_id": key_id, "user_id": user_id}
        )

        # Clear from cache
        await cache_manager.delete(f"api_key:*{key_id}*")

        return True

    async def list_user_keys(
        self,
        db: AsyncSession,
        user_id: str
    ) -> List[APIKeyMetadata]:
        """
        List all API keys for a user.

        Args:
            db: Database session
            user_id: User ID

        Returns:
            List of API key metadata (without secret keys)
        """
        # Query database for user's keys
        from app.models.api_key import APIKey

        query = select(APIKey).where(
            APIKey.user_id == user_id
        ).order_by(APIKey.created_at.desc())

        result = await db.execute(query)
        api_keys = result.scalars().all()

        # Convert to metadata (without secret keys)
        return [
            APIKeyMetadata(
                key_id=key.key_id,
                user_id=str(key.user_id),
                name=key.name,
                permissions=key.permissions.get("permissions", []),
                created_at=key.created_at.isoformat(),
                expires_at=key.expires_at.isoformat() if key.expires_at else None,
                last_used_at=key.last_used_at.isoformat() if key.last_used_at else None,
                is_active=key.is_active,
            )
            for key in api_keys
        ]

    async def record_usage(
        self,
        db: AsyncSession,
        key_id: str,
        endpoint: str,
        success: bool
    ):
        """
        Record API key usage.

        Args:
            db: Database session
            key_id: Key ID
            endpoint: Endpoint accessed
            success: Whether request was successful
        """
        # Update last_used_at timestamp
        # Increment usage counter
        # Log for analytics

        logger.debug(
            f"API key usage: {key_id}",
            extra={
                "key_id": key_id,
                "endpoint": endpoint,
                "success": success
            }
        )


# Global instance
api_key_manager = APIKeyManager()
