"""Celery application configuration."""

import logging
from celery import Celery
from celery.schedules import crontab
from celery.signals import task_prerun, task_postrun, task_failure

from app.core.config import settings

logger = logging.getLogger(__name__)

# Create Celery app
celery_app = Celery(
    "quant",
    broker=settings.CELERY_BROKER_URL,
    backend=settings.CELERY_RESULT_BACKEND,
    include=["app.tasks.scraper_tasks"],
)

# Celery configuration
celery_app.conf.update(
    # Task settings
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,

    # Task execution
    task_acks_late=True,  # Acknowledge after task completes
    task_reject_on_worker_lost=True,
    task_track_started=True,
    task_time_limit=3600,  # 1 hour hard limit
    task_soft_time_limit=3300,  # 55 minutes soft limit

    # Worker settings
    worker_prefetch_multiplier=1,  # One task at a time
    worker_max_tasks_per_child=10,  # Restart worker after 10 tasks (prevent memory leaks)

    # Result backend
    result_expires=86400,  # Keep results for 24 hours
    result_extended=True,

    # Beat schedule
    beat_schedule={
        # Daily scraping at 2 AM UTC
        "scrape-daily": {
            "task": "app.tasks.scraper_tasks.scrape_all_chambers",
            "schedule": crontab(hour=2, minute=0),  # Every day at 2:00 AM UTC
            "kwargs": {"days_back": 1},
        },
        # Weekly full sync on Sundays at 3 AM UTC
        "scrape-weekly": {
            "task": "app.tasks.scraper_tasks.scrape_all_chambers",
            "schedule": crontab(hour=3, minute=0, day_of_week=0),  # Sunday at 3:00 AM UTC
            "kwargs": {"days_back": 7},
        },
        # Health check every 5 minutes
        "health-check": {
            "task": "app.tasks.scraper_tasks.health_check",
            "schedule": 300,  # Every 5 minutes (interval is fine for frequent checks)
        },
    },
)


# Signal handlers for monitoring
@task_prerun.connect
def task_prerun_handler(sender=None, task_id=None, task=None, args=None, kwargs=None, **extra):
    """Log when task starts."""
    logger.info(f"Task {task.name}[{task_id}] starting with args={args}, kwargs={kwargs}")


@task_postrun.connect
def task_postrun_handler(sender=None, task_id=None, task=None, args=None, kwargs=None, retval=None, **extra):
    """Log when task completes."""
    logger.info(f"Task {task.name}[{task_id}] completed successfully")


@task_failure.connect
def task_failure_handler(sender=None, task_id=None, exception=None, args=None, kwargs=None, traceback=None, **extra):
    """Log when task fails."""
    logger.error(
        f"Task {sender.name}[{task_id}] failed with exception: {exception}",
        exc_info=True,
    )


if __name__ == "__main__":
    celery_app.start()
