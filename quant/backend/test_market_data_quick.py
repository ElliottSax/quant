#!/usr/bin/env python3
"""Quick test of market data service without pytest infrastructure."""

import os
import sys
import asyncio
from datetime import datetime, timedelta

# Set environment before any imports
os.environ["ENVIRONMENT"] = "test"

# Add current directory to path
sys.path.insert(0, os.path.dirname(__file__))

from app.services.market_data import (
    DataProvider,
    Interval,
    MarketDataBar,
    MarketQuote,
    MarketDataProvider,
    get_market_data_provider,
    get_available_providers,
)


def test_enums():
    """Test enum definitions."""
    assert DataProvider.YAHOO_FINANCE == "yahoo_finance"
    assert DataProvider.MOCK == "mock"
    assert Interval.DAY_1 == "1d"
    assert Interval.MINUTE_1 == "1m"
    print("✓ Enums test passed")


def test_models():
    """Test Pydantic models."""
    bar = MarketDataBar(
        timestamp=datetime(2024, 1, 1),
        open=100.0,
        high=105.0,
        low=99.0,
        close=103.0,
        volume=1000000.0
    )
    assert bar.open == 100.0
    assert bar.close == 103.0

    quote = MarketQuote(
        symbol="AAPL",
        price=150.0,
        volume=1000000,
        timestamp=datetime(2024, 1, 1)
    )
    assert quote.symbol == "AAPL"
    assert quote.price == 150.0
    print("✓ Models test passed")


def test_provider_creation():
    """Test provider creation."""
    provider = MarketDataProvider(provider=DataProvider.MOCK)
    assert provider.provider == DataProvider.MOCK
    print("✓ Provider creation test passed")


async def test_historical_data():
    """Test fetching historical data."""
    provider = MarketDataProvider(provider=DataProvider.MOCK)

    end_date = datetime(2024, 1, 31)
    start_date = datetime(2024, 1, 1)

    bars = await provider.get_historical_data(
        symbol="AAPL",
        start_date=start_date,
        end_date=end_date,
        interval=Interval.DAY_1
    )

    assert len(bars) > 0
    assert isinstance(bars[0], MarketDataBar)
    assert bars[0].high >= bars[0].low
    assert bars[0].volume > 0

    await provider.close()
    print("✓ Historical data test passed")


async def test_quote():
    """Test fetching quotes."""
    provider = MarketDataProvider(provider=DataProvider.MOCK)

    quote = await provider.get_quote("AAPL")

    assert isinstance(quote, MarketQuote)
    assert quote.symbol == "AAPL"
    assert quote.price > 0
    assert quote.provider == "mock"

    await provider.close()
    print("✓ Quote test passed")


async def test_multiple_quotes():
    """Test fetching multiple quotes."""
    provider = MarketDataProvider(provider=DataProvider.MOCK)

    symbols = ["AAPL", "GOOGL", "MSFT"]
    quotes = await provider.get_multiple_quotes(symbols)

    assert len(quotes) == 3
    for symbol in symbols:
        assert symbol in quotes
        assert quotes[symbol].price > 0

    await provider.close()
    print("✓ Multiple quotes test passed")


def test_to_dataframe():
    """Test converting to DataFrame."""
    provider = MarketDataProvider(provider=DataProvider.MOCK)

    bars = provider._generate_mock_data(
        symbol="TEST",
        start_date=datetime(2024, 1, 1),
        end_date=datetime(2024, 1, 10),
        interval=Interval.DAY_1
    )

    df = provider.to_dataframe(bars)

    assert 'open' in df.columns
    assert 'close' in df.columns
    assert df.index.name == 'timestamp'
    assert len(df) == len(bars)
    print("✓ DataFrame conversion test passed")


def test_provider_caching():
    """Test provider caching."""
    provider1 = get_market_data_provider(DataProvider.MOCK)
    provider2 = get_market_data_provider(DataProvider.MOCK)

    # Should return same cached instance
    assert provider1 is provider2
    print("✓ Provider caching test passed")


def test_available_providers():
    """Test available providers detection."""
    providers = get_available_providers()

    assert "yahoo_finance" in providers
    assert "mock" in providers
    assert isinstance(providers, list)
    print("✓ Available providers test passed")


async def test_ohlcv_validity():
    """Test OHLCV data validity."""
    provider = MarketDataProvider(provider=DataProvider.MOCK)

    bars = await provider.get_historical_data(
        symbol="AAPL",
        start_date=datetime(2024, 1, 1),
        end_date=datetime(2024, 1, 10),
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

        # All should be positive
        assert bar.open > 0
        assert bar.high > 0
        assert bar.low > 0
        assert bar.close > 0
        assert bar.volume > 0

    await provider.close()
    print("✓ OHLCV validity test passed")


if __name__ == "__main__":
    print("Running quick market data tests...")
    print()

    # Run sync tests
    test_enums()
    test_models()
    test_provider_creation()
    test_to_dataframe()
    test_provider_caching()
    test_available_providers()

    # Run async tests
    asyncio.run(test_historical_data())
    asyncio.run(test_quote())
    asyncio.run(test_multiple_quotes())
    asyncio.run(test_ohlcv_validity())

    print()
    print("=" * 50)
    print("ALL TESTS PASSED! ✓")
    print("=" * 50)
