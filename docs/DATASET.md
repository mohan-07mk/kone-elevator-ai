# AI4I 2020 Dataset & Telemetry Simulation Protocol

## Overview
Elevator AI uses the **AI4I 2020 Predictive Maintenance Dataset** from the UCI Machine Learning Repository (10,000 real industrial machine telemetry rows) as its foundational dataset. The dataset preprocessing pipeline translates industrial machine metrics into normalized elevator telemetry frames.

---

## 1. Dataset Mapping Specification

| Raw AI4I Field | Elevator AI Sensor Key | Units | Normal Range | Fault Threshold | Physical Mapping |
| :--- | :--- | :--- | :--- | :--- | :--- |
| `Process temperature [K]` | `motor_temp` | °C | 40 – 65 °C | > 75 °C | Elevator traction motor casing temperature |
| Derived (3-phase 400V) | `voltage` | V | 380 – 420 V | < 360 / > 440 V | Line supply voltage |
| `Torque [Nm]` & `Tool wear` | `current` | A | 10 – 18 A | > 22 A | Traction motor current draw |
| Derived ($V \times I \times \sqrt{3} \times PF$) | `power` | kW | 4.0 – 8.0 kW | > 10.5 kW | Real power consumption |
| `Rotational speed [rpm]` | `rpm` | rpm | 900 – 1500 rpm | < 700 / > 1700 rpm | Sheave rotational speed |
| `Tool wear [min]` + Failure Flag | `vibration` | mm/s | 0.0 – 4.5 mm/s | > 6.8 mm/s | Tri-axial bearing vibration magnitude |
| `TWF` / `HDF` Inverse | `brake` | % | 80 – 100 % | < 60 % | Brake lining wear index |
| Derived from `Product ID` | `load` | % | 0 – 90 % | > 100 % | Cabin passenger load percentage |
| `Air temperature [K]` | `humidity` | % | 30 – 60 % | > 85 % | Hoistway ambient relative humidity |
| Binary Event Signal | `door` | state | 0 (closed) / 1 (open) | 1 during motion | Door interlock safety loop signal |

---

## 2. Deterministic Simulation Scenarios

The simulator engine (`app/simulator/engine.py`) streams preprocessed telemetry frames deterministically:

1. `NORMAL`: Ground-truth operational baseline ($H = 95 - 100\%$, zero faults).
2. `BEARING_DEGRADATION`: Primary competition scenario.
   - Stage 1 (0 – 20% progress): Normal baseline ($V = 1.8\text{ mm/s}, T = 45^\circ\text{C}, I = 11.8\text{ A}$)
   - Stage 2 (20 – 50% progress): Micro-vibration increase ($V = 4.8\text{ mm/s}, T = 58^\circ\text{C}, I = 14.2\text{ A}$)
   - Stage 3 (50 – 80% progress): Thermal rise & current drag ($V = 8.5\text{ mm/s}, T = 78^\circ\text{C}, I = 18.5\text{ A}$)
   - Stage 4 (80 – 100% progress): Critical fault trigger ($V = 14.2\text{ mm/s}, T = 88^\circ\text{C}, I = 22.4\text{ A}$)
3. `MOTOR_OVERHEATING`: Thermal breakdown trajectory ($T > 85^\circ\text{C}$).
4. `DOOR_ALIGNMENT`: Door alignment drift & cycle friction.
5. `WARNING`: Unsupervised tool wear warning.

---

## 3. Dataset Caching & Offline Resilience

- **Local Cache Path**: `backend/datasets/cache/ai4i2020.csv` (~522 KB)
- **Automatic Fallback**: If internet access is unavailable, the backend reads directly from the local CSV cache.
- **Repository Inclusion**: The source repository includes the loader code and lightweight cached CSV to allow instant out-of-the-box execution without external web dependencies.
