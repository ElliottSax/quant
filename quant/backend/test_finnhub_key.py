#!/usr/bin/env python3
"""
Quick test to verify Finnhub API key is working
"""

import os
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

try:
    from app.services.finnhub_client import FinnhubClient
    import asyncio
except ImportError as e:
    print(f"❌ Import error: {e}")
    print("Make sure you're in the backend directory and dependencies are installed.")
    sys.exit(1)


async def test_finnhub():
    """Test Finnhub API connection"""

    print("🔍 Testing Finnhub API Key...")
    print("-" * 50)

    # Check if API key is configured
    api_key = os.getenv("FINNHUB_API_KEY")

    if not api_key:
        print("❌ ERROR: FINNHUB_API_KEY not found in environment")
        print("\nPlease add your API key to .env file:")
        print("FINNHUB_API_KEY=your_key_here")
        return False

    if api_key == "PASTE_YOUR_KEY_HERE":
        print("❌ ERROR: Please replace 'PASTE_YOUR_KEY_HERE' with your actual Finnhub API key")
        print("\nEdit /mnt/e/projects/quant/quant/backend/.env")
        print("Replace: FINNHUB_API_KEY=PASTE_YOUR_KEY_HERE")
        print("With:    FINNHUB_API_KEY=your_actual_key")
        return False

    print(f"✅ API Key found: {api_key[:8]}...{api_key[-8:]}")
    print()

    # Test connection
    client = FinnhubClient(api_key)

    if not client.enabled:
        print("❌ ERROR: Finnhub client not enabled")
        return False

    print("📊 Testing real-time quote for AAPL...")
    try:
        quote = await client.get_quote("AAPL")
        print(f"✅ Success! AAPL Quote:")
        print(f"   Current Price: ${quote.current_price:.2f}")
        print(f"   Change: ${quote.change:+.2f} ({quote.percent_change:+.2f}%)")
        print(f"   High: ${quote.high:.2f}")
        print(f"   Low: ${quote.low:.2f}")
        print()
    except Exception as e:
        print(f"❌ Failed to get quote: {e}")
        return False

    print("📰 Testing news sentiment for AAPL...")
    try:
        sentiment = await client.get_news_sentiment("AAPL", days=7)
        print(f"✅ Success! AAPL Sentiment (7 days):")
        print(f"   Score: {sentiment.score:.1f}/100 ({sentiment.label})")
        print(f"   News Articles: {sentiment.news_count}")
        print()
    except Exception as e:
        print(f"❌ Failed to get sentiment: {e}")
        return False

    print("=" * 50)
    print("✅ ALL TESTS PASSED!")
    print("=" * 50)
    print()
    print("🎉 Your Finnhub API key is working correctly!")
    print()
    print("Next steps:")
    print("1. Deploy backend to Railway")
    print("2. Deploy frontend to Vercel")
    print("3. Launch on Product Hunt")
    print()

    await client.close()
    return True


if __name__ == "__main__":
    # Load .env file
    try:
        from dotenv import load_dotenv
        load_dotenv()
    except ImportError:
        print("⚠️  Warning: python-dotenv not installed, using system environment")

    # Run test
    success = asyncio.run(test_finnhub())
    sys.exit(0 if success else 1)
