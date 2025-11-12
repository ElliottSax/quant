"""Celery tasks for congressional trading scrapers."""

import logging
from datetime import date, timedelta
from typing import Dict, Any

from celery import Task
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker

from app.celery_app import celery_app
from app.core.config import settings
from app.services.scraper_service import run_senate_scraper, run_house_scraper, run_all_scrapers

logger = logging.getLogger(__name__)


class DatabaseTask(Task):
    """Base task that provides database session."""

    _engine = None
    _session_maker = None

    @property
    def engine(self):
        """Lazy initialize database engine."""
        if self._engine is None:
            self._engine = create_async_engine(
                settings.DATABASE_URL,
                echo=False,
                pool_pre_ping=True,
                pool_size=5,
                max_overflow=10,
            )
        return self._engine

    @property
    def session_maker(self):
        """Lazy initialize session maker."""
        if self._session_maker is None:
            self._session_maker = async_sessionmaker(
                self.engine,
                class_=AsyncSession,
                expire_on_commit=False,
            )
        return self._session_maker


@celery_app.task(
    name="app.tasks.scraper_tasks.scrape_senate",
    base=DatabaseTask,
    bind=True,
    max_retries=3,
    default_retry_delay=300,  # 5 minutes
)
def scrape_senate(
    self,
    start_date: str | None = None,
    end_date: str | None = None,
    days_back: int = 1,
) -> Dict[str, Any]:
    """
    Scrape Senate financial disclosures.

    Args:
        start_date: Start date (ISO format YYYY-MM-DD)
        end_date: End date (ISO format YYYY-MM-DD)
        days_back: Number of days back to scrape if start_date not provided

    Returns:
        Dictionary with scraping statistics
    """
    import asyncio

    logger.info(f"Starting Senate scraper task (days_back={days_back})")

    try:
        # Parse dates
        if start_date:
            start = date.fromisoformat(start_date)
        else:
            start = date.today() - timedelta(days=days_back)

        if end_date:
            end = date.fromisoformat(end_date)
        else:
            end = date.today()

        # Run scraper
        async def run():
            async with self.session_maker() as session:
                return await run_senate_scraper(
                    db=session,
                    start_date=start,
                    end_date=end,
                    headless=True,
                )

        stats = asyncio.run(run())

        logger.info(f"Senate scraper completed: {stats}")
        return {
            "status": "success",
            "chamber": "senate",
            "stats": stats,
            "start_date": start.isoformat(),
            "end_date": end.isoformat(),
        }

    except Exception as exc:
        logger.error(f"Senate scraper failed: {exc}", exc_info=True)

        # Retry on failure
        if self.request.retries < self.max_retries:
            logger.info(f"Retrying Senate scraper (attempt {self.request.retries + 1}/{self.max_retries})")
            raise self.retry(exc=exc)

        return {
            "status": "error",
            "chamber": "senate",
            "error": str(exc),
            "start_date": start.isoformat() if 'start' in locals() else None,
            "end_date": end.isoformat() if 'end' in locals() else None,
        }


@celery_app.task(
    name="app.tasks.scraper_tasks.scrape_house",
    base=DatabaseTask,
    bind=True,
    max_retries=3,
    default_retry_delay=300,  # 5 minutes
)
def scrape_house(
    self,
    start_date: str | None = None,
    end_date: str | None = None,
    days_back: int = 1,
) -> Dict[str, Any]:
    """
    Scrape House financial disclosures.

    Args:
        start_date: Start date (ISO format YYYY-MM-DD)
        end_date: End date (ISO format YYYY-MM-DD)
        days_back: Number of days back to scrape if start_date not provided

    Returns:
        Dictionary with scraping statistics
    """
    import asyncio

    logger.info(f"Starting House scraper task (days_back={days_back})")

    try:
        # Parse dates
        if start_date:
            start = date.fromisoformat(start_date)
        else:
            start = date.today() - timedelta(days=days_back)

        if end_date:
            end = date.fromisoformat(end_date)
        else:
            end = date.today()

        # Run scraper
        async def run():
            async with self.session_maker() as session:
                return await run_house_scraper(
                    db=session,
                    start_date=start,
                    end_date=end,
                    headless=True,
                )

        stats = asyncio.run(run())

        logger.info(f"House scraper completed: {stats}")
        return {
            "status": "success",
            "chamber": "house",
            "stats": stats,
            "start_date": start.isoformat(),
            "end_date": end.isoformat(),
        }

    except Exception as exc:
        logger.error(f"House scraper failed: {exc}", exc_info=True)

        # Retry on failure
        if self.request.retries < self.max_retries:
            logger.info(f"Retrying House scraper (attempt {self.request.retries + 1}/{self.max_retries})")
            raise self.retry(exc=exc)

        return {
            "status": "error",
            "chamber": "house",
            "error": str(exc),
            "start_date": start.isoformat() if 'start' in locals() else None,
            "end_date": end.isoformat() if 'end' in locals() else None,
        }


