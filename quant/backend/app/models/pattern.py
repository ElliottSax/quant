"""Pattern detection models."""

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
    Integer,
    String,
    Text,
    func,
)
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base

if TYPE_CHECKING:
    from app.models.pattern_occurrence import PatternOccurrence


class PatternModel(Base):
    """
    Detected cyclical pattern in stock market.

    Stores validated patterns identified by pattern detection algorithms
    (SARIMA, Calendar Effects, etc.) with full statistical validation metrics.
    """

    __tablename__ = "patterns"

    # Identity
    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )
    pattern_id: Mapped[str] = mapped_column(
        String(100),
        unique=True,
        nullable=False,
        index=True,
    )

    # Type and classification
    pattern_type: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        index=True,
    )  # seasonal, calendar, cycle, regime, etc.
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)

    # Target
    ticker: Mapped[str | None] = mapped_column(
        String(10),
        nullable=True,
        index=True,
    )
    sector: Mapped[str | None] = mapped_column(String(100))
    market_cap: Mapped[str | None] = mapped_column(
        String(20)
    )  # small, mid, large

    # Timing
    cycle_length_days: Mapped[int] = mapped_column(Integer, nullable=False)
    frequency: Mapped[str | None] = mapped_column(
        String(20)
    )  # daily, weekly, monthly, quarterly, annual
    next_occurrence: Mapped[date | None] = mapped_column(Date, index=True)
    window_start_day: Mapped[int | None] = mapped_column(Integer)
    window_end_day: Mapped[int | None] = mapped_column(Integer)

    # Validation metrics (stored as JSONB)
    validation_metrics: Mapped[dict] = mapped_column(JSONB, nullable=False)

    # Scores
    reliability_score: Mapped[float] = mapped_column(
        Float,
        nullable=False,
        index=True,
    )
    confidence: Mapped[float] = mapped_column(Float, nullable=False)

    # Dates
    first_detected: Mapped[date | None] = mapped_column(Date)
    last_validated: Mapped[date] = mapped_column(Date, nullable=False)

    # Explanation
    economic_rationale: Mapped[str | None] = mapped_column(Text)
    risk_factors: Mapped[list | None] = mapped_column(
        JSONB
    )  # List of risk factor strings

    # Politician correlation
    politician_correlation: Mapped[float | None] = mapped_column(Float)
    recent_politician_activity: Mapped[dict | None] = mapped_column(JSONB)

    # Metadata
    detected_at: Mapped[datetime] = mapped_column(
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
    detector_version: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        default="1.0.0",
    )
    parameters: Mapped[dict] = mapped_column(JSONB, nullable=False)

    # Status
    is_active: Mapped[bool] = mapped_column(
        default=True,
        nullable=False,
        index=True,
    )  # Can be deactivated if pattern breaks

    # Relationships
    occurrences: Mapped[list["PatternOccurrence"]] = relationship(
        "PatternOccurrence",
        back_populates="pattern",
        cascade="all, delete-orphan",
    )

    # Database constraints
    __table_args__ = (
        CheckConstraint(
            "pattern_type IN ('seasonal', 'calendar', 'cycle', 'regime', 'behavioral', 'politician', 'earnings', 'economic')",
            name="valid_pattern_type",
        ),
        CheckConstraint(
            "frequency IS NULL OR frequency IN ('daily', 'weekly', 'monthly', 'quarterly', 'annual')",
            name="valid_frequency",
        ),
        CheckConstraint(
            "reliability_score >= 0 AND reliability_score <= 100",
            name="valid_reliability_score",
        ),
        CheckConstraint(
            "confidence >= 0 AND confidence <= 100",
            name="valid_confidence",
        ),
        CheckConstraint(
            "cycle_length_days > 0",
            name="valid_cycle_length",
        ),
        CheckConstraint(
            "politician_correlation IS NULL OR (politician_correlation >= -1 AND politician_correlation <= 1)",
            name="valid_correlation",
        ),
        # Index for finding active patterns
        Index("idx_active_patterns", "is_active", "pattern_type", "ticker"),
        # Index for finding patterns by next occurrence
        Index(
            "idx_upcoming_patterns",
            "next_occurrence",
            "is_active",
            postgresql_where="is_active = true",
        ),
        # Index for finding high-reliability patterns
        Index(
            "idx_reliable_patterns",
            "reliability_score",
            "is_active",
            postgresql_where="reliability_score >= 70",
        ),
    )

    def __repr__(self) -> str:
        """String representation."""
        return f"<Pattern {self.name} (reliability: {self.reliability_score:.1f})>"

    def to_dict(self) -> dict:
        """Convert to dictionary."""
        return {
            "id": str(self.id),
            "pattern_id": self.pattern_id,
            "pattern_type": self.pattern_type,
            "name": self.name,
            "description": self.description,
            "ticker": self.ticker,
            "sector": self.sector,
            "market_cap": self.market_cap,
            "cycle_length_days": self.cycle_length_days,
            "frequency": self.frequency,
            "next_occurrence": self.next_occurrence.isoformat()
            if self.next_occurrence
            else None,
            "window_start_day": self.window_start_day,
            "window_end_day": self.window_end_day,
            "validation_metrics": self.validation_metrics,
            "reliability_score": self.reliability_score,
            "confidence": self.confidence,
            "first_detected": self.first_detected.isoformat()
            if self.first_detected
            else None,
            "last_validated": self.last_validated.isoformat(),
            "economic_rationale": self.economic_rationale,
            "risk_factors": self.risk_factors,
            "politician_correlation": self.politician_correlation,
            "recent_politician_activity": self.recent_politician_activity,
            "detected_at": self.detected_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
            "detector_version": self.detector_version,
            "parameters": self.parameters,
            "is_active": self.is_active,
        }
