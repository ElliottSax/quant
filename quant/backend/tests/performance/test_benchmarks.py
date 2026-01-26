"""
Performance Benchmark Tests for Quant Trading Platform

These tests measure the performance of critical operations and endpoints
to establish baselines and catch performance regressions.

Usage:
    # Run all benchmarks
    pytest tests/performance/test_benchmarks.py -v

    # Run with benchmark plugin for detailed stats
    pip install pytest-benchmark
    pytest tests/performance/test_benchmarks.py --benchmark-only

    # Save benchmark results
    pytest tests/performance/test_benchmarks.py --benchmark-save=baseline

    # Compare against baseline
    pytest tests/performance/test_benchmarks.py --benchmark-compare=baseline
"""

import pytest
import time
import asyncio
from datetime import datetime, timedelta, date
from decimal import Decimal
from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import AsyncSession
from unittest.mock import patch, MagicMock, AsyncMock

from app.models.politician import Politician
from app.models.trade import Trade
from app.models.user import User


# ============================================================================
# API Endpoint Benchmarks
# ============================================================================

class TestAPIEndpointBenchmarks:
    """Benchmark tests for API endpoints"""

    def test_stats_overview_performance(self, client: TestClient, benchmark):
        """Benchmark stats overview endpoint"""
        if benchmark:
            result = benchmark(lambda: client.get("/api/v1/stats/overview"))
            assert result.status_code == 200
        else:
            # Fallback if pytest-benchmark not installed
            start = time.time()
            response = client.get("/api/v1/stats/overview")
            duration = time.time() - start

            assert response.status_code == 200
            assert duration < 1.0, f"Stats overview took {duration:.3f}s (target: <1s)"

    def test_leaderboard_performance(self, client: TestClient, benchmark):
        """Benchmark leaderboard endpoint"""
        if benchmark:
            result = benchmark(lambda: client.get("/api/v1/stats/leaderboard?limit=50"))
            assert result.status_code == 200
        else:
            start = time.time()
            response = client.get("/api/v1/stats/leaderboard?limit=50")
            duration = time.time() - start

            assert response.status_code == 200
            assert duration < 2.0, f"Leaderboard took {duration:.3f}s (target: <2s)"

    def test_ticker_stats_performance(self, client: TestClient, benchmark):
        """Benchmark ticker statistics endpoint"""
        if benchmark:
            result = benchmark(lambda: client.get("/api/v1/stats/tickers?limit=50"))
            assert result.status_code == 200
        else:
            start = time.time()
            response = client.get("/api/v1/stats/tickers?limit=50")
            duration = time.time() - start

            assert response.status_code == 200
            assert duration < 2.0, f"Ticker stats took {duration:.3f}s (target: <2s)"

    def test_market_quote_performance(self, client: TestClient, benchmark):
        """Benchmark market quote endpoint"""
        with patch('app.api.v1.market_data.get_market_data_provider') as mock_provider:
            mock_data_provider = MagicMock()
            mock_quote = MagicMock(symbol='AAPL', price=150.0)
            mock_data_provider.get_quote = AsyncMock(return_value=mock_quote)
            mock_provider.return_value = mock_data_provider

            if benchmark:
                result = benchmark(lambda: client.get("/api/v1/market-data/public/quote/AAPL"))
                assert result.status_code == 200
            else:
                start = time.time()
                response = client.get("/api/v1/market-data/public/quote/AAPL")
                duration = time.time() - start

                assert response.status_code == 200
                assert duration < 0.5, f"Quote fetch took {duration:.3f}s (target: <0.5s)"

    def test_multiple_quotes_performance(self, client: TestClient, benchmark):
        """Benchmark multiple quotes endpoint"""
        with patch('app.api.v1.market_data.get_market_data_provider') as mock_provider:
            mock_data_provider = MagicMock()
            mock_data_provider.get_multiple_quotes = AsyncMock(return_value={})
            mock_provider.return_value = mock_data_provider

            query = "symbols=AAPL&symbols=GOOGL&symbols=MSFT&symbols=TSLA&symbols=AMZN"

            if benchmark:
                result = benchmark(lambda: client.get(f"/api/v1/market-data/public/quotes?{query}"))
                assert result.status_code == 200
            else:
                start = time.time()
                response = client.get(f"/api/v1/market-data/public/quotes?{query}")
                duration = time.time() - start

                assert response.status_code == 200
                assert duration < 1.0, f"Multiple quotes took {duration:.3f}s (target: <1s)"


