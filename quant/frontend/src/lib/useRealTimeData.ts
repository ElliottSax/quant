"use client";

import { useState, useEffect, useCallback, useRef } from 'react';

interface RealTimeConfig {
  url: string;
  interval?: number; // Polling interval in ms
  enabled?: boolean;
  onData?: (data: any) => void;
  onError?: (error: Error) => void;
  transform?: (data: any) => any;
}

interface RealTimeState<T> {
  data: T | null;
  isConnected: boolean;
  isLoading: boolean;
  error: Error | null;
  lastUpdate: Date | null;
}

/**
 * Hook for real-time data streaming with WebSocket support and polling fallback
 */
export function useRealTimeData<T = any>(config: RealTimeConfig): RealTimeState<T> & {
  connect: () => void;
  disconnect: () => void;
  refresh: () => Promise<void>;
} {
  const {
    url,
    interval = 5000,
    enabled = true,
    onData,
    onError,
    transform,
  } = config;

  const [state, setState] = useState<RealTimeState<T>>({
    data: null,
    isConnected: false,
    isLoading: false,
    error: null,
    lastUpdate: null,
  });

  const wsRef = useRef<WebSocket | null>(null);
  const pollingRef = useRef<NodeJS.Timeout | null>(null);
  const mountedRef = useRef(true);

  // Fetch data via HTTP (polling fallback)
  const fetchData = useCallback(async () => {
    if (!mountedRef.current) return;

    setState((prev) => ({ ...prev, isLoading: true }));

    try {
      const response = await fetch(url);
      if (!response.ok) {
        throw new Error(`HTTP ${response.status}: ${response.statusText}`);
      }

      let data = await response.json();
      if (transform) {
        data = transform(data);
      }

      if (mountedRef.current) {
        setState((prev) => ({
          ...prev,
          data,
          isLoading: false,
          error: null,
          lastUpdate: new Date(),
        }));
        onData?.(data);
      }
    } catch (error) {
      const err = error instanceof Error ? error : new Error(String(error));
      if (mountedRef.current) {
        setState((prev) => ({
          ...prev,
          isLoading: false,
          error: err,
        }));
        onError?.(err);
      }
    }
  }, [url, transform, onData, onError]);

  // Connect to WebSocket
  const connectWebSocket = useCallback(() => {
    if (!url.startsWith('ws://') && !url.startsWith('wss://')) {
      // Use polling for HTTP URLs
      return false;
    }

    try {
      const ws = new WebSocket(url);

      ws.onopen = () => {
        if (mountedRef.current) {
          setState((prev) => ({ ...prev, isConnected: true, error: null }));
        }
      };

      ws.onmessage = (event) => {
        if (!mountedRef.current) return;

        try {
          let data = JSON.parse(event.data);
          if (transform) {
            data = transform(data);
          }

          setState((prev) => ({
            ...prev,
            data,
            lastUpdate: new Date(),
          }));
          onData?.(data);
        } catch (error) {
          console.error('Failed to parse WebSocket message:', error);
        }
      };

      ws.onerror = (event) => {
        const err = new Error('WebSocket connection error');
        if (mountedRef.current) {
          setState((prev) => ({ ...prev, error: err }));
          onError?.(err);
        }
      };

      ws.onclose = () => {
        if (mountedRef.current) {
          setState((prev) => ({ ...prev, isConnected: false }));
        }
        wsRef.current = null;
      };

      wsRef.current = ws;
      return true;
    } catch (error) {
      return false;
    }
  }, [url, transform, onData, onError]);

  // Start polling
  const startPolling = useCallback(() => {
    if (pollingRef.current) {
      clearInterval(pollingRef.current);
    }

    // Initial fetch
    fetchData();

    // Set up polling interval
    pollingRef.current = setInterval(fetchData, interval);

    setState((prev) => ({ ...prev, isConnected: true }));
  }, [fetchData, interval]);

  // Stop polling
  const stopPolling = useCallback(() => {
    if (pollingRef.current) {
      clearInterval(pollingRef.current);
      pollingRef.current = null;
    }
    setState((prev) => ({ ...prev, isConnected: false }));
  }, []);

  // Connect
  const connect = useCallback(() => {
    // Try WebSocket first
    const wsConnected = connectWebSocket();
    if (!wsConnected) {
      // Fall back to polling
      startPolling();
    }
  }, [connectWebSocket, startPolling]);

  // Disconnect
  const disconnect = useCallback(() => {
    if (wsRef.current) {
      wsRef.current.close();
      wsRef.current = null;
    }
    stopPolling();
  }, [stopPolling]);

  // Manual refresh
  const refresh = useCallback(async () => {
    await fetchData();
  }, [fetchData]);

  // Effect to manage connection lifecycle
  useEffect(() => {
    mountedRef.current = true;

    if (enabled) {
      connect();
    }

    return () => {
      mountedRef.current = false;
      disconnect();
    };
  }, [enabled, connect, disconnect]);

  return {
    ...state,
    connect,
    disconnect,
    refresh,
  };
}

/**
 * Hook for simulated real-time data (useful for demos)
 */
export function useSimulatedRealTime<T>(
  initialData: T,
  updateFn: (data: T) => T,
  interval = 1000
): T {
  const [data, setData] = useState<T>(initialData);

  useEffect(() => {
    const timer = setInterval(() => {
      setData((prev) => updateFn(prev));
    }, interval);

    return () => clearInterval(timer);
  }, [updateFn, interval]);

  return data;
}

/**
 * Hook for tracking data stream statistics
 */
export function useStreamStats(enabled = true) {
  const [stats, setStats] = useState({
    messagesReceived: 0,
    bytesReceived: 0,
    avgLatency: 0,
    uptime: 0,
    lastMessage: null as Date | null,
  });

  const startTimeRef = useRef(Date.now());
  const latenciesRef = useRef<number[]>([]);

  const recordMessage = useCallback((byteSize: number, latency?: number) => {
    if (latency !== undefined) {
      latenciesRef.current.push(latency);
      if (latenciesRef.current.length > 100) {
        latenciesRef.current.shift();
      }
    }

    setStats((prev) => ({
      ...prev,
      messagesReceived: prev.messagesReceived + 1,
      bytesReceived: prev.bytesReceived + byteSize,
      avgLatency:
        latenciesRef.current.length > 0
          ? latenciesRef.current.reduce((a, b) => a + b, 0) / latenciesRef.current.length
          : 0,
      lastMessage: new Date(),
    }));
  }, []);

  // Update uptime
  useEffect(() => {
    if (!enabled) return;

    const timer = setInterval(() => {
      setStats((prev) => ({
        ...prev,
        uptime: Math.floor((Date.now() - startTimeRef.current) / 1000),
      }));
    }, 1000);

    return () => clearInterval(timer);
  }, [enabled]);

  const reset = useCallback(() => {
    startTimeRef.current = Date.now();
    latenciesRef.current = [];
    setStats({
      messagesReceived: 0,
      bytesReceived: 0,
      avgLatency: 0,
      uptime: 0,
      lastMessage: null,
    });
  }, []);

  return { stats, recordMessage, reset };
}
