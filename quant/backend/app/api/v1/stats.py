"""Statistics API endpoints."""

from typing import Literal

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.services.statistics_service import StatisticsService

router = APIRouter()


@router.get("/leaderboard")
async def get_leaderboard(
    period: Literal["7d", "30d", "90d", "1y", "all"] = Query(
        default="30d",
        description="Time period for leaderboard calculation",
    ),
    limit: int = Query(
        default=50,
        ge=1,
        le=100,
        description="Maximum number of politicians to return",
    ),
    chamber: Literal["senate", "house"] | None = Query(
        default=None,
        description="Filter by chamber",
    ),
    party: str | None = Query(
        default=None,
        description="Filter by party (e.g., Democrat, Republican)",
    ),
    db: AsyncSession = Depends(get_db),
) -> dict:
    """
    Get politician trading leaderboard.

    Returns politicians ranked by number of trades in the specified period,
    with additional statistics like buy/sell counts and average trade size.

    Args:
        period: Time period (7d, 30d, 90d, 1y, all)
        limit: Maximum number of records to return (1-100)
        chamber: Optional filter by chamber (senate/house)
        party: Optional filter by party
        db: Database session

    Returns:
        Leaderboard data with politician statistics
    """
    stats_service = StatisticsService()
    leaderboard = await stats_service.get_leaderboard(
        db=db,
        period=period,
        limit=limit,
        chamber=chamber,
        party=party,
    )

    return {
        "leaderboard": leaderboard,
        "period": period,
        "limit": limit,
        "count": len(leaderboard),
        "filters": {
            "chamber": chamber,
            "party": party,
        },
    }


@router.get("/sectors")
async def get_sector_stats(
    period: Literal["7d", "30d", "90d", "1y", "all"] = Query(
        default="30d",
        description="Time period for sector analysis",
    ),
    db: AsyncSession = Depends(get_db),
) -> dict:
    """
    Get sector (ticker) trading statistics.

    Note: Currently groups by ticker. A full sector implementation would
    require a market data API to map tickers to industry sectors.

    Args:
        period: Time period
        db: Database session

    Returns:
        Sector statistics with top traded tickers
    """
    stats_service = StatisticsService()
    sector_stats = await stats_service.get_sector_stats(
        db=db,
        period=period,
    )

    return sector_stats


@router.get("/recent")
async def get_recent_trades(
    limit: int = Query(
        default=20,
        ge=1,
        le=100,
        description="Maximum number of trades to return",
    ),
    chamber: Literal["senate", "house"] | None = Query(
        default=None,
        description="Filter by chamber",
    ),
    party: str | None = Query(
        default=None,
        description="Filter by party",
    ),
    transaction_type: Literal["buy", "sell"] | None = Query(
        default=None,
        description="Filter by transaction type",
    ),
    db: AsyncSession = Depends(get_db),
) -> dict:
    """
    Get most recent trades with politician information.

    Args:
        limit: Maximum number of trades to return (1-100)
        chamber: Optional filter by chamber
        party: Optional filter by party
        transaction_type: Optional filter by transaction type
        db: Database session

    Returns:
        List of recent trades with full details
    """
    stats_service = StatisticsService()
    trades = await stats_service.get_recent_trades(
        db=db,
        limit=limit,
        chamber=chamber,
        party=party,
        transaction_type=transaction_type,
    )

    return {
        "trades": trades,
        "count": len(trades),
        "filters": {
            "chamber": chamber,
            "party": party,
            "transaction_type": transaction_type,
        },
    }
