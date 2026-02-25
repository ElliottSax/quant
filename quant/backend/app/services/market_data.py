"""
Market Data Integration Service

Fetch real-time and historical market data from multiple providers.
Supports: Yahoo Finance, Alpha Vantage, Polygon.io, Finnhub
"""

from typing import Dict, List, Optional
from datetime import datetime, timedelta
from enum import Enum
import asyncio
import os
import logging
from pydantic import BaseModel
import pandas as pd
import numpy as np

logger = logging.getLogger(__name__)

# Import data providers
try:
    import yfinance as yf
    YFINANCE_AVAILABLE = True
except ImportError:
    YFINANCE_AVAILABLE = False
    logger.warning("yfinance not installed. Install with: pip install yfinance")

try:
    import httpx
    HTTPX_AVAILABLE = True
except ImportError:
    HTTPX_AVAILABLE = False
    logger.warning("httpx not installed. Install with: pip install httpx")


class DataProvider(str, Enum):
    """Available data providers"""
    YAHOO_FINANCE = "yahoo_finance"
    ALPHA_VANTAGE = "alpha_vantage"
    POLYGON = "polygon"
    FINNHUB = "finnhub"
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
    provider: Optional[str] = None


class MarketDataProvider:
    """
    Universal market data provider

    Abstracts multiple data sources and provides consistent interface
    """

    # API Keys from environment
    ALPHA_VANTAGE_API_KEY = os.getenv("ALPHA_VANTAGE_API_KEY", "")
    POLYGON_API_KEY = os.getenv("POLYGON_API_KEY", "")
    FINNHUB_API_KEY = os.getenv("FINNHUB_API_KEY", "")
    IEX_API_KEY = os.getenv("IEX_API_KEY", "")

    # API Base URLs
    ALPHA_VANTAGE_BASE = "https://www.alphavantage.co/query"
    POLYGON_BASE = "https://api.polygon.io"
    FINNHUB_BASE = "https://finnhub.io/api/v1"

    def __init__(self, provider: DataProvider = DataProvider.YAHOO_FINANCE):
        self.provider = provider
        self.http_client = httpx.AsyncClient(timeout=30.0) if HTTPX_AVAILABLE else None

    async def close(self):
        """Close HTTP client"""
        if self.http_client:
            await self.http_client.aclose()

    async def get_historical_data(
        self,
        symbol: str,
        start_date: datetime,
        end_date: datetime,
        interval: Interval = Interval.DAY_1
    ) -> List[MarketDataBar]:
        """Get historical price data from configured provider"""

        if self.provider == DataProvider.YAHOO_FINANCE:
            return await self._fetch_yahoo_historical(symbol, start_date, end_date, interval)
        elif self.provider == DataProvider.ALPHA_VANTAGE:
            return await self._fetch_alpha_vantage_historical(symbol, start_date, end_date, interval)
        elif self.provider == DataProvider.POLYGON:
            return await self._fetch_polygon_historical(symbol, start_date, end_date, interval)
        elif self.provider == DataProvider.FINNHUB:
            return await self._fetch_finnhub_historical(symbol, start_date, end_date, interval)
        elif self.provider == DataProvider.MOCK:
            return self._generate_mock_data(symbol, start_date, end_date, interval)
        else:
            raise NotImplementedError(f"Provider {self.provider} not yet implemented")

    async def get_quote(self, symbol: str) -> MarketQuote:
        """Get real-time quote from configured provider"""

        if self.provider == DataProvider.YAHOO_FINANCE:
            return await self._fetch_yahoo_quote(symbol)
        elif self.provider == DataProvider.ALPHA_VANTAGE:
            return await self._fetch_alpha_vantage_quote(symbol)
        elif self.provider == DataProvider.POLYGON:
            return await self._fetch_polygon_quote(symbol)
        elif self.provider == DataProvider.FINNHUB:
            return await self._fetch_finnhub_quote(symbol)
        elif self.provider == DataProvider.MOCK:
            return self._generate_mock_quote(symbol)
        else:
            raise NotImplementedError(f"Provider {self.provider} not yet implemented")

    async def get_multiple_quotes(self, symbols: List[str]) -> Dict[str, MarketQuote]:
        """Get quotes for multiple symbols"""
        tasks = [self.get_quote(symbol) for symbol in symbols]
        results = await asyncio.gather(*tasks, return_exceptions=True)

        quotes = {}
        for symbol, result in zip(symbols, results):
            if isinstance(result, MarketQuote):
                quotes[symbol] = result
            else:
                logger.error(f"Error fetching quote for {symbol}: {result}")

        return quotes

    # ==================== YAHOO FINANCE ====================

    async def _fetch_yahoo_historical(
        self,
        symbol: str,
        start_date: datetime,
        end_date: datetime,
        interval: Interval
    ) -> List[MarketDataBar]:
        """Fetch historical data from Yahoo Finance"""
        if not YFINANCE_AVAILABLE:
            return self._generate_mock_data(symbol, start_date, end_date, interval)

        try:
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
            logger.error(f"Error fetching Yahoo Finance data: {e}", exc_info=True)
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
                previous_close=previous_close,
                provider="yahoo_finance"
            )

        except Exception as e:
            logger.error(f"Error fetching Yahoo Finance quote: {e}", exc_info=True)
            return self._generate_mock_quote(symbol)

    # ==================== ALPHA VANTAGE ====================

    async def _fetch_alpha_vantage_historical(
        self,
        symbol: str,
        start_date: datetime,
        end_date: datetime,
        interval: Interval
    ) -> List[MarketDataBar]:
        """Fetch historical data from Alpha Vantage"""
        if not self.ALPHA_VANTAGE_API_KEY or not self.http_client:
            logger.warning("Alpha Vantage API key not configured, falling back to Yahoo Finance")
            return await self._fetch_yahoo_historical(symbol, start_date, end_date, interval)

        try:
            # Map interval to Alpha Vantage function
            if interval in [Interval.MINUTE_1, Interval.MINUTE_5, Interval.MINUTE_15, Interval.MINUTE_30]:
                function = "TIME_SERIES_INTRADAY"
                av_interval = interval.value
                params = {
                    "function": function,
                    "symbol": symbol,
                    "interval": av_interval,
                    "apikey": self.ALPHA_VANTAGE_API_KEY,
                    "outputsize": "full"
                }
            else:
                function = "TIME_SERIES_DAILY_ADJUSTED"
                params = {
                    "function": function,
                    "symbol": symbol,
                    "apikey": self.ALPHA_VANTAGE_API_KEY,
                    "outputsize": "full"
                }

            response = await self.http_client.get(self.ALPHA_VANTAGE_BASE, params=params)
            data = response.json()

            # Find the time series key
            ts_key = None
            for key in data.keys():
                if "Time Series" in key:
                    ts_key = key
                    break

            if not ts_key or ts_key not in data:
                raise ValueError(f"No data returned for {symbol}: {data.get('Note', data.get('Error Message', 'Unknown error'))}")

            bars = []
            for date_str, values in data[ts_key].items():
                timestamp = datetime.fromisoformat(date_str.replace(" ", "T"))

                # Filter by date range
                if start_date <= timestamp <= end_date:
                    bars.append(MarketDataBar(
                        timestamp=timestamp,
                        open=float(values.get('1. open', 0)),
                        high=float(values.get('2. high', 0)),
                        low=float(values.get('3. low', 0)),
                        close=float(values.get('4. close', 0)),
                        volume=float(values.get('5. volume', values.get('6. volume', 0))),
                        adjusted_close=float(values.get('5. adjusted close', values.get('4. close', 0)))
                    ))

            # Sort by timestamp
            bars.sort(key=lambda x: x.timestamp)
            return bars

        except Exception as e:
            logger.error(f"Error fetching Alpha Vantage data: {e}", exc_info=True)
            return await self._fetch_yahoo_historical(symbol, start_date, end_date, interval)

    async def _fetch_alpha_vantage_quote(self, symbol: str) -> MarketQuote:
        """Fetch real-time quote from Alpha Vantage"""
        if not self.ALPHA_VANTAGE_API_KEY or not self.http_client:
            return await self._fetch_yahoo_quote(symbol)

        try:
            params = {
                "function": "GLOBAL_QUOTE",
                "symbol": symbol,
                "apikey": self.ALPHA_VANTAGE_API_KEY
            }

            response = await self.http_client.get(self.ALPHA_VANTAGE_BASE, params=params)
            data = response.json()

            if "Global Quote" not in data or not data["Global Quote"]:
                raise ValueError(f"No quote data for {symbol}")

            quote = data["Global Quote"]
            price = float(quote.get("05. price", 0))
            previous_close = float(quote.get("08. previous close", 0))
            change = float(quote.get("09. change", 0))
            change_percent = float(quote.get("10. change percent", "0%").replace("%", ""))

            return MarketQuote(
                symbol=symbol,
                price=price,
                volume=int(quote.get("06. volume", 0)),
                timestamp=datetime.utcnow(),
                change=change,
                change_percent=change_percent,
                previous_close=previous_close,
                provider="alpha_vantage"
            )

        except Exception as e:
            logger.error(f"Error fetching Alpha Vantage quote: {e}", exc_info=True)
            return await self._fetch_yahoo_quote(symbol)

    # ==================== POLYGON.IO ====================

    async def _fetch_polygon_historical(
        self,
        symbol: str,
        start_date: datetime,
        end_date: datetime,
        interval: Interval
    ) -> List[MarketDataBar]:
        """Fetch historical data from Polygon.io"""
        if not self.POLYGON_API_KEY or not self.http_client:
            logger.warning("Polygon API key not configured, falling back to Yahoo Finance")
            return await self._fetch_yahoo_historical(symbol, start_date, end_date, interval)

        try:
            # Map interval to Polygon timespan
            timespan_map = {
                Interval.MINUTE_1: ("minute", 1),
                Interval.MINUTE_5: ("minute", 5),
                Interval.MINUTE_15: ("minute", 15),
                Interval.MINUTE_30: ("minute", 30),
                Interval.HOUR_1: ("hour", 1),
                Interval.DAY_1: ("day", 1),
                Interval.WEEK_1: ("week", 1),
                Interval.MONTH_1: ("month", 1),
            }

            timespan, multiplier = timespan_map.get(interval, ("day", 1))

            url = f"{self.POLYGON_BASE}/v2/aggs/ticker/{symbol}/range/{multiplier}/{timespan}/{start_date.strftime('%Y-%m-%d')}/{end_date.strftime('%Y-%m-%d')}"

            params = {
                "apiKey": self.POLYGON_API_KEY,
                "adjusted": "true",
                "sort": "asc",
                "limit": 50000
            }

            response = await self.http_client.get(url, params=params)
            data = response.json()

            if data.get("status") != "OK" or "results" not in data:
                raise ValueError(f"No data returned for {symbol}: {data.get('error', 'Unknown error')}")

            bars = []
            for result in data["results"]:
                bars.append(MarketDataBar(
                    timestamp=datetime.fromtimestamp(result["t"] / 1000),
                    open=float(result["o"]),
                    high=float(result["h"]),
                    low=float(result["l"]),
                    close=float(result["c"]),
                    volume=float(result["v"]),
                    adjusted_close=float(result.get("vw", result["c"]))  # VWAP as adjusted
                ))

            return bars

        except Exception as e:
            logger.error(f"Error fetching Polygon data: {e}", exc_info=True)
            return await self._fetch_yahoo_historical(symbol, start_date, end_date, interval)

    async def _fetch_polygon_quote(self, symbol: str) -> MarketQuote:
        """Fetch real-time quote from Polygon.io"""
        if not self.POLYGON_API_KEY or not self.http_client:
            return await self._fetch_yahoo_quote(symbol)

        try:
            # Get previous day's data for quote
            url = f"{self.POLYGON_BASE}/v2/aggs/ticker/{symbol}/prev"
            params = {"apiKey": self.POLYGON_API_KEY, "adjusted": "true"}

            response = await self.http_client.get(url, params=params)
            data = response.json()

            if data.get("status") != "OK" or "results" not in data or not data["results"]:
                raise ValueError(f"No quote data for {symbol}")

            result = data["results"][0]

            # Get real-time snapshot for current price
            snapshot_url = f"{self.POLYGON_BASE}/v2/snapshot/locale/us/markets/stocks/tickers/{symbol}"
            snapshot_response = await self.http_client.get(snapshot_url, params={"apiKey": self.POLYGON_API_KEY})
            snapshot_data = snapshot_response.json()

            current_price = result["c"]  # Default to close
            if snapshot_data.get("status") == "OK" and "ticker" in snapshot_data:
                ticker = snapshot_data["ticker"]
                if "lastTrade" in ticker:
                    current_price = ticker["lastTrade"].get("p", current_price)

            previous_close = float(result.get("c", 0))
            change = current_price - previous_close
            change_percent = (change / previous_close * 100) if previous_close else 0

            return MarketQuote(
                symbol=symbol,
                price=current_price,
                volume=int(result.get("v", 0)),
                timestamp=datetime.utcnow(),
                change=change,
                change_percent=change_percent,
                previous_close=previous_close,
                provider="polygon"
            )

        except Exception as e:
            logger.error(f"Error fetching Polygon quote: {e}", exc_info=True)
            return await self._fetch_yahoo_quote(symbol)

    # ==================== FINNHUB ====================

    async def _fetch_finnhub_historical(
        self,
        symbol: str,
        start_date: datetime,
        end_date: datetime,
        interval: Interval
    ) -> List[MarketDataBar]:
        """Fetch historical data from Finnhub"""
        if not self.FINNHUB_API_KEY or not self.http_client:
            logger.warning("Finnhub API key not configured, falling back to Yahoo Finance")
            return await self._fetch_yahoo_historical(symbol, start_date, end_date, interval)

        try:
            # Map interval to Finnhub resolution
            resolution_map = {
                Interval.MINUTE_1: "1",
                Interval.MINUTE_5: "5",
                Interval.MINUTE_15: "15",
                Interval.MINUTE_30: "30",
                Interval.HOUR_1: "60",
                Interval.DAY_1: "D",
                Interval.WEEK_1: "W",
                Interval.MONTH_1: "M",
            }

            resolution = resolution_map.get(interval, "D")

            url = f"{self.FINNHUB_BASE}/stock/candle"
            params = {
                "symbol": symbol,
                "resolution": resolution,
                "from": int(start_date.timestamp()),
                "to": int(end_date.timestamp()),
                "token": self.FINNHUB_API_KEY
            }

            response = await self.http_client.get(url, params=params)
            data = response.json()

            if data.get("s") != "ok" or "t" not in data:
                raise ValueError(f"No data returned for {symbol}: {data.get('s', 'Unknown error')}")

            bars = []
            for i in range(len(data["t"])):
                bars.append(MarketDataBar(
                    timestamp=datetime.fromtimestamp(data["t"][i]),
                    open=float(data["o"][i]),
                    high=float(data["h"][i]),
                    low=float(data["l"][i]),
                    close=float(data["c"][i]),
                    volume=float(data["v"][i]),
                    adjusted_close=float(data["c"][i])
                ))

            return bars

        except Exception as e:
            logger.error(f"Error fetching Finnhub data: {e}", exc_info=True)
            return await self._fetch_yahoo_historical(symbol, start_date, end_date, interval)

    async def _fetch_finnhub_quote(self, symbol: str) -> MarketQuote:
        """Fetch real-time quote from Finnhub"""
        if not self.FINNHUB_API_KEY or not self.http_client:
            return await self._fetch_yahoo_quote(symbol)

        try:
            url = f"{self.FINNHUB_BASE}/quote"
            params = {"symbol": symbol, "token": self.FINNHUB_API_KEY}

            response = await self.http_client.get(url, params=params)
            data = response.json()

            if not data or data.get("c", 0) == 0:
                raise ValueError(f"No quote data for {symbol}")

            current_price = float(data["c"])
            previous_close = float(data["pc"])
            change = float(data["d"]) if data.get("d") else current_price - previous_close
            change_percent = float(data["dp"]) if data.get("dp") else (change / previous_close * 100 if previous_close else 0)

            return MarketQuote(
                symbol=symbol,
                price=current_price,
                bid=None,
                ask=None,
                volume=0,  # Finnhub quote doesn't include volume
                timestamp=datetime.utcnow(),
                change=change,
                change_percent=change_percent,
                previous_close=previous_close,
                provider="finnhub"
            )

        except Exception as e:
            logger.error(f"Error fetching Finnhub quote: {e}", exc_info=True)
            return await self._fetch_yahoo_quote(symbol)

    # ==================== MOCK DATA ====================

    def _generate_mock_data(
        self,
        symbol: str,
        start_date: datetime,
        end_date: datetime,
        interval: Interval
    ) -> List[MarketDataBar]:
        """Generate mock price data for testing"""
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

        np.random.seed(hash(symbol) % 2**32)
        base_price = 100 + (hash(symbol) % 400)
        returns = np.random.normal(0.0005, 0.02, num_bars)
        prices = base_price * np.exp(np.cumsum(returns))

        bars = []
        current_time = start_date

        for i, close_price in enumerate(prices):
            high = close_price * (1 + np.random.uniform(0, 0.02))
            low = close_price * (1 - np.random.uniform(0, 0.02))
            open_price = low + np.random.uniform(0, 1) * (high - low)
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
            previous_close=float(previous_close),
            provider="mock"
        )

    # ==================== UTILITY METHODS ====================

    async def get_company_info(self, symbol: str) -> Dict:
        """Get company information (Yahoo Finance only for now)"""
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
            logger.error(f"Error fetching company info: {e}", exc_info=True)
            return {"symbol": symbol, "error": str(e)}

    def to_dataframe(self, bars: List[MarketDataBar]) -> pd.DataFrame:
        """Convert bars to pandas DataFrame"""
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


# Global instance cache
_providers: Dict[DataProvider, MarketDataProvider] = {}


def get_market_data_provider(provider: DataProvider = DataProvider.YAHOO_FINANCE) -> MarketDataProvider:
    """Get or create market data provider instance"""
    global _providers
    if provider not in _providers:
        _providers[provider] = MarketDataProvider(provider)
    return _providers[provider]


def get_available_providers() -> List[str]:
    """Get list of available providers based on configured API keys"""
    available = ["yahoo_finance", "mock"]  # Always available

    if os.getenv("ALPHA_VANTAGE_API_KEY"):
        available.append("alpha_vantage")
    if os.getenv("POLYGON_API_KEY"):
        available.append("polygon")
    if os.getenv("FINNHUB_API_KEY"):
        available.append("finnhub")
    if os.getenv("IEX_API_KEY"):
        available.append("iex_cloud")

    return available
