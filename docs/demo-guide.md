# KONE ELEVATOR AI — COMPETITION DEMO GUIDE & REPRODUCIBLE WALKTHROUGH

This document provides a minute-by-minute, reproducible 4-minute demonstration script for judging and live competition walkthroughs of the **Elevator AI Predictive Maintenance Platform**.

---

## ⏱ Demo Timeline Script

```text
┌────────┬─────────────────────────────┬────────────────────────────────────────────────────────────────────────────┐
│ Time   │ Phase                       │ Demo Action & Description                                                  │
├────────┼─────────────────────────────┼────────────────────────────────────────────────────────────────────────────┤
│ 0:00   │ Fleet Dashboard             │ Open Dashboard page. Show live fleet metrics (10 elevators, health score,  │
│        │                             │ active alerts banner, building breakdown, live telemetry feed).            │
├────────┼─────────────────────────────┼────────────────────────────────────────────────────────────────────────────┤
│ 0:30   │ Scenario Start              │ Navigate to Live Monitoring page. Select elevator `KONE-ELEV-001`.         │
│        │                             │ Click "Inject Fault: Bearing Degradation" in Demo Controls.                │
├────────┼─────────────────────────────┼────────────────────────────────────────────────────────────────────────────┤
│ 1:00   │ Telemetry Shift             │ Observe real-time telemetry charts: Vibration spikes from 1.2 to >8.8 mm/s;│
│        │                             │ Motor temp climbs above 78°C; Current draws spike to 18.5 A.               │
├────────┼─────────────────────────────┼────────────────────────────────────────────────────────────────────────────┤
│ 1:30   │ AI Fault Detection          │ Click AI Fault Detection page. Highlight real-time Random Forest / ONNX    │
│        │                             │ classification returning: `Bearing Degradation` (Confidence: 94.2%).      │
├────────┼─────────────────────────────┼────────────────────────────────────────────────────────────────────────────┤
│ 2:00   │ Root Cause Analysis (RCA)   │ Navigate to Root Cause Analysis page. Point out isolated root cause:        │
│        │                             │ "Outer Race Micro-Spalling", affected component: `Main Motor Bearing`.      │
├────────┼─────────────────────────────┼────────────────────────────────────────────────────────────────────────────┤
│ 2:30   │ Health & RUL                │ Open Predictive RUL page. Health drops from 100% to 42%. RUL drops to     │
│        │                             │ 28.5 Hours. Explainable health degradation factors displayed visually.     │
├────────┼─────────────────────────────┼────────────────────────────────────────────────────────────────────────────┤
│ 3:00   │ Alerts & Maintenance        │ Open Maintenance page. Critical alert generated automatically. Show       │
│        │                             │ auto-created task `TASK-101` and recommended technician `R. Karthik`.     │
├────────┼─────────────────────────────┼────────────────────────────────────────────────────────────────────────────┤
│ 3:30   │ AI Assistant                │ Open AI Assistant page. Query: "What should technician do for ELEV-001?"   │
│        │                             │ AI Assistant responds using actual backend database & RAG telemetry data. │
├────────┼─────────────────────────────┼────────────────────────────────────────────────────────────────────────────┤
│ 4:00   │ Snapdragon AI Benchmark     │ Return to Detection page. Highlight Snapdragon Local AI Architecture card. │
│        │                             │ Click "Run AI Benchmark". Show truthful 0.024ms latency and CPU fallback.  │
└────────┴─────────────────────────────┴────────────────────────────────────────────────────────────────────────────┘
```

---

## 🛠 Prerequisites & Quick Execution

1. Start full container stack:
   ```bash
   docker-compose up --build
   ```
2. Open browser to `http://localhost:3000`.
3. Follow the 4-minute timeline above.
