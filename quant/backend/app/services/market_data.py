"""
Market Data Integration Service

Fetch real-time and historical market data from multiple providers.
"""

from typing import Dict, List, Optional, Tuple
from datetime import datetime, timedelta
from enum import Enum
import asyncio
from pydantic import BaseModel
import pandas as pd
import numpy as np

# Import data providers
try:
    import yfinance as yf
    YFINANCE_AVAILABLE = True
except ImportError:
    YFINANCE_AVAILABLE = False
    print("Warning: yfinance not installed. Install with: pip install yfinance")

try:
    import httpx
    HTTPX_AVAILABLE = True
except ImportError:
    HTTPX_AVAILABLE = False


class DataProvider(str, Enum):
    """Available data providers"""
    YAHOO_FINANCE = "yahoo_finance"
    ALPHA_VANTAGE = "alpha_vantage"
    POLYGON = "polygon"
    IEX_CLOUD = "iex_cloud"
    MOCK = "mock"  # For testing


class Interval(str, Enum):
    """Data intervals"""
    MINUTE_1 = "1m"
    MINUTE_5 = "5m"
    MINUTE_15 = "15m"
    MINUTE_30 = "30m"
    HOUR_1 = "1h"
    DAY_1 = "1d"
    WEEK_1 = "1wk"
    MONTH_1 = "1mo"


class MarketDataBar(BaseModel):
    """Single price bar"""
    timestamp: datetime
    open: float
    high: float
    low: float
    close: float
    volume: float
    adjusted_close: Optional[float] = None


class MarketQuote(BaseModel):
    """Real-time quote"""
    symbol: str
    price: float
    bid: Optional[float] = None
    ask: Optional[float] = None
    volume: int
    timestamp: datetime
    change: Optional[float] = None
    change_percent: Optional[float] = None
    previous_close: Optional[float] = None


