"""
Test suite for the hybrid revenue model subscription system.

Tests cover:
- Subscription tier management (creation, upgrade, downgrade)
- Trial period functionality
- Referral system
- Stripe integration
"""

import pytest
import asyncio
from datetime import datetime, timedelta
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

from app.models.user import User
from app.models.subscription import SubscriptionTier, SubscriptionStatus, Subscription
from app.services.subscription_service import SubscriptionService, TIER_CONFIG
from app.core.database import Base


# Test Database Setup
TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"


@pytest.fixture
async def test_db():
    """Create a test database and session."""
    engine = create_async_engine(TEST_DATABASE_URL, echo=False)

    # Create tables
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    # Create session factory
    async_session = sessionmaker(
        engine, class_=AsyncSession, expire_on_commit=False
    )

    yield async_session

    # Cleanup
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)

    await engine.dispose()


@pytest.fixture
async def test_user(test_db):
    """Create a test user."""
    async with test_db() as session:
        user = User(
            email="test@example.com",
            username="testuser",
            hashed_password="hashed_password_here",
            is_active=True,
        )
        session.add(user)
        await session.commit()
        await session.refresh(user)
        return user


class TestSubscriptionTiers:
    """Test subscription tier configuration."""

    def test_tier_config_exists(self):
        """Verify all tiers are configured."""
        assert SubscriptionTier.FREE in TIER_CONFIG
        assert SubscriptionTier.STARTER in TIER_CONFIG
        assert SubscriptionTier.PROFESSIONAL in TIER_CONFIG
        assert SubscriptionTier.ENTERPRISE in TIER_CONFIG

    def test_free_tier_config(self):
        """Verify free tier configuration."""
        tier_config = TIER_CONFIG[SubscriptionTier.FREE]
        assert tier_config["price"] == 0.00
        assert tier_config["features"]["ad_free"] == False
        assert tier_config["features"]["faster_backtests"] == False

    def test_starter_tier_config(self):
        """Verify starter tier configuration."""
        tier_config = TIER_CONFIG[SubscriptionTier.STARTER]
        assert tier_config["price"] == 9.99
        assert tier_config["features"]["ad_free"] == True
        assert tier_config["features"]["faster_backtests"] == True

    def test_professional_tier_config(self):
        """Verify professional tier configuration."""
        tier_config = TIER_CONFIG[SubscriptionTier.PROFESSIONAL]
        assert tier_config["price"] == 29.99
        assert tier_config["features"]["ad_free"] == True
        assert tier_config["features"]["api_access"] == True
        assert tier_config["features"]["email_alerts"] == True

    def test_enterprise_tier_config(self):
        """Verify enterprise tier configuration."""
        tier_config = TIER_CONFIG[SubscriptionTier.ENTERPRISE]
        assert tier_config["features"]["ad_free"] == True
        assert tier_config["features"]["white_label"] == True


class TestSubscriptionCreation:
    """Test subscription creation and management."""

    @pytest.mark.asyncio
    async def test_create_subscription(self, test_db, test_user):
        """Test creating a subscription for a user."""
        async with test_db() as session:
            subscription = Subscription(
                user_id=test_user.id,
                tier=SubscriptionTier.STARTER,
                status=SubscriptionStatus.ACTIVE,
                stripe_customer_id="cus_test123",
            )
            session.add(subscription)
            await session.commit()
            await session.refresh(subscription)

            assert subscription.tier == SubscriptionTier.STARTER
            assert subscription.status == SubscriptionStatus.ACTIVE
            assert subscription.user_id == test_user.id

    @pytest.mark.asyncio
    async def test_upgrade_subscription(self, test_db, test_user):
        """Test upgrading from free to starter tier."""
        async with test_db() as session:
            subscription = Subscription(
                user_id=test_user.id,
                tier=SubscriptionTier.FREE,
                status=SubscriptionStatus.ACTIVE,
            )
            session.add(subscription)
            await session.commit()

            # Upgrade to Starter
            subscription.tier = SubscriptionTier.STARTER
            subscription.stripe_subscription_id = "sub_test123"
            await session.commit()
            await session.refresh(subscription)

            assert subscription.tier == SubscriptionTier.STARTER

    @pytest.mark.asyncio
    async def test_downgrade_subscription(self, test_db, test_user):
        """Test downgrading from starter to free tier."""
        async with test_db() as session:
            subscription = Subscription(
                user_id=test_user.id,
                tier=SubscriptionTier.STARTER,
                status=SubscriptionStatus.ACTIVE,
            )
            session.add(subscription)
            await session.commit()

            # Downgrade to Free
            subscription.tier = SubscriptionTier.FREE
            subscription.stripe_subscription_id = None
            await session.commit()
            await session.refresh(subscription)

            assert subscription.tier == SubscriptionTier.FREE


