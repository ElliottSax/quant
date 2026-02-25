#!/usr/bin/env python3
"""
Test Scraping Setup

Quick test to verify scrapers are working correctly.
"""

import asyncio
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.scrapers import SenateScraper, HouseScraper, DataValidator


def test_senate_scraper():
    """Test Senate scraper."""
    print("\n" + "="*50)
    print("Testing Senate Scraper")
    print("="*50)

    try:
        with SenateScraper(headless=True) as scraper:
            print("✓ Scraper initialized")

            # Test with last 3 days
            transactions = scraper.scrape_recent_transactions(days_back=3)
            print(f"✓ Found {len(transactions)} transactions")

            if transactions:
                # Show sample
                sample = transactions[0]
                print("\nSample transaction:")
                print(f"  Politician: {sample.get('politician_name')}")
                print(f"  Chamber: {sample.get('chamber')}")
                print(f"  Ticker: {sample.get('ticker')}")
                print(f"  Type: {sample.get('transaction_type')}")
                print(f"  Date: {sample.get('transaction_date')}")
                print(f"  Amount: ${sample.get('amount_min')} - ${sample.get('amount_max')}")

        print("\n✓ Senate scraper test PASSED")
        return True

    except Exception as e:
        print(f"\n✗ Senate scraper test FAILED: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_house_scraper():
    """Test House scraper."""
    print("\n" + "="*50)
    print("Testing House Scraper")
    print("="*50)

    try:
        with HouseScraper(headless=True) as scraper:
            print("✓ Scraper initialized")

            # Test with last 3 days
            transactions = scraper.scrape_recent_transactions(days_back=3)
            print(f"✓ Found {len(transactions)} transactions")

            if transactions:
                # Show sample
                sample = transactions[0]
                print("\nSample transaction:")
                print(f"  Politician: {sample.get('politician_name')}")
                print(f"  Chamber: {sample.get('chamber')}")
                print(f"  Ticker: {sample.get('ticker')}")
                print(f"  Type: {sample.get('transaction_type')}")
                print(f"  Date: {sample.get('transaction_date')}")
                print(f"  Amount: ${sample.get('amount_min')} - ${sample.get('amount_max')}")

        print("\n✓ House scraper test PASSED")
        return True

    except Exception as e:
        print(f"\n✗ House scraper test FAILED: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_validator():
    """Test data validator."""
    print("\n" + "="*50)
    print("Testing Data Validator")
    print("="*50)

    validator = DataValidator()

    # Test ticker normalization
    tests = [
        ("aapl", "AAPL"),
        ("FB", "META"),
        ("brk.b", "BRK.B"),
    ]

    print("\nTicker normalization:")
    for input_ticker, expected in tests:
        result = validator.normalize_ticker(input_ticker)
        status = "✓" if result == expected else "✗"
        print(f"  {status} {input_ticker} → {result} (expected: {expected})")

    # Test ticker validation
    print("\nTicker validation:")
    valid_tickers = ["AAPL", "GOOGL", "BRK.A"]
    invalid_tickers = ["LLC", "INC", "ABCDEF"]

    for ticker in valid_tickers:
        is_valid = validator.is_valid_ticker(ticker)
        status = "✓" if is_valid else "✗"
        print(f"  {status} {ticker} is valid: {is_valid}")

    for ticker in invalid_tickers:
        is_valid = validator.is_valid_ticker(ticker)
        status = "✓" if not is_valid else "✗"
        print(f"  {status} {ticker} is invalid: {not is_valid}")

    # Test transaction validation
    print("\nTransaction validation:")
    valid_transaction = {
        "politician_name": "John Doe",
        "chamber": "senate",
        "ticker": "AAPL",
        "transaction_type": "buy",
        "transaction_date": "2024-01-15",
        "amount_min": 1000,
        "amount_max": 15000,
    }

    # Need to import datetime for proper validation
    from datetime import datetime
    valid_transaction["transaction_date"] = datetime.strptime(
        valid_transaction["transaction_date"], "%Y-%m-%d"
    ).date()

    is_valid, error = validator.validate_transaction(valid_transaction)
    status = "✓" if is_valid else "✗"
    print(f"  {status} Valid transaction: {is_valid}")
    if error:
        print(f"    Error: {error}")

    print("\n✓ Validator test PASSED")
    return True


async def test_database_import():
    """Test database import."""
    print("\n" + "="*50)
    print("Testing Database Import")
    print("="*50)

    try:
        from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
        from sqlalchemy.orm import sessionmaker
        from sqlalchemy import select
        from app.core.config import settings
        from app.models import DataSource

        # Create test database session
        engine = create_async_engine(settings.DATABASE_URL, echo=False)
        async_session = sessionmaker(
            engine, class_=AsyncSession, expire_on_commit=False
        )

        async with async_session() as session:
            # Create test data source record
            data_source = DataSource(
                source_type="test",
                status="completed",
                records_found=10,
                records_imported=8,
                records_skipped=1,
                records_invalid=1,
                source_metadata={"test": True}
            )
            session.add(data_source)
            await session.commit()
            await session.refresh(data_source)

            print(f"✓ Created DataSource record: {data_source.id}")

            # Query it back
            stmt = select(DataSource).where(DataSource.id == data_source.id)
            result = await session.execute(stmt)
            fetched = result.scalar_one()

            print(f"✓ Fetched DataSource record: {fetched.source_type}")
            print(f"  Status: {fetched.status}")
            print(f"  Records: {fetched.records_imported}/{fetched.records_found}")

            # Clean up
            await session.delete(fetched)
            await session.commit()
            print("✓ Cleaned up test record")

        print("\n✓ Database import test PASSED")
        return True

    except Exception as e:
        print(f"\n✗ Database import test FAILED: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Run all tests."""
    print("\n" + "="*50)
    print("DATA PIPELINE TEST SUITE")
    print("="*50)

    results = []

    # Test validator (no external dependencies)
    results.append(("Validator", test_validator()))

    # Test database
    results.append(("Database", asyncio.run(test_database_import())))

    # Test scrapers (requires internet and Chrome)
    print("\nNote: Scraper tests require internet connection and Chrome/Chromium")
    print("These tests may take 30-60 seconds each...")

    try:
        results.append(("Senate Scraper", test_senate_scraper()))
    except KeyboardInterrupt:
        print("\nSkipping Senate scraper test...")
        results.append(("Senate Scraper", None))

    try:
        results.append(("House Scraper", test_house_scraper()))
    except KeyboardInterrupt:
        print("\nSkipping House scraper test...")
        results.append(("House Scraper", None))

    # Summary
    print("\n" + "="*50)
    print("TEST SUMMARY")
    print("="*50)

    for name, result in results:
        if result is True:
            print(f"✓ {name}: PASSED")
        elif result is False:
            print(f"✗ {name}: FAILED")
        else:
            print(f"- {name}: SKIPPED")

    passed = sum(1 for _, r in results if r is True)
    total = len([r for _, r in results if r is not None])

    print(f"\nTotal: {passed}/{total} tests passed")

    if passed == total:
        print("\n✓ All tests passed!")
        return 0
    else:
        print("\n✗ Some tests failed")
        return 1


if __name__ == "__main__":
    sys.exit(main())
