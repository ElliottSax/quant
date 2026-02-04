"""Tests for User model."""

import uuid
from datetime import datetime, timedelta

import pytest
from sqlalchemy.exc import IntegrityError

from app.models.user import User


class TestUserModel:
    """Test cases for User model."""

    async def test_create_user(self, db_session):
        """Test creating a basic user."""
        user = User(
            email="test@example.com",
            username="testuser",
            hashed_password="hashedpass123",
        )
        db_session.add(user)
        await db_session.commit()
        await db_session.refresh(user)

        assert user.id is not None
        assert isinstance(user.id, uuid.UUID)
        assert user.email == "test@example.com"
        assert user.username == "testuser"
        assert user.hashed_password == "hashedpass123"
        assert user.is_active is True
        assert user.is_superuser is False
        assert user.email_verified is False
        assert user.totp_enabled is False
        assert user.failed_login_attempts == 0
        assert user.refresh_token_version == 0

    async def test_unique_email_constraint(self, db_session):
        """Test that email must be unique."""
        user1 = User(
            email="duplicate@example.com",
            username="user1",
            hashed_password="pass1",
        )
        db_session.add(user1)
        await db_session.commit()

        user2 = User(
            email="duplicate@example.com",
            username="user2",
            hashed_password="pass2",
        )
        db_session.add(user2)

        with pytest.raises(IntegrityError):
            await db_session.commit()

    async def test_unique_username_constraint(self, db_session):
        """Test that username must be unique."""
        user1 = User(
            email="email1@example.com",
            username="duplicate",
            hashed_password="pass1",
        )
        db_session.add(user1)
        await db_session.commit()

        user2 = User(
            email="email2@example.com",
            username="duplicate",
            hashed_password="pass2",
        )
        db_session.add(user2)

        with pytest.raises(IntegrityError):
            await db_session.commit()

    async def test_timestamps_auto_populated(self, db_session):
        """Test that created_at and updated_at are auto-populated."""
        user = User(
            email="timestamps@example.com",
            username="timestampuser",
            hashed_password="pass",
        )
        db_session.add(user)
        await db_session.commit()
        await db_session.refresh(user)

        assert user.created_at is not None
        assert user.updated_at is not None
        assert isinstance(user.created_at, datetime)
        assert isinstance(user.updated_at, datetime)

    async def test_last_login_nullable(self, db_session):
        """Test that last_login can be null initially."""
        user = User(
            email="login@example.com",
            username="loginuser",
            hashed_password="pass",
        )
        db_session.add(user)
        await db_session.commit()
        await db_session.refresh(user)

        assert user.last_login is None

    async def test_set_last_login(self, db_session):
        """Test setting last_login."""
        user = User(
            email="login2@example.com",
            username="loginuser2",
            hashed_password="pass",
        )
        db_session.add(user)
        await db_session.commit()

        login_time = datetime.utcnow()
        user.last_login = login_time
        await db_session.commit()
        await db_session.refresh(user)

        assert user.last_login is not None
        assert isinstance(user.last_login, datetime)

    async def test_superuser_flag(self, db_session):
        """Test creating a superuser."""
        user = User(
            email="admin@example.com",
            username="admin",
            hashed_password="adminpass",
            is_superuser=True,
        )
        db_session.add(user)
        await db_session.commit()
        await db_session.refresh(user)

        assert user.is_superuser is True

    async def test_inactive_user(self, db_session):
        """Test creating an inactive user."""
        user = User(
            email="inactive@example.com",
            username="inactive",
            hashed_password="pass",
            is_active=False,
        )
        db_session.add(user)
        await db_session.commit()
        await db_session.refresh(user)

        assert user.is_active is False

    async def test_refresh_token_version(self, db_session):
        """Test refresh token version management."""
        user = User(
            email="token@example.com",
            username="tokenuser",
            hashed_password="pass",
        )
        db_session.add(user)
        await db_session.commit()
        await db_session.refresh(user)

        assert user.refresh_token_version == 0

        # Increment token version (for token rotation)
        user.refresh_token_version += 1
        await db_session.commit()
        await db_session.refresh(user)

        assert user.refresh_token_version == 1

    async def test_failed_login_attempts(self, db_session):
        """Test tracking failed login attempts."""
        user = User(
            email="security@example.com",
            username="secureuser",
            hashed_password="pass",
        )
        db_session.add(user)
        await db_session.commit()

        # Increment failed attempts
        user.failed_login_attempts = 3
        await db_session.commit()
        await db_session.refresh(user)

        assert user.failed_login_attempts == 3

    async def test_account_lockout(self, db_session):
        """Test account lockout functionality."""
        user = User(
            email="locked@example.com",
            username="lockeduser",
            hashed_password="pass",
        )
        db_session.add(user)
        await db_session.commit()

        # Lock account for 30 minutes
        lockout_time = datetime.utcnow() + timedelta(minutes=30)
        user.locked_until = lockout_time
        user.failed_login_attempts = 5
        await db_session.commit()
        await db_session.refresh(user)

        assert user.locked_until is not None
        assert user.locked_until > datetime.utcnow()
        assert user.failed_login_attempts == 5

    async def test_email_verification(self, db_session):
        """Test email verification fields."""
        user = User(
            email="verify@example.com",
            username="verifyuser",
            hashed_password="pass",
            email_verification_token="token123",
            email_verification_sent_at=datetime.utcnow(),
        )
        db_session.add(user)
        await db_session.commit()
        await db_session.refresh(user)

        assert user.email_verified is False
        assert user.email_verification_token == "token123"
        assert user.email_verification_sent_at is not None

        # Mark as verified
        user.email_verified = True
        user.email_verification_token = None
        await db_session.commit()
        await db_session.refresh(user)

        assert user.email_verified is True
        assert user.email_verification_token is None

    async def test_two_factor_auth(self, db_session):
        """Test 2FA fields."""
        user = User(
            email="2fa@example.com",
            username="2fauser",
            hashed_password="pass",
            totp_enabled=True,
            totp_secret="secret123",
            totp_backup_codes='["code1", "code2", "code3"]',
        )
        db_session.add(user)
        await db_session.commit()
        await db_session.refresh(user)

        assert user.totp_enabled is True
        assert user.totp_secret == "secret123"
        assert user.totp_backup_codes is not None

    async def test_user_repr(self, db_session):
        """Test string representation of user."""
        user = User(
            email="repr@example.com",
            username="repruser",
            hashed_password="pass",
        )
        db_session.add(user)
        await db_session.commit()
        await db_session.refresh(user)

        repr_str = repr(user)
        assert "repruser" in repr_str
        assert "repr@example.com" in repr_str

    async def test_email_min_length_constraint(self, db_session):
        """Test that email must be at least 3 characters."""
        user = User(
            email="ab",  # Too short
            username="testuser",
            hashed_password="pass",
        )
        db_session.add(user)

        with pytest.raises(IntegrityError):
            await db_session.commit()

    async def test_username_min_length_constraint(self, db_session):
        """Test that username must be at least 3 characters."""
        user = User(
            email="test@example.com",
            username="ab",  # Too short
            hashed_password="pass",
        )
        db_session.add(user)

        with pytest.raises(IntegrityError):
            await db_session.commit()

    async def test_valid_email_and_username_length(self, db_session):
        """Test valid minimum lengths for email and username."""
        user = User(
            email="abc",  # Minimum valid length
            username="abc",  # Minimum valid length
            hashed_password="pass",
        )
        db_session.add(user)
        await db_session.commit()
        await db_session.refresh(user)

        assert user.email == "abc"
        assert user.username == "abc"