class MarketDataProvider:
    """
    Universal market data provider

    Abstracts multiple data sources and provides consistent interface
    """

    def __init__(self, provider: DataProvider = DataProvider.YAHOO_FINANCE):
        self.provider = provider
        self.http_client = httpx.AsyncClient(timeout=30.0) if HTTPX_AVAILABLE else None

    async def get_historical_data(
        self,
        symbol: str,
        start_date: datetime,
        end_date: datetime,
        interval: Interval = Interval.DAY_1
    ) -> List[MarketDataBar]:
        """
        Get historical price data

        Args:
            symbol: Stock symbol
            start_date: Start date
            end_date: End date
            interval: Data interval

        Returns:
            List of price bars
        """
        if self.provider == DataProvider.YAHOO_FINANCE:
            return await self._fetch_yahoo_historical(symbol, start_date, end_date, interval)
        elif self.provider == DataProvider.MOCK:
            return self._generate_mock_data(symbol, start_date, end_date, interval)
        else:
            raise NotImplementedError(f"Provider {self.provider} not yet implemented")

    async def get_quote(self, symbol: str) -> MarketQuote:
        """
        Get real-time quote

        Args:
            symbol: Stock symbol

        Returns:
            Current market quote
        """
        if self.provider == DataProvider.YAHOO_FINANCE:
            return await self._fetch_yahoo_quote(symbol)
        elif self.provider == DataProvider.MOCK:
            return self._generate_mock_quote(symbol)
        else:
            raise NotImplementedError(f"Provider {self.provider} not yet implemented")

    async def get_multiple_quotes(self, symbols: List[str]) -> Dict[str, MarketQuote]:
        """
        Get quotes for multiple symbols

        Args:
            symbols: List of stock symbols

        Returns:
            Dictionary of symbol -> quote
        """
        tasks = [self.get_quote(symbol) for symbol in symbols]
        results = await asyncio.gather(*tasks, return_exceptions=True)

        quotes = {}
        for symbol, result in zip(symbols, results):
            if isinstance(result, MarketQuote):
                quotes[symbol] = result
            else:
                print(f"Error fetching quote for {symbol}: {result}")

        return quotes

    async def _fetch_yahoo_historical(
        self,
        symbol: str,
        start_date: datetime,
        end_date: datetime,
        interval: Interval
    ) -> List[MarketDataBar]:
        """Fetch historical data from Yahoo Finance"""
        if not YFINANCE_AVAILABLE:
            # Fallback to mock data
            return self._generate_mock_data(symbol, start_date, end_date, interval)

        try:
            # Run in executor to avoid blocking
            loop = asyncio.get_event_loop()
            df = await loop.run_in_executor(
                None,
                lambda: yf.download(
                    symbol,
                    start=start_date,
                    end=end_date,
                    interval=interval.value,
                    progress=False
                )
            )

            if df.empty:
                raise ValueError(f"No data returned for {symbol}")

            # Convert to MarketDataBar objects
            bars = []
            for timestamp, row in df.iterrows():
                bars.append(MarketDataBar(
                    timestamp=timestamp.to_pydatetime(),
                    open=float(row['Open']),
                    high=float(row['High']),
                    low=float(row['Low']),
                    close=float(row['Close']),
                    volume=float(row['Volume']),
                    adjusted_close=float(row['Adj Close']) if 'Adj Close' in row else None
                ))

            return bars

        except Exception as e:
            print(f"Error fetching Yahoo Finance data: {e}")
            # Fallback to mock data
            return self._generate_mock_data(symbol, start_date, end_date, interval)

    async def _fetch_yahoo_quote(self, symbol: str) -> MarketQuote:
        """Fetch real-time quote from Yahoo Finance"""
        if not YFINANCE_AVAILABLE:
            return self._generate_mock_quote(symbol)

        try:
            loop = asyncio.get_event_loop()
            ticker = await loop.run_in_executor(None, lambda: yf.Ticker(symbol))
            info = await loop.run_in_executor(None, lambda: ticker.info)

            current_price = info.get('currentPrice') or info.get('regularMarketPrice', 0)
            previous_close = info.get('previousClose', 0)
            change = current_price - previous_close if previous_close else 0
            change_percent = (change / previous_close * 100) if previous_close else 0

            return MarketQuote(
                symbol=symbol,
                price=current_price,
                bid=info.get('bid'),
                ask=info.get('ask'),
                volume=info.get('volume', 0),
                timestamp=datetime.utcnow(),
                change=change,
                change_percent=change_percent,
                previous_close=previous_close
            )

        except Exception as e:
            print(f"Error fetching Yahoo Finance quote: {e}")
            return self._generate_mock_quote(symbol)

    def _generate_mock_data(
        self,
        symbol: str,
        start_date: datetime,
        end_date: datetime,
        interval: Interval
    ) -> List[MarketDataBar]:
        """Generate mock price data for testing"""
        # Determine number of bars based on interval
        duration = (end_date - start_date).total_seconds()

        interval_seconds = {
            Interval.MINUTE_1: 60,
            Interval.MINUTE_5: 300,
            Interval.MINUTE_15: 900,
            Interval.MINUTE_30: 1800,
            Interval.HOUR_1: 3600,
            Interval.DAY_1: 86400,
            Interval.WEEK_1: 604800,
            Interval.MONTH_1: 2592000
        }

        seconds_per_bar = interval_seconds.get(interval, 86400)
        num_bars = int(duration / seconds_per_bar)

        # Generate random walk price data
        np.random.seed(hash(symbol) % 2**32)
        base_price = 100 + (hash(symbol) % 400)
        returns = np.random.normal(0.0005, 0.02, num_bars)
        prices = base_price * np.exp(np.cumsum(returns))

        bars = []
        current_time = start_date

        for i, close_price in enumerate(prices):
            # Generate OHLC
            high = close_price * (1 + np.random.uniform(0, 0.02))
            low = close_price * (1 - np.random.uniform(0, 0.02))
            open_price = low + np.random.uniform(0, 1) * (high - low)

            # Generate volume
            volume = np.random.uniform(1e6, 10e6)

            bars.append(MarketDataBar(
                timestamp=current_time,
                open=float(open_price),
                high=float(high),
                low=float(low),
                close=float(close_price),
                volume=float(volume),
                adjusted_close=float(close_price)
            ))

            # Increment timestamp
            current_time += timedelta(seconds=seconds_per_bar)

        return bars

    def _generate_mock_quote(self, symbol: str) -> MarketQuote:
        """Generate mock quote for testing"""
        np.random.seed(hash(symbol) % 2**32)
        base_price = 100 + (hash(symbol) % 400)
        current_price = base_price * (1 + np.random.uniform(-0.05, 0.05))
        previous_close = base_price
        change = current_price - previous_close
        change_percent = (change / previous_close) * 100

        return MarketQuote(
            symbol=symbol,
            price=float(current_price),
            bid=float(current_price - np.random.uniform(0.01, 0.1)),
            ask=float(current_price + np.random.uniform(0.01, 0.1)),
            volume=int(np.random.uniform(1e6, 10e6)),
            timestamp=datetime.utcnow(),
            change=float(change),
            change_percent=float(change_percent),
            previous_close=float(previous_close)
        )

    async def get_company_info(self, symbol: str) -> Dict:
        """
        Get company information

        Args:
            symbol: Stock symbol

        Returns:
            Dictionary with company details
        """
        if not YFINANCE_AVAILABLE:
            return {
                "symbol": symbol,
                "name": f"{symbol} Corporation",
                "sector": "Technology",
                "industry": "Software",
                "description": "Mock company data"
            }

        try:
            loop = asyncio.get_event_loop()
            ticker = await loop.run_in_executor(None, lambda: yf.Ticker(symbol))
            info = await loop.run_in_executor(None, lambda: ticker.info)

            return {
                "symbol": symbol,
                "name": info.get('longName', symbol),
                "sector": info.get('sector'),
                "industry": info.get('industry'),
                "description": info.get('longBusinessSummary'),
                "website": info.get('website'),
                "employees": info.get('fullTimeEmployees'),
                "market_cap": info.get('marketCap'),
                "pe_ratio": info.get('trailingPE')
            }

        except Exception as e:
            print(f"Error fetching company info: {e}")
            return {
                "symbol": symbol,
                "error": str(e)
            }

    def to_dataframe(self, bars: List[MarketDataBar]) -> pd.DataFrame:
        """
        Convert bars to pandas DataFrame

        Args:
            bars: List of market data bars

        Returns:
            DataFrame with OHLCV data
        """
        data = {
            'timestamp': [bar.timestamp for bar in bars],
            'open': [bar.open for bar in bars],
            'high': [bar.high for bar in bars],
            'low': [bar.low for bar in bars],
            'close': [bar.close for bar in bars],
            'volume': [bar.volume for bar in bars]
        }

        df = pd.DataFrame(data)
        df.set_index('timestamp', inplace=True)
        return df


# Global instance
_market_data_provider: Optional[MarketDataProvider] = None


def get_market_data_provider(provider: DataProvider = DataProvider.YAHOO_FINANCE) -> MarketDataProvider:
    """Get or create market data provider instance"""
    global _market_data_provider
    if _market_data_provider is None or _market_data_provider.provider != provider:
        _market_data_provider = MarketDataProvider(provider)
    return _market_data_provider
