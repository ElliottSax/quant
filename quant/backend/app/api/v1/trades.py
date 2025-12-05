"""Trades API endpoints."""

import re
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload
from sqlalchemy.sql import Select

from app.core.database import get_db
from app.core.exceptions import BadRequestException, NotFoundException
from app.core.logging import get_logger
from app.models import Politician, Trade
from app.schemas import TradeListResponse, TradeResponse, TradeWithPolitician

logger = get_logger(__name__)
router = APIRouter()


def trade_to_response(trade: Trade) -> dict:
    """
    Convert Trade model to response dictionary.

    Args:
        trade: Trade model instance (must have politician loaded)

    Returns:
        Dictionary with trade and politician information
    """
    return {
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


def validate_ticker(ticker: str) -> str:
    """
    Validate ticker symbol format.

    Args:
        ticker: Ticker symbol to validate

    Returns:
        Validated ticker in uppercase

    Raises:
        BadRequestException: If ticker format is invalid
    """
    # Allow letters, numbers, dots, and hyphens (for class shares and special tickers)
    if not re.match(r"^[A-Z0-9\.\-]+$", ticker.upper()):
        raise BadRequestException(f"Invalid ticker format: {ticker}")

    if len(ticker) > 10:
        raise BadRequestException("Ticker must be 10 characters or less")

    return ticker.upper()


def validate_transaction_type(transaction_type: str) -> str:
    """
    Validate transaction type.

    Args:
        transaction_type: Transaction type to validate

    Returns:
        Validated transaction type in lowercase

    Raises:
        BadRequestException: If transaction type is invalid
    """
    transaction_type_lower = transaction_type.lower()
    if transaction_type_lower not in ["buy", "sell"]:
        raise BadRequestException(
            f"Invalid transaction type: {transaction_type}. Must be 'buy' or 'sell'"
        )
    return transaction_type_lower


def apply_trade_filters(
    query: Select,
    ticker: str | None = None,
    transaction_type: str | None = None,
    politician_id: UUID | None = None,
) -> Select:
    """
    Apply filters to trade query (reusable for both count and data queries).

    This helper function ensures filter logic is consistent between count
    and data queries, improving maintainability and reducing code duplication.

    Args:
        query: SQLAlchemy select query to add filters to
        ticker: Filter by ticker symbol (will be validated)
        transaction_type: Filter by transaction type (will be validated)
        politician_id: Filter by politician UUID

    Returns:
        Query with filters applied
    """
    if ticker:
        validated_ticker = validate_ticker(ticker)
        query = query.where(Trade.ticker == validated_ticker)

    if transaction_type:
        validated_type = validate_transaction_type(transaction_type)
        query = query.where(Trade.transaction_type == validated_type)

    if politician_id:
        query = query.where(Trade.politician_id == politician_id)

    return query


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
    logger.debug(f"Listing trades: skip={skip}, limit={limit}, ticker={ticker}")

    # Validate inputs
    if skip < 0:
        raise BadRequestException("Skip must be non-negative")
    if limit < 1 or limit > 100:
        raise BadRequestException("Limit must be between 1 and 100")

    # Limit the maximum number of results
    limit = min(limit, 100)

    # Build base query for counting (optimized - no joins needed for count)
    count_query = select(func.count(Trade.id))
    count_query = apply_trade_filters(count_query, ticker, transaction_type, politician_id)

    # Build data query with join to get politician info
    data_query = select(Trade).join(Politician).options(joinedload(Trade.politician))
    data_query = apply_trade_filters(data_query, ticker, transaction_type, politician_id)

    # Add pagination and ordering (most recent first)
    data_query = data_query.order_by(Trade.transaction_date.desc()).offset(skip).limit(limit)

    # Execute both queries concurrently for better performance
    # Note: In production with connection pooling, concurrent execution
    # can reduce total wait time if database has capacity
    import asyncio

    count_task = db.execute(count_query)
    data_task = db.execute(data_query)

    total_result, data_result = await asyncio.gather(count_task, data_task)

    total = total_result.scalar_one()
    trades = data_result.scalars().all()

    # Convert to response models using helper function
    trade_responses = [
        TradeWithPolitician(**trade_to_response(trade)) for trade in trades
    ]

    logger.info(f"Retrieved {len(trade_responses)} trades (total: {total})")

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
    logger.debug(f"Fetching trade: {trade_id}")

    # Get trade with politician info
    query = (
        select(Trade)
        .where(Trade.id == trade_id)
        .options(joinedload(Trade.politician))
    )
    result = await db.execute(query)
    trade = result.scalar_one_or_none()

    if not trade:
        logger.warning(f"Trade not found: {trade_id}")
        raise NotFoundException("Trade", str(trade_id))

    logger.info(f"Retrieved trade: {trade_id}")
    return TradeWithPolitician(**trade_to_response(trade))


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
    logger.debug(f"Fetching recent trades: limit={limit}")

    # Validate and limit the maximum number of results
    if limit < 1:
        raise BadRequestException("Limit must be positive")

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

    # Convert to response models using helper function
    trade_responses = [
        TradeWithPolitician(**trade_to_response(trade)) for trade in trades
    ]

    logger.info(f"Retrieved {len(trade_responses)} recent trades")

    return TradeListResponse(
        trades=trade_responses,
        total=len(trade_responses),
        skip=0,
        limit=limit,
    )
