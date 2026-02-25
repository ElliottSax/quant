"""Ticker schemas."""

from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class TickerBase(BaseModel):
    """Base ticker schema."""

    symbol: str = Field(..., min_length=1, max_length=10, description="Stock ticker symbol")
    company_name: str | None = Field(None, max_length=255, description="Company name")
    sector: str | None = Field(None, max_length=100, description="Sector")
    industry: str | None = Field(None, max_length=100, description="Industry")


class TickerCreate(TickerBase):
    """Schema for creating a ticker."""

    pass


class TickerUpdate(BaseModel):
    """Schema for updating a ticker."""

    company_name: str | None = Field(None, max_length=255)
    sector: str | None = Field(None, max_length=100)
    industry: str | None = Field(None, max_length=100)


class TickerResponse(TickerBase):
    """Schema for ticker response."""

    last_updated: datetime

    model_config = ConfigDict(from_attributes=True)
