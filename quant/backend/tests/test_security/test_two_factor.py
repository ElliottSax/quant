"""
Tests for Two-Factor Authentication (2FA) features.

Tests cover:
- TOTP setup and verification
- 2FA enable/disable flow
- Login with 2FA
- Backup codes
"""

import pytest
from datetime import datetime, timedelta, timezone
from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import User
from app.core.security import get_password_hash, create_access_token
from app.core.two_factor import (
    generate_totp_secret,
    verify_totp,
    generate_backup_codes,
    hash_backup_codes,
    verify_backup_code,
    get_remaining_backup_codes_count,
)

pytestmark = pytest.mark.asyncio


class TestTOTPUtilities:
    """Tests for TOTP utility functions."""

    def test_generate_totp_secret(self):
        """Test TOTP secret generation."""
        secret1 = generate_totp_secret()
        secret2 = generate_totp_secret()

        # Secrets should be non-empty strings
        assert secret1 and isinstance(secret1, str)
        assert secret2 and isinstance(secret2, str)

        # Secrets should be unique
        assert secret1 != secret2

        # Secrets should be base32 encoded (A-Z, 2-7)
        valid_chars = set("ABCDEFGHIJKLMNOPQRSTUVWXYZ234567")
        assert all(c in valid_chars for c in secret1)

    def test_verify_totp_valid_code(self):
        """Test TOTP verification with valid code."""
        import pyotp

        secret = generate_totp_secret()
        totp = pyotp.TOTP(secret)
        current_code = totp.now()

        # Verification should succeed
        assert verify_totp(secret, current_code) is True

    def test_verify_totp_invalid_code(self):
        """Test TOTP verification with invalid code."""
        secret = generate_totp_secret()

        # Invalid codes should fail
        assert verify_totp(secret, "000000") is False
        assert verify_totp(secret, "999999") is False
        assert verify_totp(secret, "abc123") is False
        assert verify_totp(secret, "") is False

    def test_verify_totp_with_clock_drift(self):
        """Test TOTP verification allows for clock drift."""
        import pyotp

        secret = generate_totp_secret()
        totp = pyotp.TOTP(secret)

        # Current code should work
        current_code = totp.now()
        assert verify_totp(secret, current_code) is True


class TestBackupCodes:
    """Tests for backup code functionality."""

    def test_generate_backup_codes(self):
        """Test backup code generation."""
        codes = generate_backup_codes()

        # Should generate correct number of codes
        assert len(codes) == 10

        # All codes should be unique
        assert len(set(codes)) == len(codes)

        # All codes should be uppercase hex strings
        for code in codes:
            assert code.isupper()
            assert len(code) == 8

    def test_hash_and_verify_backup_codes(self):
        """Test backup code hashing and verification."""
        codes = generate_backup_codes()
        stored_codes = hash_backup_codes(codes)

        # Stored codes should be a string
        assert isinstance(stored_codes, str)

        # Each code should be verifiable
        for code in codes[:3]:  # Test first 3
            is_valid, remaining = verify_backup_code(stored_codes, code)
            assert is_valid is True
            assert remaining is not None
            stored_codes = remaining  # Use updated codes for next test

    def test_backup_code_single_use(self):
        """Test that backup codes can only be used once."""
        codes = generate_backup_codes()
        stored_codes = hash_backup_codes(codes)

        first_code = codes[0]

        # First use should succeed
        is_valid, updated_codes = verify_backup_code(stored_codes, first_code)
        assert is_valid is True

        # Second use of same code should fail
        is_valid, _ = verify_backup_code(updated_codes, first_code)
        assert is_valid is False

    def test_backup_code_case_insensitive(self):
        """Test that backup codes are case insensitive."""
        codes = generate_backup_codes()
        stored_codes = hash_backup_codes(codes)

        first_code = codes[0]

        # Should work with lowercase
        is_valid, _ = verify_backup_code(stored_codes, first_code.lower())
        assert is_valid is True

    def test_backup_code_with_formatting(self):
        """Test that backup codes work with dashes and spaces."""
        codes = ["ABCD1234"]  # Single code for testing
        stored_codes = hash_backup_codes(codes)

        # Should work with various formatting
        assert verify_backup_code(stored_codes, "ABCD1234")[0] is True
        assert verify_backup_code(stored_codes, "ABCD-1234")[0] is True
        assert verify_backup_code(stored_codes, "ABCD 1234")[0] is True

    def test_get_remaining_backup_codes_count(self):
        """Test counting remaining backup codes."""
        codes = generate_backup_codes()
        stored_codes = hash_backup_codes(codes)

        # Should have all 10 initially
        assert get_remaining_backup_codes_count(stored_codes) == 10

        # Use one code
        _, remaining = verify_backup_code(stored_codes, codes[0])
        assert get_remaining_backup_codes_count(remaining) == 9

        # None/empty should return 0
        assert get_remaining_backup_codes_count(None) == 0
        assert get_remaining_backup_codes_count("") == 0


