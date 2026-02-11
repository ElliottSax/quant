# WebSocket Real-Time Updates - Complete Guide

**Version**: 2.0
**Last Updated**: January 28, 2026

---

## 📡 Overview

The Quant Trading Platform provides comprehensive WebSocket support for real-time updates:

- **Real-time market data streaming**
- **Congressional trade notifications**
- **Price alerts with custom triggers**
- **Activity monitoring and pattern detection**
- **Portfolio updates**
- **Automatic reconnection**

---

## 🚀 Quick Start

### JavaScript Client

```javascript
// Include the client library
<script src="/websocket-client.js"></script>

// Create client
const client = new QuantWebSocket('wss://api.yourdomain.com/api/v1/ws/v2/events', {
  token: 'your-jwt-token',  // Optional
  onEvent: (event) => {
    console.log('Event received:', event);
  },
  onConnect: () => {
    console.log('Connected!');
  },
  onDisconnect: () => {
    console.log('Disconnected');
  }
});

// Connect
client.connect();

// Subscribe to events
client.subscribe(['new_trade', 'price_alert', 'large_trade']);

// Add price alert
client.addPriceAlert('AAPL', 'above', 150.0);
```

### Python Client

```python
import asyncio
import websockets
import json

async def listen_to_events():
    uri = "wss://api.yourdomain.com/api/v1/ws/v2/events?token=your-jwt-token"

    async with websockets.connect(uri) as websocket:
        # Subscribe to events
        await websocket.send(json.dumps({
            "action": "subscribe",
            "event_types": ["new_trade", "price_alert"]
        }))

        # Listen for events
        async for message in websocket:
            data = json.loads(message)
            print(f"Received: {data}")

asyncio.run(listen_to_events())
```

### cURL (Testing)

```bash
# Test connection (requires websocat or similar)
websocat "wss://api.yourdomain.com/api/v1/ws/v2/events?token=YOUR_TOKEN"

# Once connected, send:
{"action": "subscribe", "event_types": ["new_trade"]}
```

---

## 📍 WebSocket Endpoints

### 1. Universal Event Stream

**Endpoint**: `/api/v1/ws/v2/events`

**Description**: Primary endpoint for all event types.

**Query Parameters**:
- `token` (optional): JWT authentication token

**Features**:
- Subscribe to multiple event types
- Create/manage price alerts
- Receive all notifications
- Automatic keepalive

**Example**:
```javascript
const ws = new WebSocket('wss://api.example.com/api/v1/ws/v2/events?token=xxx');

ws.onmessage = (event) => {
  const data = JSON.parse(event.data);
  console.log(data);
};
```

### 2. Market Data Stream (Legacy)

**Endpoint**: `/api/v1/ws/market/{symbol}`

**Query Parameters**:
- `interval` (optional): Update interval in seconds (1-60, default: 5)

**Example**:
```javascript
const ws = new WebSocket('wss://api.example.com/api/v1/ws/market/AAPL?interval=10');
```

### 3. Market Alerts Stream

**Endpoint**: `/api/v1/ws/v2/market-alerts/{symbol}`

**Query Parameters**:
- `alert_on_change_percent` (optional): Alert on price change % (e.g., 5.0)
- `interval` (optional): Update interval in seconds (1-60)
- `token` (optional): JWT token

**Features**:
- Real-time quotes
- Automatic price change detection
- Alert on significant moves

**Example**:
```javascript
// Alert on 5% price changes
const ws = new WebSocket('wss://api.example.com/api/v1/ws/v2/market-alerts/AAPL?alert_on_change_percent=5.0');
```

### 4. Trade Notifications

**Endpoint**: `/api/v1/ws/trades`

**Query Parameters**:
- `token` (optional): JWT token for personalized notifications

**Example**:
```javascript
const ws = new WebSocket('wss://api.example.com/api/v1/ws/trades?token=xxx');
```

### 5. Portfolio Updates

**Endpoint**: `/api/v1/ws/portfolio/{user_id}`

**Query Parameters**:
- `token` (required): JWT authentication token

**Authentication**: Required - must match user_id

**Example**:
```javascript
const ws = new WebSocket('wss://api.example.com/api/v1/ws/portfolio/user123?token=xxx');
```

---

## 📨 Message Formats

### Client → Server

#### Subscribe to Events
```json
{
  "action": "subscribe",
  "event_types": ["new_trade", "price_alert", "large_trade"]
}
```

