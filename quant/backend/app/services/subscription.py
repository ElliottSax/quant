"""
Subscription and billing service
Manages Stripe integration, subscription tiers, and usage tracking
"""

import stripe
from typing import Optional, Dict, Any
from datetime import datetime, timedelta
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update
from app.models.user import User
import os
import logging

logger = logging.getLogger(__name__)

# Initialize Stripe
stripe.api_key = os.getenv("STRIPE_SECRET_KEY", "sk_test_placeholder")


class SubscriptionService:
    """Service for managing user subscriptions and Stripe integration (Hybrid Model)."""

    TIER_PRICES = {
        "free": None,  # Free tier (unlimited backtests, ad-supported)
        "starter": os.getenv("STRIPE_STARTER_PRICE_ID", "price_starter_monthly"),  # $9.99/mo
        "professional": os.getenv("STRIPE_PROFESSIONAL_PRICE_ID", "price_professional_monthly"),  # $29/mo
        "enterprise": os.getenv("STRIPE_ENTERPRISE_PRICE_ID", "price_enterprise_monthly"),
    }

    TIER_DESCRIPTIONS = {
        "free": "Free - Ad-supported, unlimited backtests",
        "starter": "Starter - $9.99/mo, ad-free experience",
        "professional": "Professional - $29/mo, advanced features + API",
        "enterprise": "Enterprise - Custom pricing",
    }

    # No limits anymore - all tiers get unlimited backtests
    # Monetization through ads (free), subscriptions, and affiliate

    TRIAL_DAYS = 7

    @staticmethod
    async def create_customer(
        session: AsyncSession, user_id: str, email: str, name: str
    ) -> Optional[str]:
        """Create a Stripe customer for a user."""
        try:
            customer = stripe.Customer.create(
                email=email,
                name=name,
                metadata={"user_id": str(user_id)},
            )
            logger.info(f"Created Stripe customer {customer.id} for user {user_id}")
            return customer.id
        except stripe.error.StripeError as e:
            logger.error(f"Failed to create Stripe customer: {e}")
            return None

    @staticmethod
    async def create_subscription(
        session: AsyncSession,
        user_id: str,
        stripe_customer_id: str,
        tier: str,
        trial_days: int = TRIAL_DAYS,
    ) -> Optional[Dict[str, Any]]:
        """Create a Stripe subscription for a user."""
        if tier == "free":
            return {"status": "active", "tier": "free"}

        price_id = SubscriptionService.TIER_PRICES.get(tier)
        if not price_id:
            logger.error(f"Invalid tier: {tier}")
            return None

        try:
            subscription = stripe.Subscription.create(
                customer=stripe_customer_id,
                items=[{"price": price_id}],
                trial_period_days=trial_days,
                payment_behavior="default_incomplete",
            )

            logger.info(
                f"Created Stripe subscription {subscription.id} for user {user_id}"
            )

            # Update user in database
            stmt = (
                update(User)
                .where(User.id == user_id)
                .values(
                    stripe_subscription_id=subscription.id,
                    subscription_status=subscription.status,
                    subscription_tier=tier,
                    trial_started_at=datetime.utcnow(),
                    trial_ends_at=datetime.utcnow() + timedelta(days=trial_days),
                )
            )
            await session.execute(stmt)
            await session.commit()

            return {
                "subscription_id": subscription.id,
                "status": subscription.status,
                "tier": tier,
                "period_end": subscription.current_period_end,
            }
        except stripe.error.StripeError as e:
            logger.error(f"Failed to create subscription: {e}")
            return None

    @staticmethod
    async def upgrade_subscription(
        session: AsyncSession, user_id: str, new_tier: str
    ) -> bool:
        """Upgrade or downgrade a user's subscription."""
        stmt = select(User).where(User.id == user_id)
        result = await session.execute(stmt)
        user = result.scalar_one_or_none()

        if not user or not user.stripe_subscription_id:
            logger.error(f"User {user_id} has no active subscription")
            return False

        try:
            new_price_id = SubscriptionService.TIER_PRICES.get(new_tier)
            if not new_price_id:
                return False

            # Get current subscription
            subscription = stripe.Subscription.retrieve(user.stripe_subscription_id)

            # Update subscription with new price
            stripe.Subscription.modify(
                user.stripe_subscription_id,
                items=[{"id": subscription.items.data[0].id, "price": new_price_id}],
            )

            # Update database
            stmt = (
                update(User)
                .where(User.id == user_id)
                .values(subscription_tier=new_tier)
            )
            await session.execute(stmt)
            await session.commit()

            logger.info(f"Upgraded user {user_id} to tier {new_tier}")
            return True
        except stripe.error.StripeError as e:
            logger.error(f"Failed to upgrade subscription: {e}")
            return False

    @staticmethod
    async def cancel_subscription(
        session: AsyncSession, user_id: str
    ) -> bool:
        """Cancel a user's subscription."""
        stmt = select(User).where(User.id == user_id)
        result = await session.execute(stmt)
        user = result.scalar_one_or_none()

        if not user or not user.stripe_subscription_id:
            return False

        try:
            stripe.Subscription.delete(user.stripe_subscription_id)

            # Update database
            stmt = (
                update(User)
                .where(User.id == user_id)
                .values(
                    subscription_tier="free",
                    stripe_subscription_id=None,
                    subscription_status="canceled",
                )
            )
            await session.execute(stmt)
            await session.commit()

            logger.info(f"Canceled subscription for user {user_id}")
            return True
        except stripe.error.StripeError as e:
            logger.error(f"Failed to cancel subscription: {e}")
            return False

    @staticmethod
    async def track_backtest(session: AsyncSession, user_id: str) -> bool:
        """Track backtest for analytics (no quota enforcement in hybrid model)."""
        try:
            stmt = select(User).where(User.id == user_id)
            result = await session.execute(stmt)
            user = result.scalar_one_or_none()

            if not user:
                return False

            # Initialize last_backtest_reset if needed
            if user.last_backtest_reset is None:
                user.last_backtest_reset = datetime.utcnow()

            # Increment counter (for analytics, not enforcement)
            stmt = (
                update(User)
                .where(User.id == user_id)
                .values(backtests_this_month=User.backtests_this_month + 1)
            )
            await session.execute(stmt)
            await session.commit()
            return True
        except Exception as e:
            logger.error(f"Failed to track backtest: {e}")
            return False

    @staticmethod
    async def process_referral(session: AsyncSession, referrer_id: str, new_user_id: str) -> bool:
        """Process referral and add $10 credit to referrer."""
        try:
            stmt = select(User).where(User.id == referrer_id)
            result = await session.execute(stmt)
            referrer = result.scalar_one_or_none()

            if not referrer:
                return False

            # Add $10 credit (can be used for $9.99 tier or future upgrades)
            stmt = (
                update(User)
                .where(User.id == referrer_id)
                .values(referral_credit_balance=User.referral_credit_balance + 10.0)
            )
            await session.execute(stmt)

            # Mark new user as referred
            stmt = (
                update(User)
                .where(User.id == new_user_id)
                .values(referred_by_user_id=referrer_id)
            )
            await session.execute(stmt)
            await session.commit()

            logger.info(f"Processed referral: {referrer_id} → {new_user_id} (+$10)")
            return True
        except Exception as e:
            logger.error(f"Failed to process referral: {e}")
            return False

    @staticmethod
    def generate_referral_code(user_id: str) -> str:
        """Generate a unique referral code for user."""
        import random
        import string
        code = ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))
        return f"{code}_{user_id[:8]}"

    @staticmethod
    async def start_free_trial(session: AsyncSession, user_id: str) -> bool:
        """Start a free trial for a user (upgrade to premium)."""
        try:
            stmt = select(User).where(User.id == user_id)
            result = await session.execute(stmt)
            user = result.scalar_one_or_none()

            if not user or user.trial_used:
                return False

            trial_end = datetime.utcnow() + timedelta(days=SubscriptionService.TRIAL_DAYS)

            stmt = (
                update(User)
                .where(User.id == user_id)
                .values(
                    subscription_tier="premium",
                    trial_started_at=datetime.utcnow(),
                    trial_ends_at=trial_end,
                )
            )
            await session.execute(stmt)
            await session.commit()

            logger.info(f"Started free trial for user {user_id}")
            return True
        except Exception as e:
            logger.error(f"Failed to start free trial: {e}")
            return False

    @staticmethod
    async def check_trial_expired(session: AsyncSession, user_id: str) -> bool:
        """Check if user's trial has expired."""
        stmt = select(User).where(User.id == user_id)
        result = await session.execute(stmt)
        user = result.scalar_one_or_none()

        if not user or not user.trial_ends_at:
            return False

        if datetime.utcnow() > user.trial_ends_at and user.subscription_tier != "premium":
            # Trial expired, downgrade to free
            stmt = (
                update(User)
                .where(User.id == user_id)
                .values(subscription_tier="free", trial_used=True)
            )
            await session.execute(stmt)
            await session.commit()
            return True

        return False
