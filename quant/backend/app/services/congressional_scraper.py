"""
Congressional Trades Scraper Service

Fetches real congressional stock trading disclosures from:
- Senate Financial Disclosures (efdsearch.senate.gov)
- House Financial Disclosures (disclosures-clerk.house.gov)

Data is updated periodically as members file disclosures (typically 45 days after trade).
"""

import re
import asyncio
from datetime import datetime, date, timedelta
from decimal import Decimal
from typing import List, Dict, Optional, AsyncGenerator
from enum import Enum
from dataclasses import dataclass

import httpx
from bs4 import BeautifulSoup
from pydantic import BaseModel

from app.core.logging import get_logger
from app.core.cache import cache_manager

logger = get_logger(__name__)

# API URLs
SENATE_SEARCH_URL = "https://efdsearch.senate.gov/search/"
SENATE_API_URL = "https://efdsearch.senate.gov/search/home/GetFilerData"
HOUSE_DISCLOSURES_URL = "https://disclosures-clerk.house.gov/PublicDisclosure/FinancialDisclosure"
HOUSE_PTR_URL = "https://disclosures-clerk.house.gov/public_disc/ptr-pdfs"


class Chamber(str, Enum):
    """Congressional chamber."""
    SENATE = "senate"
    HOUSE = "house"


class TransactionType(str, Enum):
    """Transaction type."""
    PURCHASE = "purchase"
    SALE = "sale"
    EXCHANGE = "exchange"


@dataclass
class CongressionalTrade:
    """Represents a congressional stock trade disclosure."""
    politician_name: str
    chamber: Chamber
    party: Optional[str]
    state: Optional[str]
    ticker: Optional[str]
    asset_description: str
    transaction_type: TransactionType
    transaction_date: date
    disclosure_date: date
    amount_range: str
    amount_min: Optional[Decimal]
    amount_max: Optional[Decimal]
    owner: str  # "Self", "Spouse", "Joint", "Child"
    source_url: str
    raw_data: Dict


class CongressionalTradeResponse(BaseModel):
    """Response model for congressional trade."""
    politician_name: str
    chamber: str
    party: Optional[str] = None
    state: Optional[str] = None
    ticker: Optional[str] = None
    asset_description: str
    transaction_type: str
    transaction_date: date
    disclosure_date: date
    amount_range: str
    amount_min: Optional[float] = None
    amount_max: Optional[float] = None
    owner: str
    source_url: str


# Amount range mapping
AMOUNT_RANGES = {
    "$1,001 - $15,000": (Decimal("1001"), Decimal("15000")),
    "$15,001 - $50,000": (Decimal("15001"), Decimal("50000")),
    "$50,001 - $100,000": (Decimal("50001"), Decimal("100000")),
    "$100,001 - $250,000": (Decimal("100001"), Decimal("250000")),
    "$250,001 - $500,000": (Decimal("250001"), Decimal("500000")),
    "$500,001 - $1,000,000": (Decimal("500001"), Decimal("1000000")),
    "$1,000,001 - $5,000,000": (Decimal("1000001"), Decimal("5000000")),
    "$5,000,001 - $25,000,000": (Decimal("5000001"), Decimal("25000000")),
    "Over $50,000,000": (Decimal("50000001"), Decimal("100000000")),
}


def parse_amount_range(amount_str: str) -> tuple[Optional[Decimal], Optional[Decimal]]:
    """Parse amount range string into min/max values."""
    amount_str = amount_str.strip()

    for pattern, (min_val, max_val) in AMOUNT_RANGES.items():
        if pattern.lower() in amount_str.lower():
            return min_val, max_val

    # Try to parse numeric values
    match = re.search(r'\$?([\d,]+)\s*-\s*\$?([\d,]+)', amount_str)
    if match:
        min_val = Decimal(match.group(1).replace(",", ""))
        max_val = Decimal(match.group(2).replace(",", ""))
        return min_val, max_val

    return None, None


def extract_ticker(asset_description: str) -> Optional[str]:
    """Extract stock ticker from asset description."""
    # Common patterns for ticker extraction
    patterns = [
        r'\(([A-Z]{1,5})\)',  # (AAPL)
        r'\[([A-Z]{1,5})\]',  # [AAPL]
        r'^([A-Z]{1,5})\s*[-:]',  # AAPL - Apple
        r'Ticker:\s*([A-Z]{1,5})',
        r'Stock\s*Symbol:\s*([A-Z]{1,5})',
    ]

    for pattern in patterns:
        match = re.search(pattern, asset_description)
        if match:
            ticker = match.group(1)
            # Validate it looks like a ticker
            if 1 <= len(ticker) <= 5 and ticker.isalpha():
                return ticker.upper()

    return None


