"""
Portfolio model for tracking politician holdings and performance.
"""

import uuid
from datetime import datetime
from decimal import Decimal

from sqlalchemy import String, DateTime, Numeric, Text, ForeignKey, func, Index
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base
from app.models.common import UUID, JSONType


class Portfolio(Base):
    """Portfolio model for tracking politician holdings over time."""

    __tablename__ = "portfolios"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID,
        primary_key=True,
        default=uuid.uuid4,
    )

    # Reference to politician
    politician_id: Mapped[uuid.UUID] = mapped_column(
        UUID,
        ForeignKey("politicians.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    # Snapshot date
    snapshot_date: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        index=True,
    )

    # Holdings (stored as JSON array)
    # [{"ticker": "AAPL", "shares": 100, "value": 15000, "cost_basis": 14000}]
    holdings: Mapped[dict] = mapped_column(
        JSONType,
        nullable=False,
        default=list,
    )

    # Portfolio metrics
    total_value: Mapped[Decimal] = mapped_column(
        Numeric(15, 2),
        nullable=False,
        default=0,
    )

    total_cost_basis: Mapped[Decimal | None] = mapped_column(
        Numeric(15, 2),
        nullable=True,
    )

    unrealized_gain_loss: Mapped[Decimal | None] = mapped_column(
        Numeric(15, 2),
        nullable=True,
    )

    # Performance metrics
    return_pct: Mapped[Decimal | None] = mapped_column(
        Numeric(10, 4),
        nullable=True,
    )

    # Sector allocation (stored as JSON)
    # {"Technology": 45.5, "Healthcare": 30.2, "Finance": 24.3}
    sector_allocation: Mapped[dict | None] = mapped_column(
        JSONType,
        nullable=True,
    )

    # Risk metrics
    concentration_score: Mapped[Decimal | None] = mapped_column(
        Numeric(5, 2),
        nullable=True,
    )

    diversification_score: Mapped[Decimal | None] = mapped_column(
        Numeric(5, 2),
        nullable=True,
    )

    # Timestamps
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    # Metadata (renamed to avoid conflict with SQLAlchemy's reserved 'metadata')
    portfolio_metadata: Mapped[dict | None] = mapped_column(
        JSONType,
        nullable=True,
    )

    # Unique constraint: one portfolio snapshot per politician per date
    __table_args__ = (
        Index(
            "idx_unique_portfolio_snapshot",
            "politician_id",
            "snapshot_date",
            unique=True,
        ),
    )

    def __repr__(self) -> str:
        """String representation."""
        return f"<Portfolio {self.politician_id} on {self.snapshot_date}>"


class Watchlist(Base):
    """Watchlist model for custom politician tracking lists."""

    __tablename__ = "watchlists"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID,
        primary_key=True,
        default=uuid.uuid4,
    )

    # Reference to user who owns this watchlist
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID,
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    # Watchlist details
    name: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )

    description: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    # Politicians in this watchlist (stored as JSON array of UUIDs)
    politician_ids: Mapped[dict] = mapped_column(
        JSONType,
        nullable=False,
        default=list,
    )

    # Display preferences
    is_public: Mapped[bool] = mapped_column(
        String,
        default=False,
        nullable=False,
    )

    sort_order: Mapped[int] = mapped_column(
        String,
        default=0,
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

    # Metadata (renamed to avoid conflict with SQLAlchemy's reserved 'metadata')
    watchlist_metadata: Mapped[dict | None] = mapped_column(
        JSONType,
        nullable=True,
    )

    def __repr__(self) -> str:
        """String representation."""
        return f"<Watchlist {self.name}>"
