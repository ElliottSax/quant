"""
WebSocket Event Broadcasting Service

Centralized event system for real-time updates:
- Price alerts
- Trade alerts
- Activity alerts
- System notifications
"""

import asyncio
from datetime import datetime, timezone
from typing import Dict, List, Optional, Set, Callable, Any
from enum import Enum
from dataclasses import dataclass, asdict
from decimal import Decimal

from app.core.logging import get_logger

# Conditional import for testing - cache_manager not used in this module anyway
try:
    from app.core.cache import cache_manager
except ImportError:
    cache_manager = None  # type: ignore

logger = get_logger(__name__)


class EventType(str, Enum):
    """WebSocket event types"""
    # Trade events
    NEW_TRADE = "new_trade"
    LARGE_TRADE = "large_trade"
    UNUSUAL_ACTIVITY = "unusual_activity"

    # Price events
    PRICE_ALERT = "price_alert"
    PRICE_TARGET_HIT = "price_target_hit"
    SIGNIFICANT_MOVE = "significant_move"

    # Portfolio events
    PORTFOLIO_UPDATE = "portfolio_update"
    POSITION_CHANGE = "position_change"

    # Market events
    MARKET_OPEN = "market_open"
    MARKET_CLOSE = "market_close"
    MARKET_QUOTE = "market_quote"

    # System events
    SYSTEM_ALERT = "system_alert"
    MAINTENANCE = "maintenance"


@dataclass
class Event:
    """WebSocket event data structure"""
    type: EventType
    data: Dict[str, Any]
    timestamp: str = None
    priority: int = 0  # 0=normal, 1=high, 2=critical

    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now(timezone.utc).isoformat()

    def to_dict(self) -> dict:
        """Convert event to dictionary for JSON serialization"""
        result = asdict(self)
        result['type'] = self.type.value
        return result


class PriceAlertManager:
    """
    Manages price alerts and triggers notifications.

    Monitors prices and triggers alerts when conditions are met.
    """

    def __init__(self):
        # Alert structure: {user_id: {symbol: [alerts]}}
        self.alerts: Dict[str, Dict[str, List[dict]]] = {}
        self._lock = asyncio.Lock()
        self._monitoring_task: Optional[asyncio.Task] = None

    async def add_alert(
        self,
        user_id: str,
        symbol: str,
        condition: str,  # "above", "below", "percent_change"
        target_price: Decimal,
        **kwargs
    ) -> str:
        """Add a price alert for a user"""
        alert_id = f"{user_id}_{symbol}_{datetime.now().timestamp()}"

        alert = {
            "id": alert_id,
            "user_id": user_id,
            "symbol": symbol,
            "condition": condition,
            "target_price": float(target_price),
            "created_at": datetime.now(timezone.utc).isoformat(),
            "triggered": False,
            **kwargs
        }

        async with self._lock:
            if user_id not in self.alerts:
                self.alerts[user_id] = {}
            if symbol not in self.alerts[user_id]:
                self.alerts[user_id][symbol] = []

            self.alerts[user_id][symbol].append(alert)

        logger.info(f"Added price alert: {alert_id} for {symbol} @ {target_price}")
        return alert_id

    async def remove_alert(self, user_id: str, alert_id: str) -> bool:
        """Remove a price alert"""
        async with self._lock:
            if user_id not in self.alerts:
                return False

            for symbol in self.alerts[user_id]:
                self.alerts[user_id][symbol] = [
                    a for a in self.alerts[user_id][symbol]
                    if a["id"] != alert_id
                ]

            return True

    async def check_price(
        self,
        symbol: str,
        current_price: Decimal,
        previous_price: Optional[Decimal] = None
    ) -> List[Event]:
        """Check if price meets any alert conditions"""
        triggered_events = []

        async with self._lock:
            for user_id in self.alerts:
                if symbol not in self.alerts[user_id]:
                    continue

                for alert in self.alerts[user_id][symbol]:
                    if alert["triggered"]:
                        continue

                    triggered = False
                    condition = alert["condition"]
                    target = Decimal(str(alert["target_price"]))

                    if condition == "above" and current_price >= target:
                        triggered = True
                    elif condition == "below" and current_price <= target:
                        triggered = True
                    elif condition == "percent_change" and previous_price:
                        percent_change = abs((current_price - previous_price) / previous_price * 100)
                        if percent_change >= target:
                            triggered = True

                    if triggered:
                        alert["triggered"] = True
                        alert["triggered_at"] = datetime.now(timezone.utc).isoformat()
                        alert["triggered_price"] = float(current_price)

                        event = Event(
                            type=EventType.PRICE_ALERT,
                            data={
                                "alert_id": alert["id"],
                                "user_id": user_id,
                                "symbol": symbol,
                                "condition": condition,
                                "target_price": float(target),
                                "current_price": float(current_price),
                                "message": f"{symbol} {condition} ${target}"
                            },
                            priority=1
                        )
                        triggered_events.append(event)

        return triggered_events

    async def get_user_alerts(self, user_id: str) -> List[dict]:
        """Get all alerts for a user"""
        alerts = []
        async with self._lock:
            if user_id in self.alerts:
                for symbol_alerts in self.alerts[user_id].values():
                    alerts.extend(symbol_alerts)
        return alerts


