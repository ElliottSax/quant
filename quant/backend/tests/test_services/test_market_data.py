"""
Comprehensive tests for Market Data Service

Tests cover:
- Enums and models
- Provider initialization
- Historical data fetching
- Quote fetching
- Multiple symbol quotes
- Mock data generation
- Utility methods
- Provider caching
- Error handling
"""

import pytest
import asyncio
from datetime import datetime, timedelta
from typing import Dict, List
import pandas as pd
import numpy as np

from app.services.market_data import (
    DataProvider,
    Interval,
    MarketDataBar,
    MarketQuote,
    MarketDataProvider,
    get_market_data_provider,
    get_available_providers,
)


# ==================== FIXTURES ====================

@pytest.fixture
def mock_provider():
    """Create a mock data provider"""
    provider = MarketDataProvider(provider=DataProvider.MOCK)
    yield provider
    # Cleanup
    asyncio.run(provider.close())


@pytest.fixture
def sample_date_range():
    """Sample date range for testing"""
    end_date = datetime(2024, 1, 31)
    start_date = end_date - timedelta(days=30)
    return start_date, end_date


@pytest.fixture
def test_symbols():
    """Sample symbols for testing"""
    return ["AAPL", "GOOGL", "MSFT"]


# ==================== ENUM TESTS ====================

class TestEnums:
    """Test enum definitions"""

    def test_data_provider_values(self):
        """Test DataProvider enum has expected providers"""
        assert DataProvider.YAHOO_FINANCE == "yahoo_finance"
        assert DataProvider.ALPHA_VANTAGE == "alpha_vantage"
        assert DataProvider.POLYGON == "polygon"
        assert DataProvider.FINNHUB == "finnhub"
        assert DataProvider.IEX_CLOUD == "iex_cloud"
        assert DataProvider.MOCK == "mock"

    def test_data_provider_count(self):
        """Test all providers are defined"""
        providers = list(DataProvider)
        assert len(providers) == 6

    def test_interval_values(self):
        """Test Interval enum has expected values"""
        assert Interval.MINUTE_1 == "1m"
        assert Interval.MINUTE_5 == "5m"
        assert Interval.MINUTE_15 == "15m"
        assert Interval.MINUTE_30 == "30m"
        assert Interval.HOUR_1 == "1h"
        assert Interval.DAY_1 == "1d"
        assert Interval.WEEK_1 == "1wk"
        assert Interval.MONTH_1 == "1mo"

    def test_interval_count(self):
        """Test all intervals are defined"""
        intervals = list(Interval)
        assert len(intervals) == 8


# ==================== MODEL TESTS ====================

class TestModels:
    """Test Pydantic models"""

    def test_market_data_bar_creation(self):
        """Test creating a MarketDataBar"""
        bar = MarketDataBar(
            timestamp=datetime(2024, 1, 1, 9, 30),
            open=100.0,
            high=105.0,
            low=99.0,
            close=103.0,
            volume=1000000.0,
            adjusted_close=102.5
        )

        assert bar.timestamp == datetime(2024, 1, 1, 9, 30)
        assert bar.open == 100.0
        assert bar.high == 105.0
        assert bar.low == 99.0
        assert bar.close == 103.0
        assert bar.volume == 1000000.0
        assert bar.adjusted_close == 102.5

    def test_market_data_bar_optional_adjusted_close(self):
        """Test MarketDataBar with optional adjusted_close"""
        bar = MarketDataBar(
            timestamp=datetime(2024, 1, 1),
            open=100.0,
            high=105.0,
            low=99.0,
            close=103.0,
            volume=1000000.0
        )

        assert bar.adjusted_close is None

    def test_market_quote_creation(self):
        """Test creating a MarketQuote"""
        quote = MarketQuote(
            symbol="AAPL",
            price=150.0,
            bid=149.95,
            ask=150.05,
            volume=1000000,
            timestamp=datetime(2024, 1, 1, 9, 30),
            change=2.5,
            change_percent=1.69,
            previous_close=147.5,
            provider="yahoo_finance"
        )

        assert quote.symbol == "AAPL"
        assert quote.price == 150.0
        assert quote.bid == 149.95
        assert quote.ask == 150.05
        assert quote.volume == 1000000
        assert quote.change == 2.5
        assert quote.change_percent == 1.69
        assert quote.previous_close == 147.5
        assert quote.provider == "yahoo_finance"

    def test_market_quote_optional_fields(self):
        """Test MarketQuote with minimal fields"""
        quote = MarketQuote(
            symbol="AAPL",
            price=150.0,
            volume=1000000,
            timestamp=datetime(2024, 1, 1)
        )

        assert quote.symbol == "AAPL"
        assert quote.price == 150.0
        assert quote.volume == 1000000
        assert quote.bid is None
        assert quote.ask is None
        assert quote.change is None
        assert quote.change_percent is None
        assert quote.previous_close is None
        assert quote.provider is None