#### Unsubscribe from All Events
```json
{
  "action": "unsubscribe"
}
```

#### Ping (Keepalive)
```json
{
  "action": "ping"
}
```

#### Create Price Alert
```json
{
  "action": "add_price_alert",
  "symbol": "AAPL",
  "condition": "above",
  "target_price": 150.0,
  "description": "Optional description"
}
```

**Alert Conditions**:
- `above`: Trigger when price goes above target
- `below`: Trigger when price goes below target
- `percent_change`: Trigger on % change from current price

#### Remove Price Alert
```json
{
  "action": "remove_price_alert",
  "alert_id": "alert_id_here"
}
```

#### List Price Alerts
```json
{
  "action": "list_alerts"
}
```

### Server → Client

#### Welcome Message
```json
{
  "type": "connected",
  "subscriber_id": "user_123_456789",
  "authenticated": true,
  "timestamp": "2026-01-28T12:00:00Z"
}
```

#### Event
```json
{
  "type": "event",
  "event": {
    "type": "new_trade",
    "data": {
      "politician": "John Doe",
      "ticker": "AAPL",
      "transaction_type": "buy",
      "amount": "$50,001 - $100,000",
      "disclosure_date": "2026-01-28"
    },
    "timestamp": "2026-01-28T12:00:00Z",
    "priority": 0
  }
}
```

#### Price Alert Triggered
```json
{
  "type": "event",
  "event": {
    "type": "price_alert",
    "data": {
      "alert_id": "alert_123",
      "user_id": "user_456",
      "symbol": "AAPL",
      "condition": "above",
      "target_price": 150.0,
      "current_price": 150.25,
      "message": "AAPL above $150.0"
    },
    "timestamp": "2026-01-28T12:00:00Z",
    "priority": 1
  }
}
```

#### Pong Response
```json
{
  "type": "pong"
}
```

#### Keepalive
```json
{
  "type": "keepalive",
  "timestamp": "2026-01-28T12:00:00Z"
}
```

#### Subscription Confirmed
```json
{
  "type": "subscribed",
  "event_types": ["new_trade", "price_alert"]
}
```

#### Alert Created
```json
{
  "type": "alert_created",
  "alert_id": "alert_123"
}
```

#### Error
```json
{
  "type": "error",
  "message": "Error description here"
}
```

---

## 🔔 Event Types

### Trade Events

#### `new_trade`
New congressional trade disclosed

```json
{
  "type": "new_trade",
  "data": {
    "politician": "John Doe",
    "ticker": "AAPL",
    "transaction_type": "buy",
    "amount": "$15,001 - $50,000",
    "disclosure_date": "2026-01-28",
    "transaction_date": "2026-01-20"
  }
}
```

#### `large_trade`
Large trade detected (>$1M)

```json
{
  "type": "large_trade",
  "data": {
    "politician": "Jane Smith",
    "symbol": "TSLA",
    "amount": "$1,000,001 - $5,000,000",
    "amount_value": 2500000,
    "transaction_type": "sell",
    "message": "Large sell by Jane Smith: TSLA ($1M-$5M)"
  }
}
```

#### `unusual_activity`
Unusual trading pattern detected

```json
{
  "type": "unusual_activity",
  "data": {
    "pattern": "clustering",
    "politician": "John Doe",
    "symbol": "AAPL",
    "trade_count": 5,
    "period_days": 7,
    "message": "Unusual activity: John Doe made 5 trades in AAPL within 7 days"
  }
}
```

### Price Events

#### `price_alert`
User-defined price alert triggered

```json
{
  "type": "price_alert",
  "data": {
    "alert_id": "alert_123",
    "user_id": "user_456",
    "symbol": "AAPL",
    "condition": "above",
    "target_price": 150.0,
    "current_price": 150.25
  }
}
```

#### `significant_move`
Significant price movement detected

```json
{
  "type": "significant_move",
  "data": {
    "symbol": "TSLA",
    "previous_price": 200.0,
    "current_price": 210.5,
    "change_percent": 5.25,
    "message": "TSLA moved 5.25%"
  }
}
```

#### `market_quote`
Real-time market quote update

```json
{
  "type": "market_quote",
  "data": {
    "symbol": "AAPL",
    "price": 150.25,
    "change": 1.50,
    "change_percent": 1.01,
    "volume": 50000000
  }
}
```

### Portfolio Events

#### `portfolio_update`
Portfolio value updated

