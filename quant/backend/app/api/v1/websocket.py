"""
WebSocket endpoints for real-time updates.

Provides:
- Real-time market data streaming
- Trade notification broadcasts
- Portfolio updates
- Price alerts and event subscriptions
- Activity monitoring
- Reconnection support
"""

import asyncio
import json
from datetime import datetime
from typing import Dict, Set, Optional, List
from uuid import UUID
from decimal import Decimal

from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Query, Depends, HTTPException
from starlette.websockets import WebSocketState
from pydantic import BaseModel, Field

from app.core.logging import get_logger
from app.core.security import verify_token

logger = get_logger(__name__)

router = APIRouter(prefix="/ws", tags=["websocket"])

# Try to import market data and event services
try:
    from app.services.market_data import get_market_data_provider, DataProvider
    MARKET_DATA_AVAILABLE = True
except ImportError:
    logger.warning("Market data service not available")
    MARKET_DATA_AVAILABLE = False

try:
    from app.services.websocket_events import (
        event_broadcaster,
        Event,
        EventType,
        PriceAlertManager
    )
    from app.core.deps import get_current_user_optional
    EVENTS_AVAILABLE = True
except ImportError:
    logger.warning("Event system not available")
    EVENTS_AVAILABLE = False


# ==================== MODELS ====================

class PriceAlertRequest(BaseModel):
    """Price alert creation request"""
    symbol: str = Field(..., description="Stock symbol")
    condition: str = Field(..., description="Alert condition: above, below, percent_change")
    target_price: Decimal = Field(..., description="Target price or percentage")
    description: Optional[str] = Field(None, description="Optional alert description")


class SubscriptionRequest(BaseModel):
    """Event subscription request"""
    event_types: List[str] = Field(..., description="List of event types to subscribe to")
    symbols: Optional[List[str]] = Field(None, description="Filter by symbols")
    politicians: Optional[List[str]] = Field(None, description="Filter by politicians")


class ConnectionManager:
    """
    Manages WebSocket connections and broadcasts.

    Supports multiple channels:
    - market:{symbol} - Real-time quotes for a symbol
    - trades - New congressional trade notifications
    - portfolio:{user_id} - User portfolio updates
    """

    def __init__(self):
        # Active connections by channel
        self.active_connections: Dict[str, Set[WebSocket]] = {}
        # WebSocket to user mapping
        self.authenticated_users: Dict[WebSocket, str] = {}
        # Lock for thread-safe operations
        self._lock = asyncio.Lock()

    async def connect(
        self,
        websocket: WebSocket,
        channel: str,
        user_id: Optional[str] = None,
    ):
        """Add a WebSocket connection to a channel."""
        await websocket.accept()

        async with self._lock:
            if channel not in self.active_connections:
                self.active_connections[channel] = set()
            self.active_connections[channel].add(websocket)

            if user_id:
                self.authenticated_users[websocket] = user_id

        logger.info(f"WebSocket connected to channel: {channel}")

    async def disconnect(self, websocket: WebSocket, channel: str):
        """Remove a WebSocket connection from a channel."""
        async with self._lock:
            if channel in self.active_connections:
                self.active_connections[channel].discard(websocket)
                if not self.active_connections[channel]:
                    del self.active_connections[channel]

            if websocket in self.authenticated_users:
                del self.authenticated_users[websocket]

        logger.info(f"WebSocket disconnected from channel: {channel}")

    async def broadcast(self, channel: str, message: dict):
        """Broadcast message to all connections on a channel."""
        if channel not in self.active_connections:
            return

        disconnected = []
        for connection in self.active_connections[channel]:
            try:
                if connection.client_state == WebSocketState.CONNECTED:
                    await connection.send_json(message)
            except (ConnectionError, OSError) as e:
                # Network-level connection errors
                logger.warning(f"Connection error sending message: {e}")
                disconnected.append(connection)
            except (ValueError, TypeError) as e:
                # Message serialization errors
                logger.error(f"Failed to serialize message: {e}", exc_info=True)
                disconnected.append(connection)

        # Clean up disconnected clients
        for conn in disconnected:
            await self.disconnect(conn, channel)

    async def send_personal(self, websocket: WebSocket, message: dict):
        """Send a message to a specific WebSocket."""
        try:
            if websocket.client_state == WebSocketState.CONNECTED:
                await websocket.send_json(message)
        except (ConnectionError, OSError) as e:
            # Network-level connection errors
            logger.warning(f"Connection error sending personal message: {e}")
        except (ValueError, TypeError) as e:
            # Message serialization errors
            logger.error(f"Failed to serialize personal message: {e}", exc_info=True)

    def get_channel_count(self, channel: str) -> int:
        """Get number of connections on a channel."""
        return len(self.active_connections.get(channel, set()))

    def get_total_connections(self) -> int:
        """Get total number of active connections."""
        return sum(len(conns) for conns in self.active_connections.values())