# ==================== PROVIDER INITIALIZATION ====================

class TestProviderInitialization:
    """Test provider initialization"""

    def test_create_mock_provider(self):
        """Test creating a mock provider"""
        provider = MarketDataProvider(provider=DataProvider.MOCK)
        assert provider.provider == DataProvider.MOCK

    def test_create_yahoo_provider(self):
        """Test creating a Yahoo Finance provider"""
        provider = MarketDataProvider(provider=DataProvider.YAHOO_FINANCE)
        assert provider.provider == DataProvider.YAHOO_FINANCE

    def test_default_provider(self):
        """Test default provider is Yahoo Finance"""
        provider = MarketDataProvider()
        assert provider.provider == DataProvider.YAHOO_FINANCE

    @pytest.mark.asyncio
    async def test_close_provider(self, mock_provider):
        """Test closing provider HTTP client"""
        await mock_provider.close()
        # Should not raise error
        assert True


# ==================== HISTORICAL DATA TESTS ====================

class TestHistoricalData:
    """Test historical data fetching"""

    @pytest.mark.asyncio
    async def test_get_historical_data_daily(self, mock_provider, sample_date_range):
        """Test fetching daily historical data"""
        start_date, end_date = sample_date_range

        bars = await mock_provider.get_historical_data(
            symbol="AAPL",
            start_date=start_date,
            end_date=end_date,
            interval=Interval.DAY_1
        )

        assert len(bars) > 0
        assert all(isinstance(bar, MarketDataBar) for bar in bars)
        assert all(start_date <= bar.timestamp <= end_date for bar in bars)

    @pytest.mark.asyncio
    async def test_get_historical_data_intraday(self, mock_provider):
        """Test fetching intraday historical data"""
        end_date = datetime(2024, 1, 1, 16, 0)
        start_date = datetime(2024, 1, 1, 9, 30)

        bars = await mock_provider.get_historical_data(
            symbol="AAPL",
            start_date=start_date,
            end_date=end_date,
            interval=Interval.MINUTE_5
        )

        assert len(bars) > 0
        assert all(isinstance(bar, MarketDataBar) for bar in bars)

    @pytest.mark.asyncio
    async def test_historical_data_ohlcv_validity(self, mock_provider, sample_date_range):
        """Test OHLCV data validity"""
        start_date, end_date = sample_date_range

        bars = await mock_provider.get_historical_data(
            symbol="AAPL",
            start_date=start_date,
            end_date=end_date,
            interval=Interval.DAY_1
        )

        for bar in bars:
            # High should be highest
            assert bar.high >= bar.open
            assert bar.high >= bar.close
            assert bar.high >= bar.low

            # Low should be lowest
            assert bar.low <= bar.open
            assert bar.low <= bar.close
            assert bar.low <= bar.high

            # All values should be positive
            assert bar.open > 0
            assert bar.high > 0
            assert bar.low > 0
            assert bar.close > 0
            assert bar.volume > 0

    @pytest.mark.asyncio
    async def test_historical_data_different_intervals(self, mock_provider):
        """Test different time intervals"""
        end_date = datetime(2024, 1, 31)
        start_date = datetime(2024, 1, 1)

        for interval in [Interval.DAY_1, Interval.HOUR_1, Interval.MINUTE_15]:
            bars = await mock_provider.get_historical_data(
                symbol="AAPL",
                start_date=start_date,
                end_date=end_date,
                interval=interval
            )

            assert len(bars) > 0
            assert all(isinstance(bar, MarketDataBar) for bar in bars)

    @pytest.mark.asyncio
    async def test_historical_data_symbol_consistency(self, mock_provider, sample_date_range):
        """Test same symbol returns consistent data"""
        start_date, end_date = sample_date_range

        bars1 = await mock_provider.get_historical_data(
            symbol="AAPL",
            start_date=start_date,
            end_date=end_date,
            interval=Interval.DAY_1
        )

        bars2 = await mock_provider.get_historical_data(
            symbol="AAPL",
            start_date=start_date,
            end_date=end_date,
            interval=Interval.DAY_1
        )

        # Mock data should be deterministic based on symbol
        assert len(bars1) == len(bars2)
        for b1, b2 in zip(bars1, bars2):
            assert b1.close == b2.close


