"""Trade schemas."""

from datetime import date, datetime
from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class TradeBase(BaseModel):
    """Base trade schema."""

    politician_id: UUID = Field(..., description="Politician ID")
    ticker: str = Field(..., min_length=1, max_length=10, description="Stock ticker symbol")
    transaction_type: str = Field(..., pattern="^(buy|sell)$", description="Transaction type: 'buy' or 'sell'")
    amount_min: Decimal | None = Field(None, ge=0, description="Minimum transaction amount")
    amount_max: Decimal | None = Field(None, ge=0, description="Maximum transaction amount")
    transaction_date: date = Field(..., description="Date of the transaction")
    disclosure_date: date = Field(..., description="Date of disclosure")
    source_url: str | None = Field(None, description="Source URL of the disclosure")


class TradeCreate(TradeBase):
    """Schema for creating a trade."""

    raw_data: dict | None = Field(None, description="Raw scraped data in JSON format")


class TradeUpdate(BaseModel):
    """Schema for updating a trade."""

    ticker: str | None = Field(None, min_length=1, max_length=10)
    transaction_type: str | None = Field(None, pattern="^(buy|sell)$")
    amount_min: Decimal | None = Field(None, ge=0)
    amount_max: Decimal | None = Field(None, ge=0)
    transaction_date: date | None = None
    disclosure_date: date | None = None
    source_url: str | None = None


class TradeResponse(TradeBase):
    """Schema for trade response."""

    id: UUID
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class TradeWithPolitician(TradeResponse):
    """Schema for trade with politician information."""

    politician_name: str = Field(..., description="Name of the politician")
    politician_chamber: str = Field(..., description="Chamber: senate or house")
    politician_party: str | None = Field(None, description="Political party")
    politician_state: str | None = Field(None, description="State")

    model_config = ConfigDict(from_attributes=True)


class TradeListResponse(BaseModel):
    """Schema for paginated trade list response."""

    trades: list[TradeWithPolitician]
    total: int
    skip: int
    limit: int