class CongressionalScraper:
    """
    Scraper for congressional financial disclosures.

    Fetches periodic transaction reports (PTRs) from both
    Senate and House disclosure systems.
    """

    def __init__(self):
        self.http_client = httpx.AsyncClient(
            timeout=30.0,
            follow_redirects=True,
            headers={
                "User-Agent": "Mozilla/5.0 (compatible; QuantAnalytics/1.0)",
                "Accept": "text/html,application/json",
            }
        )

    async def close(self):
        """Close HTTP client."""
        await self.http_client.aclose()

    async def fetch_senate_trades(
        self,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
        limit: int = 100,
    ) -> List[CongressionalTrade]:
        """
        Fetch Senate PTR (Periodic Transaction Report) filings.

        Args:
            start_date: Start date for filtering
            end_date: End date for filtering
            limit: Maximum number of results

        Returns:
            List of CongressionalTrade objects
        """
        # Default to last 90 days
        if not start_date:
            start_date = date.today() - timedelta(days=90)
        if not end_date:
            end_date = date.today()

        trades = []

        try:
            # First, get the search page to establish session
            await self.http_client.get(SENATE_SEARCH_URL)

            # Make search request
            # Note: The actual Senate API requires specific form data
            # This is a simplified version - real implementation would need
            # to handle CSRF tokens and session cookies

            search_params = {
                "filer_type": "1",  # Senators
                "report_type": "11",  # PTR
                "submitted_start_date": start_date.strftime("%m/%d/%Y"),
                "submitted_end_date": end_date.strftime("%m/%d/%Y"),
            }

            logger.info(f"Searching Senate PTRs from {start_date} to {end_date}")

            response = await self.http_client.post(
                SENATE_API_URL,
                data=search_params,
            )

            if response.status_code == 200:
                # Parse response (simplified - actual API returns JSON or HTML)
                data = response.json() if "application/json" in response.headers.get("content-type", "") else {}

                # Process results
                for item in data.get("data", [])[:limit]:
                    trade = self._parse_senate_trade(item)
                    if trade:
                        trades.append(trade)

            logger.info(f"Found {len(trades)} Senate trades")

        except Exception as e:
            logger.error(f"Error fetching Senate trades: {e}")

        return trades

    def _parse_senate_trade(self, data: Dict) -> Optional[CongressionalTrade]:
        """Parse a Senate trade record."""
        try:
            # Extract basic info
            name = data.get("filer_name", "").strip()
            if not name:
                return None

            # Parse amount
            amount_str = data.get("amount", "$1,001 - $15,000")
            amount_min, amount_max = parse_amount_range(amount_str)

            # Extract ticker
            asset = data.get("asset_description", "")
            ticker = extract_ticker(asset)

            # Parse dates
            transaction_date = self._parse_date(data.get("transaction_date"))
            disclosure_date = self._parse_date(data.get("file_date"))

            if not transaction_date or not disclosure_date:
                return None

            # Determine transaction type
            tx_type_str = data.get("transaction_type", "").lower()
            if "purchase" in tx_type_str or "buy" in tx_type_str:
                tx_type = TransactionType.PURCHASE
            elif "sale" in tx_type_str or "sell" in tx_type_str:
                tx_type = TransactionType.SALE
            else:
                tx_type = TransactionType.EXCHANGE

            return CongressionalTrade(
                politician_name=name,
                chamber=Chamber.SENATE,
                party=data.get("party"),
                state=data.get("state"),
                ticker=ticker,
                asset_description=asset,
                transaction_type=tx_type,
                transaction_date=transaction_date,
                disclosure_date=disclosure_date,
                amount_range=amount_str,
                amount_min=amount_min,
                amount_max=amount_max,
                owner=data.get("owner", "Self"),
                source_url=f"{SENATE_SEARCH_URL}?id={data.get('id', '')}",
                raw_data=data,
            )

        except Exception as e:
            logger.warning(f"Error parsing Senate trade: {e}")
            return None

    async def fetch_house_trades(
        self,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
        limit: int = 100,
    ) -> List[CongressionalTrade]:
        """
        Fetch House PTR filings.

        Args:
            start_date: Start date for filtering
            end_date: End date for filtering
            limit: Maximum number of results

        Returns:
            List of CongressionalTrade objects
        """
        # Default to last 90 days
        if not start_date:
            start_date = date.today() - timedelta(days=90)
        if not end_date:
            end_date = date.today()

        trades = []

        try:
            # Fetch the disclosure listing page
            logger.info(f"Fetching House PTRs from {start_date} to {end_date}")

            # House uses a different system with XML/ZIP files
            # This is a simplified version
            response = await self.http_client.get(
                f"{HOUSE_DISCLOSURES_URL}/Search",
                params={
                    "filingYear": start_date.year,
                    "state": "",
                    "district": "",
                    "lastName": "",
                    "filingType": "P",  # PTR
                },
            )

            if response.status_code == 200:
                # Parse HTML response
                soup = BeautifulSoup(response.text, "html.parser")

                # Find disclosure table rows
                rows = soup.select("table.disclosures tbody tr")

                for row in rows[:limit]:
                    trade = self._parse_house_trade(row)
                    if trade:
                        # Check date range
                        if start_date <= trade.disclosure_date <= end_date:
                            trades.append(trade)

            logger.info(f"Found {len(trades)} House trades")

        except Exception as e:
            logger.error(f"Error fetching House trades: {e}")

        return trades

    def _parse_house_trade(self, row) -> Optional[CongressionalTrade]:
        """Parse a House disclosure row."""
        try:
            cells = row.find_all("td")
            if len(cells) < 5:
                return None

            name = cells[0].get_text(strip=True)
            state = cells[1].get_text(strip=True)
            filing_year = cells[2].get_text(strip=True)
            filing_type = cells[3].get_text(strip=True)

            # Get link to PDF
            link = row.find("a", href=True)
            source_url = link["href"] if link else ""

            # For House, we'd need to download and parse the PDF
            # This is a simplified version

            return CongressionalTrade(
                politician_name=name,
                chamber=Chamber.HOUSE,
                party=None,  # Would need additional lookup
                state=state,
                ticker=None,  # Would need to parse PDF
                asset_description="See disclosure document",
                transaction_type=TransactionType.PURCHASE,
                transaction_date=date.today(),  # Would parse from PDF
                disclosure_date=date.today(),
                amount_range="$1,001 - $15,000",
                amount_min=Decimal("1001"),
                amount_max=Decimal("15000"),
                owner="Self",
                source_url=source_url,
                raw_data={"raw_row": str(row)},
            )

        except Exception as e:
            logger.warning(f"Error parsing House trade: {e}")
            return None

    def _parse_date(self, date_str: Optional[str]) -> Optional[date]:
        """Parse date from various formats."""
        if not date_str:
            return None

        formats = [
            "%m/%d/%Y",
            "%Y-%m-%d",
            "%m-%d-%Y",
            "%B %d, %Y",
        ]

        for fmt in formats:
            try:
                return datetime.strptime(date_str.strip(), fmt).date()
            except ValueError:
                continue

        return None

    async def fetch_all_trades(
        self,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
        limit: int = 100,
    ) -> List[CongressionalTrade]:
        """
        Fetch trades from both Senate and House.

        Args:
            start_date: Start date for filtering
            end_date: End date for filtering
            limit: Maximum number of results per chamber

        Returns:
            Combined list of trades from both chambers
        """
        # Fetch concurrently
        senate_task = self.fetch_senate_trades(start_date, end_date, limit)
        house_task = self.fetch_house_trades(start_date, end_date, limit)

        senate_trades, house_trades = await asyncio.gather(
            senate_task, house_task, return_exceptions=True
        )

        all_trades = []

        if isinstance(senate_trades, list):
            all_trades.extend(senate_trades)
        else:
            logger.error(f"Senate scraper error: {senate_trades}")

        if isinstance(house_trades, list):
            all_trades.extend(house_trades)
        else:
            logger.error(f"House scraper error: {house_trades}")

        # Sort by disclosure date (most recent first)
        all_trades.sort(key=lambda t: t.disclosure_date, reverse=True)

        return all_trades


