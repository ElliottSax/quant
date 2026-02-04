#!/usr/bin/env python3
"""
Seed database with real Congressional trading data from public sources.

Data sources:
- House Stock Watcher API (https://housestockwatcher.com)
- Senate Stock Watcher API (https://senatestockwatcher.com)
"""

import asyncio
import httpx
import os
import sys
from datetime import datetime, date
from decimal import Decimal
from typing import List, Dict, Any, Optional
import uuid

# Add app to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Set environment for development
os.environ.setdefault("DATABASE_URL", "sqlite+aiosqlite:///./quant_dev.db")
os.environ.setdefault("SECRET_KEY", "dev-local-development-key-min-32-chars-required")
os.environ.setdefault("ENVIRONMENT", "development")
os.environ.setdefault("REDIS_ENABLED", "false")

from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.orm import declarative_base
from sqlalchemy import select, text

# Import models after env is set
from app.core.database import Base, engine, AsyncSessionLocal
from app.models.politician import Politician
from app.models.trade import Trade


# API endpoints
HOUSE_API = "https://house-stock-watcher-data.s3-us-west-2.amazonaws.com/data/all_transactions.json"
SENATE_API = "https://senate-stock-watcher-data.s3-us-west-2.amazonaws.com/aggregate/all_transactions.json"

# Amount range mapping from disclosure categories
AMOUNT_RANGES = {
    "$1,001 - $15,000": (1001, 15000),
    "$15,001 - $50,000": (15001, 50000),
    "$50,001 - $100,000": (50001, 100000),
    "$100,001 - $250,000": (100001, 250000),
    "$250,001 - $500,000": (250001, 500000),
    "$500,001 - $1,000,000": (500001, 1000000),
    "$1,000,001 - $5,000,000": (1000001, 5000000),
    "$5,000,001 - $25,000,000": (5000001, 25000000),
    "$25,000,001 - $50,000,000": (25000001, 50000000),
    "Over $50,000,000": (50000001, 100000000),
    # Senate format
    "$1,001 -": (1001, 15000),
    "$15,001 -": (15001, 50000),
    "$50,001 -": (50001, 100000),
    "$100,001 -": (100001, 250000),
    "$250,001 -": (250001, 500000),
    "$500,001 -": (500001, 1000000),
    "$1,000,001 -": (1000001, 5000000),
}


def parse_amount(amount_str: str) -> tuple[Optional[Decimal], Optional[Decimal]]:
    """Parse amount string to min/max decimals."""
    if not amount_str:
        return None, None

    amount_str = amount_str.strip()

    # Try exact match first
    if amount_str in AMOUNT_RANGES:
        min_val, max_val = AMOUNT_RANGES[amount_str]
        return Decimal(str(min_val)), Decimal(str(max_val))

    # Try partial match
    for key, (min_val, max_val) in AMOUNT_RANGES.items():
        if key.startswith(amount_str.split(" -")[0]):
            return Decimal(str(min_val)), Decimal(str(max_val))

    return None, None


def parse_date(date_str: str) -> Optional[date]:
    """Parse date string to date object."""
    if not date_str:
        return None

    formats = [
        "%Y-%m-%d",
        "%m/%d/%Y",
        "%Y/%m/%d",
    ]

    for fmt in formats:
        try:
            return datetime.strptime(date_str, fmt).date()
        except ValueError:
            continue

    return None


async def fetch_house_data() -> List[Dict[str, Any]]:
    """Fetch House trading data."""
    print("Fetching House trading data...")
    async with httpx.AsyncClient(timeout=60.0) as client:
        try:
            response = await client.get(HOUSE_API)
            response.raise_for_status()
            data = response.json()
            print(f"  Fetched {len(data)} House transactions")
            return data
        except Exception as e:
            print(f"  Error fetching House data: {e}")
            return []


async def fetch_senate_data() -> List[Dict[str, Any]]:
    """Fetch Senate trading data."""
    print("Fetching Senate trading data...")
    async with httpx.AsyncClient(timeout=60.0) as client:
        try:
            response = await client.get(SENATE_API)
            response.raise_for_status()
            data = response.json()
            print(f"  Fetched {len(data)} Senate transactions")
            return data
        except Exception as e:
            print(f"  Error fetching Senate data: {e}")
            return []


