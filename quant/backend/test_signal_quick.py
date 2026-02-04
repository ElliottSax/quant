#!/usr/bin/env python3
"""Quick test of signal generator without pytest infrastructure."""

import os
import sys

# Set environment before any imports
os.environ["ENVIRONMENT"] = "test"

# Add current directory to path
sys.path.insert(0, os.path.dirname(__file__))

from app.services.signal_generator import (
    SignalType,
    SignalConfidence,
    TradingSignal,
    SignalGenerator
)
from datetime import datetime

def test_signal_types():
    """Test that all signal types exist."""
    assert SignalType.BUY == "buy"
    assert SignalType.SELL == "sell"
    assert SignalType.HOLD == "hold"
    assert SignalType.STRONG_BUY == "strong_buy"
    assert SignalType.STRONG_SELL == "strong_sell"
    print("✓ Signal types test passed")

def test_confidence_levels():
    """Test confidence levels."""
    assert SignalConfidence.VERY_LOW == "very_low"
    assert SignalConfidence.LOW == "low"
    assert SignalConfidence.MEDIUM == "medium"
    assert SignalConfidence.HIGH == "high"
    assert SignalConfidence.VERY_HIGH == "very_high"
    print("✓ Confidence levels test passed")

def test_signal_generator_creation():
    """Test creating a signal generator."""
    generator = SignalGenerator()
    assert generator is not None
    assert generator.ensemble is None  # No ensemble in test mode
    print("✓ SignalGenerator creation test passed")

async def test_generate_signal():
    """Test generating a basic signal."""
    generator = SignalGenerator()

    # Create sample price data (30 days)
    prices = [100 + i * 0.5 for i in range(30)]

    signal = await generator.generate_signal(
        symbol="TEST",
        price_data=prices
    )

    assert signal.symbol == "TEST"
    assert signal.signal_type in SignalType
    assert signal.confidence in SignalConfidence
    assert 0 <= signal.confidence_score <= 1
    assert signal.price == prices[-1]
    assert 0 <= signal.risk_score <= 100
    print("✓ Generate signal test passed")

if __name__ == "__main__":
    import asyncio

    print("Running quick signal generator tests...")
    print()

    # Run sync tests
    test_signal_types()
    test_confidence_levels()
    test_signal_generator_creation()

    # Run async test
    asyncio.run(test_generate_signal())

    print()
    print("=" * 50)
    print("ALL TESTS PASSED! ✓")
    print("=" * 50)
