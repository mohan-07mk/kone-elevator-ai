"""FastAPI Router for Elevator Health Engine."""

from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc

from app.database.session import get_db
from app.models.models import ElevatorHealthRecord, SensorReading
from app.ai.health_engine import get_health_engine, HealthWeights
from app.ai.pipeline import get_ai_pipeline

router = APIRouter(prefix="/api/health", tags=["Elevator Health"])


@router.get("/{elevator_id}")
async def get_elevator_health(elevator_id: str, db: AsyncSession = Depends(get_db)):
    """Fetch latest explainable health breakdown for an elevator."""
    stmt = (
        select(ElevatorHealthRecord)
        .where(ElevatorHealthRecord.elevator_id == elevator_id)
        .order_by(desc(ElevatorHealthRecord.recorded_at))
    )
    res = await db.execute(stmt)
    rec = res.scalars().first()

    if not rec:
        # Fallback to fresh calculation
        stmt_readings = (
            select(SensorReading)
            .where(SensorReading.elevator_id == elevator_id)
            .order_by(desc(SensorReading.recorded_at))
            .limit(100)
        )
        res_r = await db.execute(stmt_readings)
        readings = res_r.scalars().all()
        if readings:
            latest_time = readings[0].recorded_at
            frame = {r.sensor_key: r.value for r in readings if r.recorded_at == latest_time}
            pipeline = get_ai_pipeline()
            full_out = await pipeline.process_telemetry(db, elevator_id, [frame])
            return full_out["health"]
        else:
            raise HTTPException(status_code=404, detail=f"No health data found for {elevator_id}")

    return {
        "elevator_id": rec.elevator_id,
        "overall_health": rec.overall_health,
        "status": rec.status,
        "components": {
            "motor": rec.motor_health,
            "bearing": rec.bearing_health,
            "door": rec.door_health,
            "brake": rec.brake_health,
            "electrical": rec.electrical_health,
        },
        "weights": rec.weights or {},
        "contributing_factors": rec.contributing_factors or [],
        "recorded_at": rec.recorded_at.isoformat() if rec.recorded_at else None,
    }


@router.post("/weights")
async def update_health_weights(weights: HealthWeights):
    """Update component weights for explainable health engine."""
    engine = get_health_engine()
    engine.set_weights(weights)
    return {
        "message": "Health engine weights updated successfully",
        "weights": engine.weights.model_dump(),
    }
