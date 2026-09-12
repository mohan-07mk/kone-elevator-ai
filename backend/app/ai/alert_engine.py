"""Automated Alert Generation and Lifecycle Management Engine."""

from __future__ import annotations

import datetime as dt
import logging
from typing import Any, Optional
from pydantic import BaseModel

from app.ai.fault_detector import InferenceResult
from app.ai.health_engine import HealthResultSchema
from app.ai.rul_engine import PredictiveResultSchema

logger = logging.getLogger("elevator_ai.alert")


class GeneratedAlert(BaseModel):
    elevator_id: str
    title: str
    level: str  # "info", "warning", "critical"
    source: str
    details: dict[str, Any]


class AlertEngine:
    """Generates alerts dynamically from AI pipeline outputs."""

    def evaluate_alerts(
        self,
        elevator_id: str,
        inference: InferenceResult,
        health: HealthResultSchema,
        predictive: PredictiveResultSchema,
    ) -> list[GeneratedAlert]:
        alerts = []

        # 1. Critical Fault Classification Alert
        if inference.fault_detected:
            title = f"AI Fault Detected: {inference.fault_type} ({elevator_id})"
            level = "critical" if inference.severity == "critical" else "warning"
            alerts.append(GeneratedAlert(
                elevator_id=elevator_id,
                title=title,
                level=level,
                source="ai_fault_classifier",
                details={
                    "fault_type": inference.fault_type,
                    "confidence": inference.confidence,
                    "model": inference.model,
                    "severity": inference.severity,
                }
            ))

        # 2. Health Drop Alert
        if health.overall_health < 60.0:
            level = "critical" if health.overall_health < 40.0 else "warning"
            alerts.append(GeneratedAlert(
                elevator_id=elevator_id,
                title=f"Elevator Health Critical Drop: {health.overall_health}% ({elevator_id})",
                level=level,
                source="health_engine",
                details={
                    "overall_health": health.overall_health,
                    "status": health.status,
                    "contributing_factors": health.contributing_factors,
                }
            ))

        # 3. Low RUL / High Risk Alert
        if predictive.rul_hours < 72.0 or predictive.failure_risk > 60.0:
            level = "critical" if predictive.rul_hours < 24.0 else "warning"
            alerts.append(GeneratedAlert(
                elevator_id=elevator_id,
                title=f"Predictive Maintenance Due: RUL {predictive.rul_hours}h remaining ({elevator_id})",
                level=level,
                source="rul_engine",
                details={
                    "failure_risk": predictive.failure_risk,
                    "rul_hours": predictive.rul_hours,
                    "priority": predictive.priority,
                    "recommended_action": predictive.recommended_action,
                }
            ))

        return alerts


alert_engine = AlertEngine()


def get_alert_engine() -> AlertEngine:
    return alert_engine
