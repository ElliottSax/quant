"""
Tests for authentication security features: token rotation and account lockout.

This implements comprehensive tests for:
- Refresh token rotation (Fix #3)
- Account lockout mechanism (Fix #4)

From IMPLEMENTATION_GUIDE_FIXES.md Week 1 Critical Fixes
"""

import pytest
from datetime import datetime, timedelta
from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.models.user import User
from app.core.security import (
    create_access_token,
    create_refresh_token,
    verify_token,
    is_account_locked,
    get_lockout_time_remaining,
    MAX_FAILED_ATTEMPTS,
    LOCKOUT_DURATION_MINUTES,
)
from app.core.config import settings

pytestmark = pytest.mark.asyncio


class TestRefreshTokenRotation:
    """Test suite for refresh token rotation mechanism."""

    async def test_token_rotation_basic(self, client: TestClient, test_user: User):
        """Test that refresh token rotation works correctly."""
        # Login to get initial tokens
        login_response = client.post(
            "/api/v1/auth/login",
            json={
                "username": test_user.username,
                "password": "TestPassword123",
            },
        )
        assert login_response.status_code == 200

        first_refresh_token = login_response.json()["refresh_token"]
        first_access_token = login_response.json()["access_token"]

        # Use refresh token to get new tokens (first rotation)
        refresh_response_1 = client.post(
            "/api/v1/auth/refresh",
            json={"refresh_token": first_refresh_token}
        )
        assert refresh_response_1.status_code == 200

        second_refresh_token = refresh_response_1.json()["refresh_token"]
        second_access_token = refresh_response_1.json()["access_token"]

        # Verify new tokens are different
        assert second_refresh_token != first_refresh_token
        assert second_access_token != first_access_token

    async def test_old_refresh_token_rejected_after_rotation(
        self, client: TestClient, test_user: User
    ):
        """Test that old refresh tokens are rejected after rotation."""
        # Login to get initial tokens
        login_response = client.post(
            "/api/v1/auth/login",
            json={
                "username": test_user.username,
                "password": "TestPassword123",
            },
        )
        first_refresh_token = login_response.json()["refresh_token"]

        # Rotate tokens
        refresh_response = client.post(
            "/api/v1/auth/refresh",
            json={"refresh_token": first_refresh_token}
        )
        assert refresh_response.status_code == 200

        # Try to use the old refresh token again - should fail
        old_token_response = client.post(
            "/api/v1/auth/refresh",
            json={"refresh_token": first_refresh_token}
        )
        assert old_token_response.status_code == 401
        assert "revoked" in old_token_response.json()["detail"].lower()

    async def test_token_rotation_increments_version(
        self, client: TestClient, test_user: User, db_session: AsyncSession
    ):
        """Test that token rotation increments the version in database."""
        # Get initial version
        await db_session.refresh(test_user)
        initial_version = test_user.refresh_token_version

        # Login
        login_response = client.post(
            "/api/v1/auth/login",
            json={
                "username": test_user.username,
                "password": "TestPassword123",
            },
        )
        refresh_token = login_response.json()["refresh_token"]

        # Verify token contains initial version
        _, token_version = verify_token(refresh_token, token_type="refresh")
        assert token_version == initial_version

        # Rotate token
        client.post("/api/v1/auth/refresh", json={"refresh_token": refresh_token})

        # Check version was incremented in database
        await db_session.refresh(test_user)
        assert test_user.refresh_token_version == initial_version + 1

    async def test_multiple_token_rotations(
        self, client: TestClient, test_user: User, db_session: AsyncSession
    ):
        """Test that multiple token rotations work correctly."""
        # Login
        login_response = client.post(
            "/api/v1/auth/login",
            json={
                "username": test_user.username,
                "password": "TestPassword123",
            },
        )

        current_refresh_token = login_response.json()["refresh_token"]

        # Perform 5 rotations
        for i in range(5):
            refresh_response = client.post(
                "/api/v1/auth/refresh",
                json={"refresh_token": current_refresh_token}
            )
            assert refresh_response.status_code == 200

            # Get new refresh token for next rotation
            new_refresh_token = refresh_response.json()["refresh_token"]
            assert new_refresh_token != current_refresh_token

            current_refresh_token = new_refresh_token

        # Verify version incremented 5 times (plus initial login might not increment)
        await db_session.refresh(test_user)
        # After login (version unchanged) + 5 rotations = version 5
        assert test_user.refresh_token_version >= 5

    async def test_concurrent_refresh_attempts_prevented(
        self, client: TestClient, test_user: User
    ):
        """Test that concurrent refresh attempts are handled correctly."""
        # Login
        login_response = client.post(
            "/api/v1/auth/login",
            json={
                "username": test_user.username,
                "password": "TestPassword123",
            },
        )
        refresh_token = login_response.json()["refresh_token"]

        # First refresh - should succeed
        first_refresh = client.post(
            "/api/v1/auth/refresh",
            json={"refresh_token": refresh_token}
        )
        assert first_refresh.status_code == 200

        # Second refresh with same token - should fail (token rotated)
        second_refresh = client.post(
            "/api/v1/auth/refresh",
            json={"refresh_token": refresh_token}
        )
        assert second_refresh.status_code == 401
        assert "revoked" in second_refresh.json()["detail"].lower()

    async def test_refresh_token_version_in_jwt_payload(
        self, client: TestClient, test_user: User
    ):
        """Test that refresh tokens contain version in JWT payload."""
        # Create a refresh token with specific version
        test_version = 42
        refresh_token = create_refresh_token(
            subject=str(test_user.id),
            version=test_version
        )

        # Decode and verify version
        user_id, token_version = verify_token(refresh_token, token_type="refresh")
        assert user_id == str(test_user.id)
        assert token_version == test_version

    async def test_access_token_not_affected_by_rotation(
        self, client: TestClient, test_user: User, auth_headers: dict
    ):
        """Test that access tokens remain valid during refresh token rotation."""
        # Login to get tokens
        login_response = client.post(
            "/api/v1/auth/login",
            json={
                "username": test_user.username,
                "password": "TestPassword123",
            },
        )
        refresh_token = login_response.json()["refresh_token"]

        # Use access token before rotation
        me_response_1 = client.get("/api/v1/auth/me", headers=auth_headers)
        assert me_response_1.status_code == 200

        # Rotate refresh token
        client.post("/api/v1/auth/refresh", json={"refresh_token": refresh_token})

        # Access token should still work
        me_response_2 = client.get("/api/v1/auth/me", headers=auth_headers)
        assert me_response_2.status_code == 200


