"""
Data Validation & Cleaning

Normalizes ticker symbols, parses amount ranges, detects duplicates,
validates dates and politician names.
"""

import re
import logging
from datetime import datetime, date
from typing import Dict, List, Optional, Set, Tuple
from decimal import Decimal

logger = logging.getLogger(__name__)


class DataValidator:
    """Validates and cleans scraped trading data."""

    # Known ticker symbol variations and corrections
    TICKER_CORRECTIONS = {
        "GOOGL": "GOOGL",  # Alphabet Class A
        "GOOG": "GOOG",    # Alphabet Class C
        "BRK.A": "BRK.A",  # Berkshire Hathaway
        "BRK.B": "BRK.B",
        "FB": "META",      # Facebook -> Meta
    }

    # Common invalid tickers to filter out
    INVALID_TICKERS = {
        "LLC", "INC", "LTD", "CORP", "CO", "NA", "N/A", "NONE",
        "UNKNOWN", "OTHER", "CASH", "BOND", "FUND", "ETF", "MUTUAL",
        "STOCK", "EQUITY", "DEBT", "OPTION", "OPTIONS"
    }

    def __init__(self):
        """Initialize validator."""
        self.seen_transactions: Set[str] = set()

    def validate_transaction(self, transaction: Dict) -> Tuple[bool, Optional[str]]:
        """
        Validate a single transaction.

        Args:
            transaction: Transaction dictionary

        Returns:
            Tuple of (is_valid, error_message)
        """
        # Validate required fields
        required_fields = [
            "politician_name",
            "chamber",
            "ticker",
            "transaction_type",
            "transaction_date"
        ]

        for field in required_fields:
            if not transaction.get(field):
                return False, f"Missing required field: {field}"

        # Validate chamber
        if transaction["chamber"] not in ["senate", "house"]:
            return False, f"Invalid chamber: {transaction['chamber']}"

        # Validate transaction type
        if transaction["transaction_type"] not in ["buy", "sell"]:
            return False, f"Invalid transaction type: {transaction['transaction_type']}"

        # Validate ticker
        ticker = transaction["ticker"]
        if not self.is_valid_ticker(ticker):
            return False, f"Invalid ticker: {ticker}"

        # Validate dates
        trans_date = transaction.get("transaction_date")
        if not self.is_valid_date(trans_date):
            return False, f"Invalid transaction date: {trans_date}"

        disc_date = transaction.get("disclosure_date")
        if disc_date and not self.is_valid_date(disc_date):
            return False, f"Invalid disclosure date: {disc_date}"

        # Validate disclosure is after transaction
        if disc_date and trans_date:
            if isinstance(trans_date, str):
                trans_date = datetime.strptime(trans_date, "%Y-%m-%d").date()
            if isinstance(disc_date, str):
                disc_date = datetime.strptime(disc_date, "%Y-%m-%d").date()

            if disc_date < trans_date:
                return False, "Disclosure date before transaction date"

        # Validate amount range
        amount_min = transaction.get("amount_min")
        amount_max = transaction.get("amount_max")

        if amount_min and amount_max:
            if amount_min > amount_max:
                return False, f"Invalid amount range: {amount_min} > {amount_max}"

        return True, None

    def clean_transaction(self, transaction: Dict) -> Dict:
        """
        Clean and normalize transaction data.

        Args:
            transaction: Raw transaction dictionary

        Returns:
            Cleaned transaction dictionary
        """
        cleaned = transaction.copy()

        # Normalize ticker
        cleaned["ticker"] = self.normalize_ticker(cleaned.get("ticker", ""))

        # Normalize politician name
        cleaned["politician_name"] = self.normalize_name(cleaned.get("politician_name", ""))

        # Normalize transaction type
        cleaned["transaction_type"] = cleaned.get("transaction_type", "").lower()

        # Normalize chamber
        cleaned["chamber"] = cleaned.get("chamber", "").lower()

        # Parse and normalize amount range
        amount_min = cleaned.get("amount_min")
        amount_max = cleaned.get("amount_max")

        if isinstance(amount_min, str):
            cleaned["amount_min"] = self.parse_amount(amount_min)

        if isinstance(amount_max, str):
            cleaned["amount_max"] = self.parse_amount(amount_max)

        # Ensure dates are date objects
        trans_date = cleaned.get("transaction_date")
        if isinstance(trans_date, str):
            try:
                cleaned["transaction_date"] = datetime.strptime(trans_date, "%Y-%m-%d").date()
            except:
                pass

        disc_date = cleaned.get("disclosure_date")
        if isinstance(disc_date, str):
            try:
                cleaned["disclosure_date"] = datetime.strptime(disc_date, "%Y-%m-%d").date()
            except:
                pass

        return cleaned

    def normalize_ticker(self, ticker: str) -> str:
        """
        Normalize ticker symbol.

        Args:
            ticker: Raw ticker string

        Returns:
            Normalized ticker
        """
        if not ticker:
            return ""

        # Convert to uppercase
        ticker = ticker.upper().strip()

        # Remove common suffixes
        ticker = re.sub(r'\.(A|B|C)$', r'.\1', ticker)  # Keep class suffixes

        # Apply corrections
        if ticker in self.TICKER_CORRECTIONS:
            ticker = self.TICKER_CORRECTIONS[ticker]

        return ticker

    def is_valid_ticker(self, ticker: str) -> bool:
        """
        Check if ticker is valid.

        Args:
            ticker: Ticker symbol

        Returns:
            True if valid
        """
        if not ticker:
            return False

        ticker = ticker.upper().strip()

        # Check against invalid list
        if ticker in self.INVALID_TICKERS:
            return False

        # Basic pattern validation (1-5 letters, optional .A/.B)
        if not re.match(r'^[A-Z]{1,5}(\.[A-Z])?$', ticker):
            return False

        return True

    def normalize_name(self, name: str) -> str:
        """
        Normalize politician name.

        Args:
            name: Raw name string

        Returns:
            Normalized name
        """
        if not name:
            return ""

        # Remove extra whitespace
        name = " ".join(name.split())

        # Title case
        name = name.title()

        # Handle common prefixes/suffixes
        name = name.replace("Hon.", "").strip()
        name = name.replace("Sen.", "").strip()
        name = name.replace("Rep.", "").strip()

        # Remove Jr., Sr., III, etc. from comparison
        name = re.sub(r',?\s+(Jr\.?|Sr\.?|II|III|IV)$', '', name)

        return name

    def parse_amount(self, amount_str: str) -> Optional[Decimal]:
        """
        Parse amount string to Decimal.

        Args:
            amount_str: Amount string (e.g., "$1,001", "15000")

        Returns:
            Decimal amount or None
        """
        if not amount_str:
            return None

        if isinstance(amount_str, (int, float, Decimal)):
            return Decimal(str(amount_str))

        # Remove $ and commas
        amount_str = amount_str.replace("$", "").replace(",", "").strip()

        try:
            return Decimal(amount_str)
        except:
            logger.warning(f"Could not parse amount: {amount_str}")
            return None

    def is_valid_date(self, date_val) -> bool:
        """
        Check if date is valid.

        Args:
            date_val: Date value (date object or string)

        Returns:
            True if valid
        """
        if not date_val:
            return False

        if isinstance(date_val, date):
            # Check if date is reasonable (within last 10 years, not future)
            today = datetime.now().date()
            ten_years_ago = today.replace(year=today.year - 10)

            return ten_years_ago <= date_val <= today

        return False

    def is_duplicate(self, transaction: Dict) -> bool:
        """
        Check if transaction is a duplicate.

        Args:
            transaction: Transaction dictionary

        Returns:
            True if duplicate
        """
        # Create unique key
        key = self._create_transaction_key(transaction)

        if key in self.seen_transactions:
            return True

        self.seen_transactions.add(key)
        return False

    def _create_transaction_key(self, transaction: Dict) -> str:
        """
        Create unique key for transaction.

        Args:
            transaction: Transaction dictionary

        Returns:
            Unique key string
        """
        # Normalize politician name for comparison
        politician = self.normalize_name(transaction.get("politician_name", ""))

        # Create key from critical fields
        ticker = transaction.get("ticker", "")
        trans_type = transaction.get("transaction_type", "")
        trans_date = transaction.get("transaction_date", "")

        return f"{politician}|{ticker}|{trans_type}|{trans_date}"

    def validate_batch(self, transactions: List[Dict]) -> Tuple[List[Dict], List[Dict]]:
        """
        Validate and clean a batch of transactions.

        Args:
            transactions: List of transaction dictionaries

        Returns:
            Tuple of (valid_transactions, invalid_transactions)
        """
        valid = []
        invalid = []

        for transaction in transactions:
            try:
                # Clean transaction
                cleaned = self.clean_transaction(transaction)

                # Validate
                is_valid, error = self.validate_transaction(cleaned)

                if not is_valid:
                    logger.warning(f"Invalid transaction: {error}")
                    invalid.append({
                        "transaction": transaction,
                        "error": error
                    })
                    continue

                # Check for duplicates
                if self.is_duplicate(cleaned):
                    logger.info(f"Skipping duplicate: {cleaned.get('ticker')} on {cleaned.get('transaction_date')}")
                    continue

                valid.append(cleaned)

            except Exception as e:
                logger.error(f"Error validating transaction: {e}")
                invalid.append({
                    "transaction": transaction,
                    "error": str(e)
                })

        logger.info(f"Validated {len(transactions)} transactions: {len(valid)} valid, {len(invalid)} invalid")

        return valid, invalid

    def reset_duplicate_tracking(self):
        """Reset the duplicate tracking set."""
        self.seen_transactions.clear()
