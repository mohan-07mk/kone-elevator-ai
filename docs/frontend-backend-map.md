# Frontend → Backend Integration Map

> **Elevator AI — Phase 1 Analysis**
> Generated from `ElevatorAI.jsx` (2,147 lines, 126 KB)

---

## 1. Dashboard (`DashboardPage` — Line 557)

```
Frontend Page: Dashboard
↓
Required Backend APIs:
  GET /api/elevators                     → Fleet list with status, health, fault, risk
  GET /api/fleet/summary                 → Total, healthy, warning, critical counts
  GET /api/fleet/health                  → Average fleet health score
  GET /api/alerts?limit=5                → Latest 5 alerts for live alerts panel
  GET /api/sensors/trend?metric=vibration → Aggregated vibration trend data (30 pts)
  GET /api/faults/critical               → List of critical-status elevators
↓
Required Database Data:
  elevators         → id, building_id, floor, direction, status, health, fault, risk, speed, load, door, connection, updated_at
  alerts            → id, level, text, elevator_id, created_at, read
  sensor_telemetry  → time-series vibration index (aggregated across fleet)
↓
Required AI/Processing Service:
  Fleet health score aggregation (currently: simple average)
  Predicted failures count (currently: hardcoded "3")
  Maintenance due count (currently: hardcoded "6")
↓
WebSocket Requirement:
  ws://host/ws/fleet-status             → Real-time fleet status push (health, counts)
  ws://host/ws/alerts                   → Real-time alert push
```

---

## 2. Live Monitoring (`MonitoringPage` — Line 800)

```
Frontend Page: Live Monitoring
↓
Required Backend APIs:
  GET /api/elevators/{id}                → Single elevator detail (floor, dir, speed, door, health, status)
  GET /api/elevators/{id}/sensors        → All sensor current values for the elevator
  GET /api/elevators/{id}/sensors/{key}/trend?range={1H|6H|24H|7D}
                                         → Time-series data for specific sensor & range
↓
Required Database Data:
  elevators         → id, floor, direction, speed, load, door_status, connection_status, health
  sensor_telemetry  → time-series for each sensor (motorTemp, voltage, current, power, rpm, vibration, brake, load, humidity)
  sensor_defs       → key, label, unit, normal_range (min, max)
↓
Required AI/Processing Service:
  Anomaly detection per sensor (is value out of normal range?)
  Percentage change calculation vs previous reading
↓
WebSocket Requirement:
  ws://host/ws/elevator/{id}/sensors    → Real-time sensor feed (updates every 3 sec currently via setInterval + Math.random())
  ws://host/ws/elevator/{id}/status     → Elevator status changes (floor, direction, door)
```

---

## 3. AI Fault Detection (`DetectionPage` — Line 889)

```
Frontend Page: AI Fault Detection
↓
Required Backend APIs:
  POST /api/ai/fault-detection/run       → Trigger AI fault analysis for a specific elevator
  GET  /api/ai/fault-detection/status    → Analysis status (running, complete)
  GET  /api/ai/fault-detection/result    → Fault detection result (fault type, confidence, severity, component, detection time)
  GET  /api/ai/fault-probabilities       → Fault category probabilities list (10 categories)
↓
Required Database Data:
  fault_detections   → id, elevator_id, fault_type, confidence, severity, component, detected_at, model_version
  fault_categories   → name, probability_score, elevator_id, analysis_id
  sensor_telemetry   → Historical data for AI model input
↓
Required AI/Processing Service:
  Sensor Fusion Model — cross-references vibration, thermal, electrical signatures
  Fault Classification Engine — probability distribution across 10 fault categories
  Confidence scoring — currently Math.random() * 8 + 90
↓
WebSocket Requirement:
  ws://host/ws/ai/analysis-progress     → Real-time analysis progress during "Run AI Analysis"
```

---

## 4. Root Cause Analysis (`RootCausePage` — Line 977)