# Global connection manager
manager = ConnectionManager()


@router.websocket("/market/{symbol}")
async def market_data_stream(
    websocket: WebSocket,
    symbol: str,
    interval: int = Query(default=5, description="Update interval in seconds"),
):
    """
    Stream real-time market data for a symbol.

    Sends quote updates at specified interval.

    Message format:
    {
        "type": "quote",
        "symbol": "AAPL",
        "price": 150.25,
        "change": 1.50,
        "change_percent": 1.01,
        "volume": 50000000,
        "timestamp": "2024-01-15T10:30:00Z"
    }
    """
    if not MARKET_DATA_AVAILABLE:
        await websocket.close(code=4003, reason="Market data service not available")
        return

    channel = f"market:{symbol.upper()}"
    await manager.connect(websocket, channel)

    # Validate interval
    interval = max(1, min(interval, 60))

    try:
        provider = get_market_data_provider(DataProvider.YAHOO_FINANCE)

        while True:
            try:
                # Fetch quote
                quote = await provider.get_quote(symbol.upper())

                message = {
                    "type": "quote",
                    "symbol": symbol.upper(),
                    "price": quote.price,
                    "change": quote.change,
                    "change_percent": quote.change_percent,
                    "volume": quote.volume,
                    "bid": quote.bid,
                    "ask": quote.ask,
                    "timestamp": datetime.utcnow().isoformat(),
                }

                await manager.send_personal(websocket, message)

            except (ConnectionError, TimeoutError) as e:
                # Market data provider connection/timeout errors
                logger.warning(f"Market data service error for {symbol}: {e}")
                await manager.send_personal(websocket, {
                    "type": "error",
                    "message": f"Market data service unavailable: {str(e)}",
                })
            except (ValueError, KeyError) as e:
                # Invalid quote data format
                logger.error(f"Invalid quote data for {symbol}: {e}")
                await manager.send_personal(websocket, {
                    "type": "error",
                    "message": f"Invalid quote data received: {str(e)}",
                })

            # Wait for next update
            await asyncio.sleep(interval)

    except WebSocketDisconnect:
        logger.info(f"Market stream disconnected: {symbol}")
    finally:
        await manager.disconnect(websocket, channel)


@router.websocket("/trades")
async def trade_notifications(
    websocket: WebSocket,
    token: Optional[str] = Query(default=None),
):
    """
    Stream new congressional trade notifications.

    Optional authentication for personalized notifications.

    Message format:
    {
        "type": "new_trade",
        "politician": "John Doe",
        "ticker": "AAPL",
        "transaction_type": "buy",
        "amount": "$50,001 - $100,000",
        "disclosure_date": "2024-01-15",
        "timestamp": "2024-01-15T10:30:00Z"
    }
    """
    channel = "trades"
    user_id = None

    # Verify token if provided
    if token:
        user_id, _ = verify_token(token, token_type="access")

    await manager.connect(websocket, channel, user_id)

    try:
        # Send welcome message
        await manager.send_personal(websocket, {
            "type": "connected",
            "message": "Connected to trade notifications",
            "authenticated": user_id is not None,
        })

        # Keep connection alive with periodic pings
        while True:
            try:
                # Wait for client messages (pings/pongs)
                data = await asyncio.wait_for(
                    websocket.receive_text(),
                    timeout=30.0
                )

                # Handle ping
                if data == "ping":
                    await manager.send_personal(websocket, {"type": "pong"})

            except asyncio.TimeoutError:
                # Send keepalive
                await manager.send_personal(websocket, {"type": "keepalive"})

    except WebSocketDisconnect:
        logger.info("Trade notifications disconnected")
    finally:
        await manager.disconnect(websocket, channel)


