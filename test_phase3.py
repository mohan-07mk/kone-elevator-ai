"""Phase 3 Integration Test -- Dataset Pipeline + Simulator + Telemetry API.

Tests everything end-to-end using SQLite (since PostgreSQL may not be running).
"""

import asyncio
import os
import sys
import glob

# Force UTF-8 output
os.environ["PYTHONIOENCODING"] = "utf-8"

# Resolve paths BEFORE setting env vars
BACKEND_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BACKEND_DIR, "test_phase3.db")

# Clean up old test DB first
for f in glob.glob(os.path.join(BACKEND_DIR, "test_phase3.db*")):
    try:
        os.remove(f)
    except Exception:
        pass

# Use SQLite for testing
os.environ["DATABASE_URL"] = f"sqlite+aiosqlite:///{DB_PATH}"
os.environ["DATABASE_URL_SYNC"] = f"sqlite:///{DB_PATH}"
os.environ["JWT_SECRET_KEY"] = "test-secret-key-for-phase3-testing"
os.environ["ADMIN_EMAIL"] = "mohan@elevatorai.io"
os.environ["ADMIN_PASSWORD"] = "test-password"

# Clear lru_cache in case any module was pre-loaded
try:
    from app.core.config import get_settings
    get_settings.cache_clear()
except Exception:
    pass

# Add backend to path
sys.path.insert(0, BACKEND_DIR)


def ok(msg):
    print(f"  [OK] {msg}", flush=True)


def fail(msg):
    print(f"  [FAIL] {msg}", flush=True)


