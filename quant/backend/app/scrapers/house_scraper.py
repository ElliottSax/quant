"""
House Trading Data Scraper

Scrapes financial disclosure forms from disclosures.house.gov
Extracts: politician name, ticker, transaction type, amount range, date
"""

import re
import logging
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from decimal import Decimal

import httpx
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

logger = logging.getLogger(__name__)


class HouseScraper:
    """Scraper for House financial disclosures."""

    BASE_URL = "https://disclosures-clerk.house.gov"
    SEARCH_URL = f"{BASE_URL}/PublicDisclosure/FinancialDisclosure"

    def __init__(self, headless: bool = True, rate_limit_delay: float = 2.0):
        """
        Initialize House scraper.

        Args:
            headless: Run browser in headless mode
            rate_limit_delay: Delay between requests in seconds
        """
        self.headless = headless
        self.rate_limit_delay = rate_limit_delay
        self.driver: Optional[webdriver.Chrome] = None

    def _init_driver(self) -> webdriver.Chrome:
        """Initialize Selenium WebDriver."""
        chrome_options = Options()
        if self.headless:
            chrome_options.add_argument("--headless")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument(
            "user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        )

        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=chrome_options)
        return driver

    def __enter__(self):
        """Context manager entry."""
        self.driver = self._init_driver()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        if self.driver:
            self.driver.quit()
            self.driver = None

    def scrape_recent_transactions(
        self, days_back: int = 7
    ) -> List[Dict]:
        """
        Scrape recent House transactions.

        Args:
            days_back: Number of days to look back

        Returns:
            List of transaction dictionaries
        """
        if not self.driver:
            raise RuntimeError("Driver not initialized. Use context manager.")

        transactions = []
        start_date = datetime.now() - timedelta(days=days_back)
        end_date = datetime.now()

        try:
            logger.info(f"Scraping House transactions from {start_date.date()} to {end_date.date()}")

            # Navigate to search page
            self.driver.get(self.SEARCH_URL)
            time.sleep(2)  # Wait for page load

            # Wait for search form
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.ID, "ReportType"))
            )

            # Select Periodic Transaction Report
            report_type = self.driver.find_element(By.ID, "ReportType")
            for option in report_type.find_elements(By.TAG_NAME, "option"):
                if "Periodic Transaction" in option.text:
                    option.click()
                    break

            # Fill in year
            year_input = self.driver.find_element(By.ID, "Year")
            year_input.clear()
            year_input.send_keys(str(datetime.now().year))

            # Submit search
            search_button = self.driver.find_element(By.CSS_SELECTOR, "input[type='submit']")
            search_button.click()

            # Wait for results
            time.sleep(3)
            WebDriverWait(self.driver, 15).until(
                EC.presence_of_element_located((By.TAG_NAME, "table"))
            )

            # Parse results
            soup = BeautifulSoup(self.driver.page_source, "html.parser")
            transactions = self._parse_search_results(soup, start_date)

            logger.info(f"Scraped {len(transactions)} House transactions")

        except Exception as e:
            logger.error(f"Error scraping House data: {e}")
            raise

        return transactions

    def _parse_search_results(
        self, soup: BeautifulSoup, start_date: datetime
    ) -> List[Dict]:
        """
        Parse search results page.

        Args:
            soup: BeautifulSoup object of results page
            start_date: Filter results after this date

        Returns:
            List of transaction dictionaries
        """
        transactions = []

        # Find results table
        table = soup.find("table", {"id": "filedReports"})
        if not table:
            logger.warning("No results table found")
            return transactions

        # Parse each row
        rows = table.find_all("tr")[1:]  # Skip header row

        for row in rows:
            try:
                cells = row.find_all("td")
                if len(cells) < 5:
                    continue

                # Extract basic info
                politician_name = cells[0].get_text(strip=True)
                filing_date_str = cells[2].get_text(strip=True)

                # Parse filing date
                try:
                    filing_date = datetime.strptime(filing_date_str, "%m/%d/%Y")
                except:
                    continue

                # Filter by date
                if filing_date < start_date:
                    continue

                # Find report link
                link_cell = cells[4].find("a")
                if not link_cell:
                    continue

                report_url = link_cell.get("href", "")
                if not report_url.startswith("http"):
                    report_url = self.BASE_URL + report_url

                # Scrape individual report
                report_transactions = self._scrape_report(
                    report_url, politician_name, filing_date.date()
                )
                transactions.extend(report_transactions)

                # Rate limiting
                time.sleep(self.rate_limit_delay)

            except Exception as e:
                logger.warning(f"Error parsing row: {e}")
                continue

        return transactions

    def _scrape_report(
        self, report_url: str, politician_name: str, filing_date
    ) -> List[Dict]:
        """
        Scrape individual report for transactions.

        Args:
            report_url: URL of the report PDF or HTML
            politician_name: Name of politician
            filing_date: Date of filing

        Returns:
            List of transactions from this report
        """
        transactions = []

        try:
            # Navigate to report
            self.driver.get(report_url)
            time.sleep(2)

            soup = BeautifulSoup(self.driver.page_source, "html.parser")

            # Check if it's a PDF link
            if report_url.endswith('.pdf'):
                logger.info(f"Skipping PDF report: {report_url}")
                # TODO: Implement PDF parsing with PyPDF2 or similar
                return transactions

            # Parse HTML report
            # Look for transaction tables
            tables = soup.find_all("table")

            for table in tables:
                # Check if this is a transaction table
                headers = [th.get_text(strip=True).lower() for th in table.find_all("th")]

                if not any("asset" in h or "ticker" in h or "security" in h for h in headers):
                    continue

                # Parse transaction rows
                rows = table.find_all("tr")[1:]  # Skip header

                for row in rows:
                    try:
                        transaction = self._parse_transaction_row(
                            row, politician_name, filing_date, report_url
                        )
                        if transaction:
                            transactions.append(transaction)
                    except Exception as e:
                        logger.warning(f"Error parsing transaction row: {e}")
                        continue

        except Exception as e:
            logger.error(f"Error scraping report {report_url}: {e}")

        return transactions

    def _parse_transaction_row(
        self, row, politician_name: str, filing_date, source_url: str
    ) -> Optional[Dict]:
        """
        Parse a transaction row.

        Args:
            row: BeautifulSoup row element
            politician_name: Name of politician
            filing_date: Date of filing
            source_url: Source URL

        Returns:
            Transaction dictionary or None
        """
        cells = row.find_all("td")
        if len(cells) < 3:
            return None

        # Extract fields
        ticker = self._extract_ticker(cells)
        if not ticker:
            return None

        transaction_type = self._extract_transaction_type(cells)
        if not transaction_type:
            return None

        amount_min, amount_max = self._extract_amount_range(cells)
        transaction_date = self._extract_date(cells) or filing_date

        return {
            "politician_name": politician_name,
            "chamber": "house",
            "ticker": ticker,
            "transaction_type": transaction_type,
            "amount_min": amount_min,
            "amount_max": amount_max,
            "transaction_date": transaction_date,
            "disclosure_date": filing_date,
            "source_url": source_url,
            "raw_data": {
                "cells": [cell.get_text(strip=True) for cell in cells]
            }
        }

    def _extract_ticker(self, cells) -> Optional[str]:
        """Extract ticker symbol from cells."""
        for cell in cells:
            text = cell.get_text(strip=True).upper()

            # Look for explicit ticker in parentheses: "Apple Inc (AAPL)"
            match = re.search(r'\(([A-Z]{1,5})\)', text)
            if match:
                return match.group(1)

            # Look for standalone ticker pattern
            match = re.search(r'\b([A-Z]{1,5})\b', text)
            if match:
                ticker = match.group(1)
                # Filter out common false positives
                if ticker not in ["PTR", "DATE", "TYPE", "SALE", "BUY", "LLC", "INC", "LTD"]:
                    return ticker

        return None

    def _extract_transaction_type(self, cells) -> Optional[str]:
        """Extract transaction type (buy/sell)."""
        for cell in cells:
            text = cell.get_text(strip=True).lower()
            if "purchase" in text or "bought" in text or "buy" in text:
                return "buy"
            elif "sale" in text or "sold" in text or "sell" in text:
                return "sell"
        return None

    def _extract_amount_range(self, cells) -> Tuple[Optional[Decimal], Optional[Decimal]]:
        """Extract amount range."""
        for cell in cells:
            text = cell.get_text(strip=True)

            # Pattern: $1,001 - $15,000
            match = re.search(r'\$?([\d,]+)\s*-\s*\$?([\d,]+)', text)
            if match:
                try:
                    min_val = Decimal(match.group(1).replace(",", ""))
                    max_val = Decimal(match.group(2).replace(",", ""))
                    return min_val, max_val
                except:
                    pass

            # Pattern: Over $50,000,000
            match = re.search(r'[Oo]ver\s*\$?([\d,]+)', text)
            if match:
                try:
                    min_val = Decimal(match.group(1).replace(",", ""))
                    return min_val, None
                except:
                    pass

            # Pattern: $1,001+
            match = re.search(r'\$?([\d,]+)\+', text)
            if match:
                try:
                    min_val = Decimal(match.group(1).replace(",", ""))
                    return min_val, None
                except:
                    pass

        return None, None

    def _extract_date(self, cells) -> Optional[datetime.date]:
        """Extract transaction date."""
        for cell in cells:
            text = cell.get_text(strip=True)
            # Try common date formats
            for fmt in ["%m/%d/%Y", "%Y-%m-%d", "%m-%d-%Y", "%Y/%m/%d"]:
                try:
                    date = datetime.strptime(text, fmt).date()
                    # Sanity check: date should be within last 2 years
                    if (datetime.now().date() - date).days < 730:
                        return date
                except:
                    pass
        return None

    def close(self):
        """Close the driver."""
        if self.driver:
            self.driver.quit()
            self.driver = None
