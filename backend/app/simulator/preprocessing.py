"""Preprocessing and feature extraction — maps AI4I dataset to elevator telemetry."""

from __future__ import annotations

import logging
import math
from typing import Any

logger = logging.getLogger("elevator_ai.preprocessing")


def preprocess_record(
    rec: dict[str, Any],
    index: int,
    total: int,
) -> dict[str, float]:
    """Transform a single raw AI4I record into normalized elevator telemetry.

    Args:
        rec: Raw dataset record.
        index: Sequence index (used for deterministic simulated fields).
        total: Total number of records in sequence.

    Returns:
        Dict with all 10 sensor values.
    """
    air_temp_k = rec["Air temperature [K]"]
    proc_temp_k = rec["Process temperature [K]"]
    rpm = rec["Rotational speed [rpm]"]
    torque = rec["Torque [Nm]"]
    tool_wear = rec["Tool wear [min]"]
    machine_failure = rec.get("Machine failure", 0)
    product_type = rec.get("Type", "M")

    # ── Direct mappings ───────────────────────────────────────

    # motor_temp: Process temperature K → °C
    motor_temp = round(proc_temp_k - 273.15, 2)

    # rpm: Direct
    motor_rpm = round(rpm, 1)

    # ── Derived mappings ──────────────────────────────────────

    # voltage: Derived from air temperature (scaled to 380–420V)
    voltage = round(380.0 + (air_temp_k - 295.0) * 1.6, 2)

    # current: Derived from torque (scaled to 5–25A)
    current = round(max(5.0, min(25.0, torque * 0.5)), 2)

    # power: Mechanical power = torque × angular velocity
    power = round(torque * rpm * 2.0 * math.pi / 60.0, 2)

    # vibration: Derived from torque + tool wear (mm/s)
    vibration = round(torque * 0.1 + tool_wear * 0.02, 3)

    # ── Simulated mappings ────────────────────────────────────

    # brake: Brake force 80–120N, degraded during failures
    brake_base = 100.0
    if machine_failure:
        brake_base = 100.0 - (tool_wear * 0.1)
    brake = round(max(60.0, min(120.0, brake_base + (torque - 40.0) * 0.3)), 2)

    # load: Load percentage based on product type
    load_map = {"L": 30.0, "M": 60.0, "H": 90.0}
    load_base = load_map.get(product_type, 60.0)
    # Add deterministic variation based on index
    load_variation = math.sin(index * 0.1) * 5.0
    load = round(max(0.0, min(100.0, load_base + load_variation)), 1)

    # humidity: Correlated with air temperature
    humidity = round(max(20.0, min(90.0, 50.0 + (air_temp_k - 300.0) * 2.0)), 1)

    # door: Deterministic cycle (open every ~10 records for 2 records)
    cycle_pos = index % 10
    door = 1.0 if cycle_pos in (4, 5) else 0.0

    return {
        "motor_temp": motor_temp,
        "voltage": voltage,
        "current": current,
        "power": power,
        "rpm": motor_rpm,
        "vibration": vibration,
        "brake": brake,
        "load": load,
        "humidity": humidity,
        "door": door,
    }


def preprocess_dataset(records: list[dict[str, Any]]) -> list[dict[str, float]]:
    """Preprocess the entire dataset into elevator telemetry records."""
    total = len(records)
    telemetry = []
    for i, rec in enumerate(records):
        telemetry.append(preprocess_record(rec, i, total))

    logger.info("Preprocessed %d records into elevator telemetry", len(telemetry))
    return telemetry


def build_degradation_scenario(records: list[dict[str, Any]]) -> list[dict[str, float]]:
    """Build the deterministic bearing-degradation demo scenario.

    Selects and reorders ~500 records to create a 6-phase degradation pattern:
      Phase 1: Normal (100 records)
      Phase 2: Vibration increases (100 records)
      Phase 3: Temperature increases (100 records)
      Phase 4: Current increases (100 records)
      Phase 5: RPM instability (50 records)
      Phase 6: Bearing degradation (50 records)
    """
    # Sort records by different criteria for different phases
    normal = [r for r in records if r.get("Machine failure", 0) == 0]
    failing = [r for r in records if r.get("Machine failure", 0) == 1]

    # Sort normal records by various criteria
    by_torque = sorted(normal, key=lambda r: r["Torque [Nm]"])
    by_temp = sorted(normal, key=lambda r: r["Process temperature [K]"])
    by_wear = sorted(normal, key=lambda r: r["Tool wear [min]"])

    scenario: list[dict[str, Any]] = []

    # Phase 1: Normal — low torque, low temp records
    phase1 = by_torque[:100]
    scenario.extend(phase1)

    # Phase 2: Vibration increases — increasing torque + wear
    phase2 = sorted(by_wear[200:400], key=lambda r: r["Torque [Nm]"])[-100:]
    scenario.extend(phase2)

    # Phase 3: Temperature increases — high temp records
    phase3 = by_temp[-150:-50]
    scenario.extend(phase3)

    # Phase 4: Current increases — high torque records
    phase4 = by_torque[-120:-20]
    scenario.extend(phase4)

    # Phase 5: RPM instability — records with extreme RPM
    by_rpm_var = sorted(normal, key=lambda r: abs(r["Rotational speed [rpm]"] - 1500))
    phase5 = by_rpm_var[-50:]
    scenario.extend(phase5)

    # Phase 6: Bearing degradation — actual failure records
    if len(failing) >= 50:
        phase6 = failing[:50]
    else:
        phase6 = failing + by_torque[-50 + len(failing):]
        phase6 = phase6[:50]
    scenario.extend(phase6)

    # Convert to telemetry with progressive degradation overlay
    telemetry = []
    total = len(scenario)
    for i, rec in enumerate(scenario):
        base = preprocess_record(rec, i, total)

        # Apply progressive degradation overlay
        progress = i / max(total - 1, 1)

        if i >= 100:  # Phase 2+: vibration ramp
            vib_factor = min(1.0, (i - 100) / 400)
            base["vibration"] = round(base["vibration"] * (1.0 + vib_factor * 2.0), 3)

        if i >= 200:  # Phase 3+: temperature ramp
            temp_factor = min(1.0, (i - 200) / 300)
            base["motor_temp"] = round(base["motor_temp"] + temp_factor * 15.0, 2)

        if i >= 300:  # Phase 4+: current ramp
            curr_factor = min(1.0, (i - 300) / 200)
            base["current"] = round(min(25.0, base["current"] + curr_factor * 8.0), 2)

        if i >= 400:  # Phase 5+: RPM instability
            rpm_factor = min(1.0, (i - 400) / 100)
            rpm_jitter = math.sin(i * 0.7) * rpm_factor * 200
            base["rpm"] = round(max(500, base["rpm"] + rpm_jitter), 1)

        if i >= 450:  # Phase 6: full bearing degradation
            deg_factor = min(1.0, (i - 450) / 50)
            base["vibration"] = round(base["vibration"] * (1.0 + deg_factor * 3.0), 3)
            base["brake"] = round(max(60.0, base["brake"] - deg_factor * 20.0), 2)

        telemetry.append(base)

    logger.info("Built degradation scenario: %d telemetry records in 6 phases", len(telemetry))
    return telemetry
