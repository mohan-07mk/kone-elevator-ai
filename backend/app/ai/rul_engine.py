"""Predictive Maintenance & Remaining Useful Life (RUL) Engine."""

from __future__ import annotations

import logging
from typing import Any
from pydantic import BaseModel

from app.ai.health_engine import HealthResultSchema

logger = logging.getLogger("elevator_ai.rul")


class PredictiveResultSchema(BaseModel):
    elevator_id: str
    failure_risk: float
    rul_hours: float
    priority: str
    recommended_action: str
    component_health: dict[str, float]


class RULEngine:
    """Predictive maintenance engine for RUL and failure risk estimation."""

    def predict(self, elevator_id: str, health_data: HealthResultSchema, features: dict[str, float]) -> PredictiveResultSchema:
        overall = health_data.overall_health
        comps = health_data.components
        vib = features.get("vibration", 1.5)
        temp = features.get("motor_temp", 45.0)
        temp_slope = features.get("temp_slope", 0.0)

        # 1. Failure Risk (0-100%)
        risk = max(0.0, min(99.0, (100.0 - overall) * 1.25))

        # 2. Baseline Nominal RUL = 2400 operational hours (approx. 100 days)
        # Acceleration factor driven by vibration amplitude & thermal slope
        if vib > 14.0 or temp > 80.0:
            rul_hours = max(4.0, 48.0 - (vib * 2.0))
            priority = "Critical"
            recommended_action = "IMMEDIATE SHUTDOWN & EMERGENCY BEARING REPLACEMENT."
        elif vib > 8.0 or temp > 70.0:
            rul_hours = max(24.0, 180.0 - (vib * 10.0))
            priority = "High"
            recommended_action = "Schedule technician intervention within 48 hours for main drive overhaul."
        elif vib > 4.5 or temp > 60.0:
            rul_hours = max(120.0, 720.0 - (vib * 50.0))
            priority = "Medium"
            recommended_action = "Order replacement drive components and schedule maintenance next week."
        else:
            rul_hours = max(800.0, 2400.0 - (vib * 100.0))
            priority = "Low"
            recommended_action = "System healthy. Proceed with standard preventive inspection."

        comp_dict = {
            "motor": comps.motor,
            "bearing": comps.bearing,
            "door": comps.door,
            "brake": comps.brake,
            "electrical": comps.electrical,
        }

        return PredictiveResultSchema(
            elevator_id=elevator_id,
            failure_risk=round(risk, 1),
            rul_hours=round(rul_hours, 1),
            priority=priority,
            recommended_action=recommended_action,
            component_health=comp_dict,
        )


rul_engine = RULEngine()


def get_rul_engine() -> RULEngine:
    return rul_engine
