"""
Sentiment Analysis API Endpoints

Analyze market sentiment from news, social media, and other sources.
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from typing import List, Optional
from datetime import datetime, timedelta

from app.services.sentiment_analysis import (
    SentimentAnalyzer,
    AggregatedSentiment,
    SentimentData,
    SentimentSource,
    get_sentiment_analyzer
)
from app.core.deps import get_current_user
from app.models.user import User


router = APIRouter(prefix="/sentiment", tags=["sentiment"])


@router.get("/analyze/{symbol}", response_model=AggregatedSentiment)
async def analyze_sentiment(
    symbol: str,
    sources: Optional[List[SentimentSource]] = Query(default=None),
    limit_per_source: int = Query(default=10, le=50),
    current_user: User = Depends(get_current_user)
):
    """
    Analyze current sentiment for a symbol

    Collects and analyzes sentiment from multiple sources:
    - News articles
    - Social media (when available)
    - Analyst reports
    - SEC filings

    Returns aggregated sentiment score with source breakdown
    """
    analyzer = get_sentiment_analyzer()

    try:
        sentiment = await analyzer.analyze_symbol(
            symbol=symbol.upper(),
            sources=sources,
            limit_per_source=limit_per_source
        )
        return sentiment
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Sentiment analysis failed: {str(e)}"
        )


@router.get("/history/{symbol}")
async def get_sentiment_history(
    symbol: str,
    days: int = Query(default=30, le=365),
    current_user: User = Depends(get_current_user)
):
    """
    Get historical sentiment data for a symbol

    Returns sentiment trends over time
    """
    # This would query historical sentiment from database
    # Placeholder for now
    return {
        "symbol": symbol,
        "days": days,
        "history": [],
        "message": "Historical sentiment tracking coming soon"
    }


@router.get("/correlation/{symbol}")
async def analyze_sentiment_correlation(
    symbol: str,
    days: int = Query(default=30, le=365),
    current_user: User = Depends(get_current_user)
):
    """
    Analyze correlation between sentiment and price movements

    Returns correlation coefficient and statistical significance
    """
    # This would integrate with price data and sentiment history
    # Placeholder for now
    return {
        "symbol": symbol,
        "correlation": 0.0,
        "p_value": 1.0,
        "strength": "not_calculated",
        "message": "Sentiment correlation analysis coming soon"
    }


@router.get("/trending")
async def get_trending_sentiment(
    limit: int = Query(default=10, le=50),
    min_confidence: float = Query(default=0.7, ge=0, le=1),
    current_user: User = Depends(get_current_user)
):
    """
    Get trending stocks by sentiment

    Returns symbols with the most significant sentiment changes
    """
    return {
        "trending": [],
        "timestamp": datetime.utcnow(),
        "message": "Trending sentiment coming soon"
    }


@router.get("/market-mood")
async def get_market_mood(
    current_user: User = Depends(get_current_user)
):
    """
    Get overall market sentiment mood

    Aggregates sentiment across major indices and sectors
    """
    return {
        "overall_mood": "neutral",
        "score": 0.0,
        "sectors": {},
        "timestamp": datetime.utcnow(),
        "message": "Market mood analysis coming soon"
    }


@router.post("/alert")
async def create_sentiment_alert(
    symbol: str,
    threshold: float = Query(default=0.6, ge=-1, le=1),
    direction: str = Query(default="any"),  # "positive", "negative", "any"
    current_user: User = Depends(get_current_user)
):
    """
    Create alert for sentiment changes

    Get notified when sentiment crosses threshold
    """
    return {
        "alert_id": "placeholder",
        "symbol": symbol,
        "threshold": threshold,
        "direction": direction,
        "status": "active",
        "message": "Sentiment alerts coming soon"
    }


@router.get("/news/{symbol}")
async def get_sentiment_news(
    symbol: str,
    limit: int = Query(default=20, le=100),
    min_score: Optional[float] = Query(default=None, ge=-1, le=1),
    current_user: User = Depends(get_current_user)
):
    """
    Get news articles with sentiment scores

    Returns recent news articles analyzed for sentiment
    """
    analyzer = get_sentiment_analyzer()

    try:
        # Get news sentiment
        news_data = await analyzer._collect_news_sentiment(symbol.upper(), limit)

        # Filter by score if specified
        if min_score is not None:
            news_data = [n for n in news_data if abs(n.score) >= abs(min_score)]

        # Convert to dict format
        news_list = [
            {
                "text": n.text,
                "score": n.score,
                "category": n.category,
                "confidence": n.confidence,
                "timestamp": n.timestamp,
                "url": n.url,
                "author": n.author
            }
            for n in news_data
        ]

        return {
            "symbol": symbol,
            "news": news_list,
            "count": len(news_list),
            "timestamp": datetime.utcnow()
        }
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error fetching news sentiment: {str(e)}"
        )


@router.get("/compare")
async def compare_sentiment(
    symbols: List[str] = Query(...),
    current_user: User = Depends(get_current_user)
):
    """
    Compare sentiment across multiple symbols

    Returns comparative sentiment analysis for watchlist
    """
    if len(symbols) > 20:
        raise HTTPException(
            status_code=400,
            detail="Maximum 20 symbols allowed"
        )

    analyzer = get_sentiment_analyzer()
    results = []

    for symbol in symbols:
        try:
            sentiment = await analyzer.analyze_symbol(symbol.upper())
            results.append({
                "symbol": symbol.upper(),
                "score": sentiment.overall_score,
                "category": sentiment.overall_category,
                "confidence": sentiment.confidence
            })
        except Exception:
            continue

    # Sort by sentiment score
    results.sort(key=lambda x: x['score'], reverse=True)

    return {
        "comparison": results,
        "count": len(results),
        "timestamp": datetime.utcnow()
    }


@router.get("/sector/{sector}")
async def get_sector_sentiment(
    sector: str,
    current_user: User = Depends(get_current_user)
):
    """
    Get aggregated sentiment for a sector

    Analyzes sentiment across all stocks in a sector
    """
    return {
        "sector": sector,
        "overall_score": 0.0,
        "top_positive": [],
        "top_negative": [],
        "message": "Sector sentiment coming soon"
    }
