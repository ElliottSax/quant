"""
Portfolio Service for tracking politician holdings and performance.
"""

from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
from decimal import Decimal
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, func

from app.models.portfolio import Portfolio, Watchlist
from app.models.trade import Trade
from app.models.politician import Politician
from app.core.logging import get_logger

logger = get_logger(__name__)


class PortfolioService:
    """Service for portfolio tracking and analysis."""

    async def create_watchlist(
        self,
        db: AsyncSession,
        user_id: str,
        name: str,
        politician_ids: List[str],
        description: Optional[str] = None,
        is_public: bool = False
    ) -> Watchlist:
        """
        Create a custom watchlist.

        Args:
            db: Database session
            user_id: User ID
            name: Watchlist name
            politician_ids: List of politician IDs
            description: Description (optional)
            is_public: Whether watchlist is public

        Returns:
            Created watchlist
        """
        watchlist = Watchlist(
            user_id=user_id,
            name=name,
            politician_ids=politician_ids,
            description=description,
            is_public=is_public,
        )

        db.add(watchlist)
        await db.commit()
        await db.refresh(watchlist)

        logger.info(f"Created watchlist {watchlist.id} for user {user_id}")

        return watchlist

    async def get_user_watchlists(
        self,
        db: AsyncSession,
        user_id: str
    ) -> List[Watchlist]:
        """
        Get all watchlists for a user.

        Args:
            db: Database session
            user_id: User ID

        Returns:
            List of watchlists
        """
        query = select(Watchlist).where(
            Watchlist.user_id == user_id
        ).order_by(Watchlist.sort_order, Watchlist.created_at)

        result = await db.execute(query)
        return result.scalars().all()

    async def update_watchlist(
        self,
        db: AsyncSession,
        watchlist_id: str,
        user_id: str,
        **updates
    ) -> Optional[Watchlist]:
        """
        Update a watchlist.

        Args:
            db: Database session
            watchlist_id: Watchlist ID
            user_id: User ID (for authorization)
            **updates: Fields to update

        Returns:
            Updated watchlist or None
        """
        query = select(Watchlist).where(
            and_(
                Watchlist.id == watchlist_id,
                Watchlist.user_id == user_id
            )
        )

        result = await db.execute(query)
        watchlist = result.scalar_one_or_none()

        if not watchlist:
            return None

        for key, value in updates.items():
            if hasattr(watchlist, key):
                setattr(watchlist, key, value)

        await db.commit()
        await db.refresh(watchlist)

        return watchlist

    async def delete_watchlist(
        self,
        db: AsyncSession,
        watchlist_id: str,
        user_id: str
    ) -> bool:
        """
        Delete a watchlist.

        Args:
            db: Database session
            watchlist_id: Watchlist ID
            user_id: User ID (for authorization)

        Returns:
            True if deleted
        """
        query = select(Watchlist).where(
            and_(
                Watchlist.id == watchlist_id,
                Watchlist.user_id == user_id
            )
        )

        result = await db.execute(query)
        watchlist = result.scalar_one_or_none()

        if not watchlist:
            return False

        await db.delete(watchlist)
        await db.commit()

        return True

    async def calculate_portfolio_snapshot(
        self,
        db: AsyncSession,
        politician_id: str,
        snapshot_date: Optional[datetime] = None
    ) -> Portfolio:
        """
        Calculate and store a portfolio snapshot for a politician.

        Args:
            db: Database session
            politician_id: Politician ID
            snapshot_date: Snapshot date (defaults to now)

        Returns:
            Portfolio snapshot
        """
        if not snapshot_date:
            snapshot_date = datetime.utcnow()

        # Get all trades up to snapshot date
        query = select(Trade).where(
            and_(
                Trade.politician_id == politician_id,
                Trade.transaction_date <= snapshot_date.date()
            )
        ).order_by(Trade.transaction_date)

        result = await db.execute(query)
        trades = result.scalars().all()

        # Calculate holdings
        holdings = {}

        for trade in trades:
            ticker = trade.ticker

            if ticker not in holdings:
                holdings[ticker] = {
                    "ticker": ticker,
                    "shares": 0,
                    "total_cost": Decimal(0),
                    "transactions": [],
                }

            # Estimate share count based on amount
            # This is simplified - in reality would need actual share prices
            amount_mid = (trade.amount_min or 0) + (trade.amount_max or 0)
            amount_mid = amount_mid / 2 if trade.amount_max else amount_mid

            if trade.transaction_type == "buy":
                holdings[ticker]["shares"] += 1  # Placeholder
                holdings[ticker]["total_cost"] += Decimal(amount_mid)
            elif trade.transaction_type == "sell":
                holdings[ticker]["shares"] -= 1  # Placeholder
                holdings[ticker]["total_cost"] -= Decimal(amount_mid)

            holdings[ticker]["transactions"].append({
                "date": trade.transaction_date.isoformat(),
                "type": trade.transaction_type,
                "amount": float(amount_mid),
            })

        # Filter out zero holdings
        active_holdings = [
            h for h in holdings.values()
            if h["shares"] > 0
        ]

        # Calculate total value
        total_value = sum(Decimal(h["total_cost"]) for h in active_holdings)

        # Calculate sector allocation (simplified)
        sector_allocation = self._estimate_sector_allocation(active_holdings)

        # Calculate concentration
        concentration_score = self._calculate_concentration(active_holdings, total_value)

        # Create portfolio snapshot
        portfolio = Portfolio(
            politician_id=politician_id,
            snapshot_date=snapshot_date,
            holdings=active_holdings,
            total_value=total_value,
            total_cost_basis=total_value,  # Simplified
            sector_allocation=sector_allocation,
            concentration_score=concentration_score,
        )

        db.add(portfolio)
        await db.commit()
        await db.refresh(portfolio)

        logger.info(f"Created portfolio snapshot for politician {politician_id}")

        return portfolio

    def _estimate_sector_allocation(self, holdings: List[Dict]) -> Dict[str, float]:
        """
        Estimate sector allocation from holdings.

        This is a placeholder - in production would look up actual sector data.
        """
        # Simplified sector mapping
        sector_map = {
            "AAPL": "Technology",
            "MSFT": "Technology",
            "GOOGL": "Technology",
            "AMZN": "Consumer",
            "TSLA": "Automotive",
            "JPM": "Finance",
            "BAC": "Finance",
            "UNH": "Healthcare",
            "JNJ": "Healthcare",
        }

        sectors = {}

        for holding in holdings:
            ticker = holding["ticker"]
            sector = sector_map.get(ticker, "Other")

            if sector not in sectors:
                sectors[sector] = 0.0

            sectors[sector] += float(holding["total_cost"])

        # Convert to percentages
        total = sum(sectors.values())

        if total > 0:
            sectors = {k: (v / total) * 100 for k, v in sectors.items()}

        return sectors

    def _calculate_concentration(
        self,
        holdings: List[Dict],
        total_value: Decimal
    ) -> Decimal:
        """
        Calculate concentration score (0-100).

        Higher score means more concentrated portfolio.
        """
        if not holdings or total_value == 0:
            return Decimal(0)

        # Calculate HHI (Herfindahl-Hirschman Index)
        hhi = Decimal(0)

        for holding in holdings:
            weight = Decimal(holding["total_cost"]) / total_value
            hhi += weight * weight

        # Normalize to 0-100 scale
        # HHI ranges from 1/N to 1 (where N is number of holdings)
        # Perfect diversification (equal weights) = 1/N
        # Maximum concentration (one holding) = 1

        n = len(holdings)
        min_hhi = Decimal(1) / Decimal(n)
        max_hhi = Decimal(1)

        if max_hhi == min_hhi:
            return Decimal(0)

        normalized = (hhi - min_hhi) / (max_hhi - min_hhi)

        return normalized * Decimal(100)

    async def get_portfolio_history(
        self,
        db: AsyncSession,
        politician_id: str,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> List[Portfolio]:
        """
        Get portfolio history for a politician.

        Args:
            db: Database session
            politician_id: Politician ID
            start_date: Start date (optional)
            end_date: End date (optional)

        Returns:
            List of portfolio snapshots
        """
        query = select(Portfolio).where(
            Portfolio.politician_id == politician_id
        )

        if start_date:
            query = query.where(Portfolio.snapshot_date >= start_date)

        if end_date:
            query = query.where(Portfolio.snapshot_date <= end_date)

        query = query.order_by(Portfolio.snapshot_date)

        result = await db.execute(query)
        return result.scalars().all()

    async def calculate_portfolio_performance(
        self,
        db: AsyncSession,
        politician_ids: List[str],
        start_date: datetime,
        end_date: datetime
    ) -> Dict[str, Any]:
        """
        Calculate portfolio performance for politicians.

        Args:
            db: Database session
            politician_ids: List of politician IDs
            start_date: Start date
            end_date: End date

        Returns:
            Performance metrics
        """
        # Get all trades in period
        query = select(Trade).where(
            and_(
                Trade.politician_id.in_(politician_ids),
                Trade.transaction_date >= start_date.date(),
                Trade.transaction_date <= end_date.date()
            )
        )

        result = await db.execute(query)
        trades = result.scalars().all()

        # Calculate metrics
        total_volume = Decimal(0)
        buy_volume = Decimal(0)
        sell_volume = Decimal(0)

        for trade in trades:
            amount_mid = (trade.amount_min or 0) + (trade.amount_max or 0)
            amount_mid = Decimal(amount_mid) / 2 if trade.amount_max else Decimal(amount_mid)

            total_volume += amount_mid

            if trade.transaction_type == "buy":
                buy_volume += amount_mid
            elif trade.transaction_type == "sell":
                sell_volume += amount_mid

        # Calculate by politician
        by_politician = {}

        for politician_id in politician_ids:
            politician_trades = [t for t in trades if str(t.politician_id) == politician_id]

            politician_volume = sum(
                Decimal((t.amount_min or 0) + (t.amount_max or 0)) / 2
                if t.amount_max else Decimal(t.amount_min or 0)
                for t in politician_trades
            )

            by_politician[politician_id] = {
                "trade_count": len(politician_trades),
                "total_volume": float(politician_volume),
            }

        return {
            "period": {
                "start": start_date.isoformat(),
                "end": end_date.isoformat(),
            },
            "summary": {
                "total_trades": len(trades),
                "total_volume": float(total_volume),
                "buy_volume": float(buy_volume),
                "sell_volume": float(sell_volume),
                "buy_count": sum(1 for t in trades if t.transaction_type == "buy"),
                "sell_count": sum(1 for t in trades if t.transaction_type == "sell"),
            },
            "by_politician": by_politician,
        }

    async def get_portfolio_report(
        self,
        db: AsyncSession,
        politician_id: str
    ) -> Dict[str, Any]:
        """
        Generate comprehensive portfolio report for a politician.

        Args:
            db: Database session
            politician_id: Politician ID

        Returns:
            Portfolio report
        """
        # Get politician info
        query = select(Politician).where(Politician.id == politician_id)
        result = await db.execute(query)
        politician = result.scalar_one_or_none()

        if not politician:
            return {"error": "Politician not found"}

        # Get latest portfolio snapshot
        portfolio_query = select(Portfolio).where(
            Portfolio.politician_id == politician_id
        ).order_by(Portfolio.snapshot_date.desc()).limit(1)

        portfolio_result = await db.execute(portfolio_query)
        latest_portfolio = portfolio_result.scalar_one_or_none()

        # Get all trades
        trades_query = select(Trade).where(
            Trade.politician_id == politician_id
        ).order_by(Trade.transaction_date.desc())

        trades_result = await db.execute(trades_query)
        trades = trades_result.scalars().all()

        return {
            "politician": {
                "id": str(politician.id),
                "name": politician.name,
                "position": getattr(politician, "position", ""),
                "state": getattr(politician, "state", ""),
            },
            "portfolio": {
                "snapshot_date": latest_portfolio.snapshot_date.isoformat() if latest_portfolio else None,
                "total_value": float(latest_portfolio.total_value) if latest_portfolio else 0,
                "holdings_count": len(latest_portfolio.holdings) if latest_portfolio else 0,
                "sector_allocation": latest_portfolio.sector_allocation if latest_portfolio else {},
                "concentration_score": float(latest_portfolio.concentration_score) if latest_portfolio else 0,
            },
            "activity": {
                "total_trades": len(trades),
                "recent_trades": [
                    {
                        "date": t.transaction_date.isoformat(),
                        "ticker": t.ticker,
                        "type": t.transaction_type,
                        "amount_min": float(t.amount_min) if t.amount_min else None,
                        "amount_max": float(t.amount_max) if t.amount_max else None,
                    }
                    for t in trades[:10]
                ],
            },
        }


# Global service instance
portfolio_service = PortfolioService()
