"""
Affiliate broker integration API endpoints
Provides recommended brokers and affiliate links for backtesting results
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel
from typing import List, Optional, Dict, Any

from app.core.database import get_db
from app.core.deps import get_current_user
from app.models.user import User
from app.services.affiliate import AffiliateService, BrokerType
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/affiliate", tags=["affiliate"])


class BrokerRecommendation(BaseModel):
    """Broker recommendation response"""
    broker: str
    name: str
    logo_url: str
    signup_url: str
    description: str
    features: List[str]
    recommended_for: List[str]
    commission: float
    display_commission: str


class BrokerListResponse(BaseModel):
    """List of brokers response"""
    broker: str
    name: str
    logo_url: str
    signup_url: str
    description: str
    features: List[str]
    commission: float


class AffiliateClickEvent(BaseModel):
    """Track affiliate link click"""
    broker: str
    strategy: str
    backtest_id: Optional[str] = None


class RevenueEstimate(BaseModel):
    """Potential affiliate revenue estimate"""
    total_users: int
    estimated_conversions: int
    total_commission: float
    avg_commission_per_signup: float


@router.get("/brokers/recommendations")
async def get_broker_recommendations(
    strategy: str = Query(..., description="Trading strategy type"),
    user_tier: str = Query("free", description="User subscription tier"),
) -> List[BrokerRecommendation]:
    """
    Get recommended brokers for a specific trading strategy

    Returns list of brokers with affiliate links, sorted by relevance
    to the strategy type.

    Strategies: momentum, mean_reversion, trend, volatility

    Returns:
    - Top 3 brokers recommended for the strategy
    - Affiliate signup links
    - Features and commission info
    - Commission per referral
    """
    recommendations = AffiliateService.get_recommended_brokers(strategy, user_tier)
    if not recommendations:
        raise HTTPException(
            status_code=404,
            detail=f"No brokers found for strategy: {strategy}"
        )
    return recommendations


@router.get("/brokers/all", response_model=List[BrokerListResponse])
async def get_all_brokers():
    """
    Get all available affiliate brokers

    Returns complete list of supported brokers with:
    - Full broker details
    - Affiliate links
    - Commission per referral
    """
    return AffiliateService.get_all_brokers()


@router.get("/brokers/{broker_name}")
async def get_broker_details(broker_name: str) -> BrokerListResponse:
    """
    Get details for a specific broker

    Args:
        broker_name: Broker identifier (e.g., 'interactive_brokers')

    Returns broker details and affiliate link
    """
    try:
        broker_type = BrokerType(broker_name)
        if broker_type not in AffiliateService.BROKERS:
            raise HTTPException(status_code=404, detail=f"Broker not found: {broker_name}")

        broker = AffiliateService.BROKERS[broker_type]
        return BrokerListResponse(
            broker=broker.broker.value,
            name=broker.name,
            logo_url=broker.logo_url,
            signup_url=broker.signup_url,
            description=broker.description,
            features=broker.features,
            commission=broker.commission_per_referral,
        )
    except ValueError:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid broker name: {broker_name}"
        )


@router.get("/link/{broker_name}")
async def get_affiliate_link(
    broker_name: str,
    campaign: str = Query("backtest-results", description="UTM campaign"),
    medium: str = Query("web", description="UTM medium"),
    source: str = Query("quant", description="UTM source"),
    content: Optional[str] = Query(None, description="UTM content (e.g., strategy name)"),
):
    """
    Get affiliate link for a broker with UTM tracking

    Generates trackable affiliate link with UTM parameters for analytics

    UTM Parameters:
    - campaign: Marketing campaign (default: backtest-results)
    - medium: Traffic medium (default: web)
    - source: Traffic source (default: quant)
    - content: Optional content identifier (e.g., strategy type)
    """
    try:
        broker_type = BrokerType(broker_name)

        utm_params = {
            "utm_campaign": campaign,
            "utm_medium": medium,
            "utm_source": source,
        }
        if content:
            utm_params["utm_content"] = content

        link = AffiliateService.get_affiliate_link(broker_type, utm_params)
        if not link:
            raise HTTPException(status_code=404, detail=f"Broker not found: {broker_name}")

        return {"broker": broker_name, "link": link, "utm_params": utm_params}
    except ValueError:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid broker name: {broker_name}"
        )


@router.post("/track-click")
async def track_affiliate_click(
    event: AffiliateClickEvent,
    current_user: Optional[User] = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Track affiliate link click for analytics

    Called when user clicks on broker recommendation
    Helps track conversion metrics and revenue attribution
    """
    try:
        user_id = current_user.id if current_user else None

        success = await AffiliateService.track_affiliate_click(
            db,
            broker=event.broker,
            user_id=str(user_id) if user_id else None,
            backtest_id=event.backtest_id,
            strategy=event.strategy,
        )

        if not success:
            raise HTTPException(
                status_code=500,
                detail="Failed to track affiliate click"
            )

        return {
            "status": "tracked",
            "broker": event.broker,
            "strategy": event.strategy
        }
    except Exception as e:
        logger.error(f"Error tracking affiliate click: {e}")
        raise HTTPException(
            status_code=500,
            detail="Failed to track affiliate click"
        )


@router.get("/revenue/estimate")
async def estimate_revenue(
    num_brokers: int = Query(3, description="Number of recommended brokers", ge=1, le=8),
    conversion_rate: float = Query(0.05, description="Estimated conversion rate", ge=0.01, le=0.5),
    users_per_backtest: int = Query(1, description="Average users viewing results", ge=1),
) -> RevenueEstimate:
    """
    Estimate potential affiliate revenue

    Calculates potential affiliate revenue based on:
    - Number of recommended brokers shown
    - Estimated conversion rate (default 5%)
    - Number of users viewing results

    Use this for marketing ROI analysis
    """
    estimate = AffiliateService.calculate_potential_revenue(
        recommended_brokers=[{"commission": 50} for _ in range(num_brokers)],
        estimated_conversion_rate=conversion_rate,
        users_viewing_results=users_per_backtest,
    )
    return RevenueEstimate(**estimate)


@router.get("/top-broker/{strategy}")
async def get_top_broker(strategy: str) -> BrokerRecommendation:
    """
    Get top recommended broker for a specific strategy

    Returns the single best broker recommendation for the given strategy
    """
    recommendation = AffiliateService.get_broker_by_strategy(strategy)
    if not recommendation:
        raise HTTPException(
            status_code=404,
            detail=f"No brokers found for strategy: {strategy}"
        )
    return recommendation
