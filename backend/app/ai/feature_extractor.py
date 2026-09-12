"""Feature extraction pipeline for elevator telemetry time-series."""

from __future__ import annotations

import math
from typing import Any, Sequence


def extract_features(window_records: Sequence[dict[str, float]]) -> dict[str, float]:
    """Extract statistical and domain features from a sequence of telemetry frames.
    
    If window_records contains a single frame, window statistical operations fallback to 1-point defaults.
    """
    if not window_records:
        return {}

    latest = window_records[-1]

    # Raw metrics
    motor_temp = latest.get("motor_temp", 45.0)
    voltage = latest.get("voltage", 400.0)
    current = latest.get("current", 12.0)
    power = latest.get("power", 5000.0)
    rpm = latest.get("rpm", 1450.0)
    vibration = latest.get("vibration", 1.5)
    brake = latest.get("brake", 95.0)
    load = latest.get("load", 40.0)
    humidity = latest.get("humidity", 50.0)
    door = latest.get("door", 0.0)

    # 1. Vibration RMS & Peak
    vibrations = [r.get("vibration", 1.5) for r in window_records]
    n = len(vibrations)
    vibration_rms = math.sqrt(sum(v ** 2 for v in vibrations) / n)
    vibration_peak = max(abs(v) for v in vibrations)

    # 2. Rolling mean & std
    vibration_mean = sum(vibrations) / n
    vibration_std = math.sqrt(sum((v - vibration_mean) ** 2 for v in vibrations) / n) if n > 1 else 0.0

    temps = [r.get("motor_temp", 45.0) for r in window_records]
    temp_mean = sum(temps) / n
    temp_std = math.sqrt(sum((t - temp_mean) ** 2 for t in temps) / n) if n > 1 else 0.0

    currents = [r.get("current", 12.0) for r in window_records]
    current_mean = sum(currents) / n

    rpms = [r.get("rpm", 1450.0) for r in window_records]
    rpm_mean = sum(rpms) / n
    rpm_var = sum((r - rpm_mean) ** 2 for r in rpms) / n if n > 1 else 0.0

    # 3. Temperature slope (°C per sample step)
    temp_slope = (temps[-1] - temps[0]) / (n - 1) if n > 1 else 0.0

    # 4. Current deviation from nominal (assume 12.0A nominal)
    current_dev = abs(current - 12.0)

    # 5. Load-normalized current ratio
    norm_load = max(1.0, load)
    load_normalized_current = current / (norm_load / 100.0) if norm_load > 0 else current

    # 6. Sensor correlation (Vibration vs Temp)
    if n > 2 and vibration_std > 1e-4 and temp_std > 1e-4:
        cov = sum((vibrations[i] - vibration_mean) * (temps[i] - temp_mean) for i in range(n)) / n
        vib_temp_corr = cov / (vibration_std * temp_std)
    else:
        vib_temp_corr = 0.0

    return {
        "motor_temp": motor_temp,
        "voltage": voltage,
        "current": current,
        "power": power,
        "rpm": rpm,
        "vibration": vibration,
        "brake": brake,
        "load": load,
        "humidity": humidity,
        "door": door,
        "vibration_rms": round(vibration_rms, 3),
        "vibration_peak": round(vibration_peak, 3),
        "vibration_mean": round(vibration_mean, 3),
        "vibration_std": round(vibration_std, 3),
        "temp_mean": round(temp_mean, 2),
        "temp_std": round(temp_std, 2),
        "temp_slope": round(temp_slope, 4),
        "current_dev": round(current_dev, 2),
        "rpm_var": round(rpm_var, 2),
        "load_normalized_current": round(load_normalized_current, 2),
        "vib_temp_corr": round(vib_temp_corr, 3),
    }
