"""Statistics service for performance calculations."""

from datetime import date, timedelta
from typing import Any

from sqlalchemy import func, select, desc
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.politician import Politician
from app.models.trade import Trade


class StatisticsService:
    """Service for calculating trading statistics."""

    @staticmethod
    def _get_date_range(period: str) -> tuple[date, date]:
        """
        Get date range for a given period.

        Args:
            period: Time period (7d, 30d, 90d, 1y, all)

        Returns:
            Tuple of (start_date, end_date)
        """
        end_date = date.today()

        period_days = {
            "7d": 7,
            "30d": 30,
            "90d": 90,
            "1y": 365,
            "all": 365 * 10,  # 10 years back
        }

        days = period_days.get(period, 30)
        start_date = end_date - timedelta(days=days)

        return start_date, end_date

    async def get_leaderboard(
        self,
        db: AsyncSession,
        period: str = "30d",
        limit: int = 50,
        chamber: str | None = None,
        party: str | None = None,
    ) -> list[dict[str, Any]]:
        """
        Get politician performance leaderboard.

        Args:
            db: Database session
            period: Time period (7d, 30d, 90d, 1y, all)
            limit: Maximum number of records to return
            chamber: Filter by chamber (senate/house)
            party: Filter by party

        Returns:
            List of politicians with trade statistics
        """
        start_date, end_date = self._get_date_range(period)

        # Build query
        query = (
            select(
                Politician.id,
                Politician.name,
                Politician.chamber,
                Politician.party,
                Politician.state,
                func.count(Trade.id).label("trade_count"),
                func.count(
                    func.distinct(
                        func.case(
                            (Trade.transaction_type == "buy", Trade.id),
                            else_=None,
                        )
                    )
                ).label("buy_count"),
                func.count(
                    func.distinct(
                        func.case(
                            (Trade.transaction_type == "sell", Trade.id),
                            else_=None,
                        )
                    )
                ).label("sell_count"),
                func.avg(
                    func.coalesce(
                        (Trade.amount_min + Trade.amount_max) / 2,
                        Trade.amount_min,
                        Trade.amount_max,
                    )
                ).label("avg_trade_size"),
                func.min(Trade.transaction_date).label("first_trade_date"),
                func.max(Trade.transaction_date).label("last_trade_date"),
            )
            .join(Trade, Politician.id == Trade.politician_id)
            .where(Trade.transaction_date >= start_date)
            .where(Trade.transaction_date <= end_date)
            .group_by(
                Politician.id,
                Politician.name,
                Politician.chamber,
                Politician.party,
                Politician.state,
            )
        )

        # Apply filters
        if chamber:
            query = query.where(Politician.chamber == chamber)
        if party:
            query = query.where(Politician.party == party)

        # Order by trade count and limit
        query = query.order_by(desc("trade_count")).limit(limit)

        result = await db.execute(query)
        rows = result.all()

        # Format results
        leaderboard = []
        for row in rows:
            # Calculate days between first and last trade
            days_trading = 0
            if row.first_trade_date and row.last_trade_date:
                days_trading = (row.last_trade_date - row.first_trade_date).days

            leaderboard.append(
                {
                    "id": str(row.id),
                    "name": row.name,
                    "chamber": row.chamber,
                    "party": row.party,
                    "state": row.state,
                    "trade_count": row.trade_count,
                    "buy_count": row.buy_count,
                    "sell_count": row.sell_count,
                    "avg_trade_size": float(row.avg_trade_size) if row.avg_trade_size else None,
                    "first_trade_date": row.first_trade_date.isoformat() if row.first_trade_date else None,
                    "last_trade_date": row.last_trade_date.isoformat() if row.last_trade_date else None,
                    "days_trading": days_trading,
                    "trades_per_day": (
                        round(row.trade_count / days_trading, 2) if days_trading > 0 else 0
                    ),
                }
            )

        return leaderboard

    async def get_sector_stats(
        self,
        db: AsyncSession,
        period: str = "30d",
    ) -> dict[str, Any]:
        """
        Get sector trading statistics.

        Note: This is a simplified version that groups by ticker.
        A full implementation would require market data API to map tickers to sectors.

        Args:
            db: Database session
            period: Time period (7d, 30d, 90d, 1y, all)

        Returns:
            Sector statistics
        """
        start_date, end_date = self._get_date_range(period)

        # Get top traded tickers
        query = (
            select(
                Trade.ticker,
                func.count(Trade.id).label("trade_count"),
                func.count(
                    func.distinct(
                        func.case(
                            (Trade.transaction_type == "buy", Trade.id),
                            else_=None,
                        )
                    )
                ).label("buy_count"),
                func.count(
                    func.distinct(
                        func.case(
                            (Trade.transaction_type == "sell", Trade.id),
                            else_=None,
                        )
                    )
                ).label("sell_count"),
                func.avg(
                    func.coalesce(
                        (Trade.amount_min + Trade.amount_max) / 2,
                        Trade.amount_min,
                        Trade.amount_max,
                    )
                ).label("avg_trade_size"),
                func.sum(
                    func.coalesce(
                        (Trade.amount_min + Trade.amount_max) / 2,
                        Trade.amount_min,
                        Trade.amount_max,
                        0,
                    )
                ).label("total_volume"),
            )
            .where(Trade.transaction_date >= start_date)
            .where(Trade.transaction_date <= end_date)
            .group_by(Trade.ticker)
            .order_by(desc("trade_count"))
            .limit(50)
        )

        result = await db.execute(query)
        rows = result.all()

        # Format results
        tickers = []
        total_trades = 0
        for row in rows:
            total_trades += row.trade_count
            tickers.append(
                {
                    "ticker": row.ticker,
                    "trade_count": row.trade_count,
                    "buy_count": row.buy_count,
                    "sell_count": row.sell_count,
                    "avg_trade_size": float(row.avg_trade_size) if row.avg_trade_size else None,
                    "total_volume": float(row.total_volume) if row.total_volume else 0,
                    "buy_sell_ratio": (
                        round(row.buy_count / row.sell_count, 2)
                        if row.sell_count > 0
                        else None
                    ),
                }
            )

        # Calculate percentages
        for ticker in tickers:
            ticker["percentage"] = (
                round((ticker["trade_count"] / total_trades) * 100, 1) if total_trades > 0 else 0
            )

        return {
            "period": period,
            "start_date": start_date.isoformat(),
            "end_date": end_date.isoformat(),
            "total_trades": total_trades,
            "tickers": tickers,
        }

    async def get_recent_trades(
        self,
        db: AsyncSession,
        limit: int = 20,
        chamber: str | None = None,
        party: str | None = None,
        transaction_type: str | None = None,
    ) -> list[dict[str, Any]]:
        """
        Get most recent trades with politician info.

        Args:
            db: Database session
            limit: Maximum number of trades to return
            chamber: Filter by chamber
            party: Filter by party
            transaction_type: Filter by transaction type (buy/sell)

        Returns:
            List of recent trades with politician info
        """
        query = (
            select(
                Trade.id,
                Trade.ticker,
                Trade.transaction_type,
                Trade.amount_min,
                Trade.amount_max,
                Trade.transaction_date,
                Trade.disclosure_date,
                Politician.id.label("politician_id"),
                Politician.name.label("politician_name"),
                Politician.chamber,
                Politician.party,
                Politician.state,
            )
            .join(Politician, Trade.politician_id == Politician.id)
            .order_by(Trade.disclosure_date.desc(), Trade.transaction_date.desc())
        )

        # Apply filters
        if chamber:
            query = query.where(Politician.chamber == chamber)
        if party:
            query = query.where(Politician.party == party)
        if transaction_type:
            query = query.where(Trade.transaction_type == transaction_type)

        query = query.limit(limit)

        result = await db.execute(query)
        rows = result.all()

        # Format results
        trades = []
        for row in rows:
            trades.append(
                {
                    "id": str(row.id),
                    "ticker": row.ticker,
                    "transaction_type": row.transaction_type,
                    "amount_min": float(row.amount_min) if row.amount_min else None,
                    "amount_max": float(row.amount_max) if row.amount_max else None,
                    "transaction_date": row.transaction_date.isoformat(),
                    "disclosure_date": row.disclosure_date.isoformat(),
                    "disclosure_delay_days": (row.disclosure_date - row.transaction_date).days,
                    "politician": {
                        "id": str(row.politician_id),
                        "name": row.politician_name,
                        "chamber": row.chamber,
                        "party": row.party,
                        "state": row.state,
                    },
                }
            )

        return trades
