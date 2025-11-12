"""Comprehensive tests for Senate scraper parsing functions."""

import pytest
from datetime import date
from decimal import Decimal

from app.scrapers.senate import SenateScraper


class TestSenateScraper:
    """Tests for SenateScraper parsing functions."""

    def setup_method(self):
        """Set up test fixtures."""
        self.scraper = SenateScraper()

    def test_clean_ticker_basic(self):
        """Test basic ticker cleaning."""
        assert self.scraper._clean_ticker("AAPL") == "AAPL"
        assert self.scraper._clean_ticker("aapl") == "AAPL"
        assert self.scraper._clean_ticker(" TSLA ") == "TSLA"

    def test_clean_ticker_with_description(self):
        """Test cleaning tickers with company descriptions."""
        assert self.scraper._clean_ticker("AAPL (Apple Inc.)") == "AAPL"
        assert self.scraper._clean_ticker("MSFT - Microsoft Corporation") == "MSFT"
        assert self.scraper._clean_ticker("GOOGL (Alphabet Inc. Class A)") == "GOOGL"

    def test_clean_ticker_complex_symbols(self):
        """Test cleaning complex ticker symbols."""
        assert self.scraper._clean_ticker("BRK.B") == "BRK.B"
        assert self.scraper._clean_ticker("BRK-B") == "BRK-B"
        assert self.scraper._clean_ticker("META") == "META"

    def test_clean_ticker_invalid(self):
        """Test that invalid tickers return None."""
        assert self.scraper._clean_ticker("") is None
        assert self.scraper._clean_ticker("   ") is None
        assert self.scraper._clean_ticker("TOOLONGTICKER123") is None  # > 10 chars
        assert self.scraper._clean_ticker("ABC@#$") is None  # Invalid chars
        # Note: "123" is technically valid per regex, though uncommon
        # Real validation would check against exchange listings

    def test_parse_transaction_type_purchase(self):
        """Test parsing purchase transaction types."""
        assert self.scraper._parse_transaction_type("Purchase") == "buy"
        assert self.scraper._parse_transaction_type("purchase") == "buy"
        assert self.scraper._parse_transaction_type("PURCHASE") == "buy"
        assert self.scraper._parse_transaction_type("Buy") == "buy"
        assert self.scraper._parse_transaction_type("buy") == "buy"

    def test_parse_transaction_type_sale(self):
        """Test parsing sale transaction types."""
        assert self.scraper._parse_transaction_type("Sale") == "sale"
        assert self.scraper._parse_transaction_type("sale") == "sale"
        assert self.scraper._parse_transaction_type("SALE") == "sale"
        assert self.scraper._parse_transaction_type("Sell") == "sale"
        assert self.scraper._parse_transaction_type("sell") == "sale"

    def test_parse_transaction_type_invalid(self):
        """Test parsing invalid transaction types."""
        assert self.scraper._parse_transaction_type("") is None
        assert self.scraper._parse_transaction_type("invalid") is None
        assert self.scraper._parse_transaction_type("exchange") is None

    def test_parse_amount_range_standard_ranges(self):
        """Test parsing standard Senate amount ranges."""
        test_cases = [
            ("$1,001 - $15,000", Decimal("1001"), Decimal("15000")),
            ("$15,001 - $50,000", Decimal("15001"), Decimal("50000")),
            ("$50,001 - $100,000", Decimal("50001"), Decimal("100000")),
            ("$100,001 - $250,000", Decimal("100001"), Decimal("250000")),
            ("$250,001 - $500,000", Decimal("250001"), Decimal("500000")),
            ("$500,001 - $1,000,000", Decimal("500001"), Decimal("1000000")),
            ("$1,000,001 - $5,000,000", Decimal("1000001"), Decimal("5000000")),
            ("$5,000,001 - $25,000,000", Decimal("5000001"), Decimal("25000000")),
            ("$25,000,001 - $50,000,000", Decimal("25000001"), Decimal("50000000")),
        ]

        for amount_str, expected_min, expected_max in test_cases:
            min_val, max_val = self.scraper._parse_amount_range(amount_str)
            assert min_val == expected_min, f"Failed for {amount_str}: min"
            assert max_val == expected_max, f"Failed for {amount_str}: max"

    def test_parse_amount_range_over_50_million(self):
        """Test parsing 'Over $50,000,000' range."""
        min_val, max_val = self.scraper._parse_amount_range("Over $50,000,000")
        assert min_val == Decimal("50000001")
        assert max_val is None

    def test_parse_amount_range_numeric_extraction(self):
        """Test extracting numbers from non-standard formats."""
        min_val, max_val = self.scraper._parse_amount_range("$10,000 to $20,000")
        assert min_val == Decimal("10000")
        assert max_val == Decimal("20000")

        min_val, max_val = self.scraper._parse_amount_range("Between $5,000 and $10,000")
        assert min_val == Decimal("5000")
        assert max_val == Decimal("10000")

    def test_parse_amount_range_single_value(self):
        """Test parsing single value amounts."""
        min_val, max_val = self.scraper._parse_amount_range("$25,000")
        assert min_val == Decimal("25000")
        assert max_val == Decimal("25000")

    def test_parse_amount_range_invalid(self):
        """Test parsing invalid amount ranges."""
        min_val, max_val = self.scraper._parse_amount_range("")
        assert min_val is None
        assert max_val is None

        min_val, max_val = self.scraper._parse_amount_range("No amount specified")
        assert min_val is None
        assert max_val is None

    def test_parse_date_mm_dd_yyyy(self):
        """Test parsing MM/DD/YYYY format."""
        assert self.scraper._parse_date("01/15/2024") == date(2024, 1, 15)
        assert self.scraper._parse_date("12/31/2023") == date(2023, 12, 31)
        assert self.scraper._parse_date("3/5/2024") == date(2024, 3, 5)

    def test_parse_date_mm_dash_dd_dash_yyyy(self):
        """Test parsing MM-DD-YYYY format."""
        assert self.scraper._parse_date("01-15-2024") == date(2024, 1, 15)
        assert self.scraper._parse_date("12-31-2023") == date(2023, 12, 31)

    def test_parse_date_yyyy_mm_dd(self):
        """Test parsing YYYY-MM-DD format."""
        assert self.scraper._parse_date("2024-01-15") == date(2024, 1, 15)
        assert self.scraper._parse_date("2023-12-31") == date(2023, 12, 31)

    def test_parse_date_month_name_formats(self):
        """Test parsing formats with month names."""
        assert self.scraper._parse_date("January 15, 2024") == date(2024, 1, 15)
        assert self.scraper._parse_date("Dec 31, 2023") == date(2023, 12, 31)
        assert self.scraper._parse_date("Feb 29, 2024") == date(2024, 2, 29)  # Leap year

    def test_parse_date_invalid(self):
        """Test parsing invalid dates."""
        assert self.scraper._parse_date("") is None
        assert self.scraper._parse_date("invalid date") is None
        assert self.scraper._parse_date("13/45/2024") is None  # Invalid month/day
        assert self.scraper._parse_date("2024-13-01") is None  # Invalid month

    def test_amount_ranges_dictionary_completeness(self):
        """Test that AMOUNT_RANGES dictionary is complete."""
        assert len(self.scraper.AMOUNT_RANGES) == 10
        assert "$1,001 - $15,000" in self.scraper.AMOUNT_RANGES
        assert "Over $50,000,000" in self.scraper.AMOUNT_RANGES

    def test_scraper_configuration(self):
        """Test scraper configuration options."""
        # Default configuration
        scraper = SenateScraper()
        assert scraper.headless is True
        assert scraper.timeout == 30
        assert scraper.max_retries == 3
        assert scraper.retry_delay == 5

        # Custom configuration
        scraper = SenateScraper(headless=False, timeout=60, max_retries=5, retry_delay=10)
        assert scraper.headless is False
        assert scraper.timeout == 60
        assert scraper.max_retries == 5
        assert scraper.retry_delay == 10

    def test_scraper_base_url(self):
        """Test that base URLs are correctly set."""
        assert self.scraper.BASE_URL == "https://efdsearch.senate.gov/search/"
        assert self.scraper.AGREEMENT_URL == "https://efdsearch.senate.gov/search/home/"

    def test_date_range_configuration(self):
        """Test scraper date range configuration."""
        start = date(2024, 1, 1)
        end = date(2024, 1, 31)

        scraper = SenateScraper(start_date=start, end_date=end)
        assert scraper.start_date == start
        assert scraper.end_date == end

    def test_default_end_date(self):
        """Test that end_date defaults to today."""
        scraper = SenateScraper()
        assert scraper.end_date == date.today()
