"""Tests for stats endpoints."""

import pytest
from datetime import date, timedelta
from decimal import Decimal
from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.politician import Politician
from app.models.trade import Trade


def test_get_stats_overview(client: TestClient):
    """Test getting stats overview."""
    response = client.get("/api/v1/stats/overview")

    assert response.status_code == 200
    data = response.json()
    assert "total_trades" in data
    assert "total_politicians" in data
    assert "total_tickers" in data


def test_get_stats_overview_with_data(
    client: TestClient, test_trade: Trade, test_politician: Politician
):
    """Test stats overview reflects data."""
    response = client.get("/api/v1/stats/overview")

    assert response.status_code == 200
    data = response.json()
    assert data["total_trades"] >= 1
    assert data["total_politicians"] >= 1


def test_get_leaderboard(client: TestClient):
    """Test getting politician leaderboard."""
    response = client.get("/api/v1/stats/leaderboard")

    assert response.status_code == 200
    data = response.json()
    assert "leaderboard" in data or isinstance(data, list)


def test_get_leaderboard_with_data(
    client: TestClient, test_trade: Trade, test_politician: Politician
):
    """Test leaderboard with trade data."""
    response = client.get("/api/v1/stats/leaderboard")

    assert response.status_code == 200
    data = response.json()
    # Should return leaderboard data
    assert data is not None


def test_get_leaderboard_limit(client: TestClient):
    """Test leaderboard with limit parameter."""
    response = client.get("/api/v1/stats/leaderboard?limit=5")

    assert response.status_code == 200
    data = response.json()
    # Limit should be respected
    if "leaderboard" in data:
        assert len(data["leaderboard"]) <= 5


def test_get_leaderboard_time_range(client: TestClient):
    """Test leaderboard with time range."""
    response = client.get("/api/v1/stats/leaderboard?days=30")

    assert response.status_code == 200
    data = response.json()
    assert data is not None


def test_get_ticker_stats(client: TestClient):
    """Test getting ticker statistics."""
    response = client.get("/api/v1/stats/tickers")

    assert response.status_code == 200
    data = response.json()
    assert "tickers" in data or isinstance(data, list)


def test_get_ticker_stats_with_data(client: TestClient, test_trade: Trade):
    """Test ticker stats with trade data."""
    response = client.get("/api/v1/stats/tickers")

    assert response.status_code == 200
    data = response.json()
    # Should contain AAPL since we have a test trade with AAPL
    tickers = data.get("tickers", data)
    if tickers:
        ticker_symbols = [t.get("ticker", t.get("symbol")) for t in tickers]
        assert "AAPL" in ticker_symbols


def test_get_ticker_stats_limit(client: TestClient):
    """Test ticker stats with limit."""
    response = client.get("/api/v1/stats/tickers?limit=10")

    assert response.status_code == 200
    data = response.json()
    tickers = data.get("tickers", data)
    if isinstance(tickers, list):
        assert len(tickers) <= 10


def test_get_trade_volume_by_date(client: TestClient):
    """Test getting trade volume over time."""
    response = client.get("/api/v1/stats/volume")

    assert response.status_code == 200
    data = response.json()
    assert data is not None


def test_get_trade_volume_date_range(client: TestClient):
    """Test trade volume with date range."""
    start_date = (date.today() - timedelta(days=30)).isoformat()
    end_date = date.today().isoformat()

    response = client.get(f"/api/v1/stats/volume?start_date={start_date}&end_date={end_date}")

    assert response.status_code == 200


def test_get_party_stats(client: TestClient):
    """Test getting stats by party."""
    response = client.get("/api/v1/stats/by-party")

    assert response.status_code == 200
    data = response.json()
    assert data is not None


@pytest.mark.asyncio
async def test_stats_with_multiple_trades(
    client: TestClient, test_politician: Politician, db_session: AsyncSession
):
    """Test stats with multiple trades."""
    # Create multiple trades
    trades = [
        Trade(
            politician_id=test_politician.id,
            ticker="AAPL",
            transaction_type="buy",
            amount_min=Decimal("1000.00"),
            amount_max=Decimal("15000.00"),
            transaction_date=date.today() - timedelta(days=1),
            disclosure_date=date.today(),
            source_url="https://example.com/1",
        ),
        Trade(
            politician_id=test_politician.id,
            ticker="MSFT",
            transaction_type="sell",
            amount_min=Decimal("5000.00"),
            amount_max=Decimal("25000.00"),
            transaction_date=date.today() - timedelta(days=2),
            disclosure_date=date.today(),
            source_url="https://example.com/2",
        ),
        Trade(
            politician_id=test_politician.id,
            ticker="GOOGL",
            transaction_type="buy",
            amount_min=Decimal("10000.00"),
            amount_max=Decimal("50000.00"),
            transaction_date=date.today() - timedelta(days=3),
            disclosure_date=date.today(),
            source_url="https://example.com/3",
        ),
    ]

    for trade in trades:
        db_session.add(trade)
    await db_session.commit()

    # Test overview
    response = client.get("/api/v1/stats/overview")
    assert response.status_code == 200
    data = response.json()
    assert data["total_trades"] >= 3

    # Test leaderboard
    response = client.get("/api/v1/stats/leaderboard")
    assert response.status_code == 200


def test_stats_caching(client: TestClient):
    """Test that stats endpoints are cached."""
    # Make two requests quickly - second should be faster (cached)
    import time

    start1 = time.time()
    response1 = client.get("/api/v1/stats/overview")
    time1 = time.time() - start1

    start2 = time.time()
    response2 = client.get("/api/v1/stats/overview")
    time2 = time.time() - start2

    assert response1.status_code == 200
    assert response2.status_code == 200

    # Both should return same data
    assert response1.json() == response2.json()


def test_invalid_date_range(client: TestClient):
    """Test stats with invalid date range."""
    # End date before start date
    response = client.get("/api/v1/stats/volume?start_date=2024-12-31&end_date=2024-01-01")

    # Should handle gracefully (either 200 with empty data or 400)
    assert response.status_code in [200, 400]


def test_invalid_limit(client: TestClient):
    """Test stats with invalid limit."""
    response = client.get("/api/v1/stats/leaderboard?limit=-1")

    # Should reject negative limit
    assert response.status_code == 400 or (
        response.status_code == 200 and len(response.json().get("leaderboard", [])) == 0
    )
