"""
Monitoring and Metrics API Endpoints
"""

from fastapi import APIRouter, Depends, HTTPException
from typing import Dict, Any

from app.core.monitoring import monitoring, health_check
from app.core.deps import get_current_active_superuser

router = APIRouter()


@router.get("/metrics")
async def get_prometheus_metrics():
    """
    Get Prometheus metrics
    Public endpoint for Prometheus scraping
    """
    return monitoring.export_prometheus_metrics()


@router.get("/health")
async def health_check_endpoint():
    """
    Comprehensive health check
    Checks all critical dependencies
    """
    return await health_check.run_checks()


@router.get("/health/simple")
async def simple_health_check():
    """
    Simple health check
    Returns 200 if service is running
    """
    return {
        "status": "healthy",
        "service": "quant-trading-platform"
    }


@router.get("/metrics/summary", dependencies=[Depends(get_current_active_superuser)])
async def get_metrics_summary() -> Dict[str, Any]:
    """
    Get metrics summary
    Requires admin access
    """
    return monitoring.get_metrics()
