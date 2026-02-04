"""
Mobile API Endpoints

Optimized endpoints for mobile applications with:
- Lightweight data payloads
- Batch operations
- Offline sync support
- Push notification registration
"""

from datetime import datetime, timezone, timedelta
from typing import Optional, List
from pydantic import BaseModel, Field

from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, or_

from app.core.database import get_db
from app.core.deps import get_current_user_optional
from app.core.logging import get_logger
from app.models.politician import Politician
from app.models.trade import Trade

logger = get_logger(__name__)

router = APIRouter(prefix="/mobile", tags=["mobile"])


# ==================== REQUEST/RESPONSE MODELS ====================

class DeviceRegistration(BaseModel):
    """Device registration for push notifications"""
    device_token: str = Field(..., description="FCM/APNS device token")
    device_type: str = Field(..., description="ios or android")
    app_version: str = Field(..., description="App version")
    device_model: Optional[str] = None
    os_version: Optional[str] = None


class SyncRequest(BaseModel):
    """Sync request from mobile device"""
    last_sync_timestamp: str = Field(..., description="ISO timestamp of last sync")
    entity_types: List[str] = Field(..., description="Entity types to sync")


class BatchRequest(BaseModel):
    """Batch request for multiple operations"""
    operations: List[dict] = Field(..., description="List of operations to perform")


# ==================== ENDPOINTS ====================

@router.post("/device/register")
async def register_device(
    registration: DeviceRegistration,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user_optional)
):
    """
    Register device for push notifications.

    Stores device token for sending push notifications.

    **Body**:
    - **device_token**: FCM (Android) or APNS (iOS) token
    - **device_type**: "ios" or "android"
    - **app_version**: App version string
    """
    user_id = current_user.get("user_id") if current_user else None

    # Store device registration in database
    from app.models.device import MobileDevice
    from sqlalchemy import select

    try:
        # Check if device already exists
        query = select(MobileDevice).where(
            MobileDevice.device_token == registration.device_token
        )
        result = await db.execute(query)
        existing_device = result.scalar_one_or_none()

        if existing_device:
            # Update existing device
            existing_device.user_id = user_id
            existing_device.device_type = registration.device_type
            existing_device.app_version = registration.app_version
            existing_device.device_model = registration.device_model
            existing_device.os_version = registration.os_version
            existing_device.last_active_at = datetime.now(timezone.utc)
            await db.commit()

            logger.info(
                f"Updated device registration for push notifications",
                extra={
                    "user_id": user_id,
                    "device_id": str(existing_device.id),
                    "device_type": registration.device_type,
                    "app_version": registration.app_version
                }
            )
        else:
            # Create new device registration
            new_device = MobileDevice(
                user_id=user_id,
                device_token=registration.device_token,
                device_type=registration.device_type,
                app_version=registration.app_version,
                device_model=registration.device_model,
                os_version=registration.os_version,
                last_active_at=datetime.now(timezone.utc),
            )
            db.add(new_device)
            await db.commit()

            logger.info(
                f"Registered new device for push notifications",
                extra={
                    "user_id": user_id,
                    "device_id": str(new_device.id),
                    "device_type": registration.device_type,
                    "app_version": registration.app_version
                }
            )

        return {
            "status": "registered",
            "device_token": registration.device_token[:10] + "...",  # Partial token
            "message": "Device registered for push notifications"
        }

    except Exception as e:
        logger.error(f"Failed to register device: {e}", exc_info=True)
        await db.rollback()
        raise HTTPException(
            status_code=500,
            detail="Failed to register device"
        )


@router.delete("/device/unregister")
async def unregister_device(
    device_token: str,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user_optional)
):
    """
    Unregister device from push notifications.

    **Query Parameters**:
    - **device_token**: Device token to unregister
    """
    # Remove device registration from database
    from app.models.device import MobileDevice
    from sqlalchemy import select, delete

    try:
        # Delete device registration
        query = delete(MobileDevice).where(
            MobileDevice.device_token == device_token
        )
        result = await db.execute(query)
        await db.commit()

        if result.rowcount > 0:
            logger.info(
                f"Device unregistered from push notifications",
                extra={
                    "device_token": device_token[:10] + "...",
                    "deleted_count": result.rowcount
                }
            )

            return {
                "status": "unregistered",
                "message": "Device unregistered successfully"
            }
        else:
            logger.warning(
                f"Device not found for unregistration",
                extra={"device_token": device_token[:10] + "..."}
            )

            return {
                "status": "not_found",
                "message": "Device not found"
            }

    except Exception as e:
        logger.error(f"Failed to unregister device: {e}", exc_info=True)
        await db.rollback()
        raise HTTPException(
            status_code=500,
            detail="Failed to unregister device"
        )