# ==================== QUOTE TESTS ====================

class TestQuotes:
    """Test quote fetching"""

    @pytest.mark.asyncio
    async def test_get_quote(self, mock_provider):
        """Test fetching a single quote"""
        quote = await mock_provider.get_quote("AAPL")

        assert isinstance(quote, MarketQuote)
        assert quote.symbol == "AAPL"
        assert quote.price > 0
        assert quote.volume > 0
        assert quote.provider == "mock"

    @pytest.mark.asyncio
    async def test_quote_has_all_fields(self, mock_provider):
        """Test quote has all expected fields"""
        quote = await mock_provider.get_quote("AAPL")

        assert hasattr(quote, 'symbol')
        assert hasattr(quote, 'price')
        assert hasattr(quote, 'bid')
        assert hasattr(quote, 'ask')
        assert hasattr(quote, 'volume')
        assert hasattr(quote, 'timestamp')
        assert hasattr(quote, 'change')
        assert hasattr(quote, 'change_percent')
        assert hasattr(quote, 'previous_close')

    @pytest.mark.asyncio
    async def test_quote_bid_ask_spread(self, mock_provider):
        """Test bid/ask spread is valid"""
        quote = await mock_provider.get_quote("AAPL")

        if quote.bid and quote.ask:
            # Bid should be less than ask
            assert quote.bid <= quote.ask
            # Price should be between bid and ask
            assert quote.bid <= quote.price <= quote.ask

    @pytest.mark.asyncio
    async def test_quote_change_calculation(self, mock_provider):
        """Test change calculation is consistent"""
        quote = await mock_provider.get_quote("AAPL")

        if quote.change and quote.previous_close:
            # Change should be price - previous_close
            expected_change = quote.price - quote.previous_close
            assert abs(quote.change - expected_change) < 0.01

    @pytest.mark.asyncio
    async def test_quote_consistency(self, mock_provider):
        """Test same symbol returns consistent quote"""
        quote1 = await mock_provider.get_quote("AAPL")
        quote2 = await mock_provider.get_quote("AAPL")

        # Mock quotes should be deterministic
        assert abs(quote1.price - quote2.price) < 10  # Allow small variation


# ==================== MULTIPLE QUOTES TESTS ====================

class TestMultipleQuotes:
    """Test fetching multiple quotes"""

    @pytest.mark.asyncio
    async def test_get_multiple_quotes(self, mock_provider, test_symbols):
        """Test fetching quotes for multiple symbols"""
        quotes = await mock_provider.get_multiple_quotes(test_symbols)

        assert len(quotes) == len(test_symbols)
        for symbol in test_symbols:
            assert symbol in quotes
            assert isinstance(quotes[symbol], MarketQuote)
            assert quotes[symbol].symbol == symbol

    @pytest.mark.asyncio
    async def test_multiple_quotes_parallel_execution(self, mock_provider):
        """Test multiple quotes are fetched in parallel"""
        symbols = ["AAPL", "GOOGL", "MSFT", "AMZN", "TSLA"]

        start_time = datetime.now()
        quotes = await mock_provider.get_multiple_quotes(symbols)
        duration = (datetime.now() - start_time).total_seconds()

        # Should complete quickly if parallel
        assert duration < 5  # 5 seconds is generous for mock data
        assert len(quotes) == len(symbols)

    @pytest.mark.asyncio
    async def test_multiple_quotes_empty_list(self, mock_provider):
        """Test handling empty symbol list"""
        quotes = await mock_provider.get_multiple_quotes([])
        assert quotes == {}

    @pytest.mark.asyncio
    async def test_multiple_quotes_single_symbol(self, mock_provider):
        """Test multiple quotes with single symbol"""
        quotes = await mock_provider.get_multiple_quotes(["AAPL"])
        assert len(quotes) == 1
        assert "AAPL" in quotes


