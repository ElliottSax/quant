"""
Finnhub API Client

Free tier: 60 requests/minute
Features:
- Real-time stock quotes
- News sentiment analysis
- Company news
- Market news
"""

import os
from typing import Optional, List, Dict, Any
from datetime import datetime, timedelta
import aiohttp
from pydantic import BaseModel
import logging

logger = logging.getLogger(__name__)


class FinnhubQuote(BaseModel):
    """Real-time stock quote"""
    symbol: str
    current_price: float
    change: float
    percent_change: float
    high: float
    low: float
    open: float
    previous_close: float
    timestamp: datetime


class SentimentScore(BaseModel):
    """News sentiment score"""
    symbol: str
    sentiment: float  # -1 (very negative) to 1 (very positive)
    score: float  # 0-100
    label: str  # "positive", "neutral", "negative"
    news_count: int
    timestamp: datetime


class NewsArticle(BaseModel):
    """News article with sentiment"""
    headline: str
    summary: str
    source: str
    url: str
    published_at: datetime
    sentiment: Optional[float] = None
    category: str = "general"


class FinnhubClient:
    """
    Finnhub API client for stock data and sentiment

    Free tier limits:
    - 60 API calls per minute
    - 30 calls per second
    """

    BASE_URL = "https://finnhub.io/api/v1"

    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize Finnhub client

        Args:
            api_key: Finnhub API key (defaults to FINNHUB_API_KEY env var)
        """
        self.api_key = api_key or os.getenv("FINNHUB_API_KEY")

        if not self.api_key:
            logger.warning("Finnhub API key not configured. Service will be unavailable.")
            self.enabled = False
        else:
            self.enabled = True

        self._session: Optional[aiohttp.ClientSession] = None

    async def _get_session(self) -> aiohttp.ClientSession:
        """Get or create aiohttp session"""
        if self._session is None or self._session.closed:
            self._session = aiohttp.ClientSession()
        return self._session

    async def close(self):
        """Close aiohttp session"""
        if self._session and not self._session.closed:
            await self._session.close()

    async def _request(
        self,
        endpoint: str,
        params: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Make API request to Finnhub

        Args:
            endpoint: API endpoint path
            params: Query parameters

        Returns:
            API response as dictionary
        """
        if not self.enabled:
            raise ValueError("Finnhub API key not configured")

        url = f"{self.BASE_URL}/{endpoint}"

        # Add API key to params
        request_params = params.copy() if params else {}
        request_params["token"] = self.api_key

        session = await self._get_session()

        try:
            async with session.get(url, params=request_params) as response:
                if response.status == 429:
                    raise Exception("Finnhub rate limit exceeded (60/min)")
                elif response.status != 200:
                    error_text = await response.text()
                    raise Exception(f"Finnhub API error {response.status}: {error_text}")

                return await response.json()
        except aiohttp.ClientError as e:
            raise Exception(f"Finnhub request failed: {str(e)}")

    async def get_quote(self, symbol: str) -> FinnhubQuote:
        """
        Get real-time stock quote

        Args:
            symbol: Stock ticker symbol (e.g., "AAPL")

        Returns:
            Real-time quote data
        """
        data = await self._request("quote", {"symbol": symbol.upper()})

        return FinnhubQuote(
            symbol=symbol.upper(),
            current_price=data.get("c", 0),
            change=data.get("d", 0),
            percent_change=data.get("dp", 0),
            high=data.get("h", 0),
            low=data.get("l", 0),
            open=data.get("o", 0),
            previous_close=data.get("pc", 0),
            timestamp=datetime.fromtimestamp(data.get("t", 0))
        )

    async def get_news_sentiment(
        self,
        symbol: str,
        days: int = 7
    ) -> SentimentScore:
        """
        Get aggregated news sentiment for a symbol

        Args:
            symbol: Stock ticker symbol
            days: Number of days to look back (default: 7)

        Returns:
            Aggregated sentiment score
        """
        # Get company news
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)

        news = await self.get_company_news(
            symbol=symbol,
            start_date=start_date.strftime("%Y-%m-%d"),
            end_date=end_date.strftime("%Y-%m-%d")
        )

        if not news:
            # No news available
            return SentimentScore(
                symbol=symbol.upper(),
                sentiment=0.0,
                score=50.0,
                label="neutral",
                news_count=0,
                timestamp=datetime.now()
            )

        # Calculate average sentiment
        sentiments = []
        for article in news:
            if article.get("sentiment"):
                sentiments.append(article["sentiment"])

        if sentiments:
            avg_sentiment = sum(sentiments) / len(sentiments)
        else:
            avg_sentiment = 0.0

        # Convert to 0-100 score
        score = (avg_sentiment + 1) * 50  # -1 to 1 → 0 to 100

        # Determine label
        if score >= 60:
            label = "positive"
        elif score <= 40:
            label = "negative"
        else:
            label = "neutral"

        return SentimentScore(
            symbol=symbol.upper(),
            sentiment=avg_sentiment,
            score=score,
            label=label,
            news_count=len(news),
            timestamp=datetime.now()
        )

    async def get_company_news(
        self,
        symbol: str,
        start_date: str,
        end_date: str,
        limit: int = 50
    ) -> List[Dict[str, Any]]:
        """
        Get company news articles

        Args:
            symbol: Stock ticker symbol
            start_date: Start date (YYYY-MM-DD)
            end_date: End date (YYYY-MM-DD)
            limit: Maximum number of articles

        Returns:
            List of news articles
        """
        data = await self._request(
            "company-news",
            {
                "symbol": symbol.upper(),
                "from": start_date,
                "to": end_date
            }
        )

        # Limit results
        if isinstance(data, list):
            return data[:limit]
        return []

    async def get_market_news(
        self,
        category: str = "general",
        limit: int = 20
    ) -> List[NewsArticle]:
        """
        Get market news

        Args:
            category: News category (general, forex, crypto, merger)
            limit: Maximum number of articles

        Returns:
            List of news articles
        """
        data = await self._request(
            "news",
            {"category": category}
        )

        articles = []
        for item in data[:limit]:
            articles.append(NewsArticle(
                headline=item.get("headline", ""),
                summary=item.get("summary", ""),
                source=item.get("source", ""),
                url=item.get("url", ""),
                published_at=datetime.fromtimestamp(item.get("datetime", 0)),
                category=category
            ))

        return articles

    async def get_recommendation_trends(self, symbol: str) -> Dict[str, Any]:
        """
        Get analyst recommendation trends

        Args:
            symbol: Stock ticker symbol

        Returns:
            Recommendation trends (buy, hold, sell counts)
        """
        data = await self._request(
            "stock/recommendation",
            {"symbol": symbol.upper()}
        )

        return data

    async def get_price_target(self, symbol: str) -> Dict[str, Any]:
        """
        Get analyst price targets

        Args:
            symbol: Stock ticker symbol

        Returns:
            Price target data (high, low, average, median)
        """
        data = await self._request(
            "stock/price-target",
            {"symbol": symbol.upper()}
        )

        return data


# Global client instance
_finnhub_client: Optional[FinnhubClient] = None


def get_finnhub_client() -> FinnhubClient:
    """Get global Finnhub client instance"""
    global _finnhub_client
    if _finnhub_client is None:
        _finnhub_client = FinnhubClient()
    return _finnhub_client


async def close_finnhub_client():
    """Close global Finnhub client"""
    global _finnhub_client
    if _finnhub_client:
        await _finnhub_client.close()
        _finnhub_client = None
