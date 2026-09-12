"""WebSocket API endpoints for real-time telemetry streaming."""

from __future__ import annotations

import logging
from fastapi import APIRouter, WebSocket, WebSocketDisconnect

from app.websockets.manager import get_connection_manager

logger = logging.getLogger("elevator_ai.ws_api")

router = APIRouter(prefix="/ws", tags=["websockets"])


@router.websocket("/elevators/{elevator_id}")
async def websocket_elevator(websocket: WebSocket, elevator_id: str):
    """Real-time telemetry stream for a specific elevator."""
    manager = get_connection_manager()
    await manager.connect_elevator(websocket, elevator_id)
    try:
        while True:
            # Keep-alive receive loop
            data = await websocket.receive_text()
            # Optional ping/pong handling
            if data == "ping":
                await websocket.send_text("pong")
    except WebSocketDisconnect:
        manager.disconnect_elevator(websocket, elevator_id)
    except Exception as exc:
        logger.warning("WebSocket error for elevator %s: %s", elevator_id, exc)
        manager.disconnect_elevator(websocket, elevator_id)


@router.websocket("/fleet")
async def websocket_fleet(websocket: WebSocket):
    """Real-time telemetry stream for all elevators across the fleet."""
    manager = get_connection_manager()
    await manager.connect_fleet(websocket)
    try:
        while True:
            data = await websocket.receive_text()
            if data == "ping":
                await websocket.send_text("pong")
    except WebSocketDisconnect:
        manager.disconnect_fleet(websocket)
    except Exception as exc:
        logger.warning("WebSocket error for fleet stream: %s", exc)
        manager.disconnect_fleet(websocket)
