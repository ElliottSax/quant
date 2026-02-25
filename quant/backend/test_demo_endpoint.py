#!/usr/bin/env python3
"""
Minimal test of demo backtesting endpoint
Tests without full app initialization
"""

import asyncio
import pandas as pd
import yfinance as yf
from datetime import datetime

async def test_yfinance():
    """Test Yahoo Finance data fetching"""
    print("🧪 Testing Yahoo Finance...")
    try:
        ticker = yf.Ticker("AAPL")
        df = ticker.history(start='2025-06-01', end='2025-12-31', interval='1d')

        if df.empty:
            print("❌ No data returned")
            return False

        print(f"✅ Fetched {len(df)} days of data for AAPL")
        print(f"   Date range: {df.index[0]} to {df.index[-1]}")
        print(f"   Price range: ${df['Close'].min():.2f} - ${df['Close'].max():.2f}")
        return True
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

async def test_strategies_import():
    """Test strategies module import"""
    print("\n🧪 Testing strategies import...")
    try:
        from app.services.strategies import STRATEGY_REGISTRY, get_strategy
        print(f"✅ Strategies module imported")
        print(f"   Found {len(STRATEGY_REGISTRY)} strategies")

        # Test getting a strategy
        strategy = get_strategy('ma_crossover')
        if strategy:
            print(f"✅ Successfully loaded 'ma_crossover' strategy")
            return True
        else:
            print("❌ Failed to load strategy")
            return False
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

async def test_backtesting_engine():
    """Test backtesting engine"""
    print("\n🧪 Testing backtesting engine...")
    try:
        from app.services.backtesting import BacktestEngine

        engine = BacktestEngine(initial_capital=100000)
        print(f"✅ Backtesting engine created")
        print(f"   Initial capital: ${engine.initial_capital:,.2f}")
        return True
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

async def main():
    print("=" * 60)
    print("  Demo Backtesting Endpoint Test")
    print("=" * 60)

    results = []

    # Test 1: Yahoo Finance
    results.append(await test_yfinance())

    # Test 2: Strategies
    results.append(await test_strategies_import())

    # Test 3: Backtesting Engine
    results.append(await test_backtesting_engine())

    print("\n" + "=" * 60)
    print(f"Results: {sum(results)}/{len(results)} tests passed")

    if all(results):
        print("✅ ALL TESTS PASSED - Demo endpoint should work!")
    else:
        print("❌ SOME TESTS FAILED - Fix issues before deploying")

    print("=" * 60)

    return all(results)

if __name__ == "__main__":
    success = asyncio.run(main())
    exit(0 if success else 1)
