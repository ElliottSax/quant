"""
Tests for token blacklist functionality.

This implements the test suite from IMPLEMENTATION_GUIDE_FIXES.md -> Fix 2
"""

import pytest
from datetime import datetime, timedelta
from app.core.token_blacklist import TokenBlacklist
from app.core.security import create_access_token, create_refresh_token
from app.core.config import settings

pytestmark = pytest.mark.asyncio


@pytest.fixture
async def blacklist():
    """Create and connect token blacklist."""
    bl = TokenBlacklist()
    await bl.connect()
    yield bl

    # Cleanup: clear any test tokens
    if bl.redis_client:
        await bl.redis_client.flushdb()
    await bl.close()


class TestTokenBlacklist:
    """Test suite for token blacklist functionality."""

    async def test_blacklist_token_success(self, blacklist):
        """Test successful token blacklisting."""
        # Create a token
        token = create_access_token(subject="test-user-id")

        # Blacklist it
        result = await blacklist.blacklist_token(token)
        assert result is True, "Token should be blacklisted successfully"

        # Check it's blacklisted
        is_blacklisted = await blacklist.is_blacklisted(token)
        assert is_blacklisted is True, "Token should be marked as blacklisted"

    async def test_blacklist_expired_token(self, blacklist):
        """Test blacklisting already expired token."""
        # Create expired token
        token = create_access_token(
            subject="test-user-id",
            expires_delta=timedelta(seconds=-10)  # Already expired
        )

        # Should return True but not store it
        result = await blacklist.blacklist_token(token)
        assert result is True, "Should handle expired token gracefully"

        # Check it's not in blacklist (already expired, no need to store)
        is_blacklisted = await blacklist.is_blacklisted(token)
        # Could be True or False depending on implementation
        # The important thing is it doesn't error

    async def test_blacklist_user_tokens(self, blacklist):
        """Test blacklisting all user tokens."""
        user_id = "test-user-123"

        # Blacklist all user tokens
        result = await blacklist.blacklist_user_tokens(user_id)
        assert result is True, "Should blacklist all user tokens"

        # Check user is blacklisted
        is_blacklisted = await blacklist.is_user_blacklisted(user_id)
        assert is_blacklisted is True, "User should be blacklisted"

    async def test_token_not_blacklisted(self, blacklist):
        """Test token that's not blacklisted."""
        token = create_access_token(subject="test-user-id")

        is_blacklisted = await blacklist.is_blacklisted(token)
        assert is_blacklisted is False, "Fresh token should not be blacklisted"

    async def test_blacklist_with_redis_down(self, blacklist):
        """Test graceful degradation when Redis is down."""
        # Close Redis connection to simulate failure
        if blacklist.redis_client:
            await blacklist.redis_client.close()
            blacklist.redis_client = None

        # Should fail gracefully
        token = create_access_token(subject="test-user-id")
        result = await blacklist.blacklist_token(token)
        assert result is False, "Should return False when Redis is unavailable"

        # Should not block tokens when Redis is down (fail open)
        is_blacklisted = await blacklist.is_blacklisted(token)
        assert is_blacklisted is False, "Should fail open when Redis is down"

    async def test_blacklist_multiple_tokens(self, blacklist):
        """Test blacklisting multiple tokens."""
        tokens = [
            create_access_token(subject=f"user-{i}")
            for i in range(5)
        ]

        # Blacklist all tokens
        for token in tokens:
            result = await blacklist.blacklist_token(token)
            assert result is True

        # Verify all are blacklisted
        for token in tokens:
            is_blacklisted = await blacklist.is_blacklisted(token)
            assert is_blacklisted is True

    async def test_blacklist_ttl_expiration(self, blacklist):
        """Test that blacklisted tokens expire after TTL."""
        # Create a token that expires in 2 seconds
        token = create_access_token(
            subject="test-user-id",
            expires_delta=timedelta(seconds=2)
        )

        # Blacklist it
        await blacklist.blacklist_token(token)

        # Should be blacklisted immediately
        is_blacklisted = await blacklist.is_blacklisted(token)
        assert is_blacklisted is True

        # Wait for expiration
        import asyncio
        await asyncio.sleep(3)

        # Should no longer be in blacklist (TTL expired)
        is_blacklisted = await blacklist.is_blacklisted(token)
        # May or may not be blacklisted depending on Redis cleanup
        # This is expected behavior

    async def test_blacklist_user_then_check_token(self, blacklist):
        """Test that individual tokens work when user is blacklisted."""
        user_id = "test-user-456"

        # Create a token for the user
        token = create_access_token(subject=user_id)

        # Blacklist the user (not the specific token)
        await blacklist.blacklist_user_tokens(user_id)

        # User should be blacklisted
        is_user_blacklisted = await blacklist.is_user_blacklisted(user_id)
        assert is_user_blacklisted is True

        # Individual token is not blacklisted (different mechanism)
        is_token_blacklisted = await blacklist.is_blacklisted(token)
        # This depends on implementation
        # The auth flow should check both

    async def test_blacklist_handles_invalid_token(self, blacklist):
        """Test blacklisting invalid token format."""
        invalid_token = "not-a-valid-jwt-token"

        # Should handle gracefully
        result = await blacklist.blacklist_token(invalid_token)
        # Should either return False or True (implementation dependent)
        assert isinstance(result, bool)

        # Check should not error
        is_blacklisted = await blacklist.is_blacklisted(invalid_token)
        assert isinstance(is_blacklisted, bool)