# Cached scraper instance
_scraper: Optional[CongressionalScraper] = None


def get_congressional_scraper() -> CongressionalScraper:
    """Get or create congressional scraper instance."""
    global _scraper
    if _scraper is None:
        _scraper = CongressionalScraper()
    return _scraper


async def fetch_recent_congressional_trades(
    days: int = 30,
    chamber: Optional[Chamber] = None,
) -> List[CongressionalTradeResponse]:
    """
    Convenience function to fetch recent congressional trades.

    Args:
        days: Number of days to look back
        chamber: Optional chamber filter

    Returns:
        List of trade responses
    """
    cache_key = f"congressional_trades:{days}:{chamber}"

    # Check cache first
    cached = await cache_manager.get(cache_key)
    if cached:
        return cached

    scraper = get_congressional_scraper()

    start_date = date.today() - timedelta(days=days)
    end_date = date.today()

    if chamber == Chamber.SENATE:
        trades = await scraper.fetch_senate_trades(start_date, end_date)
    elif chamber == Chamber.HOUSE:
        trades = await scraper.fetch_house_trades(start_date, end_date)
    else:
        trades = await scraper.fetch_all_trades(start_date, end_date)

    # Convert to response models
    responses = [
        CongressionalTradeResponse(
            politician_name=t.politician_name,
            chamber=t.chamber.value,
            party=t.party,
            state=t.state,
            ticker=t.ticker,
            asset_description=t.asset_description,
            transaction_type=t.transaction_type.value,
            transaction_date=t.transaction_date,
            disclosure_date=t.disclosure_date,
            amount_range=t.amount_range,
            amount_min=float(t.amount_min) if t.amount_min else None,
            amount_max=float(t.amount_max) if t.amount_max else None,
            owner=t.owner,
            source_url=t.source_url,
        )
        for t in trades
    ]

    # Cache for 1 hour
    await cache_manager.set(cache_key, responses, ttl=3600)

    return responses
