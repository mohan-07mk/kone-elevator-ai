# Elevator AI — Predictive Maintenance & Root Cause Intelligence Platform

[![Build Status](https://img.shields.io/badge/build-passing-brightgreen.svg)](https://github.com/mohan-07mk/kone-elevator-ai)
[![Frontend](https://img.shields.io/badge/frontend-React%2018%20%7C%20Vite-blue.svg)](https://eloquent-eclair-c69e60.netlify.app)
[![Backend](https://img.shields.io/badge/backend-FastAPI%20%7C%20Python%203.12-green.svg)](https://kone-elevator-ai-production.up.railway.app)
[![License](https://img.shields.io/badge/license-MIT-orange.svg)](LICENSE)

**Elevator AI** is a production-ready, real-time predictive maintenance and root cause intelligence platform designed for modern elevator fleets. The system combines high-frequency industrial sensor telemetry, machine learning anomaly detection, graph-based root cause analysis (RCA), remaining useful life (RUL) forecasting, and automated technician dispatch into an intuitive, KONE-inspired industrial dashboard.

---

## Live Deployments

- **Production Frontend (Netlify)**: [https://eloquent-eclair-c69e60.netlify.app](https://eloquent-eclair-c69e60.netlify.app)
- **Production Backend API (Railway)**: [https://kone-elevator-ai-production.up.railway.app](https://kone-elevator-ai-production.up.railway.app)
- **Interactive OpenAPI Docs**: [https://kone-elevator-ai-production.up.railway.app/docs](https://kone-elevator-ai-production.up.railway.app/docs)
- **Production WebSocket Stream**: `wss://kone-elevator-ai-production.up.railway.app/ws/fleet`

---

## Truthfulness & Transparency Statement

> [!IMPORTANT]
> - **Simulation Mode**: Telemetry streams are generated via a deterministic simulator powered by the **AI4I 2020 Predictive Maintenance Dataset** (UCI Machine Learning Repository). Live streams are clearly identified in the UI with a `SIMULATION & DATASET REPLAY ACTIVE` indicator.
> - **AI Runtime Reporting**: The system reports actual active hardware execution providers via `GET /api/ai/status`. When Snapdragon DirectML or QNN NPU hardware acceleration is absent, the backend truthfully reports `CPUExecutionProvider (Fallback)` mode.
> - **Data Source Integrity**: The backend FastAPI engine acts as the single source of truth for all telemetry, health calculations, and RCA graphs. No client-side `Math.random()` numbers are generated.

---

## Problem & Solution

### The Problem
Elevator failures in high-rise residential and commercial buildings lead to costly emergency downtime, tenant dissatisfaction, and safety risks. Traditional maintenance relies on calendar-based schedules or reactive repairs after component failure occurs.

### The Solution
Elevator AI continuously ingests multi-sensor telemetry (vibration, motor temperature, voltage, current, power, RPM, brake condition, load, humidity, door alignment) to detect anomalies *before* failure occurs. It pinpoints the exact physical component causing degradation, projects remaining operating hours, and dispatches specialized technicians automatically.

---

## System Architecture

```
[ STM32 Sensor Node / Microcontroller ] ──► [ Raspberry Pi Edge Gateway ]
                                                       │ (HTTP POST / API Ingest)
                                                       ▼
[ Deterministic Simulator / AI4I Dataset ] ──► [ FastAPI Cloud Backend ]
                                                       │
                     ┌─────────────────────────────────┼─────────────────────────────────┐
                     ▼                                 ▼                                 ▼
         [ PostgreSQL Database ]             [ AI / ML Pipeline ]             [ WebSocket Broadcast ]
         ORM Models & Migrations             Fault Detection & RCA             Real-Time Telemetry Push
                     │                                 │                                 │
                     └─────────────────────────────────┼─────────────────────────────────┘
                                                       ▼
                                         [ React Dashboard Frontend ]
                                         KONE Dark Industrial UI
```

---

## Key Features

- **Live Fleet Monitoring**: Real-time KPI counters, active simulator controls, elevator grid status cards, and live sensor sparklines.
- **AI Fault Detection**: Supervised Random Forest Classifier + Unsupervised Isolation Forest for multi-variable fault detection.
- **Root Cause Analysis (RCA)**: Diagnostic causal trees mapping raw sensor spikes to physical component failure modes.
- **Elevator Health Scoring**: Weighted multi-component health index ($0 - 100\%$) tracking motor, bearing, brake, door, drive, and electrical systems.
- **Predictive Maintenance & RUL**: Exponential degradation models estimating remaining operational hours and days.
- **Fault Timeline & Audit Logs**: Detailed chronologically sorted events and administrator action audit trails.
- **Technician & Task Management**: Automated technician recommendation engine matching specialization and availability to task priority.
- **AI Assistant**: Natural language query engine backed by real database state (e.g., *"Why did KONE-ELEV-001 become unhealthy?"*).
- **Reports & PDF Generator**: Exportable fault analysis and maintenance summary reports.
- **Role-Based Access Control (RBAC)**: Support for Admin, Maintenance Engineer, Manager, and Technician role permissions.

---

## Technology Stack

- **Frontend**: React 18, Vite, Recharts, Lucide React, CSS Grid/Flexbox
- **Backend**: FastAPI, Python 3.12, Uvicorn, AsyncIO, Pydantic v2
- **Database**: PostgreSQL (Production) / Async SQLite (Local Dev & Testing), SQLAlchemy 2.0 Async, Alembic
- **AI / ML**: Scikit-Learn, ONNX Runtime, NumPy, SciPy, Psutil
- **Real-Time Communications**: Native WebSockets (`/ws/elevators/{id}`, `/ws/fleet`)
- **Containerization & Hosting**: Docker, Docker Compose, Railway, Netlify

---

## Project Structure

```
KONE-Elevator-AI/
├── frontend/                  # React + Vite Dashboard Application
│   ├── src/
│   │   ├── api/               # Modular HTTP API client functions
│   │   ├── websocket/         # WebSocket client connection manager
│   │   └── main.jsx           # Entrypoint wrapper
│   ├── public/                # Static assets & _redirects SPA configuration
│   ├── ElevatorAI.jsx         # Approved Claude-designed React UI Component
│   ├── package.json
│   ├── vite.config.js
│   └── netlify.toml
│
├── backend/                   # FastAPI Cloud Service
│   ├── app/
│   │   ├── ai/                # Fault detector, RCA engine, runtime manager
│   │   ├── api/               # 20 REST API routers
│   │   ├── core/              # Config settings & security validators
│   │   ├── database/          # SQLAlchemy async session, models, seed logic
│   │   ├── devices/           # Edge gateway buffer management
│   │   ├── models/            # SQLAlchemy ORM model definitions
│   │   ├── schemas/           # Pydantic validation schemas
│   │   ├── simulator/         # Dataset loader & deterministic simulation engine
│   │   └── websockets/        # Async connection manager & telemetry broadcaster
│   ├── datasets/              # AI4I 2020 local dataset cache
│   ├── migrations/            # Alembic database migration scripts
│   ├── tests/                 # Pytest unit, auth, API, and e2e integration tests
│   ├── Dockerfile
│   └── requirements.txt
│
├── hardware/                  # Edge Hardware Architecture Modules
│   ├── stm32/                 # STM32 C sensor bridge & UART serializer
│   └── raspberry_pi/          # Raspberry Pi Python gateway client
│
├── docs/                      # Technical Documentation
│   ├── ARCHITECTURE.md        # System architecture specification
│   ├── AI.md                  # AI/ML methodology & runtime abstraction
│   ├── DATASET.md             # Dataset contract & simulation protocol
│   └── DEMO.md                # KONE-ELEV-001 Competition demonstration guide
│
├── README.md
├── docker-compose.yml
├── Dockerfile
├── .gitignore
└── LICENSE
```

---

## Local Development Setup

### Prerequisites
- Node.js 18+ & npm
- Python 3.10+
- Git

### 1. Backend Setup
```bash
# Navigate to backend directory
cd backend

# Install dependencies
pip install -r requirements.txt

# Run FastAPI development server
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```
Backend API will be available at `http://localhost:8000`. API Docs: `http://localhost:8000/docs`.

### 2. Frontend Setup
```bash
# Open a new terminal and navigate to frontend directory
cd frontend

# Install Node dependencies
npm install

# Start Vite development server
npm run dev
```
Frontend dashboard will be available at `http://localhost:3000`.

---

## Environment Variables

### Backend Configuration (`backend/.env`)
```ini
APP_NAME="Elevator AI"
APP_VERSION="0.1.0"
DEBUG=true

# Database (PostgreSQL or SQLite)
DATABASE_URL=sqlite+aiosqlite:///./elevator_ai.db
DATABASE_URL_SYNC=sqlite:///./elevator_ai.db

# JWT Security
JWT_SECRET_KEY=dev-secret-key-change-in-production-mode
JWT_ALGORITHM=HS256
JWT_ACCESS_TOKEN_EXPIRE_MINUTES=30

# CORS Allowed Origins
CORS_ORIGINS=http://localhost:3000,http://localhost:5173,https://eloquent-eclair-c69e60.netlify.app
```

### Frontend Configuration (`frontend/.env`)
```ini
VITE_API_URL=https://kone-elevator-ai-production.up.railway.app
VITE_WS_URL=wss://kone-elevator-ai-production.up.railway.app
```

---

## Competition Demonstration Guide (`KONE-ELEV-001`)

To demonstrate the platform's vertical slice capability:

1. Select **`KONE-ELEV-001`** in the topbar elevator dropdown.
2. In the **Simulator Controls** bar, select scenario **`BEARING_DEGRADATION`** and click **`Start`**.
3. Observe real-time sensor escalation in **Live Monitoring**:
   - Vibration spikes from $1.5\text{ mm/s}$ to $8.8+\text{ mm/s}$.
   - Motor temperature rises to $78^\circ\text{C}+$.
   - Current draw increases to $18.5\text{ A}+$.
4. Watch status transition to **`CRITICAL`** as the **AI Fault Detector** flags *Bearing Degradation* ($94.2\%$ confidence).
5. Open **Root Cause Analysis (RCA)** to inspect the causal chain: `Abnormal Vibration ──► Thermal Rise ──► Current Spike ──► Motor Bearing Wear`.
6. Inspect **Elevator Health** score dropping to $42\%$ and **RUL** dropping to 12 days.
7. Observe auto-generated **Alerts** and scheduled **Maintenance Task** assigned to senior vibration engineer *D. Suresh*.

*For full details, see [`docs/DEMO.md`](docs/DEMO.md).*

---

## Testing & Quality Verification

Run the comprehensive Pytest suite (35 unit, API, auth, database, and end-to-end integration tests):

```bash
cd backend
python -m pytest tests
```

To verify the frontend build:
```bash
cd frontend
npm run build
```

---

## License

This project is licensed under the [MIT License](LICENSE).
