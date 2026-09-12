"""Connection manager for WebSocket telemetry broadcasts."""

from __future__ import annotations

import logging
from typing import Any
from fastapi import WebSocket

logger = logging.getLogger("elevator_ai.websockets")


class ConnectionManager:
    """Manages active WebSocket connections for elevators and fleet."""

    def __init__(self) -> None:
        # elevator_id -> list[WebSocket]
        self._elevator_connections: dict[str, list[WebSocket]] = {}
        # fleet subscribers -> list[WebSocket]
        self._fleet_connections: list[WebSocket] = []

    async def connect_elevator(self, websocket: WebSocket, elevator_id: str) -> None:
        await websocket.accept()
        if elevator_id not in self._elevator_connections:
            self._elevator_connections[elevator_id] = []
        self._elevator_connections[elevator_id].append(websocket)
        logger.info("WebSocket client connected to elevator '%s'", elevator_id)

    def disconnect_elevator(self, websocket: WebSocket, elevator_id: str) -> None:
        if elevator_id in self._elevator_connections:
            if websocket in self._elevator_connections[elevator_id]:
                self._elevator_connections[elevator_id].remove(websocket)
            if not self._elevator_connections[elevator_id]:
                del self._elevator_connections[elevator_id]
        logger.info("WebSocket client disconnected from elevator '%s'", elevator_id)

    async def connect_fleet(self, websocket: WebSocket) -> None:
        await websocket.accept()
        self._fleet_connections.append(websocket)
        logger.info("WebSocket client connected to fleet stream")

    def disconnect_fleet(self, websocket: WebSocket) -> None:
        if websocket in self._fleet_connections:
            self._fleet_connections.remove(websocket)
        logger.info("WebSocket client disconnected from fleet stream")

    async def broadcast_elevator_telemetry(self, elevator_id: str, data: dict[str, Any]) -> None:
        """Broadcast telemetry frame to elevator subscribers and fleet subscribers."""
        payload = {
            "type": "telemetry",
            "elevator_id": elevator_id,
            "data": data,
        }

        # 1. Send to elevator-specific connections
        if elevator_id in self._elevator_connections:
            disconnected = []
            for ws in self._elevator_connections[elevator_id]:
                try:
                    await ws.send_json(payload)
                except Exception as exc:
                    logger.warning("Error sending to websocket (%s): %s", elevator_id, exc)
                    disconnected.append(ws)
            for ws in disconnected:
                self.disconnect_elevator(ws, elevator_id)

        # 2. Send to fleet connections
        if self._fleet_connections:
            disconnected = []
            fleet_payload = {
                "type": "fleet_telemetry",
                "elevator_id": elevator_id,
                "data": data,
            }
            for ws in self._fleet_connections:
                try:
                    await ws.send_json(fleet_payload)
                except Exception as exc:
                    logger.warning("Error sending to fleet websocket: %s", exc)
                    disconnected.append(ws)
            for ws in disconnected:
                self.disconnect_fleet(ws)


# Singleton instance
manager = ConnectionManager()


def get_connection_manager() -> ConnectionManager:
    return manager
