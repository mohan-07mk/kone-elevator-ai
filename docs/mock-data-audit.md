# Mock Data Audit — Elevator AI Frontend

> **Phase 1: Complete inventory of all mock/static dependencies**
> Source: `ElevatorAI.jsx` (Lines 1–2147)

---

## 1. Static Data Constants

### `BUILDINGS` (Line 76–80)
| Field | Mock Value | Backend Replacement |
|---|---|---|
| id | "BLD-A", "BLD-B", "BLD-C" | `buildings` table |
| name | Skyline Tower A, Horizon Business Park, Marina Corporate Centre | `buildings.name` |
| location | Nungambakkam Chennai, Whitefield Bengaluru, OMR Chennai | `buildings.location` |
| elevators | 4, 3, 3 | `COUNT(elevators WHERE building_id = ?)` |

**3 hardcoded buildings** — must be replaced with DB-driven building management.

---

### `ELEVATORS` (Line 82–93)
| Field | Mock Value | Backend Replacement |
|---|---|---|
| id | "KONE-ELEV-001" through "KONE-ELEV-010" | `elevators` table |
| buildingId | "BLD-A", "BLD-B", "BLD-C" | `elevators.building_id` FK |
| building | Building name string | JOIN on buildings table |
| floor | Static number (1–15) | Real-time from PLC/sensor |
| dir | "up"/"down"/"idle" | Real-time from PLC/encoder |
| status | "critical"/"warning"/"healthy" | Computed from AI engine |
| health | Static number (38–95) | Computed from health scoring model |
| fault | Hardcoded string or null | From fault detection engine |
| risk | "High"/"Medium"/"Low" | Computed from predictive model |
| speed | Static float (0–1.6) | Real-time from PLC/encoder |
| load | Static percent (5–84) | Real-time from load cell |
| door | "open"/"closed" | Real-time from door sensor |
| conn | Always "online" | Real-time from edge gateway heartbeat |
| updated | "2 sec ago" etc. | Computed from last_telemetry_at |

**10 hardcoded elevators** — every field must be backed by real telemetry or computed state.

---

### `SENSOR_DEFS` (Line 95–106)
| Sensor | Key | Unit | Normal Range | Base (Faulty) |
|---|---|---|---|---|
| Motor Temperature | motorTemp | °C | 40–65 | 78 |
| Voltage | voltage | V | 380–420 | 402 |
| Current | current | A | 10–18 | 19.4 |
| Power Consumption | power | kW | 4–8 | 7.6 |
| Motor RPM | rpm | rpm | 900–1500 | 1340 |
| Vibration | vibration | mm/s | 0–4.5 | 6.8 |
| Brake Condition | brake | % | 80–100 | 88 |
| Load Percentage | load | % | 0–90 | 62 |
| Humidity | humidity | % | 30–60 | 47 |
| Door Sensor | door | — | 0–0 | 0 |

**10 sensor definitions** — normal ranges and base values are reference configurations.
- `normal` ranges should move to `sensor_configurations` table
- `base` values are used for faulty elevator simulation — must be replaced by real telemetry

---

### `FAULT_PROBS` (Line 118–129)
**10 hardcoded fault category probabilities.** These are the output of an AI classification model.

| Fault Category | Probability |
|---|---|
| Bearing Failure | 94% |
| Motor Failure | 48% |
| Over Current | 22% |
| Brake Failure | 12% |
| Door Failure | 8% |
| Power Failure | 5% |
| Sensor Failure | 4% |
| Over Voltage | 3% |
| Under Voltage | 2% |
| Communication Failure | 1% |

**Must be replaced by:** Real-time AI fault classification model output per elevator per analysis run.

---

### `ROOT_CAUSE_CHAIN` (Line 131–137)
**5 hardcoded RCA steps** for the KONE-ELEV-001 bearing fault scenario:
1. Abnormal Vibration → Vibration exceeded 4.5 mm/s threshold
2. Motor Temperature Increased → Temperature rose 18% above baseline
3. Current Consumption Increased → Current draw up 12% under equal load
4. Bearing Wear Detected → Vibration + thermal + current signature match
5. Root Cause Identified → Motor Bearing Wear at 92% confidence

**Must be replaced by:** AI RCA engine generating dynamic causal chains per fault.

---

### `CONTRIBUTING_FACTORS` (Line 139–144)
**4 hardcoded contributing factors:**
1. Vibration: 6.8 mm/s vs 4.5 mm/s limit
2. Motor temperature: 78°C vs 66°C baseline
3. Current consumption: 19.4 A vs 17.3 A baseline
4. RPM stability: ±6.2% variance vs ±1.5% baseline

**Must be replaced by:** Actual sensor readings vs calibrated baselines from DB.

---

### `PM_COMPONENTS` (Line 146–153)
**6 hardcoded predictive maintenance components:**

