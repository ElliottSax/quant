"""Tests for trades endpoints."""

import pytest
from fastapi.testclient import TestClient

from app.models.politician import Politician
from app.models.trade import Trade


def test_list_trades_empty(client: TestClient):
    """Test listing trades when none exist."""
    response = client.get("/api/v1/trades/")

    assert response.status_code == 200
    data = response.json()
    assert data["trades"] == []
    assert data["total"] == 0


def test_list_trades(client: TestClient, test_trade: Trade):
    """Test listing trades."""
    response = client.get("/api/v1/trades/")

    assert response.status_code == 200
    data = response.json()
    assert len(data["trades"]) == 1
    assert data["total"] == 1
    assert data["trades"][0]["ticker"] == "AAPL"
    assert data["trades"][0]["transaction_type"] == "buy"
    assert data["trades"][0]["politician_name"] == "John Doe"


def test_list_trades_filter_by_ticker(client: TestClient, test_trade: Trade):
    """Test filtering trades by ticker."""
    response = client.get("/api/v1/trades/?ticker=AAPL")

    assert response.status_code == 200
    data = response.json()
    assert len(data["trades"]) == 1
    assert data["trades"][0]["ticker"] == "AAPL"

    # Test non-matching ticker
    response = client.get("/api/v1/trades/?ticker=MSFT")
    data = response.json()
    assert len(data["trades"]) == 0


def test_list_trades_filter_by_transaction_type(client: TestClient, test_trade: Trade):
    """Test filtering trades by transaction type."""
    response = client.get("/api/v1/trades/?transaction_type=buy")

    assert response.status_code == 200
    data = response.json()
    assert len(data["trades"]) == 1

    # Test non-matching type
    response = client.get("/api/v1/trades/?transaction_type=sell")
    data = response.json()
    assert len(data["trades"]) == 0


def test_list_trades_invalid_transaction_type(client: TestClient):
    """Test filtering with invalid transaction type."""
    response = client.get("/api/v1/trades/?transaction_type=invalid")

    assert response.status_code == 400
    assert "invalid" in response.json()["detail"].lower()


def test_list_trades_invalid_ticker(client: TestClient):
    """Test filtering with invalid ticker format."""
    response = client.get("/api/v1/trades/?ticker=INVALID!@#")

    assert response.status_code == 400


def test_list_trades_pagination(client: TestClient, test_trade: Trade):
    """Test trades pagination."""
    response = client.get("/api/v1/trades/?skip=0&limit=10")

    assert response.status_code == 200
    data = response.json()
    assert data["skip"] == 0
    assert data["limit"] == 10


def test_list_trades_invalid_pagination(client: TestClient):
    """Test invalid pagination parameters."""
    # Negative skip
    response = client.get("/api/v1/trades/?skip=-1")
    assert response.status_code == 400

    # Invalid limit
    response = client.get("/api/v1/trades/?limit=0")
    assert response.status_code == 400

    # Limit too large (should be capped)
    response = client.get("/api/v1/trades/?limit=1000")
    assert response.status_code == 200
    data = response.json()
    assert data["limit"] == 100  # Should be capped at 100


def test_get_trade_by_id(client: TestClient, test_trade: Trade):
    """Test getting a specific trade by ID."""
    response = client.get(f"/api/v1/trades/{test_trade.id}")

    assert response.status_code == 200
    data = response.json()
    assert data["id"] == str(test_trade.id)
    assert data["ticker"] == "AAPL"
    assert data["politician_name"] == "John Doe"


def test_get_trade_not_found(client: TestClient):
    """Test getting a non-existent trade."""
    fake_uuid = "00000000-0000-0000-0000-000000000000"
    response = client.get(f"/api/v1/trades/{fake_uuid}")

    assert response.status_code == 404


def test_get_trade_invalid_uuid(client: TestClient):
    """Test getting a trade with invalid UUID."""
    response = client.get("/api/v1/trades/invalid-uuid")

    assert response.status_code == 422  # Validation error


def test_recent_trades(client: TestClient, test_trade: Trade):
    """Test getting recent trades."""
    response = client.get("/api/v1/trades/recent/list?limit=10")

    assert response.status_code == 200
    data = response.json()
    assert len(data["trades"]) == 1
    assert data["trades"][0]["ticker"] == "AAPL"


def test_recent_trades_limit(client: TestClient, test_trade: Trade):
    """Test recent trades with limit."""
    response = client.get("/api/v1/trades/recent/list?limit=5")

    assert response.status_code == 200
    data = response.json()
    assert data["limit"] == 5


def test_recent_trades_invalid_limit(client: TestClient):
    """Test recent trades with invalid limit."""
    response = client.get("/api/v1/trades/recent/list?limit=0")

    assert response.status_code == 400
