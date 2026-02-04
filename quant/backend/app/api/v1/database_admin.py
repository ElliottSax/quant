"""
Database Administration API

Endpoints for database monitoring and optimization.
Requires admin privileges.
"""

from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.security import require_admin
from app.services.database_optimizer import get_database_optimizer
from app.core.logging import get_logger

logger = get_logger(__name__)

router = APIRouter(prefix="/admin/database", tags=["database-admin"])


@router.get("/optimization-report")
async def get_optimization_report(
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(require_admin)
):
    """
    Get comprehensive database optimization report.

    Returns:
    - Query statistics
    - Slow query log
    - Index recommendations
    - Connection pool health

    **Requires**: Admin privileges
    """
    try:
        optimizer = get_database_optimizer()
        report = await optimizer.get_optimization_report(db)

        return {
            "status": "success",
            "report": report
        }

    except Exception as e:
        logger.error(f"Failed to generate optimization report: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Failed to generate report: {str(e)}"
        )


@router.get("/query-stats")
async def get_query_stats(
    limit: int = Query(default=20, ge=1, le=100),
    sort_by: str = Query(default="avg_time", regex="^(avg_time|execution_count|total_time)$"),
    current_user: dict = Depends(require_admin)
):
    """
    Get query execution statistics.

    **Parameters**:
    - **limit**: Number of queries to return (1-100)
    - **sort_by**: Sort criteria (avg_time, execution_count, total_time)

    **Requires**: Admin privileges
    """
    optimizer = get_database_optimizer()

    if sort_by == "execution_count":
        queries = optimizer.query_analyzer.get_most_frequent_queries(limit)
    else:
        queries = optimizer.query_analyzer.get_slowest_queries(limit)

    return {
        "queries": queries,
        "summary": optimizer.query_analyzer.get_stats_summary()
    }


@router.get("/slow-queries")
async def get_slow_queries(
    limit: int = Query(default=20, ge=1, le=100),
    current_user: dict = Depends(require_admin)
):
    """
    Get recent slow queries.

    **Requires**: Admin privileges
    """
    optimizer = get_database_optimizer()

    return {
        "slow_queries": optimizer.query_analyzer.slow_queries[-limit:],
        "threshold": optimizer.query_analyzer.slow_query_threshold,
        "total_slow_queries": len(optimizer.query_analyzer.slow_queries)
    }


@router.get("/index-recommendations")
async def get_index_recommendations(
    db: AsyncSession = Depends(get_db),
    min_usage: int = Query(default=5, ge=1, le=100),
    current_user: dict = Depends(require_admin)
):
    """
    Get index recommendations based on query patterns.

    **Parameters**:
    - **min_usage**: Minimum column usage count to recommend index

    **Requires**: Admin privileges
    """
    optimizer = get_database_optimizer()

    recommendations = await optimizer.index_recommender.get_recommendations(
        db,
        min_usage_count=min_usage
    )

    return {
        "recommendations": [rec.to_dict() for rec in recommendations],
        "count": len(recommendations)
    }


@router.get("/connection-pool")
async def get_connection_pool_stats(
    current_user: dict = Depends(require_admin)
):
    """
    Get database connection pool statistics and health.

    **Requires**: Admin privileges
    """
    optimizer = get_database_optimizer()
    health = optimizer.pool_monitor.check_pool_health()

    return health


@router.get("/table-stats")
async def get_table_statistics(
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(require_admin)
):
    """
    Get database table statistics (sizes, row counts).

    **Requires**: Admin privileges
    """
    optimizer = get_database_optimizer()
    stats = await optimizer.get_table_statistics(db)

    return stats


@router.post("/query-plan")
async def analyze_query_plan(
    query: str,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(require_admin)
):
    """
    Get execution plan for a query.

    **Parameters**:
    - **query**: SQL query to analyze

    **Requires**: Admin privileges
    """
    optimizer = get_database_optimizer()

    try:
        plan = await optimizer.get_query_plan(db, query)
        return plan

    except Exception as e:
        raise HTTPException(
            status_code=400,
            detail=f"Failed to analyze query: {str(e)}"
        )


@router.post("/reset-stats")
async def reset_statistics(
    current_user: dict = Depends(require_admin)
):
    """
    Reset query statistics and slow query log.

    **Requires**: Admin privileges
    """
    optimizer = get_database_optimizer()

    # Reset stats
    optimizer.query_analyzer.query_stats = {}
    optimizer.query_analyzer.slow_queries = []

    logger.info(f"Database statistics reset by user {current_user.get('user_id')}")

    return {
        "message": "Statistics reset successfully"
    }


@router.get("/health")
async def database_health_check(
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(require_admin)
):
    """
    Comprehensive database health check.

    **Requires**: Admin privileges
    """
    optimizer = get_database_optimizer()

    # Get various health metrics
    pool_health = optimizer.pool_monitor.check_pool_health()
    query_stats = optimizer.query_analyzer.get_stats_summary()

    health = {
        "status": "healthy",
        "checks": {
            "connection_pool": pool_health['status'],
            "query_performance": "healthy"
        },
        "metrics": {
            "pool": pool_health['stats'],
            "queries": query_stats
        },
        "warnings": pool_health['warnings']
    }

    # Check query performance
    if query_stats['avg_execution_time'] > 1.0:
        health['status'] = "degraded"
        health['checks']['query_performance'] = "slow"
        health['warnings'].append(
            f"Average query time is {query_stats['avg_execution_time']:.2f}s"
        )

    if query_stats['slow_queries'] > 100:
        health['warnings'].append(
            f"{query_stats['slow_queries']} slow queries detected"
        )

    return health


@router.get("/performance-recommendations")
async def get_performance_recommendations(
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(require_admin)
):
    """
    Get actionable performance recommendations.

    **Requires**: Admin privileges
    """
    optimizer = get_database_optimizer()

    recommendations = []

    # Check connection pool
    pool_health = optimizer.pool_monitor.check_pool_health()
    if pool_health['status'] == 'critical':
        recommendations.append({
            "category": "connection_pool",
            "priority": "critical",
            "message": "Connection pool is critically utilized",
            "action": "Increase pool size or investigate connection leaks"
        })

    # Check slow queries
    query_stats = optimizer.query_analyzer.get_stats_summary()
    if query_stats['slow_queries'] > 50:
        recommendations.append({
            "category": "query_performance",
            "priority": "high",
            "message": f"{query_stats['slow_queries']} slow queries detected",
            "action": "Review slow query log and optimize queries"
        })

    # Check for missing indexes
    index_recs = await optimizer.index_recommender.get_recommendations(db)
    high_impact_indexes = [r for r in index_recs if r.estimated_impact == "high"]

    if high_impact_indexes:
        recommendations.append({
            "category": "indexes",
            "priority": "high",
            "message": f"{len(high_impact_indexes)} high-impact indexes missing",
            "action": "Review and create recommended indexes",
            "details": [r.create_statement for r in high_impact_indexes[:5]]
        })

    # Check average query time
    if query_stats['avg_execution_time'] > 0.5:
        recommendations.append({
            "category": "query_performance",
            "priority": "medium",
            "message": f"Average query time is {query_stats['avg_execution_time']:.2f}s",
            "action": "Enable query caching or optimize frequently executed queries"
        })

    return {
        "recommendations": recommendations,
        "count": len(recommendations)
    }
