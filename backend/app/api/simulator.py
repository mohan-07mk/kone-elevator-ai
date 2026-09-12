"""Simulator API — control endpoints for the deterministic sensor simulator.

POST /api/simulator/start
POST /api/simulator/pause
POST /api/simulator/resume
POST /api/simulator/reset
POST /api/simulator/scenario
GET  /api/simulator/status
"""

from __future__ import annotations

import logging

from fastapi import APIRouter, Depends, HTTPException, Response
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.session import get_db
from app.schemas.telemetry import (
    SimulatorStartRequest,
    SimulatorScenarioRequest,
    SimulatorStatusResponse,
    TelemetryIngest,
)
from app.simulator.engine import (
    Scenario,
    SimulationEngine,
    SimulatorState,
    TelemetryRecord,
    get_simulator,
)

logger = logging.getLogger("elevator_ai.simulator_api")

router = APIRouter(prefix="/api/simulator", tags=["simulator"])


async def _make_telemetry_callback(db_factory):
    """Create a callback that stores telemetry in the database and broadcasts over WebSockets."""
    from app.database.session import async_session_factory
    from app.models.models import SensorReading, Elevator
    from app.websockets.manager import get_connection_manager
    from sqlalchemy import select
    import datetime as dt

    manager = get_connection_manager()

    async def on_telemetry(record: TelemetryRecord):
        """Broadcast via WebSockets FIRST, then store telemetry in DB."""
        # ── 1. Broadcast to WebSocket clients immediately ─────────────────────
        # This MUST happen before any DB operations so slow DB never blocks streaming.
        try:
            telemetry_dict = record.model_dump()
            broadcast_data = {**telemetry_dict, "timestamp": record.timestamp, "ai": {}}
            logger.info(
                "[SIMULATOR] Broadcasting telemetry: elevator=%s motor_temp=%.1f vibration=%.3f voltage=%.1f",
                record.elevator_id, record.motor_temp, record.vibration, record.voltage
            )
            await manager.broadcast_elevator_telemetry(record.elevator_id, broadcast_data)
        except Exception as exc:
            logger.warning("[SIMULATOR] WebSocket broadcast error: %s", exc)

        # ── 2. Store to database (non-blocking for WS clients) ────────────────
        async with async_session_factory() as session:
            try:
                recorded_at = dt.datetime.fromisoformat(record.timestamp)
            except ValueError:
                recorded_at = dt.datetime.now(dt.timezone.utc)

            sensor_values = {
                "motor_temp": record.motor_temp,
                "voltage": record.voltage,
                "current": record.current,
                "power": record.power,
                "rpm": record.rpm,
                "vibration": record.vibration,
                "brake": record.brake,
                "load": record.load,
                "humidity": record.humidity,
                "door": record.door,
            }

            try:
                for key, value in sensor_values.items():
                    reading = SensorReading(
                        elevator_id=record.elevator_id,
                        sensor_key=key,
                        value=value,
                        is_anomaly=False,
                        recorded_at=recorded_at,
                    )
                    session.add(reading)

                # Update elevator connection status
                result = await session.execute(
                    select(Elevator).where(Elevator.id == record.elevator_id)
                )
                elevator = result.scalar_one_or_none()
                if elevator:
                    elevator.last_telemetry_at = recorded_at
                    elevator.connection_status = "online"

                await session.commit()
            except Exception as db_exc:
                logger.warning("[SIMULATOR] DB store error (non-fatal, WS already broadcast): %s", db_exc)
                await session.rollback()

    return on_telemetry


def _status_to_response(sim: SimulationEngine) -> SimulatorStatusResponse:
    """Convert engine status to API response."""
    s = sim.status
    return SimulatorStatusResponse(
        state=s.state.value,
        scenario=s.scenario.value,
        elevator_id=s.elevator_id,
        device_id=s.device_id,
        position=s.position,
        total_records=s.total_records,
        replay_speed=s.replay_speed,
        records_emitted=s.records_emitted,
        mode=s.mode,
        started_at=s.started_at.isoformat() if s.started_at else None,
        error=s.error,
    )


@router.get("/status", response_model=SimulatorStatusResponse)
async def simulator_status():
    """Get current simulator status."""
    sim = get_simulator()
    return _status_to_response(sim)


@router.post("/start", response_model=SimulatorStatusResponse)
async def simulator_start(
    request: SimulatorStartRequest = SimulatorStartRequest(),
):
    """Start the simulator with the given configuration."""
    logger.info("[SIMULATOR] START requested via API: elevator_id=%s, scenario=%s, speed=%s",
                request.elevator_id, request.scenario, request.replay_speed)
    sim = get_simulator()

    try:
        scenario = Scenario(request.scenario)
    except ValueError:
        logger.error("[SIMULATOR] Invalid scenario request: %s", request.scenario)
        raise HTTPException(
            status_code=400,
            detail=f"Invalid scenario '{request.scenario}'. "
                   f"Valid: {[s.value for s in Scenario]}"
        )

    try:
        callback = await _make_telemetry_callback(None)

        await sim.start(
            on_telemetry=callback,
            elevator_id=request.elevator_id,
            scenario=scenario,
            replay_speed=request.replay_speed,
        )

        return _status_to_response(sim)
    except Exception as exc:
        logger.error("[SIMULATOR] Failed to start simulator: %s", exc, exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Simulator start failed: {str(exc)}"
        )


@router.post("/pause", response_model=SimulatorStatusResponse)
async def simulator_pause():
    """Pause the simulator."""
    sim = get_simulator()
    if sim.status.state != SimulatorState.RUNNING:
        raise HTTPException(status_code=400, detail="Simulator is not running")
    await sim.pause()
    return _status_to_response(sim)


@router.post("/resume", response_model=SimulatorStatusResponse)
async def simulator_resume():
    """Resume the simulator."""
    sim = get_simulator()
    if sim.status.state != SimulatorState.PAUSED:
        raise HTTPException(status_code=400, detail="Simulator is not paused")
    await sim.resume()
    return _status_to_response(sim)


@router.post("/reset", response_model=SimulatorStatusResponse)
async def simulator_reset():
    """Reset the simulator to initial state."""
    sim = get_simulator()
    await sim.reset()
    return _status_to_response(sim)


@router.post("/scenario", response_model=SimulatorStatusResponse)
async def simulator_scenario(request: SimulatorScenarioRequest):
    """Change the active scenario."""
    sim = get_simulator()

    try:
        scenario = Scenario(request.scenario)
    except ValueError:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid scenario '{request.scenario}'. "
                   f"Valid: {[s.value for s in Scenario]}"
        )

    await sim.set_scenario(
        scenario=scenario,
        elevator_id=request.elevator_id,
        replay_speed=request.replay_speed,
    )

    return _status_to_response(sim)
