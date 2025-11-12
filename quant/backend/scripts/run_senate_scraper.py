#!/usr/bin/env python3
"""CLI script to run Senate scraper."""

import asyncio
import logging
import sys
from datetime import date, timedelta
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker

from app.core.config import settings
from app.services.scraper_service import run_senate_scraper

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler("scraper.log"),
    ],
)

logger = logging.getLogger(__name__)


async def main():
    """Run Senate scraper."""
    logger.info("=" * 80)
    logger.info("Senate Financial Disclosure Scraper")
    logger.info("=" * 80)

    # Parse command line arguments
    import argparse

    parser = argparse.ArgumentParser(description="Scrape Senate financial disclosures")
    parser.add_argument(
        "--start-date",
        type=str,
        help="Start date (YYYY-MM-DD). Default: 30 days ago",
    )
    parser.add_argument(
        "--end-date",
        type=str,
        help="End date (YYYY-MM-DD). Default: today",
    )
    parser.add_argument(
        "--no-headless",
        action="store_true",
        help="Run browser in visible mode (not headless)",
    )
    parser.add_argument(
        "--days-back",
        type=int,
        default=30,
        help="Number of days back to scrape. Default: 30",
    )

    args = parser.parse_args()

    # Parse dates
    end_date = date.today()
    if args.end_date:
        try:
            end_date = date.fromisoformat(args.end_date)
        except ValueError:
            logger.error(f"Invalid end date format: {args.end_date}. Use YYYY-MM-DD")
            return 1

    start_date = end_date - timedelta(days=args.days_back)
    if args.start_date:
        try:
            start_date = date.fromisoformat(args.start_date)
        except ValueError:
            logger.error(f"Invalid start date format: {args.start_date}. Use YYYY-MM-DD")
            return 1

    logger.info(f"Scraping period: {start_date} to {end_date}")
    logger.info(f"Headless mode: {not args.no_headless}")

    # Create database engine
    engine = create_async_engine(
        settings.DATABASE_URL,
        echo=False,
        pool_pre_ping=True,
    )

    async_session = async_sessionmaker(
        engine,
        class_=AsyncSession,
        expire_on_commit=False,
    )

    try:
        async with async_session() as session:
            # Run scraper
            stats = await run_senate_scraper(
                db=session,
                start_date=start_date,
                end_date=end_date,
                headless=not args.no_headless,
            )

            logger.info("=" * 80)
            logger.info("Scraping Results:")
            logger.info(f"  Total processed: {stats['total']}")
            logger.info(f"  Successfully saved: {stats['saved']}")
            logger.info(f"  Skipped (duplicates): {stats['skipped']}")
            logger.info(f"  Errors: {stats['errors']}")
            logger.info("=" * 80)

            return 0

    except KeyboardInterrupt:
        logger.info("\nScraping interrupted by user")
        return 130

    except Exception as e:
        logger.error(f"Scraping failed: {e}", exc_info=True)
        return 1

    finally:
        await engine.dispose()


if __name__ == "__main__":
    try:
        exit_code = asyncio.run(main())
        sys.exit(exit_code)
    except KeyboardInterrupt:
        logger.info("\nExiting...")
        sys.exit(130)
