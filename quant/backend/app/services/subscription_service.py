"""
Subscription Service for managing premium subscriptions and Stripe integration.
"""

from typing import Optional, Dict, Any
from datetime import datetime, timedelta
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.models.subscription import (
    Subscription,
    SubscriptionTier,
    SubscriptionStatus,
    UsageRecord,
)
from app.models.user import User
from app.core.logging import get_logger
from app.core.config import settings

logger = get_logger(__name__)


# Subscription tier configuration
TIER_CONFIG = {
    SubscriptionTier.FREE: {
        "price": 0.00,
        "api_rate_limit": 100,  # requests per day
        "features": {
            "historical_data_months": 6,
            "alerts": 1,
            "watchlists": 1,
            "export_formats": ["json"],
            "advanced_analytics": False,
            "real_time_alerts": False,
            "portfolio_tracking": False,
        },
    },
    SubscriptionTier.BASIC: {
        "price": 9.99,
        "api_rate_limit": 1000,
        "features": {
            "historical_data_months": 24,
            "alerts": 10,
            "watchlists": 5,
            "export_formats": ["json", "csv"],
            "advanced_analytics": True,
            "real_time_alerts": True,
            "portfolio_tracking": False,
        },
    },
    SubscriptionTier.PREMIUM: {
        "price": 29.99,
        "api_rate_limit": 10000,
        "features": {
            "historical_data_months": 0,  # unlimited
            "alerts": 50,
            "watchlists": 20,
            "export_formats": ["json", "csv", "excel", "pdf"],
            "advanced_analytics": True,
            "real_time_alerts": True,
            "portfolio_tracking": True,
        },
    },
    SubscriptionTier.ENTERPRISE: {
        "price": 99.99,
        "api_rate_limit": 100000,
        "features": {
            "historical_data_months": 0,  # unlimited
            "alerts": 0,  # unlimited
            "watchlists": 0,  # unlimited
            "export_formats": ["json", "csv", "excel", "pdf"],
            "advanced_analytics": True,
            "real_time_alerts": True,
            "portfolio_tracking": True,
        },
    },
}


