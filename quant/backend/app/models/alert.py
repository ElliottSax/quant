"""
Alert model for real-time trade alerts.
"""

import uuid
from datetime import datetime
from typing import List

from sqlalchemy import String, DateTime, Boolean, Text, ForeignKey, func, Enum as SQLEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base
from app.models.common import UUID, JSONType
import enum


class AlertType(str, enum.Enum):
    """Alert types."""
    TRADE = "trade"
    PRICE = "price"
    POLITICIAN_ACTIVITY = "politician_activity"
    PATTERN = "pattern"


class NotificationChannel(str, enum.Enum):
    """Notification channels."""
    EMAIL = "email"
    WEBHOOK = "webhook"
    PUSH = "push"
    SMS = "sms"


class AlertStatus(str, enum.Enum):
    """Alert status."""
    ACTIVE = "active"
    PAUSED = "paused"
    TRIGGERED = "triggered"
    EXPIRED = "expired"


class Alert(Base):
    """Alert model for monitoring trades and market conditions."""

    __tablename__ = "alerts"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID,
        primary_key=True,
        default=uuid.uuid4,
    )

    # Reference to user who owns this alert
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID,
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    # Alert configuration
    name: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )

    alert_type: Mapped[AlertType] = mapped_column(
        SQLEnum(AlertType, name="alert_type_enum"),
        nullable=False,
        index=True,
    )

    # Alert conditions (stored as JSON)
    # For trade alerts: {"politician_id": "uuid", "ticker": "AAPL", "min_amount": 100000}
    # For price alerts: {"ticker": "AAPL", "target_price": 150.00, "condition": "above"}
    conditions: Mapped[dict] = mapped_column(
        JSONType,
        nullable=False,
    )

    # Notification channels (email, webhook, push)
    notification_channels: Mapped[dict] = mapped_column(
        JSONType,
        nullable=False,
        default=list,
    )

    # Webhook URL for webhook notifications
    webhook_url: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    # Email override (if different from user's email)
    notification_email: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
    )

    # Status
    status: Mapped[AlertStatus] = mapped_column(
        SQLEnum(AlertStatus, name="alert_status_enum"),
        default=AlertStatus.ACTIVE,
        nullable=False,
        index=True,
    )

    is_active: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
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

    last_triggered_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    expires_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    # Statistics
    trigger_count: Mapped[int] = mapped_column(
        String,
        default=0,
        nullable=False,
    )

    # Metadata (renamed to avoid conflict with SQLAlchemy's reserved 'metadata')
    alert_metadata: Mapped[dict | None] = mapped_column(
        JSONType,
        nullable=True,
    )

    def __repr__(self) -> str:
        """String representation."""
        return f"<Alert {self.name} ({self.alert_type})>"