# ============================================================================
# Database Query Benchmarks
# ============================================================================

class TestDatabaseBenchmarks:
    """Benchmark tests for database operations"""

    @pytest.mark.asyncio
    async def test_politician_query_performance(
        self, db_session: AsyncSession, test_politician: Politician, benchmark
    ):
        """Benchmark politician query"""
        from sqlalchemy import select

        async def query_politician():
            result = await db_session.execute(
                select(Politician).where(Politician.id == test_politician.id)
            )
            return result.scalar_one_or_none()

        if benchmark:
            result = benchmark(lambda: asyncio.run(query_politician()))
            assert result is not None
        else:
            start = time.time()
            politician = await query_politician()
            duration = time.time() - start

            assert politician is not None
            assert duration < 0.1, f"Politician query took {duration:.3f}s (target: <0.1s)"

    @pytest.mark.asyncio
    async def test_trade_query_performance(
        self, db_session: AsyncSession, test_politician: Politician, benchmark
    ):
        """Benchmark trade query"""
        from sqlalchemy import select

        # Create some test trades
        trades = []
        for i in range(10):
            trade = Trade(
                politician_id=test_politician.id,
                ticker=f"TST{i}",
                transaction_type="buy",
                amount_min=Decimal("1000.00"),
                amount_max=Decimal("15000.00"),
                transaction_date=date.today() - timedelta(days=i),
                disclosure_date=date.today(),
                source_url=f"https://example.com/{i}"
            )
            trades.append(trade)
            db_session.add(trade)

        await db_session.commit()

        async def query_trades():
            result = await db_session.execute(
                select(Trade)
                .where(Trade.politician_id == test_politician.id)
                .order_by(Trade.transaction_date.desc())
                .limit(10)
            )
            return result.scalars().all()

        if benchmark:
            result = benchmark(lambda: asyncio.run(query_trades()))
            assert len(result) > 0
        else:
            start = time.time()
            trades = await query_trades()
            duration = time.time() - start

            assert len(trades) > 0
            assert duration < 0.2, f"Trade query took {duration:.3f}s (target: <0.2s)"

    @pytest.mark.asyncio
    async def test_bulk_insert_performance(
        self, db_session: AsyncSession, test_politician: Politician, benchmark
    ):
        """Benchmark bulk trade insertion"""

        async def bulk_insert():
            trades = []
            for i in range(100):
                trade = Trade(
                    politician_id=test_politician.id,
                    ticker=f"BULK{i}",
                    transaction_type="buy" if i % 2 == 0 else "sell",
                    amount_min=Decimal("1000.00"),
                    amount_max=Decimal("15000.00"),
                    transaction_date=date.today() - timedelta(days=i),
                    disclosure_date=date.today(),
                    source_url=f"https://example.com/bulk/{i}"
                )
                trades.append(trade)

            db_session.add_all(trades)
            await db_session.commit()
            return len(trades)

        if benchmark:
            count = benchmark(lambda: asyncio.run(bulk_insert()))
            assert count == 100
        else:
            start = time.time()
            count = await bulk_insert()
            duration = time.time() - start

            assert count == 100
            assert duration < 1.0, f"Bulk insert took {duration:.3f}s (target: <1s)"


# ============================================================================
# Cache Performance Benchmarks
# ============================================================================