class SubscriptionService:
    """Service for managing subscriptions."""

    async def get_subscription(
        self,
        db: AsyncSession,
        user_id: str
    ) -> Optional[Subscription]:
        """
        Get user's subscription.

        Args:
            db: Database session
            user_id: User ID

        Returns:
            Subscription or None
        """
        query = select(Subscription).where(Subscription.user_id == user_id)
        result = await db.execute(query)
        return result.scalar_one_or_none()

    async def get_or_create_subscription(
        self,
        db: AsyncSession,
        user_id: str
    ) -> Subscription:
        """
        Get or create a subscription for a user.

        Args:
            db: Database session
            user_id: User ID

        Returns:
            Subscription
        """
        subscription = await self.get_subscription(db, user_id)

        if not subscription:
            # Create free tier subscription
            subscription = Subscription(
                user_id=user_id,
                tier=SubscriptionTier.FREE,
                status=SubscriptionStatus.ACTIVE,
                api_rate_limit=TIER_CONFIG[SubscriptionTier.FREE]["api_rate_limit"],
                features=TIER_CONFIG[SubscriptionTier.FREE]["features"],
            )

            db.add(subscription)
            await db.commit()
            await db.refresh(subscription)

            logger.info(f"Created free subscription for user {user_id}")

        return subscription

    async def check_premium_access(
        self,
        db: AsyncSession,
        user_id: str
    ) -> bool:
        """
        Check if user has premium access.

        Args:
            db: Database session
            user_id: User ID

        Returns:
            True if user has premium access
        """
        subscription = await self.get_subscription(db, user_id)

        if not subscription:
            return False

        # Check if subscription is active
        if subscription.status != SubscriptionStatus.ACTIVE:
            return False

        # Check tier
        return subscription.tier in [
            SubscriptionTier.BASIC,
            SubscriptionTier.PREMIUM,
            SubscriptionTier.ENTERPRISE,
        ]

    async def check_feature_access(
        self,
        db: AsyncSession,
        user_id: str,
        feature: str
    ) -> bool:
        """
        Check if user has access to a specific feature.

        Args:
            db: Database session
            user_id: User ID
            feature: Feature name

        Returns:
            True if user has access to feature
        """
        subscription = await self.get_or_create_subscription(db, user_id)

        features = subscription.features or {}

        return features.get(feature, False)

    async def get_rate_limit(
        self,
        db: AsyncSession,
        user_id: str
    ) -> int:
        """
        Get user's API rate limit.

        Args:
            db: Database session
            user_id: User ID

        Returns:
            Rate limit (requests per day)
        """
        subscription = await self.get_or_create_subscription(db, user_id)

        return subscription.api_rate_limit

    async def check_rate_limit(
        self,
        db: AsyncSession,
        user_id: str
    ) -> Dict[str, Any]:
        """
        Check user's current rate limit usage.

        Args:
            db: Database session
            user_id: User ID

        Returns:
            Rate limit status
        """
        subscription = await self.get_or_create_subscription(db, user_id)

        # Get today's usage
        today = datetime.utcnow().date()

        query = select(UsageRecord).where(
            UsageRecord.user_id == user_id,
            UsageRecord.usage_date >= today,
        )

        result = await db.execute(query)
        usage_records = result.scalars().all()

        total_requests = sum(int(record.request_count) for record in usage_records)

        rate_limit = subscription.api_rate_limit
        remaining = max(0, rate_limit - total_requests)

        return {
            "limit": rate_limit,
            "used": total_requests,
            "remaining": remaining,
            "reset_at": (datetime.utcnow() + timedelta(days=1)).replace(
                hour=0, minute=0, second=0, microsecond=0
            ).isoformat(),
        }

    async def record_usage(
        self,
        db: AsyncSession,
        user_id: Optional[str] = None,
        api_key_id: Optional[str] = None,
        resource_type: str = "api_call",
        endpoint: Optional[str] = None,
        request_count: int = 1
    ):
        """
        Record API usage.

        Args:
            db: Database session
            user_id: User ID (optional)
            api_key_id: API Key ID (optional)
            resource_type: Type of resource
            endpoint: Endpoint path (optional)
            request_count: Number of requests
        """
        usage = UsageRecord(
            user_id=user_id,
            api_key_id=api_key_id,
            resource_type=resource_type,
            endpoint=endpoint,
            request_count=request_count,
            usage_date=datetime.utcnow(),
        )

        db.add(usage)
        await db.commit()

    async def upgrade_subscription(
        self,
        db: AsyncSession,
        user_id: str,
        new_tier: SubscriptionTier
    ) -> Subscription:
        """
        Upgrade user's subscription tier.

        Args:
            db: Database session
            user_id: User ID
            new_tier: New subscription tier

        Returns:
            Updated subscription
        """
        subscription = await self.get_or_create_subscription(db, user_id)

        # Update tier
        subscription.tier = new_tier
        subscription.api_rate_limit = TIER_CONFIG[new_tier]["api_rate_limit"]
        subscription.features = TIER_CONFIG[new_tier]["features"]
        subscription.price_per_period = TIER_CONFIG[new_tier]["price"]

        await db.commit()
        await db.refresh(subscription)

        logger.info(f"Upgraded subscription for user {user_id} to {new_tier}")

        return subscription