class ActivityMonitor:
    """
    Monitors trading activity and detects unusual patterns.
    """

    def __init__(self):
        self.baseline_volumes: Dict[str, float] = {}
        self.recent_trades: Dict[str, List[dict]] = {}
        self._lock = asyncio.Lock()

    async def analyze_trade(
        self,
        politician_name: str,
        symbol: str,
        amount: str,
        transaction_type: str,
        **kwargs
    ) -> List[Event]:
        """Analyze a trade for unusual activity"""
        events = []

        # Parse amount (e.g., "$1,000,001 - $5,000,000")
        amount_value = self._parse_amount(amount)

        # Check for large trades (>$1M)
        if amount_value and amount_value > 1_000_000:
            events.append(Event(
                type=EventType.LARGE_TRADE,
                data={
                    "politician": politician_name,
                    "symbol": symbol,
                    "amount": amount,
                    "amount_value": amount_value,
                    "transaction_type": transaction_type,
                    "message": f"Large {transaction_type} by {politician_name}: {symbol} ({amount})",
                    **kwargs
                },
                priority=1
            ))

        # Track for clustering detection
        async with self._lock:
            key = f"{politician_name}_{symbol}"
            if key not in self.recent_trades:
                self.recent_trades[key] = []

            self.recent_trades[key].append({
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "amount_value": amount_value,
                "transaction_type": transaction_type
            })

            # Keep only last 30 days of trades
            cutoff = datetime.now(timezone.utc).timestamp() - (30 * 24 * 60 * 60)
            self.recent_trades[key] = [
                t for t in self.recent_trades[key]
                if datetime.fromisoformat(t["timestamp"].replace('Z', '+00:00')).timestamp() > cutoff
            ]

            # Check for clustering (3+ trades in 7 days)
            recent_count = len([
                t for t in self.recent_trades[key]
                if datetime.fromisoformat(t["timestamp"].replace('Z', '+00:00')).timestamp()
                > datetime.now(timezone.utc).timestamp() - (7 * 24 * 60 * 60)
            ])

            if recent_count >= 3:
                events.append(Event(
                    type=EventType.UNUSUAL_ACTIVITY,
                    data={
                        "pattern": "clustering",
                        "politician": politician_name,
                        "symbol": symbol,
                        "trade_count": recent_count,
                        "period_days": 7,
                        "message": f"Unusual activity: {politician_name} made {recent_count} trades in {symbol} within 7 days"
                    },
                    priority=1
                ))

        return events

    def _parse_amount(self, amount_str: str) -> Optional[float]:
        """Parse amount string to numeric value"""
        try:
            # Extract first number from range
            import re
            numbers = re.findall(r'[\d,]+', amount_str)
            if numbers:
                return float(numbers[0].replace(',', ''))
        except Exception:
            pass
        return None


