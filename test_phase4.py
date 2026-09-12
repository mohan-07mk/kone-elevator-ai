"""Phase 4 End-to-End Test Script — Tests WebSockets, Simulator, DB, & API endpoints."""

import asyncio
import json
import logging
import sys
import websockets
import httpx

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("phase4_test")

BASE_URL = "http://localhost:8000"
WS_URL = "ws://localhost:8000"


async def test_phase4():
    logger.info("Starting Phase 4 Integration Verification Test...")

    async with httpx.AsyncClient(base_url=BASE_URL, timeout=10.0) as client:
        # 1. Check simulator status
        resp = await client.get("/api/simulator/status")
        assert resp.status_code == 200, f"Status check failed: {resp.text}"
        status = resp.json()
        logger.info("Initial Simulator Status: state=%s, mode=%s", status["state"], status["mode"])

        # 2. Reset simulator to clear prior state
        resp = await client.post("/api/simulator/reset")
        assert resp.status_code == 200

        received_elevator_telemetry = []
        received_fleet_telemetry = []

        # 3. Connect to WebSocket streams
        async def listen_elevator_ws():
            uri = f"{WS_URL}/ws/elevators/KONE-ELEV-001"
            logger.info("Connecting to WebSocket: %s", uri)
            async with websockets.connect(uri) as ws:
                while len(received_elevator_telemetry) < 5:
                    try:
                        msg = await asyncio.wait_for(ws.recv(), timeout=5.0)
                        data = json.loads(msg)
                        logger.info("[WS Elevator Received] %s timestamp=%s vibration=%s motor_temp=%s",
                                    data["elevator_id"], data["data"]["timestamp"], data["data"]["vibration"], data["data"]["motor_temp"])
                        received_elevator_telemetry.append(data)
                    except asyncio.TimeoutError:
                        logger.warning("Elevator WS timeout")
                        break

        async def listen_fleet_ws():
            uri = f"{WS_URL}/ws/fleet"
            logger.info("Connecting to WebSocket: %s", uri)
            async with websockets.connect(uri) as ws:
                while len(received_fleet_telemetry) < 5:
                    try:
                        msg = await asyncio.wait_for(ws.recv(), timeout=5.0)
                        data = json.loads(msg)
                        logger.info("[WS Fleet Received] %s telemetry for %s", data["type"], data["elevator_id"])
                        received_fleet_telemetry.append(data)
                    except asyncio.TimeoutError:
                        logger.warning("Fleet WS timeout")
                        break

        # 4. Start WebSocket listeners in background tasks
        elevator_task = asyncio.create_task(listen_elevator_ws())
        fleet_task = asyncio.create_task(listen_fleet_ws())
        await asyncio.sleep(0.5)  # Give WS time to connect

        # 5. Start Simulator with scenario BEARING_DEGRADATION at 5.0x speed
        logger.info("Triggering POST /api/simulator/start (BEARING_DEGRADATION, 5x)...")
        resp = await client.post("/api/simulator/start", json={
            "elevator_id": "KONE-ELEV-001",
            "scenario": "BEARING_DEGRADATION",
            "replay_speed": 5.0,
        })
        assert resp.status_code == 200, f"Start failed: {resp.text}"

        # 6. Wait for WS tasks to collect records
        await asyncio.gather(elevator_task, fleet_task)

        # 7. Assert WebSocket telemetry received
        assert len(received_elevator_telemetry) >= 5, f"Expected 5 WS records, got {len(received_elevator_telemetry)}"
        assert len(received_fleet_telemetry) >= 5, f"Expected 5 Fleet WS records, got {len(received_fleet_telemetry)}"

        # 8. Test Pause
        logger.info("Testing POST /api/simulator/pause...")
        resp = await client.post("/api/simulator/pause")
        assert resp.status_code == 200
        p_status = resp.json()
        assert p_status["state"] == "PAUSED"
        logger.info("Simulator paused at position %d", p_status["position"])

        # 9. Test Resume
        logger.info("Testing POST /api/simulator/resume...")
        resp = await client.post("/api/simulator/resume")
        assert resp.status_code == 200
        r_status = resp.json()
        assert r_status["state"] == "RUNNING"

        await asyncio.sleep(1.0)

        # 10. Verify DB persistence via REST API
        logger.info("Verifying REST API GET /api/elevators/KONE-ELEV-001/sensors/latest...")
        latest_resp = await client.get("/api/elevators/KONE-ELEV-001/sensors/latest")
        assert latest_resp.status_code == 200
        latest_data = latest_resp.json()
        logger.info("Latest sensors from DB: %s", latest_data)
        assert latest_data["vibration"] is not None
        assert latest_data["motor_temp"] is not None

        logger.info("Verifying REST API GET /api/elevators/KONE-ELEV-001/sensors/vibration/history...")
        hist_resp = await client.get("/api/elevators/KONE-ELEV-001/sensors/vibration/history?limit=10")
        assert hist_resp.status_code == 200
        hist_data = hist_resp.json()
        logger.info("Vibration history count: %d points", hist_data["count"])
        assert hist_data["count"] > 0

        # 11. Reset simulator
        await client.post("/api/simulator/reset")
        logger.info("✅ ALL PHASE 4 TESTS PASSED SUCCESSFULLY!")


if __name__ == "__main__":
    asyncio.run(test_phase4())
