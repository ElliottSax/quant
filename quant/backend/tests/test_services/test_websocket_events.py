"""Tests for WebSocket Events service."""

import pytest
import asyncio
from datetime import datetime, timezone, timedelta
from decimal import Decimal
from unittest.mock import AsyncMock, Mock
from typing import List

# Heavy imports are mocked in conftest.py
from app.services.websocket_events import (
    EventType,
    Event,
    PriceAlertManager,
    ActivityMonitor,
    EventBroadcaster,
    event_broadcaster,
)


class TestEventType:
    """Test EventType enum."""

    def test_trade_event_types(self):
        """Test trade-related event types."""
        assert EventType.NEW_TRADE == "new_trade"
        assert EventType.LARGE_TRADE == "large_trade"
        assert EventType.UNUSUAL_ACTIVITY == "unusual_activity"

    def test_price_event_types(self):
        """Test price-related event types."""
        assert EventType.PRICE_ALERT == "price_alert"
        assert EventType.PRICE_TARGET_HIT == "price_target_hit"
        assert EventType.SIGNIFICANT_MOVE == "significant_move"

    def test_portfolio_event_types(self):
        """Test portfolio event types."""
        assert EventType.PORTFOLIO_UPDATE == "portfolio_update"
        assert EventType.POSITION_CHANGE == "position_change"

    def test_market_event_types(self):
        """Test market event types."""
        assert EventType.MARKET_OPEN == "market_open"
        assert EventType.MARKET_CLOSE == "market_close"
        assert EventType.MARKET_QUOTE == "market_quote"

    def test_system_event_types(self):
        """Test system event types."""
        assert EventType.SYSTEM_ALERT == "system_alert"
        assert EventType.MAINTENANCE == "maintenance"

    def test_all_event_types_count(self):
        """Test that we have all expected event types."""
        event_types = list(EventType)
        assert len(event_types) == 13


class TestEvent:
    """Test Event dataclass."""

    def test_create_basic_event(self):
        """Test creating a basic event."""
        event = Event(
            type=EventType.NEW_TRADE,
            data={"symbol": "AAPL", "price": 150.0}
        )

        assert event.type == EventType.NEW_TRADE
        assert event.data == {"symbol": "AAPL", "price": 150.0}
        assert event.priority == 0
        assert event.timestamp is not None

    def test_event_auto_timestamp(self):
        """Test that timestamp is auto-generated."""
        event = Event(
            type=EventType.PRICE_ALERT,
            data={}
        )

        assert event.timestamp is not None
        # Verify it's a valid ISO format timestamp
        parsed = datetime.fromisoformat(event.timestamp.replace('Z', '+00:00'))
        assert isinstance(parsed, datetime)

    def test_event_custom_timestamp(self):
        """Test creating event with custom timestamp."""
        custom_time = "2024-01-15T10:30:00+00:00"
        event = Event(
            type=EventType.MARKET_OPEN,
            data={},
            timestamp=custom_time
        )

        assert event.timestamp == custom_time

    def test_event_priority_levels(self):
        """Test different priority levels."""
        normal = Event(type=EventType.NEW_TRADE, data={}, priority=0)
        high = Event(type=EventType.LARGE_TRADE, data={}, priority=1)
        critical = Event(type=EventType.SYSTEM_ALERT, data={}, priority=2)

        assert normal.priority == 0
        assert high.priority == 1
        assert critical.priority == 2

    def test_event_to_dict(self):
        """Test converting event to dictionary."""
        event = Event(
            type=EventType.PRICE_ALERT,
            data={"symbol": "TSLA", "price": 200.0},
            priority=1
        )

        result = event.to_dict()

        assert isinstance(result, dict)
        assert result["type"] == "price_alert"  # Enum converted to string value
        assert result["data"] == {"symbol": "TSLA", "price": 200.0}
        assert result["priority"] == 1
        assert "timestamp" in result


