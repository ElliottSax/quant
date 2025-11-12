"""Trades API endpoints."""

import re
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

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

    # Build query with join to get politician info
    query = select(Trade).join(Politician).options(joinedload(Trade.politician))

    # Apply filters with validation
    if ticker:
        validated_ticker = validate_ticker(ticker)
        query = query.where(Trade.ticker == validated_ticker)

    if transaction_type:
        validated_type = validate_transaction_type(transaction_type)
        query = query.where(Trade.transaction_type == validated_type)

    if politician_id:
        query = query.where(Trade.politician_id == politician_id)

    # Get total count with separate query (more efficient)
    count_query = select(func.count(Trade.id))
    if ticker:
        count_query = count_query.where(Trade.ticker == validate_ticker(ticker))
    if transaction_type:
        count_query = count_query.where(Trade.transaction_type == validate_transaction_type(transaction_type))
    if politician_id:
        count_query = count_query.where(Trade.politician_id == politician_id)

    total_result = await db.execute(count_query)
    total = total_result.scalar_one()

    # Add pagination and ordering (most recent first)
    query = query.order_by(Trade.transaction_date.desc()).offset(skip).limit(limit)

    # Execute query
    result = await db.execute(query)
    trades = result.scalars().all()

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
