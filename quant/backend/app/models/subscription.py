"""
Subscription model for premium tier management.
"""

import uuid
from datetime import datetime
from decimal import Decimal
import enum

from sqlalchemy import String, DateTime, Numeric, Text, ForeignKey, func, Enum as SQLEnum
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base
from app.models.common import UUID, JSONType


class SubscriptionTier(str, enum.Enum):
    """Subscription tiers - Hybrid Revenue Model."""
    FREE = "free"  # Unlimited backtests, ad-supported
    STARTER = "starter"  # $9.99/mo - Ad-free, faster results
    PROFESSIONAL = "professional"  # $29/mo - Advanced features + API
    ENTERPRISE = "enterprise"  # Custom pricing


class SubscriptionStatus(str, enum.Enum):
    """Subscription status."""
    ACTIVE = "active"
    CANCELLED = "cancelled"
    PAST_DUE = "past_due"
    TRIALING = "trialing"
    PAUSED = "paused"


class Subscription(Base):
    """Subscription model for user premium features."""

    __tablename__ = "subscriptions"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID,
        primary_key=True,
        default=uuid.uuid4,
    )

    # Reference to user
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID,
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
        unique=True,  # One subscription per user
    )

    # Subscription details
    tier: Mapped[SubscriptionTier] = mapped_column(
        SQLEnum(SubscriptionTier, name="subscription_tier_enum"),
        default=SubscriptionTier.FREE,
        nullable=False,
        index=True,
    )

    status: Mapped[SubscriptionStatus] = mapped_column(
        SQLEnum(SubscriptionStatus, name="subscription_status_enum"),
        default=SubscriptionStatus.ACTIVE,
        nullable=False,
        index=True,
    )

    # Stripe integration
    stripe_customer_id: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
        unique=True,
        index=True,
    )

    stripe_subscription_id: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
        unique=True,
        index=True,
    )

    stripe_price_id: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
    )

    # Billing
    billing_cycle: Mapped[str] = mapped_column(
        String(20),
        default="monthly",
        nullable=False,
    )  # monthly, yearly

    price_per_period: Mapped[Decimal | None] = mapped_column(
        Numeric(10, 2),
        nullable=True,
    )

    currency: Mapped[str] = mapped_column(
        String(3),
        default="USD",
        nullable=False,
    )

    # Timestamps
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )

    current_period_start: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    current_period_end: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    cancel_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    cancelled_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    trial_start: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    trial_end: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    # Usage limits (based on tier)
    api_rate_limit: Mapped[int] = mapped_column(
        String,
        default=100,
        nullable=False,
    )  # requests per day

    # Feature flags
    features: Mapped[dict] = mapped_column(
        JSONType,
        nullable=False,
        default=dict,
    )

    # Metadata (renamed to avoid conflict with SQLAlchemy's reserved 'metadata')
    subscription_metadata: Mapped[dict | None] = mapped_column(
        JSONType,
        nullable=True,
    )

    def __repr__(self) -> str:
        """String representation."""
        return f"<Subscription {self.tier} - {self.status}>"


class UsageRecord(Base):
    """Usage tracking for API rate limiting and billing."""

    __tablename__ = "usage_records"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID,
        primary_key=True,
        default=uuid.uuid4,
    )

    # Reference to user or API key
    user_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID,
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=True,
        index=True,
    )

    api_key_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID,
        ForeignKey("api_keys.id", ondelete="CASCADE"),
        nullable=True,
        index=True,
    )

    # Usage details
    resource_type: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        index=True,
    )  # api_call, export, alert, etc.

    endpoint: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
    )

    request_count: Mapped[int] = mapped_column(
        String,
        default=1,
        nullable=False,
    )

    # Timestamps (date-based for daily aggregation)
    usage_date: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        index=True,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    # Metadata (renamed to avoid conflict with SQLAlchemy's reserved 'metadata')
    usage_metadata: Mapped[dict | None] = mapped_column(
        JSONType,
        nullable=True,
    )

    def __repr__(self) -> str:
        """String representation."""
        return f"<UsageRecord {self.resource_type} - {self.usage_date}>"
