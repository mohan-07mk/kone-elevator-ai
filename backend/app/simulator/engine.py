"""Deterministic Simulation Engine — owns all telemetry state.

The simulator is a singleton that:
- Loads and preprocesses the dataset on init
- Maintains playback position, speed, and scenario state
- Produces telemetry on-demand (no frontend randomness)
- Supports pause/resume/reset/replay
"""

from __future__ import annotations

import asyncio
import datetime as dt
import logging
from enum import Enum
from typing import Any, Optional

from pydantic import BaseModel

from app.simulator.dataset_loader import load_raw_dataset, validate_dataset
from app.simulator.preprocessing import (
    build_degradation_scenario,
    preprocess_dataset,
)

logger = logging.getLogger("elevator_ai.simulator")


class Scenario(str, Enum):
    NORMAL = "NORMAL"
    WARNING = "WARNING"
    BEARING_DEGRADATION = "BEARING_DEGRADATION"
    MOTOR_OVERHEATING = "MOTOR_OVERHEATING"
    DOOR_ALIGNMENT = "DOOR_ALIGNMENT"


class SimulatorState(str, Enum):
    IDLE = "IDLE"
    RUNNING = "RUNNING"
    PAUSED = "PAUSED"
    COMPLETED = "COMPLETED"
    ERROR = "ERROR"


class SimulatorStatus(BaseModel):
    state: SimulatorState
    scenario: Scenario
    elevator_id: str
    device_id: str
    position: int
    total_records: int
    replay_speed: float
    records_emitted: int
    mode: str  # "Simulation Mode" or "Dataset Replay"
    started_at: Optional[dt.datetime] = None
    error: Optional[str] = None


class TelemetryRecord(BaseModel):
    device_id: str
    elevator_id: str
    timestamp: str
    motor_temp: float
    voltage: float
    current: float
    power: float
    rpm: float
    vibration: float
    brake: float
    load: float
    humidity: float
    door: float


