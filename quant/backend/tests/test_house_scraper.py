"""Comprehensive tests for House scraper parsing functions."""

import pytest
from datetime import date
from decimal import Decimal

from app.scrapers.house import HouseScraper


class TestHouseScraper:
    """Tests for HouseScraper parsing functions."""

    def setup_method(self):
        """Set up test fixtures."""
        self.scraper = HouseScraper()

    def test_clean_ticker_basic(self):
        """Test basic ticker cleaning."""
        assert self.scraper._clean_ticker("NVDA") == "NVDA"
        assert self.scraper._clean_ticker("nvda") == "NVDA"
        assert self.scraper._clean_ticker(" AMD ") == "AMD"

    def test_clean_ticker_with_company_name(self):
        """Test cleaning tickers with company names."""
        assert self.scraper._clean_ticker("NVDA - NVIDIA Corp") == "NVDA"
        assert self.scraper._clean_ticker("AMD (Advanced Micro Devices)") == "AMD"
        assert self.scraper._clean_ticker("INTC - Intel Corporation") == "INTC"

    def test_clean_ticker_with_stock_suffix(self):
        """Test cleaning tickers with 'Stock' or 'Common' suffixes."""
        assert self.scraper._clean_ticker("AAPL Stock") == "AAPL"
        assert self.scraper._clean_ticker("MSFT Common") == "MSFT"
        assert self.scraper._clean_ticker("TSLA Common Shares") == "TSLA"
        assert self.scraper._clean_ticker("META Inc.") == "META"
        assert self.scraper._clean_ticker("GOOGL Corp.") == "GOOGL"

    def test_clean_ticker_complex(self):
        """Test cleaning complex ticker formats."""
        assert self.scraper._clean_ticker("BRK.B") == "BRK.B"
        assert self.scraper._clean_ticker("BRK-B") == "BRK-B"
        assert self.scraper._clean_ticker("SPY") == "SPY"

    def test_clean_ticker_invalid(self):
        """Test that invalid tickers return None."""
        assert self.scraper._clean_ticker("") is None
        assert self.scraper._clean_ticker("   ") is None
        assert self.scraper._clean_ticker("WAYTOOLONGTICKER") is None  # > 10 chars
        assert self.scraper._clean_ticker("ABC@#$%") is None  # Invalid characters
        # Note: Short numeric strings are technically valid per regex
        # Real validation would check against exchange listings

    def test_parse_transaction_type_purchase(self):
        """Test parsing purchase types."""
        assert self.scraper._parse_transaction_type("Purchase") == "buy"
        assert self.scraper._parse_transaction_type("purchase") == "buy"
        assert self.scraper._parse_transaction_type("PURCHASE") == "buy"
        assert self.scraper._parse_transaction_type("Buy") == "buy"

    def test_parse_transaction_type_sale(self):
        """Test parsing sale types."""
        assert self.scraper._parse_transaction_type("Sale") == "sale"
        assert self.scraper._parse_transaction_type("sale") == "sale"
        assert self.scraper._parse_transaction_type("SALE") == "sale"
        assert self.scraper._parse_transaction_type("Sell") == "sale"

    def test_parse_transaction_type_invalid(self):
        """Test invalid transaction types."""
        assert self.scraper._parse_transaction_type("") is None
        assert self.scraper._parse_transaction_type("unknown") is None
        assert self.scraper._parse_transaction_type("transfer") is None

    def test_parse_amount_range_standard(self):
        """Test parsing standard House amount ranges."""
        test_cases = [
            ("$1,001 - $15,000", Decimal("1001"), Decimal("15000")),
            ("$15,001 - $50,000", Decimal("15001"), Decimal("50000")),
            ("$100,001 - $250,000", Decimal("100001"), Decimal("250000")),
            ("$1,000,001 - $5,000,000", Decimal("1000001"), Decimal("5000000")),
        ]

        for amount_str, expected_min, expected_max in test_cases:
            min_val, max_val = self.scraper._parse_amount_range(amount_str)
            assert min_val == expected_min
            assert max_val == expected_max

    def test_parse_amount_range_over_50_million(self):
        """Test parsing amounts over $50 million."""
        min_val, max_val = self.scraper._parse_amount_range("Over $50,000,000")
        assert min_val == Decimal("50000001")
        assert max_val is None

    def test_parse_amount_range_extraction(self):
        """Test extracting amounts from various formats."""
        min_val, max_val = self.scraper._parse_amount_range("$25,000 to $35,000")
        assert min_val == Decimal("25000")
        assert max_val == Decimal("35000")

    def test_parse_amount_range_invalid(self):
        """Test invalid amount ranges."""
        min_val, max_val = self.scraper._parse_amount_range("")
        assert min_val is None
        assert max_val is None

    def test_parse_date_various_formats(self):
        """Test parsing dates in various formats."""
        assert self.scraper._parse_date("02/14/2024") == date(2024, 2, 14)
        assert self.scraper._parse_date("2024-02-14") == date(2024, 2, 14)
        assert self.scraper._parse_date("February 14, 2024") == date(2024, 2, 14)
        assert self.scraper._parse_date("Feb 14, 2024") == date(2024, 2, 14)

    def test_parse_date_invalid(self):
        """Test parsing invalid dates."""
        assert self.scraper._parse_date("") is None
        assert self.scraper._parse_date("not a date") is None
        assert self.scraper._parse_date("99/99/9999") is None

    def test_amount_ranges_match_senate(self):
        """Test that House and Senate use same amount ranges."""
        from app.scrapers.senate import SenateScraper
        senate_scraper = SenateScraper()

        assert len(self.scraper.AMOUNT_RANGES) == len(senate_scraper.AMOUNT_RANGES)
        assert self.scraper.AMOUNT_RANGES == senate_scraper.AMOUNT_RANGES

    def test_scraper_configuration(self):
        """Test scraper configuration."""
        scraper = HouseScraper(headless=False, timeout=45, max_retries=4)
        assert scraper.headless is False
        assert scraper.timeout == 45
        assert scraper.max_retries == 4

    def test_base_url(self):
        """Test that base URL is correct."""
        expected_url = "https://disclosuresclerk.house.gov/PublicDisclosure/FinancialDisclosure"
        assert self.scraper.BASE_URL == expected_url

    def test_date_range_config(self):
        """Test date range configuration."""
        start = date(2024, 2, 1)
        end = date(2024, 2, 28)

        scraper = HouseScraper(start_date=start, end_date=end)
        assert scraper.start_date == start
        assert scraper.end_date == end

    def test_default_end_date(self):
        """Test default end date is today."""
        scraper = HouseScraper()
        assert scraper.end_date == date.today()
