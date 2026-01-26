"""Tests for politicians endpoints."""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.politician import Politician
from app.models.trade import Trade


def test_list_politicians_empty(client: TestClient):
    """Test listing politicians when none exist."""
    response = client.get("/api/v1/politicians/")

    assert response.status_code == 200
    data = response.json()
    assert data["politicians"] == []
    assert data["total"] == 0


def test_list_politicians(client: TestClient, test_politician: Politician):
    """Test listing politicians."""
    response = client.get("/api/v1/politicians/")

    assert response.status_code == 200
    data = response.json()
    assert len(data["politicians"]) == 1
    assert data["total"] == 1
    assert data["politicians"][0]["name"] == "John Doe"
    assert data["politicians"][0]["chamber"] == "senate"
    assert data["politicians"][0]["party"] == "Independent"


def test_list_politicians_filter_by_chamber(client: TestClient, test_politician: Politician):
    """Test filtering politicians by chamber."""
    response = client.get("/api/v1/politicians/?chamber=senate")

    assert response.status_code == 200
    data = response.json()
    assert len(data["politicians"]) == 1
    assert data["politicians"][0]["chamber"] == "senate"

    # Test non-matching chamber
    response = client.get("/api/v1/politicians/?chamber=house")
    data = response.json()
    assert len(data["politicians"]) == 0


def test_list_politicians_filter_by_party(client: TestClient, test_politician: Politician):
    """Test filtering politicians by party."""
    response = client.get("/api/v1/politicians/?party=Independent")

    assert response.status_code == 200
    data = response.json()
    assert len(data["politicians"]) == 1

    # Test non-matching party
    response = client.get("/api/v1/politicians/?party=Democrat")
    data = response.json()
    assert len(data["politicians"]) == 0


def test_list_politicians_filter_by_state(client: TestClient, test_politician: Politician):
    """Test filtering politicians by state."""
    response = client.get("/api/v1/politicians/?state=CA")

    assert response.status_code == 200
    data = response.json()
    assert len(data["politicians"]) == 1
    assert data["politicians"][0]["state"] == "CA"

    # Test non-matching state
    response = client.get("/api/v1/politicians/?state=NY")
    data = response.json()
    assert len(data["politicians"]) == 0


def test_list_politicians_pagination(client: TestClient, test_politician: Politician):
    """Test politicians pagination."""
    response = client.get("/api/v1/politicians/?skip=0&limit=10")

    assert response.status_code == 200
    data = response.json()
    assert data["skip"] == 0
    assert data["limit"] == 10


def test_list_politicians_search(client: TestClient, test_politician: Politician):
    """Test searching politicians by name."""
    response = client.get("/api/v1/politicians/?search=John")

    assert response.status_code == 200
    data = response.json()
    assert len(data["politicians"]) == 1
    assert "John" in data["politicians"][0]["name"]

    # Test non-matching search
    response = client.get("/api/v1/politicians/?search=XYZ")
    data = response.json()
    assert len(data["politicians"]) == 0


def test_get_politician_by_id(client: TestClient, test_politician: Politician):
    """Test getting a specific politician by ID."""
    response = client.get(f"/api/v1/politicians/{test_politician.id}")

    assert response.status_code == 200
    data = response.json()
    assert data["id"] == str(test_politician.id)
    assert data["name"] == "John Doe"
    assert data["chamber"] == "senate"
    assert data["party"] == "Independent"
    assert data["state"] == "CA"
    assert data["bioguide_id"] == "D000001"


def test_get_politician_not_found(client: TestClient):
    """Test getting a non-existent politician."""
    fake_uuid = "00000000-0000-0000-0000-000000000000"
    response = client.get(f"/api/v1/politicians/{fake_uuid}")

    assert response.status_code == 404


def test_get_politician_invalid_uuid(client: TestClient):
    """Test getting a politician with invalid UUID."""
    response = client.get("/api/v1/politicians/invalid-uuid")

    assert response.status_code == 422  # Validation error


def test_get_politician_trades(client: TestClient, test_trade: Trade, test_politician: Politician):
    """Test getting trades for a specific politician."""
    response = client.get(f"/api/v1/politicians/{test_politician.id}/trades")

    assert response.status_code == 200
    data = response.json()
    assert len(data["trades"]) == 1
    assert data["trades"][0]["ticker"] == "AAPL"
    assert data["politician"]["name"] == "John Doe"


def test_get_politician_trades_empty(client: TestClient, test_politician: Politician):
    """Test getting trades for politician with no trades."""
    response = client.get(f"/api/v1/politicians/{test_politician.id}/trades")

    assert response.status_code == 200
    data = response.json()
    assert data["trades"] == []


def test_get_politician_trades_pagination(
    client: TestClient, test_trade: Trade, test_politician: Politician
):
    """Test pagination for politician trades."""
    response = client.get(f"/api/v1/politicians/{test_politician.id}/trades?skip=0&limit=5")

    assert response.status_code == 200
    data = response.json()
    assert data["skip"] == 0
    assert data["limit"] == 5


@pytest.mark.asyncio
async def test_list_politicians_multiple_filters(
    client: TestClient, db_session: AsyncSession
):
    """Test multiple filters combined."""
    # Create additional politicians
    politician1 = Politician(
        name="Jane Smith",
        chamber="house",
        party="Democrat",
        state="NY",
        bioguide_id="S000001",
    )
    politician2 = Politician(
        name="Bob Wilson",
        chamber="senate",
        party="Republican",
        state="TX",
        bioguide_id="W000001",
    )
    db_session.add(politician1)
    db_session.add(politician2)
    await db_session.commit()

    # Filter by chamber and party
    response = client.get("/api/v1/politicians/?chamber=house&party=Democrat")
    assert response.status_code == 200
    data = response.json()
    assert len(data["politicians"]) == 1
    assert data["politicians"][0]["name"] == "Jane Smith"

    # Filter by chamber and state
    response = client.get("/api/v1/politicians/?chamber=senate&state=TX")
    data = response.json()
    assert len(data["politicians"]) == 1
    assert data["politicians"][0]["name"] == "Bob Wilson"


def test_invalid_chamber_filter(client: TestClient):
    """Test invalid chamber filter value."""
    response = client.get("/api/v1/politicians/?chamber=invalid")

    # Should either return empty or 400 depending on implementation
    assert response.status_code in [200, 400]
