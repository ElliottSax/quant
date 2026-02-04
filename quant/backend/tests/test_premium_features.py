"""
Tests for Premium Features (Task #10)
"""

import pytest
from datetime import datetime, timedelta
from decimal import Decimal
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.alert import Alert, AlertType, AlertStatus
from app.models.portfolio import Portfolio, Watchlist
from app.models.subscription import Subscription, SubscriptionTier, SubscriptionStatus
from app.services.alert_service import alert_service
from app.services.portfolio_service import portfolio_service
from app.services.subscription_service import subscription_service


@pytest.mark.asyncio
class TestAlertService:
    """Test alert service."""

    async def test_create_alert(self, db_session: AsyncSession, test_user):
        """Test creating an alert."""
        alert = await alert_service.create_alert(
            db=db_session,
            user_id=str(test_user.id),
            name="Test Alert",
            alert_type=AlertType.TRADE,
            conditions={"ticker": "AAPL", "min_amount": 100000},
            notification_channels=["email"],
        )

        assert alert.id is not None
        assert alert.user_id == test_user.id
        assert alert.name == "Test Alert"
        assert alert.alert_type == AlertType.TRADE
        assert alert.status == AlertStatus.ACTIVE

    async def test_get_user_alerts(self, db_session: AsyncSession, test_user):
        """Test getting user alerts."""
        # Create multiple alerts
        await alert_service.create_alert(
            db=db_session,
            user_id=str(test_user.id),
            name="Alert 1",
            alert_type=AlertType.TRADE,
            conditions={},
            notification_channels=["email"],
        )

        await alert_service.create_alert(
            db=db_session,
            user_id=str(test_user.id),
            name="Alert 2",
            alert_type=AlertType.PRICE,
            conditions={},
            notification_channels=["webhook"],
        )

        # Get all alerts
        alerts = await alert_service.get_user_alerts(
            db=db_session,
            user_id=str(test_user.id),
        )

        assert len(alerts) == 2

        # Filter by type
        trade_alerts = await alert_service.get_user_alerts(
            db=db_session,
            user_id=str(test_user.id),
            alert_type=AlertType.TRADE,
        )

        assert len(trade_alerts) == 1

    async def test_delete_alert(self, db_session: AsyncSession, test_user):
        """Test deleting an alert."""
        alert = await alert_service.create_alert(
            db=db_session,
            user_id=str(test_user.id),
            name="Test Alert",
            alert_type=AlertType.TRADE,
            conditions={},
            notification_channels=["email"],
        )

        # Delete alert
        deleted = await alert_service.delete_alert(
            db=db_session,
            alert_id=str(alert.id),
            user_id=str(test_user.id),
        )

        assert deleted is True

        # Verify deleted
        alerts = await alert_service.get_user_alerts(
            db=db_session,
            user_id=str(test_user.id),
        )

        assert len(alerts) == 0

    async def test_update_alert(self, db_session: AsyncSession, test_user):
        """Test updating an alert."""
        alert = await alert_service.create_alert(
            db=db_session,
            user_id=str(test_user.id),
            name="Test Alert",
            alert_type=AlertType.TRADE,
            conditions={},
            notification_channels=["email"],
        )

        # Update alert
        updated = await alert_service.update_alert(
            db=db_session,
            alert_id=str(alert.id),
            user_id=str(test_user.id),
            name="Updated Alert",
            is_active=False,
        )

        assert updated is not None
        assert updated.name == "Updated Alert"
        assert updated.is_active is False


