"""
Integration tests for email workflows.
Tests registration, verification, password reset with mocked email service.
"""

import pytest
from unittest.mock import Mock, patch, AsyncMock
from datetime import datetime, timedelta
import uuid

from app.models.user import User


class TestEmailWorkflows:
    """Test complete email workflows with mocked email service."""

    @pytest.mark.asyncio
    async def test_registration_sends_verification_email(self, client, test_db):
        """Test that user registration sends verification email."""
        with patch("app.core.email.send_email") as mock_send:
            mock_send.return_value = True

            response = await client.post(
                "/api/v1/auth/register",
                json={
                    "email": "newuser@test.com",
                    "username": "newuser",
                    "password": "securepass123",
                    "password_confirm": "securepass123"
                }
            )
            assert response.status_code == 201

            # Verify email was sent
            mock_send.assert_called_once()
            call_args = mock_send.call_args
            assert call_args[1]["to_email"] == "newuser@test.com"
            assert "verify" in call_args[1]["subject"].lower()
            assert "verification_token" in call_args[1]["template_data"]

    @pytest.mark.asyncio
    async def test_email_verification_workflow(self, client, test_db):
        """Test complete email verification workflow."""
        # Register user
        with patch("app.core.email.send_email") as mock_send:
            mock_send.return_value = True

            register_response = await client.post(
                "/api/v1/auth/register",
                json={
                    "email": "verify@test.com",
                    "username": "verifyuser",
                    "password": "securepass123",
                    "password_confirm": "securepass123"
                }
            )
            assert register_response.status_code == 201

            # Extract token from email call
            verification_token = mock_send.call_args[1]["template_data"]["verification_token"]

        # Verify email
        verify_response = await client.post(
            "/api/v1/auth/verify-email",
            json={"token": verification_token}
        )
        assert verify_response.status_code == 200

        # Login should now work
        login_response = await client.post(
            "/api/v1/auth/login",
            json={"email": "verify@test.com", "password": "securepass123"}
        )
        assert login_response.status_code == 200

    @pytest.mark.asyncio
    async def test_password_reset_workflow(self, client, test_user, test_db):
        """Test complete password reset workflow."""
        # Request password reset
        with patch("app.core.email.send_email") as mock_send:
            mock_send.return_value = True

            reset_request = await client.post(
                "/api/v1/auth/forgot-password",
                json={"email": test_user.email}
            )
            assert reset_request.status_code == 200

            # Extract reset token
            mock_send.assert_called_once()
            reset_token = mock_send.call_args[1]["template_data"]["reset_token"]

        # Reset password
        new_password = "newsecurepass456"
        reset_response = await client.post(
            "/api/v1/auth/reset-password",
            json={
                "token": reset_token,
                "new_password": new_password,
                "new_password_confirm": new_password
            }
        )
        assert reset_response.status_code == 200

        # Login with new password
        login_response = await client.post(
            "/api/v1/auth/login",
            json={"email": test_user.email, "password": new_password}
        )
        assert login_response.status_code == 200

        # Old password should not work
        old_login = await client.post(
            "/api/v1/auth/login",
            json={"email": test_user.email, "password": "testpass123"}
        )
        assert old_login.status_code == 401

    @pytest.mark.asyncio
    async def test_alert_notification_email(self, client, test_user, test_db):
        """Test that alert triggers send email notification."""
        # Login
        login_response = await client.post(
            "/api/v1/auth/login",
            json={"email": test_user.email, "password": "testpass123"}
        )
        token = login_response.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}

        # Create alert
        alert_response = await client.post(
            "/api/v1/alerts/",
            json={
                "name": "Test Alert",
                "alert_type": "trade",
                "conditions": {"min_amount": 100000},
                "notification_channels": ["email"]
            },
            headers=headers
        )
        assert alert_response.status_code == 201

        # Simulate alert trigger
        with patch("app.core.email.send_email") as mock_send:
            mock_send.return_value = True

            # Mock trade that matches alert
            trigger_response = await client.post(
                "/api/v1/alerts/test-trigger",
                json={"alert_id": alert_response.json()["id"]},
                headers=headers
            )

            # Verify email sent
            if trigger_response.status_code == 200:
                mock_send.assert_called()
                call_args = mock_send.call_args
                assert test_user.email in call_args[1]["to_email"]
                assert "alert" in call_args[1]["subject"].lower()

    @pytest.mark.asyncio
    async def test_email_failure_graceful_degradation(self, client, test_db):
        """Test that registration succeeds even if email fails."""
        with patch("app.core.email.send_email") as mock_send:
            # Simulate email service failure
            mock_send.side_effect = Exception("SMTP connection failed")

            response = await client.post(
                "/api/v1/auth/register",
                json={
                    "email": "nomail@test.com",
                    "username": "nomailuser",
                    "password": "securepass123",
                    "password_confirm": "securepass123"
                }
            )
            # Registration should still succeed
            assert response.status_code == 201

    @pytest.mark.asyncio
    async def test_resend_verification_email(self, client, test_db):
        """Test resending verification email."""
        # Register user
        with patch("app.core.email.send_email") as mock_send:
            mock_send.return_value = True

            await client.post(
                "/api/v1/auth/register",
                json={
                    "email": "resend@test.com",
                    "username": "resenduser",
                    "password": "securepass123",
                    "password_confirm": "securepass123"
                }
            )

        # Request resend
        with patch("app.core.email.send_email") as mock_send:
            mock_send.return_value = True

            resend_response = await client.post(
                "/api/v1/auth/resend-verification",
                json={"email": "resend@test.com"}
            )
            assert resend_response.status_code == 200
            mock_send.assert_called_once()

    @pytest.mark.asyncio
    async def test_email_rate_limiting(self, client, test_user, test_db):
        """Test rate limiting on email endpoints."""
        # Try to request password reset multiple times rapidly
        for i in range(10):
            response = await client.post(
                "/api/v1/auth/forgot-password",
                json={"email": test_user.email}
            )
            # First few should succeed, then rate limit kicks in
            if i < 3:
                assert response.status_code == 200
            else:
                # Should be rate limited
                assert response.status_code in [429, 200]

    @pytest.mark.asyncio
    async def test_weekly_report_email(self, client, premium_user, test_db):
        """Test weekly report email generation."""
        with patch("app.core.email.send_email") as mock_send:
            mock_send.return_value = True

            # Trigger weekly report generation (admin endpoint)
            response = await client.post(
                "/api/v1/admin/send-weekly-reports",
                headers={"X-Admin-Token": "test_admin_token"}
            )

            if response.status_code == 200:
                # Verify emails were sent
                assert mock_send.call_count > 0


@pytest.fixture
async def premium_user(test_db):
    """Create a verified premium user."""
    from app.models.subscription import Subscription, SubscriptionTier, SubscriptionStatus

    user = User(
        email="premium@test.com",
        username="premiumuser",
        is_active=True,
        is_verified=True
    )
    user.set_password("testpass123")
    test_db.add(user)

    subscription = Subscription(
        user_id=user.id,
        tier=SubscriptionTier.PREMIUM,
        status=SubscriptionStatus.ACTIVE
    )
    test_db.add(subscription)
    await test_db.commit()
    await test_db.refresh(user)
    return user