class TestCacheBenchmarks:
    """Benchmark tests for caching functionality"""

    def test_cache_hit_performance(self, benchmark):
        """Benchmark cache hit performance"""
        from app.core.cache import CacheManager

        cache = CacheManager()
        cache.set("test_key", {"data": "test_value"}, ttl=60)

        if benchmark:
            result = benchmark(lambda: cache.get("test_key"))
            assert result is not None
        else:
            start = time.time()
            value = cache.get("test_key")
            duration = time.time() - start

            assert value is not None
            assert duration < 0.01, f"Cache hit took {duration:.3f}s (target: <0.01s)"

    def test_cache_miss_performance(self, benchmark):
        """Benchmark cache miss performance"""
        from app.core.cache import CacheManager

        cache = CacheManager()

        if benchmark:
            result = benchmark(lambda: cache.get("nonexistent_key"))
            assert result is None
        else:
            start = time.time()
            value = cache.get("nonexistent_key")
            duration = time.time() - start

            assert value is None
            assert duration < 0.01, f"Cache miss took {duration:.3f}s (target: <0.01s)"

    def test_cache_set_performance(self, benchmark):
        """Benchmark cache set performance"""
        from app.core.cache import CacheManager

        cache = CacheManager()
        data = {"key": "value", "number": 123, "list": [1, 2, 3]}

        if benchmark:
            benchmark(lambda: cache.set(f"perf_test_{time.time()}", data, ttl=60))
        else:
            start = time.time()
            cache.set("perf_test", data, ttl=60)
            duration = time.time() - start

            assert duration < 0.01, f"Cache set took {duration:.3f}s (target: <0.01s)"


# ============================================================================
# Authentication Benchmarks
# ============================================================================

class TestAuthenticationBenchmarks:
    """Benchmark tests for authentication operations"""

    def test_password_hashing_performance(self, benchmark):
        """Benchmark password hashing"""
        from app.core.security import get_password_hash

        if benchmark:
            benchmark(lambda: get_password_hash("TestPassword123"))
        else:
            start = time.time()
            get_password_hash("TestPassword123")
            duration = time.time() - start

            # Password hashing should be slow (security feature)
            assert duration > 0.05, f"Password hash too fast: {duration:.3f}s (should be >0.05s for security)"
            assert duration < 1.0, f"Password hash too slow: {duration:.3f}s (target: <1s)"

    def test_token_creation_performance(self, benchmark):
        """Benchmark JWT token creation"""
        from app.core.security import create_access_token

        if benchmark:
            benchmark(lambda: create_access_token(subject="test-user-id"))
        else:
            start = time.time()
            create_access_token(subject="test-user-id")
            duration = time.time() - start

            assert duration < 0.1, f"Token creation took {duration:.3f}s (target: <0.1s)"

    def test_token_verification_performance(self, benchmark):
        """Benchmark JWT token verification"""
        from app.core.security import create_access_token, verify_token

        token = create_access_token(subject="test-user-id")

        if benchmark:
            benchmark(lambda: verify_token(token))
        else:
            start = time.time()
            verify_token(token)
            duration = time.time() - start

            assert duration < 0.1, f"Token verification took {duration:.3f}s (target: <0.1s)"


# ============================================================================
# Data Processing Benchmarks
# ============================================================================

class TestDataProcessingBenchmarks:
    """Benchmark tests for data processing operations"""

    def test_json_serialization_performance(self, benchmark):
        """Benchmark JSON serialization"""
        from app.core.cache import CacheJSONEncoder
        import json

        data = {
            "trades": [
                {
                    "id": i,
                    "ticker": f"TST{i}",
                    "amount": Decimal("1000.50"),
                    "date": datetime.utcnow()
                }
                for i in range(100)
            ]
        }

        if benchmark:
            benchmark(lambda: json.dumps(data, cls=CacheJSONEncoder))
        else:
            start = time.time()
            json.dumps(data, cls=CacheJSONEncoder)
            duration = time.time() - start

            assert duration < 0.1, f"JSON serialization took {duration:.3f}s (target: <0.1s)"

    def test_dataframe_creation_performance(self, benchmark):
        """Benchmark pandas DataFrame creation"""
        import pandas as pd

        data = [
            {
                "ticker": f"TST{i}",
                "price": 100.0 + i,
                "volume": 1000000 + i,
                "date": datetime.utcnow() - timedelta(days=i)
            }
            for i in range(1000)
        ]

        if benchmark:
            benchmark(lambda: pd.DataFrame(data))
        else:
            start = time.time()
            pd.DataFrame(data)
            duration = time.time() - start

            assert duration < 0.5, f"DataFrame creation took {duration:.3f}s (target: <0.5s)"


