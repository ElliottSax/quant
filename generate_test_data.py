#!/usr/bin/env python3
"""
Generate Sample Trade Data for Analytics Testing

Creates realistic trading patterns for politicians to test advanced analytics.
"""

import asyncio
import sys
import os
from datetime import datetime, timedelta
import random
import numpy as np

# Add backend to path
sys.path.insert(0, '/mnt/e/projects/quant/quant/backend')

from sqlalchemy import select, delete, text
from decimal import Decimal
from app.core.database import AsyncSessionLocal
from app.models.politician import Politician
from app.models.trade import Trade

async def generate_cyclical_trades(politician_id: str, start_date: datetime,
                                   num_months: int, cycle_days: int,
                                   base_frequency: float = 2.0):
    """Generate trades with a cyclical pattern."""
    trades = []
    current_date = start_date
    end_date = start_date + timedelta(days=num_months * 30)

    while current_date < end_date:
        # Cyclical trading frequency
        days_since_start = (current_date - start_date).days
        cycle_position = (days_since_start % cycle_days) / cycle_days * 2 * np.pi
        frequency_multiplier = 1.0 + 0.5 * np.sin(cycle_position)

        # Decide if trade happens today (stochastic)
        if random.random() < (base_frequency / 30) * frequency_multiplier:
            # Create a trade
            amount_ranges = [
                (1000, 15000),
                (15001, 50000),
                (50001, 100000),
                (100001, 250000),
                (250001, 500000)
            ]

            amount_range = random.choice(amount_ranges)
            amount_min = Decimal(amount_range[0])
            amount_max = Decimal(amount_range[1])

            trade = Trade(
                politician_id=politician_id,
                transaction_date=current_date.date(),
                disclosure_date=(current_date + timedelta(days=random.randint(1, 45))).date(),
                ticker=random.choice(["AAPL", "MSFT", "GOOGL", "AMZN", "TSLA",
                                     "NVDA", "META", "JPM", "V", "UNH"]),
                transaction_type=random.choice(["buy", "sell"]),
                amount_min=amount_min,
                amount_max=amount_max
            )
            trades.append(trade)

        current_date += timedelta(days=1)

    return trades

async def main():
    print("\n" + "="*80)
    print("GENERATING SAMPLE TRADE DATA FOR ANALYTICS TESTING")
    print("="*80 + "\n")

    async with AsyncSessionLocal() as db:
        # Get existing politicians
        result = await db.execute(select(Politician))
        politicians = result.scalars().all()

        if not politicians:
            print("No politicians found in database!")
            return

        print(f"Found {len(politicians)} politicians")
        print("Generating trading patterns...\n")

        # Generate different patterns for different politicians
        # Need 120+ trades for DTW analysis
        patterns = [
            {"cycle_days": 30, "base_frequency": 5.5, "months": 24},   # Monthly cycle, higher frequency
            {"cycle_days": 45, "base_frequency": 4.5, "months": 24},   # 45-day cycle
            {"cycle_days": 60, "base_frequency": 4.5, "months": 24},   # 60-day cycle
            {"cycle_days": 90, "base_frequency": 4.0, "months": 24},   # Quarterly cycle
            {"cycle_days": 120, "base_frequency": 4.5, "months": 24},  # 4-month cycle
        ]

        start_date = datetime(2023, 1, 1)
        total_trades = 0

        for politician, pattern in zip(politicians[:5], patterns):
            print(f"Generating trades for {politician.name}...")
            print(f"  Pattern: {pattern['cycle_days']}-day cycle, ~{pattern['base_frequency']} trades/month")

            # Delete existing trades
            await db.execute(
                delete(Trade).where(Trade.politician_id == politician.id)
            )

            # Generate new trades
            trades = await generate_cyclical_trades(
                politician_id=str(politician.id),
                start_date=start_date,
                num_months=pattern['months'],
                cycle_days=pattern['cycle_days'],
                base_frequency=pattern['base_frequency']
            )

            # Add to database
            for trade in trades:
                db.add(trade)

            print(f"  Generated {len(trades)} trades")
            total_trades += len(trades)

        # Commit all changes
        await db.commit()

        print(f"\n{'='*80}")
        print(f"SUCCESS: Generated {total_trades} trades across {len(politicians[:5])} politicians")
        print(f"{'='*80}\n")

        # Verify
        print("Verifying data...")
        for politician in politicians[:5]:
            result = await db.execute(
                select(Trade).where(Trade.politician_id == politician.id)
            )
            count = len(result.scalars().all())
            print(f"  {politician.name}: {count} trades")

if __name__ == "__main__":
    asyncio.run(main())