```
Frontend Page: Root Cause Analysis
↓
Required Backend APIs:
  GET /api/ai/rca/{elevator_id}          → Root cause chain (ordered steps)
  GET /api/ai/rca/{elevator_id}/result   → Root cause result (cause, confidence, severity)
  GET /api/ai/rca/{elevator_id}/factors  → Contributing factors with values
  GET /api/ai/rca/{elevator_id}/timeline → Event correlation timeline
↓
Required Database Data:
  rca_analyses       → id, elevator_id, root_cause, confidence, severity, recommended_action, analyzed_at
  rca_chain_steps    → analysis_id, step_order, label, detail, sensor_source
  contributing_factors → analysis_id, label, actual_value, baseline_value
  timeline_events    → time, type, title, severity, sensor, description
↓
Required AI/Processing Service:
  Root Cause Analysis Engine — multi-step causal reasoning
  Event Correlation — temporal pattern matching across sensor streams
  Recommendation Engine — action recommendations based on identified root cause
↓
WebSocket Requirement:
  None (analysis is retrospective, not real-time)
```

---

## 5. Predictive Maintenance (`PredictivePage` — Line 1082)

```
Frontend Page: Predictive Maintenance
↓
Required Backend APIs:
  GET /api/predictive/components/{elevator_id}  → Component list with health, risk, RUL, action
  GET /api/predictive/rul/{elevator_id}/{component}  → RUL projection data over time
  GET /api/predictive/recommendations      → AI-ranked recommendations sorted by urgency
↓
Required Database Data:
  component_health    → component_name, health_score, risk_level, rul_days, recommended_action, elevator_id
  rul_projections     → component_id, projected_date, projected_health
  maintenance_recommendations → component_id, urgency_rank, action, reason
↓
Required AI/Processing Service:
  Remaining Useful Life (RUL) Prediction Model — per component
  Component Health Scoring Engine — currently hardcoded in PM_COMPONENTS
  Risk Classification — Low/Medium/High
  Urgency Ranking — sorted recommendations
↓
WebSocket Requirement:
  ws://host/ws/predictive/updates        → Push when RUL or health scores change significantly
```

---

## 6. Elevator Health (`HealthPage` — Line 1163)

```
Frontend Page: Elevator Health
↓
Required Backend APIs:
  GET /api/elevators/{id}/health           → Overall health score + per-component breakdown
  GET /api/elevators/{id}/health/summary   → AI-generated health summary text
  GET /api/elevators/{id}/health/trend?span={today|7d|30d|6mo}  → Historical health trend
↓
Required Database Data:
  health_scores       → elevator_id, overall, motor, bearing, brake, door, electrical, sensor, drive, summary_text, timestamp
  health_history      → elevator_id, timestamp, overall_score (time-series)
↓
Required AI/Processing Service:
  Health Score Calculator — weighted composite from component metrics
  Health Summary NLG — natural language summary generation
  Health Trend Analysis — historical tracking and anomaly flagging
↓
WebSocket Requirement:
  ws://host/ws/elevator/{id}/health      → Real-time health score push
```

---

## 7. Analytics (`AnalyticsPage` — Line 1239)

```
Frontend Page: Analytics
↓
Required Backend APIs:
  GET /api/analytics/metrics?building={id}&severity={level}&dateRange={range}
                                           → KPI metrics (MTBF, MTTR, cost, availability, etc.)
  GET /api/analytics/fault-trends?range={7d|30d|90d}  → Daily fault counts
  GET /api/analytics/fault-mix              → Fault category distribution
↓
Required Database Data:
  fault_events       → id, elevator_id, building_id, fault_type, severity, occurred_at, resolved_at
  maintenance_costs  → task_id, cost, date
  downtime_records   → elevator_id, start_time, end_time, duration
↓
Required AI/Processing Service:
  MTBF Calculation (currently hardcoded "42 days")
  MTTR Calculation (currently hardcoded "3.1 hrs")
  Fleet Availability Calculation (currently hardcoded "98.6%")
  Cost Aggregation (currently hardcoded "₹4.2L")
↓
WebSocket Requirement:
  None (analytics are aggregated, not real-time)
```

---

