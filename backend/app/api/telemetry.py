"""Telemetry API — ingest, query latest, and history endpoints.

POST /api/sensors/ingest
GET  /api/elevators/{id}/sensors/latest
GET  /api/elevators/{id}/sensors/history
GET  /api/elevators/{id}/sensors/{sensor}/history
"""

from __future__ import annotations

import datetime as dt
import logging
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select, func, desc
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.session import get_db
from app.models.models import SensorReading, Elevator
from app.schemas.telemetry import (
    TelemetryIngest,
    TelemetryResponse,
    SensorLatest,
    SensorHistory,
    SensorHistoryPoint,
)

logger = logging.getLogger("elevator_ai.telemetry")

router = APIRouter(prefix="/api", tags=["telemetry"])

# All 10 sensor keys from the contract
SENSOR_KEYS = [
    "motor_temp", "voltage", "current", "power", "rpm",
    "vibration", "brake", "load", "humidity", "door",
]


@router.post("/sensors/ingest", response_model=TelemetryResponse)
async def ingest_telemetry(
    payload: TelemetryIngest,
    db: AsyncSession = Depends(get_db),
):
    """Ingest a single telemetry record into the database.

    Stores each sensor value as a separate SensorReading row.
    """
    timestamp_str = payload.timestamp or dt.datetime.now(dt.timezone.utc).isoformat()
    try:
        recorded_at = dt.datetime.fromisoformat(timestamp_str)
    except ValueError:
        recorded_at = dt.datetime.now(dt.timezone.utc)

    # Verify elevator exists
    result = await db.execute(select(Elevator).where(Elevator.id == payload.elevator_id))
    elevator = result.scalar_one_or_none()
    if not elevator:
        raise HTTPException(status_code=404, detail=f"Elevator {payload.elevator_id} not found")

    # Store each sensor value
    sensor_values = {
        "motor_temp": payload.motor_temp,
        "voltage": payload.voltage,
        "current": payload.current,
        "power": payload.power,
        "rpm": payload.rpm,
        "vibration": payload.vibration,
        "brake": payload.brake,
        "load": payload.load,
        "humidity": payload.humidity,
        "door": payload.door,
    }

    records_stored = 0
    for key, value in sensor_values.items():
        reading = SensorReading(
            elevator_id=payload.elevator_id,
            sensor_key=key,
            value=value,
            is_anomaly=False,
            recorded_at=recorded_at,
        )
        db.add(reading)
        records_stored += 1

    # Update elevator's last_telemetry_at and connection_status
    elevator.last_telemetry_at = recorded_at
    elevator.connection_status = "online"

    await db.flush()

    # Broadcast via WebSockets
    try:
        from app.websockets.manager import get_connection_manager
        manager = get_connection_manager()
        telemetry_dict = {
            "device_id": payload.device_id,
            "elevator_id": payload.elevator_id,
            "timestamp": timestamp_str,
            **sensor_values,
        }
        await manager.broadcast_elevator_telemetry(payload.elevator_id, telemetry_dict)
    except Exception as exc:
        logger.warning("WebSocket broadcast error on ingest: %s", exc)

    logger.debug("Ingested %d sensor readings for %s", records_stored, payload.elevator_id)

    return TelemetryResponse(
        status="ok",
        records_stored=records_stored,
        elevator_id=payload.elevator_id,
        timestamp=recorded_at.isoformat(),
    )


@router.get("/elevators/{elevator_id}/sensors/latest", response_model=SensorLatest)
async def get_latest_sensors(
    elevator_id: str,
    db: AsyncSession = Depends(get_db),
):
    """Get the latest value for each sensor of an elevator."""
    # Verify elevator exists
    result = await db.execute(select(Elevator).where(Elevator.id == elevator_id))
    if not result.scalar_one_or_none():
        raise HTTPException(status_code=404, detail=f"Elevator {elevator_id} not found")

    latest: dict[str, Optional[float]] = {}
    latest_ts: Optional[str] = None

    for key in SENSOR_KEYS:
        stmt = (
            select(SensorReading)
            .where(
                SensorReading.elevator_id == elevator_id,
                SensorReading.sensor_key == key,
            )
            .order_by(desc(SensorReading.recorded_at))
            .limit(1)
        )
        result = await db.execute(stmt)
        reading = result.scalar_one_or_none()

        if reading:
            latest[key] = reading.value
            ts = reading.recorded_at.isoformat() if reading.recorded_at else None
            if ts and (latest_ts is None or ts > latest_ts):
                latest_ts = ts
        else:
            latest[key] = None

    return SensorLatest(
        elevator_id=elevator_id,
        timestamp=latest_ts,
        **latest,
    )


@router.get("/elevators/{elevator_id}/sensors/history", response_model=SensorHistory)
async def get_sensor_history_all(
    elevator_id: str,
    limit: int = Query(default=100, ge=1, le=1000),
    offset: int = Query(default=0, ge=0),
    db: AsyncSession = Depends(get_db),
):
    """Get sensor history for all sensors of an elevator."""
    # Verify elevator exists
    result = await db.execute(select(Elevator).where(Elevator.id == elevator_id))
    if not result.scalar_one_or_none():
        raise HTTPException(status_code=404, detail=f"Elevator {elevator_id} not found")

    stmt = (
        select(SensorReading)
        .where(SensorReading.elevator_id == elevator_id)
        .order_by(desc(SensorReading.recorded_at))
        .limit(limit)
        .offset(offset)
    )
    result = await db.execute(stmt)
    readings = result.scalars().all()

    data = [
        SensorHistoryPoint(
            value=r.value,
            recorded_at=r.recorded_at.isoformat() if r.recorded_at else "",
            is_anomaly=r.is_anomaly,
        )
        for r in readings
    ]

    return SensorHistory(
        elevator_id=elevator_id,
        count=len(data),
        data=data,
    )


@router.get("/elevators/{elevator_id}/sensors/{sensor_key}/history", response_model=SensorHistory)
async def get_sensor_history_single(
    elevator_id: str,
    sensor_key: str,
    limit: int = Query(default=100, ge=1, le=1000),
    offset: int = Query(default=0, ge=0),
    db: AsyncSession = Depends(get_db),
):
    """Get sensor history for a specific sensor of an elevator."""
    if sensor_key not in SENSOR_KEYS:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid sensor key '{sensor_key}'. Valid keys: {SENSOR_KEYS}"
        )

    # Verify elevator exists
    result = await db.execute(select(Elevator).where(Elevator.id == elevator_id))
    if not result.scalar_one_or_none():
        raise HTTPException(status_code=404, detail=f"Elevator {elevator_id} not found")

    stmt = (
        select(SensorReading)
        .where(
            SensorReading.elevator_id == elevator_id,
            SensorReading.sensor_key == sensor_key,
        )
        .order_by(desc(SensorReading.recorded_at))
        .limit(limit)
        .offset(offset)
    )
    result = await db.execute(stmt)
    readings = result.scalars().all()

    data = [
        SensorHistoryPoint(
            value=r.value,
            recorded_at=r.recorded_at.isoformat() if r.recorded_at else "",
            is_anomaly=r.is_anomaly,
        )
        for r in readings
    ]

    return SensorHistory(
        elevator_id=elevator_id,
        sensor_key=sensor_key,
        count=len(data),
        data=data,
    )