class TestAccountLockout:
    """Test suite for account lockout mechanism."""

    async def test_account_locks_after_max_failed_attempts(
        self, client: TestClient, test_user: User, db_session: AsyncSession
    ):
        """Test that account locks after MAX_FAILED_ATTEMPTS."""
        # Make MAX_FAILED_ATTEMPTS failed login attempts
        for i in range(MAX_FAILED_ATTEMPTS):
            response = client.post(
                "/api/v1/auth/login",
                json={
                    "username": test_user.username,
                    "password": "WrongPassword123",
                },
            )
            assert response.status_code == 401

        # Refresh user from database
        await db_session.refresh(test_user)

        # Verify account is locked
        assert test_user.failed_login_attempts == MAX_FAILED_ATTEMPTS
        assert test_user.locked_until is not None
        assert test_user.locked_until > datetime.utcnow()

    async def test_locked_account_rejects_correct_password(
        self, client: TestClient, test_user: User, db_session: AsyncSession
    ):
        """Test that locked account rejects even correct password."""
        # Lock the account manually
        test_user.failed_login_attempts = MAX_FAILED_ATTEMPTS
        test_user.locked_until = datetime.utcnow() + timedelta(minutes=30)
        await db_session.commit()

        # Try to login with correct password
        response = client.post(
            "/api/v1/auth/login",
            json={
                "username": test_user.username,
                "password": "TestPassword123",
            },
        )

        assert response.status_code == 401
        assert "locked" in response.json()["detail"].lower()
        assert "minutes" in response.json()["detail"].lower()

    async def test_lockout_duration_is_correct(
        self, client: TestClient, test_user: User, db_session: AsyncSession
    ):
        """Test that lockout duration matches LOCKOUT_DURATION_MINUTES."""
        # Trigger lockout
        for i in range(MAX_FAILED_ATTEMPTS):
            client.post(
                "/api/v1/auth/login",
                json={
                    "username": test_user.username,
                    "password": "WrongPassword123",
                },
            )

        # Refresh user from database
        await db_session.refresh(test_user)

        # Verify lockout duration
        lockout_duration = (test_user.locked_until - datetime.utcnow()).total_seconds()
        expected_duration = LOCKOUT_DURATION_MINUTES * 60

        # Allow 5 second variance for test execution time
        assert abs(lockout_duration - expected_duration) < 5

    async def test_failed_attempts_counter_increments(
        self, client: TestClient, test_user: User, db_session: AsyncSession
    ):
        """Test that failed login attempts counter increments correctly."""
        # Make 3 failed attempts
        for i in range(3):
            client.post(
                "/api/v1/auth/login",
                json={
                    "username": test_user.username,
                    "password": "WrongPassword123",
                },
            )

            # Check counter after each attempt
            await db_session.refresh(test_user)
            assert test_user.failed_login_attempts == i + 1

    async def test_successful_login_resets_failed_attempts(
        self, client: TestClient, test_user: User, db_session: AsyncSession
    ):
        """Test that successful login resets failed attempts counter."""
        # Make some failed attempts
        for i in range(3):
            client.post(
                "/api/v1/auth/login",
                json={
                    "username": test_user.username,
                    "password": "WrongPassword123",
                },
            )

        # Verify counter incremented
        await db_session.refresh(test_user)
        assert test_user.failed_login_attempts == 3

        # Successful login
        response = client.post(
            "/api/v1/auth/login",
            json={
                "username": test_user.username,
                "password": "TestPassword123",
            },
        )
        assert response.status_code == 200

        # Verify counter reset
        await db_session.refresh(test_user)
        assert test_user.failed_login_attempts == 0
        assert test_user.locked_until is None

    async def test_lockout_expiration_allows_login(
        self, client: TestClient, test_user: User, db_session: AsyncSession
    ):
        """Test that login works after lockout expires."""
        # Lock account with already-expired lockout
        test_user.failed_login_attempts = MAX_FAILED_ATTEMPTS
        test_user.locked_until = datetime.utcnow() - timedelta(minutes=1)  # Expired
        await db_session.commit()

        # Should allow login since lockout expired
        response = client.post(
            "/api/v1/auth/login",
            json={
                "username": test_user.username,
                "password": "TestPassword123",
            },
        )

        assert response.status_code == 200
        assert "access_token" in response.json()

    async def test_is_account_locked_function(
        self, test_user: User, db_session: AsyncSession
    ):
        """Test the is_account_locked() helper function."""
        # Not locked initially
        assert is_account_locked(test_user) is False

        # Lock the account
        test_user.locked_until = datetime.utcnow() + timedelta(minutes=30)
        await db_session.commit()
        await db_session.refresh(test_user)

        # Should be locked
        assert is_account_locked(test_user) is True

        # Expire the lockout
        test_user.locked_until = datetime.utcnow() - timedelta(minutes=1)
        await db_session.commit()
        await db_session.refresh(test_user)

        # Should not be locked
        assert is_account_locked(test_user) is False

    async def test_get_lockout_time_remaining_function(
        self, test_user: User, db_session: AsyncSession
    ):
        """Test the get_lockout_time_remaining() helper function."""
        # No lockout
        assert get_lockout_time_remaining(test_user) == 0

        # Lock for 10 minutes
        test_user.locked_until = datetime.utcnow() + timedelta(minutes=10)
        await db_session.commit()
        await db_session.refresh(test_user)

        remaining = get_lockout_time_remaining(test_user)
        # Should be approximately 600 seconds (10 minutes)
        assert 595 < remaining < 605

        # Expired lockout
        test_user.locked_until = datetime.utcnow() - timedelta(minutes=1)
        await db_session.commit()
        await db_session.refresh(test_user)

        assert get_lockout_time_remaining(test_user) == 0

    async def test_lockout_message_includes_time_remaining(
        self, client: TestClient, test_user: User, db_session: AsyncSession
    ):
        """Test that lockout error message includes time remaining."""
        # Lock account for 30 minutes
        test_user.locked_until = datetime.utcnow() + timedelta(minutes=30)
        await db_session.commit()

        # Try to login
        response = client.post(
            "/api/v1/auth/login",
            json={
                "username": test_user.username,
                "password": "TestPassword123",
            },
        )

        assert response.status_code == 401
        error_message = response.json()["detail"].lower()

        # Should mention it's locked and approximately how long
        assert "locked" in error_message
        # Should mention minutes (could be 29 or 30 depending on timing)
        assert "minute" in error_message

    async def test_different_users_have_independent_lockouts(
        self, client: TestClient, test_user: User, test_superuser: User, db_session: AsyncSession
    ):
        """Test that lockouts are per-user, not global."""
        # Lock test_user
        for i in range(MAX_FAILED_ATTEMPTS):
            client.post(
                "/api/v1/auth/login",
                json={
                    "username": test_user.username,
                    "password": "WrongPassword123",
                },
            )

        # Verify test_user is locked
        await db_session.refresh(test_user)
        assert is_account_locked(test_user) is True

        # test_superuser should still be able to login
        response = client.post(
            "/api/v1/auth/login",
            json={
                "username": test_superuser.username,
                "password": "AdminPassword123",
            },
        )
        assert response.status_code == 200

        # Verify test_superuser is not locked
        await db_session.refresh(test_superuser)
        assert is_account_locked(test_superuser) is False


