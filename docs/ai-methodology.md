# Elevator AI — Artificial Intelligence & Machine Learning Methodology

This document details the Machine Learning pipeline, feature engineering, fault classification algorithms, Root Cause Analysis (RCA), Remaining Useful Life (RUL) modeling, and local ONNX runtime abstraction used in the **Elevator AI Platform**.

---

## 1. Feature Engineering Engine (`backend/app/ai/feature_extractor.py`)

Raw sensor readings are processed across sliding temporal windows ($N=5..20$ frames) to extract 10 statistically rich statistical features:

$$\text{RMS} = \sqrt{\frac{1}{N} \sum_{i=1}^N x_i^2}$$

$$\text{Peak} = \max(|x_1|, |x_2|, \dots, |x_N|)$$

* **Vibration RMS & Peak**: Quantifies structural vibration energy and impact shocks.
* **Rolling Mean & Std Dev**: Smooths transient noise and measures metric variability.
* **Thermal Slope ($\Delta T / \Delta t$)**: Detects rapid temperature acceleration prior to thermal breakdown.
* **Current Deviation ($\Delta I$)**: Measures variance from baseline motor current.
* **RPM Variance**: Identifies slip or motor hunting.
* **Load-Normalized Current ($I / L$)**: Normalizes motor current against payload to prevent false alarms during heavy passenger loads.

---

## 2. Multi-Stage Anomaly Detection & ML Fault Classification (`backend/app/ai/fault_detector.py`)

```text
Feature Vector (10 Dimensions)
            │
            ▼
┌───────────────────────┐      Anomaly Detected
│ Isolation Forest      ├───────────────────────────────┐
│ (Unsupervised Anomaly)│                               │
└───────────┬───────────┘                               ▼
            │ Nominal                    ┌────────────────────────────┐
            ▼                            │ Random Forest Classifier   │
┌───────────────────────┐                │ (Supervised Multi-Class)   │
│ Normal Operational    │                └──────────────┬─────────────┘
│ State (Confidence:0%) │                               │
└───────────────────────┘                               ▼
                                         Fault Class + Confidence + Severity
```

### ML Fault Categories
1. **Bearing Degradation**: Characterized by elevated vibration RMS + high peak acceleration.
2. **Motor Overheating**: High thermal slope + elevated current draw.
3. **Door Alignment Drift**: Door sensor timing anomalies + elevated current spikes during open/close cycles.
4. **Brake Wear & Slippage**: High current draw during deceleration + RPM overspeed variance.
5. **VFD Inverter Fault**: Harmonic distortion in voltage/current ratio + load imbalance.

---

## 3. Explainable Root Cause Analysis (RCA) Engine (`backend/app/ai/rca_engine.py`)

Rather than black-box outputs, the RCA engine isolates exact failing hardware sub-assemblies:
* **Primary Root Cause Statement**
* **Affected Sub-Assembly Isolation** (`Main Drive Bearing`, `Motor Stator Winding`, `Door Interlock Track`)
* **Ranked Factor Weights**: Ranks contributing sensor metrics by normalized feature importances.
* **Verification Steps**: Actionable diagnostic procedures for field technicians.

---

## 4. Health Scoring & Remaining Useful Life (RUL) (`backend/app/ai/health_engine.py`, `backend/app/ai/rul_engine.py`)

* **Component Health Index**: Weighted composite of sub-system degradation ($H_{\text{motor}}, H_{\text{bearing}}, H_{\text{door}}, H_{\text{brake}}, H_{\text{electrical}}$).
* **RUL Calculation**: Accelerates degradation hours ($RUL_{\text{hours}}$) based on exponential stress factors derived from vibration amplitude and thermal slope.

---

## 5. Local ONNX Runtime & Snapdragon Hardware Acceleration (`backend/app/ai/runtime.py`)

* **Abstraction Interface**: Integrates `onnxruntime.InferenceSession` with support for Qualcomm Hexagon NPU (`QNNExecutionProvider`), DirectML (`DmlExecutionProvider`), and CPU (`CPUExecutionProvider`).
* **Fallback & Audit**: Gracefully falls back to CPU if hardware acceleration dependencies are absent, logging exact diagnostic status via `/api/ai/status`.
