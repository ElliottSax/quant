"""
Premium Features Service
Advanced analytics and features for premium users
"""

from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_, or_

from app.models.politician import Politician
from app.models.trade import Trade
from app.core.logging import get_logger
from app.core.performance import cached, timed
from app.core.alerts import alerting, AlertSeverity

logger = get_logger(__name__)


class AdvancedAnalytics:
    """Advanced analytics for premium users"""

    @staticmethod
    @timed("advanced_pattern_detection")
    @cached(ttl=1800, key_prefix="premium:patterns")
    async def detect_trading_patterns(
        db: AsyncSession,
        politician_id: Optional[str] = None,
        days: int = 90
    ) -> Dict[str, Any]:
        """
        Detect advanced trading patterns
        - Insider trading indicators
        - Unusual activity
        - Correlation patterns
        """
        cutoff_date = datetime.utcnow() - timedelta(days=days)

        # Build query
        query = select(Trade).where(Trade.transaction_date >= cutoff_date)
        if politician_id:
            query = query.where(Trade.politician_id == politician_id)

        result = await db.execute(query)
        trades = result.scalars().all()

        patterns = {
            'unusual_volume': [],
            'clustered_trades': [],
            'pre_announcement_trades': [],
            'synchronized_trades': []
        }

        # Detect unusual volume
        avg_trade_size = sum(t.amount for t in trades) / len(trades) if trades else 0
        for trade in trades:
            if trade.amount > avg_trade_size * 3:
                patterns['unusual_volume'].append({
                    'trade_id': str(trade.id),
                    'politician': trade.politician_id,
                    'amount': trade.amount,
                    'date': trade.transaction_date.isoformat()
                })

        # Detect clustered trades (multiple trades in short period)
        trade_dates = {}
        for trade in trades:
            date_key = trade.transaction_date.date()
            if date_key not in trade_dates:
                trade_dates[date_key] = []
            trade_dates[date_key].append(trade)

        for date, day_trades in trade_dates.items():
            if len(day_trades) >= 3:
                patterns['clustered_trades'].append({
                    'date': date.isoformat(),
                    'trade_count': len(day_trades),
                    'total_amount': sum(t.amount for t in day_trades)
                })

        return {
            'patterns': patterns,
            'analysis_period_days': days,
            'total_trades_analyzed': len(trades),
            'generated_at': datetime.utcnow().isoformat()
        }

    @staticmethod
    @timed("portfolio_correlation")
    async def analyze_portfolio_correlation(
        db: AsyncSession,
        politician_id: str,
        days: int = 180
    ) -> Dict[str, Any]:
        """
        Analyze correlation between politician's trades and market movements
        """
        # This would integrate with market data to analyze correlations
        # For now, return structure
        return {
            'politician_id': politician_id,
            'correlation_score': 0.0,  # Placeholder
            'analysis_period_days': days,
            'correlated_sectors': [],
            'performance_vs_market': {
                'politician_return': 0.0,
                'market_return': 0.0,
                'alpha': 0.0
            }
        }

    @staticmethod
    @timed("risk_assessment")
    async def assess_portfolio_risk(
        db: AsyncSession,
        politician_id: str
    ) -> Dict[str, Any]:
        """
        Assess risk metrics for politician's portfolio
        """
        # Get all trades
        query = select(Trade).where(Trade.politician_id == politician_id)
        result = await db.execute(query)
        trades = result.scalars().all()

        if not trades:
            return {
                'risk_score': 0,
                'risk_level': 'unknown',
                'message': 'No trades found'
            }

        # Calculate basic risk metrics
        total_amount = sum(t.amount for t in trades)
        avg_trade_size = total_amount / len(trades)
        max_trade = max(t.amount for t in trades)

        # Concentration risk (simplified)
        concentration_risk = max_trade / total_amount if total_amount > 0 else 0

        # Risk score (0-100)
        risk_score = min(100, concentration_risk * 100)

        risk_level = 'low' if risk_score < 30 else 'medium' if risk_score < 70 else 'high'

        return {
            'risk_score': round(risk_score, 2),
            'risk_level': risk_level,
            'concentration_risk': round(concentration_risk, 2),
            'total_exposure': total_amount,
            'largest_position': max_trade,
            'position_count': len(trades),
            'avg_position_size': round(avg_trade_size, 2)
        }


class RealTimeAlerts:
    """Real-time alert system for premium users"""

    @staticmethod
    async def create_price_alert(
        user_id: str,
        symbol: str,
        target_price: float,
        condition: str = "above"
    ):
        """Create price alert"""
        # Store alert configuration
        alert_config = {
            'user_id': user_id,
            'symbol': symbol,
            'target_price': target_price,
            'condition': condition,
            'created_at': datetime.utcnow(),
            'triggered': False
        }

        # In production, this would be stored in database
        logger.info(f"Price alert created for {symbol} at ${target_price}")

        return alert_config

    @staticmethod
    async def check_price_alerts(symbol: str, current_price: float):
        """Check if any alerts should be triggered"""
        # In production, query database for active alerts
        # For now, just log
        logger.info(f"Checking alerts for {symbol} at ${current_price}")

    @staticmethod
    async def create_politician_activity_alert(
        user_id: str,
        politician_id: str,
        alert_types: List[str]
    ):
        """Create alert for politician activity"""
        alert_config = {
            'user_id': user_id,
            'politician_id': politician_id,
            'alert_types': alert_types,  # ['new_trade', 'large_trade', 'unusual_activity']
            'created_at': datetime.utcnow()
        }

        logger.info(f"Activity alert created for politician {politician_id}")

        return alert_config

    @staticmethod
    async def trigger_trade_alert(trade_data: Dict[str, Any]):
        """Trigger alert for new trade"""
        await alerting.send_alert(
            title="New Political Trade Detected",
            message=f"${trade_data['amount']:,.2f} trade in {trade_data['symbol']}",
            severity=AlertSeverity.INFO,
            metadata=trade_data
        )