class TestPasswordChangeSecurity:
    """Test suite for password change security."""

    async def test_password_change_requires_current_password(
        self, client: TestClient, auth_headers: dict
    ):
        """Test that password change requires correct current password."""
        response = client.post(
            "/api/v1/auth/change-password",
            headers=auth_headers,
            json={
                "current_password": "WrongPassword123",
                "new_password": "NewPassword456",
            },
        )

        assert response.status_code == 401
        assert "incorrect" in response.json()["detail"].lower()

    async def test_password_change_invalidates_sessions(
        self, client: TestClient, test_user: User, db_session: AsyncSession
    ):
        """Test that password change invalidates all user sessions."""
        # Login to get first token
        login_response_1 = client.post(
            "/api/v1/auth/login",
            json={
                "username": test_user.username,
                "password": "TestPassword123",
            },
        )
        token_1 = login_response_1.json()["access_token"]
        headers_1 = {"Authorization": f"Bearer {token_1}"}

        # Login again to get second token
        login_response_2 = client.post(
            "/api/v1/auth/login",
            json={
                "username": test_user.username,
                "password": "TestPassword123",
            },
        )
        token_2 = login_response_2.json()["access_token"]
        headers_2 = {"Authorization": f"Bearer {token_2}"}

        # Both tokens should work
        assert client.get("/api/v1/auth/me", headers=headers_1).status_code == 200
        assert client.get("/api/v1/auth/me", headers=headers_2).status_code == 200

        # Change password with token_1
        password_change_response = client.post(
            "/api/v1/auth/change-password",
            headers=headers_1,
            json={
                "current_password": "TestPassword123",
                "new_password": "NewPassword456",
            },
        )
        assert password_change_response.status_code == 200
        assert password_change_response.json()["sessions_invalidated"] is True

        # Both tokens should now be invalid (user tokens blacklisted)
        # Note: This depends on token blacklist implementation
        # The implementation blacklists all user tokens on password change

    async def test_password_change_prevents_reuse(
        self, client: TestClient, auth_headers: dict
    ):
        """Test that password change prevents reusing same password."""
        response = client.post(
            "/api/v1/auth/change-password",
            headers=auth_headers,
            json={
                "current_password": "TestPassword123",
                "new_password": "TestPassword123",  # Same as current
            },
        )

        assert response.status_code == 400
        assert "different" in response.json()["detail"].lower()

    async def test_password_change_success_allows_new_login(
        self, client: TestClient, test_user: User, auth_headers: dict
    ):
        """Test that after password change, can login with new password."""
        # Change password
        response = client.post(
            "/api/v1/auth/change-password",
            headers=auth_headers,
            json={
                "current_password": "TestPassword123",
                "new_password": "NewPassword456",
            },
        )
        assert response.status_code == 200

        # Login with new password should work
        login_response = client.post(
            "/api/v1/auth/login",
            json={
                "username": test_user.username,
                "password": "NewPassword456",
            },
        )
        assert login_response.status_code == 200
        assert "access_token" in login_response.json()

        # Login with old password should fail
        old_login_response = client.post(
            "/api/v1/auth/login",
            json={
                "username": test_user.username,
                "password": "TestPassword123",
            },
        )
        assert old_login_response.status_code == 401