class StripeService:
    """Service for Stripe payment integration."""

    def __init__(self):
        self.stripe_enabled = False
        try:
            import stripe
            self.stripe = stripe
            if hasattr(settings, 'STRIPE_SECRET_KEY'):
                self.stripe.api_key = settings.STRIPE_SECRET_KEY
                self.stripe_enabled = True
        except ImportError:
            logger.warning("Stripe library not installed")

    async def create_customer(
        self,
        db: AsyncSession,
        user: User
    ) -> Optional[str]:
        """
        Create a Stripe customer.

        Args:
            db: Database session
            user: User

        Returns:
            Stripe customer ID or None
        """
        if not self.stripe_enabled:
            logger.warning("Stripe is not enabled")
            return None

        try:
            customer = self.stripe.Customer.create(
                email=user.email,
                name=user.username,
                metadata={
                    "user_id": str(user.id),
                },
            )

            logger.info(f"Created Stripe customer {customer.id} for user {user.id}")

            return customer.id

        except Exception as e:
            logger.error(f"Failed to create Stripe customer: {e}")
            return None

    async def create_subscription(
        self,
        db: AsyncSession,
        user_id: str,
        tier: SubscriptionTier,
        billing_cycle: str = "monthly"
    ) -> Optional[Dict[str, Any]]:
        """
        Create a Stripe subscription.

        Args:
            db: Database session
            user_id: User ID
            tier: Subscription tier
            billing_cycle: Billing cycle (monthly or yearly)

        Returns:
            Subscription data or None
        """
        if not self.stripe_enabled:
            logger.warning("Stripe is not enabled")
            return None

        subscription = await subscription_service.get_or_create_subscription(db, user_id)

        # Get or create Stripe customer
        if not subscription.stripe_customer_id:
            query = select(User).where(User.id == user_id)
            result = await db.execute(query)
            user = result.scalar_one_or_none()

            if not user:
                return None

            customer_id = await self.create_customer(db, user)

            if not customer_id:
                return None

            subscription.stripe_customer_id = customer_id
            await db.commit()

        # Create subscription
        try:
            # Get price ID based on tier and billing cycle
            price_id = self._get_price_id(tier, billing_cycle)

            stripe_subscription = self.stripe.Subscription.create(
                customer=subscription.stripe_customer_id,
                items=[{"price": price_id}],
                metadata={
                    "user_id": str(user_id),
                    "tier": tier.value,
                },
            )

            # Update subscription
            subscription.stripe_subscription_id = stripe_subscription.id
            subscription.stripe_price_id = price_id
            subscription.tier = tier
            subscription.status = SubscriptionStatus.ACTIVE
            subscription.current_period_start = datetime.fromtimestamp(
                stripe_subscription.current_period_start
            )
            subscription.current_period_end = datetime.fromtimestamp(
                stripe_subscription.current_period_end
            )

            await db.commit()

            logger.info(f"Created Stripe subscription {stripe_subscription.id} for user {user_id}")

            return {
                "subscription_id": stripe_subscription.id,
                "status": stripe_subscription.status,
                "current_period_end": subscription.current_period_end.isoformat(),
            }

        except Exception as e:
            logger.error(f"Failed to create Stripe subscription: {e}")
            return None

    def _get_price_id(self, tier: SubscriptionTier, billing_cycle: str) -> str:
        """
        Get Stripe price ID for tier and billing cycle.

        In production, these would be created in Stripe dashboard.
        """
        # Placeholder price IDs
        price_ids = {
            (SubscriptionTier.BASIC, "monthly"): "price_basic_monthly",
            (SubscriptionTier.BASIC, "yearly"): "price_basic_yearly",
            (SubscriptionTier.PREMIUM, "monthly"): "price_premium_monthly",
            (SubscriptionTier.PREMIUM, "yearly"): "price_premium_yearly",
            (SubscriptionTier.ENTERPRISE, "monthly"): "price_enterprise_monthly",
            (SubscriptionTier.ENTERPRISE, "yearly"): "price_enterprise_yearly",
        }

        return price_ids.get((tier, billing_cycle), "")

    async def handle_webhook(
        self,
        db: AsyncSession,
        event: Dict[str, Any]
    ):
        """
        Handle Stripe webhook events.

        Args:
            db: Database session
            event: Stripe event data
        """
        event_type = event.get("type")

        logger.info(f"Handling Stripe webhook event: {event_type}")

        if event_type == "customer.subscription.created":
            await self._handle_subscription_created(db, event)
        elif event_type == "customer.subscription.updated":
            await self._handle_subscription_updated(db, event)
        elif event_type == "customer.subscription.deleted":
            await self._handle_subscription_deleted(db, event)
        elif event_type == "invoice.payment_succeeded":
            await self._handle_payment_succeeded(db, event)
        elif event_type == "invoice.payment_failed":
            await self._handle_payment_failed(db, event)

    async def _handle_subscription_created(
        self,
        db: AsyncSession,
        event: Dict[str, Any]
    ):
        """Handle subscription created event."""
        subscription_data = event["data"]["object"]
        customer_id = subscription_data["customer"]

        # Find subscription by Stripe customer ID
        query = select(Subscription).where(
            Subscription.stripe_customer_id == customer_id
        )
        result = await db.execute(query)
        subscription = result.scalar_one_or_none()

        if subscription:
            subscription.status = SubscriptionStatus.ACTIVE
            await db.commit()

    async def _handle_subscription_updated(
        self,
        db: AsyncSession,
        event: Dict[str, Any]
    ):
        """Handle subscription updated event."""
        subscription_data = event["data"]["object"]
        subscription_id = subscription_data["id"]

        # Find subscription by Stripe subscription ID
        query = select(Subscription).where(
            Subscription.stripe_subscription_id == subscription_id
        )
        result = await db.execute(query)
        subscription = result.scalar_one_or_none()

        if subscription:
            # Update status
            status_map = {
                "active": SubscriptionStatus.ACTIVE,
                "canceled": SubscriptionStatus.CANCELLED,
                "past_due": SubscriptionStatus.PAST_DUE,
                "trialing": SubscriptionStatus.TRIALING,
            }

            subscription.status = status_map.get(
                subscription_data["status"],
                SubscriptionStatus.ACTIVE
            )

            subscription.current_period_start = datetime.fromtimestamp(
                subscription_data["current_period_start"]
            )
            subscription.current_period_end = datetime.fromtimestamp(
                subscription_data["current_period_end"]
            )

            await db.commit()

    async def _handle_subscription_deleted(
        self,
        db: AsyncSession,
        event: Dict[str, Any]
    ):
        """Handle subscription deleted event."""
        subscription_data = event["data"]["object"]
        subscription_id = subscription_data["id"]

        # Find subscription by Stripe subscription ID
        query = select(Subscription).where(
            Subscription.stripe_subscription_id == subscription_id
        )
        result = await db.execute(query)
        subscription = result.scalar_one_or_none()

        if subscription:
            subscription.status = SubscriptionStatus.CANCELLED
            subscription.cancelled_at = datetime.utcnow()
            await db.commit()

    async def _handle_payment_succeeded(
        self,
        db: AsyncSession,
        event: Dict[str, Any]
    ):
        """Handle payment succeeded event."""
        invoice = event["data"]["object"]
        subscription_id = invoice.get("subscription")

        if subscription_id:
            query = select(Subscription).where(
                Subscription.stripe_subscription_id == subscription_id
            )
            result = await db.execute(query)
            subscription = result.scalar_one_or_none()

            if subscription:
                subscription.status = SubscriptionStatus.ACTIVE
                await db.commit()

    async def _handle_payment_failed(
        self,
        db: AsyncSession,
        event: Dict[str, Any]
    ):
        """Handle payment failed event."""
        invoice = event["data"]["object"]
        subscription_id = invoice.get("subscription")

        if subscription_id:
            query = select(Subscription).where(
                Subscription.stripe_subscription_id == subscription_id
            )
            result = await db.execute(query)
            subscription = result.scalar_one_or_none()

            if subscription:
                subscription.status = SubscriptionStatus.PAST_DUE
                await db.commit()


# Global service instances
subscription_service = SubscriptionService()
stripe_service = StripeService()
