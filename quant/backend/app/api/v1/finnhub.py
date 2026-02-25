"""
Finnhub API Endpoints

Real-time quotes, news sentiment, and market data from Finnhub
"""

from fastapi import APIRouter, HTTPException, Query
from typing import List, Optional
from datetime import datetime, timedelta
from pydantic import BaseModel

from app.services.finnhub_client import (
    get_finnhub_client,
    FinnhubQuote,
    SentimentScore,
    NewsArticle
)


router = APIRouter(prefix="/finnhub", tags=["finnhub"])


class QuoteResponse(BaseModel):
    """Quote response"""
    quote: FinnhubQuote
    timestamp: str


class SentimentResponse(BaseModel):
    """Sentiment response"""
    sentiment: SentimentScore
    timestamp: str


class NewsResponse(BaseModel):
    """News response"""
    articles: List[NewsArticle]
    count: int
    timestamp: str


@router.get("/demo/quote/{symbol}", response_model=QuoteResponse)
async def get_real_time_quote(symbol: str):
    """
    Get real-time stock quote from Finnhub - DEMO MODE

    Free tier: 60 requests/minute

    Returns:
    - Current price
    - Change and percent change
    - High/low/open
    - Previous close
    """
    client = get_finnhub_client()

    if not client.enabled:
        raise HTTPException(
            status_code=503,
            detail="Finnhub API not configured. Set FINNHUB_API_KEY environment variable."
        )

    try:
        quote = await client.get_quote(symbol)
        return QuoteResponse(
            quote=quote,
            timestamp=datetime.now().isoformat()
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to fetch quote: {str(e)}"
        )


@router.get("/demo/sentiment/{symbol}", response_model=SentimentResponse)
async def get_news_sentiment(
    symbol: str,
    days: int = Query(7, ge=1, le=30, description="Days to look back (1-30)")
):
    """
    Get aggregated news sentiment for a stock - DEMO MODE

    Analyzes recent news articles and returns sentiment score:
    - Sentiment: -1 (very negative) to 1 (very positive)
    - Score: 0-100
    - Label: positive, neutral, or negative

    Free tier: 60 requests/minute
    """
    client = get_finnhub_client()

    if not client.enabled:
        raise HTTPException(
            status_code=503,
            detail="Finnhub API not configured. Set FINNHUB_API_KEY environment variable."
        )

    try:
        sentiment = await client.get_news_sentiment(symbol, days)
        return SentimentResponse(
            sentiment=sentiment,
            timestamp=datetime.now().isoformat()
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to fetch sentiment: {str(e)}"
        )


@router.get("/demo/news/{symbol}", response_model=NewsResponse)
async def get_company_news(
    symbol: str,
    days: int = Query(7, ge=1, le=30, description="Days to look back"),
    limit: int = Query(20, ge=1, le=100, description="Max articles to return")
):
    """
    Get recent company news - DEMO MODE

    Returns news articles for a specific company from major sources.

    Free tier: 60 requests/minute
    """
    client = get_finnhub_client()

    if not client.enabled:
        raise HTTPException(
            status_code=503,
            detail="Finnhub API not configured. Set FINNHUB_API_KEY environment variable."
        )

    try:
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)

        news_data = await client.get_company_news(
            symbol=symbol,
            start_date=start_date.strftime("%Y-%m-%d"),
            end_date=end_date.strftime("%Y-%m-%d"),
            limit=limit
        )

        articles = []
        for item in news_data:
            articles.append(NewsArticle(
                headline=item.get("headline", ""),
                summary=item.get("summary", ""),
                source=item.get("source", ""),
                url=item.get("url", ""),
                published_at=datetime.fromtimestamp(item.get("datetime", 0)),
                category=item.get("category", "general")
            ))

        return NewsResponse(
            articles=articles,
            count=len(articles),
            timestamp=datetime.now().isoformat()
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to fetch news: {str(e)}"
        )


@router.get("/demo/market-news", response_model=NewsResponse)
async def get_market_news(
    category: str = Query("general", description="News category"),
    limit: int = Query(20, ge=1, le=100)
):
    """
    Get general market news - DEMO MODE

    Categories:
    - general: General market news
    - forex: Forex news
    - crypto: Cryptocurrency news
    - merger: M&A news

    Free tier: 60 requests/minute
    """
    client = get_finnhub_client()

    if not client.enabled:
        raise HTTPException(
            status_code=503,
            detail="Finnhub API not configured. Set FINNHUB_API_KEY environment variable."
        )

    try:
        articles = await client.get_market_news(category, limit)
        return NewsResponse(
            articles=articles,
            count=len(articles),
            timestamp=datetime.now().isoformat()
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to fetch market news: {str(e)}"
        )


@router.get("/demo/recommendations/{symbol}")
async def get_analyst_recommendations(symbol: str):
    """
    Get analyst recommendations - DEMO MODE

    Returns buy/hold/sell recommendations from analysts.

    Free tier: 60 requests/minute
    """
    client = get_finnhub_client()

    if not client.enabled:
        raise HTTPException(
            status_code=503,
            detail="Finnhub API not configured. Set FINNHUB_API_KEY environment variable."
        )

    try:
        data = await client.get_recommendation_trends(symbol)
        return {
            "symbol": symbol.upper(),
            "recommendations": data,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to fetch recommendations: {str(e)}"
        )


@router.get("/demo/price-target/{symbol}")
async def get_analyst_price_target(symbol: str):
    """
    Get analyst price targets - DEMO MODE

    Returns average, high, low, and median price targets.

    Free tier: 60 requests/minute
    """
    client = get_finnhub_client()

    if not client.enabled:
        raise HTTPException(
            status_code=503,
            detail="Finnhub API not configured. Set FINNHUB_API_KEY environment variable."
        )

    try:
        data = await client.get_price_target(symbol)
        return {
            "symbol": symbol.upper(),
            "price_target": data,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to fetch price target: {str(e)}"
        )


@router.get("/demo/status")
async def finnhub_status():
    """
    Check Finnhub API status

    Returns whether Finnhub is configured and available.
    """
    client = get_finnhub_client()

    return {
        "enabled": client.enabled,
        "api_key_configured": client.api_key is not None,
        "base_url": client.BASE_URL,
        "rate_limit": "60 requests/minute (free tier)",
        "timestamp": datetime.now().isoformat()
    }
