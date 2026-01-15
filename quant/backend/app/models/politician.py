"""Politician model."""

import uuid
from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import String, DateTime, func, CheckConstraint, TypeDecorator, CHAR
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base
from app.core.config import settings

if TYPE_CHECKING:
    from app.models.trade import Trade


# Database-agnostic UUID type
class UUID(TypeDecorator):
    """Platform-independent UUID type. Uses PostgreSQL's UUID type or CHAR(36) for SQLite."""
    impl = CHAR
    cache_ok = True

    def load_dialect_impl(self, dialect):
        if dialect.name == 'postgresql':
            return dialect.type_descriptor(PG_UUID(as_uuid=True))
        else:
            return dialect.type_descriptor(CHAR(36))

    def process_bind_param(self, value, dialect):
        if value is None:
            return value
        elif dialect.name == 'postgresql':
            return value
        else:
            return str(value)

    def process_result_value(self, value, dialect):
        if value is None:
            return value
        if isinstance(value, uuid.UUID):
            return value
        return uuid.UUID(value)


class Politician(Base):
    """Politician model."""

    __tablename__ = "politicians"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(),
        primary_key=True,
        default=uuid.uuid4,
    )
    name: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    chamber: Mapped[str] = mapped_column(
        String(10),
        nullable=False,
        index=True,
    )  # 'senate' or 'house'
    party: Mapped[str | None] = mapped_column(String(20), index=True)
    state: Mapped[str | None] = mapped_column(String(2))
    bioguide_id: Mapped[str | None] = mapped_column(String(10), unique=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
    )

    # Relationships
    trades: Mapped[list["Trade"]] = relationship(
        "Trade",
        back_populates="politician",
        cascade="all, delete-orphan",
    )

    # Database constraints
    __table_args__ = (
        CheckConstraint(
            "chamber IN ('senate', 'house')",
            name="valid_chamber",
        ),
    )

    def __repr__(self) -> str:
        """String representation."""
        return f"<Politician {self.name} ({self.chamber})>"
