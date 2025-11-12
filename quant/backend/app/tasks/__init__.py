"""Celery tasks package."""

from app.tasks.scraper_tasks import (
    scrape_senate,
    scrape_house,
    scrape_all_chambers,
    health_check,
    cleanup_old_results,
)

__all__ = [
    "scrape_senate",
    "scrape_house",
    "scrape_all_chambers",
    "health_check",
    "cleanup_old_results",
]