```json
{
  "type": "portfolio_update",
  "data": {
    "user_id": "user_123",
    "total_value": 100000.00,
    "daily_change": 1500.00,
    "daily_change_percent": 1.52
  }
}
```

### Market Events

#### `market_open`
Market opened for trading

```json
{
  "type": "market_open",
  "data": {
    "message": "Market is now open",
    "open_time": "09:30:00"
  }
}
```

#### `market_close`
Market closed for trading

```json
{
  "type": "market_close",
  "data": {
    "message": "Market is now closed",
    "close_time": "16:00:00"
  }
}
```

### System Events

#### `system_alert`
System notification

```json
{
  "type": "system_alert",
  "data": {
    "message": "System maintenance scheduled for tonight at 2 AM UTC"
  }
}
```

---

## 🔐 Authentication

### With Token (Recommended)

```javascript
// Pass token in query parameter
const ws = new WebSocket('wss://api.example.com/api/v1/ws/v2/events?token=YOUR_JWT_TOKEN');
```

### Without Token (Limited Features)

```javascript
// Connect without authentication
const ws = new WebSocket('wss://api.example.com/api/v1/ws/v2/events');

// Can still receive public events
// Cannot create price alerts or receive personalized notifications
```

---

## 🔄 Reconnection Logic

The JavaScript client automatically handles reconnections:

- **Exponential Backoff**: Increasing delay between reconnection attempts
- **Max Attempts**: 10 attempts (configurable)
- **State Preservation**: Re-subscribes to events after reconnection
- **Message Queue**: Queues messages sent while disconnected

```javascript
const client = new QuantWebSocket(url, {
  reconnectInterval: 3000,      // Initial delay: 3s
  maxReconnectAttempts: 10      // Max attempts
});
```

**Reconnection Schedule**:
1. Attempt 1: 3s delay
2. Attempt 2: 6s delay
3. Attempt 3: 12s delay
4. Attempt 4: 24s delay
5. Attempt 5+: 30s delay (capped)

---

## 📊 REST API Endpoints

### Create Price Alert (REST)

```http
POST /api/v1/ws/v2/alerts/price
Authorization: Bearer YOUR_JWT_TOKEN

{
  "symbol": "AAPL",
  "condition": "above",
  "target_price": 150.0,
  "description": "Alert when AAPL hits $150"
}
```

**Response**:
```json
{
  "alert_id": "alert_123",
  "symbol": "AAPL",
  "condition": "above",
  "target_price": 150.0,
  "message": "Price alert created. Connect to WebSocket to receive notifications."
}
```

### List Price Alerts

```http
GET /api/v1/ws/v2/alerts/price
Authorization: Bearer YOUR_JWT_TOKEN
```

**Response**:
```json
{
  "alerts": [
    {
      "id": "alert_123",
      "symbol": "AAPL",
      "condition": "above",
      "target_price": 150.0,
      "created_at": "2026-01-28T10:00:00Z",
      "triggered": false
    }
  ],
  "count": 1
}
```

### Delete Price Alert

```http
DELETE /api/v1/ws/v2/alerts/price/alert_123
Authorization: Bearer YOUR_JWT_TOKEN
```

### List Event Types

```http
GET /api/v1/ws/v2/events/types
```

**Response**:
```json
{
  "event_types": [
    {
      "name": "new_trade",
      "description": "New congressional trade disclosed"
    },
    {
      "name": "price_alert",
      "description": "User-defined price alert triggered"
    }
  ]
}
```

### WebSocket Statistics

```http
GET /api/v1/ws/v2/stats
```

**Response**:
```json
{
  "websocket_connections": 42,
  "channels": {
    "trades": 10,
    "market:AAPL": 5
  },
  "event_subscribers": 15,
  "active_price_alerts": 23,
  "timestamp": "2026-01-28T12:00:00Z"
}
```

---

## 💡 Usage Examples

### Example 1: Real-Time Trade Notifications

```javascript
const client = new QuantWebSocket('wss://api.example.com/api/v1/ws/v2/events');

client.onEvent = (event) => {
  if (event.type === 'new_trade') {
    console.log(`New trade: ${event.data.politician} bought ${event.data.ticker}`);
    showNotification(event.data);
  }
};

client.connect();
client.subscribe(['new_trade', 'large_trade']);
```

### Example 2: Price Alert Dashboard

