"""
Integration tests for payment workflows.
Tests subscription creation, upgrades, and Stripe integration (mocked).
"""

import pytest
from unittest.mock import Mock, patch, AsyncMock
from fastapi import HTTPException
from decimal import Decimal
from datetime import datetime, timedelta
import uuid

from app.models.subscription import Subscription, SubscriptionTier, SubscriptionStatus
from app.models.user import User


class TestPaymentWorkflows:
    """Test complete payment workflows with mocked Stripe."""

    @pytest.mark.asyncio
    async def test_free_to_premium_upgrade_workflow(self, client, test_user, test_db):
        """Test complete workflow: free user upgrades to premium."""
        # Login as free user
        login_response = await client.post(
            "/api/v1/auth/login",
            json={"email": test_user.email, "password": "testpass123"}
        )
        assert login_response.status_code == 200
        token = login_response.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}

        # Check initial subscription status
        profile_response = await client.get("/api/v1/auth/me", headers=headers)
        assert profile_response.status_code == 200
        assert profile_response.json()["subscription_tier"] == "free"

        # Mock Stripe customer creation
        with patch("stripe.Customer.create") as mock_customer, \
             patch("stripe.Subscription.create") as mock_subscription:

            mock_customer.return_value = Mock(id="cus_test123")
            mock_subscription.return_value = Mock(
                id="sub_test123",
                status="active",
                current_period_start=int(datetime.utcnow().timestamp()),
                current_period_end=int((datetime.utcnow() + timedelta(days=30)).timestamp())
            )

            # Upgrade to premium
            upgrade_response = await client.post(
                "/api/v1/premium/subscribe",
                json={
                    "tier": "premium",
                    "billing_cycle": "monthly",
                    "payment_method": "pm_test_card"
                },
                headers=headers
            )
            assert upgrade_response.status_code == 200
            assert upgrade_response.json()["tier"] == "premium"

        # Verify subscription updated
        profile_response = await client.get("/api/v1/auth/me", headers=headers)
        assert profile_response.status_code == 200
        assert profile_response.json()["subscription_tier"] == "premium"

    @pytest.mark.asyncio
    async def test_payment_failure_rollback(self, client, test_user, test_db):
        """Test that failed payment doesn't upgrade subscription."""
        login_response = await client.post(
            "/api/v1/auth/login",
            json={"email": test_user.email, "password": "testpass123"}
        )
        token = login_response.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}

        # Mock Stripe payment failure
        with patch("stripe.Subscription.create") as mock_subscription:
            mock_subscription.side_effect = Exception("Payment failed: card declined")

            # Attempt upgrade
            upgrade_response = await client.post(
                "/api/v1/premium/subscribe",
                json={
                    "tier": "premium",
                    "billing_cycle": "monthly",
                    "payment_method": "pm_test_card"
                },
                headers=headers
            )
            assert upgrade_response.status_code == 400

        # Verify still on free tier
        profile_response = await client.get("/api/v1/auth/me", headers=headers)
        assert profile_response.json()["subscription_tier"] == "free"

    @pytest.mark.asyncio
    async def test_subscription_cancellation_workflow(self, client, premium_user, test_db):
        """Test subscription cancellation."""
        login_response = await client.post(
            "/api/v1/auth/login",
            json={"email": premium_user.email, "password": "testpass123"}
        )
        token = login_response.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}

        # Mock Stripe cancellation
        with patch("stripe.Subscription.modify") as mock_cancel:
            mock_cancel.return_value = Mock(
                id="sub_test123",
                status="canceled",
                cancel_at_period_end=True
            )

            # Cancel subscription
            cancel_response = await client.post(
                "/api/v1/premium/cancel",
                headers=headers
            )
            assert cancel_response.status_code == 200

        # Verify subscription marked for cancellation
        subscription_response = await client.get(
            "/api/v1/premium/subscription",
            headers=headers
        )
        assert subscription_response.json()["status"] == "cancelled"

    @pytest.mark.asyncio
    async def test_webhook_subscription_updated(self, client, test_db):
        """Test Stripe webhook for subscription update."""
        # Mock webhook event
        webhook_payload = {
            "type": "customer.subscription.updated",
            "data": {
                "object": {
                    "id": "sub_test123",
                    "customer": "cus_test123",
                    "status": "active",
                    "current_period_start": int(datetime.utcnow().timestamp()),
                    "current_period_end": int((datetime.utcnow() + timedelta(days=30)).timestamp())
                }
            }
        }

        with patch("stripe.Webhook.construct_event") as mock_verify:
            mock_verify.return_value = webhook_payload

            response = await client.post(
                "/api/v1/premium/webhook",
                json=webhook_payload,
                headers={"Stripe-Signature": "test_signature"}
            )
            assert response.status_code == 200

    @pytest.mark.asyncio
    async def test_trial_period_creation(self, client, test_user, test_db):
        """Test creating subscription with trial period."""
        login_response = await client.post(
            "/api/v1/auth/login",
            json={"email": test_user.email, "password": "testpass123"}
        )
        token = login_response.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}

        with patch("stripe.Subscription.create") as mock_subscription:
            trial_end = datetime.utcnow() + timedelta(days=14)
            mock_subscription.return_value = Mock(
                id="sub_test123",
                status="trialing",
                trial_start=int(datetime.utcnow().timestamp()),
                trial_end=int(trial_end.timestamp())
            )

            response = await client.post(
                "/api/v1/premium/start-trial",
                json={"tier": "premium"},
                headers=headers
            )
            assert response.status_code == 200
            assert response.json()["status"] == "trialing"

    @pytest.mark.asyncio
    async def test_upgrade_preserves_billing_cycle(self, client, basic_user, test_db):
        """Test upgrading from basic to premium preserves billing cycle."""
        login_response = await client.post(
            "/api/v1/auth/login",
            json={"email": basic_user.email, "password": "testpass123"}
        )
        token = login_response.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}

        with patch("stripe.Subscription.modify") as mock_upgrade:
            mock_upgrade.return_value = Mock(
                id="sub_test123",
                status="active"
            )

            response = await client.post(
                "/api/v1/premium/upgrade",
                json={"tier": "premium"},
                headers=headers
            )
            assert response.status_code == 200

            # Verify billing cycle wasn't changed
            subscription_response = await client.get(
                "/api/v1/premium/subscription",
                headers=headers
            )
            assert subscription_response.json()["billing_cycle"] == "monthly"


@pytest.fixture
async def premium_user(test_db):
    """Create a user with premium subscription."""
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
        status=SubscriptionStatus.ACTIVE,
        stripe_customer_id="cus_test123",
        stripe_subscription_id="sub_test123",
        billing_cycle="monthly",
        price_per_period=Decimal("29.99")
    )
    test_db.add(subscription)
    await test_db.commit()
    await test_db.refresh(user)
    return user


@pytest.fixture
async def basic_user(test_db):
    """Create a user with basic subscription."""
    user = User(
        email="basic@test.com",
        username="basicuser",
        is_active=True,
        is_verified=True
    )
    user.set_password("testpass123")
    test_db.add(user)

    subscription = Subscription(
        user_id=user.id,
        tier=SubscriptionTier.BASIC,
        status=SubscriptionStatus.ACTIVE,
        billing_cycle="monthly",
        price_per_period=Decimal("9.99")
    )
    test_db.add(subscription)
    await test_db.commit()
    await test_db.refresh(user)
    return user