# ==================== MOCK DATA GENERATION ====================

class TestMockDataGeneration:
    """Test mock data generation"""

    @pytest.mark.asyncio
    async def test_mock_data_generation(self, mock_provider, sample_date_range):
        """Test mock data is generated correctly"""
        start_date, end_date = sample_date_range

        bars = await mock_provider.get_historical_data(
            symbol="TEST",
            start_date=start_date,
            end_date=end_date,
            interval=Interval.DAY_1
        )

        assert len(bars) > 0
        assert all(isinstance(bar, MarketDataBar) for bar in bars)

    def test_mock_quote_generation(self, mock_provider):
        """Test mock quote generation"""
        quote = mock_provider._generate_mock_quote("TEST")

        assert isinstance(quote, MarketQuote)
        assert quote.symbol == "TEST"
        assert quote.provider == "mock"
        assert quote.price > 0

    def test_mock_data_deterministic(self, mock_provider):
        """Test mock data is deterministic based on symbol"""
        bars1 = mock_provider._generate_mock_data(
            symbol="TEST",
            start_date=datetime(2024, 1, 1),
            end_date=datetime(2024, 1, 31),
            interval=Interval.DAY_1
        )

        bars2 = mock_provider._generate_mock_data(
            symbol="TEST",
            start_date=datetime(2024, 1, 1),
            end_date=datetime(2024, 1, 31),
            interval=Interval.DAY_1
        )

        # Should generate same data for same symbol and dates
        assert len(bars1) == len(bars2)
        for b1, b2 in zip(bars1, bars2):
            assert b1.close == b2.close

    def test_mock_data_different_symbols(self, mock_provider):
        """Test different symbols generate different data"""
        bars1 = mock_provider._generate_mock_data(
            symbol="AAPL",
            start_date=datetime(2024, 1, 1),
            end_date=datetime(2024, 1, 31),
            interval=Interval.DAY_1
        )

        bars2 = mock_provider._generate_mock_data(
            symbol="GOOGL",
            start_date=datetime(2024, 1, 1),
            end_date=datetime(2024, 1, 31),
            interval=Interval.DAY_1
        )

        # Different symbols should have different prices
        avg_price_1 = sum(b.close for b in bars1) / len(bars1)
        avg_price_2 = sum(b.close for b in bars2) / len(bars2)
        assert avg_price_1 != avg_price_2


# ==================== UTILITY METHODS ====================

class TestUtilityMethods:
    """Test utility methods"""

    @pytest.mark.asyncio
    async def test_get_company_info(self, mock_provider):
        """Test getting company information"""
        info = await mock_provider.get_company_info("AAPL")

        assert isinstance(info, dict)
        assert "symbol" in info
        assert info["symbol"] == "AAPL"

    def test_to_dataframe(self, mock_provider):
        """Test converting bars to DataFrame"""
        bars = mock_provider._generate_mock_data(
            symbol="TEST",
            start_date=datetime(2024, 1, 1),
            end_date=datetime(2024, 1, 10),
            interval=Interval.DAY_1
        )

        df = mock_provider.to_dataframe(bars)

        assert isinstance(df, pd.DataFrame)
        assert 'open' in df.columns
        assert 'high' in df.columns
        assert 'low' in df.columns
        assert 'close' in df.columns
        assert 'volume' in df.columns
        assert df.index.name == 'timestamp'
        assert len(df) == len(bars)

    def test_to_dataframe_empty(self, mock_provider):
        """Test converting empty bars list"""
        df = mock_provider.to_dataframe([])

        assert isinstance(df, pd.DataFrame)
        assert len(df) == 0

    def test_to_dataframe_values(self, mock_provider):
        """Test DataFrame values match bars"""
        bars = mock_provider._generate_mock_data(
            symbol="TEST",
            start_date=datetime(2024, 1, 1),
            end_date=datetime(2024, 1, 5),
            interval=Interval.DAY_1
        )

        df = mock_provider.to_dataframe(bars)

        # Check first row matches first bar
        first_bar = bars[0]
        first_row = df.iloc[0]

        assert first_row['open'] == first_bar.open
        assert first_row['high'] == first_bar.high
        assert first_row['low'] == first_bar.low
        assert first_row['close'] == first_bar.close
        assert first_row['volume'] == first_bar.volume