class SimulationEngine:
    """Deterministic simulation engine.

    Owns all telemetry state. The frontend never generates sensor values.
    """

    def __init__(self) -> None:
        self._state = SimulatorState.IDLE
        self._scenario = Scenario.NORMAL
        self._elevator_id = "KONE-ELEV-001"
        self._device_id = "SIM-GATEWAY-001"
        self._replay_speed = 1.0
        self._position = 0
        self._records_emitted = 0
        self._started_at: Optional[dt.datetime] = None
        self._error: Optional[str] = None

        # Dataset
        self._raw_data: list[dict[str, Any]] = []
        self._telemetry: list[dict[str, float]] = []
        self._scenario_data: dict[Scenario, list[dict[str, float]]] = {}

        # Playback task
        self._task: Optional[asyncio.Task] = None
        self._pause_event = asyncio.Event()
        self._pause_event.set()  # Not paused initially

        # Callback for emitting telemetry
        self._on_telemetry: Optional[Any] = None

        # Track if dataset is loaded
        self._loaded = False

    async def load_dataset(self) -> None:
        """Load and preprocess the dataset. Thread-safe for async."""
        if self._loaded:
            return

        logger.info("Loading AI4I dataset...")
        try:
            raw = load_raw_dataset()
            valid = validate_dataset(raw)
            self._raw_data = valid
            self._telemetry = preprocess_dataset(valid)

            # Build scenario-specific datasets
            self._build_scenarios(valid)

            self._loaded = True
            logger.info("Dataset loaded: %d records, %d scenarios",
                        len(self._telemetry), len(self._scenario_data))
        except Exception as exc:
            self._state = SimulatorState.ERROR
            self._error = str(exc)
            logger.error("Failed to load dataset: %s", exc)
            raise

    def _build_scenarios(self, records: list[dict[str, Any]]) -> None:
        """Build telemetry sequences for each scenario."""
        # BEARING_DEGRADATION: The full demo scenario
        self._scenario_data[Scenario.BEARING_DEGRADATION] = build_degradation_scenario(records)

        # NORMAL: First 500 healthy records
        normal_recs = [r for r in records if r.get("Machine failure", 0) == 0][:500]
        self._scenario_data[Scenario.NORMAL] = preprocess_dataset(normal_recs)

        # WARNING: Records approaching failure (high tool wear)
        warning_recs = sorted(
            [r for r in records if r.get("Machine failure", 0) == 0],
            key=lambda r: r["Tool wear [min]"],
            reverse=True
        )[:300]
        self._scenario_data[Scenario.WARNING] = preprocess_dataset(warning_recs)

        # MOTOR_OVERHEATING: Records with high process temperature
        hot_recs = sorted(records, key=lambda r: r["Process temperature [K]"], reverse=True)[:400]
        hot_telem = preprocess_dataset(hot_recs)
        # Apply temperature escalation overlay
        for i, t in enumerate(hot_telem):
            factor = i / max(len(hot_telem) - 1, 1)
            t["motor_temp"] = round(t["motor_temp"] + factor * 20.0, 2)
        self._scenario_data[Scenario.MOTOR_OVERHEATING] = hot_telem

        # DOOR_ALIGNMENT: Normal records with door anomaly pattern
        door_recs = normal_recs[:300]
        door_telem = preprocess_dataset(door_recs)
        import math
        for i, t in enumerate(door_telem):
            # Door gets stuck intermittently
            if i > 100:
                stuck_prob = (i - 100) / 200
                if math.sin(i * 0.3) > (1.0 - stuck_prob):
                    t["door"] = 1.0  # Stuck open
            if i > 200:
                t["vibration"] = round(t["vibration"] * 1.3, 3)  # Misalignment vibration
        self._scenario_data[Scenario.DOOR_ALIGNMENT] = door_telem

    @property
    def status(self) -> SimulatorStatus:
        """Return current simulator status."""
        active_data = self._get_active_data()
        return SimulatorStatus(
            state=self._state,
            scenario=self._scenario,
            elevator_id=self._elevator_id,
            device_id=self._device_id,
            position=self._position,
            total_records=len(active_data),
            replay_speed=self._replay_speed,
            records_emitted=self._records_emitted,
            mode="Dataset Replay" if self._loaded else "Simulation Mode",
            started_at=self._started_at,
            error=self._error,
        )

    def _get_active_data(self) -> list[dict[str, float]]:
        """Get the telemetry data for the current scenario."""
        return self._scenario_data.get(self._scenario, self._telemetry)

    def get_current_telemetry(self) -> Optional[TelemetryRecord]:
        """Get the telemetry record at the current position."""
        data = self._get_active_data()
        if not data or self._position >= len(data):
            return None

        values = data[self._position]
        now = dt.datetime.now(dt.timezone.utc)

        return TelemetryRecord(
            device_id=self._device_id,
            elevator_id=self._elevator_id,
            timestamp=now.isoformat(),
            **values,
        )

    async def start(
        self,
        on_telemetry=None,
        elevator_id: Optional[str] = None,
        scenario: Optional[Scenario] = None,
        replay_speed: Optional[float] = None,
    ) -> SimulatorStatus:
        """Start the simulation playback."""
        logger.info("[SIMULATOR] START requested: scenario=%s, speed=%s, elevator=%s", scenario, replay_speed, elevator_id)

        if not self._loaded:
            await self.load_dataset()

        old_state_str = self._state.value if hasattr(self._state, "value") else str(self._state)

        if elevator_id:
            self._elevator_id = elevator_id
        if scenario:
            self._scenario = scenario
        if replay_speed:
            self._replay_speed = max(0.1, min(10.0, replay_speed))

        # Cancel existing playback task if any to ensure exactly one playback loop runs
        if self._task and not self._task.done():
            logger.info("[SIMULATOR] Cancelling previous active playback task")
            self._task.cancel()
            try:
                await self._task
            except (asyncio.CancelledError, Exception):
                pass

        self._on_telemetry = on_telemetry
        self._position = 0
        self._records_emitted = 0
        self._state = SimulatorState.RUNNING
        self._started_at = dt.datetime.now(dt.timezone.utc)
        self._error = None
        self._pause_event.set()

        logger.info("[SIMULATOR] State: %s -> RUNNING", old_state_str)

        # Start playback task
        self._task = asyncio.create_task(self._playback_loop())

        return self.status

    async def pause(self) -> SimulatorStatus:
        """Pause the simulation."""
        if self._state == SimulatorState.RUNNING:
            old_state_str = self._state.value
            self._state = SimulatorState.PAUSED
            self._pause_event.clear()
            logger.info("[SIMULATOR] State: %s -> PAUSED at position %d", old_state_str, self._position)
        return self.status

    async def resume(self) -> SimulatorStatus:
        """Resume the simulation."""
        if self._state == SimulatorState.PAUSED:
            old_state_str = self._state.value
            self._state = SimulatorState.RUNNING
            self._pause_event.set()
            logger.info("[SIMULATOR] State: %s -> RUNNING at position %d", old_state_str, self._position)
        return self.status

    async def reset(self) -> SimulatorStatus:
        """Reset the simulation to the beginning."""
        # Cancel running task
        if self._task and not self._task.done():
            self._task.cancel()
            try:
                await self._task
            except asyncio.CancelledError:
                pass

        old_state_str = self._state.value if hasattr(self._state, "value") else str(self._state)
        self._state = SimulatorState.IDLE
        self._position = 0
        self._records_emitted = 0
        self._started_at = None
        self._error = None
        self._pause_event.set()
        logger.info("[SIMULATOR] State: %s -> IDLE (Reset completed)", old_state_str)
        return self.status

    async def set_scenario(
        self,
        scenario: Scenario,
        elevator_id: Optional[str] = None,
        replay_speed: Optional[float] = None,
    ) -> SimulatorStatus:
        """Change scenario (resets playback)."""
        await self.reset()
        self._scenario = scenario
        if elevator_id:
            self._elevator_id = elevator_id
        if replay_speed:
            self._replay_speed = max(0.1, min(10.0, replay_speed))
        logger.info("[SIMULATOR] Scenario changed to %s", scenario)
        return self.status

    async def _playback_loop(self) -> None:
        """Main playback loop — emits telemetry records at replay speed."""
        logger.info("[SIMULATOR] Playback loop started")
        data = self._get_active_data()
        base_interval = 1.0  # 1 second per record at 1x speed

        try:
            while self._position < len(data):
                # Check for pause
                await self._pause_event.wait()

                if self._state not in (SimulatorState.RUNNING,):
                    break

                # Emit telemetry
                record = self.get_current_telemetry()
                if record:
                    logger.info(
                        "[SIMULATOR] Telemetry tick: %s pos=%d/%d motor_temp=%.1f vibration=%.3f voltage=%.1f",
                        record.elevator_id, self._position + 1, len(data), record.motor_temp, record.vibration, record.voltage
                    )
                    if self._on_telemetry:
                        try:
                            await self._on_telemetry(record)
                        except Exception as exc:
                            logger.error("[SIMULATOR] Telemetry callback exception: %s", exc, exc_info=True)

                self._position += 1
                self._records_emitted += 1

                # Wait for next record based on replay speed
                interval = base_interval / self._replay_speed
                await asyncio.sleep(interval)

            # Completed
            if self._position >= len(data):
                old_state_str = self._state.value
                self._state = SimulatorState.COMPLETED
                logger.info("[SIMULATOR] State: %s -> COMPLETED (%d records emitted)", old_state_str, self._records_emitted)

        except asyncio.CancelledError:
            logger.info("[SIMULATOR] Playback loop cancelled")
            raise
        except Exception as exc:
            old_state_str = self._state.value if hasattr(self._state, "value") else str(self._state)
            self._state = SimulatorState.ERROR
            self._error = str(exc)
            logger.error("[SIMULATOR] State: %s -> ERROR: %s", old_state_str, exc, exc_info=True)


# ── Singleton ────────────────────────────────────────────────
_engine: Optional[SimulationEngine] = None


def get_simulator() -> SimulationEngine:
    """Get or create the singleton simulation engine."""
    global _engine
    if _engine is None:
        _engine = SimulationEngine()
    return _engine
