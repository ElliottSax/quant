"""Service for managing scraped trade data."""

import logging
from datetime import date, datetime, timezone
from decimal import Decimal
from typing import Any

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError

from app.models.politician import Politician
from app.models.trade import Trade
from app.schemas.trade import TradeCreate

logger = logging.getLogger(__name__)


class DataValidationError(Exception):
    """Raised when scraped data fails validation."""
    pass


class ScraperService:
    """Service for processing and storing scraped trade data."""

    def __init__(self, db: AsyncSession):
        """
        Initialize scraper service.

        Args:
            db: Database session
        """
        self.db = db

    async def save_trades(
        self,
        trades_data: list[dict[str, Any]],
        skip_duplicates: bool = True,
    ) -> dict[str, int]:
        """
        Save scraped trades to database.

        Args:
            trades_data: List of trade dictionaries from scraper
            skip_duplicates: If True, skip duplicate trades instead of raising error

        Returns:
            Dictionary with statistics:
                - total: Total trades processed
                - saved: Successfully saved trades
                - skipped: Skipped trades (duplicates)
                - errors: Failed trades

        Raises:
            DataValidationError: If data validation fails
        """
        stats = {
            "total": len(trades_data),
            "saved": 0,
            "skipped": 0,
            "errors": 0,
        }

        for trade_data in trades_data:
            try:
                # Validate data
                validated_data = self._validate_trade_data(trade_data)

                # Get or create politician
                politician = await self._get_or_create_politician(
                    name=validated_data["politician_name"],
                    chamber=validated_data["chamber"],
                )

                # Create trade
                trade = Trade(
                    politician_id=politician.id,
                    ticker=validated_data["ticker"],
                    transaction_type=validated_data["transaction_type"],
                    amount_min=validated_data.get("amount_min"),
                    amount_max=validated_data.get("amount_max"),
                    transaction_date=validated_data["transaction_date"],
                    disclosure_date=validated_data["disclosure_date"],
                    source_url=validated_data.get("source_url"),
                    raw_data=validated_data.get("raw_data"),
                )

                self.db.add(trade)
                await self.db.flush()

                stats["saved"] += 1
                logger.debug(
                    f"Saved trade: {politician.name} {trade.transaction_type} "
                    f"{trade.ticker} on {trade.transaction_date}"
                )

            except IntegrityError as e:
                await self.db.rollback()

                if skip_duplicates:
                    stats["skipped"] += 1
                    logger.debug(f"Skipping duplicate trade: {trade_data.get('ticker')}")
                else:
                    stats["errors"] += 1
                    logger.error(f"Duplicate trade error: {e}")

            except DataValidationError as e:
                stats["errors"] += 1
                logger.warning(f"Validation error for trade: {e}")

            except Exception as e:
                stats["errors"] += 1
                logger.error(f"Error saving trade: {e}", exc_info=True)

        # Commit all changes
        try:
            await self.db.commit()
            logger.info(
                f"Trade import complete: {stats['saved']} saved, "
                f"{stats['skipped']} skipped, {stats['errors']} errors"
            )
        except Exception as e:
            await self.db.rollback()
            logger.error(f"Failed to commit trades: {e}", exc_info=True)
            raise

        return stats

    async def _get_or_create_politician(
        self,
        name: str,
        chamber: str,
    ) -> Politician:
        """
        Get existing politician or create new one.

        Args:
            name: Politician's full name
            chamber: 'senate' or 'house'

        Returns:
            Politician model instance
        """
        # Try to find existing politician
        result = await self.db.execute(
            select(Politician).where(
                Politician.name == name,
                Politician.chamber == chamber,
            )
        )
        politician = result.scalar_one_or_none()

        if politician:
            return politician

        # Create new politician
        politician = Politician(
            name=name,
            chamber=chamber,
        )
        self.db.add(politician)
        await self.db.flush()

        logger.info(f"Created new politician: {name} ({chamber})")
        return politician

    def _validate_trade_data(self, data: dict[str, Any]) -> dict[str, Any]:
        """
        Validate and clean trade data.

        Args:
            data: Raw trade data dictionary

        Returns:
            Validated trade data

        Raises:
            DataValidationError: If validation fails
        """
        validated = {}

        # Required fields
        required_fields = [
            "politician_name",
            "chamber",
            "ticker",
            "transaction_type",
            "transaction_date",
            "disclosure_date",
        ]

        for field in required_fields:
            if field not in data or data[field] is None:
                raise DataValidationError(f"Missing required field: {field}")
            validated[field] = data[field]

        # Validate politician name
        if not isinstance(validated["politician_name"], str) or len(validated["politician_name"]) < 2:
            raise DataValidationError("Invalid politician name")

        # Validate chamber
        if validated["chamber"] not in ("senate", "house"):
            raise DataValidationError(f"Invalid chamber: {validated['chamber']}")

        # Validate ticker
        ticker = validated["ticker"].upper().strip()
        if not ticker or len(ticker) > 10:
            raise DataValidationError(f"Invalid ticker: {ticker}")
        validated["ticker"] = ticker

        # Validate transaction type
        if validated["transaction_type"] not in ("buy", "sell", "sale"):
            raise DataValidationError(f"Invalid transaction type: {validated['transaction_type']}")

        # Normalize 'sale' to 'sell'
        if validated["transaction_type"] == "sale":
            validated["transaction_type"] = "sell"

        # Validate dates
        validated["transaction_date"] = self._validate_date(
            validated["transaction_date"],
            "transaction_date",
        )
        validated["disclosure_date"] = self._validate_date(
            validated["disclosure_date"],
            "disclosure_date",
        )

        # Validate disclosure date is after transaction date
        if validated["disclosure_date"] < validated["transaction_date"]:
            raise DataValidationError(
                "Disclosure date must be on or after transaction date"
            )

        # Validate dates are not in the future
        today = date.today()
        if validated["transaction_date"] > today:
            raise DataValidationError("Transaction date cannot be in the future")
        if validated["disclosure_date"] > today:
            raise DataValidationError("Disclosure date cannot be in the future")

        # Validate amount range (optional)
        if "amount_min" in data and data["amount_min"] is not None:
            validated["amount_min"] = self._validate_amount(data["amount_min"], "amount_min")

        if "amount_max" in data and data["amount_max"] is not None:
            validated["amount_max"] = self._validate_amount(data["amount_max"], "amount_max")

        # Validate amount range relationship
        if (
            validated.get("amount_min") is not None
            and validated.get("amount_max") is not None
            and validated["amount_min"] > validated["amount_max"]
        ):
            raise DataValidationError("amount_min cannot be greater than amount_max")

        # Optional fields
        validated["source_url"] = data.get("source_url")
        validated["raw_data"] = data.get("raw_data")

        return validated

    def _validate_date(self, value: Any, field_name: str) -> date:
        """
        Validate date value.

        Args:
            value: Date value (date object or string)
            field_name: Name of the field for error messages

        Returns:
            date object

        Raises:
            DataValidationError: If validation fails
        """
        if isinstance(value, date):
            return value

        if isinstance(value, str):
            try:
                return datetime.fromisoformat(value).date()
            except ValueError:
                pass

        raise DataValidationError(f"Invalid date format for {field_name}: {value}")

    def _validate_amount(self, value: Any, field_name: str) -> Decimal:
        """
        Validate amount value.

        Args:
            value: Amount value (Decimal, int, float, or string)
            field_name: Name of the field for error messages

        Returns:
            Decimal amount

        Raises:
            DataValidationError: If validation fails
        """
        try:
            amount = Decimal(str(value))
        except Exception:
            raise DataValidationError(f"Invalid amount for {field_name}: {value}")

        if amount < 0:
            raise DataValidationError(f"{field_name} cannot be negative")

        return amount

    async def get_scraping_stats(self) -> dict[str, Any]:
        """
        Get statistics about scraped data.

        Returns:
            Dictionary with statistics
        """
        # Total trades
        total_trades_result = await self.db.execute(select(Trade))
        total_trades = len(total_trades_result.scalars().all())

        # Total politicians
        total_politicians_result = await self.db.execute(select(Politician))
        total_politicians = len(total_politicians_result.scalars().all())

        # Latest scrape date
        latest_trade_result = await self.db.execute(
            select(Trade.created_at)
            .order_by(Trade.created_at.desc())
            .limit(1)
        )
        latest_scrape = latest_trade_result.scalar_one_or_none()

        return {
            "total_trades": total_trades,
            "total_politicians": total_politicians,
            "latest_scrape": latest_scrape,
        }


