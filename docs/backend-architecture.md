# Backend Architecture Plan — Elevator AI

> **Phase 1: Architecture design for Phase 2 implementation**

---

## 1. System Architecture Overview

```
┌─────────────────────────────────────────────────────────────────────────┐
│                        CURRENT STATE (Phase 1)                         │
│                                                                        │
│   React SPA (ElevatorAI.jsx)                                          │
│     └── All data is hardcoded constants + Math.random()               │
│     └── No backend, no database, no real AI                           │
│     └── 16 pages, 2147 lines, 126 KB single file                     │
└─────────────────────────────────────────────────────────────────────────┘

                              ↓ Phase 2 ↓

┌─────────────────────────────────────────────────────────────────────────┐
│                       TARGET ARCHITECTURE                              │
│                                                                        │
│  ┌──────────────┐    ┌──────────────┐    ┌───────────────────────┐    │
│  │  React SPA   │←──→│   FastAPI    │←──→│    PostgreSQL         │    │
│  │  (Frontend)  │    │  (Backend)   │    │    (Database)         │    │
│  │              │    │              │    │                       │    │
│  │ - Dashboard  │    │ - REST APIs  │    │ - elevators           │    │
│  │ - Monitoring │    │ - WebSocket  │    │ - sensor_telemetry    │    │
│  │ - AI Pages   │    │ - AI Engine  │    │ - fault_detections    │    │
│  │ - Admin      │    │ - Auth       │    │ - maintenance_tasks   │    │
│  │ - Settings   │    │ - Workers    │    │ - health_scores       │    │
│  └──────────────┘    └──────────────┘    └───────────────────────┘    │
│         ↑                   ↑                                         │
│    WebSocket            Simulator                                     │
│    (real-time)         / Dataset                                      │
└─────────────────────────────────────────────────────────────────────────┘
```

---

## 2. Detailed Data Flow

### Production Flow (Target)

```
STM32 Sensors (Future Hardware)
 ├── Motor Temperature Sensor
 ├── Vibration Sensor (accelerometer)
 ├── Current Sensor
 ├── RPM Encoder
 ├── Load Cell
 ├── Door Sensor
 ├── Humidity Sensor
 └── Voltage Sensor
     ↓
Raspberry Pi (Edge Gateway)
 ├── Data acquisition & local processing
 ├── Edge anomaly detection
 ├── Data buffering for intermittent connectivity
 └── MQTT/HTTP push to cloud
     ↓
FastAPI Backend
 ├── /api/telemetry/ingest     ← Sensor data ingestion
 ├── AI Processing Pipeline    ← Fault detection, RCA, health scoring
 ├── PostgreSQL writes         ← Persistent storage
 └── WebSocket broadcast       ← Real-time push to frontend
     ↓
React Dashboard
 └── Renders real-time data
```

### Simulation Flow (Phase 2 Development)

```
Dataset / Simulator
 ├── CSV dataset with realistic elevator telemetry
 ├── Scenario replay engine (bearing degradation timeline)
 └── Configurable noise & drift injection
     ↓
Telemetry Ingestion API
 ├── POST /api/telemetry/ingest
 └── Same API that hardware will use later
     ↓
AI Processing Pipeline
 ├── Fault Detection Model (sensor fusion)
 ├── Root Cause Analysis Engine
 ├── Predictive Maintenance / RUL Model
 ├── Health Score Calculator
 └── Alert Generator
     ↓
PostgreSQL Database
 ├── Time-series sensor data
 ├── Fault detection results
 ├── Health scores & RUL projections
 ├── Alerts & events
 └── Maintenance tasks & assignments
     ↓
WebSocket Server
 ├── Real-time sensor push
 ├── Alert push
 ├── Health score updates
 └── AI analysis progress
     ↓
React Dashboard (unchanged UI)
 └── Fetches from API + listens on WebSocket
```

---

## 3. Backend Service Architecture

