"""Unified AI Pipeline Orchestrator for Elevator AI."""

from __future__ import annotations

import logging
from typing import Any, Sequence
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.ai.feature_extractor import extract_features
from app.ai.fault_detector import get_fault_detector, InferenceResult
from app.ai.rca_engine import get_rca_engine, RCAResultSchema
from app.ai.health_engine import get_health_engine, HealthResultSchema
from app.ai.rul_engine import get_rul_engine, PredictiveResultSchema
from app.ai.alert_engine import get_alert_engine, GeneratedAlert
from app.models.models import (
    Elevator, AIInference, RCAResult, ElevatorHealthRecord, PredictiveRecord, AlertRecord
)

logger = logging.getLogger("elevator_ai.pipeline")


class AIPipeline:
    """Runs end-to-end AI analysis, persists results, and updates elevator status."""

    async def process_telemetry(
        self,
        db: AsyncSession,
        elevator_id: str,
        window_records: Sequence[dict[str, float]],
    ) -> dict[str, Any]:
        if not window_records:
            return {}

        # 1. Feature Extraction
        features = extract_features(window_records)

        # 2. Anomaly Detection & ML Fault Classification
        detector = get_fault_detector()
        inference: InferenceResult = detector.predict(features)

        # 3. Root Cause Analysis (RCA)
        rca: RCAResultSchema = get_rca_engine().analyze(elevator_id, inference, features)

        # 4. Explainable Health Scoring
        health: HealthResultSchema = get_health_engine().calculate_health(elevator_id, features)

        # 5. RUL & Failure Risk Prediction
        predictive: PredictiveResultSchema = get_rul_engine().predict(elevator_id, health, features)

        # 6. Automated Alert Generation
        alert_engine = get_alert_engine()
        new_alerts: list[GeneratedAlert] = alert_engine.evaluate_alerts(elevator_id, inference, health, predictive)

        # 7. Database Persistence
        try:
            # Save AI Inference
            db_inf = AIInference(
                elevator_id=elevator_id,
                fault_detected=inference.fault_detected,
                fault_type=inference.fault_type,
                confidence=inference.confidence,
                severity=inference.severity,
                model_name=inference.model,
                model_version=inference.model_version,
                inference_time_ms=inference.inference_time_ms,
                features=features,
            )
            db.add(db_inf)
            await db.flush()

            # Save RCA Result
            db_rca = RCAResult(
                elevator_id=elevator_id,
                inference_id=db_inf.id,
                root_cause=rca.root_cause,
                affected_component=rca.affected_component,
                confidence=rca.confidence,
                contributing_factors=rca.contributing_factors,
                evidence=rca.evidence,
                verification_steps=rca.verification_steps,
            )
            db.add(db_rca)

            # Save Health Record
            db_health = ElevatorHealthRecord(
                elevator_id=elevator_id,
                overall_health=health.overall_health,
                motor_health=health.components.motor,
                bearing_health=health.components.bearing,
                door_health=health.components.door,
                brake_health=health.components.brake,
                electrical_health=health.components.electrical,
                status=health.status,
                contributing_factors=health.contributing_factors,
                weights=health.weights.model_dump(),
            )
            db.add(db_health)

            # Save Predictive Record
            db_pred = PredictiveRecord(
                elevator_id=elevator_id,
                failure_risk=predictive.failure_risk,
                rul_hours=predictive.rul_hours,
                priority=predictive.priority,
                recommended_action=predictive.recommended_action,
                component_health=predictive.component_health,
            )
            db.add(db_pred)

            # Save Alerts (if not duplicate active alert)
            for a in new_alerts:
                stmt = select(AlertRecord).where(
                    AlertRecord.elevator_id == elevator_id,
                    AlertRecord.title == a.title,
                    AlertRecord.status == "active",
                )
                res = await db.execute(stmt)
                existing = res.scalars().first()

                if not existing:
                    db_alert = AlertRecord(
                        elevator_id=elevator_id,
                        title=a.title,
                        level=a.level,
                        source=a.source,
                        status="active",
                        details=a.details,
                    )
                    db.add(db_alert)

            # Update Elevator table state
            stmt_elev = select(Elevator).where(Elevator.id == elevator_id)
            elev_res = await db.execute(stmt_elev)
            elev = elev_res.scalars().first()
            if elev:
                elev.health_score = health.overall_health
                elev.status = health.status
                elev.active_fault = inference.fault_type if inference.fault_detected else None
                elev.risk_level = predictive.priority

            await db.commit()
        except Exception as exc:
            logger.error("Error saving AI pipeline execution to DB: %s", exc)
            await db.rollback()

        return {
            "elevator_id": elevator_id,
            "inference": inference.model_dump(),
            "rca": rca.model_dump(),
            "health": health.model_dump(),
            "predictive": predictive.model_dump(),
            "alerts": [a.model_dump() for a in new_alerts],
        }


ai_pipeline = AIPipeline()


def get_ai_pipeline() -> AIPipeline:
    return ai_pipeline