| Component | Health | Risk | RUL | Action |
|---|---|---|---|---|
| Motor | 78% | Low | 180 Days | Monitor |
| Bearing | 42% | High | 12 Days | Replace |
| Brake | 88% | Low | 220 Days | Monitor |
| Door System | 65% | Medium | 45 Days | Inspect |
| Controller | 91% | Low | 300 Days | Monitor |
| Drive System | 74% | Medium | 60 Days | Inspect |

**Must be replaced by:** RUL prediction model output per component per elevator.

---

### `HEALTH_BREAKDOWN` (Line 155–159)
**3 hardcoded health breakdowns** for specific elevators only (KONE-ELEV-001, 003, 007):

| Elevator | Overall | Motor | Bearing | Brake | Door | Electrical | Sensor | Drive |
|---|---|---|---|---|---|---|---|---|
| KONE-ELEV-001 | 71 | 78 | 42 | 88 | 76 | 85 | 93 | 79 |
| KONE-ELEV-003 | 89 | 92 | 88 | 94 | 90 | 91 | 96 | 88 |
| KONE-ELEV-007 | 65 | 51 | 80 | 82 | 85 | 68 | 90 | 77 |

**Only 3 of 10 elevators have breakdown data.** Others fall back to KONE-ELEV-003.
**Must be replaced by:** Health scoring model output for all elevators.

---

### `ALERTS` (Line 161–170)
**8 hardcoded alerts:**

| ID | Level | Text | Elevator | Time |
|---|---|---|---|---|
| AL-901 | critical | Bearing failure risk 94% | KONE-ELEV-001 | 2 min ago |
| AL-900 | critical | Motor overheating detected | KONE-ELEV-007 | 6 min ago |
| AL-898 | warning | Motor temp above range | KONE-ELEV-005 | 18 min ago |
| AL-895 | warning | Door alignment drift | KONE-ELEV-002 | 34 min ago |
| AL-891 | warning | Vibration trending up | KONE-ELEV-010 | 51 min ago |
| AL-888 | info | Maintenance due tomorrow | KONE-ELEV-004 | 1 hr ago |
| AL-884 | info | Firmware update available | System | 2 hr ago |
| AL-870 | resolved | Brake pad wear resolved | KONE-ELEV-006 | Yesterday |

**Must be replaced by:** Real-time alerts generated from threshold breaches and AI detections.

---

### `MAINT_TASKS` (Line 172–180)
**7 hardcoded maintenance tasks** with static assignments and dates.
**Must be replaced by:** Database-driven task management with CRUD operations.

---

### `TECHNICIANS` (Line 182–188)
**5 hardcoded technicians** with static availability and completion counts.
**Must be replaced by:** User management system with real-time status tracking.

---

### `TIMELINE_EVENTS` (Line 190–197)
**6 hardcoded timeline events** for the KONE-ELEV-001 bearing fault scenario.
**Must be replaced by:** Dynamically generated event sequences from fault detection pipeline.

---

### `REPORTS` (Line 199–205)
**5 hardcoded report entries.** No actual report content exists.
**Must be replaced by:** Report generation engine with persistent storage.

---

### `AUDIT_LOG` (Line 207–215)
**7 hardcoded audit log entries.**
**Must be replaced by:** System-wide audit logging middleware.

---

### `FAULT_TREND` (Line 217–220)
**7 hardcoded daily fault counts** (Mon–Sun).
**Must be replaced by:** Aggregated fault counts from fault_events table.

---

### `FAULT_MIX` (Line 222–225)
**5 hardcoded fault category percentages.**
**Must be replaced by:** Aggregated fault distribution from historical fault data.

---

### `SUGGESTIONS` (Line 1592–1599)
**6 hardcoded AI assistant suggestion prompts.** Can remain as UI suggestions but response logic needs backend.

---

### `assistantAnswer()` (Line 1601–1622)
**7 hardcoded keyword-matched responses** for the AI assistant:

| Keyword Match | Static Response Focus |
|---|---|
| "stop" or "001" | KONE-ELEV-001 bearing fault |
| "vibration" | High vibration explanation |
| "critical" | Critical elevator list |
| "maintenance"/"due"/"week" | Maintenance schedule |
| "bearing" | Bearing fault explanation |
| "technician"/"check" | Technician checklist |
| Default (no match) | Generic fleet overview |

**Must be replaced by:** LLM-powered or RAG-based assistant with real data access.

---

### Admin Panel Mock Data (Line 1884)
**4 hardcoded user accounts:**
- Mohan K. (Admin)
- R. Karthik (Maintenance Engineer)
- S. Priya (Maintenance Engineer)
- Manager Desk (Manager)

**Must be replaced by:** User management with authentication.

---

### Settings Mock Data (Line 1946–1947)
**Hardcoded settings values:**
- Language: "English" (state only, no translations)
- Notification prefs: `{ critical: true, warning: true, info: false, email: true }`