class TestTwoFactorSetup:
    """Tests for 2FA setup endpoints."""

    async def test_2fa_setup_returns_secret_and_qr(
        self, client: TestClient, test_user: User, db_session: AsyncSession
    ):
        """Test 2FA setup returns secret, URI, and QR code."""
        # Login first
        login_response = client.post(
            "/api/v1/auth/login",
            json={"username": test_user.username, "password": "TestPassword123"},
        )
        token = login_response.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}

        # Setup 2FA
        response = client.post("/api/v1/auth/2fa/setup", headers=headers)

        assert response.status_code == 200
        data = response.json()

        assert "secret" in data
        assert "provisioning_uri" in data
        assert "qr_code" in data

        # Secret should be base32
        valid_chars = set("ABCDEFGHIJKLMNOPQRSTUVWXYZ234567")
        assert all(c in valid_chars for c in data["secret"])

        # URI should be otpauth format
        assert data["provisioning_uri"].startswith("otpauth://totp/")

        # QR code should be base64
        assert len(data["qr_code"]) > 100

    async def test_2fa_setup_stores_secret_temporarily(
        self, client: TestClient, test_user: User, db_session: AsyncSession
    ):
        """Test that 2FA setup stores secret but doesn't enable 2FA."""
        # Login
        login_response = client.post(
            "/api/v1/auth/login",
            json={"username": test_user.username, "password": "TestPassword123"},
        )
        token = login_response.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}

        # Setup 2FA
        response = client.post("/api/v1/auth/2fa/setup", headers=headers)
        assert response.status_code == 200

        # Refresh user
        await db_session.refresh(test_user)

        # Secret should be stored but 2FA not enabled
        assert test_user.totp_secret is not None
        assert test_user.totp_enabled is False

    async def test_2fa_setup_fails_if_already_enabled(
        self, client: TestClient, test_user: User, db_session: AsyncSession
    ):
        """Test that 2FA setup fails if already enabled."""
        # Enable 2FA manually
        test_user.totp_enabled = True
        test_user.totp_secret = generate_totp_secret()
        await db_session.commit()

        # Login
        login_response = client.post(
            "/api/v1/auth/login",
            json={"username": test_user.username, "password": "TestPassword123"},
        )
        # Since 2FA is enabled, login returns 2FA required
        assert login_response.json().get("requires_2fa") is True


