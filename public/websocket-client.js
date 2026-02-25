/**
 * WebSocket Client with Automatic Reconnection
 *
 * Usage:
 *   const client = new QunatWebSocket('wss://api.example.com/api/v1/ws/v2/events', {
 *     token: 'your-jwt-token',
 *     onEvent: (event) => console.log('Received event:', event),
 *     onConnect: () => console.log('Connected'),
 *     onDisconnect: () => console.log('Disconnected')
 *   });
 *
 *   client.connect();
 *   client.subscribe(['new_trade', 'price_alert']);
 *   client.addPriceAlert('AAPL', 'above', 150.0);
 */

class QuantWebSocket {
  constructor(url, options = {}) {
    this.url = url;
    this.token = options.token || null;
    this.onEvent = options.onEvent || (() => {});
    this.onConnect = options.onConnect || (() => {});
    this.onDisconnect = options.onDisconnect || (() => {});
    this.onError = options.onError || ((error) => console.error('WebSocket error:', error));

    // Reconnection settings
    this.reconnectInterval = options.reconnectInterval || 3000; // 3 seconds
    this.maxReconnectAttempts = options.maxReconnectAttempts || 10;
    this.reconnectAttempts = 0;

    // State
    this.ws = null;
    this.isConnected = false;
    this.reconnectTimer = null;
    this.pingInterval = null;
    this.subscribedEvents = [];
    this.messageQueue = [];
  }

  /**
   * Build WebSocket URL with query parameters
   */
  buildUrl() {
    const url = new URL(this.url);
    if (this.token) {
      url.searchParams.set('token', this.token);
    }
    return url.toString();
  }

  /**
   * Connect to WebSocket server
   */
  connect() {
    if (this.ws && this.isConnected) {
      console.log('Already connected');
      return;
    }

    console.log('Connecting to WebSocket...');

    try {
      this.ws = new WebSocket(this.buildUrl());

      this.ws.onopen = this.handleOpen.bind(this);
      this.ws.onclose = this.handleClose.bind(this);
      this.ws.onerror = this.handleError.bind(this);
      this.ws.onmessage = this.handleMessage.bind(this);

    } catch (error) {
      console.error('Failed to create WebSocket:', error);
      this.scheduleReconnect();
    }
  }

  /**
   * Disconnect from WebSocket server
   */
  disconnect() {
    console.log('Disconnecting...');

    this.clearReconnectTimer();
    this.clearPingInterval();

    if (this.ws) {
      this.ws.close(1000, 'Client disconnect');
      this.ws = null;
    }

    this.isConnected = false;
  }

  /**
   * Handle WebSocket open event
   */
  handleOpen(event) {
    console.log('WebSocket connected');
    this.isConnected = true;
    this.reconnectAttempts = 0;

    // Start ping interval (every 30 seconds)
    this.startPingInterval();

    // Process queued messages
    this.processMessageQueue();

    // Re-subscribe to events
    if (this.subscribedEvents.length > 0) {
      this.subscribe(this.subscribedEvents);
    }

    // Call user callback
    this.onConnect();
  }

  /**
   * Handle WebSocket close event
   */
  handleClose(event) {
    console.log('WebSocket closed:', event.code, event.reason);
    this.isConnected = false;
    this.clearPingInterval();

    // Call user callback
    this.onDisconnect();

    // Attempt reconnection if not intentional close
    if (event.code !== 1000) {
      this.scheduleReconnect();
    }
  }

  /**
   * Handle WebSocket error event
   */
  handleError(error) {
    console.error('WebSocket error:', error);
    this.onError(error);
  }

