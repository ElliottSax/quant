"""Data Source model for tracking scraping runs."""

import uuid
from datetime import datetime
from typing import Optional

from sqlalchemy import (
    String,
    DateTime,
    Integer,
    Text,
    Boolean,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base
from app.models.common import UUID, JSONType


class DataSource(Base):
    """Model to track data scraping runs."""

    __tablename__ = "data_sources"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(),
        primary_key=True,
        default=uuid.uuid4,
    )
    source_type: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        index=True,
    )  # 'senate' or 'house'
    run_date: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        index=True,
        server_default=func.now(),
    )
    status: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        index=True,
    )  # 'running', 'completed', 'failed'
    records_found: Mapped[int] = mapped_column(Integer, default=0)
    records_imported: Mapped[int] = mapped_column(Integer, default=0)
    records_skipped: Mapped[int] = mapped_column(Integer, default=0)
    records_invalid: Mapped[int] = mapped_column(Integer, default=0)
    error_message: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    source_metadata: Mapped[Optional[dict]] = mapped_column(JSONType(), nullable=True)
    started_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
    )
    completed_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    def __repr__(self) -> str:
        """String representation."""
        return f"<DataSource {self.source_type} on {self.run_date} - {self.status}>"

    def mark_completed(self, records_imported: int, records_skipped: int, records_invalid: int):
        """Mark the run as completed."""
        self.status = "completed"
        self.records_imported = records_imported
        self.records_skipped = records_skipped
        self.records_invalid = records_invalid
        self.completed_at = datetime.utcnow()

    def mark_failed(self, error_message: str):
        """Mark the run as failed."""
        self.status = "failed"
        self.error_message = error_message
        self.completed_at = datetime.utcnow()
