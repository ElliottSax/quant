#!/usr/bin/env python3
"""CLI script to run congressional trading scrapers."""

import asyncio
import logging
import sys
from datetime import date, timedelta
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker

from app.core.config import settings
from app.services.scraper_service import (
    run_senate_scraper,
    run_house_scraper,
    run_all_scrapers,
)

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


def print_stats(stats: dict[str, int], chamber: str = "") -> None:
    """Print scraper statistics."""
    prefix = f"{chamber} " if chamber else ""
    logger.info("=" * 80)
    logger.info(f"{prefix}Scraping Results:")

    if "error" in stats:
        logger.error(f"  Error: {stats['error']}")
    else:
        logger.info(f"  Total processed: {stats.get('total', 0)}")
        logger.info(f"  Successfully saved: {stats.get('saved', 0)}")
        logger.info(f"  Skipped (duplicates): {stats.get('skipped', 0)}")
        logger.info(f"  Errors: {stats.get('errors', 0)}")

    logger.info("=" * 80)


async def main():
    """Run congressional trading scrapers."""
    logger.info("=" * 80)
    logger.info("Congressional Financial Disclosure Scraper")
    logger.info("=" * 80)

    # Parse command line arguments
    import argparse

    parser = argparse.ArgumentParser(
        description="Scrape congressional financial disclosures",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Scrape both Senate and House for last 30 days
  python run_scrapers.py --chamber all

  # Scrape only Senate
  python run_scrapers.py --chamber senate

  # Scrape only House
  python run_scrapers.py --chamber house

  # Custom date range
  python run_scrapers.py --chamber all --start-date 2024-01-01 --end-date 2024-01-31

  # Run in visible browser mode for debugging
  python run_scrapers.py --chamber senate --no-headless
        """,
    )
    parser.add_argument(
        "--chamber",
        type=str,
        choices=["senate", "house", "all"],
        default="all",
        help="Which chamber to scrape. Default: all",
    )
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

    logger.info(f"Chamber: {args.chamber}")
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
            # Run appropriate scraper(s)
            if args.chamber == "all":
                logger.info("Running both Senate and House scrapers...")
                results = await run_all_scrapers(
                    db=session,
                    start_date=start_date,
                    end_date=end_date,
                    headless=not args.no_headless,
                )

                # Print results for both
                if "senate" in results:
                    print_stats(results["senate"], "Senate")
                if "house" in results:
                    print_stats(results["house"], "House")

                # Calculate totals
                total_saved = results.get("senate", {}).get("saved", 0) + results.get("house", {}).get("saved", 0)
                total_errors = results.get("senate", {}).get("errors", 0) + results.get("house", {}).get("errors", 0)

                logger.info("=" * 80)
                logger.info("Combined Results:")
                logger.info(f"  Total saved: {total_saved}")
                logger.info(f"  Total errors: {total_errors}")
                logger.info("=" * 80)

            elif args.chamber == "senate":
                logger.info("Running Senate scraper...")
                stats = await run_senate_scraper(
                    db=session,
                    start_date=start_date,
                    end_date=end_date,
                    headless=not args.no_headless,
                )
                print_stats(stats, "Senate")

            elif args.chamber == "house":
                logger.info("Running House scraper...")
                stats = await run_house_scraper(
                    db=session,
                    start_date=start_date,
                    end_date=end_date,
                    headless=not args.no_headless,
                )
                print_stats(stats, "House")

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