## 8. Fault Timeline (`TimelinePage` — Line 1318)

```
Frontend Page: Fault Timeline & Failure Replay
↓
Required Backend APIs:
  GET /api/faults/{elevator_id}/timeline   → Ordered event sequence for a fault episode
↓
Required Database Data:
  fault_timeline_events → elevator_id, fault_id, time, event_type, title, severity, sensor, description, sequence_order
↓
Required AI/Processing Service:
  Event Sequencing — ordering events in causal chain
  Failure Replay Engine — reconstructing the fault progression
↓
WebSocket Requirement:
  None (replay is historical)
```

---

## 9. Maintenance (`MaintenancePage` — Line 1381)

```
Frontend Page: Maintenance Command Center
↓
Required Backend APIs:
  GET    /api/maintenance/tasks?status={status}  → Filtered task list
  POST   /api/maintenance/tasks                  → Create new maintenance task
  PATCH  /api/maintenance/tasks/{id}             → Update task (mark complete, reassign)
  DELETE /api/maintenance/tasks/{id}             → Delete task
↓
Required Database Data:
  maintenance_tasks   → id, elevator_id, building_name, fault_description, priority, technician_id, scheduled_date, status
↓
Required AI/Processing Service:
  Task Auto-Generation — from detected faults
  Priority Assignment — based on fault severity and RUL
↓
WebSocket Requirement:
  ws://host/ws/maintenance/updates       → Push task status changes
```

---

## 10. Technicians (`TechniciansPage` — Line 1457)

```
Frontend Page: Technician Management
↓
Required Backend APIs:
  GET  /api/technicians                   → Technician list with availability, workload, specialization
  GET  /api/ai/recommend-technician?task_id={id}  → AI-recommended technician for a task
  POST /api/technicians/{id}/assign       → Assign technician to task
↓
Required Database Data:
  technicians         → name, role, availability, current_task_count, completed_count, specialization
  task_assignments    → technician_id, task_id, assigned_at
↓
Required AI/Processing Service:
  Technician Recommendation Engine — based on availability, skill match, workload
↓
WebSocket Requirement:
  ws://host/ws/technicians/status        → Real-time availability changes
```

---

## 11. Reports (`ReportsPage` — Line 1510)

```
Frontend Page: Automated Maintenance Reports
↓
Required Backend APIs:
  GET  /api/reports                       → List of generated reports
  GET  /api/reports/{id}/preview          → Report preview data (summary, root cause, recommendation)
  POST /api/reports/generate              → Generate new report
  GET  /api/reports/{id}/download?format=pdf  → Download report as PDF
↓
Required Database Data:
  reports             → id, type, elevator_id, generated_at, status, content_json
↓
Required AI/Processing Service:
  Report Generation Engine — compiles fault analysis, root cause, recommendation into report
  PDF Generation Service (e.g., WeasyPrint, Puppeteer)
↓
WebSocket Requirement:
  None
```

---

## 12. AI Assistant (`AssistantPage` — Line 1624)

```
Frontend Page: AI Maintenance Assistant
↓
Required Backend APIs:
  POST /api/ai/assistant/chat             → Send user query, receive structured AI response
                                            Request: { message: string, context: { elevator_id, building_id } }
                                            Response: { summary, rootCause, data, action, priority }
↓
Required Database Data:
  chat_history        → session_id, role (user/ai), message, timestamp
  All other tables    → AI needs access to entire system state for grounding
↓
Required AI/Processing Service:
  LLM Integration (or rule-based NLU) — currently keyword-matching in assistantAnswer()
  Context Retrieval — pulls relevant data from telemetry, faults, tasks, health scores
  Response Structuring — summary + root cause + data + action + priority
↓
WebSocket Requirement:
  ws://host/ws/ai/assistant              → Streaming AI response for real-time typing effect
```

---

## 13. Buildings & Elevators (`BuildingsPage` — Line 1726)