@router.websocket("/portfolio/{user_id}")
async def portfolio_updates(
    websocket: WebSocket,
    user_id: str,
    token: str = Query(...),
):
    """
    Stream portfolio updates for authenticated user.

    Requires authentication token.

    Message format:
    {
        "type": "portfolio_update",
        "positions": [...],
        "total_value": 100000.00,
        "daily_change": 1500.00,
        "daily_change_percent": 1.52,
        "timestamp": "2024-01-15T10:30:00Z"
    }
    """
    # Verify authentication
    verified_user_id, _ = verify_token(token, token_type="access")

    if not verified_user_id or verified_user_id != user_id:
        await websocket.close(code=4001, reason="Unauthorized")
        return

    channel = f"portfolio:{user_id}"
    await manager.connect(websocket, channel, user_id)

    try:
        await manager.send_personal(websocket, {
            "type": "connected",
            "message": "Connected to portfolio updates",
        })

        while True:
            try:
                data = await asyncio.wait_for(
                    websocket.receive_text(),
                    timeout=30.0
                )

                if data == "ping":
                    await manager.send_personal(websocket, {"type": "pong"})

            except asyncio.TimeoutError:
                await manager.send_personal(websocket, {"type": "keepalive"})

    except WebSocketDisconnect:
        logger.info(f"Portfolio updates disconnected for user: {user_id}")
    finally:
        await manager.disconnect(websocket, channel)


# ==================== BROADCAST FUNCTIONS ====================

async def broadcast_new_trade(trade_data: dict):
    """
    Broadcast a new congressional trade to all subscribers.

    Called by the trade ingestion system when new trades are detected.
    """
    message = {
        "type": "new_trade",
        **trade_data,
        "timestamp": datetime.utcnow().isoformat(),
    }
    await manager.broadcast("trades", message)


async def broadcast_market_update(symbol: str, quote_data: dict):
    """
    Broadcast a market update to symbol subscribers.

    Called by market data polling system.
    """
    message = {
        "type": "quote",
        "symbol": symbol,
        **quote_data,
        "timestamp": datetime.utcnow().isoformat(),
    }
    await manager.broadcast(f"market:{symbol}", message)


async def broadcast_portfolio_update(user_id: str, portfolio_data: dict):
    """
    Broadcast portfolio update to specific user.

    Called by portfolio calculation system.
    """
    message = {
        "type": "portfolio_update",
        **portfolio_data,
        "timestamp": datetime.utcnow().isoformat(),
    }
    await manager.broadcast(f"portfolio:{user_id}", message)


# ==================== ENHANCED ENDPOINTS ====================