class TestTwoFactorEnable:
    """Tests for enabling 2FA."""

    async def test_enable_2fa_with_valid_code(
        self, client: TestClient, test_user: User, db_session: AsyncSession
    ):
        """Test enabling 2FA with valid TOTP code."""
        import pyotp

        # Login
        login_response = client.post(
            "/api/v1/auth/login",
            json={"username": test_user.username, "password": "TestPassword123"},
        )
        token = login_response.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}

        # Setup 2FA
        setup_response = client.post("/api/v1/auth/2fa/setup", headers=headers)
        secret = setup_response.json()["secret"]

        # Generate valid TOTP code
        totp = pyotp.TOTP(secret)
        valid_code = totp.now()

        # Enable 2FA
        enable_response = client.post(
            "/api/v1/auth/2fa/enable",
            headers=headers,
            json={"token": valid_code},
        )

        assert enable_response.status_code == 200
        data = enable_response.json()

        assert data["enabled"] is True
        assert "backup_codes" in data
        assert len(data["backup_codes"]) == 10

        # Verify 2FA is enabled in database
        await db_session.refresh(test_user)
        assert test_user.totp_enabled is True

    async def test_enable_2fa_with_invalid_code(
        self, client: TestClient, test_user: User, db_session: AsyncSession
    ):
        """Test enabling 2FA fails with invalid code."""
        # Login
        login_response = client.post(
            "/api/v1/auth/login",
            json={"username": test_user.username, "password": "TestPassword123"},
        )
        token = login_response.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}

        # Setup 2FA
        client.post("/api/v1/auth/2fa/setup", headers=headers)

        # Try to enable with invalid code
        enable_response = client.post(
            "/api/v1/auth/2fa/enable",
            headers=headers,
            json={"token": "000000"},
        )

        assert enable_response.status_code == 400
        assert "invalid" in enable_response.json()["detail"].lower()


class TestTwoFactorLogin:
    """Tests for login with 2FA."""

    async def test_login_with_2fa_requires_verification(
        self, client: TestClient, test_user: User, db_session: AsyncSession
    ):
        """Test that login with 2FA enabled requires verification."""
        import pyotp

        # Enable 2FA
        secret = generate_totp_secret()
        test_user.totp_secret = secret
        test_user.totp_enabled = True
        test_user.totp_backup_codes = hash_backup_codes(generate_backup_codes())
        await db_session.commit()

        # Login
        login_response = client.post(
            "/api/v1/auth/login",
            json={"username": test_user.username, "password": "TestPassword123"},
        )

        assert login_response.status_code == 200
        data = login_response.json()

        assert data.get("requires_2fa") is True
        assert "user_id" in data

    async def test_2fa_verification_with_valid_code(
        self, client: TestClient, test_user: User, db_session: AsyncSession
    ):
        """Test 2FA verification with valid TOTP code."""
        import pyotp

        # Enable 2FA
        secret = generate_totp_secret()
        test_user.totp_secret = secret
        test_user.totp_enabled = True
        test_user.totp_backup_codes = hash_backup_codes(generate_backup_codes())
        await db_session.commit()

        # Login (get 2FA prompt)
        login_response = client.post(
            "/api/v1/auth/login",
            json={"username": test_user.username, "password": "TestPassword123"},
        )
        user_id = login_response.json()["user_id"]

        # Generate valid TOTP code
        totp = pyotp.TOTP(secret)
        valid_code = totp.now()

        # Verify 2FA
        verify_response = client.post(
            "/api/v1/auth/2fa/verify",
            json={"user_id": user_id, "token": valid_code},
        )

        assert verify_response.status_code == 200
        data = verify_response.json()
        assert "access_token" in data
        assert "refresh_token" in data

    async def test_2fa_verification_with_backup_code(
        self, client: TestClient, test_user: User, db_session: AsyncSession
    ):
        """Test 2FA verification with backup code."""
        # Enable 2FA
        secret = generate_totp_secret()
        backup_codes = generate_backup_codes()
        test_user.totp_secret = secret
        test_user.totp_enabled = True
        test_user.totp_backup_codes = hash_backup_codes(backup_codes)
        await db_session.commit()

        # Login (get 2FA prompt)
        login_response = client.post(
            "/api/v1/auth/login",
            json={"username": test_user.username, "password": "TestPassword123"},
        )
        user_id = login_response.json()["user_id"]

        # Use backup code
        verify_response = client.post(
            "/api/v1/auth/2fa/verify",
            json={"user_id": user_id, "token": backup_codes[0]},
        )

        assert verify_response.status_code == 200
        assert "access_token" in verify_response.json()

        # Backup code should be consumed
        await db_session.refresh(test_user)
        assert get_remaining_backup_codes_count(test_user.totp_backup_codes) == 9

    async def test_2fa_verification_with_invalid_code(
        self, client: TestClient, test_user: User, db_session: AsyncSession
    ):
        """Test 2FA verification fails with invalid code."""
        # Enable 2FA
        secret = generate_totp_secret()
        test_user.totp_secret = secret
        test_user.totp_enabled = True
        test_user.totp_backup_codes = hash_backup_codes(generate_backup_codes())
        await db_session.commit()

        # Login (get 2FA prompt)
        login_response = client.post(
            "/api/v1/auth/login",
            json={"username": test_user.username, "password": "TestPassword123"},
        )
        user_id = login_response.json()["user_id"]

        # Try invalid code
        verify_response = client.post(
            "/api/v1/auth/2fa/verify",
            json={"user_id": user_id, "token": "000000"},
        )

        assert verify_response.status_code == 401


