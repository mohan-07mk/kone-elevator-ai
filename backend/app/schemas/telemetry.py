"""Pydantic schemas for telemetry ingestion and simulator control."""

from __future__ import annotations

import datetime as dt
from typing import Optional

from pydantic import BaseModel, Field


# ════════════════════════════════════════════════════════════
#  TELEMETRY INGESTION
# ════════════════════════════════════════════════════════════
class TelemetryIngest(BaseModel):
    """Sensor contract for telemetry ingestion."""
    device_id: str = Field(default="SIM-GATEWAY-001")
    elevator_id: str = Field(default="KONE-ELEV-001")
    timestamp: Optional[str] = None
    motor_temp: float = Field(ge=-50, le=200)
    voltage: float = Field(ge=0, le=500)
    current: float = Field(ge=0, le=100)
    power: float = Field(ge=0, le=50000)
    rpm: float = Field(ge=0, le=5000)
    vibration: float = Field(ge=0, le=100)
    brake: float = Field(ge=0, le=200)
    load: float = Field(ge=0, le=100)
    humidity: float = Field(ge=0, le=100)
    door: float = Field(ge=0, le=1)


class TelemetryResponse(BaseModel):
    """Response after telemetry ingestion."""
    status: str = "ok"
    records_stored: int
    elevator_id: str
    timestamp: str


class SensorLatest(BaseModel):
    """Latest sensor readings for an elevator."""
    elevator_id: str
    timestamp: Optional[str] = None
    motor_temp: Optional[float] = None
    voltage: Optional[float] = None
    current: Optional[float] = None
    power: Optional[float] = None
    rpm: Optional[float] = None
    vibration: Optional[float] = None
    brake: Optional[float] = None
    load: Optional[float] = None
    humidity: Optional[float] = None
    door: Optional[float] = None


class SensorHistoryPoint(BaseModel):
    """Single point in sensor history."""
    value: float
    recorded_at: str
    is_anomaly: bool = False


class SensorHistory(BaseModel):
    """Sensor history response."""
    elevator_id: str
    sensor_key: Optional[str] = None
    count: int
    data: list[SensorHistoryPoint]


# ════════════════════════════════════════════════════════════
#  SIMULATOR CONTROL
# ════════════════════════════════════════════════════════════
class SimulatorStartRequest(BaseModel):
    elevator_id: str = "KONE-ELEV-001"
    scenario: str = "BEARING_DEGRADATION"
    replay_speed: float = Field(default=1.0, ge=0.1, le=10.0)


class SimulatorScenarioRequest(BaseModel):
    scenario: str
    elevator_id: Optional[str] = None
    replay_speed: Optional[float] = Field(default=None, ge=0.1, le=10.0)


class SimulatorStatusResponse(BaseModel):
    state: str
    scenario: str
    elevator_id: str
    device_id: str
    position: int
    total_records: int
    replay_speed: float
    records_emitted: int
    mode: str
    started_at: Optional[str] = None
    error: Optional[str] = None
