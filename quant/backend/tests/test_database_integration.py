"""Tests for database integration with scrapers."""

import pytest
from datetime import date
from decimal import Decimal
from sqlalchemy import select

from app.models.politician import Politician
from app.models.trade import Trade
from app.services.scraper_service import ScraperService, DataValidationError


@pytest.mark.asyncio
class TestDatabaseIntegration:
    """Tests for database operations."""

    async def test_get_or_create_politician_new(self, db_session):
        """Test creating a new politician."""
        service = ScraperService(db_session)

        politician = await service._get_or_create_politician(
            name="John Smith",
            chamber="senate",
        )

        assert politician.name == "John Smith"
        assert politician.chamber == "senate"
        assert politician.id is not None

    async def test_get_or_create_politician_existing(self, db_session):
        """Test retrieving existing politician."""
        service = ScraperService(db_session)

        # Create first time
        politician1 = await service._get_or_create_politician(
            name="Jane Doe",
            chamber="house",
        )
        politician1_id = politician1.id

        # Get second time
        politician2 = await service._get_or_create_politician(
            name="Jane Doe",
            chamber="house",
        )

        assert politician2.id == politician1_id
        assert politician2.name == "Jane Doe"

    async def test_save_trades_single(self, db_session):
        """Test saving a single trade."""
        service = ScraperService(db_session)

        trades_data = [
            {
                "politician_name": "Bob Johnson",
                "chamber": "senate",
                "ticker": "AAPL",
                "transaction_type": "buy",
                "amount_min": Decimal("1001"),
                "amount_max": Decimal("15000"),
                "transaction_date": date(2024, 1, 15),
                "disclosure_date": date(2024, 1, 20),
                "source_url": "https://example.com/report1",
                "raw_data": {"test": "data"},
            }
        ]

        stats = await service.save_trades(trades_data)

        assert stats["total"] == 1
        assert stats["saved"] == 1
        assert stats["skipped"] == 0
        assert stats["errors"] == 0

        # Verify trade was saved
        result = await db_session.execute(select(Trade))
        trades = result.scalars().all()
        assert len(trades) == 1
        assert trades[0].ticker == "AAPL"

    async def test_save_trades_multiple(self, db_session):
        """Test saving multiple trades."""
        service = ScraperService(db_session)

        trades_data = [
            {
                "politician_name": "Alice Williams",
                "chamber": "house",
                "ticker": "MSFT",
                "transaction_type": "buy",
                "transaction_date": date(2024, 1, 10),
                "disclosure_date": date(2024, 1, 15),
            },
            {
                "politician_name": "Alice Williams",
                "chamber": "house",
                "ticker": "GOOGL",
                "transaction_type": "sell",
                "transaction_date": date(2024, 1, 12),
                "disclosure_date": date(2024, 1, 17),
            },
            {
                "politician_name": "Bob Miller",
                "chamber": "senate",
                "ticker": "TSLA",
                "transaction_type": "buy",
                "transaction_date": date(2024, 1, 14),
                "disclosure_date": date(2024, 1, 19),
            },
        ]

        stats = await service.save_trades(trades_data)

        assert stats["total"] == 3
        assert stats["saved"] == 3
        assert stats["skipped"] == 0
        assert stats["errors"] == 0

        # Verify politicians
        result = await db_session.execute(select(Politician))
        politicians = result.scalars().all()
        assert len(politicians) == 2  # Alice and Bob

        # Verify trades
        result = await db_session.execute(select(Trade))
        trades = result.scalars().all()
        assert len(trades) == 3

    async def test_save_trades_duplicate_skipped(self, db_session):
        """Test that duplicate trades are skipped."""
        service = ScraperService(db_session)

        trade_data = {
            "politician_name": "Charlie Brown",
            "chamber": "senate",
            "ticker": "NVDA",
            "transaction_type": "buy",
            "transaction_date": date(2024, 1, 10),
            "disclosure_date": date(2024, 1, 15),
        }

        # Save first time
        stats1 = await service.save_trades([trade_data])
        assert stats1["saved"] == 1

        # Try to save duplicate
        stats2 = await service.save_trades([trade_data])
        assert stats2["total"] == 1
        assert stats2["saved"] == 0
        assert stats2["skipped"] == 1
        assert stats2["errors"] == 0

        # Verify only one trade exists
        result = await db_session.execute(select(Trade))
        trades = result.scalars().all()
        assert len(trades) == 1

    async def test_save_trades_validation_error(self, db_session):
        """Test that validation errors are counted."""
        service = ScraperService(db_session)

        trades_data = [
            {
                "politician_name": "Valid Politician",
                "chamber": "senate",
                "ticker": "AAPL",
                "transaction_type": "buy",
                "transaction_date": date(2024, 1, 10),
                "disclosure_date": date(2024, 1, 15),
            },
            {
                "politician_name": "Invalid Trade",
                "chamber": "invalid_chamber",  # Invalid!
                "ticker": "MSFT",
                "transaction_type": "buy",
                "transaction_date": date(2024, 1, 10),
                "disclosure_date": date(2024, 1, 15),
            },
        ]

        stats = await service.save_trades(trades_data)

        assert stats["total"] == 2
        assert stats["saved"] == 1
        assert stats["errors"] == 1

        # Verify only valid trade was saved
        result = await db_session.execute(select(Trade))
        trades = result.scalars().all()
        assert len(trades) == 1
        assert trades[0].ticker == "AAPL"

    async def test_save_trades_missing_required_field(self, db_session):
        """Test error handling for missing required fields."""
        service = ScraperService(db_session)

        trades_data = [
            {
                "politician_name": "Test Person",
                "chamber": "senate",
                # Missing ticker!
                "transaction_type": "buy",
                "transaction_date": date(2024, 1, 10),
                "disclosure_date": date(2024, 1, 15),
            }
        ]

        stats = await service.save_trades(trades_data)

        assert stats["total"] == 1
        assert stats["saved"] == 0
        assert stats["errors"] == 1

    async def test_scraping_stats(self, db_session):
        """Test get_scraping_stats function."""
        service = ScraperService(db_session)

        # Initially empty
        stats = await service.get_scraping_stats()
        assert stats["total_trades"] == 0
        assert stats["total_politicians"] == 0
        assert stats["latest_scrape"] is None

        # Add some trades
        trades_data = [
            {
                "politician_name": "Stat Test Person",
                "chamber": "senate",
                "ticker": "AAPL",
                "transaction_type": "buy",
                "transaction_date": date(2024, 1, 10),
                "disclosure_date": date(2024, 1, 15),
            }
        ]
        await service.save_trades(trades_data)

        # Check stats
        stats = await service.get_scraping_stats()
        assert stats["total_trades"] == 1
        assert stats["total_politicians"] == 1
        assert stats["latest_scrape"] is not None

    async def test_trade_relationships(self, db_session):
        """Test that trade-politician relationships work correctly."""
        service = ScraperService(db_session)

        # Create trades for same politician
        trades_data = [
            {
                "politician_name": "Relationship Test",
                "chamber": "house",
                "ticker": "AAPL",
                "transaction_type": "buy",
                "transaction_date": date(2024, 1, 10),
                "disclosure_date": date(2024, 1, 15),
            },
            {
                "politician_name": "Relationship Test",
                "chamber": "house",
                "ticker": "MSFT",
                "transaction_type": "sell",
                "transaction_date": date(2024, 1, 12),
                "disclosure_date": date(2024, 1, 17),
            },
        ]

        await service.save_trades(trades_data)

        # Get politician and check trades
        result = await db_session.execute(
            select(Politician).where(Politician.name == "Relationship Test")
        )
        politician = result.scalar_one()

        # Eagerly load trades
        result = await db_session.execute(
            select(Trade).where(Trade.politician_id == politician.id)
        )
        trades = result.scalars().all()

        assert len(trades) == 2
        assert all(trade.politician_id == politician.id for trade in trades)

    async def test_amount_storage_precision(self, db_session):
        """Test that decimal amounts are stored with correct precision."""
        service = ScraperService(db_session)

        trades_data = [
            {
                "politician_name": "Precision Test",
                "chamber": "senate",
                "ticker": "TEST",
                "transaction_type": "buy",
                "amount_min": Decimal("1234.56"),
                "amount_max": Decimal("9876543.21"),
                "transaction_date": date(2024, 1, 10),
                "disclosure_date": date(2024, 1, 15),
            }
        ]

        await service.save_trades(trades_data)

        result = await db_session.execute(select(Trade))
        trade = result.scalar_one()

        assert trade.amount_min == Decimal("1234.56")
        assert trade.amount_max == Decimal("9876543.21")