```
Frontend Page: Buildings & Multi-Elevator Monitoring
↓
Required Backend APIs:
  GET /api/buildings                      → List of buildings with location, elevator count
  GET /api/buildings/{id}/elevators       → Elevators in a specific building with status, health
  GET /api/buildings/{id}/health          → Aggregated building health score
↓
Required Database Data:
  buildings           → id, name, location, elevator_count
  elevators           → (linked via building_id) status, health, floor, direction, risk
↓
Required AI/Processing Service:
  Building-level health aggregation
↓
WebSocket Requirement:
  ws://host/ws/buildings/status          → Real-time building health updates
```

---

## 14. Alerts & Notifications (`AlertsPage` — Line 1806)

```
Frontend Page: Alert Center
↓
Required Backend APIs:
  GET   /api/alerts?level={filter}        → Filtered alerts list
  PATCH /api/alerts/{id}/read             → Mark alert as read
  PATCH /api/alerts/{id}/acknowledge      → Acknowledge alert
  PATCH /api/alerts/{id}/resolve          → Resolve alert
  POST  /api/alerts/{id}/create-task      → Create maintenance task from alert
↓
Required Database Data:
  alerts              → id, level (critical/warning/info/resolved), text, elevator_id, created_at, read, acknowledged, resolved_at
↓
Required AI/Processing Service:
  Alert Generation — triggered by sensor threshold breaches and AI detections
  Alert Deduplication — prevent duplicate alerts for same condition
↓
WebSocket Requirement:
  ws://host/ws/alerts                    → Real-time alert push (critical: immediate, warning: near-real-time)
```

---

## 15. Admin Panel (`AdminPage` — Line 1852)

```
Frontend Page: Admin Management
↓
Required Backend APIs:
  CRUD /api/admin/buildings               → Building management
  CRUD /api/admin/elevators               → Elevator management
  CRUD /api/admin/users                   → User management
  CRUD /api/admin/technicians             → Technician management
  CRUD /api/admin/sensors                 → Sensor configuration
  GET/PUT /api/admin/alert-thresholds     → Alert threshold configuration (vibration, motorTemp, current)
  GET  /api/admin/audit-log               → System audit log
↓
Required Database Data:
  buildings, elevators, users, technicians, sensor_defs, alert_thresholds, audit_log
↓
Required AI/Processing Service:
  None (pure CRUD administration)
↓
WebSocket Requirement:
  None
```

---

## 16. Settings (`SettingsPage` — Line 1945)

```
Frontend Page: Settings
↓
Required Backend APIs:
  GET/PUT /api/settings/profile           → User profile (name, email)
  GET/PUT /api/settings/preferences       → System preferences (dark mode, language)
  GET/PUT /api/settings/notifications     → Notification preferences (critical, warning, info, email toggles)
  GET/PUT /api/settings/alert-thresholds  → Alert thresholds (shared with Admin)
↓
Required Database Data:
  user_preferences    → user_id, dark_mode, language, notification_settings
  alert_thresholds    → sensor_key, threshold_value
↓
Required AI/Processing Service:
  None
↓
WebSocket Requirement:
  None
```

---

## Shared Components & Their Backend Needs

| Component | Backend Dependency |
|---|---|
| `Sidebar` | Navigation config + role-based access (currently: `NAV` array with roles) |
| `Topbar` | Buildings list, Elevators list, unread alert count, role switching |
| `QRModal` | `GET /api/elevators/{id}` — lookup elevator by QR code |
| `KPICard / Counter` | Various aggregated metrics from fleet data |
| `GaugeChart` | Health score (single numeric value) |
| `Sparkline / Charts` | Time-series sensor data |
| `StatusBadge / StatusDot` | Status enum from elevator/alert data |
| `Modal` | Generic container — no backend dependency |

---

## API Summary Count

| Category | API Count |
|---|---|
| Fleet / Elevator | 8 |
| Sensor / Telemetry | 4 |
| AI / ML | 7 |
| Maintenance / Tasks | 4 |
| Alerts | 5 |
| Admin / CRUD | 7 |
| Settings | 4 |
| Reports | 4 |
| Technicians | 3 |
| Buildings | 3 |
| **Total** | **~49 API endpoints** |
