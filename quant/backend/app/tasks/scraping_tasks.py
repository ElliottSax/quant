"""
Celery Tasks for Automated Data Collection

Background tasks for scraping congressional trading data from Senate and House.
Scheduled to run daily at 6 AM EST.
"""

import logging
from typing import Dict, List
from datetime import datetime, timedelta

from celery import Celery
from celery.schedules import crontab

from app.core.config import settings

logger = logging.getLogger(__name__)

# Initialize Celery
celery_app = Celery(
    'quant_scraping',
    broker=settings.REDIS_URL,
    backend=settings.REDIS_URL
)

celery_app.conf.update(
    task_serializer='json',
    accept_content=['json'],
    result_serializer='json',
    timezone='America/New_York',  # EST
    enable_utc=False,
    task_track_started=True,
    task_time_limit=3600,  # 1 hour max
    task_soft_time_limit=3000,  # 50 minutes soft limit
    task_acks_late=True,
    worker_prefetch_multiplier=1,
)


@celery_app.task(
    name='scrape_senate_daily',
    bind=True,
    max_retries=3,
    autoretry_for=(Exception,),
    retry_backoff=True,
    retry_jitter=True,
)
def scrape_senate_daily(self, days_back: int = 7):
    """
    Scrape Senate trading data daily.

    Args:
        days_back: Number of days to look back (default: 7)

    Returns:
        Dict with scraping statistics
    """
    import asyncio
    from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
    from sqlalchemy.orm import sessionmaker
    from app.scrapers import SenateScraper, DataValidator
    from app.models import DataSource

    logger.info(f"Starting Senate scraping task (days_back={days_back})")

    # Create data source record
    async def _scrape():
        engine = create_async_engine(settings.DATABASE_URL, echo=False)
        async_session = sessionmaker(
            engine, class_=AsyncSession, expire_on_commit=False
        )

        async with async_session() as session:
            # Create data source record
            data_source = DataSource(
                source_type="senate",
                status="running",
                run_date=datetime.now(),
                source_metadata={"days_back": days_back}
            )
            session.add(data_source)
            await session.commit()
            await session.refresh(data_source)

            try:
                # Run scraper
                validator = DataValidator()
                transactions = []

                with SenateScraper(headless=True) as scraper:
                    raw_transactions = scraper.scrape_recent_transactions(days_back=days_back)
                    data_source.records_found = len(raw_transactions)

                    # Validate and clean
                    valid_transactions, invalid_transactions = validator.validate_batch(
                        raw_transactions
                    )

                    data_source.records_invalid = len(invalid_transactions)
                    transactions = valid_transactions

                # Import to database
                records_imported = await _import_transactions(session, transactions)

                # Update data source
                data_source.mark_completed(
                    records_imported=records_imported,
                    records_skipped=len(transactions) - records_imported,
                    records_invalid=len(invalid_transactions) if invalid_transactions else 0
                )

                await session.commit()

                logger.info(
                    f"Senate scraping completed: {records_imported} imported, "
                    f"{data_source.records_skipped} skipped, "
                    f"{data_source.records_invalid} invalid"
                )

                return {
                    "success": True,
                    "source": "senate",
                    "records_found": data_source.records_found,
                    "records_imported": records_imported,
                    "records_skipped": data_source.records_skipped,
                    "records_invalid": data_source.records_invalid,
                }

            except Exception as e:
                logger.error(f"Senate scraping failed: {e}", exc_info=True)
                data_source.mark_failed(str(e))
                await session.commit()
                raise

    loop = asyncio.get_event_loop()
    return loop.run_until_complete(_scrape())


@celery_app.task(
    name='scrape_house_daily',
    bind=True,
    max_retries=3,
    autoretry_for=(Exception,),
    retry_backoff=True,
    retry_jitter=True,
)
def scrape_house_daily(self, days_back: int = 7):
    """
    Scrape House trading data daily.

    Args:
        days_back: Number of days to look back (default: 7)

    Returns:
        Dict with scraping statistics
    """
    import asyncio
    from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
    from sqlalchemy.orm import sessionmaker
    from app.scrapers import HouseScraper, DataValidator
    from app.models import DataSource

    logger.info(f"Starting House scraping task (days_back={days_back})")

    async def _scrape():
        engine = create_async_engine(settings.DATABASE_URL, echo=False)
        async_session = sessionmaker(
            engine, class_=AsyncSession, expire_on_commit=False
        )

        async with async_session() as session:
            # Create data source record
            data_source = DataSource(
                source_type="house",
                status="running",
                run_date=datetime.now(),
                source_metadata={"days_back": days_back}
            )
            session.add(data_source)
            await session.commit()
            await session.refresh(data_source)

            try:
                # Run scraper
                validator = DataValidator()
                transactions = []

                with HouseScraper(headless=True) as scraper:
                    raw_transactions = scraper.scrape_recent_transactions(days_back=days_back)
                    data_source.records_found = len(raw_transactions)

                    # Validate and clean
                    valid_transactions, invalid_transactions = validator.validate_batch(
                        raw_transactions
                    )

                    data_source.records_invalid = len(invalid_transactions)
                    transactions = valid_transactions

                # Import to database
                records_imported = await _import_transactions(session, transactions)

                # Update data source
                data_source.mark_completed(
                    records_imported=records_imported,
                    records_skipped=len(transactions) - records_imported,
                    records_invalid=len(invalid_transactions) if invalid_transactions else 0
                )

                await session.commit()

                logger.info(
                    f"House scraping completed: {records_imported} imported, "
                    f"{data_source.records_skipped} skipped, "
                    f"{data_source.records_invalid} invalid"
                )

                return {
                    "success": True,
                    "source": "house",
                    "records_found": data_source.records_found,
                    "records_imported": records_imported,
                    "records_skipped": data_source.records_skipped,
                    "records_invalid": data_source.records_invalid,
                }

            except Exception as e:
                logger.error(f"House scraping failed: {e}", exc_info=True)
                data_source.mark_failed(str(e))
                await session.commit()
                raise

    loop = asyncio.get_event_loop()
    return loop.run_until_complete(_scrape())


