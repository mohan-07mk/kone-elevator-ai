"""End-to-end vertical slice integration test for KONE-ELEV-001 scenario."""

from __future__ import annotations

import datetime as dt
import pytest
from sqlalchemy import select, desc

from app.schemas.telemetry import TelemetryIngest
from app.api.telemetry import ingest_telemetry
from app.ai.pipeline import get_ai_pipeline
from app.models.models import AlertRecord, MaintenanceTask, Technician
from app.ai.runtime import get_ai_runtime


@pytest.mark.asyncio
async def test_full_e2e_bearing_degradation_flow(db_session):
    """Validate full flow: Normal telemetry -> Degradation -> AI Fault -> RCA -> Health -> Alert -> Task."""

    # 1. Ingest NORMAL Telemetry Frame
    normal_payload = TelemetryIngest(
        device_id="SIM-GATEWAY-001",
        elevator_id="KONE-ELEV-001",
        motor_temp=42.0,
        voltage=400.0,
        current=11.5,
        power=4600.0,
        rpm=1450.0,
        vibration=1.2,
        brake=95.0,
        load=40.0,
        humidity=50.0,
        door=0.0
    )
    res1 = await ingest_telemetry(normal_payload, db_session)
    assert res1.records_stored == 10

    # AI Process Nominal
    pipeline = get_ai_pipeline()
    normal_frame = {
        "motor_temp": 42.0, "voltage": 400.0, "current": 11.5, "power": 4600.0,
        "rpm": 1450.0, "vibration": 1.2, "brake": 95.0, "load": 40.0, "humidity": 50.0, "door": 0.0
    }
    res_ai_normal = await pipeline.process_telemetry(db_session, "KONE-ELEV-001", [normal_frame])
    assert res_ai_normal["inference"]["fault_detected"] is False

    # 2. Inject BEARING_DEGRADATION Anomaly Frames
    degraded_frames = []
    for i in range(5):
        t_offset = dt.datetime.now(dt.timezone.utc) + dt.timedelta(seconds=i*3)
        fault_payload = TelemetryIngest(
            device_id="SIM-GATEWAY-001",
            elevator_id="KONE-ELEV-001",
            timestamp=t_offset.isoformat(),
            motor_temp=78.5 + (i * 2.0),
            voltage=395.0,
            current=18.5 + (i * 0.8),
            power=7300.0,
            rpm=1410.0 - (i * 5.0),
            vibration=8.8 + (i * 1.2),
            brake=90.0,
            load=55.0,
            humidity=48.0,
            door=0.0
        )
        await ingest_telemetry(fault_payload, db_session)
        degraded_frames.append({
            "motor_temp": 78.5 + (i * 2.0), "voltage": 395.0, "current": 18.5 + (i * 0.8),
            "power": 7300.0, "rpm": 1410.0 - (i * 5.0), "vibration": 8.8 + (i * 1.2),
            "brake": 90.0, "load": 55.0, "humidity": 48.0, "door": 0.0
        })

    # 3. AI Fault Detection Processing
    ai_out = await pipeline.process_telemetry(db_session, "KONE-ELEV-001", degraded_frames)
    inf = ai_out["inference"]
    assert inf["fault_detected"] is True
    assert inf["fault_type"] == "Bearing Degradation"

    # 4. Root Cause Analysis (RCA) Verification
    rca = ai_out["rca"]
    assert "Bearing" in rca["affected_component"] or "Drive" in rca["affected_component"]

    # 5. Elevator Health & RUL Verification
    health_data = ai_out["health"]
    pred_data = ai_out["predictive"]
    assert health_data["overall_health"] < 80
    assert pred_data["rul_hours"] > 0

    # 6. Verify Alert Generation in DB
    stmt_alert = select(AlertRecord).where(AlertRecord.elevator_id == "KONE-ELEV-001").order_by(desc(AlertRecord.created_at))
    res_alert = await db_session.execute(stmt_alert)
    alerts = res_alert.scalars().all()
    assert len(alerts) > 0

    # 7. Hardware AI Status Audit Verification
    runtime = get_ai_runtime()
    status = runtime.get_status()
    assert status.status in ("active", "fallback")
