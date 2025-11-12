"""Senate financial disclosure scraper."""

import logging
import re
from datetime import date, datetime
from decimal import Decimal
from typing import Any

from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException

from app.scrapers.base import BaseScraper, NavigationException, ParsingException

logger = logging.getLogger(__name__)


class SenateScraper(BaseScraper):
    """Scraper for Senate financial disclosures from efdsearch.senate.gov."""

    BASE_URL = "https://efdsearch.senate.gov/search/"
    AGREEMENT_URL = "https://efdsearch.senate.gov/search/home/"

    # Amount range patterns from Senate disclosure forms
    AMOUNT_RANGES = {
        "$1,001 - $15,000": (1001, 15000),
        "$15,001 - $50,000": (15001, 50000),
        "$50,001 - $100,000": (50001, 100000),
        "$100,001 - $250,000": (100001, 250000),
        "$250,001 - $500,000": (250001, 500000),
        "$500,001 - $1,000,000": (500001, 1000000),
        "$1,000,001 - $5,000,000": (1000001, 5000000),
        "$5,000,001 - $25,000,000": (5000001, 25000000),
        "$25,000,001 - $50,000,000": (25000001, 50000000),
        "Over $50,000,000": (50000001, None),
    }

    def __init__(
        self,
        start_date: date | None = None,
        end_date: date | None = None,
        **kwargs,
    ):
        """
        Initialize Senate scraper.

        Args:
            start_date: Start date for trade search (defaults to 30 days ago)
            end_date: End date for trade search (defaults to today)
            **kwargs: Additional arguments passed to BaseScraper
        """
        super().__init__(**kwargs)
        self.start_date = start_date
        self.end_date = end_date or date.today()

    def scrape(self) -> list[dict[str, Any]]:
        """
        Main scraping workflow for Senate disclosures.

        Returns:
            List of trade data dictionaries

        Raises:
            NavigationException: If navigation fails
            ParsingException: If data extraction fails
        """
        # Navigate to search page
        self._retry_on_failure(self._navigate_to_source)

        # Accept agreement if present
        self._retry_on_failure(self._accept_agreement)

        # Perform search for PTR filings
        self._retry_on_failure(self._search_ptr_filings)

        # Extract trade data
        trades = self._retry_on_failure(self._extract_data)

        return trades

    def _navigate_to_source(self) -> None:
        """Navigate to Senate EFD search page."""
        try:
            logger.info(f"Navigating to {self.AGREEMENT_URL}")
            self.driver.get(self.AGREEMENT_URL)

            # Wait for page to load
            self.wait.until(
                EC.presence_of_element_located((By.TAG_NAME, "body"))
            )

            logger.info("Successfully navigated to Senate EFD search")

        except Exception as e:
            logger.error(f"Navigation failed: {e}", exc_info=True)
            raise NavigationException(f"Failed to navigate to Senate website: {e}")

    def _accept_agreement(self) -> None:
        """Accept the agreement dialog if present."""
        try:
            # Look for agreement button
            logger.info("Checking for agreement dialog...")

            try:
                # Try to find "I agree" or similar button
                agree_button = self.wait.until(
                    EC.element_to_be_clickable(
                        (By.XPATH, "//button[contains(text(), 'agree') or contains(text(), 'Agree')]")
                    )
                )
                agree_button.click()
                logger.info("Agreement accepted successfully")

            except TimeoutException:
                # Agreement might not be present or already accepted
                logger.info("No agreement dialog found - proceeding")

        except Exception as e:
            logger.warning(f"Error handling agreement: {e}")
            # Don't fail on agreement issues - it might not always be present

    def _search_ptr_filings(self) -> None:
        """
        Search for Periodic Transaction Report (PTR) filings.

        PTR forms contain individual stock transactions.
        """
        try:
            logger.info("Searching for PTR filings...")

            # Wait for search form to be ready
            self.wait.until(
                EC.presence_of_element_located((By.ID, "reportTypes"))
            )

            # Select PTR report type
            report_type_dropdown = self.driver.find_element(By.ID, "reportTypes")
            # Click to open dropdown
            report_type_dropdown.click()

            # Select PTR option
            ptr_option = self.wait.until(
                EC.element_to_be_clickable(
                    (By.XPATH, "//option[@value='11' or contains(text(), 'Periodic Transaction Report')]")
                )
            )
            ptr_option.click()

            # Set date range if provided
            if self.start_date:
                start_date_input = self.driver.find_element(By.ID, "fromDate")
                start_date_input.clear()
                start_date_input.send_keys(self.start_date.strftime("%m/%d/%Y"))

            if self.end_date:
                end_date_input = self.driver.find_element(By.ID, "toDate")
                end_date_input.clear()
                end_date_input.send_keys(self.end_date.strftime("%m/%d/%Y"))

            # Submit search
            search_button = self.driver.find_element(
                By.XPATH, "//button[@type='submit' or contains(text(), 'Search')]"
            )
            search_button.click()

            # Wait for results
            self.wait.until(
                EC.presence_of_element_located((By.CLASS_NAME, "table"))
            )

            logger.info("Search completed successfully")

        except NoSuchElementException as e:
            logger.error(f"Could not find search form elements: {e}")
            raise NavigationException(f"Search form not found: {e}")
        except TimeoutException as e:
            logger.error(f"Timeout waiting for search results: {e}")
            raise NavigationException(f"Search timed out: {e}")

    def _extract_data(self) -> list[dict[str, Any]]:
        """
        Extract trade data from search results.

        Returns:
            List of trade dictionaries with politician and transaction info
        """
        trades = []

        try:
            # Find all result rows
            results_table = self.driver.find_element(By.CLASS_NAME, "table")
            rows = results_table.find_elements(By.TAG_NAME, "tr")[1:]  # Skip header

            logger.info(f"Found {len(rows)} PTR filings to process")

            for idx, row in enumerate(rows, 1):
                try:
                    # Extract basic filing info
                    cells = row.find_elements(By.TAG_NAME, "td")

                    if len(cells) < 4:
                        logger.warning(f"Row {idx} has insufficient cells, skipping")
                        continue

                    politician_name = cells[0].text.strip()
                    filing_date_str = cells[2].text.strip()

                    # Find link to detailed report
                    try:
                        report_link = row.find_element(By.TAG_NAME, "a")
                        report_url = report_link.get_attribute("href")
                    except NoSuchElementException:
                        logger.warning(f"No report link found for row {idx}")
                        continue

                    logger.info(f"Processing filing {idx}/{len(rows)} for {politician_name}")

                    # Navigate to detailed report
                    self.driver.get(report_url)
                    self.wait.until(
                        EC.presence_of_element_located((By.TAG_NAME, "body"))
                    )

                    # Extract transactions from detail page
                    filing_trades = self._extract_transactions_from_report(
                        politician_name=politician_name,
                        filing_date_str=filing_date_str,
                        source_url=report_url,
                    )

                    trades.extend(filing_trades)
                    logger.info(f"Extracted {len(filing_trades)} transactions from filing")

                    # Navigate back to results
                    self.driver.back()
                    self.wait.until(
                        EC.presence_of_element_located((By.CLASS_NAME, "table"))
                    )

                except Exception as e:
                    logger.error(f"Error processing row {idx}: {e}", exc_info=True)
                    continue

            logger.info(f"Extraction complete. Total trades: {len(trades)}")
            return trades

        except NoSuchElementException as e:
            logger.error(f"Could not find results table: {e}")
            raise ParsingException(f"Results table not found: {e}")
        except Exception as e:
            logger.error(f"Extraction failed: {e}", exc_info=True)
            raise ParsingException(f"Data extraction failed: {e}")

    def _extract_transactions_from_report(
        self,
        politician_name: str,
        filing_date_str: str,
        source_url: str,
    ) -> list[dict[str, Any]]:
        """
        Extract individual transactions from a PTR detail page.

        Args:
            politician_name: Name of the politician
            filing_date_str: Date the report was filed
            source_url: URL of the report

        Returns:
            List of transaction dictionaries
        """
        transactions = []

        try:
            # Parse filing date
            filing_date = self._parse_date(filing_date_str)

            # Look for transaction table
            # Senate PTR forms typically have a table with transaction details
            try:
                transaction_rows = self.driver.find_elements(
                    By.XPATH, "//table[@class='transaction-table']//tr | //table[contains(@id, 'transaction')]//tr"
                )

                if not transaction_rows:
                    logger.warning("No transaction table found in report")
                    return transactions

                # Skip header row
                for row in transaction_rows[1:]:
                    try:
                        cells = row.find_elements(By.TAG_NAME, "td")

                        if len(cells) < 5:
                            continue

                        # Extract transaction details
                        # Format may vary, but typical columns are:
                        # [Transaction Date, Asset, Type, Amount, Comment]
                        transaction_date_str = cells[0].text.strip()
                        ticker_raw = cells[1].text.strip()
                        transaction_type_raw = cells[2].text.strip()
                        amount_range_str = cells[3].text.strip()

                        # Clean and validate data
                        ticker = self._clean_ticker(ticker_raw)
                        if not ticker:
                            logger.debug(f"Skipping transaction with invalid ticker: {ticker_raw}")
                            continue

                        transaction_type = self._parse_transaction_type(transaction_type_raw)
                        if not transaction_type:
                            logger.debug(f"Skipping transaction with invalid type: {transaction_type_raw}")
                            continue

                        transaction_date = self._parse_date(transaction_date_str)
                        if not transaction_date:
                            logger.warning(f"Could not parse transaction date: {transaction_date_str}")
                            continue

                        amount_min, amount_max = self._parse_amount_range(amount_range_str)

                        # Create transaction record
                        transaction = {
                            "politician_name": politician_name,
                            "chamber": "senate",
                            "ticker": ticker,
                            "transaction_type": transaction_type,
                            "amount_min": amount_min,
                            "amount_max": amount_max,
                            "transaction_date": transaction_date,
                            "disclosure_date": filing_date,
                            "source_url": source_url,
                            "raw_data": {
                                "ticker_raw": ticker_raw,
                                "transaction_type_raw": transaction_type_raw,
                                "amount_range_str": amount_range_str,
                                "filing_date_str": filing_date_str,
                                "transaction_date_str": transaction_date_str,
                            },
                        }

                        transactions.append(transaction)

                    except Exception as e:
                        logger.warning(f"Error parsing transaction row: {e}")
                        continue

            except NoSuchElementException:
                logger.warning("Transaction table structure not found")

        except Exception as e:
            logger.error(f"Error extracting transactions from report: {e}", exc_info=True)

        return transactions

    def _clean_ticker(self, ticker_raw: str) -> str | None:
        """
        Clean and validate ticker symbol.

        Args:
            ticker_raw: Raw ticker string from form

        Returns:
            Cleaned ticker symbol or None if invalid
        """
        if not ticker_raw:
            return None

        # Remove common prefixes/suffixes
        ticker = ticker_raw.upper().strip()

        # Remove parenthetical descriptions
        ticker = re.sub(r'\([^)]*\)', '', ticker).strip()

        # Extract ticker if format is "TICKER - Company Name"
        if ' - ' in ticker:
            ticker = ticker.split(' - ')[0].strip()

        # Validate ticker format (1-5 alphanumeric characters, dots, or hyphens)
        if not re.match(r'^[A-Z0-9.\-]{1,10}$', ticker):
            return None

        return ticker

    def _parse_transaction_type(self, type_raw: str) -> str | None:
        """
        Parse transaction type from raw string.

        Args:
            type_raw: Raw transaction type string

        Returns:
            'buy' or 'sell', or None if invalid
        """
        if not type_raw:
            return None

        type_lower = type_raw.lower().strip()

        if 'purchase' in type_lower or 'buy' in type_lower:
            return 'buy'
        elif 'sale' in type_lower or 'sell' in type_lower:
            return 'sale'

        return None

    def _parse_amount_range(self, amount_str: str) -> tuple[Decimal | None, Decimal | None]:
        """
        Parse amount range from string.

        Args:
            amount_str: Amount range string (e.g., "$1,001 - $15,000")

        Returns:
            Tuple of (min_amount, max_amount)
        """
        if not amount_str:
            return (None, None)

        # Check known ranges
        for range_key, (min_val, max_val) in self.AMOUNT_RANGES.items():
            if range_key in amount_str:
                return (
                    Decimal(str(min_val)) if min_val else None,
                    Decimal(str(max_val)) if max_val else None,
                )

        # Try to extract numbers
        try:
            numbers = re.findall(r'[\d,]+', amount_str)
            if len(numbers) >= 2:
                min_val = Decimal(numbers[0].replace(',', ''))
                max_val = Decimal(numbers[1].replace(',', ''))
                return (min_val, max_val)
            elif len(numbers) == 1:
                val = Decimal(numbers[0].replace(',', ''))
                return (val, val)
        except Exception as e:
            logger.warning(f"Could not parse amount range '{amount_str}': {e}")

        return (None, None)

    def _parse_date(self, date_str: str) -> date | None:
        """
        Parse date from various string formats.

        Args:
            date_str: Date string

        Returns:
            date object or None if parsing fails
        """
        if not date_str:
            return None

        date_str = date_str.strip()

        # Try common date formats
        formats = [
            "%m/%d/%Y",
            "%m-%d-%Y",
            "%Y-%m-%d",
            "%B %d, %Y",
            "%b %d, %Y",
        ]

        for fmt in formats:
            try:
                return datetime.strptime(date_str, fmt).date()
            except ValueError:
                continue

        logger.warning(f"Could not parse date: {date_str}")
        return None