async def _import_transactions(session, transactions: List[Dict]) -> int:
    """
    Import transactions to database.

    Args:
        session: Database session
        transactions: List of transaction dictionaries

    Returns:
        Number of records imported
    """
    from sqlalchemy import select
    from app.models import Politician, Trade

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

            # Check if trade already exists
            stmt = select(Trade).where(
                Trade.politician_id == politician.id,
                Trade.ticker == trans["ticker"],
                Trade.transaction_date == trans["transaction_date"],
                Trade.transaction_type == trans["transaction_type"]
            )
            result = await session.execute(stmt)
            existing_trade = result.scalar_one_or_none()

            if existing_trade:
                logger.debug(f"Trade already exists: {trans['ticker']} on {trans['transaction_date']}")
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


@celery_app.task(name='scrape_all_daily')
def scrape_all_daily(days_back: int = 7):
    """
    Scrape both Senate and House data.

    Args:
        days_back: Number of days to look back

    Returns:
        Dict with combined statistics
    """
    from celery import group

    logger.info("Starting combined scraping task")

    # Run both scrapers in parallel
    job = group([
        scrape_senate_daily.s(days_back),
        scrape_house_daily.s(days_back),
    ])

    result = job.apply_async()
    results = result.get()

    # Combine results
    total_found = sum(r.get("records_found", 0) for r in results)
    total_imported = sum(r.get("records_imported", 0) for r in results)
    total_skipped = sum(r.get("records_skipped", 0) for r in results)
    total_invalid = sum(r.get("records_invalid", 0) for r in results)

    logger.info(
        f"Combined scraping completed: {total_imported} imported, "
        f"{total_skipped} skipped, {total_invalid} invalid out of {total_found} found"
    )

    return {
        "success": True,
        "total_found": total_found,
        "total_imported": total_imported,
        "total_skipped": total_skipped,
        "total_invalid": total_invalid,
        "results": results,
    }


# Celery Beat schedule for periodic tasks
celery_app.conf.beat_schedule = {
    'scrape-senate-daily': {
        'task': 'scrape_senate_daily',
        'schedule': crontab(hour=6, minute=0),  # 6 AM EST daily
        'args': (7,)  # Look back 7 days
    },
    'scrape-house-daily': {
        'task': 'scrape_house_daily',
        'schedule': crontab(hour=6, minute=30),  # 6:30 AM EST daily
        'args': (7,)
    },
}


# Error handling
@celery_app.task(bind=True)
def error_handler(self, uuid):
    """Handle task errors and send alerts."""
    from app.core.alerts import send_alert

    result = celery_app.AsyncResult(uuid)
    exc = result.info.get('exc_type', '')
    error_msg = result.info.get('exc_message', '')

    logger.error(f"Task {uuid} failed: {exc} - {error_msg}")

    # Send alert (implement based on your alerting system)
    send_alert(
        title="Scraping Task Failed",
        message=f"Task {uuid} failed with error: {exc} - {error_msg}",
        severity="error"
    )


# Usage examples
"""
# Start Celery worker:
celery -A app.tasks.scraping_tasks worker --loglevel=info

# Start Celery beat scheduler:
celery -A app.tasks.scraping_tasks beat --loglevel=info

# Trigger tasks manually:
from app.tasks.scraping_tasks import scrape_senate_daily, scrape_house_daily

# Scrape senate (last 7 days)
scrape_senate_daily.delay(7)

# Scrape house (last 30 days)
scrape_house_daily.delay(30)

# Scrape both
from app.tasks.scraping_tasks import scrape_all_daily
scrape_all_daily.delay(7)
"""
