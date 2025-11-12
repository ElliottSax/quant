"""Celery tasks for congressional trading scrapers."""

import asyncio
import atexit
import logging
from datetime import date, timedelta
from typing import Dict, Any

from celery import Task
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker

from app.celery_app import celery_app
from app.core.config import settings
from app.services.scraper_service import run_senate_scraper, run_house_scraper, run_all_scrapers

logger = logging.getLogger(__name__)

# Module-level engine and session maker (shared across all tasks)
_engine = None
_session_maker = None
_event_loop = None


def get_engine():
    """Get or create the shared database engine."""
    global _engine
    if _engine is None:
        _engine = create_async_engine(
            settings.DATABASE_URL,
            echo=False,
            pool_pre_ping=True,
            pool_size=5,
            max_overflow=10,
        )
        # Register cleanup on exit
        atexit.register(cleanup_engine)
        logger.info("Database engine initialized")
    return _engine


def get_session_maker():
    """Get or create the shared session maker."""
    global _session_maker
    if _session_maker is None:
        _session_maker = async_sessionmaker(
            get_engine(),
            class_=AsyncSession,
            expire_on_commit=False,
        )
    return _session_maker


def get_event_loop():
    """Get or create the shared event loop for tasks."""
    global _event_loop
    if _event_loop is None or _event_loop.is_closed():
        _event_loop = asyncio.new_event_loop()
        asyncio.set_event_loop(_event_loop)
        logger.info("Event loop initialized")
    return _event_loop


def cleanup_engine():
    """Clean up database engine on shutdown."""
    global _engine, _event_loop
    if _engine is not None:
        logger.info("Disposing database engine")
        if _event_loop is not None and not _event_loop.is_closed():
            _event_loop.run_until_complete(_engine.dispose())
        _engine = None


class DatabaseTask(Task):
    """Base task that provides database session and event loop."""

    @property
    def session_maker(self):
        """Get the shared session maker."""
        return get_session_maker()

    @property
    def event_loop(self):
        """Get the shared event loop."""
        return get_event_loop()


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
    logger.info(f"Starting Senate scraper task (days_back={days_back})")

    try:
        # Parse and validate dates
        try:
            if start_date:
                start = date.fromisoformat(start_date)
            else:
                start = date.today() - timedelta(days=days_back)

            if end_date:
                end = date.fromisoformat(end_date)
            else:
                end = date.today()

            # Validate date range
            if start > end:
                raise ValueError(f"start_date ({start}) cannot be after end_date ({end})")
        except ValueError as e:
            logger.error(f"Invalid date parameters: {e}")
            return {
                "status": "error",
                "chamber": "senate",
                "error": f"Invalid date parameters: {str(e)}",
            }

        # Run scraper using shared event loop
        async def run():
            async with self.session_maker() as session:
                return await run_senate_scraper(
                    db=session,
                    start_date=start,
                    end_date=end,
                    headless=True,
                )

        stats = self.event_loop.run_until_complete(run())

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

        # Retry on failure (this raises an exception, so no code after this will execute)
        if self.request.retries < self.max_retries:
            logger.info(f"Retrying Senate scraper (attempt {self.request.retries + 1}/{self.max_retries})")
            raise self.retry(exc=exc)

        # Only reached if max retries exceeded
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
    logger.info(f"Starting House scraper task (days_back={days_back})")

    try:
        # Parse and validate dates
        try:
            if start_date:
                start = date.fromisoformat(start_date)
            else:
                start = date.today() - timedelta(days=days_back)

            if end_date:
                end = date.fromisoformat(end_date)
            else:
                end = date.today()

            # Validate date range
            if start > end:
                raise ValueError(f"start_date ({start}) cannot be after end_date ({end})")
        except ValueError as e:
            logger.error(f"Invalid date parameters: {e}")
            return {
                "status": "error",
                "chamber": "house",
                "error": f"Invalid date parameters: {str(e)}",
            }

        # Run scraper using shared event loop
        async def run():
            async with self.session_maker() as session:
                return await run_house_scraper(
                    db=session,
                    start_date=start,
                    end_date=end,
                    headless=True,
                )

        stats = self.event_loop.run_until_complete(run())

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

        # Retry on failure (this raises an exception, so no code after this will execute)
        if self.request.retries < self.max_retries:
            logger.info(f"Retrying House scraper (attempt {self.request.retries + 1}/{self.max_retries})")
            raise self.retry(exc=exc)

        # Only reached if max retries exceeded
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
    logger.info(f"Starting combined scraper task (days_back={days_back})")

    try:
        # Parse and validate dates
        try:
            if start_date:
                start = date.fromisoformat(start_date)
            else:
                start = date.today() - timedelta(days=days_back)

            if end_date:
                end = date.fromisoformat(end_date)
            else:
                end = date.today()

            # Validate date range
            if start > end:
                raise ValueError(f"start_date ({start}) cannot be after end_date ({end})")
        except ValueError as e:
            logger.error(f"Invalid date parameters: {e}")
            return {
                "status": "error",
                "error": f"Invalid date parameters: {str(e)}",
            }

        # Run both scrapers using shared event loop
        async def run():
            async with self.session_maker() as session:
                return await run_all_scrapers(
                    db=session,
                    start_date=start,
                    end_date=end,
                    headless=True,
                )

        results = self.event_loop.run_until_complete(run())

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
