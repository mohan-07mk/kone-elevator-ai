"""Hardware Devices API Router — Register, Heartbeat, STM32 & Raspberry Pi Telemetry Ingestion."""

from __future__ import annotations

import time
import logging
from typing import Any, Dict, List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.session import get_db
from app.devices.edge_buffer import get_edge_manager, EdgeBufferManager
from app.api.telemetry import ingest_telemetry
from app.schemas.telemetry import TelemetryIngest
from app.ai.runtime import get_ai_runtime

logger = logging.getLogger("elevator_ai.api.devices")

router = APIRouter(prefix="/api/devices", tags=["Hardware Devices"])


class DeviceRegisterRequest(BaseModel):
    device_id: str
    device_type: str = "raspberry-pi"  # "stm32", "raspberry-pi", "simulator"
    building_id: str = "BLD-A"
    elevator_id: str = "KONE-ELEV-001"
    ip_address: Optional[str] = "192.168.1.105"
    firmware_version: str = "v2.1.0-edge"


class DeviceHeartbeatRequest(BaseModel):
    device_id: str
    uptime_seconds: float = 3600.0
    cpu_temp_c: float = 42.5
    ram_usage_mb: float = 128.0
    network_signal_dbm: float = -65.0
    status: str = "online"


class STM32IngestPayload(BaseModel):
    device_id: str = "STM32-ACC-01"
    elevator_id: str = "KONE-ELEV-001"
    raw_accel_x: float = 0.05
    raw_accel_y: float = 0.12
    raw_accel_z: float = 9.81
    analog_temp_raw: int = 1420
    current_adc_raw: int = 850
    voltage_adc_raw: int = 2100
    rpm_pulse_count: int = 1450
    door_switch: int = 0
    timestamp: float = Field(default_factory=time.time)


class RaspberryPiIngestPayload(BaseModel):
    device_id: str = "RPI-GW-001"
    elevator_id: str = "KONE-ELEV-001"
    timestamp: str = Field(default_factory=lambda: time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()))
    motor_temp: float = 48.2
    voltage: float = 402.0
    current: float = 12.4
    power: float = 4984.8
    rpm: float = 1450.0
    vibration: float = 1.45
    brake: float = 95.0
    load: float = 42.0
    humidity: float = 52.0
    door: float = 0.0


@router.post("/register", status_code=status.HTTP_201_CREATED)
async def register_device(req: DeviceRegisterRequest):
    """Registers a hardware device (STM32 sensor node, Raspberry Pi Gateway, Simulator)."""
    mgr = get_edge_manager()
    dev = mgr.register_device(
        device_id=req.device_id,
        device_type=req.device_type,
        building_id=req.building_id,
        elevator_id=req.elevator_id,
        ip_address=req.ip_address,
        firmware_version=req.firmware_version,
    )
    return {"status": "registered", "device": dev}


@router.post("/heartbeat")
async def device_heartbeat(req: DeviceHeartbeatRequest):
    """Updates device heartbeat and edge health diagnostics."""
    mgr = get_edge_manager()
    updated = mgr.update_heartbeat(req.device_id, req.dict())
    return {"status": "ok", "device": updated}


