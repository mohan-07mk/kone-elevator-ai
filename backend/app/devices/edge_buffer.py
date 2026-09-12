"""Edge Buffer & Offline Resiliency Engine for Hardware Telemetry."""

from __future__ import annotations

import time
import logging
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field

logger = logging.getLogger("elevator_ai.edge_buffer")


class TelemetryBatch(BaseModel):
    device_id: str
    gateway_type: str = "raspberry-pi"  # "stm32", "raspberry-pi", "simulator"
    timestamp: float = Field(default_factory=time.time)
    readings: List[Dict[str, Any]]
    offline_buffered: bool = False
    retry_count: int = 0


class EdgeBufferManager:
    """Manages edge device offline buffering, retry mechanisms, and batching."""

    def __init__(self, max_buffer_size: int = 1000) -> None:
        self.max_buffer_size = max_buffer_size
        self.buffer: List[TelemetryBatch] = []
        self.registered_devices: Dict[str, Dict[str, Any]] = {}
        self.device_heartbeats: Dict[str, float] = {}

    def register_device(
        self,
        device_id: str,
        device_type: str,
        building_id: str = "BLD-A",
        elevator_id: str = "KONE-ELEV-001",
        ip_address: Optional[str] = "192.168.1.100",
        firmware_version: str = "v2.1.0-edge"
    ) -> Dict[str, Any]:
        """Registers an edge device (STM32, Raspberry Pi, Simulator)."""
        now = time.time()
        record = {
            "device_id": device_id,
            "device_type": device_type,
            "building_id": building_id,
            "elevator_id": elevator_id,
            "ip_address": ip_address,
            "firmware_version": firmware_version,
            "status": "online",
            "registered_at": now,
            "last_seen": now,
            "packets_received": 0,
            "offline_events": 0,
        }
        self.registered_devices[device_id] = record
        self.device_heartbeats[device_id] = now
        logger.info("Registered edge device [%s] (%s)", device_id, device_type)
        return record

    def update_heartbeat(self, device_id: str, metrics: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Updates device heartbeat and online status."""
        now = time.time()
        if device_id not in self.registered_devices:
            self.register_device(device_id, "gateway", "BLD-A", "KONE-ELEV-001")

        dev = self.registered_devices[device_id]
        dev["last_seen"] = now
        dev["status"] = "online"
        if metrics:
            dev.update(metrics)
        self.device_heartbeats[device_id] = now
        return dev

    def buffer_telemetry(self, batch: TelemetryBatch) -> int:
        """Buffers telemetry reading if backend or database is unreachable."""
        if len(self.buffer) >= self.max_buffer_size:
            self.buffer.pop(0)  # FIFO drop oldest
            logger.warning("Buffer overflow limit reached (%d); dropped oldest telemetry payload.", self.max_buffer_size)

        batch.offline_buffered = True
        self.buffer.append(batch)
        logger.info("Buffered telemetry payload from [%s] (Queue depth: %d)", batch.device_id, len(self.buffer))
        return len(self.buffer)

    def get_buffered_payloads(self) -> List[TelemetryBatch]:
        """Returns all queued offline payloads for synchronization upon reconnect."""
        payloads = list(self.buffer)
        self.buffer.clear()
        return payloads

    def list_devices(self) -> List[Dict[str, Any]]:
        """Lists all registered devices with updated online status."""
        now = time.time()
        res = []
        for dev_id, dev in self.registered_devices.items():
            last = self.device_heartbeats.get(dev_id, 0)
            # If no heartbeat for > 30s, mark degraded / offline
            if now - last > 30:
                dev["status"] = "offline"
            res.append(dev)
        return res

    def get_device(self, device_id: str) -> Optional[Dict[str, Any]]:
        """Gets device by ID."""
        devs = self.list_devices()
        for d in devs:
            if d["device_id"] == device_id:
                return d
        return None


# Global Singleton instance
edge_manager = EdgeBufferManager()


def get_edge_manager() -> EdgeBufferManager:
    return edge_manager
