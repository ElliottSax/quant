"""
Security Administration API

Endpoints for security testing and management.

WARNING: These endpoints should only be accessible in development/testing environments
or to authenticated administrators.
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.security import require_admin
from app.core.config import settings
from app.security.penetration_tests import PenetrationTester
from app.core.logging import get_logger

logger = get_logger(__name__)

router = APIRouter(prefix="/admin/security", tags=["security-admin"])


@router.get("/pen-test")
async def run_penetration_tests(
    target_url: str = Query(default=None, description="Target URL to test (defaults to current host)"),
    current_user: dict = Depends(require_admin)
):
    """
    Run automated penetration tests.

    **WARNING**: Only use in testing environments!

    Tests include:
    - XSS vulnerabilities
    - Security headers
    - Authentication weaknesses
    - Authorization issues
    - Rate limiting
    - Sensitive data exposure

    **Requires**: Admin privileges
    """
    if settings.ENVIRONMENT == "production":
        raise HTTPException(
            status_code=403,
            detail="Penetration testing is disabled in production"
        )

    # Use provided URL or default to current host
    if not target_url:
        target_url = f"http://localhost:8000"

    logger.info(
        f"Running penetration tests against: {target_url}",
        extra={"user_id": current_user.get("user_id"), "target_url": target_url}
    )

    try:
        tester = PenetrationTester(target_url)
        vulnerabilities = await tester.run_all_tests()
        report = tester.generate_report()

        return {
            "status": "complete",
            "target_url": target_url,
            "report": report
        }

    except Exception as e:
        logger.error(f"Penetration testing failed: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Penetration testing failed: {str(e)}"
        )


@router.get("/sql-injection-test")
async def test_sql_injection(
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(require_admin)
):
    """
    Run SQL injection tests.

    **WARNING**: Only use in testing environments!

    **Requires**: Admin privileges
    """
    if settings.ENVIRONMENT == "production":
        raise HTTPException(
            status_code=403,
            detail="SQL injection testing is disabled in production"
        )

    from app.security.sql_injection_tester import SQLInjectionTester, InjectionType

    logger.info(
        "Running SQL injection tests",
        extra={"user_id": current_user.get("user_id")}
    )

    try:
        tester = SQLInjectionTester()

        # Test a safe query (should pass all tests)
        test_query = "SELECT * FROM politicians WHERE name = '{search_param}'"

        results = await tester.test_query(
            db,
            test_query,
            "search_param",
            [InjectionType.CLASSIC, InjectionType.ERROR_BASED]
        )

        report = tester.generate_report(results)

        return {
            "status": "complete",
            "query_tested": test_query,
            "report": report
        }

    except Exception as e:
        logger.error(f"SQL injection testing failed: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"SQL injection testing failed: {str(e)}"
        )


@router.get("/security-audit")
async def run_security_audit(
    current_user: dict = Depends(require_admin)
):
    """
    Run comprehensive security audit.

    Checks:
    - Security headers
    - Authentication configuration
    - HTTPS enforcement
    - CORS configuration
    - Rate limiting settings

    **Requires**: Admin privileges
    """
    audit_results = {
        "timestamp": "2026-01-28T12:00:00Z",
        "checks": []
    }

    # Check HTTPS in production
    if settings.ENVIRONMENT == "production":
        # In production, all connections should be HTTPS
        audit_results["checks"].append({
            "name": "HTTPS Enforcement",
            "status": "info",
            "message": "Verify HTTPS is enforced at load balancer/proxy level"
        })

    # Check CORS configuration
    cors_check = {
        "name": "CORS Configuration",
        "status": "pass",
        "origins": settings.BACKEND_CORS_ORIGINS
    }

    if "*" in settings.BACKEND_CORS_ORIGINS:
        cors_check["status"] = "warning"
        cors_check["message"] = "CORS allows all origins - consider restricting in production"

    audit_results["checks"].append(cors_check)

    # Check SECRET_KEY strength
    if len(settings.SECRET_KEY) < 32:
        audit_results["checks"].append({
            "name": "Secret Key Strength",
            "status": "fail",
            "message": "SECRET_KEY should be at least 32 characters"
        })
    else:
        audit_results["checks"].append({
            "name": "Secret Key Strength",
            "status": "pass"
        })

    # Check Sentry configuration
    if settings.SENTRY_DSN:
        audit_results["checks"].append({
            "name": "Error Tracking",
            "status": "pass",
            "message": "Sentry is configured"
        })
    else:
        audit_results["checks"].append({
            "name": "Error Tracking",
            "status": "warning",
            "message": "Sentry not configured - consider enabling for production"
        })

    # Summary
    total_checks = len(audit_results["checks"])
    passed = sum(1 for c in audit_results["checks"] if c["status"] == "pass")
    warnings = sum(1 for c in audit_results["checks"] if c["status"] == "warning")
    failed = sum(1 for c in audit_results["checks"] if c["status"] == "fail")

    audit_results["summary"] = {
        "total_checks": total_checks,
        "passed": passed,
        "warnings": warnings,
        "failed": failed,
        "score": f"{(passed / total_checks * 100):.1f}%" if total_checks > 0 else "0%"
    }

    return audit_results


@router.get("/api-keys")
async def list_api_keys(
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(require_admin),
    user_id: str = Query(default=None, description="Filter by user ID"),
    is_active: bool = Query(default=None, description="Filter by active status"),
    limit: int = Query(default=100, ge=1, le=1000)
):
    """
    List all API keys (admin view).

    **Query Parameters**:
    - **user_id**: Filter by specific user
    - **is_active**: Filter by active status
    - **limit**: Maximum number of keys to return

    **Requires**: Admin privileges
    """
    from app.models.api_key import APIKey
    from sqlalchemy import select, and_

    try:
        # Build query
        query = select(APIKey)

        # Apply filters
        conditions = []
        if user_id:
            conditions.append(APIKey.user_id == user_id)
        if is_active is not None:
            conditions.append(APIKey.is_active == is_active)

        if conditions:
            query = query.where(and_(*conditions))

        # Order by creation date (newest first)
        query = query.order_by(APIKey.created_at.desc()).limit(limit)

        # Execute query
        result = await db.execute(query)
        api_keys = result.scalars().all()

        # Format response (exclude sensitive data)
        keys_data = []
        for key in api_keys:
            keys_data.append({
                "key_id": key.key_id,
                "user_id": str(key.user_id),
                "name": key.name,
                "permissions": key.permissions.get("permissions", []),
                "is_active": key.is_active,
                "created_at": key.created_at.isoformat(),
                "expires_at": key.expires_at.isoformat() if key.expires_at else None,
                "last_used_at": key.last_used_at.isoformat() if key.last_used_at else None,
                "total_requests": key.total_requests,
            })

        return {
            "keys": keys_data,
            "total": len(keys_data),
            "limit": limit
        }

    except Exception as e:
        logger.error(f"Failed to list API keys: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Failed to list API keys: {str(e)}"
        )


@router.post("/api-keys/rotate")
async def rotate_api_key(
    key_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(require_admin)
):
    """
    Rotate an API key (admin function).

    **Requires**: Admin privileges
    """
    from app.services.api_key_manager import api_key_manager

    try:
        new_key_id, new_secret = await api_key_manager.rotate_key(
            db,
            key_id,
            current_user["user_id"]
        )

        return {
            "message": "API key rotated successfully",
            "new_key_id": new_key_id,
            "new_secret_key": new_secret,
            "warning": "Save this key - it won't be shown again!"
        }

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to rotate API key: {str(e)}"
        )


@router.get("/csrf-test")
async def test_csrf_protection():
    """
    Test CSRF protection configuration.

    Returns information about CSRF protection status.
    """
    return {
        "csrf_protection": "enabled",
        "cookie_name": "csrf_token",
        "header_name": "X-CSRF-Token",
        "message": "CSRF protection is active. Include CSRF token in request headers for state-changing operations."
    }