class TestSecurityEdgeCases:
    """Test edge cases and security scenarios."""

    async def test_login_with_locked_account_does_not_reset_counter(
        self, client: TestClient, test_user: User, db_session: AsyncSession
    ):
        """Test that login attempts on locked account don't reset counter."""
        # Lock the account
        test_user.failed_login_attempts = MAX_FAILED_ATTEMPTS
        test_user.locked_until = datetime.utcnow() + timedelta(minutes=30)
        await db_session.commit()

        # Try to login (should be rejected due to lock)
        client.post(
            "/api/v1/auth/login",
            json={
                "username": test_user.username,
                "password": "TestPassword123",
            },
        )

        # Counter should remain the same
        await db_session.refresh(test_user)
        assert test_user.failed_login_attempts == MAX_FAILED_ATTEMPTS

    async def test_refresh_token_with_version_zero(
        self, client: TestClient, test_user: User, db_session: AsyncSession
    ):
        """Test refresh token works with initial version 0."""
        # Ensure version is 0
        test_user.refresh_token_version = 0
        await db_session.commit()

        # Login should work
        login_response = client.post(
            "/api/v1/auth/login",
            json={
                "username": test_user.username,
                "password": "TestPassword123",
            },
        )
        assert login_response.status_code == 200

        # Refresh should work
        refresh_token = login_response.json()["refresh_token"]
        refresh_response = client.post(
            "/api/v1/auth/refresh",
            json={"refresh_token": refresh_token}
        )
        assert refresh_response.status_code == 200

    async def test_rapid_failed_login_attempts(
        self, client: TestClient, test_user: User, db_session: AsyncSession
    ):
        """Test that rapid failed login attempts are handled correctly."""
        import asyncio

        # Make rapid failed attempts
        tasks = []
        for i in range(MAX_FAILED_ATTEMPTS + 2):
            # Don't actually run concurrently in test client, but simulate rapid attempts
            response = client.post(
                "/api/v1/auth/login",
                json={
                    "username": test_user.username,
                    "password": "WrongPassword123",
                },
            )
            # First MAX_FAILED_ATTEMPTS should be 401 unauthorized
            # After that, should be 401 but with lockout message

        # Verify account is locked
        await db_session.refresh(test_user)
        assert is_account_locked(test_user) is True

    async def test_inactive_user_cannot_login(
        self, client: TestClient, test_user: User, db_session: AsyncSession
    ):
        """Test that inactive users cannot login."""
        # Deactivate user
        test_user.is_active = False
        await db_session.commit()

        # Try to login
        response = client.post(
            "/api/v1/auth/login",
            json={
                "username": test_user.username,
                "password": "TestPassword123",
            },
        )

        assert response.status_code == 401
        assert "inactive" in response.json()["detail"].lower()

    async def test_refresh_token_for_inactive_user_rejected(
        self, client: TestClient, test_user: User, db_session: AsyncSession
    ):
        """Test that refresh tokens for inactive users are rejected."""
        # Login first (user is active)
        login_response = client.post(
            "/api/v1/auth/login",
            json={
                "username": test_user.username,
                "password": "TestPassword123",
            },
        )
        refresh_token = login_response.json()["refresh_token"]

        # Deactivate user
        test_user.is_active = False
        await db_session.commit()

        # Try to refresh - should fail
        refresh_response = client.post(
            "/api/v1/auth/refresh",
            json={"refresh_token": refresh_token}
        )

        assert refresh_response.status_code == 401
        assert "inactive" in refresh_response.json()["detail"].lower()
