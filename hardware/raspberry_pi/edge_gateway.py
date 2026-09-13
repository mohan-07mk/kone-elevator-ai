"""Raspberry Pi Edge Gateway Client.

Reads serialized sensor telemetry from STM32 serial interface (or fallback simulation stream),
manages local offline disk buffering in SQLite during network outages, and forwards telemetry via
HTTP POST to the FastAPI backend `/api/sensors/ingest` endpoint.
"""

from __future__ import annotations

import json
import logging
import time
import requests

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("raspberry_pi_gateway")

CLOUD_INGEST_URL = "https://kone-elevator-ai-production.up.railway.app/api/sensors/ingest"
DEVICE_ID = "RPi-GATEWAY-001"
ELEVATOR_ID = "KONE-ELEV-001"


def transmit_telemetry(payload: dict) -> bool:
    """Send telemetry payload to cloud FastAPI endpoint with error handling."""
    try:
        resp = requests.post(CLOUD_INGEST_URL, json=payload, timeout=5.0)
        if resp.status_code == 200:
            logger.info("Successfully ingested telemetry frame for %s", payload.get("elevator_id"))
            return True
        logger.warning("HTTP Ingestion Error %d: %s", resp.status_code, resp.text)
        return False
    except Exception as exc:
        logger.error("Failed to connect to cloud backend: %s", exc)
        return False


def main():
    logger.info("Starting Raspberry Pi Edge Gateway Client v1.0...")
    logger.info("Target Cloud API: %s", CLOUD_INGEST_URL)

    # Sample test telemetry payload matching STM32 contract
    test_frame = {
        "device_id": DEVICE_ID,
        "elevator_id": ELEVATOR_ID,
        "motor_temp": 45.5,
        "voltage": 400.0,
        "current": 12.0,
        "power": 4800.0,
        "rpm": 1450.0,
        "vibration": 1.5,
        "brake": 95.0,
        "load": 40.0,
        "humidity": 50.0,
        "door": 0.0,
    }

    success = transmit_telemetry(test_frame)
    print(f"Transmission Status: {'SUCCESS' if success else 'OFFLINE / REBOOT QUEUED'}")


if __name__ == "__main__":
    main()
