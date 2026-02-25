#!/usr/bin/env python3
"""Quick test of websocket events without pytest infrastructure."""

import os
import sys
import asyncio
from decimal import Decimal

# Set environment before any imports
os.environ["ENVIRONMENT"] = "test"

# Add current directory to path
sys.path.insert(0, os.path.dirname(__file__))

from app.services.websocket_events import (
    EventType,
    Event,
    PriceAlertManager,
    ActivityMonitor,
    EventBroadcaster
)
from datetime import datetime, timezone

def test_event_types():
    """Test that all event types exist."""
    assert EventType.NEW_TRADE == "new_trade"
    assert EventType.LARGE_TRADE == "large_trade"
    assert EventType.PRICE_ALERT == "price_alert"
    assert EventType.MARKET_QUOTE == "market_quote"
    assert EventType.SYSTEM_ALERT == "system_alert"
    print("✓ Event types test passed")

def test_event_creation():
    """Test creating an event."""
    event = Event(
        type=EventType.NEW_TRADE,
        data={"symbol": "AAPL", "price": 150.0}
    )
    assert event.type == EventType.NEW_TRADE
    assert event.data["symbol"] == "AAPL"
    assert event.priority == 0
    assert event.timestamp is not None
    print("✓ Event creation test passed")

async def test_price_alerts():
    """Test price alert functionality."""
    manager = PriceAlertManager()

    # Add an alert
    alert_id = await manager.add_alert(
        user_id="user123",
        symbol="AAPL",
        condition="above",
        target_price=Decimal("150.00")
    )

    assert alert_id is not None
    assert "user123" in alert_id

    # Check price below target - no trigger
    events = await manager.check_price("AAPL", Decimal("145.00"))
    assert len(events) == 0

    # Check price above target - should trigger
    events = await manager.check_price("AAPL", Decimal("151.00"))
    assert len(events) == 1
    assert events[0].type == EventType.PRICE_ALERT
    assert events[0].data["symbol"] == "AAPL"

    print("✓ Price alerts test passed")

async def test_activity_monitor():
    """Test activity monitoring."""
    monitor = ActivityMonitor()

    # Small trade - no events
    events = await monitor.analyze_trade(
        politician_name="John Doe",
        symbol="AAPL",
        amount="$50,000",
        transaction_type="buy"
    )
    assert len(events) == 0

    # Large trade - should trigger
    events = await monitor.analyze_trade(
        politician_name="Jane Smith",
        symbol="TSLA",
        amount="$1,500,000 - $5,000,000",
        transaction_type="sell"
    )
    assert len(events) == 1
    assert events[0].type == EventType.LARGE_TRADE
    assert events[0].data["politician"] == "Jane Smith"

    print("✓ Activity monitor test passed")

async def test_event_broadcaster():
    """Test event broadcasting."""
    broadcaster = EventBroadcaster()

    # Track callback calls
    called = []

    async def callback(event):
        called.append(event)

    # Subscribe
    await broadcaster.subscribe(
        subscriber_id="test_sub",
        event_types=[EventType.SYSTEM_ALERT],
        callback=callback
    )

    # Broadcast event
    await broadcaster.emit_system_alert("Test message")

    # Give async tasks a moment to complete
    await asyncio.sleep(0.1)

    assert len(called) == 1
    assert called[0].type == EventType.SYSTEM_ALERT
    assert called[0].data["message"] == "Test message"

    # Cleanup
    await broadcaster.unsubscribe("test_sub")

    print("✓ Event broadcaster test passed")

if __name__ == "__main__":
    print("Running quick websocket events tests...")
    print()

    # Run sync tests
    test_event_types()
    test_event_creation()

    # Run async tests
    asyncio.run(test_price_alerts())
    asyncio.run(test_activity_monitor())
    asyncio.run(test_event_broadcaster())

    print()
    print("=" * 50)
    print("ALL TESTS PASSED! ✓")
    print("=" * 50)
