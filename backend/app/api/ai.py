"""FastAPI Router for AI Fault Detection, RCA, and Evaluation."""

from __future__ import annotations

from typing import Any
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc

from app.database.session import get_db
from app.models.models import AIInference, RCAResult, SensorReading
from app.ai.pipeline import get_ai_pipeline
from app.ai.evaluator import evaluate_models

router = APIRouter(prefix="/api/ai", tags=["AI & Fault Detection"])


@router.post("/detect/{elevator_id}")
async def detect_faults(elevator_id: str, db: AsyncSession = Depends(get_db)):
    """Trigger real-time AI fault detection for an elevator based on recent telemetry."""
    # Fetch recent sensor readings
    stmt = (
        select(SensorReading)
        .where(SensorReading.elevator_id == elevator_id)
        .order_by(desc(SensorReading.recorded_at))
        .limit(100)
    )
    res = await db.execute(stmt)
    readings = res.scalars().all()

    if not readings:
        raise HTTPException(status_code=404, detail=f"No telemetry found for elevator {elevator_id}")

    # Reconstruct frame from latest sensor readings
    latest_time = readings[0].recorded_at
    frame = {r.sensor_key: r.value for r in readings if r.recorded_at == latest_time}

    pipeline = get_ai_pipeline()
    result = await pipeline.process_telemetry(db, elevator_id, [frame])
    return result["inference"]


@router.get("/rca/{elevator_id}")
async def get_root_cause_analysis(elevator_id: str, db: AsyncSession = Depends(get_db)):
    """Fetch latest Root Cause Analysis (RCA) report for an elevator."""
    stmt = (
        select(RCAResult)
        .where(RCAResult.elevator_id == elevator_id)
        .order_by(desc(RCAResult.created_at))
    )
    res = await db.execute(stmt)
    rca = res.scalars().first()

    if not rca:
        # Fallback: trigger fresh analysis on latest telemetry
        stmt_readings = (
            select(SensorReading)
            .where(SensorReading.elevator_id == elevator_id)
            .order_by(desc(SensorReading.recorded_at))
            .limit(100)
        )
        r_res = await db.execute(stmt_readings)
        readings = r_res.scalars().all()
        if readings:
            latest_time = readings[0].recorded_at
            frame = {r.sensor_key: r.value for r in readings if r.recorded_at == latest_time}
            pipeline = get_ai_pipeline()
            full_out = await pipeline.process_telemetry(db, elevator_id, [frame])
            return full_out["rca"]
        else:
            raise HTTPException(status_code=404, detail=f"No RCA record available for {elevator_id}")

    return {
        "elevator_id": rca.elevator_id,
        "root_cause": rca.root_cause,
        "affected_component": rca.affected_component,
        "confidence": rca.confidence,
        "contributing_factors": rca.contributing_factors or [],
        "evidence": rca.evidence or [],
        "verification_steps": rca.verification_steps or [],
        "created_at": rca.created_at.isoformat() if rca.created_at else None,
    }


@router.get("/evaluation")
async def get_ml_evaluation():
    """Returns true Machine Learning performance evaluation metrics computed on the industrial dataset split."""
    return evaluate_models()


@router.get("/status")
async def get_ai_status():
    """Returns actual AI Hardware, Execution Provider, Model, and Latency status."""
    from app.ai.runtime import get_ai_runtime
    runtime = get_ai_runtime()
    return runtime.get_status()


@router.get("/benchmark")
@router.post("/benchmark")
async def get_ai_benchmark(num_passes: int = Query(default=100, ge=10, le=1000)):
    """Runs micro-benchmark measuring CPU vs Snapdragon Accelerator latency, throughput, RAM, utilization, and consistency."""
    from app.ai.runtime import get_ai_runtime
    runtime = get_ai_runtime()
    return runtime.run_benchmark(num_passes=num_passes)
