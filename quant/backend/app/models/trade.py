"""Trade model."""

import uuid
import json
from datetime import date, datetime
from decimal import Decimal
from typing import TYPE_CHECKING

from sqlalchemy import (
    String,
    Date,
    DateTime,
    Numeric,
    Text,
    ForeignKey,
    func,
    CheckConstraint,
    Index,
    TypeDecorator,
    CHAR,
)
from sqlalchemy.dialects.postgresql import UUID as PG_UUID, JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base

if TYPE_CHECKING:
    from app.models.politician import Politician


# Database-agnostic UUID type
class UUID(TypeDecorator):
    """Platform-independent UUID type."""
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


# Database-agnostic JSON type
class JSONType(TypeDecorator):
    """Platform-independent JSON type."""
    impl = Text
    cache_ok = True

    def load_dialect_impl(self, dialect):
        if dialect.name == 'postgresql':
            return dialect.type_descriptor(JSONB())
        else:
            return dialect.type_descriptor(Text())

    def process_bind_param(self, value, dialect):
        if value is None:
            return value
        if dialect.name == 'postgresql':
            return value
        return json.dumps(value)

    def process_result_value(self, value, dialect):
        if value is None:
            return value
        if isinstance(value, dict):
            return value
        return json.loads(value)


class Trade(Base):
    """Trade model."""

    __tablename__ = "trades"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(),
        primary_key=True,
        default=uuid.uuid4,
    )
    politician_id: Mapped[uuid.UUID] = mapped_column(
        UUID(),
        ForeignKey("politicians.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    ticker: Mapped[str] = mapped_column(String(10), nullable=False, index=True)
    transaction_type: Mapped[str] = mapped_column(
        String(10),
        nullable=False,
    )  # 'buy' or 'sell'
    amount_min: Mapped[Decimal | None] = mapped_column(Numeric(15, 2))
    amount_max: Mapped[Decimal | None] = mapped_column(Numeric(15, 2))
    transaction_date: Mapped[date] = mapped_column(Date, nullable=False, index=True)
    disclosure_date: Mapped[date] = mapped_column(Date, nullable=False)
    source_url: Mapped[str | None] = mapped_column(Text)
    raw_data: Mapped[dict | None] = mapped_column(JSONType())  # Store original scraped data
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
    )

    # Relationships
    politician: Mapped["Politician"] = relationship("Politician", back_populates="trades")

    # Database constraints
    __table_args__ = (
        CheckConstraint(
            "transaction_type IN ('buy', 'sell')",
            name="valid_transaction_type",
        ),
        CheckConstraint(
            "amount_min IS NULL OR amount_min >= 0",
            name="valid_amount_min",
        ),
        CheckConstraint(
            "amount_max IS NULL OR amount_max >= 0",
            name="valid_amount_max",
        ),
        CheckConstraint(
            "amount_min IS NULL OR amount_max IS NULL OR amount_min <= amount_max",
            name="valid_amount_range",
        ),
        CheckConstraint(
            "disclosure_date >= transaction_date",
            name="disclosure_after_transaction",
        ),
        # Unique constraint to prevent duplicate trades
        Index(
            "idx_unique_trade",
            "politician_id",
            "ticker",
            "transaction_date",
            "transaction_type",
            unique=True,
        ),
    )

    def __repr__(self) -> str:
        """String representation."""
        return f"<Trade {self.ticker} {self.transaction_type} on {self.transaction_date}>"
