"""
Senate Trading Data Scraper

Scrapes periodic transaction reports from efdsearch.senate.gov
Extracts: politician name, ticker, transaction type, amount range, date
"""

import re
import logging
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


class SenateScraper:
    """Scraper for Senate financial disclosures."""

    BASE_URL = "https://efdsearch.senate.gov"
    SEARCH_URL = f"{BASE_URL}/search/"

    def __init__(self, headless: bool = True, rate_limit_delay: float = 2.0):
        """
        Initialize Senate scraper.

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
        Scrape recent Senate transactions.

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
            logger.info(f"Scraping Senate transactions from {start_date.date()} to {end_date.date()}")

            # Navigate to search page
            self.driver.get(self.SEARCH_URL)

            # Wait for page to load
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.ID, "agree_statement"))
            )

            # Accept agreement
            agree_button = self.driver.find_element(By.ID, "agree_statement")
            agree_button.click()

            # Wait for search form
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.NAME, "start_date"))
            )

            # Fill in date range
            start_input = self.driver.find_element(By.NAME, "start_date")
            end_input = self.driver.find_element(By.NAME, "end_date")

            start_input.clear()
            start_input.send_keys(start_date.strftime("%m/%d/%Y"))

            end_input.clear()
            end_input.send_keys(end_date.strftime("%m/%d/%Y"))

            # Submit search
            search_button = self.driver.find_element(By.NAME, "submit")
            search_button.click()

            # Wait for results
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.CLASS_NAME, "table-responsive"))
            )

            # Parse results
            soup = BeautifulSoup(self.driver.page_source, "html.parser")
            transactions = self._parse_search_results(soup)

            logger.info(f"Scraped {len(transactions)} Senate transactions")

        except Exception as e:
            logger.error(f"Error scraping Senate data: {e}")
            raise

        return transactions

    def _parse_search_results(self, soup: BeautifulSoup) -> List[Dict]:
        """
        Parse search results page.

        Args:
            soup: BeautifulSoup object of results page

        Returns:
            List of transaction dictionaries
        """
        transactions = []

        # Find results table
        table = soup.find("table", {"class": "table"})
        if not table:
            logger.warning("No results table found")
            return transactions

        # Parse each row
        rows = table.find_all("tr")[1:]  # Skip header row

        for row in rows:
            try:
                cells = row.find_all("td")
                if len(cells) < 4:
                    continue

                # Extract report link
                link_cell = cells[0].find("a")
                if not link_cell:
                    continue

                report_url = self.BASE_URL + link_cell.get("href", "")

                # Extract basic info
                politician_name = cells[0].get_text(strip=True)
                report_date = cells[1].get_text(strip=True)
                report_type = cells[2].get_text(strip=True)

                # Only process periodic transaction reports
                if "Periodic Transaction Report" not in report_type:
                    continue

                # Scrape individual report
                report_transactions = self._scrape_report(report_url, politician_name)
                transactions.extend(report_transactions)

            except Exception as e:
                logger.warning(f"Error parsing row: {e}")
                continue

        return transactions

    def _scrape_report(
        self, report_url: str, politician_name: str
    ) -> List[Dict]:
        """
        Scrape individual report for transactions.

        Args:
            report_url: URL of the report
            politician_name: Name of politician

        Returns:
            List of transactions from this report
        """
        transactions = []

        try:
            # Navigate to report
            self.driver.get(report_url)

            # Wait for report content
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.TAG_NAME, "table"))
            )

            soup = BeautifulSoup(self.driver.page_source, "html.parser")

            # Find transaction tables
            tables = soup.find_all("table")

            for table in tables:
                # Look for transaction headers
                headers = [th.get_text(strip=True).lower() for th in table.find_all("th")]

                if not any("ticker" in h or "asset" in h for h in headers):
                    continue

                # Parse transactions
                rows = table.find_all("tr")[1:]  # Skip header

                for row in rows:
                    try:
                        transaction = self._parse_transaction_row(
                            row, politician_name, report_url
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
        self, row, politician_name: str, source_url: str
    ) -> Optional[Dict]:
        """
        Parse a transaction row.

        Args:
            row: BeautifulSoup row element
            politician_name: Name of politician
            source_url: Source URL

        Returns:
            Transaction dictionary or None
        """
        cells = row.find_all("td")
        if len(cells) < 4:
            return None

        # Extract fields (layout varies, so we try multiple patterns)
        ticker = self._extract_ticker(cells)
        if not ticker:
            return None

        transaction_type = self._extract_transaction_type(cells)
        if not transaction_type:
            return None

        amount_min, amount_max = self._extract_amount_range(cells)
        transaction_date = self._extract_date(cells)

        return {
            "politician_name": politician_name,
            "chamber": "senate",
            "ticker": ticker,
            "transaction_type": transaction_type,
            "amount_min": amount_min,
            "amount_max": amount_max,
            "transaction_date": transaction_date,
            "disclosure_date": datetime.now().date(),
            "source_url": source_url,
            "raw_data": {
                "cells": [cell.get_text(strip=True) for cell in cells]
            }
        }

    def _extract_ticker(self, cells) -> Optional[str]:
        """Extract ticker symbol from cells."""
        for cell in cells:
            text = cell.get_text(strip=True).upper()
            # Look for ticker pattern (1-5 letters)
            match = re.search(r'\b([A-Z]{1,5})\b', text)
            if match:
                ticker = match.group(1)
                # Filter out common false positives
                if ticker not in ["PTR", "DATE", "TYPE", "SALE"]:
                    return ticker
        return None

    def _extract_transaction_type(self, cells) -> Optional[str]:
        """Extract transaction type (buy/sell)."""
        for cell in cells:
            text = cell.get_text(strip=True).lower()
            if "purchase" in text or "buy" in text:
                return "buy"
            elif "sale" in text or "sell" in text:
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

        return None, None

    def _extract_date(self, cells) -> Optional[datetime.date]:
        """Extract transaction date."""
        for cell in cells:
            text = cell.get_text(strip=True)
            # Try common date formats
            for fmt in ["%m/%d/%Y", "%Y-%m-%d", "%m-%d-%Y"]:
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
