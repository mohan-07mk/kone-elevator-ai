# Elevator AI — System Architecture & Platform Design

## Executive Overview
**Elevator AI** is a real-time predictive maintenance and root cause intelligence platform designed for modern vertical transportation systems. The platform ingests multi-sensor industrial telemetry (vibration, motor temperature, voltage, current, power, RPM, brake condition, load, humidity, door alignment), processes it through a hybrid machine learning pipeline (Random Forest Classifier + Isolation Forest + Deterministic Fallbacks), and delivers real-time health scoring, remaining useful life (RUL) projections, and automated technician dispatch via a high-performance React dashboard.

---

## 1. High-Level Data Flow

```
[ Industrial Sensors ]
          │ (Vibration, Temp, Current, RPM, Load, Door)
          ▼
[ STM32 Sensor Node / Microcontroller ] (ADC / I2C / UART Serializer)
          │
          ▼
[ Raspberry Pi Edge Gateway ] (Edge Buffer, Offline Queue, HTTP/JSON Ingestion)
          │
          ▼
[ FastAPI Backend Engine ] ◄── (Deterministic Simulator / AI4I Dataset Replay)
     │         │
     │         ├─► [ PostgreSQL Database ] (Persistence: SensorReadings, Alerts, Health, RCA, Tasks)
     │         │
     │         ├─► [ AI / ML Inference Pipeline ] (Fault Detection, RCA Engine, Health Scoring, RUL)
     │         │
     ▼         ▼
[ WebSocket Broadcast Server ] (`/ws/elevators/{id}`, `/ws/fleet`)
          │
          ▼
[ React Frontend Dashboard ] (KONE Industrial Dark Theme, Live Monitoring, RCA Graph, AI Assistant)
```

---

## 2. Component Specifications

### 2.1 React Frontend
- **Framework**: React 18 + Vite SPA architecture
- **Design System**: KONE Industrial Dark UI with high-contrast tokens, CSS Grid/Flexbox, Chakra Petch typography
- **State & Data Handling**: Real-time WebSocket connection hooks with automatic fallback HTTP polling
- **Visualization**: Recharts (`AreaChart`, `LineChart`, `BarChart`, `RadialBarChart`, `PieChart`)
- **Deployment**: Netlify SPA (`publish = "dist"`, `public/_redirects`)

### 2.2 FastAPI Backend
- **Framework**: FastAPI (Python 3.12, AsyncIO)
- **Database Access**: SQLAlchemy 2.0 Async Session + AsyncPG driver (PostgreSQL) / SQLite (`aiosqlite`) fallback
- **Authentication**: JWT Access Tokens (HS256) + Role-Based Access Control (RBAC: Admin, Maintenance Engineer, Manager, Technician)
- **Deployment**: Railway / Docker containerized service

### 2.3 Simulator & Dataset Replay Engine
- **Source Data**: AI4I 2020 Predictive Maintenance Dataset (UCI Machine Learning Repository)
- **Scenarios**:
  - `NORMAL`: Baseline operational telemetry
  - `BEARING_DEGRADATION`: Gradual vibration & temperature escalation (Primary Competition Demo)
  - `MOTOR_OVERHEATING`: Thermal overload trajectory
  - `DOOR_ALIGNMENT`: Door alignment drift & cycle friction
  - `WARNING`: Unsupervised tool wear warning
- **Modes**: Support for Start, Pause, Resume, Reset, Scenario Selection, and Replay Speed scaling (0.5x to 10x)

### 2.4 AI & Predictive Intelligence Engine
- **Supervised Classifier**: Random Forest Classifier (50 estimators) for multi-fault categorization
- **Unsupervised Anomaly Detector**: Isolation Forest (5% contamination) for unexpected drift
- **ONNX Runtime Abstraction**: Hardware acceleration abstraction layer supporting DirectML / Qualcomm QNN NPU with CPU fallback
- **RCA Engine**: Step-by-step diagnostic graph linking sensor spikes to physical component root cause
- **Health Scoring**: Multi-component weighted scoring (Motor 25%, Bearing 25%, Brake 15%, Door 15%, Drive 10%, Sensor/Electrical 10%)
- **RUL Estimator**: Exponential degradation curve calculating remaining operating hours before failure threshold

---

## 3. WebSocket Real-Time Architecture

- **Endpoints**:
  - `/ws/elevators/{elevator_id}`: Stream telemetry, alerts, and state changes for a specific elevator
  - `/ws/fleet`: Stream fleet-wide updates for all monitored assets
- **Heartbeat & Reconnection**: Client-side auto-reconnection loop (2-second interval) with state synchronization
- **Broadcasting Engine**: Asynchronous singleton `ConnectionManager` broadcasting telemetry frames instantly on ingest

---

## 4. Hardware Edge Architecture (Production-Ready)

```
                       ┌────────────────────────────┐
                       │  Physical Elevator Cabin   │
                       └──────────────┬─────────────┘
                                      │
          ┌───────────────────────────┼───────────────────────────┐
          ▼                           ▼                           ▼
[ Vibration Sensor ]       [ Temp / Thermal Sensor ]     [ Current / RPM Sensor ]
(STMicroelectronics LIS3DH)      (MAX31855 Thermocouple)        (ACS712 Current / Encoder)
          │                           │                           │
          └───────────────────────────┼───────────────────────────┘
                                      ▼
                      ┌──────────────────────────────┐
                      │  STM32F4 Microcontroller     │
                      │  - 1 kHz Sensor Sampling     │
                      │  - Normalization & Framing   │
                      └──────────────┬───────────────┘
                                     │ UART (115200 baud)
                                     ▼
                      ┌──────────────────────────────┐
                      │  Raspberry Pi 4 Edge Gateway │
                      │  - Serial Frame Ingestion    │
                      │  - SQLite Edge Buffer        │
                      │  - HTTP POST /api/sensors/ingest
                      └──────────────┬───────────────┘
                                     │ HTTPS / WSS
                                     ▼
                      ┌──────────────────────────────┐
                      │    FastAPI Cloud Backend     │
                      └──────────────────────────────┘
```

---

## 5. Security & Truthfulness Protocol

1. **No Committed Credentials**: All secrets (JWT keys, DB passwords) are loaded strictly via environment variables. `.env.example` provides safe templates.
2. **Explicit CORS**: Allowed origins are limited to production Netlify domains (`https://eloquent-eclair-c69e60.netlify.app`, `https://elevator-ai.netlify.app`) and development localhost ports (`3000`, `5173`, `8000`). Wildcard `*` is disabled when credentials are required.
3. **Simulation Truthfulness**: All simulated data feeds are explicitly labeled with `SIMULATION & DATASET REPLAY ACTIVE` badges in the dashboard UI.
4. **AI Runtime Truthfulness**: The `/api/ai/status` endpoint reports the actual active hardware provider, ONNX version, and fallback state. No fake NPU or benchmark numbers are fabricated.
