#!/usr/bin/env python3
"""
Authenticated Stock Prediction Demo

Demonstrates using the secured prediction endpoints with:
- JWT authentication
- Rate limiting awareness
- Proper resource management (context managers)
- Error handling

Requirements:
- Running backend server
- Valid user account
"""

import asyncio
import httpx
from datetime import datetime
from typing import Optional


class AuthenticatedPredictionClient:
    """Client for authenticated prediction API calls."""

    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
        self.api_v1 = f"{base_url}/api/v1"
        self.token: Optional[str] = None

    async def login(self, email: str, password: str) -> bool:
        """
        Authenticate and obtain access token.

        Args:
            email: User email
            password: User password

        Returns:
            True if login successful
        """
        async with httpx.AsyncClient() as client:
            try:
                response = await client.post(
                    f"{self.api_v1}/auth/login",
                    json={"username": email, "password": password}
                )

                if response.status_code == 200:
                    data = response.json()
                    self.token = data.get("access_token")
                    print(f"✅ Login successful! Token obtained.")
                    return True
                else:
                    print(f"❌ Login failed: {response.status_code}")
                    print(f"   Response: {response.text}")
                    return False

            except Exception as e:
                print(f"❌ Login error: {e}")
                return False

    def _get_headers(self) -> dict:
        """Get headers with auth token."""
        if not self.token:
            raise ValueError("Not authenticated. Call login() first.")
        return {
            "Authorization": f"Bearer {self.token}",
            "Content-Type": "application/json"
        }

    async def get_indicators(self, symbol: str, period: str = "1y") -> dict:
        """
        Get technical indicators for a symbol.

        Args:
            symbol: Stock ticker (e.g., "AAPL")
            period: Time period (e.g., "1y", "3mo")

        Returns:
            Indicator data
        """
        async with httpx.AsyncClient() as client:
            try:
                response = await client.post(
                    f"{self.api_v1}/prediction/indicators",
                    headers=self._get_headers(),
                    json={"symbol": symbol, "period": period}
                )

                if response.status_code == 200:
                    return response.json()
                elif response.status_code == 429:
                    retry_after = response.headers.get("Retry-After", "60")
                    print(f"⚠️  Rate limit exceeded. Retry after {retry_after}s")
                    return {"error": "rate_limit", "retry_after": retry_after}
                elif response.status_code == 401:
                    print("❌ Authentication failed. Token may be expired.")
                    return {"error": "authentication"}
                else:
                    print(f"❌ Request failed: {response.status_code}")
                    print(f"   Response: {response.text}")
                    return {"error": response.status_code}

            except Exception as e:
                print(f"❌ Request error: {e}")
                return {"error": str(e)}

    async def get_prediction(
        self,
        symbol: str,
        period: str = "1y",
        horizon: int = 5
    ) -> dict:
        """
        Get ML prediction for a symbol.

        Args:
            symbol: Stock ticker
            period: Historical period
            horizon: Prediction horizon in days

        Returns:
            Prediction data
        """
        async with httpx.AsyncClient() as client:
            try:
                response = await client.post(
                    f"{self.api_v1}/prediction/predict",
                    headers=self._get_headers(),
                    json={
                        "symbol": symbol,
                        "period": period,
                        "horizon": horizon
                    }
                )

                if response.status_code == 200:
                    return response.json()
                elif response.status_code == 429:
                    retry_after = response.headers.get("Retry-After", "60")
                    print(f"⚠️  Rate limit exceeded. Retry after {retry_after}s")
                    return {"error": "rate_limit", "retry_after": retry_after}
                else:
                    print(f"❌ Request failed: {response.status_code}")
                    return {"error": response.status_code}

            except Exception as e:
                print(f"❌ Request error: {e}")
                return {"error": str(e)}

    async def scan_patterns(self, symbols: list[str]) -> dict:
        """
        Scan multiple symbols for candlestick patterns.

        Args:
            symbols: List of stock tickers (max 50)

        Returns:
            Pattern data
        """
        async with httpx.AsyncClient(timeout=60.0) as client:
            try:
                response = await client.post(
                    f"{self.api_v1}/prediction/patterns/scan",
                    headers=self._get_headers(),
                    json={"symbols": symbols[:50]}  # Limit to 50
                )

                if response.status_code == 200:
                    return response.json()
                elif response.status_code == 429:
                    print("⚠️  Rate limit exceeded")
                    return {"error": "rate_limit"}
                else:
                    print(f"❌ Request failed: {response.status_code}")
                    return {"error": response.status_code}

            except Exception as e:
                print(f"❌ Request error: {e}")
                return {"error": str(e)}