@router.post("/sync")
async def sync_data(
    sync_request: SyncRequest,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user_optional)
):
    """
    Sync data for offline support.

    Returns changed data since last sync timestamp.

    **Body**:
    - **last_sync_timestamp**: ISO timestamp of last sync
    - **entity_types**: List of entity types to sync (e.g., ["politicians", "trades"])

    **Returns**:
    - **politicians**: Changed politicians since last sync
    - **trades**: New trades since last sync
    - **deleted**: IDs of deleted entities
    - **sync_timestamp**: Current server timestamp for next sync
    """
    from dateutil import parser

    last_sync = parser.isoparse(sync_request.last_sync_timestamp)
    sync_data = {
        "sync_timestamp": datetime.now(timezone.utc).isoformat()
    }

    # Sync politicians if requested
    if "politicians" in sync_request.entity_types:
        query = select(Politician).where(
            Politician.updated_at > last_sync
        ).limit(100)

        result = await db.execute(query)
        politicians = result.scalars().all()

        sync_data["politicians"] = [
            {
                "id": str(p.id),
                "name": p.name,
                "chamber": p.chamber,
                "party": p.party,
                "state": p.state,
                "updated_at": p.updated_at.isoformat()
            }
            for p in politicians
        ]

    # Sync trades if requested
    if "trades" in sync_request.entity_types:
        query = select(Trade).where(
            Trade.created_at > last_sync
        ).order_by(Trade.transaction_date.desc()).limit(200)

        result = await db.execute(query)
        trades = result.scalars().all()

        sync_data["trades"] = [
            {
                "id": str(t.id),
                "politician_id": str(t.politician_id),
                "ticker": t.ticker,
                "transaction_type": t.transaction_type,
                "transaction_date": t.transaction_date.isoformat(),
                "disclosure_date": t.disclosure_date.isoformat(),
                "created_at": t.created_at.isoformat()
            }
            for t in trades
        ]

    return sync_data


@router.get("/feed")
async def get_mobile_feed(
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=50),
    db: AsyncSession = Depends(get_db)
):
    """
    Get mobile-optimized feed of recent trades.

    Lightweight payload optimized for mobile bandwidth.

    **Query Parameters**:
    - **page**: Page number (default: 1)
    - **page_size**: Items per page (1-50, default: 20)

    **Returns**:
    Paginated list of recent trades with minimal data.
    """
    offset = (page - 1) * page_size

    # Get recent trades with politician info
    query = (
        select(Trade, Politician)
        .join(Politician, Trade.politician_id == Politician.id)
        .order_by(Trade.transaction_date.desc())
        .offset(offset)
        .limit(page_size)
    )

    result = await db.execute(query)
    trades_with_politicians = result.all()

    feed_items = []
    for trade, politician in trades_with_politicians:
        feed_items.append({
            "id": str(trade.id),
            "politician": {
                "id": str(politician.id),
                "name": politician.name,
                "party": politician.party,
                "chamber": politician.chamber
            },
            "ticker": trade.ticker,
            "type": trade.transaction_type,
            "date": trade.transaction_date.isoformat(),
            "disclosed": trade.disclosure_date.isoformat()
        })

    return {
        "items": feed_items,
        "page": page,
        "page_size": page_size,
        "has_more": len(feed_items) == page_size
    }


@router.get("/politicians/compact")
async def get_politicians_compact(
    search: Optional[str] = Query(default=None),
    chamber: Optional[str] = Query(default=None),
    party: Optional[str] = Query(default=None),
    limit: int = Query(default=50, ge=1, le=100),
    db: AsyncSession = Depends(get_db)
):
    """
    Get compact politician list for mobile.

    Minimal data payload for list views.

    **Query Parameters**:
    - **search**: Search by name
    - **chamber**: Filter by chamber (senate/house)
    - **party**: Filter by party
    - **limit**: Max results (1-100, default: 50)
    """
    query = select(Politician)

    # Apply filters
    conditions = []
    if search:
        conditions.append(Politician.name.ilike(f"%{search}%"))
    if chamber:
        conditions.append(Politician.chamber == chamber)
    if party:
        conditions.append(Politician.party == party)

    if conditions:
        query = query.where(and_(*conditions))

    query = query.limit(limit)

    result = await db.execute(query)
    politicians = result.scalars().all()

    return {
        "politicians": [
            {
                "id": str(p.id),
                "name": p.name,
                "party": p.party,
                "chamber": p.chamber,
                "state": p.state
            }
            for p in politicians
        ],
        "count": len(politicians)
    }