  /**
   * Handle incoming WebSocket message
   */
  handleMessage(event) {
    try {
      const message = JSON.parse(event.data);

      // Handle different message types
      switch (message.type) {
        case 'connected':
          console.log('Received welcome message:', message);
          break;

        case 'event':
          // User event
          this.onEvent(message.event);
          break;

        case 'pong':
          // Pong response
          console.debug('Received pong');
          break;

        case 'keepalive':
          // Keepalive message
          console.debug('Received keepalive');
          break;

        case 'subscribed':
          console.log('Subscribed to:', message.event_types);
          break;

        case 'unsubscribed':
          console.log('Unsubscribed from all events');
          this.subscribedEvents = [];
          break;

        case 'alert_created':
          console.log('Price alert created:', message.alert_id);
          break;

        case 'alert_removed':
          console.log('Price alert removed:', message.alert_id);
          break;

        case 'alerts_list':
          console.log('Price alerts:', message.alerts);
          break;

        case 'error':
          console.error('Server error:', message.message);
          this.onError(new Error(message.message));
          break;

        default:
          console.warn('Unknown message type:', message.type);
      }

    } catch (error) {
      console.error('Failed to parse message:', error);
    }
  }

  /**
   * Send message to server
   */
  send(message) {
    if (!this.isConnected || !this.ws) {
      console.warn('Not connected, queueing message');
      this.messageQueue.push(message);
      return;
    }

    try {
      this.ws.send(JSON.stringify(message));
    } catch (error) {
      console.error('Failed to send message:', error);
      this.messageQueue.push(message);
    }
  }

  /**
   * Process queued messages
   */
  processMessageQueue() {
    while (this.messageQueue.length > 0) {
      const message = this.messageQueue.shift();
      this.send(message);
    }
  }

  /**
   * Subscribe to event types
   */
  subscribe(eventTypes) {
    if (!Array.isArray(eventTypes)) {
      eventTypes = [eventTypes];
    }

    this.subscribedEvents = [...new Set([...this.subscribedEvents, ...eventTypes])];

    this.send({
      action: 'subscribe',
      event_types: eventTypes
    });
  }

  /**
   * Unsubscribe from all events
   */
  unsubscribe() {
    this.send({
      action: 'unsubscribe'
    });
  }

  /**
   * Add a price alert
   */
  addPriceAlert(symbol, condition, targetPrice, description = null) {
    this.send({
      action: 'add_price_alert',
      symbol: symbol.toUpperCase(),
      condition: condition,
      target_price: targetPrice,
      description: description
    });
  }

  /**
   * Remove a price alert
   */
  removePriceAlert(alertId) {
    this.send({
      action: 'remove_price_alert',
      alert_id: alertId
    });
  }

  /**
   * List all price alerts
   */
  listAlerts() {
    this.send({
      action: 'list_alerts'
    });
  }

  /**
   * Send ping to server
   */
  ping() {
    this.send({
      action: 'ping'
    });
  }

  /**
   * Start ping interval
   */
  startPingInterval() {
    this.clearPingInterval();

    this.pingInterval = setInterval(() => {
      if (this.isConnected) {
        this.ping();
      }
    }, 30000); // Every 30 seconds
  }

  /**
   * Clear ping interval
   */
  clearPingInterval() {
    if (this.pingInterval) {
      clearInterval(this.pingInterval);
      this.pingInterval = null;
    }
  }

  /**
   * Schedule reconnection attempt
   */
  scheduleReconnect() {
    if (this.reconnectAttempts >= this.maxReconnectAttempts) {
      console.error('Max reconnection attempts reached');
      this.onError(new Error('Failed to reconnect after maximum attempts'));
      return;
    }

    this.reconnectAttempts++;

    // Exponential backoff
    const delay = Math.min(
      this.reconnectInterval * Math.pow(2, this.reconnectAttempts - 1),
      30000 // Max 30 seconds
    );

    console.log(`Reconnecting in ${delay}ms (attempt ${this.reconnectAttempts}/${this.maxReconnectAttempts})`);

    this.reconnectTimer = setTimeout(() => {
      this.connect();
    }, delay);
  }

  /**
   * Clear reconnection timer
   */
  clearReconnectTimer() {
    if (this.reconnectTimer) {
      clearTimeout(this.reconnectTimer);
      this.reconnectTimer = null;
    }
  }

  /**
   * Get connection state
   */
  getState() {
    return {
      connected: this.isConnected,
      reconnectAttempts: this.reconnectAttempts,
      subscribedEvents: this.subscribedEvents,
      queuedMessages: this.messageQueue.length
    };
  }
}

// Export for use in browser or Node.js
if (typeof module !== 'undefined' && module.exports) {
  module.exports = QuantWebSocket;
}