```
backend/
├── main.py                    # FastAPI app initialization
├── config.py                  # Environment configuration
├── database.py                # PostgreSQL connection & session
│
├── api/                       # REST API routes
│   ├── elevators.py           # /api/elevators/*
│   ├── sensors.py             # /api/elevators/{id}/sensors/*
│   ├── telemetry.py           # /api/telemetry/ingest
│   ├── faults.py              # /api/ai/fault-detection/*
│   ├── rca.py                 # /api/ai/rca/*
│   ├── predictive.py          # /api/predictive/*
│   ├── health.py              # /api/elevators/{id}/health/*
│   ├── analytics.py           # /api/analytics/*
│   ├── maintenance.py         # /api/maintenance/*
│   ├── technicians.py         # /api/technicians/*
│   ├── alerts.py              # /api/alerts/*
│   ├── reports.py             # /api/reports/*
│   ├── buildings.py           # /api/buildings/*
│   ├── assistant.py           # /api/ai/assistant/*
│   ├── admin.py               # /api/admin/*
│   └── settings.py            # /api/settings/*
│
├── models/                    # SQLAlchemy ORM models
│   ├── building.py
│   ├── elevator.py
│   ├── sensor_telemetry.py
│   ├── sensor_config.py
│   ├── fault_detection.py
│   ├── rca_analysis.py
│   ├── component_health.py
│   ├── health_score.py
│   ├── alert.py
│   ├── maintenance_task.py
│   ├── technician.py
│   ├── report.py
│   ├── user.py
│   ├── audit_log.py
│   └── user_preference.py
│
├── ai/                        # AI/ML processing
│   ├── fault_detector.py      # Sensor fusion fault classification
│   ├── rca_engine.py          # Root cause analysis
│   ├── rul_predictor.py       # Remaining useful life prediction
│   ├── health_scorer.py       # Component & overall health scoring
│   ├── alert_generator.py     # Threshold-based + AI alert generation
│   ├── tech_recommender.py    # Technician recommendation
│   └── assistant.py           # AI assistant (LLM or rule-based)
│
├── simulator/                 # Data simulation for development
│   ├── scenario_engine.py     # Bearing degradation scenario replay
│   ├── telemetry_simulator.py # Realistic sensor data generation
│   └── dataset_loader.py     # Load from CSV datasets
│
├── websocket/                 # WebSocket management
│   ├── manager.py             # Connection management
│   └── handlers.py            # Message routing
│
└── workers/                   # Background tasks
    ├── telemetry_processor.py # Process incoming sensor data
    ├── health_updater.py      # Periodic health score recalculation
    └── alert_processor.py     # Alert deduplication & batching
```

---

## 4. Database Schema (PostgreSQL)

### Core Entities