# ============================================================================
# Concurrent Request Benchmarks
# ============================================================================

class TestConcurrentRequestBenchmarks:
    """Benchmark tests for concurrent request handling"""

    def test_concurrent_stats_requests(self, client: TestClient, benchmark):
        """Benchmark concurrent stats requests"""
        import concurrent.futures

        def make_request():
            return client.get("/api/v1/stats/overview")

        if benchmark:
            def run_concurrent():
                with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
                    futures = [executor.submit(make_request) for _ in range(10)]
                    results = [f.result() for f in futures]
                return all(r.status_code == 200 for r in results)

            result = benchmark(run_concurrent)
            assert result
        else:
            start = time.time()
            with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
                futures = [executor.submit(make_request) for _ in range(10)]
                results = [f.result() for f in futures]
            duration = time.time() - start

            assert all(r.status_code == 200 for r in results)
            assert duration < 3.0, f"10 concurrent requests took {duration:.3f}s (target: <3s)"


# ============================================================================
# Performance Regression Tests
# ============================================================================

class TestPerformanceRegression:
    """Tests to catch performance regressions"""

    def test_no_n_plus_one_queries(self, client: TestClient):
        """Ensure we don't have N+1 query problems"""
        # This test would require query counting
        # For now, just verify the endpoint works efficiently

        start = time.time()
        response = client.get("/api/v1/stats/leaderboard?limit=50")
        duration = time.time() - start

        assert response.status_code == 200
        # Leaderboard with 50 items should not take more than 2 seconds
        assert duration < 2.0, f"Potential N+1 query issue: {duration:.3f}s for 50 items"

    def test_response_size_reasonable(self, client: TestClient):
        """Ensure response sizes are reasonable"""
        response = client.get("/api/v1/stats/overview")

        assert response.status_code == 200
        # Response should be less than 100KB
        size_kb = len(response.content) / 1024
        assert size_kb < 100, f"Response too large: {size_kb:.2f}KB (target: <100KB)"


# ============================================================================
# Fixtures
# ============================================================================

@pytest.fixture
def benchmark():
    """Provide benchmark fixture (returns None if pytest-benchmark not installed)"""
    try:
        # If pytest-benchmark is installed, request it from pytest
        import pytest_benchmark
        return None  # Pytest will inject the real benchmark fixture
    except ImportError:
        return None


# ============================================================================
# Standalone Performance Test
# ============================================================================

def run_quick_performance_check(host="http://localhost:8000"):
    """Quick performance check without pytest"""
    import requests

    print("\n" + "="*70)
    print("QUICK PERFORMANCE CHECK")
    print("="*70 + "\n")

    endpoints = [
        ("/api/v1/stats/overview", 1.0),
        ("/api/v1/stats/leaderboard?limit=20", 2.0),
        ("/api/v1/stats/tickers?limit=20", 2.0),
        ("/api/v1/market-data/public/market-status", 0.5),
    ]

    for endpoint, target_time in endpoints:
        try:
            start = time.time()
            response = requests.get(f"{host}{endpoint}", timeout=10)
            duration = time.time() - start

            status = "✅" if duration < target_time else "⚠️"
            print(f"{status} {endpoint}")
            print(f"   Time: {duration:.3f}s (target: <{target_time}s)")
            print(f"   Status: {response.status_code}")
            print()

        except Exception as e:
            print(f"❌ {endpoint}")
            print(f"   Error: {str(e)}")
            print()

    print("="*70 + "\n")


if __name__ == "__main__":
    import sys
    host = sys.argv[1] if len(sys.argv) > 1 else "http://localhost:8000"
    run_quick_performance_check(host)
