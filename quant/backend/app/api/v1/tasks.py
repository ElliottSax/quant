"""API endpoints for task management and monitoring."""

import logging
from typing import Dict, Any
from fastapi import APIRouter, HTTPException, Query, Depends
from pydantic import BaseModel, Field
from celery.result import AsyncResult

from app.celery_app import celery_app
from app.tasks.scraper_tasks import scrape_senate, scrape_house, scrape_all_chambers
from app.core.deps import get_current_active_user
from app.models.user import User

router = APIRouter(prefix="/tasks", tags=["tasks"])
logger = logging.getLogger(__name__)


class TaskResponse(BaseModel):
    """Response model for task submission."""

    task_id: str = Field(..., description="Celery task ID")
    status: str = Field(..., description="Task status")
    message: str = Field(..., description="Status message")


class TaskStatusResponse(BaseModel):
    """Response model for task status."""

    task_id: str
    status: str
    result: Dict[str, Any] | None = None
    error: str | None = None


class ScraperRequest(BaseModel):
    """Request model for scraper tasks."""

    start_date: str | None = Field(None, description="Start date (YYYY-MM-DD)")
    end_date: str | None = Field(None, description="End date (YYYY-MM-DD)")
    days_back: int = Field(1, description="Number of days back to scrape", ge=1, le=365)


@router.post("/scrape/senate", response_model=TaskResponse)
async def trigger_senate_scraper(
    request: ScraperRequest,
    current_user: User = Depends(get_current_active_user),
) -> TaskResponse:
    """
    Trigger Senate scraper task.

    This endpoint queues a background task to scrape Senate financial disclosures.
    Use the returned task_id to check status.

    Requires authentication.
    """
    try:
        task = scrape_senate.delay(
            start_date=request.start_date,
            end_date=request.end_date,
            days_back=request.days_back,
        )

        logger.info(f"Senate scraper task queued by {current_user.username}: {task.id}")

        return TaskResponse(
            task_id=task.id,
            status="queued",
            message="Senate scraper task has been queued",
        )

    except Exception as e:
        logger.error(f"Failed to queue Senate scraper: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/scrape/house", response_model=TaskResponse)
async def trigger_house_scraper(
    request: ScraperRequest,
    current_user: User = Depends(get_current_active_user),
) -> TaskResponse:
    """
    Trigger House scraper task.

    This endpoint queues a background task to scrape House financial disclosures.
    Use the returned task_id to check status.

    Requires authentication.
    """
    try:
        task = scrape_house.delay(
            start_date=request.start_date,
            end_date=request.end_date,
            days_back=request.days_back,
        )

        logger.info(f"House scraper task queued by {current_user.username}: {task.id}")

        return TaskResponse(
            task_id=task.id,
            status="queued",
            message="House scraper task has been queued",
        )

    except Exception as e:
        logger.error(f"Failed to queue House scraper: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/scrape/all", response_model=TaskResponse)
async def trigger_all_scrapers(
    request: ScraperRequest,
    current_user: User = Depends(get_current_active_user),
) -> TaskResponse:
    """
    Trigger both Senate and House scraper tasks.

    This endpoint queues a background task to scrape both chambers.
    Use the returned task_id to check status.

    Requires authentication.
    """
    try:
        task = scrape_all_chambers.delay(
            start_date=request.start_date,
            end_date=request.end_date,
            days_back=request.days_back,
        )

        logger.info(f"Combined scraper task queued by {current_user.username}: {task.id}")

        return TaskResponse(
            task_id=task.id,
            status="queued",
            message="Combined scraper task has been queued",
        )

    except Exception as e:
        logger.error(f"Failed to queue combined scraper: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/status/{task_id}", response_model=TaskStatusResponse)
async def get_task_status(
    task_id: str,
    current_user: User = Depends(get_current_active_user),
) -> TaskStatusResponse:
    """
    Get status of a task by ID.

    Returns the current status and result (if completed) of the task.

    Requires authentication.
    """
    try:
        task_result = AsyncResult(task_id, app=celery_app)

        response = TaskStatusResponse(
            task_id=task_id,
            status=task_result.status,
        )

        if task_result.ready():
            if task_result.successful():
                response.result = task_result.result
            else:
                response.error = str(task_result.info)

        return response

    except Exception as e:
        logger.error(f"Failed to get task status: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/active")