class PortfolioTracking:
    """Portfolio tracking and performance monitoring"""

    @staticmethod
    async def create_watchlist(
        user_id: str,
        name: str,
        politicians: List[str]
    ) -> Dict[str, Any]:
        """Create a custom watchlist"""
        watchlist = {
            'id': f"watchlist_{user_id}_{datetime.utcnow().timestamp()}",
            'user_id': user_id,
            'name': name,
            'politicians': politicians,
            'created_at': datetime.utcnow(),
            'updated_at': datetime.utcnow()
        }

        logger.info(f"Watchlist created: {name} with {len(politicians)} politicians")

        return watchlist

    @staticmethod
    @timed("portfolio_performance")
    async def calculate_portfolio_performance(
        db: AsyncSession,
        politician_ids: List[str],
        start_date: datetime,
        end_date: datetime
    ) -> Dict[str, Any]:
        """Calculate portfolio performance metrics"""
        query = select(Trade).where(
            and_(
                Trade.politician_id.in_(politician_ids),
                Trade.transaction_date >= start_date,
                Trade.transaction_date <= end_date
            )
        )

        result = await db.execute(query)
        trades = result.scalars().all()

        # Calculate metrics
        total_volume = sum(t.amount for t in trades)
        trade_count = len(trades)

        # Group by action
        buys = [t for t in trades if t.action.lower() == 'purchase']
        sells = [t for t in trades if t.action.lower() == 'sale']

        return {
            'period': {
                'start': start_date.isoformat(),
                'end': end_date.isoformat()
            },
            'summary': {
                'total_trades': trade_count,
                'total_volume': total_volume,
                'buy_count': len(buys),
                'sell_count': len(sells),
                'buy_volume': sum(t.amount for t in buys),
                'sell_volume': sum(t.amount for t in sells)
            },
            'by_politician': {}  # Would include per-politician breakdown
        }


class CustomReports:
    """Custom report generation for premium users"""

    @staticmethod
    @timed("generate_custom_report")
    async def generate_activity_report(
        db: AsyncSession,
        filters: Dict[str, Any],
        format: str = "json"
    ) -> Dict[str, Any]:
        """
        Generate custom activity report

        Filters can include:
        - date_range
        - politicians
        - symbols
        - trade_types
        - min_amount
        """
        # Build query from filters
        query = select(Trade)

        if 'politician_ids' in filters:
            query = query.where(Trade.politician_id.in_(filters['politician_ids']))

        if 'start_date' in filters:
            query = query.where(Trade.transaction_date >= filters['start_date'])

        if 'end_date' in filters:
            query = query.where(Trade.transaction_date <= filters['end_date'])

        if 'min_amount' in filters:
            query = query.where(Trade.amount >= filters['min_amount'])

        result = await db.execute(query)
        trades = result.scalars().all()

        # Generate report
        report = {
            'report_id': f"report_{datetime.utcnow().timestamp()}",
            'generated_at': datetime.utcnow().isoformat(),
            'filters': filters,
            'format': format,
            'data': {
                'trade_count': len(trades),
                'total_volume': sum(t.amount for t in trades),
                'trades': [
                    {
                        'date': t.transaction_date.isoformat(),
                        'politician': t.politician_id,
                        'symbol': getattr(t, 'symbol', 'N/A'),
                        'action': t.action,
                        'amount': t.amount
                    }
                    for t in trades[:100]  # Limit for response size
                ]
            }
        }

        return report

    @staticmethod
    async def export_report(report_data: Dict[str, Any], format: str = "csv"):
        """Export report in specified format"""
        # Would generate CSV, Excel, PDF, etc.
        logger.info(f"Exporting report in {format} format")

        return {
            'format': format,
            'download_url': '/api/v1/reports/download/123',  # Placeholder
            'expires_at': (datetime.utcnow() + timedelta(hours=24)).isoformat()
        }


class PremiumFeaturesService:
    """Main service coordinating all premium features"""

    def __init__(self):
        self.analytics = AdvancedAnalytics()
        self.alerts = RealTimeAlerts()
        self.portfolio = PortfolioTracking()
        self.reports = CustomReports()

    async def check_premium_access(self, user_id: str) -> bool:
        """Check if user has premium access"""
        # In production, query subscription status from database
        # For now, return True for testing
        return True

    async def get_premium_features_summary(self) -> Dict[str, Any]:
        """Get summary of available premium features"""
        return {
            'features': [
                {
                    'name': 'Advanced Pattern Detection',
                    'description': 'Detect insider trading patterns and unusual activity',
                    'endpoint': '/api/v1/premium/analytics/patterns'
                },
                {
                    'name': 'Portfolio Correlation Analysis',
                    'description': 'Analyze correlation with market movements',
                    'endpoint': '/api/v1/premium/analytics/correlation'
                },
                {
                    'name': 'Real-Time Alerts',
                    'description': 'Get notified of important events instantly',
                    'endpoint': '/api/v1/premium/alerts'
                },
                {
                    'name': 'Custom Watchlists',
                    'description': 'Track specific politicians and symbols',
                    'endpoint': '/api/v1/premium/watchlists'
                },
                {
                    'name': 'Advanced Reporting',
                    'description': 'Generate custom reports with flexible filters',
                    'endpoint': '/api/v1/premium/reports'
                },
                {
                    'name': 'Risk Assessment',
                    'description': 'Comprehensive portfolio risk analysis',
                    'endpoint': '/api/v1/premium/analytics/risk'
                }
            ],
            'subscription_required': True
        }


# Global service instance
premium_service = PremiumFeaturesService()
