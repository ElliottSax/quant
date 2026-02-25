"""
Sentiment Analysis Pipeline

Collect, analyze, and score market sentiment from multiple sources using AI.
"""

from typing import Dict, List, Optional, Tuple
from datetime import datetime, timedelta
from enum import Enum
from pydantic import BaseModel
import asyncio
import httpx
from bs4 import BeautifulSoup
import re

from app.core.cache import cache_result
from app.core.config import settings
from app.core.logging import get_logger

logger = get_logger(__name__)


class SentimentScore(str, Enum):
    """Sentiment score categories"""
    VERY_NEGATIVE = "very_negative"
    NEGATIVE = "negative"
    NEUTRAL = "neutral"
    POSITIVE = "positive"
    VERY_POSITIVE = "very_positive"


class SentimentSource(str, Enum):
    """Sentiment data sources"""
    NEWS = "news"
    SOCIAL_MEDIA = "social_media"
    ANALYST_REPORTS = "analyst_reports"
    EARNINGS_CALLS = "earnings_calls"
    SEC_FILINGS = "sec_filings"


class SentimentData(BaseModel):
    """Sentiment data point"""
    symbol: str
    source: SentimentSource
    text: str
    score: float  # -1 to 1
    category: SentimentScore
    confidence: float  # 0 to 1
    timestamp: datetime
    url: Optional[str] = None
    author: Optional[str] = None
    metadata: Dict = {}


class AggregatedSentiment(BaseModel):
    """Aggregated sentiment for a symbol"""
    symbol: str
    overall_score: float  # -1 to 1
    overall_category: SentimentScore
    confidence: float
    timestamp: datetime
    source_breakdown: Dict[str, float]
    total_sources: int
    positive_count: int
    negative_count: int
    neutral_count: int
    trend_24h: Optional[float] = None  # Change from 24h ago


