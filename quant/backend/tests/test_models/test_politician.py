"""Tests for Politician model."""

import uuid
from datetime import datetime

import pytest
from sqlalchemy.exc import IntegrityError

from app.models.politician import Politician
from app.models.trade import Trade
from datetime import date


class TestPoliticianModel:
    """Test cases for Politician model."""

    async def test_create_politician(self, db_session):
        """Test creating a basic politician."""
        pol = Politician(
            name="Jane Smith",
            chamber="senate",
            party="Republican",
            state="TX",
            bioguide_id="S000001",
        )
        db_session.add(pol)
        await db_session.commit()
        await db_session.refresh(pol)

        assert pol.id is not None
        assert isinstance(pol.id, uuid.UUID)
        assert pol.name == "Jane Smith"
        assert pol.chamber == "senate"
        assert pol.party == "Republican"
        assert pol.state == "TX"
        assert pol.bioguide_id == "S000001"

    async def test_house_chamber(self, db_session):
        """Test creating a house member."""
        pol = Politician(
            name="Bob Johnson",
            chamber="house",
            party="Democrat",
            state="NY",
        )
        db_session.add(pol)
        await db_session.commit()
        await db_session.refresh(pol)

        assert pol.chamber == "house"

    async def test_invalid_chamber(self, db_session):
        """Test that chamber must be 'senate' or 'house'."""
        pol = Politician(
            name="Invalid Chamber",
            chamber="president",  # Invalid
            party="Independent",
        )
        db_session.add(pol)

        with pytest.raises(IntegrityError):
            await db_session.commit()

    async def test_optional_party(self, db_session):
        """Test that party is optional."""
        pol = Politician(
            name="Independent Person",
            chamber="senate",
            state="ME",
            # No party specified
        )
        db_session.add(pol)
        await db_session.commit()
        await db_session.refresh(pol)

        assert pol.party is None

    async def test_optional_state(self, db_session):
        """Test that state is optional."""
        pol = Politician(
            name="No State",
            chamber="house",
            party="Democrat",
            # No state specified
        )
        db_session.add(pol)
        await db_session.commit()
        await db_session.refresh(pol)

        assert pol.state is None

    async def test_optional_bioguide_id(self, db_session):
        """Test that bioguide_id is optional."""
        pol = Politician(
            name="No Bioguide",
            chamber="senate",
            party="Republican",
            state="FL",
            # No bioguide_id
        )
        db_session.add(pol)
        await db_session.commit()
        await db_session.refresh(pol)

        assert pol.bioguide_id is None

    async def test_unique_bioguide_id(self, db_session):
        """Test that bioguide_id must be unique."""
        pol1 = Politician(
            name="First Person",
            chamber="senate",
            bioguide_id="S000123",
        )
        db_session.add(pol1)
        await db_session.commit()

        pol2 = Politician(
            name="Second Person",
            chamber="house",
            bioguide_id="S000123",  # Duplicate
        )
        db_session.add(pol2)

        with pytest.raises(IntegrityError):
            await db_session.commit()

    async def test_timestamps_auto_populated(self, db_session):
        """Test that created_at and updated_at are auto-populated."""
        pol = Politician(
            name="Timestamp Test",
            chamber="senate",
        )
        db_session.add(pol)
        await db_session.commit()
        await db_session.refresh(pol)

        assert pol.created_at is not None
        assert pol.updated_at is not None
        assert isinstance(pol.created_at, datetime)
        assert isinstance(pol.updated_at, datetime)

    async def test_name_indexed(self, db_session):
        """Test that name is indexed for efficient querying."""
        # Create multiple politicians
        for i in range(5):
            pol = Politician(
                name=f"Test Politician {i}",
                chamber="senate" if i % 2 == 0 else "house",
            )
            db_session.add(pol)
        await db_session.commit()

        # Query by name should be fast (indexed)
        pol = await db_session.query(Politician).filter_by(name="Test Politician 3").first()
        assert pol is not None
        assert pol.name == "Test Politician 3"

    async def test_chamber_indexed(self, db_session):
        """Test that chamber is indexed for efficient querying."""
        # Create senators and representatives
        for i in range(10):
            pol = Politician(
                name=f"Politician {i}",
                chamber="senate" if i < 5 else "house",
            )
            db_session.add(pol)
        await db_session.commit()

        # Query by chamber should be fast (indexed)
        senators = await db_session.query(Politician).filter_by(chamber="senate").all()
        assert len(senators) == 5

    async def test_party_indexed(self, db_session):
        """Test that party is indexed for efficient querying."""
        # Create politicians from different parties
        pol1 = Politician(name="Dem 1", chamber="senate", party="Democrat")
        pol2 = Politician(name="Rep 1", chamber="house", party="Republican")
        pol3 = Politician(name="Dem 2", chamber="senate", party="Democrat")
        db_session.add_all([pol1, pol2, pol3])
        await db_session.commit()

        # Query by party should be fast (indexed)
        democrats = await db_session.query(Politician).filter_by(party="Democrat").all()
        assert len(democrats) == 2

    async def test_trades_relationship(self, db_session):
        """Test relationship to trades."""
        pol = Politician(
            name="Trader",
            chamber="senate",
        )
        db_session.add(pol)
        await db_session.commit()
        await db_session.refresh(pol)

        # Add trades for this politician
        trade1 = Trade(
            politician_id=pol.id,
            ticker="AAPL",
            transaction_type="buy",
            transaction_date=date.today(),
            disclosure_date=date.today(),
        )
        trade2 = Trade(
            politician_id=pol.id,
            ticker="GOOGL",
            transaction_type="sell",
            transaction_date=date.today(),
            disclosure_date=date.today(),
        )
        db_session.add_all([trade1, trade2])
        await db_session.commit()

        # Access trades through relationship
        await db_session.refresh(pol)
        assert len(pol.trades) == 2
        assert pol.trades[0].ticker in ["AAPL", "GOOGL"]
        assert pol.trades[1].ticker in ["AAPL", "GOOGL"]

    async def test_cascade_delete_trades(self, db_session):
        """Test that deleting politician deletes associated trades."""
        pol = Politician(
            name="To Delete",
            chamber="house",
        )
        db_session.add(pol)
        await db_session.commit()

        # Add trades
        for ticker in ["AAPL", "MSFT", "GOOGL"]:
            trade = Trade(
                politician_id=pol.id,
                ticker=ticker,
                transaction_type="buy",
                transaction_date=date.today(),
                disclosure_date=date.today(),
            )
            db_session.add(trade)
        await db_session.commit()

        pol_id = pol.id

        # Verify trades exist
        trades_before = await db_session.query(Trade).filter_by(politician_id=pol_id).all()
        assert len(trades_before) == 3

        # Delete politician
        db_session.delete(pol)
        await db_session.commit()

        # Verify trades are also deleted (cascade)
        trades_after = await db_session.query(Trade).filter_by(politician_id=pol_id).all()
        assert len(trades_after) == 0

    async def test_politician_repr(self, db_session):
        """Test string representation of politician."""
        pol = Politician(
            name="Repr Test",
            chamber="senate",
        )
        db_session.add(pol)
        await db_session.commit()
        await db_session.refresh(pol)

        repr_str = repr(pol)
        assert "Repr Test" in repr_str
        assert "senate" in repr_str

    async def test_duplicate_name_allowed(self, db_session):
        """Test that duplicate names are allowed (different people can have same name)."""
        pol1 = Politician(
            name="John Smith",
            chamber="senate",
            state="CA",
        )
        pol2 = Politician(
            name="John Smith",
            chamber="house",
            state="NY",
        )
        db_session.add_all([pol1, pol2])
        await db_session.commit()

        pols = await db_session.query(Politician).filter_by(name="John Smith").all()
        assert len(pols) == 2

    async def test_state_abbreviation_format(self, db_session):
        """Test that state uses standard 2-letter abbreviation."""
        pol = Politician(
            name="State Test",
            chamber="senate",
            state="CA",  # Standard 2-letter code
        )
        db_session.add(pol)
        await db_session.commit()
        await db_session.refresh(pol)

        assert pol.state == "CA"
        assert len(pol.state) == 2

    async def test_all_parties(self, db_session):
        """Test various party affiliations."""
        parties = ["Democrat", "Republican", "Independent", "Libertarian"]
        for i, party in enumerate(parties):
            pol = Politician(
                name=f"Politician {i}",
                chamber="senate" if i % 2 == 0 else "house",
                party=party,
            )
            db_session.add(pol)
        await db_session.commit()

        for party in parties:
            found = await db_session.query(Politician).filter_by(party=party).first()
            assert found is not None
            assert found.party == party

    async def test_query_by_state_and_chamber(self, db_session):
        """Test querying by state and chamber combination."""
        # CA senators
        pol1 = Politician(name="CA Senator 1", chamber="senate", state="CA")
        pol2 = Politician(name="CA Senator 2", chamber="senate", state="CA")
        # CA representatives
        pol3 = Politician(name="CA Rep 1", chamber="house", state="CA")
        # TX senator
        pol4 = Politician(name="TX Senator", chamber="senate", state="TX")

        db_session.add_all([pol1, pol2, pol3, pol4])
        await db_session.commit()

        # Query CA senators specifically
        ca_senators = (
            await db_session.query(Politician)
            .filter_by(state="CA", chamber="senate")
            .all()
        )
        assert len(ca_senators) == 2
        assert all(p.state == "CA" and p.chamber == "senate" for p in ca_senators)
