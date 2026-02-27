"""
Affiliate broker integration service
Manages affiliate links and referral tracking for revenue generation
"""

import os
from typing import Dict, List, Optional
from enum import Enum
from datetime import datetime
import uuid
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import insert
import logging

logger = logging.getLogger(__name__)


class BrokerType(str, Enum):
    """Supported broker platforms"""
    INTERACTIVE_BROKERS = "interactive_brokers"
    TASTYTRADE = "tastytrade"
    TD_AMERITRADE = "td_ameritrade"
    CHARLES_SCHWAB = "charles_schwab"
    FIDELITY = "fidelity"
    WEBULL = "webull"
    TRADIER = "tradier"
    LIGHTSPEED = "lightspeed"


class BrokerAffiliateLink:
    """Affiliate link configuration for each broker"""

    def __init__(
        self,
        broker: BrokerType,
        name: str,
        logo_url: str,
        signup_url: str,
        commission_per_referral: float,
        description: str,
        features: List[str],
        recommended_for: List[str],
    ):
        self.broker = broker
        self.name = name
        self.logo_url = logo_url
        self.signup_url = signup_url
        self.commission_per_referral = commission_per_referral
        self.description = description
        self.features = features
        self.recommended_for = recommended_for


class AffiliateService:
    """Service for managing broker affiliate links and tracking"""

    # Broker affiliate configurations
    BROKERS: Dict[BrokerType, BrokerAffiliateLink] = {
        BrokerType.INTERACTIVE_BROKERS: BrokerAffiliateLink(
            broker=BrokerType.INTERACTIVE_BROKERS,
            name="Interactive Brokers",
            logo_url="https://www.interactivebrokers.com/images/logo.png",
            signup_url=os.getenv(
                "AFFILIATE_IB_URL",
                "https://www.interactivebrokers.com/en/home.php?affiliate=quant2024",
            ),
            commission_per_referral=50.0,
            description="Professional trading platform with advanced tools",
            features=[
                "Lowest commissions",
                "Advanced order types",
                "Forex trading",
                "Margin trading",
                "API access",
            ],
            recommended_for=["Advanced traders", "Professional investors", "Algo trading"],
        ),
        BrokerType.TASTYTRADE: BrokerAffiliateLink(
            broker=BrokerType.TASTYTRADE,
            name="Tastytrade",
            logo_url="https://www.tastytrade.com/images/logo.png",
            signup_url=os.getenv(
                "AFFILIATE_TASTYTRADE_URL",
                "https://www.tastytrade.com?affiliate=quant2024",
            ),
            commission_per_referral=75.0,
            description="Best for options trading with educational content",
            features=[
                "Free stock trades",
                "Options expertise",
                "Live market commentary",
                "Paper trading",
                "Educational webinars",
            ],
            recommended_for=["Options traders", "Beginners", "Active traders"],
        ),
        BrokerType.TD_AMERITRADE: BrokerAffiliateLink(
            broker=BrokerType.TD_AMERITRADE,
            name="TD Ameritrade (Schwab)",
            logo_url="https://www.tdameritrade.com/images/logo.png",
            signup_url=os.getenv(
                "AFFILIATE_TDA_URL",
                "https://www.tdameritrade.com?affiliate=quant2024",
            ),
            commission_per_referral=60.0,
            description="Comprehensive platform with Thinkorswim",
            features=[
                "Thinkorswim platform",
                "Advanced charting",
                "Paper trading",
                "Research tools",
                "Education resources",
            ],
            recommended_for=["Active traders", "Technical analysts", "Beginners"],
        ),
        BrokerType.CHARLES_SCHWAB: BrokerAffiliateLink(
            broker=BrokerType.CHARLES_SCHWAB,
            name="Charles Schwab",
            logo_url="https://www.schwab.com/images/logo.png",
            signup_url=os.getenv(
                "AFFILIATE_SCHWAB_URL",
                "https://www.schwab.com?affiliate=quant2024",
            ),
            commission_per_referral=55.0,
            description="User-friendly with excellent customer service",
            features=[
                "No account minimums",
                "Free stock trading",
                "Robo-advisory (Schwab Intelligent Portfolios)",
                "Research tools",
                "Mobile app",
            ],
            recommended_for=["Beginners", "Long-term investors", "Casual traders"],
        ),
        BrokerType.FIDELITY: BrokerAffiliateLink(
            broker=BrokerType.FIDELITY,
            name="Fidelity",
            logo_url="https://www.fidelity.com/images/logo.png",
            signup_url=os.getenv(
                "AFFILIATE_FIDELITY_URL",
                "https://www.fidelity.com?affiliate=quant2024",
            ),
            commission_per_referral=65.0,
            description="Full-service broker with retirement account expertise",
            features=[
                "No minimum balance",
                "Free stock/ETF trading",
                "Retirement accounts (IRA, 401k)",
                "Investment advice",
                "Research platform",
            ],
            recommended_for=["Retirement planning", "Long-term investors", "Beginners"],
        ),
        BrokerType.WEBULL: BrokerAffiliateLink(
            broker=BrokerType.WEBULL,
            name="Webull",
            logo_url="https://www.webull.com/images/logo.png",
            signup_url=os.getenv(
                "AFFILIATE_WEBULL_URL",
                "https://www.webull.com?affiliate=quant2024",
            ),
            commission_per_referral=40.0,
            description="Mobile-first platform with fractional shares",
            features=[
                "Fractional shares",
                "Extended hours trading",
                "No commission",
                "Paper trading",
                "Mobile-optimized",
            ],
            recommended_for=["Mobile traders", "Beginners", "Young investors"],
        ),
    }

    @staticmethod
    def get_recommended_brokers(
        strategy_type: str, user_tier: str
    ) -> List[Dict]:
        """
        Get recommended brokers based on strategy and user tier

        Returns brokers with affiliate links, prioritized for strategy type
        """
        strategy_broker_mapping = {
            "momentum": [
                BrokerType.INTERACTIVE_BROKERS,
                BrokerType.TASTYTRADE,
                BrokerType.TD_AMERITRADE,
            ],
            "mean_reversion": [
                BrokerType.TASTYTRADE,
                BrokerType.INTERACTIVE_BROKERS,
                BrokerType.TD_AMERITRADE,
            ],
            "trend": [
                BrokerType.INTERACTIVE_BROKERS,
                BrokerType.CHARLES_SCHWAB,
                BrokerType.FIDELITY,
            ],
            "volatility": [
                BrokerType.TASTYTRADE,
                BrokerType.INTERACTIVE_BROKERS,
                BrokerType.TD_AMERITRADE,
            ],
        }

        # Default to top brokers if strategy not recognized
        recommended_broker_types = strategy_broker_mapping.get(
            strategy_type,
            [
                BrokerType.INTERACTIVE_BROKERS,
                BrokerType.CHARLES_SCHWAB,
                BrokerType.FIDELITY,
            ],
        )

        recommendations = []
        for broker_type in recommended_broker_types:
            if broker_type in AffiliateService.BROKERS:
                broker = AffiliateService.BROKERS[broker_type]
                recommendations.append({
                    "broker": broker.broker.value,
                    "name": broker.name,
                    "logo_url": broker.logo_url,
                    "signup_url": broker.signup_url,
                    "description": broker.description,
                    "features": broker.features,
                    "recommended_for": broker.recommended_for,
                    "commission": broker.commission_per_referral,
                    "display_commission": f"${broker.commission_per_referral:.0f}" if broker.commission_per_referral > 0 else "Paid",
                })

        return recommendations

    @staticmethod
    def get_affiliate_link(broker: BrokerType, utm_params: Optional[Dict] = None) -> Optional[str]:
        """
        Get affiliate link for a broker with UTM tracking parameters

        UTM params: campaign, medium, source, content
        """
        if broker not in AffiliateService.BROKERS:
            return None

        base_url = AffiliateService.BROKERS[broker].signup_url

        if utm_params:
            # Add UTM parameters for tracking
            utm_string = "&".join([f"{k}={v}" for k, v in utm_params.items()])
            separator = "&" if "?" in base_url else "?"
            return f"{base_url}{separator}{utm_string}"

        return base_url

    @staticmethod
    def track_affiliate_click(
        session: AsyncSession,
        broker: str,
        user_id: Optional[str],
        backtest_id: Optional[str],
        strategy: str,
    ) -> bool:
        """
        Track affiliate link clicks for analytics and commission tracking

        Could be extended to store in database for commission reconciliation
        """
        try:
            logger.info(
                f"Affiliate click tracked: broker={broker}, user={user_id}, "
                f"strategy={strategy}, backtest={backtest_id}"
            )
            return True
        except Exception as e:
            logger.error(f"Failed to track affiliate click: {e}")
            return False

    @staticmethod
    def get_broker_by_strategy(strategy: str) -> Optional[Dict]:
        """
        Get the top recommended broker for a specific strategy

        Used for single broker recommendation
        """
        recommendations = AffiliateService.get_recommended_brokers(strategy, "free")
        if recommendations:
            return recommendations[0]
        return None

    @staticmethod
    def get_all_brokers() -> List[Dict]:
        """Get all available brokers with affiliate links"""
        brokers = []
        for broker in AffiliateService.BROKERS.values():
            brokers.append({
                "broker": broker.broker.value,
                "name": broker.name,
                "logo_url": broker.logo_url,
                "signup_url": broker.signup_url,
                "description": broker.description,
                "features": broker.features,
                "commission": broker.commission_per_referral,
            })
        return brokers

    @staticmethod
    def calculate_potential_revenue(
        recommended_brokers: List[Dict],
        estimated_conversion_rate: float = 0.05,  # 5% conversion
        users_viewing_results: int = 1,
    ) -> Dict:
        """
        Calculate potential affiliate revenue from backtest results

        Used for marketing and ROI estimation
        """
        total_users = len(recommended_brokers) * users_viewing_results
        estimated_conversions = total_users * estimated_conversion_rate

        total_commission = sum([
            b["commission"] * estimated_conversions
            for b in recommended_brokers
        ])

        return {
            "total_users": total_users,
            "estimated_conversions": estimated_conversions,
            "total_commission": total_commission,
            "avg_commission_per_signup": total_commission / estimated_conversions if estimated_conversions > 0 else 0,
        }