async def seed_data():
    """Seed database with real Congressional trading data."""
    print("\n" + "="*60)
    print("SEEDING REAL CONGRESSIONAL TRADING DATA")
    print("="*60 + "\n")

    # Initialize database tables
    print("Initializing database tables...")
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    print("  Database tables created\n")

    # Fetch data from APIs
    house_data = await fetch_house_data()
    senate_data = await fetch_senate_data()

    if not house_data and not senate_data:
        print("No data fetched. Creating sample data instead...")
        await seed_sample_data()
        return

    async with AsyncSessionLocal() as session:
        # Process and insert data
        politicians_cache: Dict[str, Politician] = {}
        trades_added = 0
        politicians_added = 0

        print("\nProcessing House transactions...")
        for i, tx in enumerate(house_data[:1000]):  # Limit to 1000 for demo
            try:
                name = tx.get("representative", "").strip()
                if not name:
                    continue

                # Get or create politician
                if name not in politicians_cache:
                    # Check if exists in DB
                    result = await session.execute(
                        select(Politician).where(Politician.name == name)
                    )
                    politician = result.scalar_one_or_none()

                    if not politician:
                        politician = Politician(
                            name=name,
                            chamber="house",
                            party=tx.get("party", "Unknown")[:20] if tx.get("party") else None,
                            state=tx.get("state", "")[:2] if tx.get("state") else None,
                        )
                        session.add(politician)
                        await session.flush()
                        politicians_added += 1

                    politicians_cache[name] = politician

                politician = politicians_cache[name]

                # Parse trade data
                ticker = tx.get("ticker", "").upper()[:10]
                if not ticker or ticker == "--":
                    continue

                tx_type_raw = tx.get("type", "").lower()
                tx_type = "buy" if "purchase" in tx_type_raw or "buy" in tx_type_raw else "sell"

                tx_date = parse_date(tx.get("transaction_date"))
                disc_date = parse_date(tx.get("disclosure_date"))

                if not tx_date:
                    continue
                if not disc_date:
                    disc_date = tx_date

                amount_min, amount_max = parse_amount(tx.get("amount", ""))

                # Create trade
                trade = Trade(
                    politician_id=politician.id,
                    ticker=ticker,
                    transaction_type=tx_type,
                    amount_min=amount_min,
                    amount_max=amount_max,
                    transaction_date=tx_date,
                    disclosure_date=disc_date,
                    source_url=tx.get("ptr_link"),
                    raw_data=tx,
                )
                session.add(trade)
                trades_added += 1

                if (i + 1) % 100 == 0:
                    print(f"  Processed {i + 1} House transactions...")
                    await session.commit()

            except Exception as e:
                print(f"  Error processing House transaction: {e}")
                continue

        print(f"\nProcessing Senate transactions...")
        for i, tx in enumerate(senate_data[:500]):  # Limit to 500 for demo
            try:
                name = tx.get("senator", "") or tx.get("first_name", "") + " " + tx.get("last_name", "")
                name = name.strip()
                if not name:
                    continue

                # Get or create politician
                if name not in politicians_cache:
                    result = await session.execute(
                        select(Politician).where(Politician.name == name)
                    )
                    politician = result.scalar_one_or_none()

                    if not politician:
                        politician = Politician(
                            name=name,
                            chamber="senate",
                            party=tx.get("party", "Unknown")[:20] if tx.get("party") else None,
                            state=tx.get("state", "")[:2] if tx.get("state") else None,
                        )
                        session.add(politician)
                        await session.flush()
                        politicians_added += 1

                    politicians_cache[name] = politician

                politician = politicians_cache[name]

                # Parse trade data
                ticker = tx.get("ticker", "").upper()[:10]
                if not ticker or ticker == "--" or ticker == "N/A":
                    continue

                tx_type_raw = tx.get("type", "").lower()
                tx_type = "buy" if "purchase" in tx_type_raw or "buy" in tx_type_raw else "sell"

                tx_date = parse_date(tx.get("transaction_date"))
                disc_date = parse_date(tx.get("disclosure_date"))

                if not tx_date:
                    continue
                if not disc_date:
                    disc_date = tx_date

                amount_min, amount_max = parse_amount(tx.get("amount", ""))

                trade = Trade(
                    politician_id=politician.id,
                    ticker=ticker,
                    transaction_type=tx_type,
                    amount_min=amount_min,
                    amount_max=amount_max,
                    transaction_date=tx_date,
                    disclosure_date=disc_date,
                    source_url=tx.get("ptr_link"),
                    raw_data=tx,
                )
                session.add(trade)
                trades_added += 1

                if (i + 1) % 100 == 0:
                    print(f"  Processed {i + 1} Senate transactions...")
                    await session.commit()

            except Exception as e:
                print(f"  Error processing Senate transaction: {e}")
                continue

        await session.commit()

        print("\n" + "="*60)
        print("SEEDING COMPLETE")
        print("="*60)
        print(f"  Politicians added: {politicians_added}")
        print(f"  Total politicians: {len(politicians_cache)}")
        print(f"  Trades added: {trades_added}")
        print("="*60 + "\n")