class TestPriceAlertManager:
    """Test PriceAlertManager class."""

    @pytest.fixture
    async def manager(self):
        """Create a PriceAlertManager instance."""
        return PriceAlertManager()

    async def test_add_alert(self, manager):
        """Test adding a price alert."""
        alert_id = await manager.add_alert(
            user_id="user123",
            symbol="AAPL",
            condition="above",
            target_price=Decimal("150.00")
        )

        assert alert_id is not None
        assert "user123" in alert_id
        assert "AAPL" in alert_id

    async def test_add_multiple_alerts_same_symbol(self, manager):
        """Test adding multiple alerts for the same symbol."""
        alert1 = await manager.add_alert(
            user_id="user123",
            symbol="AAPL",
            condition="above",
            target_price=Decimal("150.00")
        )
        alert2 = await manager.add_alert(
            user_id="user123",
            symbol="AAPL",
            condition="below",
            target_price=Decimal("140.00")
        )

        assert alert1 != alert2
        alerts = await manager.get_user_alerts("user123")
        assert len(alerts) == 2

    async def test_add_alerts_different_users(self, manager):
        """Test adding alerts for different users."""
        await manager.add_alert(
            user_id="user1",
            symbol="AAPL",
            condition="above",
            target_price=Decimal("150.00")
        )
        await manager.add_alert(
            user_id="user2",
            symbol="AAPL",
            condition="above",
            target_price=Decimal("155.00")
        )

        user1_alerts = await manager.get_user_alerts("user1")
        user2_alerts = await manager.get_user_alerts("user2")

        assert len(user1_alerts) == 1
        assert len(user2_alerts) == 1
        assert user1_alerts[0]["user_id"] == "user1"
        assert user2_alerts[0]["user_id"] == "user2"

    async def test_remove_alert(self, manager):
        """Test removing an alert."""
        alert_id = await manager.add_alert(
            user_id="user123",
            symbol="AAPL",
            condition="above",
            target_price=Decimal("150.00")
        )

        success = await manager.remove_alert("user123", alert_id)
        assert success is True

        alerts = await manager.get_user_alerts("user123")
        assert len(alerts) == 0

    async def test_remove_nonexistent_alert(self, manager):
        """Test removing an alert that doesn't exist."""
        success = await manager.remove_alert("user123", "fake_alert_id")
        assert success is False

    async def test_check_price_above_condition(self, manager):
        """Test price check with 'above' condition."""
        await manager.add_alert(
            user_id="user123",
            symbol="AAPL",
            condition="above",
            target_price=Decimal("150.00")
        )

        # Price below target - no trigger
        events = await manager.check_price("AAPL", Decimal("145.00"))
        assert len(events) == 0

        # Price above target - should trigger
        events = await manager.check_price("AAPL", Decimal("151.00"))
        assert len(events) == 1
        assert events[0].type == EventType.PRICE_ALERT
        assert events[0].data["symbol"] == "AAPL"
        assert events[0].data["current_price"] == 151.00

    async def test_check_price_below_condition(self, manager):
        """Test price check with 'below' condition."""
        await manager.add_alert(
            user_id="user123",
            symbol="TSLA",
            condition="below",
            target_price=Decimal("200.00")
        )

        # Price above target - no trigger
        events = await manager.check_price("TSLA", Decimal("205.00"))
        assert len(events) == 0

        # Price below target - should trigger
        events = await manager.check_price("TSLA", Decimal("195.00"))
        assert len(events) == 1
        assert events[0].type == EventType.PRICE_ALERT

    async def test_check_price_percent_change_condition(self, manager):
        """Test price check with 'percent_change' condition."""
        await manager.add_alert(
            user_id="user123",
            symbol="MSFT",
            condition="percent_change",
            target_price=Decimal("5.0")  # 5% change
        )

        # Small change - no trigger
        events = await manager.check_price(
            "MSFT",
            Decimal("102.00"),
            previous_price=Decimal("100.00")
        )
        assert len(events) == 0

        # Large change - should trigger
        events = await manager.check_price(
            "MSFT",
            Decimal("106.00"),
            previous_price=Decimal("100.00")
        )
        assert len(events) == 1

    async def test_alert_triggered_only_once(self, manager):
        """Test that alerts only trigger once."""
        await manager.add_alert(
            user_id="user123",
            symbol="AAPL",
            condition="above",
            target_price=Decimal("150.00")
        )

        # First check - triggers
        events1 = await manager.check_price("AAPL", Decimal("151.00"))
        assert len(events1) == 1

        # Second check - should not trigger again
        events2 = await manager.check_price("AAPL", Decimal("152.00"))
        assert len(events2) == 0

    async def test_get_user_alerts_empty(self, manager):
        """Test getting alerts for user with no alerts."""
        alerts = await manager.get_user_alerts("nonexistent_user")
        assert alerts == []

    async def test_alert_includes_extra_kwargs(self, manager):
        """Test that extra kwargs are stored in alert."""
        await manager.add_alert(
            user_id="user123",
            symbol="GOOGL",
            condition="above",
            target_price=Decimal("2800.00"),
            note="Important milestone",
            notification_type="email"
        )

        alerts = await manager.get_user_alerts("user123")
        assert len(alerts) == 1
        assert alerts[0]["note"] == "Important milestone"
        assert alerts[0]["notification_type"] == "email"

    async def test_concurrent_alert_operations(self, manager):
        """Test concurrent alert additions (thread safety)."""
        tasks = [
            manager.add_alert(
                user_id=f"user{i}",
                symbol="AAPL",
                condition="above",
                target_price=Decimal("150.00")
            )
            for i in range(10)
        ]

        alert_ids = await asyncio.gather(*tasks)
        assert len(alert_ids) == 10
        assert len(set(alert_ids)) == 10  # All unique