async def get_active_tasks(
    current_user: User = Depends(get_current_active_user),
) -> Dict[str, Any]:
    """
    Get list of active tasks.

    Returns information about currently running tasks.

    Requires authentication.
    """
    try:
        # Get active tasks from all workers
        inspect = celery_app.control.inspect()
        active = inspect.active()

        if not active:
            return {"active_tasks": [], "worker_count": 0}

        # Flatten task list
        all_tasks = []
        for worker, tasks in active.items():
            for task in tasks:
                all_tasks.append({
                    "worker": worker,
                    "task_id": task.get("id"),
                    "task_name": task.get("name"),
                    "args": task.get("args"),
                    "kwargs": task.get("kwargs"),
                })

        return {
            "active_tasks": all_tasks,
            "worker_count": len(active),
        }

    except Exception as e:
        logger.error(f"Failed to get active tasks: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/scheduled")
async def get_scheduled_tasks(
    current_user: User = Depends(get_current_active_user),
) -> Dict[str, Any]:
    """
    Get list of scheduled (reserved) tasks.

    Returns information about tasks waiting to be executed.

    Requires authentication.
    """
    try:
        inspect = celery_app.control.inspect()
        scheduled = inspect.scheduled()

        if not scheduled:
            return {"scheduled_tasks": [], "worker_count": 0}

        # Flatten task list
        all_tasks = []
        for worker, tasks in scheduled.items():
            for task in tasks:
                all_tasks.append({
                    "worker": worker,
                    "task_id": task.get("id"),
                    "task_name": task.get("name"),
                    "eta": task.get("eta"),
                })

        return {
            "scheduled_tasks": all_tasks,
            "worker_count": len(scheduled),
        }

    except Exception as e:
        logger.error(f"Failed to get scheduled tasks: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/stats")
async def get_worker_stats(
    current_user: User = Depends(get_current_active_user),
) -> Dict[str, Any]:
    """
    Get worker statistics.

    Returns statistics about Celery workers including pool size,
    active tasks, and processed tasks.

    Requires authentication.
    """
    try:
        inspect = celery_app.control.inspect()

        stats = inspect.stats()
        active = inspect.active()

        if not stats:
            return {
                "status": "no_workers",
                "message": "No Celery workers are currently running",
            }

        worker_info = {}
        for worker, worker_stats in stats.items():
            worker_info[worker] = {
                "pool_size": worker_stats.get("pool", {}).get("max-concurrency"),
                "active_tasks": len(active.get(worker, [])) if active else 0,
                "total_tasks": worker_stats.get("total", {}),
            }

        return {
            "status": "ok",
            "workers": worker_info,
            "worker_count": len(stats),
        }

    except Exception as e:
        logger.error(f"Failed to get worker stats: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/cancel/{task_id}")
async def cancel_task(
    task_id: str,
    current_user: User = Depends(get_current_active_user),
) -> Dict[str, Any]:
    """
    Cancel a running or queued task.

    Attempts to terminate the task if it's currently running.

    Requires authentication.
    """
    try:
        task_result = AsyncResult(task_id, app=celery_app)
        task_result.revoke(terminate=True)

        logger.info(f"Task {task_id} cancelled by {current_user.username}")

        return {
            "status": "cancelled",
            "task_id": task_id,
            "message": "Task has been cancelled",
        }

    except Exception as e:
        logger.error(f"Failed to cancel task: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/health")
async def health_check() -> Dict[str, Any]:
    """
    Health check endpoint for task system.

    Verifies that Celery workers are running and Redis is accessible.
    """
    try:
        # Check if workers are responding
        inspect = celery_app.control.inspect()
        stats = inspect.stats()

        if not stats:
            return {
                "status": "unhealthy",
                "message": "No Celery workers are running",
                "workers": 0,
            }

        return {
            "status": "healthy",
            "message": "Task system is operational",
            "workers": len(stats),
        }

    except Exception as e:
        logger.error(f"Health check failed: {e}", exc_info=True)
        return {
            "status": "unhealthy",
            "message": str(e),
            "workers": 0,
        }
