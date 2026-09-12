"""Explainable Elevator Health Engine with Configurable Component Weights."""

from __future__ import annotations

import logging
from typing import Any
from pydantic import BaseModel, Field

logger = logging.getLogger("elevator_ai.health")


class ComponentHealth(BaseModel):
    motor: float = 100.0
    bearing: float = 100.0
    door: float = 100.0
    brake: float = 100.0
    electrical: float = 100.0


class HealthWeights(BaseModel):
    motor: float = Field(default=0.25, ge=0.0, le=1.0)
    bearing: float = Field(default=0.30, ge=0.0, le=1.0)
    door: float = Field(default=0.15, ge=0.0, le=1.0)
    brake: float = Field(default=0.15, ge=0.0, le=1.0)
    electrical: float = Field(default=0.15, ge=0.0, le=1.0)


class HealthResultSchema(BaseModel):
    elevator_id: str
    overall_health: float
    status: str
    components: ComponentHealth
    weights: HealthWeights
    contributing_factors: list[dict[str, Any]]


class HealthEngine:
    """Computes explainable elevator health scores."""

    def __init__(self) -> None:
        self.weights = HealthWeights()

    def set_weights(self, weights: HealthWeights) -> None:
        # Normalize weights so they sum to 1.0
        total = weights.motor + weights.bearing + weights.door + weights.brake + weights.electrical
        if total > 0:
            self.weights = HealthWeights(
                motor=round(weights.motor / total, 3),
                bearing=round(weights.bearing / total, 3),
                door=round(weights.door / total, 3),
                brake=round(weights.brake / total, 3),
                electrical=round(weights.electrical / total, 3),
            )

    def calculate_health(self, elevator_id: str, features: dict[str, float]) -> HealthResultSchema:
        vib = features.get("vibration", 1.5)
        temp = features.get("motor_temp", 45.0)
        current = features.get("current", 12.0)
        voltage = features.get("voltage", 400.0)
        brake = features.get("brake", 95.0)
        door = features.get("door", 0.0)

        # 1. Bearing Health (driven by vibration & vibration RMS)
        bearing_penalty = max(0.0, (vib - 2.0) * 5.0)
        if vib > 12.0:
            bearing_penalty += (vib - 12.0) * 3.0
        bearing_health = max(10.0, min(100.0, 100.0 - bearing_penalty))

        # 2. Motor Health (driven by temperature & current)
        motor_penalty = max(0.0, (temp - 55.0) * 1.8) + max(0.0, (current - 14.0) * 3.0)
        motor_health = max(15.0, min(100.0, 100.0 - motor_penalty))

        # 3. Electrical Health (driven by voltage deviation & power factor)
        volt_dev = abs(voltage - 400.0)
        electrical_penalty = volt_dev * 0.8
        electrical_health = max(30.0, min(100.0, 100.0 - electrical_penalty))

        # 4. Brake Health
        brake_health = max(20.0, min(100.0, brake))

        # 5. Door Health
        door_health = 45.0 if door > 0.5 else 98.0

        components = ComponentHealth(
            motor=round(motor_health, 1),
            bearing=round(bearing_health, 1),
            door=round(door_health, 1),
            brake=round(brake_health, 1),
            electrical=round(electrical_health, 1),
        )

        # Weighted Overall Health
        w = self.weights
        overall = (
            components.motor * w.motor +
            components.bearing * w.bearing +
            components.door * w.door +
            components.brake * w.brake +
            components.electrical * w.electrical
        )
        overall = round(overall, 1)

        # System Status
        if overall >= 80.0:
            status = "healthy"
        elif overall >= 50.0:
            status = "warning"
        else:
            status = "critical"

        # Contributing penalty factors
        factors = []
        if bearing_health < 80.0:
            factors.append({
                "component": "Bearing Assembly",
                "score": bearing_health,
                "reason": f"High vibration reading ({vib:.2f} mm/s)"
            })
        if motor_health < 80.0:
            factors.append({
                "component": "Traction Motor",
                "score": motor_health,
                "reason": f"Elevated temperature ({temp:.1f} °C)"
            })
        if door_health < 80.0:
            factors.append({
                "component": "Door System",
                "score": door_health,
                "reason": "Door interlock status anomaly"
            })

        return HealthResultSchema(
            elevator_id=elevator_id,
            overall_health=overall,
            status=status,
            components=components,
            weights=self.weights,
            contributing_factors=factors,
        )


health_engine = HealthEngine()


def get_health_engine() -> HealthEngine:
    return health_engine
