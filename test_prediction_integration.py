#!/usr/bin/env python3
"""
Quick test script to verify prediction API integration.

Usage:
    python test_prediction_integration.py
"""

import asyncio
import sys
from pathlib import Path

# Add backend to path
backend_path = Path(__file__).parent / "quant" / "backend"
sys.path.insert(0, str(backend_path))


async def test_import():
    """Test that all prediction modules can be imported."""
    print("Testing imports...")

    try:
        # Test service imports
        from app.services.market_data import MarketDataClient
        print("✓ MarketDataClient imported")

        from app.services.technical_analysis import IndicatorCalculator, PatternDetector
        print("✓ IndicatorCalculator imported")
        print("✓ PatternDetector imported")

        # Test API import
        from app.api.v1 import prediction
        print("✓ Prediction API imported")

        # Test dependencies
        from app.core.deps import get_redis_client
        print("✓ get_redis_client dependency imported")

        print("\n✅ All imports successful!")
        return True

    except ImportError as e:
        print(f"\n❌ Import failed: {e}")
        print("\nMissing dependencies? Run:")
        print("  pip install yfinance alpha_vantage twelvedata finnhub-python pandas-ta")
        return False


async def test_basic_functionality():
    """Test basic functionality without API keys."""
    print("\nTesting basic functionality...")

    try:
        from app.services.market_data import MarketDataClient
        from app.services.technical_analysis import IndicatorCalculator

        # Test market data client (using yfinance, no API key needed)
        print("\n1. Testing MarketDataClient...")
        client = MarketDataClient()
        df = await client.get_historical_data("AAPL", period="1mo", interval="1d")
        print(f"   ✓ Fetched {len(df)} days of AAPL data")
        await client.close()

        # Test indicator calculator
        print("\n2. Testing IndicatorCalculator...")
        calc = IndicatorCalculator()
        indicators = calc.calculate_all(df)
        print(f"   ✓ Calculated indicators")
        print(f"   - RSI: {indicators['current'].get('rsi', 'N/A'):.2f}" if indicators['current'].get('rsi') else "   - RSI: N/A")
        print(f"   - Signal: {indicators['signals'].get('overall', 'N/A')}")

        print("\n✅ Basic functionality test passed!")
        return True

    except Exception as e:
        print(f"\n❌ Functionality test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


async def test_api_endpoints():
    """Test that API endpoints are registered."""
    print("\nTesting API endpoint registration...")

    try:
        from app.api.v1 import api_router

        # Get all routes
        routes = []
        for route in api_router.routes:
            if hasattr(route, 'path'):
                routes.append(route.path)

        # Check for prediction endpoints
        prediction_routes = [r for r in routes if '/prediction' in r]

        if prediction_routes:
            print(f"✓ Found {len(prediction_routes)} prediction routes:")
            for route in prediction_routes[:5]:  # Show first 5
                print(f"  - {route}")
            if len(prediction_routes) > 5:
                print(f"  ... and {len(prediction_routes) - 5} more")
            print("\n✅ API endpoints registered successfully!")
            return True
        else:
            print("❌ No prediction routes found in API router")
            print("Routes found:", routes[:10])
            return False

    except Exception as e:
        print(f"\n❌ API endpoint test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


async def main():
    """Run all tests."""
    print("=" * 60)
    print("Stock Prediction Integration Test")
    print("=" * 60)

    results = []

    # Test 1: Imports
    results.append(await test_import())

    if results[0]:
        # Test 2: Basic functionality (only if imports work)
        results.append(await test_basic_functionality())

        # Test 3: API endpoints
        results.append(await test_api_endpoints())

    print("\n" + "=" * 60)
    print("Test Summary")
    print("=" * 60)
    print(f"Imports: {'✅ PASS' if results[0] else '❌ FAIL'}")
    if len(results) > 1:
        print(f"Functionality: {'✅ PASS' if results[1] else '❌ FAIL'}")
    if len(results) > 2:
        print(f"API Endpoints: {'✅ PASS' if results[2] else '❌ FAIL'}")

    all_passed = all(results)
    print("\n" + ("✅ ALL TESTS PASSED!" if all_passed else "❌ SOME TESTS FAILED"))

    if all_passed:
        print("\n🚀 Ready to start the server!")
        print("Run: uvicorn app.main:app --reload")
        print("Docs: http://localhost:8000/api/v1/docs")

    return 0 if all_passed else 1


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
