"""
API Key model for programmatic access.
"""

import uuid
from datetime import datetime
from typing import List

from sqlalchemy import String, DateTime, Boolean, Text, ForeignKey, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base
from app.models.common import UUID, JSONType


class APIKey(Base):
    """API Key model for user authentication and authorization."""

    __tablename__ = "api_keys"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID,
        primary_key=True,
        default=uuid.uuid4,
    )

    # Reference to user who owns this key
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID,
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    # Key identifier (first part of hashed key, for display)
    key_id: Mapped[str] = mapped_column(
        String(16),
        unique=True,
        nullable=False,
        index=True,
    )

    # Hashed version of the full key
    key_hash: Mapped[str] = mapped_column(
        String(64),
        unique=True,
        nullable=False,
        index=True,
    )

    # Friendly name for the key
    name: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )

    # Permissions (stored as JSON array)
    permissions: Mapped[dict] = mapped_column(
        JSONType,
        nullable=False,
        default=list,
    )

    # Status
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

    expires_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    last_used_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    # Usage tracking
    total_requests: Mapped[int] = mapped_column(
        String,
        default=0,
        nullable=False,
    )

    # Metadata (renamed to avoid conflict with SQLAlchemy's reserved 'metadata')
    key_metadata: Mapped[dict | None] = mapped_column(
        JSONType,
        nullable=True,
    )

    def __repr__(self) -> str:
        """String representation."""
        return f"<APIKey {self.key_id} - {self.name}>"