```sql
-- Buildings
CREATE TABLE buildings (
    id VARCHAR(10) PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    location VARCHAR(200),
    created_at TIMESTAMP DEFAULT NOW()
);

-- Elevators
CREATE TABLE elevators (
    id VARCHAR(20) PRIMARY KEY,
    building_id VARCHAR(10) REFERENCES buildings(id),
    current_floor INTEGER DEFAULT 1,
    direction VARCHAR(10) DEFAULT 'idle',
    status VARCHAR(20) DEFAULT 'healthy',
    health_score FLOAT DEFAULT 100.0,
    active_fault TEXT,
    risk_level VARCHAR(10) DEFAULT 'Low',
    speed FLOAT DEFAULT 0.0,
    load_percentage FLOAT DEFAULT 0.0,
    door_status VARCHAR(10) DEFAULT 'closed',
    connection_status VARCHAR(10) DEFAULT 'offline',
    last_telemetry_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Sensor Configurations
CREATE TABLE sensor_configs (
    id SERIAL PRIMARY KEY,
    sensor_key VARCHAR(30) NOT NULL,
    label VARCHAR(50),
    unit VARCHAR(10),
    normal_min FLOAT,
    normal_max FLOAT,
    warning_threshold FLOAT,
    critical_threshold FLOAT,
    UNIQUE(sensor_key)
);

-- Sensor Telemetry (Time-series)
CREATE TABLE sensor_telemetry (
    id BIGSERIAL PRIMARY KEY,
    elevator_id VARCHAR(20) REFERENCES elevators(id),
    sensor_key VARCHAR(30),
    value FLOAT NOT NULL,
    is_anomaly BOOLEAN DEFAULT FALSE,
    recorded_at TIMESTAMP DEFAULT NOW(),
    INDEX idx_telemetry_elevator_sensor_time (elevator_id, sensor_key, recorded_at DESC)
);

-- Fault Detections
CREATE TABLE fault_detections (
    id SERIAL PRIMARY KEY,
    elevator_id VARCHAR(20) REFERENCES elevators(id),
    fault_type VARCHAR(50),
    confidence FLOAT,
    severity VARCHAR(20),
    affected_component VARCHAR(50),
    model_version VARCHAR(20),
    detected_at TIMESTAMP DEFAULT NOW()
);

-- Fault Category Probabilities
CREATE TABLE fault_probabilities (
    id SERIAL PRIMARY KEY,
    detection_id INTEGER REFERENCES fault_detections(id),
    category_name VARCHAR(50),
    probability FLOAT
);

-- RCA Analyses
CREATE TABLE rca_analyses (
    id SERIAL PRIMARY KEY,
    elevator_id VARCHAR(20) REFERENCES elevators(id),
    detection_id INTEGER REFERENCES fault_detections(id),
    root_cause VARCHAR(100),
    confidence FLOAT,
    severity VARCHAR(20),
    recommended_action TEXT,
    analyzed_at TIMESTAMP DEFAULT NOW()
);

-- RCA Chain Steps
CREATE TABLE rca_chain_steps (
    id SERIAL PRIMARY KEY,
    analysis_id INTEGER REFERENCES rca_analyses(id),
    step_order INTEGER,
    label VARCHAR(100),
    detail TEXT,
    sensor_source VARCHAR(50)
);

-- Contributing Factors
CREATE TABLE contributing_factors (
    id SERIAL PRIMARY KEY,
    analysis_id INTEGER REFERENCES rca_analyses(id),
    label VARCHAR(200),
    actual_value VARCHAR(100),
    baseline_value VARCHAR(100)
);

-- Component Health
CREATE TABLE component_health (
    id SERIAL PRIMARY KEY,
    elevator_id VARCHAR(20) REFERENCES elevators(id),
    component_name VARCHAR(50),
    health_score FLOAT,
    risk_level VARCHAR(10),
    rul_days INTEGER,
    recommended_action TEXT,
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Health Scores (Historical)
CREATE TABLE health_scores (
    id SERIAL PRIMARY KEY,
    elevator_id VARCHAR(20) REFERENCES elevators(id),
    overall FLOAT,
    motor FLOAT,
    bearing FLOAT,
    brake FLOAT,
    door FLOAT,
    electrical FLOAT,
    sensor FLOAT,
    drive FLOAT,
    summary_text TEXT,
    recorded_at TIMESTAMP DEFAULT NOW()
);

-- Alerts
CREATE TABLE alerts (
    id VARCHAR(10) PRIMARY KEY,
    level VARCHAR(20) NOT NULL,
    text TEXT NOT NULL,
    elevator_id VARCHAR(20),
    is_read BOOLEAN DEFAULT FALSE,
    is_acknowledged BOOLEAN DEFAULT FALSE,
    resolved_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Maintenance Tasks
CREATE TABLE maintenance_tasks (
    id VARCHAR(10) PRIMARY KEY,
    elevator_id VARCHAR(20) REFERENCES elevators(id),
    building_name VARCHAR(100),
    fault_description TEXT,
    priority VARCHAR(20),
    technician_id INTEGER REFERENCES technicians(id),
    scheduled_date DATE,
    status VARCHAR(20) DEFAULT 'Scheduled',
    completed_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Technicians
CREATE TABLE technicians (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100),
    role VARCHAR(50),
    availability VARCHAR(20) DEFAULT 'Available',
    current_task_count INTEGER DEFAULT 0,
    completed_task_count INTEGER DEFAULT 0,
    specialization VARCHAR(100),
    created_at TIMESTAMP DEFAULT NOW()
);

-- Reports
CREATE TABLE reports (
    id VARCHAR(10) PRIMARY KEY,
    report_type VARCHAR(50),
    elevator_id VARCHAR(20),
    content_json JSONB,
    status VARCHAR(20) DEFAULT 'Generating',
    generated_at TIMESTAMP DEFAULT NOW()
);

-- Users
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100),
    email VARCHAR(150) UNIQUE,
    role VARCHAR(30),
    password_hash VARCHAR(255),
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT NOW()
);

-- User Preferences
CREATE TABLE user_preferences (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id) UNIQUE,
    dark_mode BOOLEAN DEFAULT TRUE,
    language VARCHAR(20) DEFAULT 'English',
    notify_critical BOOLEAN DEFAULT TRUE,
    notify_warning BOOLEAN DEFAULT TRUE,
    notify_info BOOLEAN DEFAULT FALSE,
    notify_email BOOLEAN DEFAULT TRUE
);

-- Alert Thresholds
CREATE TABLE alert_thresholds (
    id SERIAL PRIMARY KEY,
    sensor_key VARCHAR(30),
    threshold_value FLOAT,
    updated_by INTEGER REFERENCES users(id),
    updated_at TIMESTAMP DEFAULT NOW(),
    UNIQUE(sensor_key)
);

-- Audit Log
CREATE TABLE audit_log (
    id SERIAL PRIMARY KEY,
    timestamp TIMESTAMP DEFAULT NOW(),
    user_name VARCHAR(100),
    action VARCHAR(100),
    elevator_id VARCHAR(20),
    status VARCHAR(20),
    details JSONB
);

-- Fault Timeline Events
CREATE TABLE fault_timeline_events (
    id SERIAL PRIMARY KEY,
    elevator_id VARCHAR(20) REFERENCES elevators(id),
    fault_id INTEGER REFERENCES fault_detections(id),
    event_time TIME,
    event_type VARCHAR(20),
    title VARCHAR(100),
    severity VARCHAR(20),
    sensor VARCHAR(50),
    description TEXT,
    sequence_order INTEGER
);

-- Chat History
CREATE TABLE chat_history (
    id SERIAL PRIMARY KEY,
    session_id UUID,
    user_id INTEGER REFERENCES users(id),
    role VARCHAR(10),
    message TEXT,
    response_json JSONB,
    created_at TIMESTAMP DEFAULT NOW()
);
```

