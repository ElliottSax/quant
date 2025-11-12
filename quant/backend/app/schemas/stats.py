"""Statistics schemas."""

from datetime import date
from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel, Field


class PoliticianLeaderboard(BaseModel):
    """Schema for politician leaderboard entry."""

    politician_id: UUID
    politician_name: str
    chamber: str
    party: str | None
    state: str | None
    trade_count: int = Field(..., description="Number of trades in period")
    total_volume_min: Decimal = Field(..., description="Minimum total trading volume")
    total_volume_max: Decimal = Field(..., description="Maximum total trading volume")
    buy_count: int = Field(..., description="Number of buy transactions")
    sell_count: int = Field(..., description="Number of sell transactions")
    most_recent_trade: date | None = Field(None, description="Date of most recent trade")


class LeaderboardResponse(BaseModel):
    """Schema for leaderboard response."""

    leaderboard: list[PoliticianLeaderboard]
    period: str
    limit: int


class SectorStats(BaseModel):
    """Schema for sector statistics."""

    sector: str
    trade_count: int = Field(..., description="Number of trades in sector")
    total_volume_min: Decimal = Field(..., description="Minimum total trading volume")
    total_volume_max: Decimal = Field(..., description="Maximum total trading volume")
    unique_politicians: int = Field(..., description="Number of unique politicians trading in sector")
    buy_count: int = Field(..., description="Number of buy transactions")
    sell_count: int = Field(..., description="Number of sell transactions")


class SectorStatsResponse(BaseModel):
    """Schema for sector statistics response."""

    sectors: list[SectorStats]
    period: str