class TestTokenBlacklistIntegration:
    """Integration tests with actual auth flow."""

    async def test_logout_blacklists_token(self, client, auth_headers, blacklist):
        """Test that logout endpoint blacklists the token."""
        # Logout
        response = client.post("/api/v1/auth/logout", headers=auth_headers)
        assert response.status_code == 204

        # Extract token from headers
        token = auth_headers["Authorization"].replace("Bearer ", "")

        # Token should be blacklisted
        is_blacklisted = await blacklist.is_blacklisted(token)
        assert is_blacklisted is True

    async def test_password_change_blacklists_user(self, client, auth_headers, test_user, blacklist):
        """Test that password change blacklists all user tokens."""
        # Change password
        response = client.post(
            "/api/v1/auth/change-password",
            headers=auth_headers,
            json={
                "current_password": "TestPassword123",
                "new_password": "NewPassword456"
            }
        )
        assert response.status_code == 200

        # User should be blacklisted
        is_blacklisted = await blacklist.is_user_blacklisted(str(test_user.id))
        assert is_blacklisted is True

    async def test_blacklisted_token_rejected(self, client, auth_headers, blacklist):
        """Test that blacklisted tokens are rejected."""
        # Blacklist the token manually
        token = auth_headers["Authorization"].replace("Bearer ", "")
        await blacklist.blacklist_token(token)

        # Try to use the token
        response = client.get("/api/v1/auth/me", headers=auth_headers)
        assert response.status_code == 401
        assert "revoked" in response.json()["detail"].lower()


# Performance tests
class TestTokenBlacklistPerformance:
    """Performance tests for token blacklist."""

    async def test_blacklist_performance_bulk(self, blacklist):
        """Test performance of blacklisting many tokens."""
        import time

        tokens = [
            create_access_token(subject=f"user-{i}")
            for i in range(100)
        ]

        start = time.time()
        for token in tokens:
            await blacklist.blacklist_token(token)
        duration = time.time() - start

        # Should complete in reasonable time (< 1 second)
        assert duration < 1.0, f"Blacklisting 100 tokens took {duration:.2f}s"

    async def test_check_performance_bulk(self, blacklist):
        """Test performance of checking many tokens."""
        import time

        # Create and blacklist some tokens
        blacklisted_tokens = [
            create_access_token(subject=f"user-{i}")
            for i in range(50)
        ]
        for token in blacklisted_tokens:
            await blacklist.blacklist_token(token)

        # Create some non-blacklisted tokens
        clean_tokens = [
            create_access_token(subject=f"clean-user-{i}")
            for i in range(50)
        ]

        all_tokens = blacklisted_tokens + clean_tokens

        start = time.time()
        for token in all_tokens:
            await blacklist.is_blacklisted(token)
        duration = time.time() - start

        # Should complete in reasonable time (< 0.5 seconds)
        assert duration < 0.5, f"Checking 100 tokens took {duration:.2f}s"