**Must be replaced by:** User preferences stored in DB.

---

## 2. Math.random() Locations

| Line(s) | Function | Purpose | Backend Replacement |
|---|---|---|---|
| **112–113** | `genSeries()` | Generates random time-series data points with drift | Real sensor telemetry from DB |
| **768–770** | `SensorMiniCard` | Generates live sensor value: `base + (Math.random() - 0.5) * 0.6` for faulty sensors, random within normal range for healthy | Real-time sensor reading from WebSocket |
| **770** | `SensorMiniCard` | Normal sensor value: `normal[0] + range * (0.4 + Math.random() * 0.2)` | Real-time sensor reading |
| **774** | `SensorMiniCard` | Generates sparkline data per sensor per tick via `genSeries()` | Historical sensor series from DB |
| **775** | `SensorMiniCard` | Generates random percentage change: `(Math.random() * 6 - 3).toFixed(1)` | Computed from actual last 2 readings |
| **900** | `DetectionPage` | Confidence score: `90 + Math.floor(Math.random() * 8)` | AI model actual confidence output |

**Total: 6 locations** where `Math.random()` drives data (2 of which are called repeatedly via `genSeries()`).

---

## 3. Static AI Responses

| Location | Type | Description |
|---|---|---|
| `FAULT_PROBS` (L118) | Fault probabilities | 10 static probability values |
| `ROOT_CAUSE_CHAIN` (L131) | RCA chain | 5 static causal steps |
| `CONTRIBUTING_FACTORS` (L139) | RCA factors | 4 static contributing factors |
| `PM_COMPONENTS` (L146) | Predictive maintenance | 6 static component health/RUL values |
| `HEALTH_BREAKDOWN` (L155) | Health scores | 3 static elevator breakdowns |
| `assistantAnswer()` (L1601) | AI assistant | 7 keyword-matched static responses |
| Detection result (L934) | Fault detection | Always shows "BEARING DEGRADATION DETECTED" |
| RCA result (L1013) | Root cause | Always shows "Motor Bearing Wear — 92%" |
| Detection confidence (L900) | Confidence | Random 90–97% |
| Predicted failures (L594) | Dashboard KPI | Hardcoded "3" |
| Maintenance due (L595) | Dashboard KPI | Hardcoded "6" |
| AI tech recommendation (L1465) | Technician page | Always recommends "R. Karthik" |
| Report preview content (L1547) | Reports | Always shows bearing fault summary |

**13 total static AI responses** that must be replaced with real model outputs.

---

## 4. Frontend Calculations

| Location | Calculation | Backend Candidate |
|---|---|---|
| L558–563 | Count healthy/warning/critical from elevator array | DB aggregation query |
| L563 | Average fleet health: `reduce + /total` | DB `AVG(health)` |
| L571 | Dashboard trend: `genSeries(60, 30, 20)` | Real aggregated sensor trend |
| L772–773 | Sensor anomaly: compare value vs normal range | Backend anomaly detection |
| L808 | Faulty sensor base: uses `def.base` directly | Real telemetry |
| L1172 | Health trend: `genSeries(data.overall, 24, 10)` | Real health time-series |
| L1765 | Building health avg: `reduce + /length` | DB aggregation |

---

## 5. Mock Timing/Simulation

| Location | Mechanism | Purpose |
|---|---|---|
| L2069–2072 | `setInterval(3000)` → `tick` state increments | Simulates real-time sensor updates |
| L897–901 | `setTimeout(2200)` | Simulates AI analysis run duration |
| L1640–1643 | `setTimeout(1000)` | Simulates AI assistant thinking time |
| L2018 | `setTimeout(1600)` | Simulates QR code scanning duration |
| L1323–1332 | `setInterval(1000/speed)` | Timeline replay animation (keep as-is, this is UI feature) |

---

## Priority Replacement Order

1. **🔴 Critical** — Sensor telemetry (`genSeries`, `Math.random()` in `SensorMiniCard`)
2. **🔴 Critical** — Elevator state data (`ELEVATORS` constant)
3. **🔴 Critical** — Fault detection results (static detection + `FAULT_PROBS`)
4. **🔴 Critical** — Root cause analysis (static `ROOT_CAUSE_CHAIN`, `CONTRIBUTING_FACTORS`)
5. **🟠 High** — Predictive maintenance (`PM_COMPONENTS`, RUL data)
6. **🟠 High** — Health scores (`HEALTH_BREAKDOWN`)
7. **🟠 High** — Alerts (static `ALERTS`)
8. **🟡 Medium** — AI Assistant (static `assistantAnswer()`)
9. **🟡 Medium** — Maintenance tasks (static `MAINT_TASKS`)
10. **🟡 Medium** — Analytics metrics (hardcoded KPIs)
11. **🟢 Low** — Technicians, Reports, Admin, Audit Log
12. **🟢 Low** — Settings, User preferences
