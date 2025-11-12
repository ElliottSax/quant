"""Tests for scraper service."""

import pytest
from datetime import date
from decimal import Decimal

from app.services.scraper_service import ScraperService, DataValidationError


class TestScraperService:
    """Tests for ScraperService."""

    def test_validate_trade_data_valid(self):
        """Test validation with valid trade data."""
        service = ScraperService(db=None)  # Don't need DB for validation tests

        data = {
            "politician_name": "John Smith",
            "chamber": "senate",
            "ticker": "AAPL",
            "transaction_type": "buy",
            "transaction_date": date(2024, 1, 15),
            "disclosure_date": date(2024, 1, 20),
            "amount_min": Decimal("1000"),
            "amount_max": Decimal("15000"),
            "source_url": "https://example.com/report",
            "raw_data": {"test": "data"},
        }

        validated = service._validate_trade_data(data)

        assert validated["politician_name"] == "John Smith"
        assert validated["chamber"] == "senate"
        assert validated["ticker"] == "AAPL"
        assert validated["transaction_type"] == "buy"
        assert validated["transaction_date"] == date(2024, 1, 15)
        assert validated["disclosure_date"] == date(2024, 1, 20)
        assert validated["amount_min"] == Decimal("1000")
        assert validated["amount_max"] == Decimal("15000")

    def test_validate_trade_data_normalize_sale_to_sell(self):
        """Test that 'sale' is normalized to 'sell'."""
        service = ScraperService(db=None)

        data = {
            "politician_name": "Jane Doe",
            "chamber": "house",
            "ticker": "TSLA",
            "transaction_type": "sale",  # Should be normalized to 'sell'
            "transaction_date": date(2024, 1, 15),
            "disclosure_date": date(2024, 1, 20),
        }

        validated = service._validate_trade_data(data)
        assert validated["transaction_type"] == "sell"

    def test_validate_trade_data_missing_required_field(self):
        """Test validation fails with missing required field."""
        service = ScraperService(db=None)

        data = {
            "politician_name": "John Smith",
            "chamber": "senate",
            # Missing ticker
            "transaction_type": "buy",
            "transaction_date": date(2024, 1, 15),
            "disclosure_date": date(2024, 1, 20),
        }

        with pytest.raises(DataValidationError, match="Missing required field: ticker"):
            service._validate_trade_data(data)

    def test_validate_trade_data_invalid_chamber(self):
        """Test validation fails with invalid chamber."""
        service = ScraperService(db=None)

        data = {
            "politician_name": "John Smith",
            "chamber": "invalid",  # Invalid chamber
            "ticker": "AAPL",
            "transaction_type": "buy",
            "transaction_date": date(2024, 1, 15),
            "disclosure_date": date(2024, 1, 20),
        }

        with pytest.raises(DataValidationError, match="Invalid chamber"):
            service._validate_trade_data(data)

    def test_validate_trade_data_invalid_transaction_type(self):
        """Test validation fails with invalid transaction type."""
        service = ScraperService(db=None)

        data = {
            "politician_name": "John Smith",
            "chamber": "senate",
            "ticker": "AAPL",
            "transaction_type": "invalid",  # Invalid type
            "transaction_date": date(2024, 1, 15),
            "disclosure_date": date(2024, 1, 20),
        }

        with pytest.raises(DataValidationError, match="Invalid transaction type"):
            service._validate_trade_data(data)

    def test_validate_trade_data_disclosure_before_transaction(self):
        """Test validation fails when disclosure date is before transaction date."""
        service = ScraperService(db=None)

        data = {
            "politician_name": "John Smith",
            "chamber": "senate",
            "ticker": "AAPL",
            "transaction_type": "buy",
            "transaction_date": date(2024, 1, 20),
            "disclosure_date": date(2024, 1, 15),  # Before transaction
        }

        with pytest.raises(DataValidationError, match="Disclosure date must be on or after transaction date"):
            service._validate_trade_data(data)

    def test_validate_trade_data_amount_min_greater_than_max(self):
        """Test validation fails when amount_min > amount_max."""
        service = ScraperService(db=None)

        data = {
            "politician_name": "John Smith",
            "chamber": "senate",
            "ticker": "AAPL",
            "transaction_type": "buy",
            "transaction_date": date(2024, 1, 15),
            "disclosure_date": date(2024, 1, 20),
            "amount_min": Decimal("15000"),
            "amount_max": Decimal("1000"),  # Less than min
        }

        with pytest.raises(DataValidationError, match="amount_min cannot be greater than amount_max"):
            service._validate_trade_data(data)

    def test_validate_trade_data_negative_amount(self):
        """Test validation fails with negative amount."""
        service = ScraperService(db=None)

        data = {
            "politician_name": "John Smith",
            "chamber": "senate",
            "ticker": "AAPL",
            "transaction_type": "buy",
            "transaction_date": date(2024, 1, 15),
            "disclosure_date": date(2024, 1, 20),
            "amount_min": Decimal("-1000"),  # Negative
        }

        with pytest.raises(DataValidationError, match="amount_min cannot be negative"):
            service._validate_trade_data(data)

    def test_validate_trade_data_ticker_normalization(self):
        """Test ticker is normalized to uppercase."""
        service = ScraperService(db=None)

        data = {
            "politician_name": "John Smith",
            "chamber": "senate",
            "ticker": "aapl",  # Lowercase
            "transaction_type": "buy",
            "transaction_date": date(2024, 1, 15),
            "disclosure_date": date(2024, 1, 20),
        }

        validated = service._validate_trade_data(data)
        assert validated["ticker"] == "AAPL"  # Should be uppercase
