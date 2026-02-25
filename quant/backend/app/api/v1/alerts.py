"""
Alert Management API Endpoints
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional
from datetime import datetime
from pydantic import BaseModel, Field

from app.core.deps import get_db, get_current_active_user
from app.models.user import User
from app.models.alert import AlertType, NotificationChannel, AlertStatus
from app.services.alert_service import alert_service
from app.services.subscription_service import subscription_service

router = APIRouter()


# Request/Response models
class AlertCreate(BaseModel):
    """Request model for creating an alert."""

    name: str = Field(..., min_length=1, max_length=255)
    alert_type: AlertType
    conditions: dict = Field(..., description="Alert conditions as JSON")
    notification_channels: List[str] = Field(default=["email"])
    webhook_url: Optional[str] = None
    notification_email: Optional[str] = None
    expires_at: Optional[datetime] = None


class AlertUpdate(BaseModel):
    """Request model for updating an alert."""

    name: Optional[str] = None
    conditions: Optional[dict] = None
    notification_channels: Optional[List[str]] = None
    webhook_url: Optional[str] = None
    notification_email: Optional[str] = None
    status: Optional[AlertStatus] = None
    is_active: Optional[bool] = None


class AlertResponse(BaseModel):
    """Response model for alert."""

    id: str
    user_id: str
    name: str
    alert_type: AlertType
    conditions: dict
    notification_channels: List[str]
    webhook_url: Optional[str]
    notification_email: Optional[str]
    status: AlertStatus
    is_active: bool
    created_at: datetime
    updated_at: datetime
    last_triggered_at: Optional[datetime]
    expires_at: Optional[datetime]
    trigger_count: int

    class Config:
        from_attributes = True


async def require_premium(
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """Require premium subscription for alerts."""
    has_premium = await subscription_service.check_premium_access(db, str(current_user.id))

    if not has_premium:
        raise HTTPException(
            status_code=403,
            detail="Premium subscription required for alerts"
        )

    return current_user


@router.post("/", response_model=AlertResponse, status_code=201)
async def create_alert(
    alert_data: AlertCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_premium)
):
    """
    Create a new alert.

    **Premium feature**: Requires premium subscription.

    Available alert types:
    - `trade`: Alert on new trades matching conditions
    - `price`: Alert when stock price crosses threshold
    - `politician_activity`: Alert on politician activity

    Example conditions:
    ```json
    {
        "politician_id": "uuid",
        "ticker": "AAPL",
        "min_amount": 100000,
        "transaction_type": "buy"
    }
    ```
    """
    alert = await alert_service.create_alert(
        db=db,
        user_id=str(current_user.id),
        name=alert_data.name,
        alert_type=alert_data.alert_type,
        conditions=alert_data.conditions,
        notification_channels=alert_data.notification_channels,
        webhook_url=alert_data.webhook_url,
        notification_email=alert_data.notification_email,
        expires_at=alert_data.expires_at,
    )

    return AlertResponse.from_orm(alert)


@router.get("/", response_model=List[AlertResponse])
async def get_alerts(
    alert_type: Optional[AlertType] = Query(None),
    status: Optional[AlertStatus] = Query(None),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_premium)
):
    """
    Get all alerts for the current user.

    **Premium feature**: Requires premium subscription.

    Optional filters:
    - `alert_type`: Filter by alert type
    - `status`: Filter by status
    """
    alerts = await alert_service.get_user_alerts(
        db=db,
        user_id=str(current_user.id),
        alert_type=alert_type,
        status=status,
    )

    return [AlertResponse.from_orm(alert) for alert in alerts]


@router.get("/{alert_id}", response_model=AlertResponse)
async def get_alert(
    alert_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_premium)
):
    """
    Get a specific alert.

    **Premium feature**: Requires premium subscription.
    """
    alerts = await alert_service.get_user_alerts(
        db=db,
        user_id=str(current_user.id),
    )

    alert = next((a for a in alerts if str(a.id) == alert_id), None)

    if not alert:
        raise HTTPException(status_code=404, detail="Alert not found")

    return AlertResponse.from_orm(alert)


@router.patch("/{alert_id}", response_model=AlertResponse)
async def update_alert(
    alert_id: str,
    alert_update: AlertUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_premium)
):
    """
    Update an alert.

    **Premium feature**: Requires premium subscription.
    """
    # Get update data
    update_data = alert_update.dict(exclude_none=True)

    alert = await alert_service.update_alert(
        db=db,
        alert_id=alert_id,
        user_id=str(current_user.id),
        **update_data
    )

    if not alert:
        raise HTTPException(status_code=404, detail="Alert not found")

    return AlertResponse.from_orm(alert)


@router.delete("/{alert_id}", status_code=204)
async def delete_alert(
    alert_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_premium)
):
    """
    Delete an alert.

    **Premium feature**: Requires premium subscription.
    """
    deleted = await alert_service.delete_alert(
        db=db,
        alert_id=alert_id,
        user_id=str(current_user.id),
    )

    if not deleted:
        raise HTTPException(status_code=404, detail="Alert not found")

    return None


@router.get("/statistics/summary")
async def get_alert_statistics(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_premium)
):
    """
    Get alert statistics for the current user.

    **Premium feature**: Requires premium subscription.
    """
    alerts = await alert_service.get_user_alerts(
        db=db,
        user_id=str(current_user.id),
    )

    total_alerts = len(alerts)
    active_alerts = sum(1 for a in alerts if a.status == AlertStatus.ACTIVE)
    triggered_count = sum(int(a.trigger_count) for a in alerts)

    by_type = {}
    for alert in alerts:
        alert_type = alert.alert_type.value
        if alert_type not in by_type:
            by_type[alert_type] = 0
        by_type[alert_type] += 1

    return {
        "total_alerts": total_alerts,
        "active_alerts": active_alerts,
        "total_triggered": triggered_count,
        "by_type": by_type,
    }