@pytest.mark.asyncio
class TestPortfolioService:
    """Test portfolio service."""

    async def test_create_watchlist(self, db_session: AsyncSession, test_user):
        """Test creating a watchlist."""
        watchlist = await portfolio_service.create_watchlist(
            db=db_session,
            user_id=str(test_user.id),
            name="My Watchlist",
            politician_ids=["pol1", "pol2", "pol3"],
        )

        assert watchlist.id is not None
        assert watchlist.user_id == test_user.id
        assert watchlist.name == "My Watchlist"
        assert len(watchlist.politician_ids) == 3

    async def test_get_user_watchlists(self, db_session: AsyncSession, test_user):
        """Test getting user watchlists."""
        # Create multiple watchlists
        await portfolio_service.create_watchlist(
            db=db_session,
            user_id=str(test_user.id),
            name="Watchlist 1",
            politician_ids=["pol1"],
        )

        await portfolio_service.create_watchlist(
            db=db_session,
            user_id=str(test_user.id),
            name="Watchlist 2",
            politician_ids=["pol2"],
        )

        # Get all watchlists
        watchlists = await portfolio_service.get_user_watchlists(
            db=db_session,
            user_id=str(test_user.id),
        )

        assert len(watchlists) == 2

    async def test_delete_watchlist(self, db_session: AsyncSession, test_user):
        """Test deleting a watchlist."""
        watchlist = await portfolio_service.create_watchlist(
            db=db_session,
            user_id=str(test_user.id),
            name="Test Watchlist",
            politician_ids=["pol1"],
        )

        # Delete watchlist
        deleted = await portfolio_service.delete_watchlist(
            db=db_session,
            watchlist_id=str(watchlist.id),
            user_id=str(test_user.id),
        )

        assert deleted is True

    async def test_update_watchlist(self, db_session: AsyncSession, test_user):
        """Test updating a watchlist."""
        watchlist = await portfolio_service.create_watchlist(
            db=db_session,
            user_id=str(test_user.id),
            name="Test Watchlist",
            politician_ids=["pol1"],
        )

        # Update watchlist
        updated = await portfolio_service.update_watchlist(
            db=db_session,
            watchlist_id=str(watchlist.id),
            user_id=str(test_user.id),
            name="Updated Watchlist",
            politician_ids=["pol1", "pol2"],
        )

        assert updated is not None
        assert updated.name == "Updated Watchlist"
        assert len(updated.politician_ids) == 2


@pytest.mark.asyncio
class TestSubscriptionService:
    """Test subscription service."""

    async def test_get_or_create_subscription(
        self, db_session: AsyncSession, test_user
    ):
        """Test getting or creating a subscription."""
        subscription = await subscription_service.get_or_create_subscription(
            db=db_session,
            user_id=str(test_user.id),
        )

        assert subscription.id is not None
        assert subscription.user_id == test_user.id
        assert subscription.tier == SubscriptionTier.FREE
        assert subscription.status == SubscriptionStatus.ACTIVE

    async def test_check_premium_access(self, db_session: AsyncSession, test_user):
        """Test checking premium access."""
        # Free tier should not have premium
        has_premium = await subscription_service.check_premium_access(
            db=db_session,
            user_id=str(test_user.id),
        )

        assert has_premium is False

        # Upgrade to premium
        await subscription_service.upgrade_subscription(
            db=db_session,
            user_id=str(test_user.id),
            new_tier=SubscriptionTier.PREMIUM,
        )

        # Check again
        has_premium = await subscription_service.check_premium_access(
            db=db_session,
            user_id=str(test_user.id),
        )

        assert has_premium is True

    async def test_check_rate_limit(self, db_session: AsyncSession, test_user):
        """Test checking rate limit."""
        # Create subscription
        await subscription_service.get_or_create_subscription(
            db=db_session,
            user_id=str(test_user.id),
        )

        # Check rate limit
        rate_limit = await subscription_service.check_rate_limit(
            db=db_session,
            user_id=str(test_user.id),
        )

        assert rate_limit["limit"] == 100  # Free tier
        assert rate_limit["used"] == 0
        assert rate_limit["remaining"] == 100

    async def test_record_usage(self, db_session: AsyncSession, test_user):
        """Test recording usage."""
        # Create subscription
        await subscription_service.get_or_create_subscription(
            db=db_session,
            user_id=str(test_user.id),
        )

        # Record usage
        await subscription_service.record_usage(
            db=db_session,
            user_id=str(test_user.id),
            resource_type="api_call",
            endpoint="/api/v1/trades",
            request_count=1,
        )

        # Check rate limit
        rate_limit = await subscription_service.check_rate_limit(
            db=db_session,
            user_id=str(test_user.id),
        )

        assert rate_limit["used"] == 1
        assert rate_limit["remaining"] == 99

    async def test_upgrade_subscription(self, db_session: AsyncSession, test_user):
        """Test upgrading subscription."""
        # Create free subscription
        subscription = await subscription_service.get_or_create_subscription(
            db=db_session,
            user_id=str(test_user.id),
        )

        assert subscription.tier == SubscriptionTier.FREE

        # Upgrade to premium
        updated = await subscription_service.upgrade_subscription(
            db=db_session,
            user_id=str(test_user.id),
            new_tier=SubscriptionTier.PREMIUM,
        )

        assert updated.tier == SubscriptionTier.PREMIUM
        assert updated.api_rate_limit == 10000  # Premium tier


# Fixtures
@pytest.fixture
async def test_user(db_session: AsyncSession):
    """Create a test user."""
    from app.models.user import User
    from app.security.password import get_password_hash

    user = User(
        email="test@example.com",
        username="testuser",
        hashed_password=get_password_hash("testpassword"),
        is_active=True,
    )

    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)

    return user
