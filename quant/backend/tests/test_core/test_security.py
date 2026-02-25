"""Tests for core security module."""

import pytest
from datetime import datetime, timedelta, timezone

from app.core.security import (
    create_access_token,
    create_refresh_token,
    verify_token,
    verify_password,
    get_password_hash,
    is_account_locked,
    get_lockout_time_remaining,
    MAX_FAILED_ATTEMPTS,
    LOCKOUT_DURATION_MINUTES,
)


class TestPasswordHashing:
    """Tests for password hashing functions."""

    def test_password_hash_creates_unique_hashes(self):
        """Test that same password creates different hashes."""
        password = "TestPassword123"
        hash1 = get_password_hash(password)
        hash2 = get_password_hash(password)

        # Hashes should be different (bcrypt adds salt)
        assert hash1 != hash2

    def test_password_verification_success(self):
        """Test password verification with correct password."""
        password = "TestPassword123"
        hashed = get_password_hash(password)

        assert verify_password(password, hashed) is True

    def test_password_verification_failure(self):
        """Test password verification with incorrect password."""
        password = "TestPassword123"
        wrong_password = "WrongPassword123"
        hashed = get_password_hash(password)

        assert verify_password(wrong_password, hashed) is False

    def test_password_hash_not_plaintext(self):
        """Test that hash is not plaintext password."""
        password = "TestPassword123"
        hashed = get_password_hash(password)

        assert hashed != password
        assert password not in hashed

    def test_empty_password_verification(self):
        """Test verification with empty password."""
        password = "TestPassword123"
        hashed = get_password_hash(password)

        assert verify_password("", hashed) is False


class TestAccessToken:
    """Tests for access token functions."""

    def test_create_access_token_default_expiry(self):
        """Test access token creation with default expiry."""
        token = create_access_token(subject="user123")

        assert token is not None
        assert isinstance(token, str)
        assert len(token) > 50  # JWT tokens are long

    def test_create_access_token_custom_expiry(self):
        """Test access token with custom expiry."""
        token = create_access_token(
            subject="user123",
            expires_delta=timedelta(hours=1)
        )

        assert token is not None

    def test_verify_access_token_success(self):
        """Test successful access token verification."""
        user_id = "user123"
        token = create_access_token(subject=user_id)

        verified_id, version = verify_token(token, token_type="access")

        assert verified_id == user_id
        assert version is not None

    def test_verify_access_token_wrong_type(self):
        """Test access token fails when verified as refresh token."""
        token = create_access_token(subject="user123")

        verified_id, _ = verify_token(token, token_type="refresh")

        assert verified_id is None

    def test_verify_expired_access_token(self):
        """Test verification of expired token."""
        # Create token with -1 second expiry (already expired)
        token = create_access_token(
            subject="user123",
            expires_delta=timedelta(seconds=-1)
        )

        verified_id, _ = verify_token(token, token_type="access")

        assert verified_id is None

    def test_verify_invalid_token(self):
        """Test verification of invalid token."""
        verified_id, _ = verify_token("invalid.token.here", token_type="access")

        assert verified_id is None

    def test_verify_tampered_token(self):
        """Test verification of tampered token."""
        token = create_access_token(subject="user123")

        # Tamper with token
        tampered = token[:-5] + "xxxxx"

        verified_id, _ = verify_token(tampered, token_type="access")

        assert verified_id is None


class TestRefreshToken:
    """Tests for refresh token functions."""

    def test_create_refresh_token(self):
        """Test refresh token creation."""
        token = create_refresh_token(subject="user123")

        assert token is not None
        assert isinstance(token, str)

    def test_create_refresh_token_with_version(self):
        """Test refresh token with version."""
        token = create_refresh_token(subject="user123", version=5)

        verified_id, version = verify_token(token, token_type="refresh")

        assert verified_id == "user123"
        assert version == 5

    def test_verify_refresh_token_success(self):
        """Test successful refresh token verification."""
        user_id = "user123"
        token = create_refresh_token(subject=user_id, version=1)

        verified_id, version = verify_token(token, token_type="refresh")

        assert verified_id == user_id
        assert version == 1

    def test_verify_refresh_token_wrong_type(self):
        """Test refresh token fails when verified as access token."""
        token = create_refresh_token(subject="user123")

        verified_id, _ = verify_token(token, token_type="access")

        assert verified_id is None

    def test_refresh_token_version_zero(self):
        """Test refresh token with version 0."""
        token = create_refresh_token(subject="user123", version=0)

        verified_id, version = verify_token(token, token_type="refresh")

        assert verified_id == "user123"
        assert version == 0


class TestAccountLockout:
    """Tests for account lockout functions."""

    def test_is_account_locked_not_locked(self):
        """Test account that is not locked."""
        class MockUser:
            locked_until = None

        assert is_account_locked(MockUser()) is False

    def test_is_account_locked_active_lock(self):
        """Test account with active lock."""
        class MockUser:
            locked_until = datetime.now(timezone.utc) + timedelta(minutes=30)

        assert is_account_locked(MockUser()) is True

    def test_is_account_locked_expired_lock(self):
        """Test account with expired lock."""
        class MockUser:
            locked_until = datetime.now(timezone.utc) - timedelta(minutes=1)

        assert is_account_locked(MockUser()) is False

    def test_get_lockout_time_remaining_not_locked(self):
        """Test remaining time when not locked."""
        class MockUser:
            locked_until = None

        assert get_lockout_time_remaining(MockUser()) == 0

    def test_get_lockout_time_remaining_active_lock(self):
        """Test remaining time with active lock."""
        class MockUser:
            locked_until = datetime.now(timezone.utc) + timedelta(minutes=10)

        remaining = get_lockout_time_remaining(MockUser())
        assert 595 <= remaining <= 605  # ~600 seconds (10 min)

    def test_get_lockout_time_remaining_expired_lock(self):
        """Test remaining time with expired lock."""
        class MockUser:
            locked_until = datetime.now(timezone.utc) - timedelta(minutes=1)

        assert get_lockout_time_remaining(MockUser()) == 0

    def test_lockout_constants(self):
        """Test lockout constants are reasonable."""
        assert MAX_FAILED_ATTEMPTS >= 3
        assert MAX_FAILED_ATTEMPTS <= 10
        assert LOCKOUT_DURATION_MINUTES >= 5
        assert LOCKOUT_DURATION_MINUTES <= 60
