"""Politician schemas."""

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class PoliticianBase(BaseModel):
    """Base politician schema."""

    name: str = Field(..., min_length=1, max_length=255, description="Full name of the politician")
    chamber: str = Field(..., pattern="^(senate|house)$", description="Chamber: 'senate' or 'house'")
    party: str | None = Field(None, max_length=20, description="Political party")
    state: str | None = Field(None, pattern="^[A-Z]{2}$", description="Two-letter state code")
    bioguide_id: str | None = Field(None, max_length=10, description="Bioguide ID")


class PoliticianCreate(PoliticianBase):
    """Schema for creating a politician."""

    pass


class PoliticianUpdate(BaseModel):
    """Schema for updating a politician."""

    name: str | None = Field(None, min_length=1, max_length=255)
    chamber: str | None = Field(None, pattern="^(senate|house)$")
    party: str | None = Field(None, max_length=20)
    state: str | None = Field(None, pattern="^[A-Z]{2}$")
    bioguide_id: str | None = Field(None, max_length=10)


class PoliticianResponse(PoliticianBase):
    """Schema for politician response."""

    id: UUID
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class PoliticianWithTrades(PoliticianResponse):
    """Schema for politician with trade count."""

    trade_count: int = Field(0, description="Number of trades")
    recent_trade_date: datetime | None = Field(None, description="Most recent trade date")

    model_config = ConfigDict(from_attributes=True)