@router.websocket("/events")
async def event_stream(
    websocket: WebSocket,
    token: Optional[str] = Query(None, description="Authentication token"),
):
    """
    Universal event stream endpoint.

    Streams all subscribed events to the client.

    Supports:
    - Real-time trade notifications
    - Price alerts
    - Activity alerts
    - System notifications

    Client messages:
    - {"action": "subscribe", "event_types": ["new_trade", "price_alert"]}
    - {"action": "unsubscribe"}
    - {"action": "ping"}
    - {"action": "add_price_alert", "symbol": "AAPL", "condition": "above", "target_price": 150.0}

    Server messages:
    - {"type": "event", "data": {...}}
    - {"type": "ack", "message_id": "..."}
    - {"type": "pong"}
    - {"type": "error", "message": "..."}
    """
    if not EVENTS_AVAILABLE:
        await websocket.close(code=4003, reason="Event system not available")
        return

    # Verify authentication
    user_id = None
    if token:
        try:
            user_id, _ = verify_token(token, token_type="access")
        except (ValueError, KeyError) as e:
            # Invalid token format or missing claims
            logger.warning(f"Invalid token format: {e}")
        except HTTPException as e:
            # Token expired or invalid
            logger.warning(f"Token verification failed: {e.detail}")

    # Connection ID
    subscriber_id = f"ws_{id(websocket)}"
    if user_id:
        subscriber_id = f"user_{user_id}_{id(websocket)}"

    await websocket.accept()

    # Send welcome message
    await websocket.send_json({
        "type": "connected",
        "subscriber_id": subscriber_id,
        "authenticated": user_id is not None,
        "timestamp": datetime.utcnow().isoformat()
    })

    # Event callback
    async def on_event(event: Event):
        """Handle incoming events"""
        try:
            if websocket.client_state == WebSocketState.CONNECTED:
                await websocket.send_json({
                    "type": "event",
                    "event": event.to_dict()
                })
        except (ConnectionError, OSError) as e:
            # Connection errors - client likely disconnected
            logger.info(f"Connection error sending event (client disconnected): {e}")
        except (ValueError, TypeError, AttributeError) as e:
            # Event serialization errors
            logger.error(f"Error serializing event: {e}", exc_info=True)

    try:
        # Subscribe to default events
        await event_broadcaster.subscribe(
            subscriber_id=subscriber_id,
            event_types=[EventType.SYSTEM_ALERT],
            callback=on_event,
            user_id=user_id
        )

        # Event loop
        while True:
            try:
                # Wait for client message
                data = await asyncio.wait_for(
                    websocket.receive_json(),
                    timeout=60.0
                )

                action = data.get("action")

                if action == "ping":
                    await websocket.send_json({"type": "pong"})

                elif action == "subscribe":
                    # Subscribe to event types
                    event_type_names = data.get("event_types", [])
                    event_types = []

                    for name in event_type_names:
                        try:
                            event_types.append(EventType(name))
                        except ValueError:
                            await websocket.send_json({
                                "type": "error",
                                "message": f"Invalid event type: {name}"
                            })

                    if event_types:
                        await event_broadcaster.subscribe(
                            subscriber_id=subscriber_id,
                            event_types=event_types,
                            callback=on_event,
                            user_id=user_id
                        )

                        await websocket.send_json({
                            "type": "subscribed",
                            "event_types": event_type_names
                        })

                elif action == "unsubscribe":
                    await event_broadcaster.unsubscribe(subscriber_id)
                    await websocket.send_json({
                        "type": "unsubscribed"
                    })

                elif action == "add_price_alert":
                    if not user_id:
                        await websocket.send_json({
                            "type": "error",
                            "message": "Authentication required for price alerts"
                        })
                        continue

                    try:
                        alert_id = await event_broadcaster.price_alerts.add_alert(
                            user_id=user_id,
                            symbol=data.get("symbol", "").upper(),
                            condition=data.get("condition"),
                            target_price=Decimal(str(data.get("target_price"))),
                            description=data.get("description")
                        )

                        await websocket.send_json({
                            "type": "alert_created",
                            "alert_id": alert_id
                        })

                        # Subscribe to price alerts if not already
                        await event_broadcaster.subscribe(
                            subscriber_id=subscriber_id,
                            event_types=[EventType.PRICE_ALERT],
                            callback=on_event,
                            user_id=user_id
                        )

                    except (ValueError, TypeError) as e:
                        # Invalid alert parameters
                        logger.warning(f"Invalid alert parameters: {e}")
                        await websocket.send_json({
                            "type": "error",
                            "message": f"Invalid alert parameters: {str(e)}"
                        })
                    except (ConnectionError, TimeoutError) as e:
                        # Alert service unavailable
                        logger.error(f"Alert service error: {e}")
                        await websocket.send_json({
                            "type": "error",
                            "message": "Alert service temporarily unavailable"
                        })

                elif action == "remove_price_alert":
                    if not user_id:
                        await websocket.send_json({
                            "type": "error",
                            "message": "Authentication required"
                        })
                        continue

                    alert_id = data.get("alert_id")
                    removed = await event_broadcaster.price_alerts.remove_alert(
                        user_id, alert_id
                    )

                    await websocket.send_json({
                        "type": "alert_removed" if removed else "error",
                        "alert_id": alert_id
                    })

                elif action == "list_alerts":
                    if not user_id:
                        await websocket.send_json({
                            "type": "error",
                            "message": "Authentication required"
                        })
                        continue

                    alerts = await event_broadcaster.price_alerts.get_user_alerts(user_id)
                    await websocket.send_json({
                        "type": "alerts_list",
                        "alerts": alerts
                    })

                else:
                    await websocket.send_json({
                        "type": "error",
                        "message": f"Unknown action: {action}"
                    })

            except asyncio.TimeoutError:
                # Send keepalive
                if websocket.client_state == WebSocketState.CONNECTED:
                    await websocket.send_json({
                        "type": "keepalive",
                        "timestamp": datetime.utcnow().isoformat()
                    })

    except WebSocketDisconnect:
        logger.info(f"Client disconnected: {subscriber_id}")
    except (ConnectionError, OSError) as e:
        logger.warning(f"WebSocket connection error for {subscriber_id}: {e}")
    except Exception as e:
        # Broad exception acceptable here: WebSocket endpoint should handle
        # all unexpected errors gracefully to avoid crashing the connection manager
        logger.error(
            f"Unexpected WebSocket error for {subscriber_id}: {e}",
            exc_info=True,
            extra={"subscriber_id": subscriber_id, "user_id": user_id}
        )
    finally:
        # Cleanup
        await event_broadcaster.unsubscribe(subscriber_id)


