"""
Subscription and Billing API Endpoints
"""

from fastapi import APIRouter, Depends, HTTPException, Request, Header
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional
from pydantic import BaseModel

from app.core.deps import get_db, get_current_active_user
from app.models.user import User
from app.models.subscription import SubscriptionTier
from app.services.subscription_service import (
    subscription_service,
    stripe_service,
    TIER_CONFIG,
)

router = APIRouter()


# Request/Response models
class SubscriptionResponse(BaseModel):
    """Response model for subscription."""

    tier: SubscriptionTier
    status: str
    api_rate_limit: int
    features: dict
    current_period_start: Optional[str] = None
    current_period_end: Optional[str] = None
    cancel_at: Optional[str] = None


class CreateSubscriptionRequest(BaseModel):
    """Request model for creating subscription."""

    tier: SubscriptionTier
    billing_cycle: str = "monthly"  # monthly or yearly


class UsageResponse(BaseModel):
    """Response model for usage statistics."""

    limit: int
    used: int
    remaining: int
    reset_at: str


@router.get("/current", response_model=SubscriptionResponse)
async def get_current_subscription(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Get current user's subscription details.
    """
    subscription = await subscription_service.get_or_create_subscription(
        db, str(current_user.id)
    )

    return SubscriptionResponse(
        tier=subscription.tier,
        status=subscription.status.value,
        api_rate_limit=subscription.api_rate_limit,
        features=subscription.features or {},
        current_period_start=subscription.current_period_start.isoformat()
        if subscription.current_period_start
        else None,
        current_period_end=subscription.current_period_end.isoformat()
        if subscription.current_period_end
        else None,
        cancel_at=subscription.cancel_at.isoformat() if subscription.cancel_at else None,
    )


@router.get("/plans")
async def get_subscription_plans():
    """
    Get available subscription plans and pricing.
    """
    plans = []

    for tier, config in TIER_CONFIG.items():
        plans.append(
            {
                "tier": tier.value,
                "name": tier.value.title(),
                "price_monthly": config["price"],
                "price_yearly": config["price"] * 10,  # 2 months free
                "api_rate_limit": config["api_rate_limit"],
                "features": config["features"],
            }
        )

    return {"plans": plans}


@router.post("/subscribe", response_model=SubscriptionResponse)
async def create_subscription(
    subscription_request: CreateSubscriptionRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Create or upgrade subscription.

    This will create a Stripe subscription and redirect to checkout.
    """
    if subscription_request.tier == SubscriptionTier.FREE:
        raise HTTPException(
            status_code=400, detail="Cannot subscribe to free tier explicitly"
        )

    # Create Stripe subscription
    result = await stripe_service.create_subscription(
        db=db,
        user_id=str(current_user.id),
        tier=subscription_request.tier,
        billing_cycle=subscription_request.billing_cycle,
    )

    if not result:
        raise HTTPException(
            status_code=500, detail="Failed to create subscription. Please try again."
        )

    # Get updated subscription
    subscription = await subscription_service.get_subscription(db, str(current_user.id))

    return SubscriptionResponse(
        tier=subscription.tier,
        status=subscription.status.value,
        api_rate_limit=subscription.api_rate_limit,
        features=subscription.features or {},
        current_period_start=subscription.current_period_start.isoformat()
        if subscription.current_period_start
        else None,
        current_period_end=subscription.current_period_end.isoformat()
        if subscription.current_period_end
        else None,
        cancel_at=subscription.cancel_at.isoformat() if subscription.cancel_at else None,
    )


@router.post("/cancel")
async def cancel_subscription(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Cancel current subscription.

    Subscription will remain active until end of current period.
    """
    subscription = await subscription_service.get_subscription(db, str(current_user.id))

    if not subscription or subscription.tier == SubscriptionTier.FREE:
        raise HTTPException(status_code=400, detail="No active subscription to cancel")

    # In production, cancel Stripe subscription
    # For now, just update status
    from datetime import datetime
    from app.models.subscription import SubscriptionStatus

    subscription.status = SubscriptionStatus.CANCELLED
    subscription.cancelled_at = datetime.utcnow()
    await db.commit()

    return {"message": "Subscription cancelled successfully"}


@router.get("/usage", response_model=UsageResponse)
async def get_usage_statistics(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Get current usage statistics and rate limits.
    """
    usage = await subscription_service.check_rate_limit(db, str(current_user.id))

    return UsageResponse(**usage)


@router.post("/webhooks/stripe")
async def stripe_webhook(
    request: Request,
    stripe_signature: Optional[str] = Header(None, alias="Stripe-Signature"),
    db: AsyncSession = Depends(get_db),
):
    """
    Handle Stripe webhook events.

    This endpoint receives events from Stripe about subscription changes.
    """
    # Get raw body
    body = await request.body()

    # In production, verify signature
    # webhook_secret = settings.STRIPE_WEBHOOK_SECRET
    # stripe.Webhook.construct_event(body, stripe_signature, webhook_secret)

    # Parse event
    import json

    event = json.loads(body)

    # Handle event
    await stripe_service.handle_webhook(db, event)

    return {"status": "success"}


@router.get("/features")
async def get_available_features(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Get available features for current subscription tier.
    """
    subscription = await subscription_service.get_or_create_subscription(
        db, str(current_user.id)
    )

    return {
        "tier": subscription.tier.value,
        "features": subscription.features or {},
    }


@router.get("/check-access/{feature}")
async def check_feature_access(
    feature: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Check if user has access to a specific feature.
    """
    has_access = await subscription_service.check_feature_access(
        db, str(current_user.id), feature
    )

    return {
        "feature": feature,
        "has_access": has_access,
    }
