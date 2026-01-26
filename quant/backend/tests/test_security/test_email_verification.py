"""
Tests for email verification features.

Tests cover:
- Email verification token generation
- Verification link handling
- Token expiration
- Resend rate limiting
"""

import pytest
from datetime import datetime, timedelta, timezone
from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import User
from app.core.security import get_password_hash, create_access_token
from app.core.email_verification import (
    generate_verification_token,
    is_token_expired,
    VERIFICATION_TOKEN_EXPIRE_HOURS,
)

pytestmark = pytest.mark.asyncio


class TestEmailVerificationUtilities:
    """Tests for email verification utility functions."""

    def test_generate_verification_token(self):
        """Test verification token generation."""
        token1 = generate_verification_token()
        token2 = generate_verification_token()

        # Tokens should be non-empty strings
        assert token1 and isinstance(token1, str)
        assert token2 and isinstance(token2, str)

        # Tokens should be unique
        assert token1 != token2

        # Tokens should be URL-safe
        assert all(c.isalnum() or c in "-_" for c in token1)

    def test_is_token_expired_none(self):
        """Test token expiration check with None."""
        assert is_token_expired(None) is True

    def test_is_token_expired_valid(self):
        """Test token expiration check with valid token."""
        # Token sent just now
        sent_at = datetime.now(timezone.utc)
        assert is_token_expired(sent_at) is False

        # Token sent 1 hour ago (within expiration)
        sent_at = datetime.now(timezone.utc) - timedelta(hours=1)
        assert is_token_expired(sent_at) is False

    def test_is_token_expired_expired(self):
        """Test token expiration check with expired token."""
        # Token sent more than VERIFICATION_TOKEN_EXPIRE_HOURS ago
        sent_at = datetime.now(timezone.utc) - timedelta(hours=VERIFICATION_TOKEN_EXPIRE_HOURS + 1)
        assert is_token_expired(sent_at) is True


class TestSendVerificationEmail:
    """Tests for send verification email endpoint."""

    async def test_send_verification_email_success(
        self, client: TestClient, test_user: User, db_session: AsyncSession
    ):
        """Test successfully sending verification email."""
        # Ensure email is not verified
        test_user.email_verified = False
        await db_session.commit()

        # Login
        login_response = client.post(
            "/api/v1/auth/login",
            json={"username": test_user.username, "password": "TestPassword123"},
        )
        token = login_response.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}

        # Request verification email
        response = client.post("/api/v1/auth/email/send-verification", headers=headers)

        assert response.status_code == 200
        data = response.json()
        assert "verification email sent" in data["message"].lower()
        assert data["email_verified"] is False

        # Check token was stored
        await db_session.refresh(test_user)
        assert test_user.email_verification_token is not None
        assert test_user.email_verification_sent_at is not None

    async def test_send_verification_email_already_verified(
        self, client: TestClient, test_user: User, db_session: AsyncSession
    ):
        """Test sending verification when already verified."""
        # Mark as verified
        test_user.email_verified = True
        await db_session.commit()

        # Login
        login_response = client.post(
            "/api/v1/auth/login",
            json={"username": test_user.username, "password": "TestPassword123"},
        )
        token = login_response.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}

        # Request verification email
        response = client.post("/api/v1/auth/email/send-verification", headers=headers)

        assert response.status_code == 200
        data = response.json()
        assert "already verified" in data["message"].lower()
        assert data["email_verified"] is True

    async def test_send_verification_email_rate_limited(
        self, client: TestClient, test_user: User, db_session: AsyncSession
    ):
        """Test rate limiting for verification email resend."""
        # Set verification sent recently (less than 5 minutes ago)
        test_user.email_verified = False
        test_user.email_verification_sent_at = datetime.now(timezone.utc) - timedelta(minutes=2)
        test_user.email_verification_token = generate_verification_token()
        await db_session.commit()

        # Login
        login_response = client.post(
            "/api/v1/auth/login",
            json={"username": test_user.username, "password": "TestPassword123"},
        )
        token = login_response.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}

        # Request verification email - should be rate limited
        response = client.post("/api/v1/auth/email/send-verification", headers=headers)

        assert response.status_code == 400
        assert "wait" in response.json()["detail"].lower()


