"""
WebSocket endpoints for real-time updates.

Provides:
- Real-time market data streaming
- Trade notification broadcasts
- Portfolio updates
"""

import asyncio
import json
from datetime import datetime
from typing import Dict, Set, Optional
from uuid import UUID

from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Query, Depends
from starlette.websockets import WebSocketState

from app.core.logging import get_logger
from app.core.security import verify_token
from app.services.market_data import get_market_data_provider, DataProvider

logger = get_logger(__name__)

router = APIRouter(prefix="/ws", tags=["websocket"])


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
            except Exception as e:
                logger.warning(f"Failed to send message: {e}")
                disconnected.append(connection)

        # Clean up disconnected clients
        for conn in disconnected:
            await self.disconnect(conn, channel)

    async def send_personal(self, websocket: WebSocket, message: dict):
        """Send a message to a specific WebSocket."""
        try:
            if websocket.client_state == WebSocketState.CONNECTED:
                await websocket.send_json(message)
        except Exception as e:
            logger.warning(f"Failed to send personal message: {e}")

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

            except Exception as e:
                logger.warning(f"Error fetching quote for {symbol}: {e}")
                await manager.send_personal(websocket, {
                    "type": "error",
                    "message": f"Failed to fetch quote: {str(e)}",
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


# ==================== STATUS ENDPOINT ====================

@router.get("/status")
async def websocket_status():
    """Get WebSocket connection statistics."""
    return {
        "total_connections": manager.get_total_connections(),
        "channels": {
            channel: len(connections)
            for channel, connections in manager.active_connections.items()
        },
    }