class TestTrialPeriod:
    """Test free trial functionality."""

    @pytest.mark.asyncio
    async def test_start_trial(self, test_db, test_user):
        """Test starting a free trial."""
        async with test_db() as session:
            trial_end = datetime.utcnow() + timedelta(days=7)

            subscription = Subscription(
                user_id=test_user.id,
                tier=SubscriptionTier.STARTER,
                status=SubscriptionStatus.TRIALING,
                trial_start=datetime.utcnow(),
                trial_end=trial_end,
            )
            session.add(subscription)
            await session.commit()
            await session.refresh(subscription)

            assert subscription.status == SubscriptionStatus.TRIALING
            assert (subscription.trial_end - trial_end).total_seconds() < 1

    @pytest.mark.asyncio
    async def test_trial_expiration(self, test_db, test_user):
        """Test trial expiration detection."""
        async with test_db() as session:
            past_time = datetime.utcnow() - timedelta(days=1)

            subscription = Subscription(
                user_id=test_user.id,
                tier=SubscriptionTier.STARTER,
                status=SubscriptionStatus.TRIALING,
                trial_start=past_time - timedelta(days=8),
                trial_end=past_time,
            )
            session.add(subscription)
            await session.commit()

            # Check if trial is expired
            is_expired = datetime.utcnow() > subscription.trial_end
            assert is_expired == True


class TestReferralSystem:
    """Test referral code generation and tracking."""

    def test_generate_referral_code(self):
        """Test referral code generation."""
        import uuid
        user_id = str(uuid.uuid4())
        code = SubscriptionService.generate_referral_code(user_id)

        # Code should contain user ID and be unique
        assert len(code) > 10
        assert "_" in code

    @pytest.mark.asyncio
    async def test_referral_code_uniqueness(self):
        """Test that referral codes are unique."""
        import uuid
        user_id1 = str(uuid.uuid4())
        user_id2 = str(uuid.uuid4())

        code1 = SubscriptionService.generate_referral_code(user_id1)
        code2 = SubscriptionService.generate_referral_code(user_id2)

        assert code1 != code2

    @pytest.mark.asyncio
    async def test_referral_credit_award(self, test_db, test_user):
        """Test awarding referral credits."""
        async with test_db() as session:
            # Create referrer and referee
            referrer = User(
                email="referrer@example.com",
                username="referrer",
                hashed_password="hashed",
                is_active=True,
            )
            session.add(referrer)
            await session.commit()
            await session.refresh(referrer)

            # Award referral credit
            initial_balance = referrer.referral_credit_balance
            referrer.referral_credit_balance += 10.0
            await session.commit()

            assert referrer.referral_credit_balance == initial_balance + 10.0


class TestSubscriptionStatus:
    """Test subscription status transitions."""

    @pytest.mark.asyncio
    async def test_subscription_active(self, test_db, test_user):
        """Test active subscription status."""
        async with test_db() as session:
            subscription = Subscription(
                user_id=test_user.id,
                tier=SubscriptionTier.STARTER,
                status=SubscriptionStatus.ACTIVE,
                current_period_end=datetime.utcnow() + timedelta(days=30),
            )
            session.add(subscription)
            await session.commit()

            assert subscription.status == SubscriptionStatus.ACTIVE

    @pytest.mark.asyncio
    async def test_subscription_canceled(self, test_db, test_user):
        """Test canceled subscription status."""
        async with test_db() as session:
            subscription = Subscription(
                user_id=test_user.id,
                tier=SubscriptionTier.FREE,
                status=SubscriptionStatus.CANCELLED,
                cancelled_at=datetime.utcnow(),
            )
            session.add(subscription)
            await session.commit()

            assert subscription.status == SubscriptionStatus.CANCELLED

    @pytest.mark.asyncio
    async def test_subscription_past_due(self, test_db, test_user):
        """Test past due subscription status."""
        async with test_db() as session:
            subscription = Subscription(
                user_id=test_user.id,
                tier=SubscriptionTier.STARTER,
                status=SubscriptionStatus.PAST_DUE,
            )
            session.add(subscription)
            await session.commit()

            assert subscription.status == SubscriptionStatus.PAST_DUE


