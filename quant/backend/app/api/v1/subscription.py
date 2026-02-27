"""
Subscription and billing API endpoints
Handles Stripe integration, tier upgrades, and usage tracking
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update
from pydantic import BaseModel
from datetime import datetime, timedelta

from app.core.deps import get_current_user
from app.core.database import get_db
from app.models.user import User
from app.services.subscription import SubscriptionService


router = APIRouter(prefix="/subscription", tags=["subscription"])


class SubscriptionTier(BaseModel):
    """Subscription tier info"""

    tier: str
    name: str
    price: float | None
    monthly_backtests: int
    description: str


class UpgradeRequest(BaseModel):
    """Request to upgrade subscription"""

    tier: str  # 'premium' or 'enterprise'


class SubscriptionStatus(BaseModel):
    """Current subscription status"""

    tier: str
    stripe_customer_id: str | None
    stripe_subscription_id: str | None
    status: str | None
    period_end: datetime | None
    trial_started_at: datetime | None
    trial_ends_at: datetime | None
    trial_used: bool
    usage: dict


class UsageResponse(BaseModel):
    """Monthly usage stats"""

    tier: str
    used: int
    limit: int
    remaining: int
    percentage: float
    reset_date: str


@router.get("/tiers", response_model=list[SubscriptionTier])
async def get_subscription_tiers():
    """
    Get available subscription tiers with pricing and features

    Returns all subscription options with details

    HYBRID MODEL:
    - Free: Unlimited backtests, ad-supported
    - Starter: $9.99/mo, ad-free, faster results
    - Professional: $29/mo, advanced features + API
    - Enterprise: Custom pricing
    """
    return [
        SubscriptionTier(
            tier="free",
            name="Free",
            price=None,
            monthly_backtests=float("inf"),
            description="Unlimited backtests. Ad-supported. Perfect for learning.",
        ),
        SubscriptionTier(
            tier="starter",
            name="Starter",
            price=9.99,
            monthly_backtests=float("inf"),
            description="$9.99/month. Ad-free experience, faster backtest results, export.",
        ),
        SubscriptionTier(
            tier="professional",
            name="Professional",
            price=29.0,
            monthly_backtests=float("inf"),
            description="$29/month. Advanced analytics, portfolio tracking, API access, email alerts.",
        ),
        SubscriptionTier(
            tier="enterprise",
            name="Enterprise",
            price=None,  # Custom pricing
            monthly_backtests=float("inf"),
            description="Custom pricing. Unlimited everything, white-label, dedicated support.",
        ),
    ]


@router.get("/status", response_model=SubscriptionStatus)
async def get_subscription_status(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Get current user's subscription status

    Returns subscription tier, Stripe info, trial status, and usage
    """
    usage = await SubscriptionService.check_usage(db, current_user.id)

    from datetime import datetime

    return SubscriptionStatus(
        tier=current_user.subscription_tier,
        stripe_customer_id=current_user.stripe_customer_id,
        stripe_subscription_id=current_user.stripe_subscription_id,
        status=current_user.subscription_status,
        period_end=(
            datetime.fromtimestamp(current_user.subscription_period_end)
            if current_user.subscription_period_end
            else None
        ),
        trial_started_at=current_user.trial_started_at,
        trial_ends_at=current_user.trial_ends_at,
        trial_used=current_user.trial_used,
        usage=usage,
    )


