"""Pydantic schemas."""

from app.schemas.politician import (
    PoliticianBase,
    PoliticianCreate,
    PoliticianResponse,
    PoliticianUpdate,
    PoliticianWithTrades,
)
from app.schemas.stats import (
    LeaderboardResponse,
    PoliticianLeaderboard,
    SectorStats,
    SectorStatsResponse,
)
from app.schemas.ticker import TickerBase, TickerCreate, TickerResponse, TickerUpdate
from app.schemas.trade import (
    TradeBase,
    TradeCreate,
    TradeListResponse,
    TradeResponse,
    TradeUpdate,
    TradeWithPolitician,
)

__all__ = [
    # Politician schemas
    "PoliticianBase",
    "PoliticianCreate",
    "PoliticianUpdate",
    "PoliticianResponse",
    "PoliticianWithTrades",
    # Trade schemas
    "TradeBase",
    "TradeCreate",
    "TradeUpdate",
    "TradeResponse",
    "TradeWithPolitician",
    "TradeListResponse",
    # Ticker schemas
    "TickerBase",
    "TickerCreate",
    "TickerUpdate",
    "TickerResponse",
    # Stats schemas
    "PoliticianLeaderboard",
    "LeaderboardResponse",
    "SectorStats",
    "SectorStatsResponse",
]