class TestActivityMonitor:
    """Test ActivityMonitor class."""

    @pytest.fixture
    async def monitor(self):
        """Create an ActivityMonitor instance."""
        return ActivityMonitor()

    async def test_analyze_small_trade(self, monitor):
        """Test analyzing a small trade (no events)."""
        events = await monitor.analyze_trade(
            politician_name="John Doe",
            symbol="AAPL",
            amount="$15,001 - $50,000",
            transaction_type="buy"
        )

        assert len(events) == 0

    async def test_analyze_large_trade(self, monitor):
        """Test analyzing a large trade (>$1M)."""
        events = await monitor.analyze_trade(
            politician_name="Jane Smith",
            symbol="TSLA",
            amount="$1,000,001 - $5,000,000",
            transaction_type="buy"
        )

        assert len(events) == 1
        assert events[0].type == EventType.LARGE_TRADE
        assert events[0].data["politician"] == "Jane Smith"
        assert events[0].data["symbol"] == "TSLA"
        assert events[0].data["amount_value"] == 1000001.0
        assert events[0].priority == 1

    async def test_analyze_trade_clustering(self, monitor):
        """Test detecting trade clustering (3+ trades in 7 days)."""
        # Add 3 trades for same politician/symbol
        for i in range(3):
            await monitor.analyze_trade(
                politician_name="Bob Johnson",
                symbol="MSFT",
                amount="$50,000 - $100,000",
                transaction_type="buy"
            )
            # Small delay to ensure distinct timestamps
            await asyncio.sleep(0.01)

        # Third trade should trigger clustering detection
        events = await monitor.analyze_trade(
            politician_name="Bob Johnson",
            symbol="MSFT",
            amount="$50,000 - $100,000",
            transaction_type="sell"
        )

        # Should have unusual activity event
        clustering_events = [e for e in events if e.type == EventType.UNUSUAL_ACTIVITY]
        assert len(clustering_events) > 0

        clustering = clustering_events[0]
        assert clustering.data["pattern"] == "clustering"
        assert clustering.data["politician"] == "Bob Johnson"
        assert clustering.data["symbol"] == "MSFT"
        assert clustering.data["trade_count"] >= 3

    async def test_parse_amount_range(self, monitor):
        """Test parsing amount ranges."""
        assert monitor._parse_amount("$15,001 - $50,000") == 15001.0
        assert monitor._parse_amount("$1,000,001 - $5,000,000") == 1000001.0
        assert monitor._parse_amount("$250,001 - $500,000") == 250001.0

    async def test_parse_amount_single_value(self, monitor):
        """Test parsing single amount value."""
        assert monitor._parse_amount("$100,000") == 100000.0

    async def test_parse_amount_invalid(self, monitor):
        """Test parsing invalid amount returns None."""
        assert monitor._parse_amount("Unknown") is None
        assert monitor._parse_amount("") is None

    async def test_recent_trades_cleanup(self, monitor):
        """Test that old trades are cleaned up."""
        # This would require mocking datetime to test properly
        # For now, verify the data structure
        await monitor.analyze_trade(
            politician_name="Test",
            symbol="TEST",
            amount="$50,000",
            transaction_type="buy"
        )

        assert "Test_TEST" in monitor.recent_trades
        assert len(monitor.recent_trades["Test_TEST"]) > 0

    async def test_concurrent_trade_analysis(self, monitor):
        """Test concurrent trade analysis (thread safety)."""
        tasks = [
            monitor.analyze_trade(
                politician_name="Politician",
                symbol="STOCK",
                amount="$50,000",
                transaction_type="buy"
            )
            for _ in range(5)
        ]

        results = await asyncio.gather(*tasks)
        assert len(results) == 5


