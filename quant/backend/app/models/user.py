"""User model for authentication."""

import uuid
from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import String, DateTime, Boolean, Integer, Float, func, CheckConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class User(Base):
    """User model for authentication and authorization."""

    __tablename__ = "users"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )
    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False, index=True)
    username: Mapped[str] = mapped_column(String(50), unique=True, nullable=False, index=True)
    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    is_superuser: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
    )
    last_login: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    # Security: Refresh token rotation
    refresh_token_version: Mapped[int] = mapped_column(
        Integer,
        default=0,
        nullable=False,
        server_default="0",
    )

    # Security: Account lockout
    failed_login_attempts: Mapped[int] = mapped_column(
        Integer,
        default=0,
        nullable=False,
        server_default="0",
    )
    locked_until: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    # Email verification
    email_verified: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False,
        server_default="false",
    )
    email_verification_token: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
    )
    email_verification_sent_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    # Two-Factor Authentication
    totp_enabled: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False,
        server_default="false",
    )
    totp_secret: Mapped[str | None] = mapped_column(
        String(64),
        nullable=True,
    )
    totp_backup_codes: Mapped[str | None] = mapped_column(
        String,  # Stored as JSON string
        nullable=True,
    )

    # Subscription Management (Hybrid Model)
    subscription_tier: Mapped[str] = mapped_column(
        String(20),
        default="free",
        nullable=False,
        server_default="free",
        index=True,
    )  # 'free', 'starter' ($9.99), 'professional' ($29), 'enterprise'

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
    subscription_status: Mapped[str | None] = mapped_column(
        String(50),
        nullable=True,
    )  # 'active', 'canceled', 'past_due'
    subscription_period_end: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    # Ad-free flag (for starter/professional tiers)
    ad_free: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False,
        server_default="false",
    )

    # Free trial tracking (for $9.99 and $29 tiers)
    trial_started_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )
    trial_ends_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )
    trial_used: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False,
        server_default="false",
    )

    # Referral tracking (users can earn $10 credit per referred friend)
    referral_code: Mapped[str | None] = mapped_column(
        String(50),
        nullable=True,
        unique=True,
        index=True,
    )
    referral_credit_balance: Mapped[float] = mapped_column(
        Float,
        default=0.0,
        nullable=False,
        server_default="0.0",
    )
    referred_by_user_id: Mapped[str | None] = mapped_column(
        String(36),
        nullable=True,
        index=True,
    )

    # Usage tracking (informational, not enforced for free tier)
    backtests_this_month: Mapped[int] = mapped_column(
        Integer,
        default=0,
        nullable=False,
        server_default="0",
    )
    last_backtest_reset: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    # Database constraints
    # Note: Using length() for SQLite compatibility (PostgreSQL also supports it)
    __table_args__ = (
        CheckConstraint(
            "length(email) >= 3",
            name="valid_email_length",
        ),
        CheckConstraint(
            "length(username) >= 3",
            name="valid_username_length",
        ),
        CheckConstraint(
            "subscription_tier IN ('free', 'starter', 'professional', 'enterprise')",
            name="valid_subscription_tier",
        ),
    )

    def __repr__(self) -> str:
        """String representation."""
        return f"<User {self.username} ({self.email}) - {self.subscription_tier}>"

    def is_paid(self) -> bool:
        """Check if user has paid tier (starter, professional, or enterprise)."""
        return self.subscription_tier in ('starter', 'professional', 'enterprise')

    def is_professional(self) -> bool:
        """Check if user has professional or higher tier."""
        return self.subscription_tier in ('professional', 'enterprise')

    def is_enterprise(self) -> bool:
        """Check if user has enterprise tier."""
        return self.subscription_tier == 'enterprise'

    def should_show_ads(self) -> bool:
        """Check if user should see ads (free tier or trial expired)."""
        if self.ad_free:
            return False
        # If trial expired and not paid, show ads
        if self.trial_ends_at and datetime.utcnow() > self.trial_ends_at:
            if not self.is_paid():
                return True
        return self.subscription_tier == 'free'

    def get_features(self) -> dict:
        """Get feature access based on tier."""
        features = {
            'free': {
                'unlimited_backtests': True,
                'basic_strategies': True,
                'export': False,
                'portfolio_tracking': False,
                'email_alerts': False,
                'api_access': False,
                'advanced_analytics': False,
            },
            'starter': {
                'unlimited_backtests': True,
                'basic_strategies': True,
                'export': True,
                'portfolio_tracking': False,
                'email_alerts': False,
                'api_access': False,
                'advanced_analytics': False,
            },
            'professional': {
                'unlimited_backtests': True,
                'basic_strategies': True,
                'export': True,
                'portfolio_tracking': True,
                'email_alerts': True,
                'api_access': True,
                'advanced_analytics': True,
            },
            'enterprise': {
                'unlimited_backtests': True,
                'basic_strategies': True,
                'export': True,
                'portfolio_tracking': True,
                'email_alerts': True,
                'api_access': True,
                'advanced_analytics': True,
            },
        }
        return features.get(self.subscription_tier, features['free'])
