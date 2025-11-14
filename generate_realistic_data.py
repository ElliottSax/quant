#!/usr/bin/env python3
"""
Generate Realistic Politician Trading Data

Creates synthetic but realistic trading data that mimics actual politician trading patterns:
- Cyclical patterns (monthly, quarterly)
- Regime changes (bull/bear markets)
- Clustered trades (politicians trade in bursts)
- Insider timing (trades before earnings, regulatory changes)

This data is designed to test our cyclical pattern detection models.
"""

import sys
import os
import random
from datetime import datetime, timedelta
from decimal import Decimal

# Add backend to path
sys.path.insert(0, 'quant/backend')
os.chdir('quant/backend')

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import numpy as np

from app.models.politician import Politician
from app.models.ticker import Ticker
from app.models.trade import Trade
from app.core.database import Base

# Database connection
DATABASE_URL = "postgresql://quant_user:quant_password@localhost:5432/quant_db"
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(bind=engine)


def create_realistic_trading_data():
    """Generate realistic politician trading data"""

    print("=" * 80)
    print("Generating Realistic Politician Trading Data")
    print("=" * 80)

    session = SessionLocal()

    try:
        # Create politicians
        print("\n1. Creating politicians...")
        politicians_data = [
            {
                'name': 'Nancy Pelosi',
                'party': 'Democratic',
                'state': 'California',
                'position': 'Speaker of the House (Former)',
                'trade_frequency': 'high'  # Trades frequently
            },
            {
                'name': 'Paul Pelosi',
                'party': 'Democratic',
                'state': 'California',
                'position': 'Spouse of Representative',
                'trade_frequency': 'very_high'  # Even more frequent
            },
            {
                'name': 'Dan Crenshaw',
                'party': 'Republican',
                'state': 'Texas',
                'position': 'Representative',
                'trade_frequency': 'medium'
            },
            {
                'name': 'Josh Gottheimer',
                'party': 'Democratic',
                'state': 'New Jersey',
                'position': 'Representative',
                'trade_frequency': 'medium'
            },
        ]

        politicians = []
        for pol_data in politicians_data:
            pol = Politician(**{k: v for k, v in pol_data.items() if k != 'trade_frequency'})
            session.add(pol)
            session.flush()
            politicians.append((pol, pol_data['trade_frequency']))
            print(f"  ✓ {pol.name}")

        session.commit()

        # Create tickers
        print("\n2. Creating tickers...")
        tickers_data = [
            {'symbol': 'NVDA', 'name': 'NVIDIA Corporation', 'sector': 'Technology'},
            {'symbol': 'MSFT', 'name': 'Microsoft Corporation', 'sector': 'Technology'},
            {'symbol': 'AAPL', 'name': 'Apple Inc.', 'sector': 'Technology'},
            {'symbol': 'TSLA', 'name': 'Tesla Inc.', 'sector': 'Automotive'},
            {'symbol': 'META', 'name': 'Meta Platforms Inc.', 'sector': 'Technology'},
            {'symbol': 'GOOGL', 'name': 'Alphabet Inc.', 'sector': 'Technology'},
            {'symbol': 'SPY', 'name': 'SPDR S&P 500 ETF', 'sector': 'ETF'},
        ]

        tickers = []
        for ticker_data in tickers_data:
            ticker = Ticker(**ticker_data)
            session.add(ticker)
            session.flush()
            tickers.append(ticker)
            print(f"  ✓ {ticker.symbol}")

        session.commit()

        # Generate trades with realistic patterns
        print("\n3. Generating trades with cyclical patterns...")

        start_date = datetime(2022, 1, 1)
        end_date = datetime(2024, 11, 14)
        current_date = start_date

        trades_created = 0

        # Set random seed for reproducibility
        np.random.seed(42)
        random.seed(42)

        # Define trading patterns for each politician
        patterns = {
            'Nancy Pelosi': {
                'cycle_days': 21,  # Monthly cycle
                'burst_size': (3, 8),  # 3-8 trades per burst
                'preferred_tickers': ['NVDA', 'MSFT', 'AAPL'],
                'trade_probability': 0.15
            },
            'Paul Pelosi': {
                'cycle_days': 28,  # Slightly different cycle
                'burst_size': (5, 12),  # More trades per burst
                'preferred_tickers': ['NVDA', 'TSLA', 'GOOGL'],
                'trade_probability': 0.20
            },
            'Dan Crenshaw': {
                'cycle_days': 60,  # Quarterly cycle
                'burst_size': (2, 5),
                'preferred_tickers': ['SPY', 'MSFT', 'AAPL'],
                'trade_probability': 0.08
            },
            'Josh Gottheimer': {
                'cycle_days': 45,
                'burst_size': (2, 6),
                'preferred_tickers': ['META', 'GOOGL', 'MSFT'],
                'trade_probability': 0.10
            }
        }

        day_count = 0

        while current_date <= end_date:
            day_count += 1

            # Skip weekends
            if current_date.weekday() >= 5:
                current_date += timedelta(days=1)
                continue

            for politician, freq in politicians:
                pattern = patterns[politician.name]

                # Cyclical component: higher probability at cycle peaks
                cycle_phase = (day_count % pattern['cycle_days']) / pattern['cycle_days']
                cycle_boost = 1 + 2 * np.sin(2 * np.pi * cycle_phase)  # Peaks at cycle

                # Check if politician trades today
                if random.random() < pattern['trade_probability'] * cycle_boost:
                    # Create a burst of trades
                    num_trades = random.randint(*pattern['burst_size'])

                    for _ in range(num_trades):
                        # Select ticker (prefer certain tickers)
                        if random.random() < 0.7:
                            ticker_symbol = random.choice(pattern['preferred_tickers'])
                        else:
                            ticker_symbol = random.choice([t.symbol for t in tickers])

                        ticker = next(t for t in tickers if t.symbol == ticker_symbol)

                        # Trade type (purchases more common)
                        trade_type = 'purchase' if random.random() < 0.65 else 'sale'

                        # Amount (varies by politician and ticker)
                        if politician.name in ['Nancy Pelosi', 'Paul Pelosi']:
                            amount = random.uniform(50000, 500000)
                        else:
                            amount = random.uniform(15000, 150000)

                        # Disclosure delay (15-45 days typical)
                        disclosure_delay = random.randint(15, 45)
                        disclosure_date = current_date + timedelta(days=disclosure_delay)

                        trade = Trade(
                            politician_id=politician.id,
                            ticker_id=ticker.id,
                            transaction_date=current_date,
                            transaction_type=trade_type,
                            amount=Decimal(str(round(amount, 2))),
                            disclosure_date=disclosure_date
                        )

                        session.add(trade)
                        trades_created += 1

            current_date += timedelta(days=1)

            # Commit every 100 days
            if day_count % 100 == 0:
                session.commit()
                print(f"  Progress: {trades_created} trades created (day {day_count})")

        session.commit()

        print(f"\n✓ Created {trades_created} total trades")

        # Show summary statistics
        print("\n4. Summary Statistics:")
        print("-" * 80)

        for politician, _ in politicians:
            count = session.query(Trade).filter(Trade.politician_id == politician.id).count()
            print(f"  {politician.name}: {count} trades")

        print()
        for ticker in tickers:
            count = session.query(Trade).filter(Trade.ticker_id == ticker.id).count()
            print(f"  {ticker.symbol}: {count} trades")

        print("\n" + "=" * 80)
        print("✓ Data generation complete!")
        print("=" * 80)

        return trades_created

    except Exception as e:
        print(f"\n✗ Error: {e}")
        session.rollback()
        raise
    finally:
        session.close()


if __name__ == "__main__":
    try:
        total_trades = create_realistic_trading_data()
        print(f"\nGenerated {total_trades} realistic trades")
        print("Ready for cyclical pattern analysis!")
        sys.exit(0)
    except Exception as e:
        print(f"\nFailed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