async def run_tests():
    """Run all Phase 3 integration tests."""
    print("=" * 70, flush=True)
    print("  ELEVATOR AI -- PHASE 3 INTEGRATION TEST", flush=True)
    print("=" * 70, flush=True)

    raw = None
    valid = None
    total_in_db = 0
    expected_keys = set()

    # -- Test 1: Dataset Loading -----------------------------------------
    print("\n[TEST 1] Dataset Loading...", flush=True)
    try:
        from app.simulator.dataset_loader import load_raw_dataset, validate_dataset
        raw = load_raw_dataset()
        ok(f"Loaded {len(raw)} raw records")
        assert len(raw) > 9000, f"Expected 10000+ records, got {len(raw)}"

        valid = validate_dataset(raw)
        ok(f"Validated: {len(valid)} valid records")
        assert len(valid) > 9000, f"Expected most records valid, got {len(valid)}"

        # Show sample record
        sample = raw[0]
        ok(f"Sample keys: {list(sample.keys())}")
        print(f"    Air temp: {sample.get('Air temperature [K]')} K", flush=True)
        print(f"    RPM: {sample.get('Rotational speed [rpm]')} rpm", flush=True)
        print(f"    Torque: {sample.get('Torque [Nm]')} Nm", flush=True)
    except Exception as e:
        fail(f"Dataset loading: {e}")
        import traceback
        traceback.print_exc()
        return

    # -- Test 2: Preprocessing Pipeline ----------------------------------
    print("\n[TEST 2] Preprocessing Pipeline...", flush=True)
    try:
        from app.simulator.preprocessing import preprocess_dataset, build_degradation_scenario
        telemetry = preprocess_dataset(valid[:100])
        ok(f"Preprocessed {len(telemetry)} records")

        sample = telemetry[0]
        ok(f"Sensor keys: {list(sample.keys())}")
        expected_keys = {"motor_temp", "voltage", "current", "power", "rpm",
                         "vibration", "brake", "load", "humidity", "door"}
        assert set(sample.keys()) == expected_keys
        ok("All 10 sensor contract fields present")

        # Build degradation scenario
        scenario = build_degradation_scenario(valid)
        ok(f"Degradation scenario: {len(scenario)} records")
        assert len(scenario) == 500

        # Verify degradation pattern
        phase1_avg_vib = sum(s["vibration"] for s in scenario[:50]) / 50
        phase6_avg_vib = sum(s["vibration"] for s in scenario[460:500]) / 40
        ok(f"Phase 1 avg vibration: {phase1_avg_vib:.3f} mm/s")
        ok(f"Phase 6 avg vibration: {phase6_avg_vib:.3f} mm/s")
        assert phase6_avg_vib > phase1_avg_vib
        ok("Vibration increases from Phase 1 -> Phase 6")
    except Exception as e:
        fail(f"Preprocessing: {e}")
        import traceback
        traceback.print_exc()
        return

    # -- Test 3: FastAPI App + API Tests ---------------------------------
    print("\n[TEST 3] FastAPI Application + API Tests...", flush=True)
    try:
        # First, explicitly create all tables
        from app.database.session import Base, engine, async_session_factory
        from app.database.seed import seed_all

        print("  Creating database tables...", flush=True)
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        ok("Database tables created")

        # Seed data
        async with async_session_factory() as session:
            counts = await seed_all(session)
            ok(f"Seed data: {counts}")

        # Now test APIs
        from app.main import app
        import httpx
        from httpx import ASGITransport

        transport = ASGITransport(app=app)
        async with httpx.AsyncClient(transport=transport, base_url="http://test") as client:

            # Root endpoint
            resp = await client.get("/")
            assert resp.status_code == 200
            data = resp.json()
            ok(f"Root: {data['app']} v{data['version']}")

            # -- Telemetry Ingest ----------------------------------------
            print("\n[TEST 3a] Telemetry Ingestion API...", flush=True)
            telemetry_payload = {
                "device_id": "SIM-GATEWAY-001",
                "elevator_id": "KONE-ELEV-001",
                "timestamp": "2026-09-10T12:00:00+00:00",
                "motor_temp": 45.2,
                "voltage": 395.5,
                "current": 12.3,
                "power": 4850.0,
                "rpm": 1450.0,
                "vibration": 2.1,
                "brake": 95.0,
                "load": 45.0,
                "humidity": 52.0,
                "door": 0.0,
            }
            resp = await client.post("/api/sensors/ingest", json=telemetry_payload)
            assert resp.status_code == 200, f"Ingest failed: {resp.status_code} {resp.text}"
            data = resp.json()
            ok(f"Ingested {data['records_stored']} sensor readings for {data['elevator_id']}")
            assert data["records_stored"] == 10

            # Ingest a second reading
            telemetry_payload["timestamp"] = "2026-09-10T12:01:00+00:00"
            telemetry_payload["motor_temp"] = 47.8
            telemetry_payload["vibration"] = 2.5
            resp = await client.post("/api/sensors/ingest", json=telemetry_payload)
            assert resp.status_code == 200
            ok("Ingested second telemetry batch")

            # -- Sensor Latest -------------------------------------------
            print("\n[TEST 3b] Sensor Latest API...", flush=True)
            resp = await client.get("/api/elevators/KONE-ELEV-001/sensors/latest")
            assert resp.status_code == 200
            data = resp.json()
            ok(f"Latest sensors for {data['elevator_id']}:")
            print(f"    motor_temp={data['motor_temp']}, vibration={data['vibration']}, rpm={data['rpm']}", flush=True)
            assert data["motor_temp"] == 47.8
            assert data["vibration"] == 2.5

            # -- Sensor History ------------------------------------------
            print("\n[TEST 3c] Sensor History API...", flush=True)
            resp = await client.get("/api/elevators/KONE-ELEV-001/sensors/history?limit=50")
            assert resp.status_code == 200
            data = resp.json()
            ok(f"History: {data['count']} readings for {data['elevator_id']}")
            assert data["count"] == 20  # 10 sensors * 2 readings

            # Single sensor history
            resp = await client.get("/api/elevators/KONE-ELEV-001/sensors/vibration/history")
            assert resp.status_code == 200
            data = resp.json()
            ok(f"Vibration history: {data['count']} points")
            assert data["count"] == 2
            assert data["sensor_key"] == "vibration"

            # -- Simulator Status ----------------------------------------
            print("\n[TEST 3d] Simulator Control API...", flush=True)
            resp = await client.get("/api/simulator/status")
            assert resp.status_code == 200
            data = resp.json()
            ok(f"Simulator status: state={data['state']}, mode={data['mode']}")

            # Start simulator
            resp = await client.post("/api/simulator/start", json={
                "elevator_id": "KONE-ELEV-001",
                "scenario": "BEARING_DEGRADATION",
                "replay_speed": 10.0,
            })
            assert resp.status_code == 200
            data = resp.json()
            ok(f"Started: state={data['state']}, scenario={data['scenario']}")
            assert data["state"] == "RUNNING"
            assert data["scenario"] == "BEARING_DEGRADATION"

            # Wait for a few records to be emitted
            await asyncio.sleep(1.5)

            # Check status
            resp = await client.get("/api/simulator/status")
            data = resp.json()
            emitted = data["records_emitted"]
            ok(f"After 1.5s at 10x: {emitted} records emitted")
            assert emitted > 0

            # Pause
            resp = await client.post("/api/simulator/pause")
            assert resp.status_code == 200
            data = resp.json()
            ok(f"Paused: state={data['state']}")
            assert data["state"] == "PAUSED"

            # Resume
            resp = await client.post("/api/simulator/resume")
            assert resp.status_code == 200
            data = resp.json()
            ok(f"Resumed: state={data['state']}")
            assert data["state"] == "RUNNING"

            # Reset + change scenario
            resp = await client.post("/api/simulator/reset")
            assert resp.status_code == 200

            resp = await client.post("/api/simulator/scenario", json={
                "scenario": "MOTOR_OVERHEATING",
            })
            assert resp.status_code == 200
            data = resp.json()
            ok(f"Scenario changed: {data['scenario']}")
            assert data["scenario"] == "MOTOR_OVERHEATING"

            # Reset
            resp = await client.post("/api/simulator/reset")
            assert resp.status_code == 200
            data = resp.json()
            ok(f"Reset: state={data['state']}, position={data['position']}")
            assert data["state"] == "IDLE"

            # -- DB Verification -----------------------------------------
            print("\n[TEST 4] Database Telemetry Verification...", flush=True)
            resp = await client.get("/api/elevators/KONE-ELEV-001/sensors/history?limit=1000")
            data = resp.json()
            total_in_db = data["count"]
            ok(f"Total sensor readings in DB for KONE-ELEV-001: {total_in_db}")
            assert total_in_db >= 20

            resp = await client.get("/api/elevators/KONE-ELEV-001/sensors/motor_temp/history?limit=100")
            data = resp.json()
            motor_temps = [p["value"] for p in data["data"]]
            ok(f"Motor temp readings in DB: {len(motor_temps)}")
            print(f"    Latest values: {motor_temps[:5]}", flush=True)
            assert len(motor_temps) >= 2

    except Exception as e:
        fail(f"API tests: {e}")
        import traceback
        traceback.print_exc()
        try:
            from app.simulator.engine import get_simulator
            await get_simulator().reset()
        except Exception:
            pass
        return

    # -- Final Report ---------------------------------------------------
    print("\n" + "=" * 70, flush=True)
    print("  PHASE 3 -- ALL TESTS PASSED", flush=True)
    print("=" * 70, flush=True)
    print(f"""
  Dataset:        AI4I 2020 Predictive Maintenance (UCI ML Repository)
  License:        CC BY 4.0
  Raw records:    {len(raw) if raw else 'N/A'}
  Valid records:  {len(valid) if valid else 'N/A'}
  Sensor fields:  {', '.join(sorted(expected_keys))}

  Simulator:
    Scenarios:    NORMAL, WARNING, BEARING_DEGRADATION, MOTOR_OVERHEATING, DOOR_ALIGNMENT
    Demo:         KONE-ELEV-001 bearing degradation (6 phases, 500 records)
    Deterministic: Yes (backend owns all telemetry state)

  APIs tested:
    POST /api/sensors/ingest                          [OK]
    GET  /api/elevators/id/sensors/latest              [OK]
    GET  /api/elevators/id/sensors/history              [OK]
    GET  /api/elevators/id/sensors/sensor/history       [OK]
    POST /api/simulator/start                          [OK]
    POST /api/simulator/pause                          [OK]
    POST /api/simulator/resume                         [OK]
    POST /api/simulator/reset                          [OK]
    POST /api/simulator/scenario                       [OK]
    GET  /api/simulator/status                         [OK]

  Database:       Telemetry verified in SQLite (PostgreSQL equivalent)
  Records in DB:  {total_in_db}+ sensor readings
""", flush=True)

    try:
        from app.simulator.engine import get_simulator
        await get_simulator().reset()
    except Exception:
        pass


if __name__ == "__main__":
    asyncio.run(run_tests())