class TestVerifyEmail:
    """Tests for email verification endpoint."""

    async def test_verify_email_success(
        self, client: TestClient, test_user: User, db_session: AsyncSession
    ):
        """Test successful email verification."""
        # Set up verification token
        verification_token = generate_verification_token()
        test_user.email_verified = False
        test_user.email_verification_token = verification_token
        test_user.email_verification_sent_at = datetime.now(timezone.utc)
        await db_session.commit()

        # Verify email
        response = client.post(
            "/api/v1/auth/email/verify",
            json={"token": verification_token},
        )

        assert response.status_code == 200
        data = response.json()
        assert "verified successfully" in data["message"].lower()
        assert data["email_verified"] is True

        # Check user is now verified
        await db_session.refresh(test_user)
        assert test_user.email_verified is True
        assert test_user.email_verification_token is None

    async def test_verify_email_invalid_token(
        self, client: TestClient, test_user: User, db_session: AsyncSession
    ):
        """Test email verification with invalid token."""
        # Set up verification token
        test_user.email_verified = False
        test_user.email_verification_token = generate_verification_token()
        test_user.email_verification_sent_at = datetime.now(timezone.utc)
        await db_session.commit()

        # Try to verify with wrong token
        response = client.post(
            "/api/v1/auth/email/verify",
            json={"token": "invalid-token-123"},
        )

        assert response.status_code == 400
        assert "invalid" in response.json()["detail"].lower()

    async def test_verify_email_expired_token(
        self, client: TestClient, test_user: User, db_session: AsyncSession
    ):
        """Test email verification with expired token."""
        # Set up expired verification token
        verification_token = generate_verification_token()
        test_user.email_verified = False
        test_user.email_verification_token = verification_token
        test_user.email_verification_sent_at = datetime.now(timezone.utc) - timedelta(
            hours=VERIFICATION_TOKEN_EXPIRE_HOURS + 1
        )
        await db_session.commit()

        # Try to verify with expired token
        response = client.post(
            "/api/v1/auth/email/verify",
            json={"token": verification_token},
        )

        assert response.status_code == 400
        assert "expired" in response.json()["detail"].lower()

    async def test_verify_email_already_verified(
        self, client: TestClient, test_user: User, db_session: AsyncSession
    ):
        """Test verification when already verified."""
        # Mark as verified but with token still present
        verification_token = generate_verification_token()
        test_user.email_verified = True
        test_user.email_verification_token = verification_token
        test_user.email_verification_sent_at = datetime.now(timezone.utc)
        await db_session.commit()

        # Try to verify again
        response = client.post(
            "/api/v1/auth/email/verify",
            json={"token": verification_token},
        )

        assert response.status_code == 200
        data = response.json()
        assert "already verified" in data["message"].lower()


class TestEmailVerificationIntegration:
    """Integration tests for email verification flow."""

    async def test_full_verification_flow(
        self, client: TestClient, test_user: User, db_session: AsyncSession
    ):
        """Test complete email verification flow."""
        # Ensure not verified
        test_user.email_verified = False
        await db_session.commit()

        # Login
        login_response = client.post(
            "/api/v1/auth/login",
            json={"username": test_user.username, "password": "TestPassword123"},
        )
        token = login_response.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}

        # Request verification email
        send_response = client.post("/api/v1/auth/email/send-verification", headers=headers)
        assert send_response.status_code == 200

        # Get the token from database
        await db_session.refresh(test_user)
        verification_token = test_user.email_verification_token

        # Verify email
        verify_response = client.post(
            "/api/v1/auth/email/verify",
            json={"token": verification_token},
        )
        assert verify_response.status_code == 200

        # Check user response includes verified status
        me_response = client.get("/api/v1/auth/me", headers=headers)
        assert me_response.status_code == 200
        assert me_response.json()["email_verified"] is True

    async def test_resend_after_rate_limit_expires(
        self, client: TestClient, test_user: User, db_session: AsyncSession
    ):
        """Test resending verification email after rate limit expires."""
        # Set verification sent more than 5 minutes ago
        test_user.email_verified = False
        test_user.email_verification_sent_at = datetime.now(timezone.utc) - timedelta(minutes=6)
        old_token = generate_verification_token()
        test_user.email_verification_token = old_token
        await db_session.commit()

        # Login
        login_response = client.post(
            "/api/v1/auth/login",
            json={"username": test_user.username, "password": "TestPassword123"},
        )
        token = login_response.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}

        # Request new verification email - should succeed
        response = client.post("/api/v1/auth/email/send-verification", headers=headers)
        assert response.status_code == 200

        # New token should be generated
        await db_session.refresh(test_user)
        assert test_user.email_verification_token != old_token

    async def test_user_response_includes_verification_status(
        self, client: TestClient, test_user: User, db_session: AsyncSession
    ):
        """Test that user response includes email_verified field."""
        # Unverified user
        test_user.email_verified = False
        await db_session.commit()

        login_response = client.post(
            "/api/v1/auth/login",
            json={"username": test_user.username, "password": "TestPassword123"},
        )
        token = login_response.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}

        me_response = client.get("/api/v1/auth/me", headers=headers)
        assert me_response.json()["email_verified"] is False

        # Verify user
        test_user.email_verified = True
        await db_session.commit()

        me_response = client.get("/api/v1/auth/me", headers=headers)
        assert me_response.json()["email_verified"] is True