@router.post("/stm32/ingest", status_code=status.HTTP_201_CREATED)
async def ingest_stm32_telemetry(payload: STM32IngestPayload, db: AsyncSession = Depends(get_db)):
    """Ingests raw sensor readings directly from STM32 microcontroller nodes.

    Normalizes ADC raw samples into standard engineering units.
    """
    # 1. Update heartbeat
    mgr = get_edge_manager()
    mgr.update_heartbeat(payload.device_id)

    # 2. Convert raw ADC values to normalized engineering units
    norm_vibration = round(((payload.raw_accel_x**2 + payload.raw_accel_y**2 + (payload.raw_accel_z - 9.81)**2)**0.5), 2)
    norm_temp = round(20.0 + (payload.analog_temp_raw / 4095.0) * 80.0, 1)
    norm_current = round((payload.current_adc_raw / 4095.0) * 30.0, 1)
    norm_voltage = round(380.0 + (payload.voltage_adc_raw / 4095.0) * 40.0, 1)
    norm_power = round(norm_voltage * norm_current, 1)

    telemetry_in = TelemetryIngest(
        device_id=payload.device_id,
        elevator_id=payload.elevator_id,
        motor_temp=norm_temp,
        voltage=norm_voltage,
        current=norm_current,
        power=norm_power,
        rpm=float(payload.rpm_pulse_count),
        vibration=norm_vibration,
        brake=95.0,
        load=40.0,
        humidity=50.0,
        door=float(payload.door_switch)
    )

    # 3. DB storage
    ingest_res = await ingest_telemetry(telemetry_in, db)

    # 4. Trigger Local AI Runtime Inference
    ai_runtime = get_ai_runtime()
    inference_res = ai_runtime.run_inference({
        "motor_temp": norm_temp, "voltage": norm_voltage, "current": norm_current,
        "power": norm_power, "rpm": float(payload.rpm_pulse_count), "vibration": norm_vibration,
        "brake": 95.0, "load": 40.0, "humidity": 50.0, "door": float(payload.door_switch)
    })

    return {
        "status": "ingested",
        "gateway": "STM32",
        "device_id": payload.device_id,
        "records_stored": ingest_res.records_stored,
        "normalized_units": {
            "vibration_mm_s": norm_vibration,
            "motor_temp_c": norm_temp,
            "current_a": norm_current,
            "voltage_v": norm_voltage
        },
        "fault_detected": inference_res.fault_detected,
        "fault_type": inference_res.fault_type,
        "confidence": inference_res.confidence
    }


@router.post("/raspberry-pi/ingest", status_code=status.HTTP_201_CREATED)
async def ingest_raspberry_pi_telemetry(payload: RaspberryPiIngestPayload, db: AsyncSession = Depends(get_db)):
    """Ingests sensor telemetry stream from Raspberry Pi edge gateways."""
    mgr = get_edge_manager()
    mgr.update_heartbeat(payload.device_id)

    telemetry_in = TelemetryIngest(
        device_id=payload.device_id,
        elevator_id=payload.elevator_id,
        motor_temp=payload.motor_temp,
        voltage=payload.voltage,
        current=payload.current,
        power=payload.power,
        rpm=payload.rpm,
        vibration=payload.vibration,
        brake=payload.brake,
        load=payload.load,
        humidity=payload.humidity,
        door=payload.door
    )

    ingest_res = await ingest_telemetry(telemetry_in, db)

    ai_runtime = get_ai_runtime()
    inference_res = ai_runtime.run_inference({
        "motor_temp": payload.motor_temp, "voltage": payload.voltage, "current": payload.current,
        "power": payload.power, "rpm": payload.rpm, "vibration": payload.vibration,
        "brake": payload.brake, "load": payload.load, "humidity": payload.humidity, "door": payload.door
    })

    return {
        "status": "ingested",
        "gateway": "Raspberry-Pi",
        "device_id": payload.device_id,
        "records_stored": ingest_res.records_stored,
        "fault_detected": inference_res.fault_detected,
        "fault_type": inference_res.fault_type,
        "confidence": inference_res.confidence
    }


@router.get("")
async def list_devices():
    """Lists all registered edge devices and hardware nodes."""
    mgr = get_edge_manager()
    devices = mgr.list_devices()

    # Ensure SIM-GATEWAY-001 is included if empty
    if not devices:
        mgr.register_device("SIM-GATEWAY-001", "simulator", "BLD-A", "KONE-ELEV-001")
        devices = mgr.list_devices()

    return devices


@router.get("/{device_id}")
async def get_device(device_id: str):
    """Gets details for a specific edge hardware device."""
    mgr = get_edge_manager()
    dev = mgr.get_device(device_id)
    if not dev:
        raise HTTPException(status_code=404, detail=f"Device {device_id} not registered")
    return dev