class EventBroadcaster:
    """
    Central event broadcasting system.

    Manages event subscribers and distributes events.
    """

    def __init__(self):
        # Event subscribers: {event_type: {subscriber_id: callback}}
        self.subscribers: Dict[EventType, Dict[str, Callable]] = {}
        # User-specific subscriptions: {user_id: {event_type}}
        self.user_subscriptions: Dict[str, Set[EventType]] = {}
        self._lock = asyncio.Lock()

        # Initialize managers
        self.price_alerts = PriceAlertManager()
        self.activity_monitor = ActivityMonitor()

    async def subscribe(
        self,
        subscriber_id: str,
        event_types: List[EventType],
        callback: Callable,
        user_id: Optional[str] = None
    ):
        """Subscribe to events"""
        async with self._lock:
            for event_type in event_types:
                if event_type not in self.subscribers:
                    self.subscribers[event_type] = {}

                self.subscribers[event_type][subscriber_id] = callback

            if user_id:
                if user_id not in self.user_subscriptions:
                    self.user_subscriptions[user_id] = set()
                self.user_subscriptions[user_id].update(event_types)

        logger.info(f"Subscriber {subscriber_id} subscribed to {len(event_types)} event types")

    async def unsubscribe(self, subscriber_id: str):
        """Unsubscribe from all events"""
        async with self._lock:
            for event_type in self.subscribers:
                self.subscribers[event_type].pop(subscriber_id, None)

        logger.info(f"Subscriber {subscriber_id} unsubscribed")

    async def broadcast(self, event: Event, target_user_id: Optional[str] = None):
        """Broadcast an event to subscribers"""
        if event.type not in self.subscribers:
            return

        callbacks = []
        async with self._lock:
            for subscriber_id, callback in self.subscribers[event.type].items():
                # If target_user_id specified, only notify that user
                if target_user_id:
                    if subscriber_id.startswith(f"user_{target_user_id}"):
                        callbacks.append(callback)
                else:
                    callbacks.append(callback)

        # Execute callbacks concurrently
        if callbacks:
            await asyncio.gather(
                *[self._safe_callback(cb, event) for cb in callbacks],
                return_exceptions=True
            )

        logger.debug(f"Broadcasted {event.type} to {len(callbacks)} subscribers")

    async def _safe_callback(self, callback: Callable, event: Event):
        """Execute callback with error handling"""
        try:
            if asyncio.iscoroutinefunction(callback):
                await callback(event)
            else:
                callback(event)
        except Exception as e:
            logger.error(f"Error in event callback: {e}", exc_info=True)

    async def emit_trade(self, trade_data: dict):
        """Emit a new trade event with activity analysis"""
        # Create base event
        event = Event(
            type=EventType.NEW_TRADE,
            data=trade_data
        )
        await self.broadcast(event)

        # Check for unusual activity
        activity_events = await self.activity_monitor.analyze_trade(
            politician_name=trade_data.get("politician", ""),
            symbol=trade_data.get("ticker", ""),
            amount=trade_data.get("amount", ""),
            transaction_type=trade_data.get("transaction_type", ""),
            **trade_data
        )

        for activity_event in activity_events:
            await self.broadcast(activity_event)

    async def emit_price_update(
        self,
        symbol: str,
        current_price: Decimal,
        quote_data: dict,
        previous_price: Optional[Decimal] = None
    ):
        """Emit price update and check alerts"""
        # Market quote event
        event = Event(
            type=EventType.MARKET_QUOTE,
            data={
                "symbol": symbol,
                "price": float(current_price),
                **quote_data
            }
        )
        await self.broadcast(event)

        # Check price alerts
        alert_events = await self.price_alerts.check_price(
            symbol, current_price, previous_price
        )

        for alert_event in alert_events:
            # Send to specific user
            await self.broadcast(
                alert_event,
                target_user_id=alert_event.data.get("user_id")
            )

    async def emit_system_alert(self, message: str, priority: int = 0):
        """Emit a system-wide alert"""
        event = Event(
            type=EventType.SYSTEM_ALERT,
            data={"message": message},
            priority=priority
        )
        await self.broadcast(event)


# Global event broadcaster
event_broadcaster = EventBroadcaster()