@router.websocket("/market-alerts/{symbol}")
async def market_alerts_stream(
    websocket: WebSocket,
    symbol: str,
    alert_on_change_percent: Optional[float] = Query(
        default=None,
        description="Alert on price change % (e.g., 5.0 for 5%)"
    ),
    interval: int = Query(default=5, ge=1, le=60),
    token: Optional[str] = Query(None)
):
    """
    Market data stream with automatic price change alerts.

    Monitors symbol and sends alerts on significant price changes.
    """
    if not MARKET_DATA_AVAILABLE or not EVENTS_AVAILABLE:
        await websocket.close(code=4003, reason="Required services not available")
        return

    symbol = symbol.upper()
    user_id = None

    if token:
        try:
            user_id, _ = verify_token(token, token_type="access")
        except Exception:
            pass

    await websocket.accept()

    # Welcome message
    await websocket.send_json({
        "type": "connected",
        "symbol": symbol,
        "alert_threshold": alert_on_change_percent,
        "interval": interval
    })

    previous_price: Optional[Decimal] = None
    subscriber_id = f"market_alert_{symbol}_{id(websocket)}"

    # Event callback for price alerts
    async def on_price_alert(event: Event):
        if websocket.client_state == WebSocketState.CONNECTED:
            await websocket.send_json({
                "type": "alert",
                "event": event.to_dict()
            })

    # Subscribe to price alerts for this symbol
    await event_broadcaster.subscribe(
        subscriber_id=subscriber_id,
        event_types=[EventType.PRICE_ALERT, EventType.SIGNIFICANT_MOVE],
        callback=on_price_alert,
        user_id=user_id
    )

    try:
        provider = get_market_data_provider(DataProvider.YAHOO_FINANCE)

        while True:
            try:
                # Fetch current quote
                quote = await provider.get_quote(symbol)
                current_price = Decimal(str(quote.price))

                # Check for significant price change
                if previous_price and alert_on_change_percent:
                    price_change_pct = abs(
                        (current_price - previous_price) / previous_price * 100
                    )

                    if price_change_pct >= alert_on_change_percent:
                        # Emit significant move event
                        event = Event(
                            type=EventType.SIGNIFICANT_MOVE,
                            data={
                                "symbol": symbol,
                                "previous_price": float(previous_price),
                                "current_price": float(current_price),
                                "change_percent": float(price_change_pct),
                                "message": f"{symbol} moved {price_change_pct:.2f}%"
                            },
                            priority=1
                        )
                        await event_broadcaster.broadcast(event, target_user_id=user_id)

                # Send quote update
                await websocket.send_json({
                    "type": "quote",
                    "symbol": symbol,
                    "price": float(current_price),
                    "change": quote.change,
                    "change_percent": quote.change_percent,
                    "volume": quote.volume,
                    "timestamp": datetime.utcnow().isoformat()
                })

                # Emit price update (will check all user alerts)
                await event_broadcaster.emit_price_update(
                    symbol=symbol,
                    current_price=current_price,
                    quote_data={
                        "change": quote.change,
                        "change_percent": quote.change_percent,
                        "volume": quote.volume
                    },
                    previous_price=previous_price
                )

                previous_price = current_price

            except Exception as e:
                logger.warning(f"Error fetching quote for {symbol}: {e}")
                await websocket.send_json({
                    "type": "error",
                    "message": f"Failed to fetch quote: {str(e)}"
                })

            await asyncio.sleep(interval)

    except WebSocketDisconnect:
        logger.info(f"Market alerts stream disconnected: {symbol}")
    finally:
        await event_broadcaster.unsubscribe(subscriber_id)


