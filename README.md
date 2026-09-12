# KONE ELEVATOR AI — PREDICTIVE FLEET INTELLIGENCE PLATFORM

[![FastAPI](https://img.shields.io/badge/FastAPI-0.110.0-009688?logo=fastapi)](https://fastapi.tiangolo.com)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-16--alpine-336791?logo=postgresql)](https://www.postgresql.org)
[![React](https://img.shields.io/badge/React-18.2.0-61DAFB?logo=react)](https://react.dev)
[![ONNX Runtime](https://img.shields.io/badge/ONNX_Runtime-Qualcomm_QNN_/_DirectML-blue)](https://onnxruntime.ai)

Enterprise Predictive Maintenance, AI Fault Classification, Root Cause Analysis (RCA), Remaining Useful Life (RUL) Estimation, and Edge Hardware Integration platform optimized for Snapdragon-powered PC hardware.

---

## 🚀 Quick Start

### Option 1: Docker Compose (Recommended)

To run the complete stack (`frontend`, `backend`, `postgresql`) with a single command:

```bash
docker-compose up --build
```

Access services:
* **Frontend Application**: [http://localhost:3000](http://localhost:3000)
* **FastAPI Backend OpenAPI Docs**: [http://localhost:8000/docs](http://localhost:8000/docs)
* **PostgreSQL Database**: `localhost:5432` (`user: elevator_user`, `pass: elevator_pass`, `db: elevator_ai`)

---

### Option 2: Local Development Setup

#### 1. Backend Setup

```bash
cd backend
python -m venv venv
# On Windows:
venv\Scripts\activate
# On Linux/macOS:
source venv/bin/activate

pip install -r requirements.txt
python -c "from app.ai.export_onnx import export_to_onnx; export_to_onnx()"
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

#### 2. Frontend Setup

```bash
# In project root:
npm install
npm run dev
```

---

## 🏢 Platform Architecture

```text
Edge Sensors (STM32 Node / Gateway)
            │
            ▼ (Raw ADC / Telemetry Ingest)
┌───────────────────────────────────────────────────────────┐
│                 FastAPI Async Engine                      │
│                                                           │
│  ├── /api/sensors/ingest   ──► Telemetry Pipeline        │
│  ├── /api/devices/*        ──► Hardware Edge Buffer       │
│  ├── /ws/elevators/{id}    ──► Real-Time Broadcast        │
│  └── /api/ai/*             ──► Local AI Runtime (ONNX)    │
└─────────────┬───────────────────────────────┬─────────────┘
              │                               │
              ▼                               ▼
    ┌──────────────────┐            ┌──────────────────┐
    │  PostgreSQL 16   │            │ Snapdragon Local │
    │  (Async ORM)     │            │ AI Acceleration  │
    └──────────────────┘            └──────────────────┘
```

---

## 🛠 Features & Capabilities

1. **Deterministic Sensor Replay & Simulation Engine**:
   * Industrial Machine Condition Dataset (C-MAPSS Turbofan + Bearing Vibration Benchmark) preprocessed and normalized for elevator telemetry.
   * Real-time fault injection (`BEARING_DEGRADATION`, `MOTOR_OVERHEATING`, `DOOR_ALIGNMENT_DRIFT`).
2. **Explainable AI Fault Engine**:
   * Random Forest + Isolation Forest anomaly detection.
   * Automated Root Cause Analysis (RCA) with component isolation.
   * Component-level health scoring & Remaining Useful Life (RUL) estimation in hours & days.
3. **Snapdragon Local AI & Hardware Abstraction**:
   * Supports Qualcomm Hexagon QNN (`QNNExecutionProvider`), DirectML (`DmlExecutionProvider`), and CPU fallback (`CPUExecutionProvider`).
   * Live hardware status and 100-pass micro-benchmark execution APIs.
4. **Resilient Hardware Ingestion Layer**:
   * Raw ADC signal conversion for STM32 microcontroller nodes (`raw_accel` -> `vibration mm/s`, `analog_temp` -> `°C`).
   * Edge FIFO buffering queue for offline network telemetry recovery.

---

## 🧪 Running Test Suites

```bash
cd backend
pytest -v
python test_phase8_e2e.py
```

---

## 📚 Documentation Index

* [Demo Scenario & Competition Guide](docs/demo-guide.md)
* [Frontend-to-Backend Route Mapping](docs/frontend-backend-map.md)
* [Backend System Architecture](docs/backend-architecture.md)
* [AI Methodology & Feature Engineering](docs/ai-methodology.md)
* [Snapdragon Local AI Benchmark](docs/benchmark.md)
* [Dataset Specification & Preprocessing](datasets/README.md)

---

## ⚖ License & Disclaimer

Built for KONE Elevator AI Competition. Sensor simulation mode and dataset replay are explicitly indicated within system UI badges. Hardware status reporting truthfully reflects local OS execution providers.