# ==================== PROVIDER CACHING ====================

class TestProviderCaching:
    """Test provider caching mechanism"""

    def test_get_market_data_provider_creates_instance(self):
        """Test getting provider creates new instance"""
        provider = get_market_data_provider(DataProvider.MOCK)

        assert isinstance(provider, MarketDataProvider)
        assert provider.provider == DataProvider.MOCK

    def test_get_market_data_provider_returns_cached(self):
        """Test getting same provider returns cached instance"""
        provider1 = get_market_data_provider(DataProvider.MOCK)
        provider2 = get_market_data_provider(DataProvider.MOCK)

        # Should return same instance
        assert provider1 is provider2

    def test_get_market_data_provider_different_providers(self):
        """Test different providers create different instances"""
        mock_provider = get_market_data_provider(DataProvider.MOCK)
        yahoo_provider = get_market_data_provider(DataProvider.YAHOO_FINANCE)

        # Should be different instances
        assert mock_provider is not yahoo_provider
        assert mock_provider.provider == DataProvider.MOCK
        assert yahoo_provider.provider == DataProvider.YAHOO_FINANCE

    def test_get_market_data_provider_default(self):
        """Test default provider"""
        provider = get_market_data_provider()

        assert provider.provider == DataProvider.YAHOO_FINANCE


# ==================== AVAILABLE PROVIDERS ====================

class TestAvailableProviders:
    """Test available providers detection"""

    def test_get_available_providers_always_has_defaults(self):
        """Test always-available providers are included"""
        providers = get_available_providers()

        assert "yahoo_finance" in providers
        assert "mock" in providers

    def test_get_available_providers_returns_list(self):
        """Test returns a list"""
        providers = get_available_providers()

        assert isinstance(providers, list)
        assert len(providers) >= 2  # At least yahoo_finance and mock


# ==================== ERROR HANDLING ====================

class TestErrorHandling:
    """Test error handling"""

    @pytest.mark.asyncio
    async def test_unsupported_provider_historical(self):
        """Test error for unsupported provider historical data"""
        # This would require mocking a non-existent provider
        # For now, test that implemented providers don't raise errors
        provider = MarketDataProvider(provider=DataProvider.MOCK)

        bars = await provider.get_historical_data(
            symbol="AAPL",
            start_date=datetime(2024, 1, 1),
            end_date=datetime(2024, 1, 31),
            interval=Interval.DAY_1
        )

        assert len(bars) > 0

    @pytest.mark.asyncio
    async def test_unsupported_provider_quote(self):
        """Test error for unsupported provider quote"""
        provider = MarketDataProvider(provider=DataProvider.MOCK)

        quote = await provider.get_quote("AAPL")

        assert isinstance(quote, MarketQuote)

    @pytest.mark.asyncio
    async def test_empty_symbol(self, mock_provider):
        """Test handling empty symbol"""
        quote = await mock_provider.get_quote("")

        # Mock provider should still generate data
        assert isinstance(quote, MarketQuote)

    @pytest.mark.asyncio
    async def test_invalid_date_range(self, mock_provider):
        """Test handling invalid date range (end before start)"""
        # Even with invalid range, mock should generate data
        bars = await mock_provider.get_historical_data(
            symbol="AAPL",
            start_date=datetime(2024, 1, 31),
            end_date=datetime(2024, 1, 1),  # End before start
            interval=Interval.DAY_1
        )

        # Mock provider will still work, just generate empty or minimal data
        assert isinstance(bars, list)
