"""Seed database with test data."""

import asyncio
from datetime import date, datetime
from decimal import Decimal

from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession

from app.core.config import settings
from app.models import Politician, Trade, Ticker
from app.core.database import Base


async def seed_data():
    """Seed the database with test data."""
    # Create async engine
    engine = create_async_engine(settings.async_database_url, echo=True)

    # Create session
    AsyncSessionLocal = async_sessionmaker(
        engine, class_=AsyncSession, expire_on_commit=False
    )

    async with AsyncSessionLocal() as session:
        print("🌱 Seeding database with test data...")

        # Create test politicians
        politicians_data = [
            {
                "name": "Nancy Pelosi",
                "chamber": "house",
                "party": "Democratic",
                "state": "CA",
                "bioguide_id": "P000197",
            },
            {
                "name": "Josh Hawley",
                "chamber": "senate",
                "party": "Republican",
                "state": "MO",
                "bioguide_id": "H001089",
            },
            {
                "name": "Ro Khanna",
                "chamber": "house",
                "party": "Democratic",
                "state": "CA",
                "bioguide_id": "K000389",
            },
            {
                "name": "Tommy Tuberville",
                "chamber": "senate",
                "party": "Republican",
                "state": "AL",
                "bioguide_id": "T000278",
            },
            {
                "name": "Marjorie Taylor Greene",
                "chamber": "house",
                "party": "Republican",
                "state": "GA",
                "bioguide_id": "G000596",
            },
        ]

        politicians = []
        for pol_data in politicians_data:
            politician = Politician(**pol_data)
            session.add(politician)
            politicians.append(politician)

        # Flush to get IDs
        await session.flush()

        print(f"✅ Created {len(politicians)} politicians")

        # Create test tickers
        tickers_data = [
            {
                "symbol": "AAPL",
                "company_name": "Apple Inc.",
                "sector": "Technology",
                "industry": "Consumer Electronics",
            },
            {
                "symbol": "MSFT",
                "company_name": "Microsoft Corporation",
                "sector": "Technology",
                "industry": "Software",
            },
            {
                "symbol": "NVDA",
                "company_name": "NVIDIA Corporation",
                "sector": "Technology",
                "industry": "Semiconductors",
            },
            {
                "symbol": "TSLA",
                "company_name": "Tesla, Inc.",
                "sector": "Consumer Cyclical",
                "industry": "Auto Manufacturers",
            },
            {
                "symbol": "AMZN",
                "company_name": "Amazon.com, Inc.",
                "sector": "Consumer Cyclical",
                "industry": "Internet Retail",
            },
        ]

        for ticker_data in tickers_data:
            ticker = Ticker(**ticker_data)
            session.add(ticker)

        print(f"✅ Created {len(tickers_data)} tickers")

        # Create test trades
        trades_data = [
            {
                "politician_id": politicians[0].id,  # Pelosi
                "ticker": "NVDA",
                "transaction_type": "buy",
                "amount_min": Decimal("1000000"),
                "amount_max": Decimal("5000000"),
                "transaction_date": date(2024, 10, 15),
                "disclosure_date": date(2024, 10, 30),
                "source_url": "https://efdsearch.senate.gov/example1",
            },
            {
                "politician_id": politicians[0].id,  # Pelosi
                "ticker": "MSFT",
                "transaction_type": "buy",
                "amount_min": Decimal("500000"),
                "amount_max": Decimal("1000000"),
                "transaction_date": date(2024, 11, 1),
                "disclosure_date": date(2024, 11, 10),
                "source_url": "https://efdsearch.senate.gov/example2",
            },
            {
                "politician_id": politicians[1].id,  # Hawley
                "ticker": "TSLA",
                "transaction_type": "sell",
                "amount_min": Decimal("100000"),
                "amount_max": Decimal("250000"),
                "transaction_date": date(2024, 10, 20),
                "disclosure_date": date(2024, 11, 5),
                "source_url": "https://efdsearch.senate.gov/example3",
            },
            {
                "politician_id": politicians[2].id,  # Khanna
                "ticker": "AAPL",
                "transaction_type": "buy",
                "amount_min": Decimal("50000"),
                "amount_max": Decimal("100000"),
                "transaction_date": date(2024, 9, 15),
                "disclosure_date": date(2024, 9, 30),
                "source_url": "https://efdsearch.senate.gov/example4",
            },
            {
                "politician_id": politicians[3].id,  # Tuberville
                "ticker": "AMZN",
                "transaction_type": "buy",
                "amount_min": Decimal("250000"),
                "amount_max": Decimal("500000"),
                "transaction_date": date(2024, 11, 5),
                "disclosure_date": date(2024, 11, 10),
                "source_url": "https://efdsearch.senate.gov/example5",
            },
            {
                "politician_id": politicians[4].id,  # Greene
                "ticker": "NVDA",
                "transaction_type": "sell",
                "amount_min": Decimal("15000"),
                "amount_max": Decimal("50000"),
                "transaction_date": date(2024, 10, 1),
                "disclosure_date": date(2024, 10, 15),
                "source_url": "https://efdsearch.senate.gov/example6",
            },
            {
                "politician_id": politicians[1].id,  # Hawley
                "ticker": "AAPL",
                "transaction_type": "buy",
                "amount_min": Decimal("100000"),
                "amount_max": Decimal("250000"),
                "transaction_date": date(2024, 11, 8),
                "disclosure_date": date(2024, 11, 10),
                "source_url": "https://efdsearch.senate.gov/example7",
            },
            {
                "politician_id": politicians[0].id,  # Pelosi
                "ticker": "TSLA",
                "transaction_type": "sell",
                "amount_min": Decimal("500000"),
                "amount_max": Decimal("1000000"),
                "transaction_date": date(2024, 11, 9),
                "disclosure_date": date(2024, 11, 10),
                "source_url": "https://efdsearch.senate.gov/example8",
            },
        ]

        for trade_data in trades_data:
            trade = Trade(**trade_data)
            session.add(trade)

        print(f"✅ Created {len(trades_data)} trades")

        # Commit all changes
        await session.commit()

        print("✨ Database seeding completed successfully!")
        print("\nSummary:")
        print(f"  • {len(politicians)} politicians")
        print(f"  • {len(tickers_data)} tickers")
        print(f"  • {len(trades_data)} trades")


if __name__ == "__main__":
    print("🚀 Starting database seeding...")
    asyncio.run(seed_data())