async def demo():
    """Run authenticated prediction demo."""
    print("=" * 60)
    print("Authenticated Stock Prediction Demo")
    print("=" * 60)
    print()

    # Initialize client
    client = AuthenticatedPredictionClient()

    # Login (use environment variables in production)
    print("🔐 Step 1: Authentication")
    print("-" * 60)

    # For demo purposes - replace with your credentials
    email = input("Email: ").strip()
    if not email:
        email = "test@example.com"

    password = input("Password: ").strip()
    if not password:
        password = "password123"

    success = await client.login(email, password)

    if not success:
        print()
        print("❌ Demo failed: Could not authenticate")
        print()
        print("Make sure:")
        print("  1. Backend server is running (uvicorn app.main:app --reload)")
        print("  2. User account exists")
        print("  3. Credentials are correct")
        return

    print()

    # Test 1: Get Indicators
    print("📊 Step 2: Get Technical Indicators")
    print("-" * 60)
    symbol = "AAPL"
    print(f"Fetching indicators for {symbol}...")

    indicators = await client.get_indicators(symbol)

    if "error" not in indicators:
        print(f"✅ Success! Retrieved indicators for {symbol}")
        print()
        print("Current Indicators:")
        current = indicators.get("indicators", {})
        if current:
            print(f"  RSI:        {current.get('rsi', 'N/A'):.2f}")
            print(f"  MACD:       {current.get('macd', 'N/A'):.2f}")
            print(f"  SMA 20:     ${current.get('sma_20', 'N/A'):.2f}")
            print(f"  SMA 50:     ${current.get('sma_50', 'N/A'):.2f}")

        print()
        print("Trading Signals:")
        signals = indicators.get("signals", {})
        if signals:
            overall = signals.get("overall", "N/A")
            print(f"  Overall:    {overall}")
            print(f"  RSI:        {signals.get('rsi', 'N/A')}")
            print(f"  MACD:       {signals.get('macd', 'N/A')}")
            print(f"  MA Cross:   {signals.get('ma', 'N/A')}")
    else:
        print(f"❌ Failed to get indicators: {indicators.get('error')}")

    print()

    # Test 2: Get Prediction
    print("🎯 Step 3: Get ML Prediction")
    print("-" * 60)
    print(f"Generating prediction for {symbol}...")

    prediction = await client.get_prediction(symbol, horizon=5)

    if "error" not in prediction:
        print(f"✅ Success! Prediction generated for {symbol}")
        print()
        print(f"Current Price:        ${prediction.get('current_price', 0):.2f}")
        print(f"Predicted Direction:  {prediction.get('predicted_direction', 'N/A')}")
        print(f"Confidence:           {prediction.get('confidence', 0):.1%}")
        print(f"Recommendation:       {prediction.get('recommendation', 'N/A')}")
        print()

        predicted_prices = prediction.get('predicted_prices', [])
        if predicted_prices:
            print("5-Day Forecast:")
            for day, price in enumerate(predicted_prices, 1):
                print(f"  Day {day}: ${price:.2f}")
    else:
        print(f"❌ Failed to get prediction: {prediction.get('error')}")

    print()

    # Test 3: Pattern Scanning
    print("🔍 Step 4: Scan for Candlestick Patterns")
    print("-" * 60)
    scan_symbols = ["AAPL", "TSLA", "GOOGL", "MSFT", "AMZN"]
    print(f"Scanning {len(scan_symbols)} symbols for patterns...")

    patterns = await client.scan_patterns(scan_symbols)

    if "error" not in patterns:
        total = patterns.get("total_patterns_found", 0)
        print(f"✅ Success! Found {total} patterns")
        print()

        results = patterns.get("results", {})
        for sym, pattern_list in results.items():
            if pattern_list:
                print(f"{sym}:")
                for pattern in pattern_list[:3]:  # Show first 3
                    print(f"  • {pattern.get('name', 'N/A')} ({pattern.get('direction', 'N/A')})")
    else:
        print(f"❌ Failed to scan patterns: {patterns.get('error')}")

    print()

    # Summary
    print("=" * 60)
    print("✅ Demo Complete!")
    print("=" * 60)
    print()
    print("📝 Notes:")
    print("  • All endpoints require authentication")
    print("  • Rate limits enforced (20/min for free tier)")
    print("  • Input validation prevents invalid symbols")
    print("  • Resource cleanup handled automatically")
    print()
    print("🔗 API Documentation:")
    print("  http://localhost:8000/api/v1/docs")
    print()


async def test_rate_limiting():
    """Test rate limiting by making rapid requests."""
    print("=" * 60)
    print("Rate Limiting Test")
    print("=" * 60)
    print()

    client = AuthenticatedPredictionClient()

    # Login
    email = input("Email: ").strip() or "test@example.com"
    password = input("Password: ").strip() or "password123"

    success = await client.login(email, password)
    if not success:
        print("❌ Authentication failed")
        return

    print()
    print("Making 25 rapid requests to test rate limiting...")
    print("Free tier limit: 20 requests/minute")
    print()

    for i in range(25):
        result = await client.get_indicators("AAPL")

        if "error" in result:
            if result["error"] == "rate_limit":
                print(f"🛑 Rate limited after {i} requests")
                print(f"   Retry after: {result.get('retry_after', '60')}s")
                break
            else:
                print(f"❌ Error: {result['error']}")
                break
        else:
            print(f"✅ Request {i+1}: Success")

        # Small delay to see individual requests
        await asyncio.sleep(0.1)

    print()
    print("Rate limiting test complete!")


if __name__ == "__main__":
    import sys

    if len(sys.argv) > 1 and sys.argv[1] == "--test-rate-limit":
        asyncio.run(test_rate_limiting())
    else:
        asyncio.run(demo())
