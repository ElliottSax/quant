"""
Multi-provider market data client with automatic fallback.

Supports:
- Alpha Vantage
- Twelve Data
- yfinance
- Finnhub

Features:
- Automatic provider fallback on failures
- Rate limiting per provider
- Redis caching
- Async/await support
"""

import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from enum import Enum

import yfinance as yf
import httpx
import pandas as pd
from redis import Redis

from app.core.config import settings

logger = logging.getLogger(__name__)


class Provider(str, Enum):
    """Available market data providers."""
    YFINANCE = "yfinance"
    ALPHA_VANTAGE = "alpha_vantage"
    TWELVE_DATA = "twelve_data"
    FINNHUB = "finnhub"


class MarketDataClient:
    """
    Multi-provider market data client with automatic fallback.

    Supports async context manager for automatic resource cleanup:
        async with MarketDataClient(redis_client) as client:
            data = await client.get_historical_data("AAPL")
    """

    def __init__(self, redis_client: Optional[Redis] = None):
        """Initialize market data client."""
        self.redis_client = redis_client
        self.client = httpx.AsyncClient(timeout=30.0)
        self._is_closed = False

        # Provider credentials
        self.alpha_vantage_key = getattr(settings, 'ALPHA_VANTAGE_API_KEY', None)
        self.twelve_data_key = getattr(settings, 'TWELVE_DATA_API_KEY', None)
        self.finnhub_key = getattr(settings, 'FINNHUB_API_KEY', None)

        # Provider priority order
        self.provider_order = [
            Provider.YFINANCE,  # Try yfinance first (unlimited)
            Provider.TWELVE_DATA,  # Then Twelve Data (800 req/day)
            Provider.ALPHA_VANTAGE,  # Then Alpha Vantage (25 req/day)
            Provider.FINNHUB,  # Finally Finnhub (60 req/min)
        ]

        logger.info("Initialized MarketDataClient with providers: %s", self.provider_order)

    async def get_historical_data(
        self,
        symbol: str,
        period: str = "1y",
        interval: str = "1d",
        force_provider: Optional[Provider] = None
    ) -> pd.DataFrame:
        """
        Get historical OHLCV data for a symbol.

        Args:
            symbol: Stock ticker symbol
            period: Time period (1d, 5d, 1mo, 3mo, 6mo, 1y, 2y, 5y, 10y, max)
            interval: Data interval (1m, 5m, 15m, 1h, 1d, 1wk, 1mo)
            force_provider: Force specific provider (optional)

        Returns:
            DataFrame with OHLCV data
        """
        cache_key = f"market_data:{symbol}:{period}:{interval}"

        # Try cache first
        if self.redis_client:
            cached_data = await self._get_from_cache(cache_key)
            if cached_data is not None:
                logger.info(f"Cache hit for {symbol}")
                return cached_data

        # Try providers in order
        providers = [force_provider] if force_provider else self.provider_order

        for provider in providers:
            try:
                data = await self._fetch_from_provider(symbol, period, interval, provider)
                if data is not None and not data.empty:
                    # Cache successful result
                    if self.redis_client:
                        await self._save_to_cache(cache_key, data)
                    logger.info(f"Successfully fetched {symbol} from {provider}")
                    return data
            except Exception as e:
                logger.warning(f"Provider {provider} failed for {symbol}: {e}")
                continue

        raise ValueError(f"All providers failed to fetch data for {symbol}")

    async def _fetch_from_provider(
        self,
        symbol: str,
        period: str,
        interval: str,
        provider: Provider
    ) -> Optional[pd.DataFrame]:
        """Fetch data from specific provider."""
        if provider == Provider.YFINANCE:
            return await self._fetch_yfinance(symbol, period, interval)
        elif provider == Provider.ALPHA_VANTAGE:
            return await self._fetch_alpha_vantage(symbol, period, interval)
        elif provider == Provider.TWELVE_DATA:
            return await self._fetch_twelve_data(symbol, period, interval)
        elif provider == Provider.FINNHUB:
            return await self._fetch_finnhub(symbol, period, interval)
        return None

    async def _fetch_yfinance(
        self,
        symbol: str,
        period: str,
        interval: str
    ) -> pd.DataFrame:
        """Fetch data from yfinance."""
        # Run in executor since yfinance is synchronous
        loop = asyncio.get_event_loop()
        ticker = yf.Ticker(symbol)
        data = await loop.run_in_executor(
            None,
            lambda: ticker.history(period=period, interval=interval)
        )
        return data

    async def _fetch_alpha_vantage(
        self,
        symbol: str,
        period: str,
        interval: str
    ) -> Optional[pd.DataFrame]:
        """Fetch data from Alpha Vantage."""
        if not self.alpha_vantage_key:
            return None

        # Map intervals to Alpha Vantage function
        if interval in ['1d', '1wk', '1mo']:
            function = 'TIME_SERIES_DAILY'
            outputsize = 'full' if period in ['5y', '10y', 'max'] else 'compact'
        else:
            # Intraday data
            function = 'TIME_SERIES_INTRADAY'
            outputsize = 'full'

        url = "https://www.alphavantage.co/query"
        params = {
            'function': function,
            'symbol': symbol,
            'apikey': self.alpha_vantage_key,
            'outputsize': outputsize,
            'datatype': 'json'
        }

        if function == 'TIME_SERIES_INTRADAY':
            params['interval'] = interval.replace('m', 'min').replace('h', '60min')

        response = await self.client.get(url, params=params)
        data = response.json()

        # Parse response
        if 'Error Message' in data or 'Note' in data:
            return None

        # Find time series key
        time_series_key = next((k for k in data.keys() if 'Time Series' in k), None)
        if not time_series_key:
            return None

        time_series = data[time_series_key]

        # Convert to DataFrame
        df = pd.DataFrame.from_dict(time_series, orient='index')
        df.index = pd.to_datetime(df.index)
        df = df.sort_index()

        # Rename columns
        df.columns = ['Open', 'High', 'Low', 'Close', 'Volume']
        df = df.astype(float)

        return df

    async def _fetch_twelve_data(
        self,
        symbol: str,
        period: str,
        interval: str
    ) -> Optional[pd.DataFrame]:
        """Fetch data from Twelve Data."""
        if not self.twelve_data_key:
            return None

        url = "https://api.twelvedata.com/time_series"
        params = {
            'symbol': symbol,
            'interval': interval,
            'apikey': self.twelve_data_key,
            'format': 'JSON',
            'outputsize': 5000  # Max allowed
        }

        response = await self.client.get(url, params=params)
        data = response.json()

        if 'status' in data and data['status'] == 'error':
            return None

        if 'values' not in data:
            return None

        # Convert to DataFrame
        df = pd.DataFrame(data['values'])
        df['datetime'] = pd.to_datetime(df['datetime'])
        df = df.set_index('datetime').sort_index()

        # Rename and convert columns
        column_map = {
            'open': 'Open',
            'high': 'High',
            'low': 'Low',
            'close': 'Close',
            'volume': 'Volume'
        }
        df = df.rename(columns=column_map)
        df = df[['Open', 'High', 'Low', 'Close', 'Volume']].astype(float)

        return df

    async def _fetch_finnhub(
        self,
        symbol: str,
        period: str,
        interval: str
    ) -> Optional[pd.DataFrame]:
        """Fetch data from Finnhub."""
        if not self.finnhub_key:
            return None

        # Finnhub uses Unix timestamps
        end_date = int(datetime.now().timestamp())

        # Map period to start date
        period_map = {
            '1d': 1, '5d': 5, '1mo': 30, '3mo': 90,
            '6mo': 180, '1y': 365, '2y': 730, '5y': 1825
        }
        days = period_map.get(period, 365)
        start_date = int((datetime.now() - timedelta(days=days)).timestamp())

        # Map interval to resolution
        resolution_map = {
            '1m': '1', '5m': '5', '15m': '15', '30m': '30',
            '1h': '60', '1d': 'D', '1wk': 'W', '1mo': 'M'
        }
        resolution = resolution_map.get(interval, 'D')

        url = f"https://finnhub.io/api/v1/stock/candle"
        params = {
            'symbol': symbol,
            'resolution': resolution,
            'from': start_date,
            'to': end_date,
            'token': self.finnhub_key
        }

        response = await self.client.get(url, params=params)
        data = response.json()

        if data.get('s') != 'ok':
            return None

        # Convert to DataFrame
        df = pd.DataFrame({
            'Open': data['o'],
            'High': data['h'],
            'Low': data['l'],
            'Close': data['c'],
            'Volume': data['v'],
        }, index=pd.to_datetime(data['t'], unit='s'))

        df = df.sort_index()
        return df

    async def get_quote(self, symbol: str) -> Dict[str, Any]:
        """Get real-time quote for a symbol."""
        cache_key = f"quote:{symbol}"

        # Try cache first (5 minute TTL for quotes)
        if self.redis_client:
            cached_quote = await self._get_from_cache(cache_key, ttl=300)
            if cached_quote is not None:
                return cached_quote

        # Try providers
        for provider in self.provider_order:
            try:
                quote = await self._get_quote_from_provider(symbol, provider)
                if quote:
                    if self.redis_client:
                        await self._save_to_cache(cache_key, quote, ttl=300)
                    return quote
            except Exception as e:
                logger.warning(f"Quote fetch failed for {symbol} from {provider}: {e}")
                continue

        raise ValueError(f"Failed to fetch quote for {symbol}")

    async def _get_quote_from_provider(
        self,
        symbol: str,
        provider: Provider
    ) -> Optional[Dict[str, Any]]:
        """Get quote from specific provider."""
        if provider == Provider.YFINANCE:
            ticker = yf.Ticker(symbol)
            info = ticker.info
            return {
                'symbol': symbol,
                'price': info.get('currentPrice', info.get('regularMarketPrice')),
                'change': info.get('regularMarketChange'),
                'change_percent': info.get('regularMarketChangePercent'),
                'volume': info.get('volume'),
                'market_cap': info.get('marketCap'),
            }
        elif provider == Provider.FINNHUB and self.finnhub_key:
            url = f"https://finnhub.io/api/v1/quote"
            params = {'symbol': symbol, 'token': self.finnhub_key}
            response = await self.client.get(url, params=params)
            data = response.json()
            return {
                'symbol': symbol,
                'price': data.get('c'),  # current price
                'change': data.get('d'),  # change
                'change_percent': data.get('dp'),  # change percent
                'high': data.get('h'),
                'low': data.get('l'),
                'open': data.get('o'),
                'previous_close': data.get('pc'),
            }
        return None

    async def _get_from_cache(self, key: str, ttl: int = 3600) -> Optional[Any]:
        """Get data from Redis cache."""
        if not self.redis_client:
            return None
        try:
            import pickle
            data = self.redis_client.get(key)
            if data:
                return pickle.loads(data)
        except Exception as e:
            logger.warning(f"Cache read error: {e}")
        return None

    async def _save_to_cache(self, key: str, data: Any, ttl: int = 3600):
        """Save data to Redis cache."""
        if not self.redis_client:
            return
        try:
            import pickle
            self.redis_client.setex(key, ttl, pickle.dumps(data))
        except Exception as e:
            logger.warning(f"Cache write error: {e}")

    async def close(self):
        """Close HTTP client and release resources."""
        if not self._is_closed:
            await self.client.aclose()
            self._is_closed = True
            logger.debug("MarketDataClient closed")

    async def __aenter__(self):
        """Async context manager entry."""
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit - ensures client is closed."""
        await self.close()
        return False

    def __del__(self):
        """Destructor to warn if client wasn't properly closed."""
        if hasattr(self, '_is_closed') and not self._is_closed:
            logger.warning(
                "MarketDataClient was not properly closed. "
                "Use 'async with MarketDataClient() as client' or call 'await client.close()'"
            )
