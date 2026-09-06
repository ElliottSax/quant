"""Referral endpoints, split out of the still-dormant subscription.py.

subscription.py (singular) was never mounted in __init__.py, so every call
the frontend makes to /api/v1/subscription/* 404s in production -- including
settings/referral/page.tsx's /api/v1/subscription/referral/code and
/api/v1/subscription/referral/track. Elliott confirmed (2026-09-06) referral
functionality doesn't conflict with the free-forever pricing decision, so
only the referral piece is wired up here. subscription.py's tier/upgrade/
downgrade/start-trial/cancel/usage endpoints remain unmounted -- those are
billing/tier logic still tangled in the paused pricing decision (see
CLAUDE.md) and stay 404ing until Elliott resolves that separately.
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update
from pydantic import BaseModel

from app.core.deps import get_current_user
from app.core.database import get_db
from app.models.user import User
from app.services.subscription import SubscriptionService

router = APIRouter(prefix="/subscription/referral", tags=["referral"])


class ReferralResponse(BaseModel):
    """Referral tracking response"""
    referral_code: str
    referral_credit: float
    referral_url: str


@router.get("/code", response_model=ReferralResponse)
async def get_referral_code(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Get user's referral code and credit balance

    Users earn $10 credit for each friend who signs up and validates email.
    Credits can be applied to subscription upgrades.
    """
    if not current_user.referral_code:
        # Generate referral code if not exists
        code = SubscriptionService.generate_referral_code(str(current_user.id))
        stmt = update(User).where(User.id == current_user.id).values(referral_code=code)
        await db.execute(stmt)
        await db.commit()
    else:
        code = current_user.referral_code

    return ReferralResponse(
        referral_code=code,
        referral_credit=current_user.referral_credit_balance,
        referral_url=f"https://quant.platform.com?ref={code}",
    )


class ReferralTrackingRequest(BaseModel):
    """Track referral signup"""
    referral_code: str


@router.post("/track")
async def track_referral(
    request: ReferralTrackingRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Track referral when new user signs up with referral code

    Adds $10 credit to referrer's account.
    """
    if not request.referral_code:
        raise HTTPException(status_code=400, detail="Referral code required")

    try:
        parts = request.referral_code.split("_")
        if len(parts) != 2:
            raise ValueError("Invalid referral code format")

        # Find referrer
        stmt = select(User).where(User.referral_code == request.referral_code)
        result = await db.execute(stmt)
        referrer = result.scalar_one_or_none()

        if not referrer:
            raise HTTPException(status_code=404, detail="Referrer not found")

        # Process referral
        success = await SubscriptionService.process_referral(db, referrer.id, current_user.id)

        if not success:
            raise HTTPException(status_code=500, detail="Failed to process referral")

        return {
            "status": "success",
            "message": f"Referral tracked. {referrer.username} earned $10 credit!",
            "referrer_name": referrer.username,
        }
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid referral code format")
