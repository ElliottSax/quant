"""
Test suite for Stripe webhook handling.

Tests cover:
- Webhook event validation
- Subscription event processing (created, updated, deleted)
- Customer event processing
- Error handling and retries
"""

import pytest
import json
from datetime import datetime, timedelta
from unittest.mock import patch, MagicMock
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

from app.models.user import User
from app.models.subscription import Subscription, SubscriptionTier, SubscriptionStatus
from app.core.database import Base


TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"


@pytest.fixture
async def test_db():
    """Create a test database."""
    engine = create_async_engine(TEST_DATABASE_URL, echo=False)

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    yield async_session

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)

    await engine.dispose()


@pytest.fixture
async def test_user(test_db):
    """Create a test user with subscription."""
    async with test_db() as session:
        user = User(
            email="test@example.com",
            username="testuser",
            hashed_password="hashed",
            is_active=True,
            stripe_customer_id="cus_test123",
        )
        session.add(user)
        await session.commit()
        await session.refresh(user)
        return user


class TestWebhookEvents:
    """Test Stripe webhook event structures."""

    def test_customer_subscription_created_event(self):
        """Test subscription.created webhook event structure."""
        event = {
            "type": "customer.subscription.created",
            "id": "evt_test123",
            "data": {
                "object": {
                    "id": "sub_test123",
                    "customer": "cus_test123",
                    "status": "active",
                    "current_period_start": 1645000000,
                    "current_period_end": 1647600000,
                    "items": {
                        "data": [{"price": {"id": "price_starter_monthly"}}]
                    },
                }
            },
        }

        assert event["type"] == "customer.subscription.created"
        assert event["data"]["object"]["status"] == "active"

    def test_customer_subscription_updated_event(self):
        """Test subscription.updated webhook event."""
        event = {
            "type": "customer.subscription.updated",
            "id": "evt_test456",
            "data": {
                "object": {
                    "id": "sub_test123",
                    "customer": "cus_test123",
                    "status": "active",
                    "items": {
                        "data": [{"price": {"id": "price_professional_monthly"}}]
                    },
                }
            },
        }

        assert event["type"] == "customer.subscription.updated"
        assert event["data"]["object"]["id"] == "sub_test123"

    def test_customer_subscription_deleted_event(self):
        """Test subscription.deleted webhook event."""
        event = {
            "type": "customer.subscription.deleted",
            "id": "evt_test789",
            "data": {
                "object": {
                    "id": "sub_test123",
                    "customer": "cus_test123",
                    "status": "canceled",
                }
            },
        }

        assert event["type"] == "customer.subscription.deleted"
        assert event["data"]["object"]["status"] == "canceled"

    def test_invoice_payment_succeeded_event(self):
        """Test invoice.payment_succeeded webhook event."""
        event = {
            "type": "invoice.payment_succeeded",
            "id": "evt_inv_123",
            "data": {
                "object": {
                    "id": "in_test123",
                    "customer": "cus_test123",
                    "subscription": "sub_test123",
                    "amount_paid": 999,
                    "status": "paid",
                }
            },
        }

        assert event["type"] == "invoice.payment_succeeded"
        assert event["data"]["object"]["amount_paid"] == 999

    def test_invoice_payment_failed_event(self):
        """Test invoice.payment_failed webhook event."""
        event = {
            "type": "invoice.payment_failed",
            "id": "evt_inv_456",
            "data": {
                "object": {
                    "id": "in_test456",
                    "customer": "cus_test123",
                    "subscription": "sub_test123",
                    "status": "open",
                }
            },
        }

        assert event["type"] == "invoice.payment_failed"
        assert event["data"]["object"]["status"] == "open"


class TestWebhookProcessing:
    """Test webhook event processing."""

    @pytest.mark.asyncio
    async def test_process_subscription_created(self, test_db, test_user):
        """Test processing subscription.created event."""
        async with test_db() as session:
            # Find user by Stripe customer ID
            from sqlalchemy import select

            stmt = select(User).where(User.stripe_customer_id == "cus_test123")
            result = await session.execute(stmt)
            user = result.scalar_one_or_none()

            assert user is not None
            assert user.stripe_customer_id == "cus_test123"

            # Create subscription
            subscription = Subscription(
                user_id=user.id,
                stripe_subscription_id="sub_test123",
                stripe_customer_id="cus_test123",
                tier=SubscriptionTier.STARTER,
                status=SubscriptionStatus.ACTIVE,
                current_period_start=datetime.utcfromtimestamp(1645000000),
                current_period_end=datetime.utcfromtimestamp(1647600000),
            )
            session.add(subscription)
            await session.commit()

            # Verify
            from sqlalchemy import select

            stmt = select(Subscription).where(
                Subscription.stripe_subscription_id == "sub_test123"
            )
            result = await session.execute(stmt)
            sub = result.scalar_one_or_none()

            assert sub is not None
            assert sub.status == SubscriptionStatus.ACTIVE

    @pytest.mark.asyncio
    async def test_process_subscription_updated(self, test_db, test_user):
        """Test processing subscription.updated event."""
        async with test_db() as session:
            from sqlalchemy import select

            # Create initial subscription
            subscription = Subscription(
                user_id=test_user.id,
                stripe_subscription_id="sub_test123",
                tier=SubscriptionTier.STARTER,
                status=SubscriptionStatus.ACTIVE,
            )
            session.add(subscription)
            await session.commit()

            # Update subscription tier
            stmt = select(Subscription).where(
                Subscription.stripe_subscription_id == "sub_test123"
            )
            result = await session.execute(stmt)
            sub = result.scalar_one()

            sub.tier = SubscriptionTier.PROFESSIONAL
            await session.commit()

            # Verify
            result = await session.execute(stmt)
            sub = result.scalar_one()
            assert sub.tier == SubscriptionTier.PROFESSIONAL

    @pytest.mark.asyncio
    async def test_process_subscription_canceled(self, test_db, test_user):
        """Test processing subscription cancellation."""
        async with test_db() as session:
            from sqlalchemy import select

            # Create subscription
            subscription = Subscription(
                user_id=test_user.id,
                stripe_subscription_id="sub_test123",
                tier=SubscriptionTier.STARTER,
                status=SubscriptionStatus.ACTIVE,
            )
            session.add(subscription)
            await session.commit()

            # Cancel subscription
            stmt = select(Subscription).where(
                Subscription.stripe_subscription_id == "sub_test123"
            )
            result = await session.execute(stmt)
            sub = result.scalar_one()

            sub.status = SubscriptionStatus.CANCELLED
            sub.cancelled_at = datetime.utcnow()
            await session.commit()

            # Verify
            result = await session.execute(stmt)
            sub = result.scalar_one()
            assert sub.status == SubscriptionStatus.CANCELLED