@celery_app.task(
    name="app.tasks.scraper_tasks.scrape_all_chambers",
    base=DatabaseTask,
    bind=True,
)
def scrape_all_chambers(
    self,
    start_date: str | None = None,
    end_date: str | None = None,
    days_back: int = 1,
) -> Dict[str, Any]:
    """
    Scrape both Senate and House financial disclosures.

    Args:
        start_date: Start date (ISO format YYYY-MM-DD)
        end_date: End date (ISO format YYYY-MM-DD)
        days_back: Number of days back to scrape if start_date not provided

    Returns:
        Dictionary with scraping statistics for both chambers
    """
    import asyncio

    logger.info(f"Starting combined scraper task (days_back={days_back})")

    try:
        # Parse dates
        if start_date:
            start = date.fromisoformat(start_date)
        else:
            start = date.today() - timedelta(days=days_back)

        if end_date:
            end = date.fromisoformat(end_date)
        else:
            end = date.today()

        # Run both scrapers
        async def run():
            async with self.session_maker() as session:
                return await run_all_scrapers(
                    db=session,
                    start_date=start,
                    end_date=end,
                    headless=True,
                )

        results = asyncio.run(run())

        # Calculate totals
        total_saved = 0
        total_errors = 0

        if "senate" in results and "saved" in results["senate"]:
            total_saved += results["senate"]["saved"]
            total_errors += results["senate"].get("errors", 0)

        if "house" in results and "saved" in results["house"]:
            total_saved += results["house"]["saved"]
            total_errors += results["house"].get("errors", 0)

        logger.info(f"Combined scraper completed: {total_saved} saved, {total_errors} errors")

        return {
            "status": "success",
            "results": results,
            "totals": {
                "saved": total_saved,
                "errors": total_errors,
            },
            "start_date": start.isoformat(),
            "end_date": end.isoformat(),
        }

    except Exception as exc:
        logger.error(f"Combined scraper failed: {exc}", exc_info=True)
        return {
            "status": "error",
            "error": str(exc),
            "start_date": start.isoformat() if 'start' in locals() else None,
            "end_date": end.isoformat() if 'end' in locals() else None,
        }


@celery_app.task(name="app.tasks.scraper_tasks.health_check")
def health_check() -> Dict[str, Any]:
    """
    Health check task to verify Celery workers are functioning.

    Returns:
        Dictionary with health status
    """
    from datetime import datetime, timezone

    return {
        "status": "healthy",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "worker": "celery",
    }


@celery_app.task(
    name="app.tasks.scraper_tasks.cleanup_old_results",
    bind=True,
)
def cleanup_old_results(self, days_old: int = 7) -> Dict[str, Any]:
    """
    Clean up old Celery task results from Redis.

    Args:
        days_old: Remove results older than this many days

    Returns:
        Dictionary with cleanup statistics
    """
    from datetime import datetime, timezone

    logger.info(f"Starting cleanup of results older than {days_old} days")

    try:
        # Get all result keys
        from celery.result import AsyncResult

        # This is a placeholder - actual implementation would iterate through
        # result keys in Redis and delete old ones

        logger.info("Cleanup completed")
        return {
            "status": "success",
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "days_old": days_old,
        }

    except Exception as exc:
        logger.error(f"Cleanup failed: {exc}", exc_info=True)
        return {
            "status": "error",
            "error": str(exc),
        }
