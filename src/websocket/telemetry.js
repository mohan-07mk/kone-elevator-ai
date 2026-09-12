/**
 * WebSocket Telemetry Manager
 */

const WS_BASE_URL =
  (import.meta.env && (import.meta.env.VITE_WS_URL || import.meta.env.VITE_WS_BASE_URL || import.meta.env.REACT_APP_WS_URL)) ||
  "wss://kone-elevator-ai-production.up.railway.app";

class TelemetryWebSocket {
  constructor(path) {
    this.path = path;
    this.socket = null;
    this.listeners = new Set();
    this.reconnectTimer = null;
    this.shouldReconnect = true;
  }

  connect() {
    if (this.socket && (this.socket.readyState === WebSocket.CONNECTING || this.socket.readyState === WebSocket.OPEN)) {
      return;
    }

    const url = `${WS_BASE_URL}${this.path}`;
    try {
      this.socket = new WebSocket(url);

      this.socket.onopen = () => {
        console.log(`[WebSocket Connected] ${this.path}`);
      };

      this.socket.onmessage = (event) => {
        try {
          const payload = JSON.parse(event.data);
          this.listeners.forEach((listener) => listener(payload));
        } catch (err) {
          console.error("Failed to parse WebSocket message:", err);
        }
      };

      this.socket.onerror = (err) => {
        console.warn(`[WebSocket Error] ${this.path}:`, err);
      };

      this.socket.onclose = () => {
        console.log(`[WebSocket Closed] ${this.path}`);
        if (this.shouldReconnect) {
          this.reconnectTimer = setTimeout(() => this.connect(), 2000);
        }
      };
    } catch (err) {
      console.error(`[WebSocket Exception] ${this.path}:`, err);
      if (this.shouldReconnect) {
        this.reconnectTimer = setTimeout(() => this.connect(), 3000);
      }
    }
  }

  subscribe(listener) {
    this.listeners.add(listener);
    if (!this.socket || this.socket.readyState === WebSocket.CLOSED) {
      this.connect();
    }
    return () => {
      this.listeners.delete(listener);
      if (this.listeners.size === 0) {
        this.disconnect();
      }
    };
  }

  disconnect() {
    this.shouldReconnect = false;
    if (this.reconnectTimer) {
      clearTimeout(this.reconnectTimer);
      this.reconnectTimer = null;
    }
    if (this.socket) {
      this.socket.close();
      this.socket = null;
    }
  }
}

// Map of active elevator WebSocket connections
const elevatorSockets = new Map();
let fleetSocket = null;

export function connectElevatorTelemetry(elevatorId, onMessage) {
  if (!elevatorSockets.has(elevatorId)) {
    elevatorSockets.set(elevatorId, new TelemetryWebSocket(`/ws/elevators/${elevatorId}`));
  }
  const instance = elevatorSockets.get(elevatorId);
  return instance.subscribe(onMessage);
}

export function connectFleetTelemetry(onMessage) {
  if (!fleetSocket) {
    fleetSocket = new TelemetryWebSocket("/ws/fleet");
  }
  return fleetSocket.subscribe(onMessage);
}