async def seed_sample_data():
    """Seed sample data if API fetch fails."""
    print("Seeding sample Congressional trading data...")

    # Sample politicians with realistic data
    sample_politicians = [
        {"name": "Nancy Pelosi", "chamber": "house", "party": "Democratic", "state": "CA"},
        {"name": "Dan Crenshaw", "chamber": "house", "party": "Republican", "state": "TX"},
        {"name": "Tommy Tuberville", "chamber": "senate", "party": "Republican", "state": "AL"},
        {"name": "Josh Gottheimer", "chamber": "house", "party": "Democratic", "state": "NJ"},
        {"name": "Pat Fallon", "chamber": "house", "party": "Republican", "state": "TX"},
        {"name": "Mark Green", "chamber": "house", "party": "Republican", "state": "TN"},
        {"name": "Ro Khanna", "chamber": "house", "party": "Democratic", "state": "CA"},
        {"name": "Michael McCaul", "chamber": "house", "party": "Republican", "state": "TX"},
        {"name": "Debbie Wasserman Schultz", "chamber": "house", "party": "Democratic", "state": "FL"},
        {"name": "Marjorie Taylor Greene", "chamber": "house", "party": "Republican", "state": "GA"},
        {"name": "Alexandria Ocasio-Cortez", "chamber": "house", "party": "Democratic", "state": "NY"},
        {"name": "Ted Cruz", "chamber": "senate", "party": "Republican", "state": "TX"},
        {"name": "Elizabeth Warren", "chamber": "senate", "party": "Democratic", "state": "MA"},
        {"name": "Marco Rubio", "chamber": "senate", "party": "Republican", "state": "FL"},
        {"name": "Bernie Sanders", "chamber": "senate", "party": "Independent", "state": "VT"},
    ]

    # Sample trades with proper min/max ranges
    sample_tickers = ["NVDA", "AAPL", "MSFT", "GOOGL", "AMZN", "META", "TSLA", "AMD", "CRM", "AVGO",
                      "JPM", "BAC", "XOM", "CVX", "UNH", "JNJ", "PFE", "LMT", "BA", "RTX"]

    # Amount ranges that satisfy min <= max constraint
    amount_ranges = [
        (1001, 15000),
        (15001, 50000),
        (50001, 100000),
        (100001, 250000),
        (250001, 500000),
        (500001, 1000000),
    ]

    async with AsyncSessionLocal() as session:
        from random import choice, randint
        from datetime import timedelta

        politicians_added = 0
        trades_added = 0

        for pol_data in sample_politicians:
            politician = Politician(**pol_data)
            session.add(politician)
            await session.flush()
            politicians_added += 1

            # Add trades for each politician
            num_trades = randint(30, 80)
            for _ in range(num_trades):
                tx_date = date.today() - timedelta(days=randint(1, 730))  # Last 2 years
                amount_range = choice(amount_ranges)
                trade = Trade(
                    politician_id=politician.id,
                    ticker=choice(sample_tickers),
                    transaction_type=choice(["buy", "sell"]),
                    amount_min=Decimal(str(amount_range[0])),
                    amount_max=Decimal(str(amount_range[1])),
                    transaction_date=tx_date,
                    disclosure_date=tx_date + timedelta(days=randint(1, 45)),
                )
                session.add(trade)
                trades_added += 1

        await session.commit()

        print("\n" + "="*60)
        print("SEEDING COMPLETE")
        print("="*60)
        print(f"  Politicians added: {politicians_added}")
        print(f"  Trades added: {trades_added}")
        print("="*60 + "\n")


if __name__ == "__main__":
    asyncio.run(seed_data())
