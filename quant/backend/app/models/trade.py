"""Trade model."""

import uuid
from datetime import date, datetime
from decimal import Decimal
from typing import TYPE_CHECKING

from sqlalchemy import String, Date, DateTime, Numeric, Text, ForeignKey, func
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base

if TYPE_CHECKING:
    from app.models.politician import Politician


class Trade(Base):
    """Trade model."""

    __tablename__ = "trades"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )
    politician_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
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
    raw_data: Mapped[dict | None] = mapped_column(JSONB)  # Store original scraped data
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
    )

    # Relationships
    politician: Mapped["Politician"] = relationship("Politician", back_populates="trades")

    def __repr__(self) -> str:
        """String representation."""
        return f"<Trade {self.ticker} {self.transaction_type} on {self.transaction_date}>"
