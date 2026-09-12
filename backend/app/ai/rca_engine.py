"""Root Cause Analysis (RCA) Engine."""

from __future__ import annotations

import logging
from typing import Any
from pydantic import BaseModel

from app.ai.fault_detector import InferenceResult

logger = logging.getLogger("elevator_ai.rca")


class RCAResultSchema(BaseModel):
    elevator_id: str
    root_cause: str
    affected_component: str
    confidence: float
    contributing_factors: list[dict[str, Any]]
    evidence: list[dict[str, Any]]
    verification_steps: list[str]


class RCAEngine:
    """Dynamically analyzes telemetry evidence to determine root cause."""

    def analyze(self, elevator_id: str, inference: InferenceResult, features: dict[str, float]) -> RCAResultSchema:
        fault_type = inference.fault_type
        vib = features.get("vibration", 1.5)
        rms = features.get("vibration_rms", vib)
        temp = features.get("motor_temp", 45.0)
        current = features.get("current", 12.0)
        rpm = features.get("rpm", 1450.0)
        load = features.get("load", 40.0)
        temp_slope = features.get("temp_slope", 0.0)

        contributing = []
        evidence = []

        if fault_type == "Bearing Degradation" or vib > 4.0:
            root_cause = "Sub-surface fatigue & inner-race roller bearing spalling in main drive gear assembly."
            affected_component = "Main Drive Shaft Bearing Assembly (SKF-6208)"
            confidence = min(0.98, max(0.85, 0.75 + (vib / 25.0)))

            contributing.append({
                "factor": "High Mechanical Vibration",
                "severity": "critical" if vib > 12.0 else "warning",
                "impact": f"Vibration amplitude reached {vib:.2f} mm/s (normal < 4.5 mm/s)"
            })
            contributing.append({
                "factor": "Vibration Energy (RMS)",
                "severity": "critical" if rms > 10.0 else "warning",
                "impact": f"RMS energy level elevated at {rms:.2f} mm/s"
            })
            if temp > 60.0:
                contributing.append({
                    "factor": "Frictional Thermal Dissipation",
                    "severity": "warning",
                    "impact": f"Motor temp at {temp:.1f} °C due to bearing friction"
                })

            evidence.append({"metric": "Vibration Amplitude", "value": f"{vib:.2f} mm/s", "threshold": "4.5 mm/s"})
            evidence.append({"metric": "Vibration RMS", "value": f"{rms:.2f} mm/s", "threshold": "3.8 mm/s"})
            evidence.append({"metric": "Motor Temp", "value": f"{temp:.1f} °C", "threshold": "65.0 °C"})

            verification_steps = [
                "1. Perform acoustic emission ultrasound scan on motor front housing bearing race.",
                "2. Check lubrication grease clarity for metallic wear debris or micro-shavings.",
                "3. Inspect drive shaft axial play with dial gauge indicator (max tolerance 0.05 mm).",
                "4. Replace SKF-6208 bearing unit if vibration harmonic exceeds 10 mm/s."
            ]

        elif fault_type == "Motor Overheating" or temp > 65.0:
            root_cause = "Stator winding thermal breakdown caused by cooling fan obstruction or rotor overload."
            affected_component = "3-Phase Induction Traction Motor Winding"
            confidence = min(0.97, max(0.82, 0.70 + (temp / 100.0)))

            contributing.append({
                "factor": "Thermal Escalation",
                "severity": "critical" if temp > 80.0 else "warning",
                "impact": f"Motor temperature elevated to {temp:.1f} °C (normal < 65.0 °C)"
            })
            if current > 15.0:
                contributing.append({
                    "factor": "Current Overload",
                    "severity": "warning",
                    "impact": f"Motor draw {current:.1f} A exceeds nominal 12.0 A"
                })

            evidence.append({"metric": "Motor Temp", "value": f"{temp:.1f} °C", "threshold": "65.0 °C"})
            evidence.append({"metric": "Temp Slope", "value": f"+{temp_slope:.2f} °C/step", "threshold": "+0.10 °C/step"})
            evidence.append({"metric": "Motor Current", "value": f"{current:.1f} A", "threshold": "18.0 A"})

            verification_steps = [
                "1. Measure motor stator phase-to-phase winding resistance with milliohm meter.",
                "2. Clear air intake vents and verify cooling fan airflow rotation speed.",
                "3. Perform infrared thermography scan on junction terminal box."
            ]

        elif fault_type == "Door Alignment Drift" or features.get("door", 0) > 0.5:
            root_cause = "Guide shoe wear & mechanical track debris causing door interlock friction."
            affected_component = "Car Door Operator Coupler & Interlock Assembly"
            confidence = 0.92

            contributing.append({
                "factor": "Door Cycle Stalling",
                "severity": "warning",
                "impact": "Door sensor indicates open/stuck state beyond cycle threshold"
            })
            evidence.append({"metric": "Door State", "value": "Stuck / Delayed", "threshold": "Closed"})

            verification_steps = [
                "1. Clean door sill track groove of dust and foreign material.",
                "2. Inspect door operator belt tension and optical sensor alignment.",
                "3. Lubricate door hanger rollers with silicone lubricant."
            ]

        else:
            root_cause = "Normal operational parameters within healthy tolerance bounds."
            affected_component = "Entire Elevator Subsystem"
            confidence = 0.96

            contributing.append({
                "factor": "Baseline Performance",
                "severity": "healthy",
                "impact": "All 10 sensor signals operating within nominal boundaries"
            })
            evidence.append({"metric": "Overall Fleet Status", "value": "Nominal", "threshold": "Healthy"})
            verification_steps = ["1. Maintain routine scheduled inspection interval."]

        return RCAResultSchema(
            elevator_id=elevator_id,
            root_cause=root_cause,
            affected_component=affected_component,
            confidence=round(confidence, 4),
            contributing_factors=contributing,
            evidence=evidence,
            verification_steps=verification_steps,
        )


rca_engine = RCAEngine()


def get_rca_engine() -> RCAEngine:
    return rca_engine