### Entity Count: **21 tables**

---

## 5. WebSocket Architecture

```
WebSocket Connections:
├── /ws/fleet-status          → Fleet-wide status updates (every 3 sec)
├── /ws/alerts                → Real-time alert push
├── /ws/elevator/{id}/sensors → Per-elevator sensor telemetry stream
├── /ws/elevator/{id}/status  → Per-elevator state changes
├── /ws/elevator/{id}/health  → Per-elevator health score updates
├── /ws/predictive/updates    → RUL/health prediction changes
├── /ws/maintenance/updates   → Task status changes
├── /ws/technicians/status    → Technician availability changes
├── /ws/buildings/status      → Building-level health updates
├── /ws/ai/analysis-progress  → AI analysis progress during runs
└── /ws/ai/assistant          → Streaming AI assistant responses
```

**11 WebSocket channels** — can be consolidated into fewer channels with topic-based routing.

---

## 6. AI/ML Components

### 6.1 Fault Detection Model
- **Input:** Multi-sensor time-series (vibration, temperature, current, RPM)
- **Output:** Fault type + confidence score + affected component
- **Approach:** Sensor fusion classification (Random Forest / LSTM / XGBoost)
- **Training Data:** Elevator maintenance datasets (e.g., CWRU bearing dataset adapted)

### 6.2 Root Cause Analysis Engine
- **Input:** Detected fault + historical sensor data + event logs
- **Output:** Ordered causal chain + contributing factors + recommended action
- **Approach:** Rule-based causal graph + pattern matching (Phase 2); ML-based (Phase 3)

### 6.3 RUL Prediction Model
- **Input:** Component sensor signatures over time
- **Output:** Days until predicted failure + confidence interval
- **Approach:** Survival analysis or LSTM regression on degradation curves

### 6.4 Health Score Calculator
- **Input:** All sensor values + fault detections + maintenance history
- **Output:** Per-component health (0–100) + overall weighted composite
- **Approach:** Weighted scoring formula (configurable weights per component)

### 6.5 Alert Generator
- **Input:** Real-time sensor values + thresholds + AI detections
- **Output:** Alert objects (level, text, elevator, timestamp)
- **Approach:** Threshold breach detection + AI-driven anomaly alerts + deduplication

### 6.6 Technician Recommender
- **Input:** Task requirements + technician skills/availability/workload
- **Output:** Ranked technician recommendation
- **Approach:** Scoring model (skill match × availability × workload balance)

