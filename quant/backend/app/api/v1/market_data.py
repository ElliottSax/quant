"""
Market Data API Endpoints

Access real-time and historical market data.
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from typing import List, Optional
from datetime import datetime, timedelta

from app.services.market_data import (
    MarketDataProvider,
    MarketDataBar,
    MarketQuote,
    DataProvider,
    Interval,
    get_market_data_provider
)
from app.core.deps import get_current_user
from app.models.user import User


router = APIRouter(prefix="/market-data", tags=["market-data"])


@router.get("/quote/{symbol}")
async def get_quote(
    symbol: str,
    provider: DataProvider = Query(default=DataProvider.YAHOO_FINANCE),
    current_user: User = Depends(get_current_user)
):
    """
    Get real-time quote for a symbol

    Returns current price, bid/ask, volume, and price change
    """
    data_provider = get_market_data_provider(provider)

    try:
        quote = await data_provider.get_quote(symbol.upper())
        return quote
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error fetching quote: {str(e)}"
        )


@router.get("/quotes")
async def get_multiple_quotes(
    symbols: List[str] = Query(...),
    provider: DataProvider = Query(default=DataProvider.YAHOO_FINANCE),
    current_user: User = Depends(get_current_user)
):
    """
    Get quotes for multiple symbols

    Returns dictionary of symbol -> quote
    """
    if len(symbols) > 50:
        raise HTTPException(
            status_code=400,
            detail="Maximum 50 symbols allowed"
        )

    data_provider = get_market_data_provider(provider)

    try:
        quotes = await data_provider.get_multiple_quotes([s.upper() for s in symbols])
        return {
            "quotes": quotes,
            "count": len(quotes),
            "timestamp": datetime.utcnow()
        }
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error fetching quotes: {str(e)}"
        )


@router.get("/historical/{symbol}")
async def get_historical_data(
    symbol: str,
    start_date: datetime = Query(...),
    end_date: datetime = Query(default=None),
    interval: Interval = Query(default=Interval.DAY_1),
    provider: DataProvider = Query(default=DataProvider.YAHOO_FINANCE),
    current_user: User = Depends(get_current_user)
):
    """
    Get historical price data

    Returns OHLCV bars for specified time period
    """
    if end_date is None:
        end_date = datetime.utcnow()

    # Validate date range
    if end_date <= start_date:
        raise HTTPException(
            status_code=400,
            detail="End date must be after start date"
        )

    duration = (end_date - start_date).days
    if duration > 3650:  # 10 years
        raise HTTPException(
            status_code=400,
            detail="Maximum date range is 10 years"
        )

    data_provider = get_market_data_provider(provider)

    try:
        bars = await data_provider.get_historical_data(
            symbol.upper(),
            start_date,
            end_date,
            interval
        )

        return {
            "symbol": symbol.upper(),
            "interval": interval,
            "start_date": start_date,
            "end_date": end_date,
            "bars": [bar.dict() for bar in bars],
            "count": len(bars)
        }
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error fetching historical data: {str(e)}"
        )


@router.get("/company/{symbol}")
async def get_company_info(
    symbol: str,
    provider: DataProvider = Query(default=DataProvider.YAHOO_FINANCE),
    current_user: User = Depends(get_current_user)
):
    """
    Get company information

    Returns company details, sector, industry, description, etc.
    """
    data_provider = get_market_data_provider(provider)

    try:
        info = await data_provider.get_company_info(symbol.upper())
        return info
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error fetching company info: {str(e)}"
        )


@router.get("/search")
async def search_symbols(
    query: str = Query(..., min_length=1),
    limit: int = Query(default=10, le=50),
    current_user: User = Depends(get_current_user)
):
    """
    Search for stock symbols

    Returns matching symbols and company names
    """
    # Placeholder - would integrate with symbol search API
    return {
        "query": query,
        "results": [],
        "message": "Symbol search coming soon. Try exact symbols like AAPL, GOOGL, MSFT"
    }


@router.get("/market-status")
async def get_market_status(
    current_user: User = Depends(get_current_user)
):
    """
    Get market trading status

    Returns whether markets are open/closed and next open/close times
    """
    # Simplified - would integrate with market calendar API
    now = datetime.utcnow()
    hour = now.hour
    weekday = now.weekday()

    # Simple US market hours check (9:30 AM - 4:00 PM ET = 14:30 - 21:00 UTC)
    is_open = (weekday < 5) and (14 <= hour < 21)

    return {
        "is_open": is_open,
        "market": "US",
        "timestamp": now,
        "message": "Market is " + ("open" if is_open else "closed")
    }
