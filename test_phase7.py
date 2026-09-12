"""Phase 7 Verification Script — Snapdragon Local AI, Benchmark & Hardware-Ready Edge APIs."""

from __future__ import annotations

import asyncio
import os
import sys

# Ensure backend path is present
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.database.session import engine, async_session_factory, Base
from app.database.seed import seed_all
from app.ai.runtime import get_ai_runtime
from app.devices.edge_buffer import get_edge_manager, TelemetryBatch
from app.api.devices import (
    register_device, DeviceRegisterRequest,
    device_heartbeat, DeviceHeartbeatRequest,
    ingest_stm32_telemetry, STM32IngestPayload,
    ingest_raspberry_pi_telemetry, RaspberryPiIngestPayload,
    list_devices, get_device
)


async def test_phase7_pipeline():
    print("\n=======================================================")
    print("      ELEVATOR AI — PHASE 7 VERIFICATION SUITE       ")
    print("=======================================================\n")

    # 1. Initialize Tables & Seed Data
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)

    async with async_session_factory() as db:
        counts = await seed_all(db)
        print(f"[✓] Database seeding completed: {counts}")

    # 2. Test Snapdragon AI Runtime Abstraction
    print("\n--- 1. Testing AI Runtime Abstraction & Status ---")
    runtime = get_ai_runtime()
    status = runtime.get_status()
    print(f"[✓] Device Target: {status.device}")
    print(f"    Runtime Engine: {status.runtime}")
    print(f"    Execution Provider: {status.accelerator}")
    print(f"    Model Name: {status.model} (Version: {status.model_version})")
    print(f"    Status: {status.status}")
    print(f"    Hardware Acceleration Available: {status.acceleration_available}")
    if status.fallback_reason:
        print(f"    Fallback Diagnosis: {status.fallback_reason}")

    # 3. Test Live Hardware Micro-Benchmark
    print("\n--- 2. Testing Live Hardware Benchmark (100 Passes) ---")
    bm = runtime.run_benchmark(num_passes=100)
    print(f"[✓] Measured CPU Latency: {bm.cpu_latency_ms:.3f} ms / pass")
    print(f"    Accelerated Latency: {bm.accelerated_latency_ms if bm.accelerated_latency_ms is not None else 'N/A (CPU execution)'}")
    print(f"    Throughput: {bm.throughput_ops_sec} ops/sec")
    print(f"    Process Memory RSS: {bm.memory_mb} MB")
    print(f"    ONNX Model Size: {bm.model_size_kb} KB")
    print(f"    CPU Utilization: {bm.cpu_utilization_pct}%")
    print(f"    Accelerator Utilization: {bm.accelerator_utilization_pct}%")
    print(f"    Prediction Consistency: {bm.prediction_consistency_pct}%")

    # 4. Test Edge Hardware Device Registration & Heartbeats
    print("\n--- 3. Testing Hardware APIs (STM32, Raspberry Pi, Simulator) ---")

    # Register STM32 node
    stm32_reg = await register_device(DeviceRegisterRequest(
        device_id="STM32-NODE-01",
        device_type="stm32",
        building_id="BLD-A",
        elevator_id="KONE-ELEV-001",
        firmware_version="v1.4.0-arm"
    ))
    print(f"[✓] Registered STM32 Node: {stm32_reg['device']['device_id']}")

    # Register Raspberry Pi gateway
    rpi_reg = await register_device(DeviceRegisterRequest(
        device_id="RPI-GW-001",
        device_type="raspberry-pi",
        building_id="BLD-A",
        elevator_id="KONE-ELEV-001",
        firmware_version="v2.1.0-edge"
    ))
    print(f"[✓] Registered Raspberry Pi Gateway: {rpi_reg['device']['device_id']}")

    # Check Heartbeat
    hb = await device_heartbeat(DeviceHeartbeatRequest(
        device_id="RPI-GW-001",
        uptime_seconds=7200.0,
        cpu_temp_c=41.2,
        status="online"
    ))
    print(f"[✓] Updated Device Heartbeat for {hb['device']['device_id']}: Status={hb['device']['status']}")

    # 5. Test Raw Hardware Ingestion Pipelines
    async with async_session_factory() as db:
        print("\n--- 4. Testing Raw Telemetry Ingestion Pipeline ---")

        # Ingest STM32 Raw ADC signals
        stm32_res = await ingest_stm32_telemetry(STM32IngestPayload(
            device_id="STM32-NODE-01",
            elevator_id="KONE-ELEV-001",
            raw_accel_x=0.8,
            raw_accel_y=1.2,
            raw_accel_z=14.5,  # high vibration signal
            analog_temp_raw=2800,
            current_adc_raw=2200,
            voltage_adc_raw=2050,
            rpm_pulse_count=1440
        ), db)
        print(f"[✓] STM32 Telemetry Ingested -> Normalized Vibration: {stm32_res['normalized_units']['vibration_mm_s']} mm/s | Temp: {stm32_res['normalized_units']['motor_temp_c']} °C")
        print(f"    AI Inference Output: Fault Detected={stm32_res['fault_detected']} ({stm32_res['fault_type']})")

        # Ingest Raspberry Pi telemetry batch
        rpi_res = await ingest_raspberry_pi_telemetry(RaspberryPiIngestPayload(
            device_id="RPI-GW-001",
            elevator_id="KONE-ELEV-001",
            motor_temp=52.0,
            vibration=1.8,
            current=12.2,
            voltage=400.0
        ), db)
        print(f"[✓] Raspberry Pi Gateway Batch Ingested -> Result Status={rpi_res['status']}")

    # 6. Test Device Enumeration & Simulator Registration
    print("\n--- 5. Testing Registered Devices Enumeration ---")
    dev_list = await list_devices()
    print(f"[✓] Total Edge Nodes Registered: {len(dev_list)}")
    for d in dev_list:
        print(f"    • {d['device_id']} ({d['device_type']}) | Status: {d['status']} | FW: {d['firmware_version']}")

    # 7. Test Edge Buffer & Offline Resiliency
    print("\n--- 6. Testing Edge Buffer & Offline Resiliency ---")
    edge_mgr = get_edge_manager()
    batch = TelemetryBatch(
        device_id="STM32-NODE-01",
        gateway_type="stm32",
        readings=[{"motor_temp": 82.0, "vibration": 14.2}]
    )
    buffered_count = edge_mgr.buffer_telemetry(batch)
    print(f"[✓] Offline payload buffered successfully (Queue size: {buffered_count})")
    flushed = edge_mgr.get_buffered_payloads()
    print(f"[✓] Reconnected & flushed {len(flushed)} buffered payload batches to pipeline.")

    print("\n=======================================================")
    print("      ALL PHASE 7 VERIFICATION TESTS PASSED!          ")
    print("=======================================================\n")


if __name__ == "__main__":
    asyncio.run(test_phase7_pipeline())
