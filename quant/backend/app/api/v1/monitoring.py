"""
Enhanced Monitoring API Endpoints

Provides comprehensive monitoring and health check endpoints.
"""

from datetime import datetime, timezone
from typing import Optional

from fastapi import APIRouter, Query, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.monitoring import monitoring_service
from app.core.logging import get_logger
from app.services.alerting import alert_manager

logger = get_logger(__name__)

router = APIRouter(prefix="/monitoring", tags=["monitoring"])


@router.get("/metrics")
async def get_prometheus_metrics():
    """
    Get metrics in Prometheus format.

    This endpoint is scraped by Prometheus for metrics collection.
    """
    return monitoring_service.export_prometheus_metrics()


@router.get("/health")
async def health_check(db: AsyncSession = Depends(get_db)):
    """
    Comprehensive health check endpoint.

    Checks:
    - Database connectivity
    - Cache connectivity
    - System resources
    - Service dependencies

    Returns health status with detailed checks.
    """
    from sqlalchemy import text

    health_status = {
        "status": "healthy",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "version": "1.0.0",
        "checks": {}
    }

    all_healthy = True

    # Database check
    try:
        import time
        start_time = time.perf_counter()
        await db.execute(text("SELECT 1"))
        response_time = (time.perf_counter() - start_time) * 1000  # Convert to ms

        health_status["checks"]["database"] = {
            "status": "connected",
            "response_time_ms": round(response_time, 2)
        }
    except Exception as e:
        health_status["checks"]["database"] = {
            "status": "error",
            "error": str(e)
        }
        all_healthy = False

    # Cache check
    try:
        from app.core.cache import cache_manager
        if cache_manager.enabled and cache_manager.redis_client:
            await cache_manager.redis_client.ping()
            health_status["checks"]["cache"] = {
                "status": "connected",
                "type": "redis"
            }
        else:
            health_status["checks"]["cache"] = {
                "status": "disabled"
            }
    except Exception as e:
        health_status["checks"]["cache"] = {
            "status": "error",
            "error": str(e)
        }
        all_healthy = False

    # WebSocket check
    try:
        from app.api.v1.websocket import manager
        connection_count = manager.get_total_connections()
        health_status["checks"]["websocket"] = {
            "status": "healthy",
            "active_connections": connection_count
        }
    except Exception as e:
        health_status["checks"]["websocket"] = {
            "status": "error",
            "error": str(e)
        }

    # System resources check
    try:
        metrics = monitoring_service.get_metrics()
        health_status["checks"]["system"] = {
            "status": "healthy",
            "cpu_percent": metrics["cpu_percent"],
            "memory_percent": metrics["memory_percent"],
            "disk_percent": metrics["disk_percent"]
        }

        # Warn on high resource usage
        if metrics["cpu_percent"] > 80 or metrics["memory_percent"] > 85:
            health_status["checks"]["system"]["status"] = "warning"
            all_healthy = False

    except Exception as e:
        health_status["checks"]["system"] = {
            "status": "error",
            "error": str(e)
        }

    # Set overall status
    health_status["status"] = "healthy" if all_healthy else "degraded"

    return health_status


@router.get("/system")
async def get_system_metrics():
    """
    Get current system metrics.

    Returns:
    - CPU usage
    - Memory usage
    - Disk usage
    - Uptime
    - Active requests
    """
    metrics = monitoring_service.get_metrics()

    return {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "system": {
            "cpu_percent": metrics["cpu_percent"],
            "memory_percent": metrics["memory_percent"],
            "disk_percent": metrics["disk_percent"],
            "uptime_seconds": metrics["uptime_seconds"]
        },
        "application": {
            "active_requests": metrics["active_requests"]
        }
    }


@router.get("/alerts")
async def get_alert_history(
    limit: int = Query(default=50, ge=1, le=100),
    severity: Optional[str] = Query(default=None, regex="^(info|warning|critical)$")
):
    """
    Get recent alert history.

    **Parameters**:
    - **limit**: Number of alerts to return (1-100)
    - **severity**: Filter by severity level
    """
    alerts = alert_manager.get_recent_alerts(limit)

    # Filter by severity if specified
    if severity:
        alerts = [a for a in alerts if a["severity"] == severity]

    return {
        "alerts": alerts,
        "count": len(alerts)
    }


@router.post("/test-alert")
async def send_test_alert(
    severity: str = Query(default="info", regex="^(info|warning|critical)$")
):
    """
    Send a test alert to verify alerting configuration.

    **Parameters**:
    - **severity**: Alert severity level

    Useful for testing Slack/email/webhook integrations.
    """
    from app.services.alerting import AlertSeverity

    severity_enum = AlertSeverity(severity)

    await alert_manager.send_alert(
        title="Test Alert",
        message=f"This is a test {severity} alert from the Quant Trading Platform",
        severity=severity_enum,
        metadata={
            "test": True,
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
    )

    return {
        "message": f"Test alert sent with severity: {severity}",
        "timestamp": datetime.now(timezone.utc).isoformat()
    }


@router.get("/status")
async def get_service_status():
    """
    Get overall service status summary.

    Quick check for monitoring dashboards.
    """
    metrics = monitoring_service.get_metrics()

    # Determine status based on metrics
    status = "operational"

    if metrics["cpu_percent"] > 90 or metrics["memory_percent"] > 95:
        status = "degraded"

    return {
        "status": status,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "metrics": {
            "uptime_seconds": metrics["uptime_seconds"],
            "active_requests": metrics["active_requests"],
            "cpu_percent": metrics["cpu_percent"],
            "memory_percent": metrics["memory_percent"]
        }
    }


@router.get("/endpoints")
async def get_endpoint_metrics():
    """
    Get metrics for all API endpoints.

    Returns request counts, error rates, and performance data.
    """
    # This would aggregate data from monitoring service
    # For now, return basic info
    return {
        "message": "Endpoint metrics available via Prometheus",
        "metrics_url": "/api/v1/monitoring/metrics"
    }
