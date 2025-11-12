"""House financial disclosure scraper."""

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


class HouseScraper(BaseScraper):
    """Scraper for House financial disclosures from disclosuresclerk.house.gov."""

    BASE_URL = "https://disclosuresclerk.house.gov/PublicDisclosure/FinancialDisclosure"

    # House uses similar amount ranges to Senate
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
        Initialize House scraper.

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
        Main scraping workflow for House disclosures.

        Returns:
            List of trade data dictionaries

        Raises:
            NavigationException: If navigation fails
            ParsingException: If data extraction fails
        """
        # Navigate to search page
        self._retry_on_failure(self._navigate_to_source)

        # Search for PTR filings
        self._retry_on_failure(self._search_ptr_filings)

        # Extract trade data
        trades = self._retry_on_failure(self._extract_data)

        return trades

    def _navigate_to_source(self) -> None:
        """Navigate to House disclosure search page."""
        try:
            logger.info(f"Navigating to {self.BASE_URL}")
            self.driver.get(self.BASE_URL)

            # Wait for page to load
            self.wait.until(
                EC.presence_of_element_located((By.TAG_NAME, "body"))
            )

            logger.info("Successfully navigated to House disclosure search")

        except Exception as e:
            logger.error(f"Navigation failed: {e}", exc_info=True)
            raise NavigationException(f"Failed to navigate to House website: {e}")

    def _search_ptr_filings(self) -> None:
        """
        Search for Periodic Transaction Reports (PTR).

        House PTRs contain individual stock transactions.
        """
        try:
            logger.info("Searching for PTR filings...")

            # Wait for search interface to load
            # House site structure: typically has dropdowns and date inputs
            self.wait.until(
                EC.presence_of_element_located((By.TAG_NAME, "select"))
            )

            # Try to find and select PTR report type
            # House site may use different selectors than Senate
            try:
                # Look for report type dropdown
                report_type_selects = self.driver.find_elements(By.TAG_NAME, "select")

                for select in report_type_selects:
                    # Check if this is the report type selector
                    options = select.find_elements(By.TAG_NAME, "option")
                    for option in options:
                        option_text = option.text.strip().lower()
                        if "periodic transaction" in option_text or "ptr" in option_text:
                            option.click()
                            logger.info("Selected PTR report type")
                            break

            except NoSuchElementException:
                logger.warning("Could not find PTR option in dropdown")

            # Set date range if provided
            # House typically uses input fields with specific IDs or names
            date_inputs = self.driver.find_elements(By.CSS_SELECTOR, "input[type='text'], input[type='date']")

            for input_field in date_inputs:
                input_name = input_field.get_attribute("name") or ""
                input_id = input_field.get_attribute("id") or ""
                input_name_lower = input_name.lower()
                input_id_lower = input_id.lower()

                # Try to identify start date field
                if ("from" in input_name_lower or "start" in input_name_lower or
                    "from" in input_id_lower or "start" in input_id_lower) and self.start_date:
                    try:
                        input_field.clear()
                        input_field.send_keys(self.start_date.strftime("%m/%d/%Y"))
                        logger.info(f"Set start date to {self.start_date}")
                    except Exception as e:
                        logger.warning(f"Could not set start date: {e}")

                # Try to identify end date field
                elif ("to" in input_name_lower or "end" in input_name_lower or
                      "to" in input_id_lower or "end" in input_id_lower) and self.end_date:
                    try:
                        input_field.clear()
                        input_field.send_keys(self.end_date.strftime("%m/%d/%Y"))
                        logger.info(f"Set end date to {self.end_date}")
                    except Exception as e:
                        logger.warning(f"Could not set end date: {e}")

            # Submit search
            # Look for search/submit button
            search_buttons = self.driver.find_elements(
                By.XPATH,
                "//button[contains(text(), 'Search') or contains(text(), 'Submit')] | "
                "//input[@type='submit' and (contains(@value, 'Search') or contains(@value, 'Submit'))]"
            )

            if search_buttons:
                search_buttons[0].click()
                logger.info("Submitted search form")

                # Wait for results to load
                self.wait.until(
                    EC.presence_of_element_located((By.TAG_NAME, "table"))
                )
                logger.info("Search results loaded")
            else:
                logger.warning("Could not find search button")
                raise NavigationException("Search button not found")

        except TimeoutException as e:
            logger.error(f"Timeout waiting for search results: {e}")
            raise NavigationException(f"Search timed out: {e}")
        except Exception as e:
            logger.error(f"Search failed: {e}", exc_info=True)
            raise NavigationException(f"Failed to search PTR filings: {e}")

    def _extract_data(self) -> list[dict[str, Any]]:
        """
        Extract trade data from search results.

        Returns:
            List of trade dictionaries with politician and transaction info
        """
        trades = []

        try:
            # Find results table
            tables = self.driver.find_elements(By.TAG_NAME, "table")

            if not tables:
                logger.warning("No results table found")
                return trades

            # Use the first table that looks like results
            results_table = tables[0]
            rows = results_table.find_elements(By.TAG_NAME, "tr")[1:]  # Skip header

            logger.info(f"Found {len(rows)} PTR filings to process")

            for idx, row in enumerate(rows, 1):
                try:
                    # Extract basic filing info from row
                    cells = row.find_elements(By.TAG_NAME, "td")

                    if len(cells) < 3:
                        logger.warning(f"Row {idx} has insufficient cells, skipping")
                        continue

                    # House format varies, but typically includes:
                    # [Name, Report Type, Filing Date, ...]
                    politician_name = cells[0].text.strip()
                    filing_date_str = ""

                    # Try to find filing date in various cells
                    for cell in cells:
                        cell_text = cell.text.strip()
                        # Look for date pattern MM/DD/YYYY
                        if re.match(r'\d{1,2}/\d{1,2}/\d{4}', cell_text):
                            filing_date_str = cell_text
                            break

                    # Find link to detailed report
                    try:
                        report_links = row.find_elements(By.TAG_NAME, "a")
                        if not report_links:
                            logger.warning(f"No report link found for row {idx}")
                            continue

                        report_url = report_links[0].get_attribute("href")
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
                        EC.presence_of_element_located((By.TAG_NAME, "table"))
                    )

                except Exception as e:
                    logger.error(f"Error processing row {idx}: {e}", exc_info=True)
                    continue

            logger.info(f"Extraction complete. Total trades: {len(trades)}")
            return trades

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

            # House reports typically have transaction data in tables or structured divs
            # Look for transaction indicators
            transaction_sections = self.driver.find_elements(
                By.XPATH,
                "//div[contains(@class, 'transaction')] | "
                "//table[contains(@class, 'transaction')] | "
                "//tr[contains(., 'Purchase') or contains(., 'Sale')]"
            )

            if not transaction_sections:
                # Try alternative: look for tables with stock symbols
                all_tables = self.driver.find_elements(By.TAG_NAME, "table")
                for table in all_tables:
                    # Check if table contains transaction data
                    table_text = table.text.lower()
                    if any(keyword in table_text for keyword in ['purchase', 'sale', 'buy', 'sell', 'stock', 'ticker']):
                        transaction_sections = table.find_elements(By.TAG_NAME, "tr")
                        break

            if not transaction_sections:
                logger.warning("No transaction data found in report")
                return transactions

            logger.info(f"Found {len(transaction_sections)} potential transaction records")

            # Process each transaction
            for section in transaction_sections:
                try:
                    section_text = section.text

                    # Skip headers
                    if any(header in section_text.lower() for header in ['asset', 'description', 'type', 'amount']):
                        continue

                    # Extract transaction details
                    # House format varies, but typically includes ticker and transaction type

                    # Try to extract from table cells
                    cells = section.find_elements(By.TAG_NAME, "td")

                    if len(cells) >= 4:
                        # Typical format: [Asset/Ticker, Type, Date, Amount]
                        ticker_raw = cells[0].text.strip()
                        transaction_type_raw = cells[1].text.strip()
                        transaction_date_str = cells[2].text.strip() if len(cells) > 2 else filing_date_str
                        amount_range_str = cells[3].text.strip() if len(cells) > 3 else ""
                    else:
                        # Try to parse from combined text
                        # Use regex to extract components
                        ticker_match = re.search(r'\b[A-Z]{1,5}\b', section_text)
                        ticker_raw = ticker_match.group(0) if ticker_match else ""

                        type_match = re.search(r'\b(purchase|sale|buy|sell)\b', section_text, re.IGNORECASE)
                        transaction_type_raw = type_match.group(0) if type_match else ""

                        date_match = re.search(r'\d{1,2}/\d{1,2}/\d{4}', section_text)
                        transaction_date_str = date_match.group(0) if date_match else filing_date_str

                        amount_range_str = ""
                        for range_key in self.AMOUNT_RANGES.keys():
                            if range_key in section_text:
                                amount_range_str = range_key
                                break

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
                        # Use filing date as fallback
                        transaction_date = filing_date
                        if not transaction_date:
                            logger.warning(f"Could not determine transaction date")
                            continue

                    amount_min, amount_max = self._parse_amount_range(amount_range_str)

                    # Create transaction record
                    transaction = {
                        "politician_name": politician_name,
                        "chamber": "house",
                        "ticker": ticker,
                        "transaction_type": transaction_type,
                        "amount_min": amount_min,
                        "amount_max": amount_max,
                        "transaction_date": transaction_date,
                        "disclosure_date": filing_date or transaction_date,
                        "source_url": source_url,
                        "raw_data": {
                            "ticker_raw": ticker_raw,
                            "transaction_type_raw": transaction_type_raw,
                            "amount_range_str": amount_range_str,
                            "filing_date_str": filing_date_str,
                            "transaction_date_str": transaction_date_str,
                            "section_text": section_text,
                        },
                    }

                    transactions.append(transaction)

                except Exception as e:
                    logger.warning(f"Error parsing transaction: {e}")
                    continue

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

        # Remove "Stock" or other common suffixes
        ticker = re.sub(r'\s+(STOCK|COMMON|SHARES?|INC\.?|CORP\.?).*$', '', ticker, flags=re.IGNORECASE).strip()

        # Validate ticker format (1-10 alphanumeric characters, dots, or hyphens)
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
