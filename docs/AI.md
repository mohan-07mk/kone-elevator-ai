# AI & Predictive Analytics Methodology

## Overview
Elevator AI features an end-to-end artificial intelligence pipeline engineered specifically for industrial equipment diagnostics. The system combines multi-variable machine learning, probabilistic anomaly detection, graph-based root cause analysis (RCA), and physics-informed degradation modeling for Remaining Useful Life (RUL) estimation.

---

## 1. AI Pipeline Overview

```
[ Raw Telemetry ] ──► [ Feature Extraction ] ──► [ AI Pipeline Manager ]
                                                        │
         ┌──────────────────────────────────────────────┼──────────────────────────────────────────────┐
         ▼                                              ▼                                              ▼
[ Fault Classifier ]                         [ Anomaly Detector ]                           [ RCA Engine ]
Random Forest Model                          Isolation Forest Model                         Diagnostic Causal Graph
Catches known fault signatures               Catches unknown drift                         Identifies root component
         │                                              │                                              │
         └──────────────────────────────────────────────┼──────────────────────────────────────────────┘
                                                        ▼
                                           [ Health & RUL Synthesizer ]
                                           Overall Health Score (0-100)
                                           Projected RUL Hours & Days
```

---

## 2. Machine Learning Models

### 2.1 Supervised Fault Classifier (`RandomForestClassifier`)
- **Architecture**: 50 Decision Trees, balanced subsample weighting.
- **Input Features (14 variables)**:
  1. `motor_temp` (°C) — Motor casing temperature
  2. `voltage` (V) — 3-phase line voltage
  3. `current` (A) — Motor draw current
  4. `power` (kW) — Real power consumption
  5. `rpm` (rpm) — Sheave rotational speed
  6. `vibration` (mm/s) — Tri-axial vibration magnitude
  7. `brake` (%) — Brake lining health index
  8. `load` (%) — Cabin load capacity
  9. `humidity` (%) — Hoistway relative humidity
  10. `door` (state/signal) — Door mechanism state
  11. `vibration_rms` — RMS rolling window vibration
  12. `temp_slope` — Rate of thermal rise (°C/min)
  13. `current_dev` — Deviation from load-normalized current baseline
  14. `rpm_var` — Variance in rotational speed under steady state
- **Target Classes**:
  - `Healthy Operational State`
  - `Bearing Degradation`
  - `Motor Overheating`
  - `Door Alignment Drift`
  - `Component Tool Wear Warning`

### 2.2 Unsupervised Anomaly Detection (`IsolationForest`)
- **Contamination Parameter**: 0.05 (5%)
- **Purpose**: Detect novel multi-sensor anomalies that do not match existing historical fault templates.

---

## 3. Root Cause Analysis (RCA) Engine

When an anomaly or fault is flagged, the RCA Engine constructs a causal diagnostic tree:
1. **Primary Anomaly Isolation**: Evaluates which sensor exceeded normalized threshold limits first.
2. **Thermal & Electrical Cross-Correlation**: Checks if thermal rise correlates with current draw increases.
3. **Mechanical Signature Verification**: Verifies vibration frequency signature against bearing race defect patterns.
4. **Causal Node Graphing**:
   ```
   [ Abnormal Vibration: 8.8 mm/s ]
             │
             ▼
   [ Thermal Escalation: +18.5% ]
             │
             ▼
   [ Current Spike: 19.4 A ]
             │
             ▼
   [ Root Cause Identified: Motor Bearing Wear — Confidence: 94.2% ]
   ```

---

## 4. System Health & RUL Calculation

### 4.1 Component Health Weights
The overall elevator health score $H_{\text{overall}} \in [0, 100]$ is computed as:
$$H_{\text{overall}} = 0.25 H_{\text{motor}} + 0.25 H_{\text{bearing}} + 0.15 H_{\text{brake}} + 0.15 H_{\text{door}} + 0.10 H_{\text{drive}} + 0.10 H_{\text{electrical}}$$

### 4.2 RUL Estimation Model
RUL (Remaining Useful Life) is modeled using an exponential degradation equation:
$$\text{RUL}_{\text{hours}} = \text{RUL}_{\text{baseline}} \times e^{-\alpha \cdot D}$$
where $D$ is the current degradation factor derived from vibration amplitude and temperature slope, and $\text{RUL}_{\text{baseline}}$ is set to 720 operating hours (30 days).

---

## 5. Hardware Acceleration Abstraction & Truthfulness

The runtime manager (`app/ai/runtime.py`) implements transparent hardware reporting:

- **Supported Hardware Providers**:
  - `QNNExecutionProvider`: Qualcomm Hexagon NPU
  - `DmlExecutionProvider`: DirectML Hardware Acceleration
  - `CPUExecutionProvider`: Standard multi-core CPU execution
- **API Endpoint**: `GET /api/ai/status`
- **Truthful Status Reporting**:
  ```json
  {
    "device": "CPU",
    "runtime": "ONNX Runtime v1.17.0",
    "accelerator": "CPUExecutionProvider (Fallback)",
    "model": "ElevatorFaultClassifier.onnx",
    "model_version": "1.0.0",
    "inference_latency_ms": 1.42,
    "status": "fallback",
    "acceleration_available": false,
    "fallback_reason": "Qualcomm Hexagon QNN / DirectML Execution Providers not detected in current OS environment; operating via CPUExecutionProvider fallback."
  }
  ```
- **Truthfulness Commitment**: No fake benchmark numbers or fabricated NPU claims are emitted. If NPU hardware is absent, the system explicitly reports CPU fallback.
