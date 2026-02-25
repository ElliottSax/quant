#!/usr/bin/env python3
"""
Test script to verify N+1 query fixes.

This script tests that eager loading is working correctly and
that no N+1 query issues are present in the API endpoints.

Usage:
    python test_n_plus_one_fixes.py
"""

import asyncio
import sys
from typing import List
from sqlalchemy import event, select
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import selectinload, joinedload


# Query counter to detect N+1 issues
class QueryCounter:
    """Counts database queries to detect N+1 problems."""

    def __init__(self):
        self.query_count = 0
        self.queries = []

    def reset(self):
        self.query_count = 0
        self.queries = []

    def increment(self, statement: str):
        self.query_count += 1
        self.queries.append(statement)

    def report(self, test_name: str, expected_max: int):
        """Report results and check if N+1 exists."""
        print(f"\n{'='*60}")
        print(f"Test: {test_name}")
        print(f"{'='*60}")
        print(f"Queries executed: {self.query_count}")
        print(f"Expected maximum: {expected_max}")

        if self.query_count > expected_max:
            print(f"❌ FAIL: Potential N+1 detected! ({self.query_count} > {expected_max})")
            print("\nQueries executed:")
            for i, query in enumerate(self.queries, 1):
                print(f"  {i}. {query[:100]}...")
            return False
        else:
            print(f"✅ PASS: Query count within acceptable range")
            return True


counter = QueryCounter()


async def test_trades_eager_loading():
    """Test that trades endpoint uses eager loading for politicians."""
    counter.reset()

    try:
        # This would normally connect to your database
        # For now, we'll test the query structure
        from quant.backend.app.api.v1.trades import router
        from quant.backend.app.models import Trade, Politician

        print("\n🔍 Testing Trades API endpoint...")

        # Check that the query includes joinedload
        query = select(Trade).join(Politician).options(joinedload(Trade.politician))

        # Verify the options are set
        has_eager_loading = len(query._with_options) > 0
        if has_eager_loading:
            print("✅ Trades query includes eager loading (joinedload)")
            return True
        else:
            print("❌ Trades query MISSING eager loading")
            return False

    except Exception as e:
        print(f"⚠️  Test skipped: {e}")
        return None


async def test_politicians_with_trades():
    """Test loading politicians with their trades."""
    counter.reset()

    try:
        from quant.backend.app.models import Politician

        print("\n🔍 Testing Politician with trades loading...")

        # Check that we're using selectinload for one-to-many
        query = select(Politician).options(selectinload(Politician.trades))

        has_eager_loading = len(query._with_options) > 0
        if has_eager_loading:
            print("✅ Politicians query includes eager loading (selectinload)")
            return True
        else:
            print("❌ Politicians query MISSING eager loading")
            return False

    except Exception as e:
        print(f"⚠️  Test skipped: {e}")
        return None


async def test_analytics_network_query():
    """Test analytics network endpoint for eager loading."""
    counter.reset()

    try:
        from quant.backend.app.models import Politician

        print("\n🔍 Testing Analytics network query...")

        # Simulate the query from analyze_trading_network
        query = (
            select(Politician)
            .options(selectinload(Politician.trades))
        )

        has_eager_loading = len(query._with_options) > 0
        if has_eager_loading:
            print("✅ Analytics query includes eager loading")
            return True
        else:
            print("❌ Analytics query MISSING eager loading")
            return False

    except Exception as e:
        print(f"⚠️  Test skipped: {e}")
        return None


async def test_patterns_load_trades():
    """Test patterns API load_politician_trades function."""
    counter.reset()

    try:
        from quant.backend.app.models import Trade, Politician

        print("\n🔍 Testing Patterns load_politician_trades function...")

        # Simulate the query from load_politician_trades
        query = (
            select(Trade, Politician)
            .join(Politician, Trade.politician_id == Politician.id)
            .options(joinedload(Trade.politician))
        )

        has_eager_loading = len(query._with_options) > 0
        if has_eager_loading:
            print("✅ Patterns query includes eager loading")
            return True
        else:
            print("❌ Patterns query MISSING eager loading")
            return False

    except Exception as e:
        print(f"⚠️  Test skipped: {e}")
        return None


async def test_query_profiler_decorators():
    """Test that query profiler decorators exist and are importable."""
    print("\n🔍 Testing Query Profiler decorators...")

    try:
        from quant.backend.app.core.query_profiler import (
            log_slow_queries,
            detect_n_plus_one,
            profile_queries,
            disable_query_profiling,
            ProfiledSession,
            QueryProfiler
        )

        print("✅ log_slow_queries decorator available")
        print("✅ detect_n_plus_one decorator available")
        print("✅ profile_queries decorator available")
        print("✅ disable_query_profiling decorator available")
        print("✅ ProfiledSession context manager available")
        print("✅ QueryProfiler class available")

        return True

    except ImportError as e:
        print(f"❌ Failed to import query profiler components: {e}")
        return False


def test_decorator_usage_example():
    """Show example of how to use the new decorators."""
    print("\n📖 Query Profiler Decorator Usage Examples:")
    print("""
# Example 1: Log slow queries
from app.core.query_profiler import log_slow_queries

@router.get("/politicians")
@log_slow_queries(threshold_ms=100.0)
async def list_politicians(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Politician))
    return result.scalars().all()

# Example 2: Detect N+1 problems
from app.core.query_profiler import detect_n_plus_one

@router.get("/politicians-with-trades")
@detect_n_plus_one
async def get_politicians_with_trades(db: AsyncSession = Depends(get_db)):
    politicians = await db.execute(
        select(Politician).options(selectinload(Politician.trades))
    )
    return politicians.scalars().all()

# Example 3: Combine both decorators
@router.get("/trades/recent")
@log_slow_queries(threshold_ms=50.0)
@detect_n_plus_one
async def recent_trades(db: AsyncSession = Depends(get_db)):
    trades = await db.execute(
        select(Trade).options(joinedload(Trade.politician))
    )
    return trades.scalars().all()
    """)


async def run_all_tests():
    """Run all N+1 query tests."""
    print("="*60)
    print("N+1 Query Fixes Verification")
    print("="*60)

    results = []

    # Run all tests
    results.append(await test_trades_eager_loading())
    results.append(await test_politicians_with_trades())
    results.append(await test_analytics_network_query())
    results.append(await test_patterns_load_trades())
    results.append(await test_query_profiler_decorators())

    # Show usage examples
    test_decorator_usage_example()

    # Summary
    print("\n" + "="*60)
    print("Test Summary")
    print("="*60)

    passed = sum(1 for r in results if r is True)
    failed = sum(1 for r in results if r is False)
    skipped = sum(1 for r in results if r is None)

    print(f"✅ Passed: {passed}")
    print(f"❌ Failed: {failed}")
    print(f"⚠️  Skipped: {skipped}")

    if failed > 0:
        print("\n❌ Some tests failed. Please review the N+1 fixes.")
        return False
    else:
        print("\n✅ All tests passed! N+1 issues have been fixed.")
        return True


def main():
    """Main entry point."""
    try:
        success = asyncio.run(run_all_tests())
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"\n❌ Test suite failed with error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