# ==================== REST ENDPOINTS FOR PRICE ALERTS ====================

if EVENTS_AVAILABLE:
    @router.post("/alerts/price")
    async def create_price_alert(
        alert: PriceAlertRequest,
        current_user: dict = Depends(get_current_user_optional)
    ):
        """
        Create a price alert (REST endpoint).

        The alert will trigger via WebSocket when condition is met.
        """
        if not current_user:
            raise HTTPException(status_code=401, detail="Authentication required")

        user_id = current_user["user_id"]

        alert_id = await event_broadcaster.price_alerts.add_alert(
            user_id=user_id,
            symbol=alert.symbol.upper(),
            condition=alert.condition,
            target_price=alert.target_price,
            description=alert.description
        )

        return {
            "alert_id": alert_id,
            "symbol": alert.symbol.upper(),
            "condition": alert.condition,
            "target_price": float(alert.target_price),
            "message": "Price alert created. Connect to WebSocket to receive notifications."
        }


    @router.get("/alerts/price")
    async def list_price_alerts(
        current_user: dict = Depends(get_current_user_optional)
    ):
        """List all price alerts for authenticated user"""
        if not current_user:
            raise HTTPException(status_code=401, detail="Authentication required")

        user_id = current_user["user_id"]
        alerts = await event_broadcaster.price_alerts.get_user_alerts(user_id)

        return {
            "alerts": alerts,
            "count": len(alerts)
        }


    @router.delete("/alerts/price/{alert_id}")
    async def delete_price_alert(
        alert_id: str,
        current_user: dict = Depends(get_current_user_optional)
    ):
        """Delete a price alert"""
        if not current_user:
            raise HTTPException(status_code=401, detail="Authentication required")

        user_id = current_user["user_id"]
        removed = await event_broadcaster.price_alerts.remove_alert(user_id, alert_id)

        if not removed:
            raise HTTPException(status_code=404, detail="Alert not found")

        return {"message": "Alert deleted successfully"}


    @router.get("/events/types")
    async def list_event_types():
        """List all available event types for subscription"""
        return {
            "event_types": [
                {
                    "name": event_type.value,
                    "description": _get_event_description(event_type)
                }
                for event_type in EventType
            ]
        }


    def _get_event_description(event_type: EventType) -> str:
        """Get human-readable description for event type"""
        descriptions = {
            EventType.NEW_TRADE: "New congressional trade disclosed",
            EventType.LARGE_TRADE: "Large trade detected (>$1M)",
            EventType.UNUSUAL_ACTIVITY: "Unusual trading pattern detected",
            EventType.PRICE_ALERT: "User-defined price alert triggered",
            EventType.PRICE_TARGET_HIT: "Price target reached",
            EventType.SIGNIFICANT_MOVE: "Significant price movement",
            EventType.PORTFOLIO_UPDATE: "Portfolio value updated",
            EventType.POSITION_CHANGE: "Position in portfolio changed",
            EventType.MARKET_OPEN: "Market opened",
            EventType.MARKET_CLOSE: "Market closed",
            EventType.MARKET_QUOTE: "Real-time market quote",
            EventType.SYSTEM_ALERT: "System notification",
            EventType.MAINTENANCE: "Scheduled maintenance notification"
        }
        return descriptions.get(event_type, "")


# ==================== STATUS ENDPOINT ====================

@router.get("/status")
async def websocket_status():
    """Get WebSocket connection statistics."""
    stats = {
        "total_connections": manager.get_total_connections(),
        "channels": {
            channel: len(connections)
            for channel, connections in manager.active_connections.items()
        },
    }

    # Add event system stats if available
    if EVENTS_AVAILABLE:
        stats.update({
            "event_subscribers": len(event_broadcaster.subscribers),
            "active_price_alerts": sum(
                len(symbol_alerts)
                for user_alerts in event_broadcaster.price_alerts.alerts.values()
                for symbol_alerts in user_alerts.values()
            ),
        })

    stats["timestamp"] = datetime.utcnow().isoformat()
    return stats
