"""
Test data factories for creating test objects.
Makes it easy to create test data with sensible defaults.
"""

import uuid
from datetime import datetime, timedelta
from decimal import Decimal
import random
from typing import Optional

from app.models.user import User
from app.models.politician import Politician
from app.models.trade import Trade
from app.models.alert import Alert, AlertType, AlertStatus
from app.models.subscription import Subscription, SubscriptionTier, SubscriptionStatus
from app.models.api_key import APIKey
from app.models.device import MobileDevice
from app.models.portfolio import Portfolio, Watchlist


class UserFactory:
    """Factory for creating test users."""

    @staticmethod
    def create(
        email: Optional[str] = None,
        username: Optional[str] = None,
        password: str = "testpass123",
        is_active: bool = True,
        is_verified: bool = True,
        is_admin: bool = False,
        **kwargs
    ) -> User:
        """Create a test user."""
        if email is None:
            email = f"user{random.randint(1000, 9999)}@test.com"
        if username is None:
            username = f"user{random.randint(1000, 9999)}"

        user = User(
            email=email,
            username=username,
            is_active=is_active,
            is_verified=is_verified,
            is_admin=is_admin,
            **kwargs
        )
        user.set_password(password)
        return user

    @staticmethod
    def create_premium_user(**kwargs) -> User:
        """Create a user with premium subscription."""
        user = UserFactory.create(**kwargs)
        return user

    @staticmethod
    def create_admin_user(**kwargs) -> User:
        """Create an admin user."""
        return UserFactory.create(is_admin=True, **kwargs)


class PoliticianFactory:
    """Factory for creating test politicians."""

    PARTIES = ["Democrat", "Republican", "Independent"]
    CHAMBERS = ["Senate", "House"]
    STATES = ["CA", "NY", "TX", "FL", "IL", "PA", "OH", "GA", "NC", "MI"]

    @staticmethod
    def create(
        name: Optional[str] = None,
        party: Optional[str] = None,
        chamber: Optional[str] = None,
        state: Optional[str] = None,
        **kwargs
    ) -> Politician:
        """Create a test politician."""
        if name is None:
            first_names = ["John", "Jane", "Robert", "Mary", "James", "Patricia"]
            last_names = ["Smith", "Johnson", "Williams", "Brown", "Jones", "Garcia"]
            name = f"{random.choice(first_names)} {random.choice(last_names)}"

        if party is None:
            party = random.choice(PoliticianFactory.PARTIES)

        if chamber is None:
            chamber = random.choice(PoliticianFactory.CHAMBERS)

        if state is None:
            state = random.choice(PoliticianFactory.STATES)

        return Politician(
            name=name,
            party=party,
            chamber=chamber,
            state=state,
            **kwargs
        )


class TradeFactory:
    """Factory for creating test trades."""

    TICKERS = ["AAPL", "GOOGL", "MSFT", "TSLA", "AMZN", "META", "NVDA", "JPM", "V", "WMT"]
    TRANSACTION_TYPES = ["purchase", "sale"]

    @staticmethod
    def create(
        politician_id: Optional[uuid.UUID] = None,
        ticker: Optional[str] = None,
        transaction_type: Optional[str] = None,
        amount: Optional[float] = None,
        transaction_date: Optional[datetime] = None,
        **kwargs
    ) -> Trade:
        """Create a test trade."""
        if politician_id is None:
            politician_id = uuid.uuid4()

        if ticker is None:
            ticker = random.choice(TradeFactory.TICKERS)

        if transaction_type is None:
            transaction_type = random.choice(TradeFactory.TRANSACTION_TYPES)

        if amount is None:
            # Random amount between $1,000 and $1,000,000
            amount = random.uniform(1000, 1000000)

        if transaction_date is None:
            # Random date in last 90 days
            days_ago = random.randint(0, 90)
            transaction_date = datetime.utcnow() - timedelta(days=days_ago)

        return Trade(
            politician_id=politician_id,
            ticker=ticker,
            transaction_type=transaction_type,
            amount=amount,
            transaction_date=transaction_date,
            **kwargs
        )

    @staticmethod
    def create_large_trade(**kwargs) -> Trade:
        """Create a large trade (>$100k)."""
        return TradeFactory.create(amount=random.uniform(100000, 1000000), **kwargs)

    @staticmethod
    def create_small_trade(**kwargs) -> Trade:
        """Create a small trade (<$50k)."""
        return TradeFactory.create(amount=random.uniform(1000, 50000), **kwargs)


class AlertFactory:
    """Factory for creating test alerts."""

    @staticmethod
    def create(
        user_id: Optional[uuid.UUID] = None,
        name: Optional[str] = None,
        alert_type: AlertType = AlertType.TRADE,
        conditions: Optional[dict] = None,
        notification_channels: Optional[dict] = None,
        status: AlertStatus = AlertStatus.ACTIVE,
        **kwargs
    ) -> Alert:
        """Create a test alert."""
        if user_id is None:
            user_id = uuid.uuid4()

        if name is None:
            name = f"Test Alert {random.randint(1000, 9999)}"

        if conditions is None:
            if alert_type == AlertType.TRADE:
                conditions = {"min_amount": 100000}
            elif alert_type == AlertType.PRICE:
                conditions = {"ticker": "AAPL", "target_price": 150.00, "condition": "above"}

        if notification_channels is None:
            notification_channels = ["email"]

        return Alert(
            user_id=user_id,
            name=name,
            alert_type=alert_type,
            conditions=conditions,
            notification_channels=notification_channels,
            status=status,
            **kwargs
        )