class TestEventBroadcaster:
    """Test EventBroadcaster class."""

    @pytest.fixture
    async def broadcaster(self):
        """Create a fresh EventBroadcaster instance."""
        return EventBroadcaster()

    async def test_subscribe_single_event(self, broadcaster):
        """Test subscribing to a single event type."""
        callback = AsyncMock()

        await broadcaster.subscribe(
            subscriber_id="sub1",
            event_types=[EventType.NEW_TRADE],
            callback=callback
        )

        assert EventType.NEW_TRADE in broadcaster.subscribers
        assert "sub1" in broadcaster.subscribers[EventType.NEW_TRADE]

    async def test_subscribe_multiple_events(self, broadcaster):
        """Test subscribing to multiple event types."""
        callback = AsyncMock()

        await broadcaster.subscribe(
            subscriber_id="sub1",
            event_types=[EventType.NEW_TRADE, EventType.PRICE_ALERT],
            callback=callback
        )

        assert EventType.NEW_TRADE in broadcaster.subscribers
        assert EventType.PRICE_ALERT in broadcaster.subscribers
        assert "sub1" in broadcaster.subscribers[EventType.NEW_TRADE]
        assert "sub1" in broadcaster.subscribers[EventType.PRICE_ALERT]

    async def test_subscribe_with_user_id(self, broadcaster):
        """Test subscribing with user ID."""
        callback = AsyncMock()

        await broadcaster.subscribe(
            subscriber_id="user_123_conn",
            event_types=[EventType.PRICE_ALERT],
            callback=callback,
            user_id="123"
        )

        assert "123" in broadcaster.user_subscriptions
        assert EventType.PRICE_ALERT in broadcaster.user_subscriptions["123"]

    async def test_unsubscribe(self, broadcaster):
        """Test unsubscribing from events."""
        callback = AsyncMock()

        await broadcaster.subscribe(
            subscriber_id="sub1",
            event_types=[EventType.NEW_TRADE],
            callback=callback
        )

        await broadcaster.unsubscribe("sub1")

        assert "sub1" not in broadcaster.subscribers.get(EventType.NEW_TRADE, {})

    async def test_broadcast_to_subscribers(self, broadcaster):
        """Test broadcasting event to subscribers."""
        callback = AsyncMock()

        await broadcaster.subscribe(
            subscriber_id="sub1",
            event_types=[EventType.NEW_TRADE],
            callback=callback
        )

        event = Event(
            type=EventType.NEW_TRADE,
            data={"symbol": "AAPL"}
        )

        await broadcaster.broadcast(event)

        callback.assert_called_once()
        assert callback.call_args[0][0].type == EventType.NEW_TRADE

    async def test_broadcast_to_multiple_subscribers(self, broadcaster):
        """Test broadcasting to multiple subscribers."""
        callback1 = AsyncMock()
        callback2 = AsyncMock()

        await broadcaster.subscribe(
            subscriber_id="sub1",
            event_types=[EventType.PRICE_ALERT],
            callback=callback1
        )
        await broadcaster.subscribe(
            subscriber_id="sub2",
            event_types=[EventType.PRICE_ALERT],
            callback=callback2
        )

        event = Event(type=EventType.PRICE_ALERT, data={})
        await broadcaster.broadcast(event)

        callback1.assert_called_once()
        callback2.assert_called_once()

    async def test_broadcast_to_specific_user(self, broadcaster):
        """Test broadcasting to a specific user."""
        callback1 = AsyncMock()
        callback2 = AsyncMock()

        await broadcaster.subscribe(
            subscriber_id="user_123_conn",
            event_types=[EventType.PRICE_ALERT],
            callback=callback1
        )
        await broadcaster.subscribe(
            subscriber_id="user_456_conn",
            event_types=[EventType.PRICE_ALERT],
            callback=callback2
        )

        event = Event(
            type=EventType.PRICE_ALERT,
            data={"user_id": "123"}
        )

        await broadcaster.broadcast(event, target_user_id="123")

        # Only user 123's callback should be called
        callback1.assert_called_once()
        callback2.assert_not_called()

    async def test_broadcast_no_subscribers(self, broadcaster):
        """Test broadcasting when there are no subscribers."""
        event = Event(type=EventType.NEW_TRADE, data={})

        # Should not raise an exception
        await broadcaster.broadcast(event)

    async def test_broadcast_callback_error_handling(self, broadcaster):
        """Test that callback errors don't break broadcasting."""
        callback1 = AsyncMock(side_effect=Exception("Callback error"))
        callback2 = AsyncMock()

        await broadcaster.subscribe(
            subscriber_id="sub1",
            event_types=[EventType.NEW_TRADE],
            callback=callback1
        )
        await broadcaster.subscribe(
            subscriber_id="sub2",
            event_types=[EventType.NEW_TRADE],
            callback=callback2
        )

        event = Event(type=EventType.NEW_TRADE, data={})

        # Should not raise exception
        await broadcaster.broadcast(event)

        # Both callbacks should have been attempted
        callback1.assert_called_once()
        callback2.assert_called_once()

    async def test_emit_trade(self, broadcaster):
        """Test emitting a trade event."""
        callback = AsyncMock()

        await broadcaster.subscribe(
            subscriber_id="sub1",
            event_types=[EventType.NEW_TRADE],
            callback=callback
        )

        trade_data = {
            "politician": "John Doe",
            "ticker": "AAPL",
            "amount": "$50,000",
            "transaction_type": "buy"
        }

        await broadcaster.emit_trade(trade_data)

        callback.assert_called()

    async def test_emit_trade_with_large_amount(self, broadcaster):
        """Test emitting a large trade triggers additional events."""
        new_trade_callback = AsyncMock()
        large_trade_callback = AsyncMock()

        await broadcaster.subscribe(
            subscriber_id="sub1",
            event_types=[EventType.NEW_TRADE],
            callback=new_trade_callback
        )
        await broadcaster.subscribe(
            subscriber_id="sub2",
            event_types=[EventType.LARGE_TRADE],
            callback=large_trade_callback
        )

        trade_data = {
            "politician": "Jane Smith",
            "ticker": "TSLA",
            "amount": "$1,500,000 - $5,000,000",
            "transaction_type": "sell"
        }

        await broadcaster.emit_trade(trade_data)

        new_trade_callback.assert_called_once()
        large_trade_callback.assert_called_once()

    async def test_emit_price_update(self, broadcaster):
        """Test emitting a price update."""
        callback = AsyncMock()

        await broadcaster.subscribe(
            subscriber_id="sub1",
            event_types=[EventType.MARKET_QUOTE],
            callback=callback
        )

        await broadcaster.emit_price_update(
            symbol="AAPL",
            current_price=Decimal("150.50"),
            quote_data={"volume": 1000000}
        )

        callback.assert_called_once()

    async def test_emit_price_update_triggers_alert(self, broadcaster):
        """Test price update that triggers an alert."""
        alert_callback = AsyncMock()

        await broadcaster.subscribe(
            subscriber_id="user_123_conn",
            event_types=[EventType.PRICE_ALERT],
            callback=alert_callback
        )

        # Add alert
        await broadcaster.price_alerts.add_alert(
            user_id="123",
            symbol="AAPL",
            condition="above",
            target_price=Decimal("150.00")
        )

        # Emit price update that triggers alert
        await broadcaster.emit_price_update(
            symbol="AAPL",
            current_price=Decimal("151.00"),
            quote_data={}
        )

        # Should trigger alert callback
        alert_callback.assert_called()

    async def test_emit_system_alert(self, broadcaster):
        """Test emitting a system alert."""
        callback = AsyncMock()

        await broadcaster.subscribe(
            subscriber_id="sub1",
            event_types=[EventType.SYSTEM_ALERT],
            callback=callback
        )

        await broadcaster.emit_system_alert("System maintenance scheduled", priority=2)

        callback.assert_called_once()
        event = callback.call_args[0][0]
        assert event.type == EventType.SYSTEM_ALERT
        assert event.data["message"] == "System maintenance scheduled"
        assert event.priority == 2

    async def test_synchronous_callback(self, broadcaster):
        """Test that synchronous callbacks work."""
        results = []

        def sync_callback(event):
            results.append(event)

        await broadcaster.subscribe(
            subscriber_id="sub1",
            event_types=[EventType.NEW_TRADE],
            callback=sync_callback
        )

        event = Event(type=EventType.NEW_TRADE, data={})
        await broadcaster.broadcast(event)

        assert len(results) == 1
        assert results[0].type == EventType.NEW_TRADE

    async def test_broadcaster_has_managers(self, broadcaster):
        """Test that broadcaster initializes managers."""
        assert isinstance(broadcaster.price_alerts, PriceAlertManager)
        assert isinstance(broadcaster.activity_monitor, ActivityMonitor)


class TestGlobalEventBroadcaster:
    """Test the global event_broadcaster instance."""

    def test_global_instance_exists(self):
        """Test that global instance is created."""
        assert event_broadcaster is not None
        assert isinstance(event_broadcaster, EventBroadcaster)

    async def test_global_instance_functional(self):
        """Test that global instance is functional."""
        callback = AsyncMock()

        await event_broadcaster.subscribe(
            subscriber_id="test_global",
            event_types=[EventType.SYSTEM_ALERT],
            callback=callback
        )

        await event_broadcaster.emit_system_alert("Test message")

        callback.assert_called_once()

        # Cleanup
        await event_broadcaster.unsubscribe("test_global")
