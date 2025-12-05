"""Statistics API endpoints."""

from datetime import datetime, timedelta
from fastapi import APIRouter, Depends, Query
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.cache import cache_manager
from app.core.logging import get_logger
from app.models.politician import Politician
from app.models.trade import Trade

router = APIRouter()
logger = get_logger(__name__)


@router.get("/leaderboard")
async def get_leaderboard(
    period: str = Query("30d", regex="^(7d|30d|90d|1y)$"),
    limit: int = Query(10, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
) -> dict:
    """
    Get politician performance leaderboard by trade volume.

    This endpoint uses Redis caching to improve performance for this expensive
    aggregation query. Cache TTL varies by period:
    - 7d: 5 minutes (more volatile data)
    - 30d: 15 minutes
    - 90d/1y: 1 hour (less volatile data)

    Args:
        period: Time period (7d, 30d, 90d, 1y)
        limit: Maximum number of records to return (1-100)
        db: Database session

    Returns:
        Leaderboard data with politician trading activity
    """
    # Try cache first
    cache_key = f"stats:leaderboard:{period}:{limit}"
    cached_result = await cache_manager.get(cache_key)

    if cached_result:
        logger.info(f"Cache hit for leaderboard: period={period}, limit={limit}")
        return cached_result

    logger.info(f"Cache miss for leaderboard: period={period}, limit={limit}")

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

    response_data = {
        "leaderboard": leaderboard,
        "period": period,
        "total_results": len(leaderboard),
    }

    # Cache result with variable TTL based on period
    ttl_map = {
        "7d": 300,      # 5 minutes (more volatile)
        "30d": 900,     # 15 minutes
        "90d": 3600,    # 1 hour
        "1y": 3600      # 1 hour (less volatile)
    }
    ttl = ttl_map.get(period, 900)
    await cache_manager.set(cache_key, response_data, ttl=ttl)

    logger.debug(f"Cached leaderboard for {ttl}s: period={period}, limit={limit}")

    return response_data


@router.get("/sectors")
async def get_sector_stats(
    period: str = Query("30d", regex="^(7d|30d|90d|1y)$"),
    db: AsyncSession = Depends(get_db),
) -> dict:
    """
    Get sector trading statistics.

    This endpoint uses Redis caching to improve performance for this expensive
    aggregation query. Cache TTL varies by period (same as leaderboard).

    Args:
        period: Time period (7d, 30d, 90d, 1y)
        db: Database session

    Returns:
        Sector statistics showing trading activity by sector
    """
    # Try cache first
    cache_key = f"stats:sectors:{period}"
    cached_result = await cache_manager.get(cache_key)

    if cached_result:
        logger.info(f"Cache hit for sectors: period={period}")
        return cached_result

    logger.info(f"Cache miss for sectors: period={period}")

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

    response_data = {
        "sectors": sectors,
        "period": period,
        "total_sectors": len(sectors),
    }

    # Cache result with variable TTL based on period
    ttl_map = {
        "7d": 300,      # 5 minutes
        "30d": 900,     # 15 minutes
        "90d": 3600,    # 1 hour
        "1y": 3600      # 1 hour
    }
    ttl = ttl_map.get(period, 900)
    await cache_manager.set(cache_key, response_data, ttl=ttl)

    logger.debug(f"Cached sectors for {ttl}s: period={period}")

    return response_data
