#!/usr/bin/env python3
"""
Historical Data Backfill Script

Loads congressional trading data from 2012 to present.
Includes progress tracking and can resume if interrupted.

Usage:
    python scripts/backfill_historical.py --start-year 2012 --end-year 2024
    python scripts/backfill_historical.py --resume
    python scripts/backfill_historical.py --senate-only
    python scripts/backfill_historical.py --house-only
"""

import asyncio
import argparse
import json
import logging
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy import select

# Add parent directory to path
import sys
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.core.config import settings
from app.scrapers import SenateScraper, HouseScraper, DataValidator
from app.models import Politician, Trade, DataSource

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('backfill.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Checkpoint file to track progress
CHECKPOINT_FILE = Path(__file__).parent / "backfill_checkpoint.json"


class BackfillProgress:
    """Track backfill progress."""

    def __init__(self, checkpoint_file: Path):
        self.checkpoint_file = checkpoint_file
        self.progress = self._load_checkpoint()

    def _load_checkpoint(self) -> Dict:
        """Load checkpoint from file."""
        if self.checkpoint_file.exists():
            with open(self.checkpoint_file, 'r') as f:
                return json.load(f)
        return {
            "senate": {"completed_years": [], "current_year": None, "last_update": None},
            "house": {"completed_years": [], "current_year": None, "last_update": None},
            "total_records": 0,
            "total_imported": 0,
        }

    def save_checkpoint(self):
        """Save checkpoint to file."""
        self.progress["last_update"] = datetime.now().isoformat()
        with open(self.checkpoint_file, 'w') as f:
            json.dump(self.progress, f, indent=2)
        logger.info(f"Checkpoint saved: {self.progress}")

    def mark_year_complete(self, source: str, year: int):
        """Mark a year as completed."""
        if year not in self.progress[source]["completed_years"]:
            self.progress[source]["completed_years"].append(year)
        self.progress[source]["completed_years"].sort()
        self.save_checkpoint()

    def set_current_year(self, source: str, year: int):
        """Set the current year being processed."""
        self.progress[source]["current_year"] = year
        self.save_checkpoint()

    def is_year_complete(self, source: str, year: int) -> bool:
        """Check if a year is already completed."""
        return year in self.progress[source]["completed_years"]

    def add_records(self, found: int, imported: int):
        """Add to record counts."""
        self.progress["total_records"] += found
        self.progress["total_imported"] += imported
        self.save_checkpoint()


async def scrape_year_senate(
    year: int,
    progress: BackfillProgress,
    session: AsyncSession
) -> Dict:
    """
    Scrape Senate data for a specific year.

    Args:
        year: Year to scrape
        progress: Progress tracker
        session: Database session

    Returns:
        Dict with statistics
    """
    logger.info(f"Scraping Senate data for {year}")

    # Create data source record
    data_source = DataSource(
        source_type="senate",
        status="running",
        run_date=datetime.now(),
        source_metadata={"year": year, "backfill": True}
    )
    session.add(data_source)
    await session.commit()
    await session.refresh(data_source)

    try:
        progress.set_current_year("senate", year)

        # Scrape by quarters to avoid timeouts
        all_transactions = []
        validator = DataValidator()

        for quarter in range(1, 5):
            # Calculate date range for quarter
            start_month = (quarter - 1) * 3 + 1
            end_month = quarter * 3
            start_date = datetime(year, start_month, 1)

            if end_month == 12:
                end_date = datetime(year, 12, 31)
            else:
                end_date = datetime(year, end_month + 1, 1) - timedelta(days=1)

            logger.info(f"Scraping Senate Q{quarter} {year}: {start_date.date()} to {end_date.date()}")

            with SenateScraper(headless=True, rate_limit_delay=3.0) as scraper:
                try:
                    # Calculate days back from end_date
                    days_back = (end_date - start_date).days + 1
                    transactions = scraper.scrape_recent_transactions(days_back=days_back)
                    all_transactions.extend(transactions)
                    logger.info(f"Found {len(transactions)} transactions in Q{quarter}")
                except Exception as e:
                    logger.error(f"Error scraping Senate Q{quarter} {year}: {e}")
                    continue

        # Validate and clean
        data_source.records_found = len(all_transactions)
        valid_transactions, invalid_transactions = validator.validate_batch(all_transactions)
        data_source.records_invalid = len(invalid_transactions)

        # Import to database
        records_imported = await _import_transactions(session, valid_transactions)

        # Update data source
        data_source.mark_completed(
            records_imported=records_imported,
            records_skipped=len(valid_transactions) - records_imported,
            records_invalid=data_source.records_invalid
        )
        await session.commit()

        # Mark year complete
        progress.mark_year_complete("senate", year)
        progress.add_records(data_source.records_found, records_imported)

        logger.info(
            f"Senate {year} complete: {records_imported} imported, "
            f"{data_source.records_skipped} skipped, {data_source.records_invalid} invalid"
        )

        return {
            "year": year,
            "source": "senate",
            "records_found": data_source.records_found,
            "records_imported": records_imported,
        }

    except Exception as e:
        logger.error(f"Senate {year} failed: {e}", exc_info=True)
        data_source.mark_failed(str(e))
        await session.commit()
        raise


async def scrape_year_house(
    year: int,
    progress: BackfillProgress,
    session: AsyncSession
) -> Dict:
    """
    Scrape House data for a specific year.

    Args:
        year: Year to scrape
        progress: Progress tracker
        session: Database session

    Returns:
        Dict with statistics
    """
    logger.info(f"Scraping House data for {year}")

    # Create data source record
    data_source = DataSource(
        source_type="house",
        status="running",
        run_date=datetime.now(),
        source_metadata={"year": year, "backfill": True}
    )
    session.add(data_source)
    await session.commit()
    await session.refresh(data_source)

    try:
        progress.set_current_year("house", year)

        # Scrape by quarters
        all_transactions = []
        validator = DataValidator()

        for quarter in range(1, 5):
            start_month = (quarter - 1) * 3 + 1
            end_month = quarter * 3
            start_date = datetime(year, start_month, 1)

            if end_month == 12:
                end_date = datetime(year, 12, 31)
            else:
                end_date = datetime(year, end_month + 1, 1) - timedelta(days=1)

            logger.info(f"Scraping House Q{quarter} {year}: {start_date.date()} to {end_date.date()}")

            with HouseScraper(headless=True, rate_limit_delay=3.0) as scraper:
                try:
                    days_back = (end_date - start_date).days + 1
                    transactions = scraper.scrape_recent_transactions(days_back=days_back)
                    all_transactions.extend(transactions)
                    logger.info(f"Found {len(transactions)} transactions in Q{quarter}")
                except Exception as e:
                    logger.error(f"Error scraping House Q{quarter} {year}: {e}")
                    continue

        # Validate and clean
        data_source.records_found = len(all_transactions)
        valid_transactions, invalid_transactions = validator.validate_batch(all_transactions)
        data_source.records_invalid = len(invalid_transactions)

        # Import to database
        records_imported = await _import_transactions(session, valid_transactions)

        # Update data source
        data_source.mark_completed(
            records_imported=records_imported,
            records_skipped=len(valid_transactions) - records_imported,
            records_invalid=data_source.records_invalid
        )
        await session.commit()

        # Mark year complete
        progress.mark_year_complete("house", year)
        progress.add_records(data_source.records_found, records_imported)

        logger.info(
            f"House {year} complete: {records_imported} imported, "
            f"{data_source.records_skipped} skipped, {data_source.records_invalid} invalid"
        )

        return {
            "year": year,
            "source": "house",
            "records_found": data_source.records_found,
            "records_imported": records_imported,
        }

    except Exception as e:
        logger.error(f"House {year} failed: {e}", exc_info=True)
        data_source.mark_failed(str(e))
        await session.commit()
        raise


async def _import_transactions(session: AsyncSession, transactions: List[Dict]) -> int:
    """Import transactions to database."""
    imported = 0

    for trans in transactions:
        try:
            # Get or create politician
            stmt = select(Politician).where(
                Politician.name == trans["politician_name"],
                Politician.chamber == trans["chamber"]
            )
            result = await session.execute(stmt)
            politician = result.scalar_one_or_none()

            if not politician:
                politician = Politician(
                    name=trans["politician_name"],
                    chamber=trans["chamber"],
                )
                session.add(politician)
                await session.flush()

            # Check if trade exists
            stmt = select(Trade).where(
                Trade.politician_id == politician.id,
                Trade.ticker == trans["ticker"],
                Trade.transaction_date == trans["transaction_date"],
                Trade.transaction_type == trans["transaction_type"]
            )
            result = await session.execute(stmt)
            existing_trade = result.scalar_one_or_none()

            if existing_trade:
                continue

            # Create trade
            trade = Trade(
                politician_id=politician.id,
                ticker=trans["ticker"],
                transaction_type=trans["transaction_type"],
                amount_min=trans.get("amount_min"),
                amount_max=trans.get("amount_max"),
                transaction_date=trans["transaction_date"],
                disclosure_date=trans.get("disclosure_date", trans["transaction_date"]),
                source_url=trans.get("source_url"),
                raw_data=trans.get("raw_data"),
            )
            session.add(trade)
            imported += 1

        except Exception as e:
            logger.error(f"Error importing transaction: {e}")
            continue

    await session.commit()
    return imported


async def run_backfill(
    start_year: int,
    end_year: int,
    senate_only: bool = False,
    house_only: bool = False,
    resume: bool = False
):
    """
    Run the backfill process.

    Args:
        start_year: Start year
        end_year: End year
        senate_only: Only scrape Senate
        house_only: Only scrape House
        resume: Resume from checkpoint
    """
    logger.info(f"Starting backfill: {start_year}-{end_year}")

    # Initialize progress tracker
    progress = BackfillProgress(CHECKPOINT_FILE)

    if resume:
        logger.info(f"Resuming from checkpoint: {progress.progress}")

    # Create database session
    engine = create_async_engine(settings.DATABASE_URL, echo=False)
    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

    # Process each year
    for year in range(start_year, end_year + 1):
        async with async_session() as session:
            # Senate
            if not house_only:
                if not progress.is_year_complete("senate", year) or not resume:
                    try:
                        await scrape_year_senate(year, progress, session)
                    except Exception as e:
                        logger.error(f"Failed to scrape Senate {year}: {e}")
                        # Continue to next year
                else:
                    logger.info(f"Senate {year} already complete, skipping")

            # House
            if not senate_only:
                if not progress.is_year_complete("house", year) or not resume:
                    try:
                        await scrape_year_house(year, progress, session)
                    except Exception as e:
                        logger.error(f"Failed to scrape House {year}: {e}")
                        # Continue to next year
                else:
                    logger.info(f"House {year} already complete, skipping")

    logger.info(
        f"Backfill complete! Total: {progress.progress['total_imported']} records imported "
        f"out of {progress.progress['total_records']} found"
    )


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description="Backfill historical congressional trading data")
    parser.add_argument(
        "--start-year",
        type=int,
        default=2012,
        help="Start year (default: 2012)"
    )
    parser.add_argument(
        "--end-year",
        type=int,
        default=datetime.now().year,
        help="End year (default: current year)"
    )
    parser.add_argument(
        "--senate-only",
        action="store_true",
        help="Only scrape Senate data"
    )
    parser.add_argument(
        "--house-only",
        action="store_true",
        help="Only scrape House data"
    )
    parser.add_argument(
        "--resume",
        action="store_true",
        help="Resume from checkpoint"
    )

    args = parser.parse_args()

    # Run backfill
    asyncio.run(run_backfill(
        start_year=args.start_year,
        end_year=args.end_year,
        senate_only=args.senate_only,
        house_only=args.house_only,
        resume=args.resume
    ))


if __name__ == "__main__":
    main()