class SentimentAnalyzer:
    """
    Analyze sentiment from various sources

    Collects and analyzes sentiment using:
    - News article scraping
    - Social media monitoring (when available)
    - AI-powered sentiment scoring
    - Trend analysis
    """

    def __init__(self, ai_provider_router=None):
        self.ai_router = ai_provider_router
        self.http_client = httpx.AsyncClient(timeout=30.0)

    async def analyze_symbol(
        self,
        symbol: str,
        sources: Optional[List[SentimentSource]] = None,
        limit_per_source: int = 10
    ) -> AggregatedSentiment:
        """
        Analyze sentiment for a symbol from multiple sources

        Args:
            symbol: Stock symbol
            sources: List of sources to check (default: all)
            limit_per_source: Max items per source

        Returns:
            Aggregated sentiment analysis
        """
        if sources is None:
            sources = [SentimentSource.NEWS]  # Start with news only

        # Collect sentiment data from all sources
        sentiment_data: List[SentimentData] = []

        tasks = []
        if SentimentSource.NEWS in sources:
            tasks.append(self._collect_news_sentiment(symbol, limit_per_source))
        if SentimentSource.SOCIAL_MEDIA in sources:
            tasks.append(self._collect_social_sentiment(symbol, limit_per_source))

        results = await asyncio.gather(*tasks, return_exceptions=True)

        for result in results:
            if isinstance(result, list):
                sentiment_data.extend(result)

        # Aggregate sentiment
        return self._aggregate_sentiment(symbol, sentiment_data)

    async def _collect_news_sentiment(
        self,
        symbol: str,
        limit: int = 10
    ) -> List[SentimentData]:
        """Collect and analyze sentiment from news articles"""
        sentiment_data = []

        try:
            # Scrape news headlines (using free APIs or scraping)
            articles = await self._fetch_news_articles(symbol, limit)

            # Analyze each article
            for article in articles:
                try:
                    score, confidence = await self._analyze_text_sentiment(
                        article['title'] + ' ' + article.get('description', '')
                    )

                    sentiment_data.append(SentimentData(
                        symbol=symbol,
                        source=SentimentSource.NEWS,
                        text=article['title'],
                        score=score,
                        category=self._score_to_category(score),
                        confidence=confidence,
                        timestamp=article.get('timestamp', datetime.utcnow()),
                        url=article.get('url'),
                        author=article.get('author'),
                        metadata={'description': article.get('description', '')}
                    ))
                except Exception as e:
                    logger.error(f"Error analyzing article: {e}", exc_info=True)
                    continue

        except Exception as e:
            logger.error(f"Error collecting news sentiment: {e}", exc_info=True)

        return sentiment_data

    async def _fetch_news_articles(
        self,
        symbol: str,
        limit: int = 10
    ) -> List[Dict]:
        """
        Fetch news articles for a symbol

        Uses free news sources and APIs
        """
        articles = []

        try:
            # Integrate with real news APIs
            # Priority: NewsAPI (free tier available), then fallback to mock data

            # Try NewsAPI if configured
            newsapi_key = getattr(settings, 'NEWSAPI_KEY', None)
            if newsapi_key:
                try:
                    articles = await self._fetch_from_newsapi(symbol, newsapi_key, limit)
                    if articles:
                        return articles
                except Exception as e:
                    logger.warning(f"NewsAPI failed, falling back to mock data: {e}")

            # Try Alpha Vantage News if configured
            alpha_vantage_key = getattr(settings, 'ALPHA_VANTAGE_API_KEY', None)
            if alpha_vantage_key:
                try:
                    articles = await self._fetch_from_alpha_vantage_news(symbol, alpha_vantage_key, limit)
                    if articles:
                        return articles
                except Exception as e:
                    logger.warning(f"Alpha Vantage News failed, falling back to mock data: {e}")

            # Fallback to mock data for development/testing
            logger.info(f"Using mock news data for {symbol}")
            mock_articles = [
                {
                    'title': f'{symbol} reaches new milestone in market performance',
                    'description': 'Company shows strong growth indicators',
                    'timestamp': datetime.utcnow() - timedelta(hours=2),
                    'url': f'https://example.com/news/{symbol}/1',
                    'author': 'Financial Times'
                },
                {
                    'title': f'Analysts upgrade {symbol} target price',
                    'description': 'Increased confidence in future earnings',
                    'timestamp': datetime.utcnow() - timedelta(hours=5),
                    'url': f'https://example.com/news/{symbol}/2',
                    'author': 'Bloomberg'
                },
                {
                    'title': f'{symbol} faces regulatory challenges',
                    'description': 'New compliance requirements may impact operations',
                    'timestamp': datetime.utcnow() - timedelta(hours=8),
                    'url': f'https://example.com/news/{symbol}/3',
                    'author': 'Reuters'
                }
            ]

            articles = mock_articles[:limit]

        except Exception as e:
            logger.error(f"Error fetching news: {e}", exc_info=True)

        return articles

    async def _fetch_from_newsapi(
        self,
        symbol: str,
        api_key: str,
        limit: int = 10
    ) -> List[Dict]:
        """
        Fetch news from NewsAPI.org

        NewsAPI provides free tier with 100 requests/day for development.
        """
        articles = []

        try:
            # Search for company news
            url = "https://newsapi.org/v2/everything"
            params = {
                "q": f"{symbol} stock OR {symbol} company",
                "language": "en",
                "sortBy": "publishedAt",
                "pageSize": min(limit, 100),
                "apiKey": api_key,
            }

            async with httpx.AsyncClient() as client:
                response = await client.get(url, params=params, timeout=30.0)
                response.raise_for_status()

                data = response.json()
                if data.get("status") == "ok":
                    for article in data.get("articles", [])[:limit]:
                        articles.append({
                            "title": article.get("title", ""),
                            "description": article.get("description", ""),
                            "timestamp": datetime.fromisoformat(
                                article.get("publishedAt", "").replace("Z", "+00:00")
                            ),
                            "url": article.get("url", ""),
                            "author": article.get("source", {}).get("name", "Unknown"),
                        })

        except Exception as e:
            logger.error(f"NewsAPI fetch failed: {e}")
            raise

        return articles

    async def _fetch_from_alpha_vantage_news(
        self,
        symbol: str,
        api_key: str,
        limit: int = 10
    ) -> List[Dict]:
        """
        Fetch news from Alpha Vantage News Sentiment API.

        Alpha Vantage provides free tier with 25 requests/day.
        """
        articles = []

        try:
            url = "https://www.alphavantage.co/query"
            params = {
                "function": "NEWS_SENTIMENT",
                "tickers": symbol,
                "apikey": api_key,
                "limit": min(limit, 50),
            }

            async with httpx.AsyncClient() as client:
                response = await client.get(url, params=params, timeout=30.0)
                response.raise_for_status()

                data = response.json()
                if "feed" in data:
                    for item in data["feed"][:limit]:
                        articles.append({
                            "title": item.get("title", ""),
                            "description": item.get("summary", ""),
                            "timestamp": datetime.fromisoformat(
                                item.get("time_published", "").replace("T", " ").replace("Z", "+00:00")
                            ) if item.get("time_published") else datetime.utcnow(),
                            "url": item.get("url", ""),
                            "author": item.get("source", "Unknown"),
                        })

        except Exception as e:
            logger.error(f"Alpha Vantage News fetch failed: {e}")
            raise

        return articles

    async def _collect_social_sentiment(
        self,
        symbol: str,
        limit: int = 10
    ) -> List[SentimentData]:
        """Collect sentiment from social media"""
        # Placeholder for social media integration
        # Would integrate with Twitter API, Reddit API, StockTwits, etc.
        return []

    async def _analyze_text_sentiment(self, text: str) -> Tuple[float, float]:
        """
        Analyze sentiment of text using AI

        Args:
            text: Text to analyze

        Returns:
            Tuple of (score, confidence)
            score: -1 (very negative) to 1 (very positive)
            confidence: 0 to 1
        """
        # If AI router available, use it for sentiment analysis
        if self.ai_router:
            try:
                prompt = f"""Analyze the sentiment of this financial text and respond with only two numbers separated by a comma:
1. Sentiment score from -1 (very negative) to 1 (very positive)
2. Confidence level from 0 (not confident) to 1 (very confident)

Text: {text}

Response format: score,confidence
Example: 0.7,0.85"""

                response = await self.ai_router.generate_text(prompt, max_tokens=20)

                # Parse response
                parts = response.strip().split(',')
                if len(parts) == 2:
                    score = float(parts[0].strip())
                    confidence = float(parts[1].strip())
                    return max(-1, min(1, score)), max(0, min(1, confidence))
            except Exception as e:
                logger.error(f"AI sentiment analysis failed: {e}", exc_info=True)

        # Fallback to simple keyword-based sentiment
        return self._simple_sentiment_analysis(text)

    def _simple_sentiment_analysis(self, text: str) -> Tuple[float, float]:
        """
        Simple keyword-based sentiment analysis

        Used as fallback when AI is unavailable
        """
        text_lower = text.lower()

        # Positive keywords
        positive_keywords = [
            'growth', 'profit', 'strong', 'bullish', 'upgrade', 'beat',
            'exceed', 'positive', 'good', 'great', 'excellent', 'surge',
            'rally', 'gain', 'up', 'high', 'success', 'milestone', 'record'
        ]

        # Negative keywords
        negative_keywords = [
            'loss', 'decline', 'weak', 'bearish', 'downgrade', 'miss',
            'below', 'negative', 'bad', 'poor', 'terrible', 'crash',
            'fall', 'down', 'low', 'failure', 'concern', 'risk', 'warning'
        ]

        # Count keywords
        positive_count = sum(1 for word in positive_keywords if word in text_lower)
        negative_count = sum(1 for word in negative_keywords if word in text_lower)

        total_count = positive_count + negative_count

        if total_count == 0:
            return 0.0, 0.3  # Neutral with low confidence

        # Calculate score
        score = (positive_count - negative_count) / total_count

        # Calculate confidence based on keyword density
        word_count = len(text_lower.split())
        keyword_density = total_count / word_count if word_count > 0 else 0
        confidence = min(keyword_density * 5, 0.7)  # Max 0.7 for simple analysis

        return score, confidence

    def _score_to_category(self, score: float) -> SentimentScore:
        """Convert numerical score to category"""
        if score >= 0.6:
            return SentimentScore.VERY_POSITIVE
        elif score >= 0.2:
            return SentimentScore.POSITIVE
        elif score <= -0.6:
            return SentimentScore.VERY_NEGATIVE
        elif score <= -0.2:
            return SentimentScore.NEGATIVE
        else:
            return SentimentScore.NEUTRAL

    def _aggregate_sentiment(
        self,
        symbol: str,
        sentiment_data: List[SentimentData]
    ) -> AggregatedSentiment:
        """Aggregate multiple sentiment data points"""
        if not sentiment_data:
            return AggregatedSentiment(
                symbol=symbol,
                overall_score=0.0,
                overall_category=SentimentScore.NEUTRAL,
                confidence=0.0,
                timestamp=datetime.utcnow(),
                source_breakdown={},
                total_sources=0,
                positive_count=0,
                negative_count=0,
                neutral_count=0
            )

        # Calculate weighted average score
        total_weight = sum(d.confidence for d in sentiment_data)
        if total_weight > 0:
            weighted_score = sum(d.score * d.confidence for d in sentiment_data) / total_weight
        else:
            weighted_score = sum(d.score for d in sentiment_data) / len(sentiment_data)

        # Calculate source breakdown
        source_breakdown = {}
        for source in SentimentSource:
            source_data = [d for d in sentiment_data if d.source == source]
            if source_data:
                source_avg = sum(d.score for d in source_data) / len(source_data)
                source_breakdown[source.value] = round(source_avg, 3)

        # Count categories
        positive_count = sum(1 for d in sentiment_data if d.score > 0.2)
        negative_count = sum(1 for d in sentiment_data if d.score < -0.2)
        neutral_count = len(sentiment_data) - positive_count - negative_count

        # Calculate overall confidence
        avg_confidence = sum(d.confidence for d in sentiment_data) / len(sentiment_data)

        return AggregatedSentiment(
            symbol=symbol,
            overall_score=round(weighted_score, 3),
            overall_category=self._score_to_category(weighted_score),
            confidence=round(avg_confidence, 3),
            timestamp=datetime.utcnow(),
            source_breakdown=source_breakdown,
            total_sources=len(sentiment_data),
            positive_count=positive_count,
            negative_count=negative_count,
            neutral_count=neutral_count
        )

    async def analyze_correlation(
        self,
        symbol: str,
        sentiment_history: List[AggregatedSentiment],
        price_data: List[Tuple[datetime, float]]
    ) -> Dict:
        """
        Analyze correlation between sentiment and price movements

        Args:
            symbol: Stock symbol
            sentiment_history: Historical sentiment data
            price_data: Historical price data (timestamp, price)

        Returns:
            Correlation analysis results
        """
        if len(sentiment_history) < 2 or len(price_data) < 2:
            return {
                'correlation': 0.0,
                'lag_days': 0,
                'strength': 'insufficient_data'
            }

        # Align timestamps and extract values
        # This is simplified - in production, use proper time series alignment
        sentiment_scores = [s.overall_score for s in sentiment_history]
        prices = [p for _, p in price_data]

        # Calculate price returns
        price_returns = [
            (prices[i] - prices[i-1]) / prices[i-1]
            for i in range(1, len(prices))
        ]

        # Simple correlation (would use numpy/scipy in production)
        if len(sentiment_scores) > len(price_returns):
            sentiment_scores = sentiment_scores[:len(price_returns)]
        elif len(price_returns) > len(sentiment_scores):
            price_returns = price_returns[:len(sentiment_scores)]

        # Simplified correlation calculation
        correlation = 0.0
        if sentiment_scores and price_returns:
            import numpy as np
            correlation = float(np.corrcoef(sentiment_scores, price_returns)[0, 1])

        # Determine strength
        abs_corr = abs(correlation)
        if abs_corr > 0.7:
            strength = 'strong'
        elif abs_corr > 0.4:
            strength = 'moderate'
        elif abs_corr > 0.2:
            strength = 'weak'
        else:
            strength = 'very_weak'

        return {
            'symbol': symbol,
            'correlation': round(correlation, 3),
            'strength': strength,
            'sample_size': len(sentiment_scores),
            'analysis_timestamp': datetime.utcnow()
        }


# Global instance
_sentiment_analyzer: Optional[SentimentAnalyzer] = None


def get_sentiment_analyzer(ai_router=None) -> SentimentAnalyzer:
    """Get or create sentiment analyzer instance"""
    global _sentiment_analyzer
    if _sentiment_analyzer is None:
        _sentiment_analyzer = SentimentAnalyzer(ai_router)
    return _sentiment_analyzer
