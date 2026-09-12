"""FastAPI Router for Predictive Maintenance and RUL."""

from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc

from app.database.session import get_db
from app.models.models import PredictiveRecord, SensorReading
from app.ai.pipeline import get_ai_pipeline

router = APIRouter(prefix="/api/predictive", tags=["Predictive Maintenance"])


@router.get("/{elevator_id}")
async def get_predictive_status(elevator_id: str, db: AsyncSession = Depends(get_db)):
    """Fetch latest RUL and predictive maintenance risk analysis for an elevator."""
    stmt = (
        select(PredictiveRecord)
        .where(PredictiveRecord.elevator_id == elevator_id)
        .order_by(desc(PredictiveRecord.computed_at))
    )
    res = await db.execute(stmt)
    rec = res.scalars().first()

    if not rec:
        # Fallback to fresh analysis
        return await analyze_predictive(elevator_id, db)

    return {
        "elevator_id": rec.elevator_id,
        "failure_risk": rec.failure_risk,
        "rul_hours": rec.rul_hours,
        "priority": rec.priority,
        "recommended_action": rec.recommended_action,
        "component_health": rec.component_health or {},
        "computed_at": rec.computed_at.isoformat() if rec.computed_at else None,
    }


@router.post("/analyze/{elevator_id}")
async def analyze_predictive(elevator_id: str, db: AsyncSession = Depends(get_db)):
    """Trigger fresh predictive maintenance analysis for an elevator."""
    stmt_readings = (
        select(SensorReading)
        .where(SensorReading.elevator_id == elevator_id)
        .order_by(desc(SensorReading.recorded_at))
        .limit(100)
    )
    res = await db.execute(stmt_readings)
    readings = res.scalars().all()

    if not readings:
        raise HTTPException(status_code=404, detail=f"No telemetry data found for elevator {elevator_id}")

    latest_time = readings[0].recorded_at
    frame = {r.sensor_key: r.value for r in readings if r.recorded_at == latest_time}

    pipeline = get_ai_pipeline()
    full_output = await pipeline.process_telemetry(db, elevator_id, [frame])
    return full_output["predictive"]