async def run_senate_scraper(
    db: AsyncSession,
    start_date: date | None = None,
    end_date: date | None = None,
    headless: bool = True,
) -> dict[str, int]:
    """
    Run Senate scraper and save results to database.

    Args:
        db: Database session
        start_date: Start date for scraping
        end_date: End date for scraping
        headless: Run browser in headless mode

    Returns:
        Statistics dictionary from save_trades
    """
    from app.scrapers.senate import SenateScraper

    logger.info("Starting Senate scraper")

    try:
        # Run scraper
        scraper = SenateScraper(
            start_date=start_date,
            end_date=end_date,
            headless=headless,
        )
        trades_data = scraper.run()

        logger.info(f"Scraper completed. Scraped {len(trades_data)} trades")

        # Save to database
        service = ScraperService(db)
        stats = await service.save_trades(trades_data, skip_duplicates=True)

        logger.info(f"Senate scraper completed: {stats}")
        return stats

    except Exception as e:
        logger.error(f"Senate scraper failed: {e}", exc_info=True)
        raise


async def run_house_scraper(
    db: AsyncSession,
    start_date: date | None = None,
    end_date: date | None = None,
    headless: bool = True,
) -> dict[str, int]:
    """
    Run House scraper and save results to database.

    Args:
        db: Database session
        start_date: Start date for scraping
        end_date: End date for scraping
        headless: Run browser in headless mode

    Returns:
        Statistics dictionary from save_trades
    """
    from app.scrapers.house import HouseScraper

    logger.info("Starting House scraper")

    try:
        # Run scraper
        scraper = HouseScraper(
            start_date=start_date,
            end_date=end_date,
            headless=headless,
        )
        trades_data = scraper.run()

        logger.info(f"Scraper completed. Scraped {len(trades_data)} trades")

        # Save to database
        service = ScraperService(db)
        stats = await service.save_trades(trades_data, skip_duplicates=True)

        logger.info(f"House scraper completed: {stats}")
        return stats

    except Exception as e:
        logger.error(f"House scraper failed: {e}", exc_info=True)
        raise


async def run_all_scrapers(
    db: AsyncSession,
    start_date: date | None = None,
    end_date: date | None = None,
    headless: bool = True,
) -> dict[str, dict[str, int]]:
    """
    Run both Senate and House scrapers.

    Args:
        db: Database session
        start_date: Start date for scraping
        end_date: End date for scraping
        headless: Run browser in headless mode

    Returns:
        Dictionary with stats for each scraper:
            {
                "senate": {...},
                "house": {...}
            }
    """
    results = {}

    # Run Senate scraper
    try:
        logger.info("=" * 80)
        logger.info("Running Senate scraper...")
        logger.info("=" * 80)
        results["senate"] = await run_senate_scraper(db, start_date, end_date, headless)
    except Exception as e:
        logger.error(f"Senate scraper failed: {e}")
        results["senate"] = {"error": str(e)}

    # Run House scraper
    try:
        logger.info("=" * 80)
        logger.info("Running House scraper...")
        logger.info("=" * 80)
        results["house"] = await run_house_scraper(db, start_date, end_date, headless)
    except Exception as e:
        logger.error(f"House scraper failed: {e}")
        results["house"] = {"error": str(e)}

    return results
