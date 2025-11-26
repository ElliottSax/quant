"""Statistics API endpoints."""

from datetime import datetime, timedelta
from fastapi import APIRouter, Depends, Query
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.models.politician import Politician
from app.models.trade import Trade

router = APIRouter()


@router.get("/leaderboard")
async def get_leaderboard(
    period: str = Query("30d", regex="^(7d|30d|90d|1y)$"),
    limit: int = Query(10, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
) -> dict:
    """
    Get politician performance leaderboard by trade volume.

    Args:
        period: Time period (7d, 30d, 90d, 1y)
        limit: Maximum number of records to return (1-100)
        db: Database session

    Returns:
        Leaderboard data with politician trading activity
    """
    # Calculate date range
    period_map = {
        "7d": 7,
        "30d": 30,
        "90d": 90,
        "1y": 365
    }
    days = period_map.get(period, 30)
    cutoff_date = datetime.utcnow() - timedelta(days=days)

    # Query for top traders by volume
    query = (
        select(
            Politician.id,
            Politician.name,
            Politician.party,
            func.count(Trade.id).label("trade_count"),
            func.sum(Trade.amount).label("total_volume")
        )
        .join(Trade, Trade.politician_id == Politician.id)
        .where(Trade.transaction_date >= cutoff_date)
        .group_by(Politician.id, Politician.name, Politician.party)
        .order_by(func.sum(Trade.amount).desc())
        .limit(limit)
    )

    result = await db.execute(query)
    leaderboard = []

    for row in result:
        leaderboard.append({
            "politician_id": str(row.id),
            "name": row.name,
            "party": row.party,
            "trade_count": row.trade_count,
            "total_volume": float(row.total_volume) if row.total_volume else 0.0,
            "rank": len(leaderboard) + 1
        })

    return {
        "leaderboard": leaderboard,
        "period": period,
        "total_results": len(leaderboard),
    }


@router.get("/sectors")
async def get_sector_stats(
    period: str = Query("30d", regex="^(7d|30d|90d|1y)$"),
    db: AsyncSession = Depends(get_db),
) -> dict:
    """
    Get sector trading statistics.

    Args:
        period: Time period (7d, 30d, 90d, 1y)
        db: Database session

    Returns:
        Sector statistics showing trading activity by sector
    """
    # Calculate date range
    period_map = {
        "7d": 7,
        "30d": 30,
        "90d": 90,
        "1y": 365
    }
    days = period_map.get(period, 30)
    cutoff_date = datetime.utcnow() - timedelta(days=days)

    # Query for sector statistics
    query = (
        select(
            Trade.ticker_sector.label("sector"),
            func.count(Trade.id).label("trade_count"),
            func.sum(Trade.amount).label("total_volume"),
            func.avg(Trade.amount).label("avg_trade_size")
        )
        .where(Trade.transaction_date >= cutoff_date)
        .where(Trade.ticker_sector.isnot(None))
        .group_by(Trade.ticker_sector)
        .order_by(func.sum(Trade.amount).desc())
    )

    result = await db.execute(query)
    sectors = []

    for row in result:
        sectors.append({
            "sector": row.sector,
            "trade_count": row.trade_count,
            "total_volume": float(row.total_volume) if row.total_volume else 0.0,
            "avg_trade_size": float(row.avg_trade_size) if row.avg_trade_size else 0.0
        })

    return {
        "sectors": sectors,
        "period": period,
        "total_sectors": len(sectors),
    }
