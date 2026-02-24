"""
Mobile Device model for push notifications.
"""

import uuid
from datetime import datetime

from sqlalchemy import String, DateTime, ForeignKey, func, Index
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base
from app.models.common import UUID, JSONType


class MobileDevice(Base):
    """Mobile device registration for push notifications."""

    __tablename__ = "mobile_devices"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID,
        primary_key=True,
        default=uuid.uuid4,
    )

    # User reference (nullable for anonymous devices)
    user_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID,
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=True,
        index=True,
    )

    # Device token for push notifications
    device_token: Mapped[str] = mapped_column(
        String(500),
        unique=True,
        nullable=False,
        index=True,
    )

    # Device type: "ios" or "android"
    device_type: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
    )

    # App version
    app_version: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
    )

    # Device information
    device_model: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True,
    )

    os_version: Mapped[str | None] = mapped_column(
        String(50),
        nullable=True,
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

    last_active_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    # Additional metadata (renamed to avoid conflict with SQLAlchemy's reserved 'metadata')
    device_metadata: Mapped[dict | None] = mapped_column(
        JSONType,
        nullable=True,
    )

    # Indexes for efficient queries
    __table_args__ = (
        Index("idx_device_user_type", "user_id", "device_type"),
    )

    def __repr__(self) -> str:
        """String representation."""
        return f"<MobileDevice {self.device_type} - {self.device_model}>"