@router.get("/usage", response_model=UsageResponse)
async def get_monthly_usage(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Get monthly backtest usage and limits

    Returns current backtest count, monthly limit, and remaining quota
    """
    from datetime import datetime, timedelta

    usage = await SubscriptionService.check_usage(db, current_user.id)

    # Calculate reset date (30 days from last reset)
    if current_user.last_backtest_reset:
        reset_date = current_user.last_backtest_reset + timedelta(days=30)
    else:
        reset_date = datetime.utcnow() + timedelta(days=30)

    limit = usage["limit"]
    used = usage["used"]
    percentage = (used / limit * 100) if limit != float("inf") else 0

    return UsageResponse(
        tier=current_user.subscription_tier,
        used=used,
        limit=int(limit) if limit != float("inf") else 999,
        remaining=usage["remaining"],
        percentage=percentage,
        reset_date=reset_date.isoformat(),
    )


@router.post("/upgrade")
async def upgrade_subscription(
    request: UpgradeRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Upgrade user subscription to a higher tier

    HYBRID MODEL:
    - free → starter ($9.99/mo): Remove ads, faster results
    - free → professional ($29/mo): All advanced features + API
    - starter → professional ($29/mo): Upgrade for advanced features
    - professional → enterprise: Custom pricing

    Creates Stripe subscription and updates user record.
    Returns payment URL if payment required.
    """
    valid_tiers = ("starter", "professional", "enterprise")
    if request.tier not in valid_tiers:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid tier. Must be one of: {', '.join(valid_tiers)}",
        )

    # Tier hierarchy for upgrades
    tier_hierarchy = {"free": 0, "starter": 1, "professional": 2, "enterprise": 3}
    current_level = tier_hierarchy.get(current_user.subscription_tier, 0)
    requested_level = tier_hierarchy.get(request.tier, 0)

    if current_level >= requested_level:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Can only upgrade to higher tiers. You are on {current_user.subscription_tier}.",
        )

    # Create Stripe customer if needed
    if not current_user.stripe_customer_id:
        customer_id = await SubscriptionService.create_customer(
            db, current_user.id, current_user.email, current_user.username
        )
        if not customer_id:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to create Stripe customer",
            )
    else:
        customer_id = current_user.stripe_customer_id

    # Create subscription
    result = await SubscriptionService.create_subscription(
        db, current_user.id, customer_id, request.tier
    )

    if not result:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create subscription",
        )

    return {
        "status": "success",
        "message": f"Upgraded to {request.tier} tier",
        "subscription": result,
    }


@router.post("/downgrade")
async def downgrade_subscription(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Downgrade user subscription to free tier

    Cancels Stripe subscription and reverts to free tier.
    """
    if current_user.subscription_tier == "free":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User already on free tier",
        )

    success = await SubscriptionService.cancel_subscription(db, current_user.id)

    if not success:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to cancel subscription",
        )

    return {"status": "success", "message": "Downgraded to free tier"}


@router.post("/start-trial")
async def start_free_trial(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Start a free trial for premium features

    Upgrades user to premium for 7 days without payment.
    Only available once per account.
    """
    if current_user.trial_used:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Free trial already used for this account",
        )

    success = await SubscriptionService.start_free_trial(db, current_user.id)

    if not success:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to start free trial",
        )

    return {
        "status": "success",
        "message": "Free 7-day trial started",
        "tier": "premium",
        "ends_at": (datetime.utcnow() + timedelta(days=7)).isoformat(),
    }


@router.post("/cancel")
async def cancel_subscription(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Cancel subscription and revert to free tier

    Same as downgrade but explicit cancellation.
    """
    return await downgrade_subscription(current_user, db)


class ReferralResponse(BaseModel):
    """Referral tracking response"""
    referral_code: str
    referral_credit: float
    referral_url: str


@router.get("/referral/code", response_model=ReferralResponse)
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


@router.post("/referral/track")
async def track_referral(
    request: ReferralTrackingRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Track referral when new user signs up with referral code

    Adds $10 credit to referrer's account.
    """
    from sqlalchemy import and_

    if not request.referral_code:
        raise HTTPException(status_code=400, detail="Referral code required")

    # Parse referral code to find referrer
    try:
        parts = request.referral_code.split("_")
        if len(parts) != 2:
            raise ValueError("Invalid referral code format")
        referrer_user_id_partial = parts[1]

        # Find referrer (you may need to refactor this based on your ID structure)
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
    except ValueError as e:
        raise HTTPException(status_code=400, detail="Invalid referral code format")