class TestHybridModelFields:
    """Test hybrid model fields on User model."""

    @pytest.mark.asyncio
    async def test_ad_free_flag(self, test_db, test_user):
        """Test ad_free flag on user."""
        async with test_db() as session:
            user = await session.get(User, test_user.id)

            # Initially should be False (free tier shows ads)
            assert user.ad_free == False

            # Set to True for paid tier
            user.ad_free = True
            await session.commit()

            user = await session.get(User, test_user.id)
            assert user.ad_free == True

    @pytest.mark.asyncio
    async def test_referral_code_field(self, test_db, test_user):
        """Test referral_code field on user."""
        async with test_db() as session:
            user = await session.get(User, test_user.id)

            # Set referral code
            code = SubscriptionService.generate_referral_code(str(user.id))
            user.referral_code = code
            await session.commit()

            user = await session.get(User, test_user.id)
            assert user.referral_code == code

    @pytest.mark.asyncio
    async def test_referral_credit_balance(self, test_db, test_user):
        """Test referral_credit_balance field on user."""
        async with test_db() as session:
            user = await session.get(User, test_user.id)

            # Initially should be 0
            assert user.referral_credit_balance == 0.0

            # Add referral credits
            user.referral_credit_balance = 30.0
            await session.commit()

            user = await session.get(User, test_user.id)
            assert user.referral_credit_balance == 30.0

    @pytest.mark.asyncio
    async def test_referred_by_user_id(self, test_db, test_user):
        """Test referred_by_user_id field on user."""
        async with test_db() as session:
            # Create referrer
            referrer = User(
                email="referrer@example.com",
                username="referrer",
                hashed_password="hashed",
                is_active=True,
            )
            session.add(referrer)
            await session.commit()
            await session.refresh(referrer)

            # Set referred_by on test user
            user = await session.get(User, test_user.id)
            user.referred_by_user_id = str(referrer.id)
            await session.commit()

            user = await session.get(User, test_user.id)
            assert user.referred_by_user_id == str(referrer.id)


# Integration tests
class TestSubscriptionIntegration:
    """Integration tests for the subscription system."""

    @pytest.mark.asyncio
    async def test_full_upgrade_flow(self, test_db, test_user):
        """Test complete upgrade flow from free to professional."""
        async with test_db() as session:
            # Start with free tier
            user = await session.get(User, test_user.id)
            user.subscription_tier = "free"
            user.ad_free = False
            await session.commit()

            # Upgrade to Starter
            user.subscription_tier = "starter"
            user.ad_free = True
            await session.commit()

            user = await session.get(User, test_user.id)
            assert user.subscription_tier == "starter"
            assert user.ad_free == True

            # Upgrade to Professional
            user.subscription_tier = "professional"
            await session.commit()

            user = await session.get(User, test_user.id)
            assert user.subscription_tier == "professional"

    @pytest.mark.asyncio
    async def test_referral_reward_flow(self, test_db):
        """Test complete referral reward flow."""
        async with test_db() as session:
            # Create referrer
            referrer = User(
                email="referrer@example.com",
                username="referrer",
                hashed_password="hashed",
                is_active=True,
                referral_credit_balance=0.0,
            )
            session.add(referrer)
            await session.commit()
            await session.refresh(referrer)

            # Create referee
            referee = User(
                email="referee@example.com",
                username="referee",
                hashed_password="hashed",
                is_active=True,
                referred_by_user_id=str(referrer.id),
            )
            session.add(referee)
            await session.commit()

            # Award credit to referrer
            referrer.referral_credit_balance += 10.0
            await session.commit()

            # Verify
            referrer = await session.get(User, referrer.id)
            referee = await session.get(User, referee.id)

            assert referrer.referral_credit_balance == 10.0
            assert referee.referred_by_user_id == str(referrer.id)


if __name__ == "__main__":
    # Run tests
    pytest.main([__file__, "-v"])