```javascript
const client = new QuantWebSocket('wss://api.example.com/api/v1/ws/v2/events', {
  token: userToken
});

// Add alerts for multiple symbols
const symbols = ['AAPL', 'TSLA', 'MSFT'];
symbols.forEach(symbol => {
  client.addPriceAlert(symbol, 'percent_change', 5.0);
});

// Handle alerts
client.onEvent = (event) => {
  if (event.type === 'price_alert') {
    displayAlert({
      symbol: event.data.symbol,
      price: event.data.current_price,
      message: event.data.message
    });
  }
};

client.connect();
client.subscribe(['price_alert', 'significant_move']);
```

### Example 3: Portfolio Monitor

```javascript
const client = new QuantWebSocket(`wss://api.example.com/api/v1/ws/portfolio/${userId}`, {
  token: userToken
});

client.onEvent = (event) => {
  if (event.type === 'portfolio_update') {
    updatePortfolioDisplay({
      value: event.data.total_value,
      change: event.data.daily_change
    });
  }
};

client.connect();
```

### Example 4: Activity Monitor

```javascript
const client = new QuantWebSocket('wss://api.example.com/api/v1/ws/v2/events');

client.onEvent = (event) => {
  switch (event.type) {
    case 'unusual_activity':
      highlightPolitician(event.data.politician);
      showAlert(`Unusual activity detected: ${event.data.message}`);
      break;

    case 'large_trade':
      addToActivityFeed(event.data);
      break;
  }
};

client.connect();
client.subscribe(['unusual_activity', 'large_trade']);
```

---

## 🔍 Monitoring & Debugging

### Check Connection State

```javascript
const state = client.getState();
console.log('Connected:', state.connected);
console.log('Reconnect attempts:', state.reconnectAttempts);
console.log('Subscribed to:', state.subscribedEvents);
console.log('Queued messages:', state.queuedMessages);
```

### Enable Debug Logging

```javascript
const client = new QuantWebSocket(url, {
  onError: (error) => {
    console.error('WebSocket error:', error);
  }
});
```

### Server-Side Monitoring

```bash
# Get WebSocket statistics
curl https://api.example.com/api/v1/ws/v2/stats

# Get legacy WebSocket status
curl https://api.example.com/api/v1/ws/status
```

---

## ⚠️ Best Practices

1. **Always Handle Reconnections**: Network issues are common; use automatic reconnection
2. **Implement Exponential Backoff**: Don't hammer the server with reconnect attempts
3. **Keep Connections Alive**: Send periodic pings (client does this automatically)
4. **Handle All Message Types**: Don't assume you'll only get events
5. **Validate Data**: Always validate incoming event data
6. **Secure Tokens**: Never expose JWT tokens in client-side code
7. **Limit Subscriptions**: Only subscribe to events you need
8. **Clean Up**: Disconnect when user navigates away

```javascript
// Cleanup on page unload
window.addEventListener('beforeunload', () => {
  client.disconnect();
});
```

---

## 🐛 Troubleshooting

### Connection Refused

**Issue**: Cannot establish WebSocket connection

**Solutions**:
- Check WebSocket URL (must start with `ws://` or `wss://`)
- Verify server is running and accessible
- Check firewall/proxy settings
- Ensure SSL certificate is valid (for `wss://`)

### Authentication Failed

**Issue**: Connection closes immediately with code 4001

**Solutions**:
- Verify JWT token is valid and not expired
- Check token is passed in query parameter correctly
- Ensure user_id matches token for portfolio endpoints

### No Events Received

**Issue**: Connected but no events arrive

**Solutions**:
- Verify you've subscribed to event types
- Check server logs for errors
- Confirm events are being generated (check REST API)
- Test with simple ping/pong

### Frequent Disconnections

**Issue**: Connection drops repeatedly

**Solutions**:
- Check network stability
- Increase ping interval
- Review server resource limits
- Check for proxy/load balancer timeouts

---

## 📚 Additional Resources

- **API Documentation**: https://api.example.com/api/v1/docs
- **Client Library**: `/websocket-client.js`
- **Server Implementation**: `app/api/v1/websocket_enhanced.py`
- **Event System**: `app/services/websocket_events.py`

---

## 🔄 Version History

### v2.0 (2026-01-28)
- Added enhanced event system
- Implemented price alerts
- Added activity monitoring
- Automatic reconnection support
- REST API for alert management

### v1.0 (2025-11-10)
- Initial WebSocket implementation
- Basic market data streaming
- Trade notifications
- Portfolio updates

---

**Last Updated**: January 28, 2026