@router.get("/trades/recent")
async def get_recent_trades_compact(
    ticker: Optional[str] = Query(default=None),
    days: int = Query(default=30, ge=1, le=365),
    limit: int = Query(default=100, ge=1, le=200),
    db: AsyncSession = Depends(get_db)
):
    """
    Get recent trades in compact format.

    **Query Parameters**:
    - **ticker**: Filter by stock ticker
    - **days**: Look back period in days (1-365, default: 30)
    - **limit**: Max results (1-200, default: 100)
    """
    cutoff_date = datetime.now(timezone.utc).date() - timedelta(days=days)

    query = select(Trade).where(
        Trade.transaction_date >= cutoff_date
    )

    if ticker:
        query = query.where(Trade.ticker == ticker.upper())

    query = query.order_by(Trade.transaction_date.desc()).limit(limit)

    result = await db.execute(query)
    trades = result.scalars().all()

    return {
        "trades": [
            {
                "id": str(t.id),
                "politician_id": str(t.politician_id),
                "ticker": t.ticker,
                "type": t.transaction_type,
                "date": t.transaction_date.isoformat()
            }
            for t in trades
        ],
        "count": len(trades),
        "period_days": days
    }


@router.post("/batch")
async def batch_operations(
    batch_request: BatchRequest,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user_optional)
):
    """
    Execute multiple operations in a single request.

    Reduces mobile network requests by batching operations.

    **Body**:
    ```json
    {
      "operations": [
        {
          "type": "get_politician",
          "params": {"politician_id": "123"}
        },
        {
          "type": "get_trades",
          "params": {"politician_id": "123", "limit": 10}
        }
      ]
    }
    ```

    **Returns**:
    Results for each operation in the same order.
    """
    results = []

    for op in batch_request.operations:
        op_type = op.get("type")
        params = op.get("params", {})

        try:
            if op_type == "get_politician":
                politician_id = params.get("politician_id")
                query = select(Politician).where(Politician.id == politician_id)
                result = await db.execute(query)
                politician = result.scalar_one_or_none()

                if politician:
                    results.append({
                        "success": True,
                        "data": {
                            "id": str(politician.id),
                            "name": politician.name,
                            "party": politician.party,
                            "chamber": politician.chamber
                        }
                    })
                else:
                    results.append({
                        "success": False,
                        "error": "Politician not found"
                    })

            elif op_type == "get_trades":
                politician_id = params.get("politician_id")
                limit = params.get("limit", 10)

                query = (
                    select(Trade)
                    .where(Trade.politician_id == politician_id)
                    .order_by(Trade.transaction_date.desc())
                    .limit(limit)
                )

                result = await db.execute(query)
                trades = result.scalars().all()

                results.append({
                    "success": True,
                    "data": [
                        {
                            "id": str(t.id),
                            "ticker": t.ticker,
                            "type": t.transaction_type,
                            "date": t.transaction_date.isoformat()
                        }
                        for t in trades
                    ]
                })

            else:
                results.append({
                    "success": False,
                    "error": f"Unknown operation type: {op_type}"
                })

        except Exception as e:
            logger.error(f"Batch operation failed: {e}", exc_info=True)
            results.append({
                "success": False,
                "error": str(e)
            })

    return {
        "results": results,
        "total": len(results),
        "successful": sum(1 for r in results if r.get("success"))
    }


@router.get("/config")
async def get_mobile_config():
    """
    Get mobile app configuration.

    Returns configuration values for mobile clients.
    """
    return {
        "api_version": "1.0.0",
        "min_supported_version": "1.0.0",
        "features": {
            "push_notifications": True,
            "offline_sync": True,
            "real_time_updates": True,
            "premium_features": True
        },
        "sync_interval_seconds": 300,  # 5 minutes
        "cache_ttl_seconds": 3600,  # 1 hour
        "max_offline_days": 7
    }


@router.get("/changelog")
async def get_changelog():
    """
    Get app changelog for display in mobile app.
    """
    return {
        "versions": [
            {
                "version": "1.0.0",
                "released": "2026-01-28",
                "changes": [
                    "Initial release",
                    "Real-time trade notifications",
                    "Offline sync support",
                    "Push notifications"
                ]
            }
        ]
    }