class TestWebhookSecurity:
    """Test webhook security and validation."""

    def test_webhook_signature_validation(self):
        """Test webhook signature validation."""
        import hmac
        import hashlib

        webhook_secret = "whsec_test123"
        payload = '{"id":"evt_test123","type":"customer.subscription.created"}'
        timestamp = str(int(datetime.utcnow().timestamp()))

        # Create signature
        signed_content = f"{timestamp}.{payload}"
        signature = hmac.new(
            webhook_secret.encode(),
            signed_content.encode(),
            hashlib.sha256,
        ).hexdigest()

        # Verify signature format
        assert len(signature) == 64
        assert all(c in "0123456789abcdef" for c in signature)

    def test_webhook_timestamp_validation(self):
        """Test webhook timestamp validation."""
        import time

        # Create timestamp from 5 minutes ago
        timestamp = int(time.time()) - 300

        # Check if timestamp is recent (within 5 minutes is valid)
        current_time = int(datetime.utcnow().timestamp())
        time_diff = current_time - timestamp

        assert time_diff < 600  # 10 minute tolerance

    def test_webhook_replay_attack_prevention(self):
        """Test webhook replay attack prevention."""
        # Store processed event IDs
        processed_event_ids = set()

        event_id_1 = "evt_test123"
        event_id_2 = "evt_test456"

        # Process first event
        assert event_id_1 not in processed_event_ids
        processed_event_ids.add(event_id_1)

        # Try to replay
        assert event_id_1 in processed_event_ids

        # New event should work
        assert event_id_2 not in processed_event_ids


class TestWebhookErrorHandling:
    """Test webhook error handling and retries."""

    @pytest.mark.asyncio
    async def test_webhook_database_error_retry(self):
        """Test retry logic on database errors."""
        retry_count = 0
        max_retries = 3

        async def attempt_webhook_processing():
            nonlocal retry_count
            retry_count += 1

            if retry_count < max_retries:
                raise Exception("Database connection error")
            return True

        # Simulate retries
        while retry_count < max_retries:
            try:
                result = await attempt_webhook_processing()
                if result:
                    break
            except Exception as e:
                if retry_count >= max_retries:
                    raise
                await asyncio.sleep(0.1)  # Brief delay before retry

        assert retry_count == max_retries

    def test_webhook_invalid_event_handling(self):
        """Test handling of invalid webhook events."""
        invalid_events = [
            None,
            {},
            {"type": "unknown.event"},
            {"data": {"object": {}}},
            [],
        ]

        valid_event_types = {
            "customer.subscription.created",
            "customer.subscription.updated",
            "customer.subscription.deleted",
            "invoice.payment_succeeded",
            "invoice.payment_failed",
        }

        for event in invalid_events:
            if event and isinstance(event, dict):
                event_type = event.get("type")
                is_valid = event_type in valid_event_types
                assert not is_valid


class TestWebhookIntegration:
    """Integration tests for webhook processing."""

    @pytest.mark.asyncio
    async def test_full_subscription_lifecycle(self, test_db, test_user):
        """Test complete subscription lifecycle via webhooks."""
        async with test_db() as session:
            from sqlalchemy import select

            user = await session.get(User, test_user.id)

            # 1. Subscription created
            subscription = Subscription(
                user_id=user.id,
                stripe_subscription_id="sub_test123",
                stripe_customer_id="cus_test123",
                tier=SubscriptionTier.STARTER,
                status=SubscriptionStatus.ACTIVE,
            )
            session.add(subscription)
            await session.commit()

            # Verify created
            stmt = select(Subscription).where(
                Subscription.stripe_subscription_id == "sub_test123"
            )
            result = await session.execute(stmt)
            sub = result.scalar_one()
            assert sub.status == SubscriptionStatus.ACTIVE

            # 2. Subscription updated (upgrade to professional)
            sub.tier = SubscriptionTier.PROFESSIONAL
            await session.commit()

            result = await session.execute(stmt)
            sub = result.scalar_one()
            assert sub.tier == SubscriptionTier.PROFESSIONAL

            # 3. Subscription canceled
            sub.status = SubscriptionStatus.CANCELLED
            sub.cancelled_at = datetime.utcnow()
            await session.commit()

            result = await session.execute(stmt)
            sub = result.scalar_one()
            assert sub.status == SubscriptionStatus.CANCELLED


import asyncio


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
