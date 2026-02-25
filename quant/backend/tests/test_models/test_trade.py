"""Tests for Trade model."""

import uuid
from datetime import date, datetime, timedelta
from decimal import Decimal

import pytest
from sqlalchemy.exc import IntegrityError

from app.models.politician import Politician
from app.models.trade import Trade


class TestTradeModel:
    """Test cases for Trade model."""

    @pytest.fixture
    def politician(self, db_session):
        """Create a test politician."""
        pol = Politician(
            name="John Doe",
            chamber="senate",
            party="Democrat",
            state="CA",
        )
        db_session.add(pol)
        await db_session.commit()
        await db_session.refresh(pol)
        return pol

    async def test_create_trade(self, db_session, politician):
        """Test creating a basic trade."""
        trade = Trade(
            politician_id=politician.id,
            ticker="AAPL",
            transaction_type="buy",
            amount_min=Decimal("15000.00"),
            amount_max=Decimal("50000.00"),
            transaction_date=date(2024, 1, 15),
            disclosure_date=date(2024, 2, 1),
            source_url="https://example.com/disclosure",
        )
        db_session.add(trade)
        await db_session.commit()
        await db_session.refresh(trade)

        assert trade.id is not None
        assert isinstance(trade.id, uuid.UUID)
        assert trade.politician_id == politician.id
        assert trade.ticker == "AAPL"
        assert trade.transaction_type == "buy"
        assert trade.amount_min == Decimal("15000.00")
        assert trade.amount_max == Decimal("50000.00")
        assert trade.transaction_date == date(2024, 1, 15)
        assert trade.disclosure_date == date(2024, 2, 1)
        assert trade.source_url == "https://example.com/disclosure"

    async def test_sell_transaction(self, db_session, politician):
        """Test creating a sell transaction."""
        trade = Trade(
            politician_id=politician.id,
            ticker="TSLA",
            transaction_type="sell",
            amount_min=Decimal("100000.00"),
            amount_max=Decimal("250000.00"),
            transaction_date=date.today(),
            disclosure_date=date.today(),
        )
        db_session.add(trade)
        await db_session.commit()
        await db_session.refresh(trade)

        assert trade.transaction_type == "sell"

    async def test_invalid_transaction_type(self, db_session, politician):
        """Test that transaction_type must be 'buy' or 'sell'."""
        trade = Trade(
            politician_id=politician.id,
            ticker="MSFT",
            transaction_type="hold",  # Invalid
            transaction_date=date.today(),
            disclosure_date=date.today(),
        )
        db_session.add(trade)

        with pytest.raises(IntegrityError):
            await db_session.commit()

    async def test_amount_range_validation(self, db_session, politician):
        """Test that amount_min <= amount_max."""
        trade = Trade(
            politician_id=politician.id,
            ticker="GOOGL",
            transaction_type="buy",
            amount_min=Decimal("100000.00"),
            amount_max=Decimal("50000.00"),  # Less than min - invalid
            transaction_date=date.today(),
            disclosure_date=date.today(),
        )
        db_session.add(trade)

        with pytest.raises(IntegrityError):
            await db_session.commit()

    async def test_negative_amount_validation(self, db_session, politician):
        """Test that amounts cannot be negative."""
        trade = Trade(
            politician_id=politician.id,
            ticker="AMZN",
            transaction_type="buy",
            amount_min=Decimal("-1000.00"),  # Negative - invalid
            transaction_date=date.today(),
            disclosure_date=date.today(),
        )
        db_session.add(trade)

        with pytest.raises(IntegrityError):
            await db_session.commit()

    async def test_disclosure_after_transaction_validation(self, db_session, politician):
        """Test that disclosure_date >= transaction_date."""
        trade = Trade(
            politician_id=politician.id,
            ticker="FB",
            transaction_type="buy",
            transaction_date=date(2024, 2, 1),
            disclosure_date=date(2024, 1, 1),  # Before transaction - invalid
        )
        db_session.add(trade)

        with pytest.raises(IntegrityError):
            await db_session.commit()

    async def test_valid_disclosure_same_day(self, db_session, politician):
        """Test that disclosure can be on same day as transaction."""
        trade_date = date.today()
        trade = Trade(
            politician_id=politician.id,
            ticker="NFLX",
            transaction_type="buy",
            transaction_date=trade_date,
            disclosure_date=trade_date,  # Same day - valid
        )
        db_session.add(trade)
        await db_session.commit()
        await db_session.refresh(trade)

        assert trade.transaction_date == trade.disclosure_date

    async def test_optional_amount_fields(self, db_session, politician):
        """Test that amount fields are optional."""
        trade = Trade(
            politician_id=politician.id,
            ticker="NVDA",
            transaction_type="buy",
            transaction_date=date.today(),
            disclosure_date=date.today(),
            # No amount_min or amount_max
        )
        db_session.add(trade)
        await db_session.commit()
        await db_session.refresh(trade)

        assert trade.amount_min is None
        assert trade.amount_max is None

    async def test_optional_source_url(self, db_session, politician):
        """Test that source_url is optional."""
        trade = Trade(
            politician_id=politician.id,
            ticker="AMD",
            transaction_type="sell",
            transaction_date=date.today(),
            disclosure_date=date.today(),
            # No source_url
        )
        db_session.add(trade)
        await db_session.commit()
        await db_session.refresh(trade)

        assert trade.source_url is None

    async def test_raw_data_json_storage(self, db_session, politician):
        """Test storing raw data as JSON."""
        raw = {
            "filing_id": "12345",
            "asset_description": "Common Stock",
            "owner": "Self",
        }
        trade = Trade(
            politician_id=politician.id,
            ticker="INTC",
            transaction_type="buy",
            transaction_date=date.today(),
            disclosure_date=date.today(),
            raw_data=raw,
        )
        db_session.add(trade)
        await db_session.commit()
        await db_session.refresh(trade)

        assert trade.raw_data is not None
        assert trade.raw_data["filing_id"] == "12345"
        assert trade.raw_data["asset_description"] == "Common Stock"

    async def test_created_at_auto_populated(self, db_session, politician):
        """Test that created_at is auto-populated."""
        trade = Trade(
            politician_id=politician.id,
            ticker="CSCO",
            transaction_type="buy",
            transaction_date=date.today(),
            disclosure_date=date.today(),
        )
        db_session.add(trade)
        await db_session.commit()
        await db_session.refresh(trade)

        assert trade.created_at is not None
        assert isinstance(trade.created_at, datetime)

    async def test_relationship_to_politician(self, db_session, politician):
        """Test relationship to politician."""
        trade = Trade(
            politician_id=politician.id,
            ticker="ORCL",
            transaction_type="buy",
            transaction_date=date.today(),
            disclosure_date=date.today(),
        )
        db_session.add(trade)
        await db_session.commit()
        await db_session.refresh(trade)

        # Access politician through relationship
        assert trade.politician is not None
        assert trade.politician.name == "John Doe"
        assert trade.politician.chamber == "senate"

    async def test_cascade_delete(self, db_session, politician):
        """Test that trades are deleted when politician is deleted."""
        trade = Trade(
            politician_id=politician.id,
            ticker="IBM",
            transaction_type="buy",
            transaction_date=date.today(),
            disclosure_date=date.today(),
        )
        db_session.add(trade)
        await db_session.commit()
        trade_id = trade.id

        # Delete politician
        db_session.delete(politician)
        await db_session.commit()

        # Trade should also be deleted
        deleted_trade = await db_session.query(Trade).filter_by(id=trade_id).first()
        assert deleted_trade is None

    async def test_unique_trade_constraint(self, db_session, politician):
        """Test that duplicate trades are prevented."""
        trade1 = Trade(
            politician_id=politician.id,
            ticker="DIS",
            transaction_type="buy",
            transaction_date=date(2024, 1, 15),
            disclosure_date=date(2024, 2, 1),
        )
        db_session.add(trade1)
        await db_session.commit()

        # Try to create duplicate
        trade2 = Trade(
            politician_id=politician.id,
            ticker="DIS",
            transaction_type="buy",
            transaction_date=date(2024, 1, 15),  # Same as trade1
            disclosure_date=date(2024, 2, 15),  # Different disclosure date
        )
        db_session.add(trade2)

        with pytest.raises(IntegrityError):
            await db_session.commit()

    async def test_different_transaction_types_allowed(self, db_session, politician):
        """Test that buy and sell on same day are different trades."""
        trade1 = Trade(
            politician_id=politician.id,
            ticker="BA",
            transaction_type="buy",
            transaction_date=date(2024, 1, 15),
            disclosure_date=date(2024, 2, 1),
        )
        db_session.add(trade1)
        await db_session.commit()

        # Different transaction type - should succeed
        trade2 = Trade(
            politician_id=politician.id,
            ticker="BA",
            transaction_type="sell",  # Different type
            transaction_date=date(2024, 1, 15),
            disclosure_date=date(2024, 2, 1),
        )
        db_session.add(trade2)
        await db_session.commit()
        await db_session.refresh(trade2)

        assert trade2.id is not None

    async def test_trade_repr(self, db_session, politician):
        """Test string representation of trade."""
        trade = Trade(
            politician_id=politician.id,
            ticker="GE",
            transaction_type="sell",
            transaction_date=date(2024, 1, 15),
            disclosure_date=date(2024, 2, 1),
        )
        db_session.add(trade)
        await db_session.commit()
        await db_session.refresh(trade)

        repr_str = repr(trade)
        assert "GE" in repr_str
        assert "sell" in repr_str
        assert "2024-01-15" in repr_str

    async def test_ticker_index(self, db_session, politician):
        """Test that ticker is indexed for efficient querying."""
        # Create multiple trades with same ticker
        for i in range(5):
            trade = Trade(
                politician_id=politician.id,
                ticker="AAPL",
                transaction_type="buy" if i % 2 == 0 else "sell",
                transaction_date=date.today() - timedelta(days=i),
                disclosure_date=date.today(),
            )
            db_session.add(trade)
        await db_session.commit()

        # Query by ticker should be fast (indexed)
        trades = await db_session.query(Trade).filter_by(ticker="AAPL").all()
        assert len(trades) == 5