### 6.7 AI Assistant
- **Input:** Natural language query + system context
- **Output:** Structured response (summary, root cause, data, action, priority)
- **Approach Phase 2:** Enhanced rule-based NLU with real data grounding
- **Approach Phase 3:** LLM integration (OpenAI/local model) with RAG over system data

---

## 7. Dataset Requirements

### For Development & Training
1. **Elevator Sensor Telemetry Dataset**
   - Vibration, temperature, current, RPM time-series
   - Normal + degradation patterns
   - Source: Adapt from CWRU Bearing Dataset or generate synthetic

2. **Bearing Degradation Dataset**
   - Progressive wear pattern data
   - Run-to-failure measurements
   - For RUL model training

3. **Fault Event History**
   - Historical fault records with timestamps
   - Fault type classification labels
   - For fault detection model training

### For Simulation
4. **KONE-ELEV-001 Scenario Dataset**
   - Reproduce the existing demo scenario:
     - 09:00 — Normal operation baseline
     - 10:15 — Vibration increase (2.1 → 4.9 mm/s)
     - 11:30 — Temperature warning (> 70°C)
     - 12:10 — Current increase (+12%)
     - 12:45 — Bearing degradation detected (94%)
     - 13:00 — Critical alert generated
   - Time-series CSV for all 10 sensors during this progression

---

## 8. Technology Stack

| Layer | Technology | Justification |
|---|---|---|
| Frontend | React (existing) | Already built, 16 pages, do not replace |
| Backend | FastAPI (Python) | Async, fast, auto-docs, ML ecosystem |
| Database | PostgreSQL | Relational + JSONB + time-series capable |
| ORM | SQLAlchemy 2.0 | Async support, mature ecosystem |
| Migrations | Alembic | Standard for SQLAlchemy |
| WebSocket | FastAPI WebSocket | Built-in support |
| AI/ML | scikit-learn, XGBoost | Phase 2: classical ML models |
| Deep Learning | PyTorch / TensorFlow | Phase 3: LSTM for RUL |
| Background Jobs | Celery / APScheduler | Periodic health recalculation |
| Caching | Redis (optional) | Session management, pub/sub for WebSocket |
| Containerization | Docker + docker-compose | Development environment |
| API Documentation | Swagger (auto from FastAPI) | Built-in |

---

## 9. Future Hardware Integration Path

```
Phase 2 (Software Only):
  Simulator → FastAPI → PostgreSQL → React

Phase 3 (Hardware Prototype):
  STM32 + Sensors
       ↓
  Raspberry Pi (Edge)
   ├── Local data buffering
   ├── Edge inference
   └── MQTT / HTTP push
       ↓
  FastAPI Backend (Cloud/Server)
       ↓
  PostgreSQL + AI Pipeline
       ↓
  React Dashboard (same frontend)
```

### Hardware Protocol Support (Future)
- **MQTT** — Lightweight sensor data transport from Raspberry Pi
- **HTTP POST** — Batch telemetry upload
- **gRPC** — High-throughput sensor streaming (optional)

---

## 10. Recommended Implementation Order

### Phase 2A: Foundation (Week 1–2)
1. FastAPI project scaffolding
2. PostgreSQL schema + migrations
3. Basic CRUD APIs (buildings, elevators, technicians, users)
4. Seed data matching current frontend mock data
5. Connect React to backend APIs for static data

### Phase 2B: Telemetry (Week 3–4)
6. Sensor telemetry ingestion API
7. Telemetry simulator (replay KONE-ELEV-001 scenario)
8. WebSocket for real-time sensor push
9. Replace `Math.random()` in frontend with WebSocket data

### Phase 2C: AI Pipeline (Week 5–7)
10. Fault detection model (sensor fusion classifier)
11. Root cause analysis engine
12. Health scoring calculator
13. RUL prediction model
14. Alert generation from AI + thresholds

### Phase 2D: Full Integration (Week 8–9)
15. Maintenance task CRUD with AI-generated tasks
16. Technician recommendation engine
17. AI Assistant with real data access
18. Report generation
19. Admin panel with real CRUD
20. Settings persistence

### Phase 2E: Polish (Week 10)
21. Authentication & RBAC
22. Audit logging middleware
23. WebSocket stability & reconnection
24. Error handling & loading states in frontend
25. Testing & documentation
