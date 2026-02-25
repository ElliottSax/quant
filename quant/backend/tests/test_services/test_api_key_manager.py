"""Tests for API Key Manager service."""

import pytest
import re
from datetime import datetime, timedelta, timezone

from app.services.api_key_manager import APIKeyManager, APIKeyPermission, APIKeyMetadata


class TestAPIKeyManager:
    """Test cases for APIKeyManager."""

    @pytest.fixture
    def manager(self):
        """Create API key manager instance."""
        return APIKeyManager()

    async def test_initialization(self, manager):
        """Test manager initialization."""
        assert manager.key_prefix == "qtp_"
        assert manager.key_length == 32
        assert manager.cache_ttl == 300

    async def test_generate_key(self, manager):
        """Test API key generation."""
        key_id, secret_key = manager.generate_key()

        # Check key_id format
        assert isinstance(key_id, str)
        assert len(key_id) == 16  # First 16 chars of SHA-256 hash
        assert re.match(r"^[a-f0-9]{16}$", key_id)

        # Check secret_key format
        assert isinstance(secret_key, str)
        assert secret_key.startswith("qtp_")
        assert len(secret_key) > 40  # Prefix + URL-safe token

    async def test_generate_key_uniqueness(self, manager):
        """Test that generated keys are unique."""
        keys = set()
        for _ in range(100):
            key_id, secret_key = manager.generate_key()
            keys.add(secret_key)

        # All keys should be unique
        assert len(keys) == 100

    async def test_hash_key(self, manager):
        """Test key hashing."""
        key = "test_key_123"
        hash1 = manager.hash_key(key)
        hash2 = manager.hash_key(key)

        # Same input produces same hash
        assert hash1 == hash2

        # Hash is hex string
        assert isinstance(hash1, str)
        assert re.match(r"^[a-f0-9]{64}$", hash1)  # SHA-256 produces 64 hex chars

    async def test_hash_key_different_inputs(self, manager):
        """Test that different keys produce different hashes."""
        hash1 = manager.hash_key("key1")
        hash2 = manager.hash_key("key2")

        assert hash1 != hash2

    @pytest.mark.asyncio
    async def test_create_key(self, manager, db_session):
        """Test creating an API key."""
        key_id, secret_key = await manager.create_key(
            db=db_session,
            user_id="user123",
            name="Test API Key",
            permissions=[APIKeyPermission.READ, APIKeyPermission.WRITE]
        )

        assert isinstance(key_id, str)
        assert isinstance(secret_key, str)
        assert secret_key.startswith("qtp_")

    @pytest.mark.asyncio
    async def test_create_key_with_expiration(self, manager, db_session):
        """Test creating an API key with expiration."""
        key_id, secret_key = await manager.create_key(
            db=db_session,
            user_id="user123",
            name="Expiring Key",
            permissions=[APIKeyPermission.READ],
            expires_days=30
        )

        assert key_id is not None
        assert secret_key is not None

    @pytest.mark.asyncio
    async def test_create_key_with_different_permissions(self, manager, db_session):
        """Test creating keys with different permission levels."""
        # Read-only key
        key_id1, secret1 = await manager.create_key(
            db=db_session,
            user_id="user123",
            name="Read Only",
            permissions=[APIKeyPermission.READ]
        )
        assert key_id1 is not None

        # Write key
        key_id2, secret2 = await manager.create_key(
            db=db_session,
            user_id="user123",
            name="Read Write",
            permissions=[APIKeyPermission.READ, APIKeyPermission.WRITE]
        )
        assert key_id2 is not None

        # Admin key
        key_id3, secret3 = await manager.create_key(
            db=db_session,
            user_id="user123",
            name="Admin",
            permissions=[APIKeyPermission.ADMIN]
        )
        assert key_id3 is not None

        # All keys should be different
        assert len({secret1, secret2, secret3}) == 3

    @pytest.mark.asyncio
    async def test_validate_key_invalid_prefix(self, manager, db_session):
        """Test validating key with invalid prefix."""
        result = await manager.validate_key(
            db=db_session,
            key="invalid_prefix_key123"
        )

        assert result is None

    @pytest.mark.asyncio
    async def test_validate_key_valid_prefix(self, manager, db_session):
        """Test validating key with valid prefix (but not in DB)."""
        _, secret_key = manager.generate_key()

        result = await manager.validate_key(
            db=db_session,
            key=secret_key
        )

        # Should return None since key is not in database
        assert result is None

    @pytest.mark.asyncio
    async def test_rotate_key(self, manager, db_session):
        """Test key rotation."""
        old_key_id = "old_key_123"
        user_id = "user456"

        new_key_id, new_secret = await manager.rotate_key(
            db=db_session,
            key_id=old_key_id,
            user_id=user_id
        )

        # New key should be different from old
        assert new_key_id != old_key_id
        assert new_secret.startswith("qtp_")

    @pytest.mark.asyncio
    async def test_revoke_key(self, manager, db_session):
        """Test key revocation."""
        key_id = "key_to_revoke"
        user_id = "user789"

        result = await manager.revoke_key(
            db=db_session,
            key_id=key_id,
            user_id=user_id
        )

        assert result is True

    @pytest.mark.asyncio
    async def test_list_user_keys(self, manager, db_session):
        """Test listing user's API keys."""
        user_id = "user_with_keys"

        keys = await manager.list_user_keys(
            db=db_session,
            user_id=user_id
        )

        # Should return empty list (no database implementation yet)
        assert isinstance(keys, list)
        assert len(keys) == 0

    @pytest.mark.asyncio
    async def test_record_usage(self, manager, db_session):
        """Test recording API key usage."""
        # Should not raise any errors
        await manager.record_usage(
            db=db_session,
            key_id="key123",
            endpoint="/api/v1/trades",
            success=True
        )

        await manager.record_usage(
            db=db_session,
            key_id="key123",
            endpoint="/api/v1/politicians",
            success=False
        )

    async def test_api_key_permission_enum(self):
        """Test APIKeyPermission enum."""
        assert APIKeyPermission.READ.value == "read"
        assert APIKeyPermission.WRITE.value == "write"
        assert APIKeyPermission.ADMIN.value == "admin"

        # Test enum comparison
        assert APIKeyPermission.READ == APIKeyPermission.READ
        assert APIKeyPermission.READ != APIKeyPermission.WRITE

    async def test_api_key_metadata_dataclass(self):
        """Test APIKeyMetadata dataclass."""
        metadata = APIKeyMetadata(
            key_id="key123",
            user_id="user456",
            name="Test Key",
            permissions=["read", "write"],
            created_at="2024-01-01T00:00:00Z",
            expires_at="2024-12-31T23:59:59Z",
            last_used_at="2024-06-01T12:00:00Z",
            is_active=True
        )

        assert metadata.key_id == "key123"
        assert metadata.user_id == "user456"
        assert metadata.name == "Test Key"
        assert metadata.permissions == ["read", "write"]
        assert metadata.is_active is True

    async def test_hash_consistency(self, manager):
        """Test that hashing is consistent across multiple calls."""
        key = "consistent_key_test"
        hashes = [manager.hash_key(key) for _ in range(10)]

        # All hashes should be identical
        assert len(set(hashes)) == 1

    async def test_key_prefix_format(self, manager):
        """Test key prefix format."""
        for _ in range(10):
            _, secret_key = manager.generate_key()
            assert secret_key.startswith("qtp_")

    @pytest.mark.asyncio
    async def test_create_multiple_keys_same_user(self, manager, db_session):
        """Test creating multiple keys for same user."""
        user_id = "multi_key_user"
        keys = []

        for i in range(5):
            key_id, secret_key = await manager.create_key(
                db=db_session,
                user_id=user_id,
                name=f"Key {i}",
                permissions=[APIKeyPermission.READ]
            )
            keys.append((key_id, secret_key))

        # All keys should be unique
        key_ids = [k[0] for k in keys]
        secret_keys = [k[1] for k in keys]

        assert len(set(key_ids)) == 5
        assert len(set(secret_keys)) == 5

    async def test_permission_list_types(self):
        """Test different permission combinations."""
        permissions = [
            [APIKeyPermission.READ],
            [APIKeyPermission.WRITE],
            [APIKeyPermission.ADMIN],
            [APIKeyPermission.READ, APIKeyPermission.WRITE],
            [APIKeyPermission.READ, APIKeyPermission.WRITE, APIKeyPermission.ADMIN],
        ]

        for perm_list in permissions:
            assert all(isinstance(p, APIKeyPermission) for p in perm_list)