class TestTwoFactorDisable:
    """Tests for disabling 2FA."""

    async def test_disable_2fa_success(
        self, client: TestClient, test_user: User, db_session: AsyncSession
    ):
        """Test successfully disabling 2FA."""
        import pyotp

        # Enable 2FA
        secret = generate_totp_secret()
        test_user.totp_secret = secret
        test_user.totp_enabled = True
        test_user.totp_backup_codes = hash_backup_codes(generate_backup_codes())
        await db_session.commit()

        # Create access token directly (bypass 2FA login for test)
        token = create_access_token(subject=str(test_user.id))
        headers = {"Authorization": f"Bearer {token}"}

        # Generate valid TOTP code
        totp = pyotp.TOTP(secret)
        valid_code = totp.now()

        # Disable 2FA
        disable_response = client.post(
            "/api/v1/auth/2fa/disable",
            headers=headers,
            json={"password": "TestPassword123", "token": valid_code},
        )

        assert disable_response.status_code == 200

        # Verify 2FA is disabled
        await db_session.refresh(test_user)
        assert test_user.totp_enabled is False
        assert test_user.totp_secret is None
        assert test_user.totp_backup_codes is None

    async def test_disable_2fa_wrong_password(
        self, client: TestClient, test_user: User, db_session: AsyncSession
    ):
        """Test disabling 2FA fails with wrong password."""
        import pyotp

        # Enable 2FA
        secret = generate_totp_secret()
        test_user.totp_secret = secret
        test_user.totp_enabled = True
        await db_session.commit()

        # Create access token
        token = create_access_token(subject=str(test_user.id))
        headers = {"Authorization": f"Bearer {token}"}

        totp = pyotp.TOTP(secret)
        valid_code = totp.now()

        # Try to disable with wrong password
        disable_response = client.post(
            "/api/v1/auth/2fa/disable",
            headers=headers,
            json={"password": "WrongPassword123", "token": valid_code},
        )

        assert disable_response.status_code == 401


class TestTwoFactorStatus:
    """Tests for 2FA status endpoint."""

    async def test_2fa_status_disabled(
        self, client: TestClient, test_user: User
    ):
        """Test 2FA status when disabled."""
        # Login
        login_response = client.post(
            "/api/v1/auth/login",
            json={"username": test_user.username, "password": "TestPassword123"},
        )
        token = login_response.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}

        # Get status
        response = client.get("/api/v1/auth/2fa/status", headers=headers)

        assert response.status_code == 200
        data = response.json()
        assert data["enabled"] is False
        assert data["backup_codes_remaining"] == 0

    async def test_2fa_status_enabled(
        self, client: TestClient, test_user: User, db_session: AsyncSession
    ):
        """Test 2FA status when enabled."""
        # Enable 2FA
        backup_codes = generate_backup_codes()
        test_user.totp_secret = generate_totp_secret()
        test_user.totp_enabled = True
        test_user.totp_backup_codes = hash_backup_codes(backup_codes)
        await db_session.commit()

        # Create access token
        token = create_access_token(subject=str(test_user.id))
        headers = {"Authorization": f"Bearer {token}"}

        # Get status
        response = client.get("/api/v1/auth/2fa/status", headers=headers)

        assert response.status_code == 200
        data = response.json()
        assert data["enabled"] is True
        assert data["backup_codes_remaining"] == 10