class SubscriptionFactory:
    """Factory for creating test subscriptions."""

    @staticmethod
    def create(
        user_id: Optional[uuid.UUID] = None,
        tier: SubscriptionTier = SubscriptionTier.FREE,
        status: SubscriptionStatus = SubscriptionStatus.ACTIVE,
        **kwargs
    ) -> Subscription:
        """Create a test subscription."""
        if user_id is None:
            user_id = uuid.uuid4()

        return Subscription(
            user_id=user_id,
            tier=tier,
            status=status,
            **kwargs
        )

    @staticmethod
    def create_premium(user_id: Optional[uuid.UUID] = None, **kwargs) -> Subscription:
        """Create a premium subscription."""
        return SubscriptionFactory.create(
            user_id=user_id,
            tier=SubscriptionTier.PREMIUM,
            price_per_period=Decimal("29.99"),
            billing_cycle="monthly",
            **kwargs
        )

    @staticmethod
    def create_enterprise(user_id: Optional[uuid.UUID] = None, **kwargs) -> Subscription:
        """Create an enterprise subscription."""
        return SubscriptionFactory.create(
            user_id=user_id,
            tier=SubscriptionTier.ENTERPRISE,
            price_per_period=Decimal("99.99"),
            billing_cycle="monthly",
            **kwargs
        )


class APIKeyFactory:
    """Factory for creating test API keys."""

    @staticmethod
    def create(
        user_id: Optional[uuid.UUID] = None,
        name: Optional[str] = None,
        key_id: Optional[str] = None,
        key_hash: Optional[str] = None,
        permissions: Optional[dict] = None,
        is_active: bool = True,
        **kwargs
    ) -> APIKey:
        """Create a test API key."""
        if user_id is None:
            user_id = uuid.uuid4()

        if name is None:
            name = f"Test API Key {random.randint(1000, 9999)}"

        if key_id is None:
            key_id = f"pk_{random.randint(100000000000, 999999999999)}"

        if key_hash is None:
            # Generate a fake hash
            import hashlib
            key_hash = hashlib.sha256(f"testkey{random.randint(1000, 9999)}".encode()).hexdigest()

        if permissions is None:
            permissions = ["read:trades", "read:politicians"]

        return APIKey(
            user_id=user_id,
            name=name,
            key_id=key_id,
            key_hash=key_hash,
            permissions=permissions,
            is_active=is_active,
            **kwargs
        )


class MobileDeviceFactory:
    """Factory for creating test mobile devices."""

    DEVICE_TYPES = ["ios", "android"]
    MODELS = ["iPhone 13", "iPhone 14", "Pixel 7", "Galaxy S23", "OnePlus 11"]

    @staticmethod
    def create(
        user_id: Optional[uuid.UUID] = None,
        device_token: Optional[str] = None,
        device_type: Optional[str] = None,
        device_model: Optional[str] = None,
        app_version: str = "1.0.0",
        **kwargs
    ) -> MobileDevice:
        """Create a test mobile device."""
        if user_id is None:
            user_id = uuid.uuid4()

        if device_token is None:
            device_token = f"dt_{random.randint(100000000000, 999999999999)}"

        if device_type is None:
            device_type = random.choice(MobileDeviceFactory.DEVICE_TYPES)

        if device_model is None:
            device_model = random.choice(MobileDeviceFactory.MODELS)

        return MobileDevice(
            user_id=user_id,
            device_token=device_token,
            device_type=device_type,
            device_model=device_model,
            app_version=app_version,
            **kwargs
        )


class PortfolioFactory:
    """Factory for creating test portfolios."""

    @staticmethod
    def create(
        politician_id: Optional[uuid.UUID] = None,
        snapshot_date: Optional[datetime] = None,
        total_value: Optional[Decimal] = None,
        holdings: Optional[dict] = None,
        **kwargs
    ) -> Portfolio:
        """Create a test portfolio."""
        if politician_id is None:
            politician_id = uuid.uuid4()

        if snapshot_date is None:
            snapshot_date = datetime.utcnow()

        if total_value is None:
            total_value = Decimal(str(random.uniform(100000, 10000000)))

        if holdings is None:
            holdings = [
                {
                    "ticker": "AAPL",
                    "shares": 100,
                    "value": 15000,
                    "cost_basis": 14000
                }
            ]

        return Portfolio(
            politician_id=politician_id,
            snapshot_date=snapshot_date,
            total_value=total_value,
            holdings=holdings,
            **kwargs
        )


class WatchlistFactory:
    """Factory for creating test watchlists."""

    @staticmethod
    def create(
        user_id: Optional[uuid.UUID] = None,
        name: Optional[str] = None,
        politician_ids: Optional[dict] = None,
        **kwargs
    ) -> Watchlist:
        """Create a test watchlist."""
        if user_id is None:
            user_id = uuid.uuid4()

        if name is None:
            name = f"Test Watchlist {random.randint(1000, 9999)}"

        if politician_ids is None:
            politician_ids = [str(uuid.uuid4()) for _ in range(3)]

        return Watchlist(
            user_id=user_id,
            name=name,
            politician_ids=politician_ids,
            **kwargs
        )


# Convenience function to create multiple objects
def create_batch(factory_class, count: int, **kwargs):
    """Create multiple objects using a factory."""
    return [factory_class.create(**kwargs) for _ in range(count)]


# Usage examples in tests:
"""
# Create a single user
user = UserFactory.create()

# Create a user with specific attributes
user = UserFactory.create(email="specific@test.com", is_admin=True)

# Create a premium user
premium_user = UserFactory.create_premium_user()

# Create multiple politicians
politicians = create_batch(PoliticianFactory, 10)

# Create trades for a specific politician
trades = create_batch(TradeFactory, 20, politician_id=politician.id)

# Create a large trade
large_trade = TradeFactory.create_large_trade(politician_id=politician.id)

# Create an alert
alert = AlertFactory.create(user_id=user.id, alert_type=AlertType.PRICE)
"""
