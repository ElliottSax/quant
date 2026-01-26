"""Trade schemas."""

from datetime import date, datetime
from decimal import Decimal
from typing import Set
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, field_validator


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


class TradeFieldSelection(BaseModel):
    """
    Schema for field selection in trade queries.

    Allows clients to request only specific fields to reduce payload size.
    Example: ?fields=id,ticker,transaction_type,transaction_date
    """

    fields: Set[str] = Field(
        default={
            "id",
            "ticker",
            "transaction_type",
            "transaction_date",
            "politician_name",
        },
        description="Fields to include in response",
    )

    # All allowed fields that can be requested
    ALLOWED_FIELDS: Set[str] = {
        "id",
        "ticker",
        "transaction_type",
        "transaction_date",
        "disclosure_date",
        "amount_min",
        "amount_max",
        "politician_id",
        "politician_name",
        "politician_chamber",
        "politician_party",
        "politician_state",
        "source_url",
        "created_at",
    }

    @field_validator("fields")
    @classmethod
    def validate_fields(cls, v: Set[str]) -> Set[str]:
        """
        Validate that requested fields are allowed.

        Args:
            v: Set of requested field names

        Returns:
            Validated set of field names

        Raises:
            ValueError: If any requested field is not allowed
        """
        invalid_fields = v - cls.ALLOWED_FIELDS
        if invalid_fields:
            raise ValueError(
                f"Invalid fields requested: {invalid_fields}. "
                f"Allowed fields: {cls.ALLOWED_FIELDS}"
            )
        return v


class TradeListResponse(BaseModel):
    """Schema for paginated trade list response."""

    trades: list[TradeWithPolitician] | list[dict]
    total: int
    skip: int
    limit: int
