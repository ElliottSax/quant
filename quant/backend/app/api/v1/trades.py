"""Trades API endpoints."""

from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from app.core.database import get_db
from app.models import Politician, Trade
from app.schemas import TradeListResponse, TradeResponse, TradeWithPolitician

router = APIRouter()


@router.get("/", response_model=TradeListResponse)
async def list_trades(
    skip: int = 0,
    limit: int = 100,
    ticker: str | None = None,
    transaction_type: str | None = None,
    politician_id: UUID | None = None,
    db: AsyncSession = Depends(get_db),
) -> TradeListResponse:
    """
    List all trades with optional filtering.

    Args:
        skip: Number of records to skip
        limit: Maximum number of records to return (max 100)
        ticker: Filter by ticker symbol
        transaction_type: Filter by transaction type (buy/sell)
        politician_id: Filter by politician ID
        db: Database session

    Returns:
        List of trades with pagination info
    """
    # Limit the maximum number of results
    limit = min(limit, 100)

    # Build query with join to get politician info
    query = select(Trade).join(Politician).options(joinedload(Trade.politician))

    # Apply filters
    if ticker:
        query = query.where(Trade.ticker == ticker.upper())
    if transaction_type:
        query = query.where(Trade.transaction_type == transaction_type.lower())
    if politician_id:
        query = query.where(Trade.politician_id == politician_id)

    # Get total count
    count_query = select(func.count()).select_from(query.subquery())
    total_result = await db.execute(count_query)
    total = total_result.scalar_one()

    # Add pagination and ordering (most recent first)
    query = query.order_by(Trade.transaction_date.desc()).offset(skip).limit(limit)

    # Execute query
    result = await db.execute(query)
    trades = result.scalars().all()

    # Convert to response models with politician info
    trade_responses = []
    for trade in trades:
        trade_dict = {
            "id": trade.id,
            "politician_id": trade.politician_id,
            "ticker": trade.ticker,
            "transaction_type": trade.transaction_type,
            "amount_min": trade.amount_min,
            "amount_max": trade.amount_max,
            "transaction_date": trade.transaction_date,
            "disclosure_date": trade.disclosure_date,
            "source_url": trade.source_url,
            "created_at": trade.created_at,
            "politician_name": trade.politician.name,
            "politician_chamber": trade.politician.chamber,
            "politician_party": trade.politician.party,
            "politician_state": trade.politician.state,
        }
        trade_responses.append(TradeWithPolitician(**trade_dict))

    return TradeListResponse(
        trades=trade_responses,
        total=total,
        skip=skip,
        limit=limit,
    )


@router.get("/{trade_id}", response_model=TradeWithPolitician)
async def get_trade(
    trade_id: UUID,
    db: AsyncSession = Depends(get_db),
) -> TradeWithPolitician:
    """
    Get a specific trade by ID.

    Args:
        trade_id: Trade UUID
        db: Database session

    Returns:
        Trade details with politician information
    """
    # Get trade with politician info
    query = (
        select(Trade)
        .where(Trade.id == trade_id)
        .options(joinedload(Trade.politician))
    )
    result = await db.execute(query)
    trade = result.scalar_one_or_none()

    if not trade:
        raise HTTPException(status_code=404, detail="Trade not found")

    # Create response with politician info
    trade_dict = {
        "id": trade.id,
        "politician_id": trade.politician_id,
        "ticker": trade.ticker,
        "transaction_type": trade.transaction_type,
        "amount_min": trade.amount_min,
        "amount_max": trade.amount_max,
        "transaction_date": trade.transaction_date,
        "disclosure_date": trade.disclosure_date,
        "source_url": trade.source_url,
        "created_at": trade.created_at,
        "politician_name": trade.politician.name,
        "politician_chamber": trade.politician.chamber,
        "politician_party": trade.politician.party,
        "politician_state": trade.politician.state,
    }

    return TradeWithPolitician(**trade_dict)


@router.get("/recent/list", response_model=TradeListResponse)
async def recent_trades(
    limit: int = 50,
    db: AsyncSession = Depends(get_db),
) -> TradeListResponse:
    """
    Get most recent trades.

    Args:
        limit: Maximum number of records to return (max 100)
        db: Database session

    Returns:
        List of recent trades
    """
    # Limit the maximum number of results
    limit = min(limit, 100)

    # Build query
    query = (
        select(Trade)
        .join(Politician)
        .options(joinedload(Trade.politician))
        .order_by(Trade.transaction_date.desc())
        .limit(limit)
    )

    # Execute query
    result = await db.execute(query)
    trades = result.scalars().all()

    # Convert to response models
    trade_responses = []
    for trade in trades:
        trade_dict = {
            "id": trade.id,
            "politician_id": trade.politician_id,
            "ticker": trade.ticker,
            "transaction_type": trade.transaction_type,
            "amount_min": trade.amount_min,
            "amount_max": trade.amount_max,
            "transaction_date": trade.transaction_date,
            "disclosure_date": trade.disclosure_date,
            "source_url": trade.source_url,
            "created_at": trade.created_at,
            "politician_name": trade.politician.name,
            "politician_chamber": trade.politician.chamber,
            "politician_party": trade.politician.party,
            "politician_state": trade.politician.state,
        }
        trade_responses.append(TradeWithPolitician(**trade_dict))

    return TradeListResponse(
        trades=trade_responses,
        total=len(trade_responses),
        skip=0,
        limit=limit,
    )
