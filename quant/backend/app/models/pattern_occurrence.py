"""Pattern occurrence model."""

import uuid
from datetime import date, datetime
from typing import TYPE_CHECKING

from sqlalchemy import (
    CheckConstraint,
    Date,
    DateTime,
    Float,
    ForeignKey,
    Index,
    String,
    Text,
    func,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base

if TYPE_CHECKING:
    from app.models.pattern import PatternModel


class PatternOccurrence(Base):
    """
    Historical occurrence of a pattern.

    Records each time a pattern has occurred in the past, with
    performance metrics for that specific occurrence.
    """

    __tablename__ = "pattern_occurrences"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )

    # Foreign key to pattern
    pattern_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("patterns.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    # Occurrence timing
    start_date: Mapped[date] = mapped_column(Date, nullable=False, index=True)
    end_date: Mapped[date] = mapped_column(Date, nullable=False, index=True)

    # Performance
    return_pct: Mapped[float] = mapped_column(
        Float,
        nullable=False,
    )  # Return percentage during this occurrence
    confidence: Mapped[float] = mapped_column(
        Float,
        nullable=False,
    )  # Confidence for this specific occurrence

    # Additional metrics
    volume_change: Mapped[float | None] = mapped_column(Float)
    notes: Mapped[str | None] = mapped_column(Text)

    # Metadata
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    # Relationships
    pattern: Mapped["PatternModel"] = relationship(
        "PatternModel",
        back_populates="occurrences",
    )

    # Database constraints
    __table_args__ = (
        CheckConstraint(
            "confidence >= 0 AND confidence <= 100",
            name="valid_occurrence_confidence",
        ),
        CheckConstraint(
            "end_date >= start_date",
            name="valid_date_range",
        ),
        # Prevent duplicate occurrences for same pattern
        Index(
            "idx_unique_occurrence",
            "pattern_id",
            "start_date",
            "end_date",
            unique=True,
        ),
        # Index for finding recent occurrences
        Index(
            "idx_recent_occurrences",
            "pattern_id",
            "end_date",
        ),
    )

    def __repr__(self) -> str:
        """String representation."""
        return f"<PatternOccurrence {self.start_date} to {self.end_date} (return: {self.return_pct:+.2%})>"

    def to_dict(self) -> dict:
        """Convert to dictionary."""
        return {
            "id": str(self.id),
            "pattern_id": str(self.pattern_id),
            "start_date": self.start_date.isoformat(),
            "end_date": self.end_date.isoformat(),
            "return_pct": self.return_pct,
            "confidence": self.confidence,
            "volume_change": self.volume_change,
            "notes": self.notes,
            "created_at": self.created_at.isoformat(),
        }
