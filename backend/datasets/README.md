# Elevator AI — Dataset Documentation

## Dataset

**Name:** AI4I 2020 Predictive Maintenance Dataset  
**Source:** [UCI Machine Learning Repository](https://archive.ics.uci.edu/dataset/601/ai4i+2020+predictive+maintenance+dataset)  
**DOI:** [10.24432/C5HS5C](https://doi.org/10.24432/C5HS5C)  
**License:** [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/legalcode)  
**Records:** 10,000 data points  
**Citation:**

> AI4I 2020 Predictive Maintenance Dataset [Dataset]. (2020). UCI Machine Learning Repository.
> Matzka, S. (2020). Explainable Artificial Intelligence for Predictive Maintenance Applications.
> International Conference on Artificial Intelligence for Industries.

---

## Original Fields

| # | Field                  | Type    | Unit | Description                                      |
|---|------------------------|---------|------|--------------------------------------------------|
| 1 | UID                    | int     | —    | Unique identifier (1–10000)                      |
| 2 | Product ID             | string  | —    | Quality variant (L/M/H) + serial number          |
| 3 | Type                   | string  | —    | Product quality: L (50%), M (30%), H (20%)        |
| 4 | Air temperature        | float   | K    | Random walk, σ=2 K around 300 K                  |
| 5 | Process temperature    | float   | K    | Air temp + 10 K, σ=1 K                           |
| 6 | Rotational speed       | float   | rpm  | Derived from 2860 W power + noise                |
| 7 | Torque                 | float   | Nm   | Normal dist, μ=40 Nm, σ=10 Nm                    |
| 8 | Tool wear              | float   | min  | Cumulative wear (quality-dependent rate)          |
| 9 | Machine failure        | int     | —    | Binary label: 0=normal, 1=failure                |
| 10| TWF                    | int     | —    | Tool wear failure                                |
| 11| HDF                    | int     | —    | Heat dissipation failure                         |
| 12| PWF                    | int     | —    | Power failure                                    |
| 13| OSF                    | int     | —    | Overstrain failure                               |
| 14| RNF                    | int     | —    | Random failure                                   |

---

## Elevator Sensor Mapping

| Elevator Sensor  | Mapping Type | Source Field(s)               | Transformation                                      |
|------------------|-------------|-------------------------------|-----------------------------------------------------|
| `motor_temp`     | **Direct**  | Process temperature [K]       | Convert K → °C: `value - 273.15`                    |
| `voltage`        | **Derived** | Air temperature [K]           | Scale to 380–420V range: `380 + (air_temp - 295) * 4` |
| `current`        | **Derived** | Torque [Nm]                   | Scale to 5–25A range: `torque * 0.5`                |
| `power`          | **Derived** | Torque × RPM                  | `torque * rpm * 2π / 60` (mechanical power in watts) |
| `rpm`            | **Direct**  | Rotational speed [rpm]        | Direct mapping                                       |
| `vibration`      | **Derived** | Torque [Nm], Tool wear [min]  | `torque * 0.1 + tool_wear * 0.02` (mm/s)            |
| `brake`          | **Simulated**| Machine failure, Type         | Brake force 80–120N, degraded during failures        |
| `load`           | **Simulated**| Type (L/M/H)                  | Load percentage: L=30%, M=60%, H=90% ± noise        |
| `humidity`       | **Simulated**| Air temperature [K]           | Correlated: `50 + (air_temp - 300) * 2` (% RH)      |
| `door`           | **Simulated**| —                             | Cycle state: 0=closed, 1=open, based on sequence idx |

### Mapping Categories

- **Direct (2 fields):** Sensor values taken directly from the dataset with unit conversion only.
- **Derived (4 fields):** Computed from one or more dataset fields using physically meaningful formulas.
- **Simulated (4 fields):** Generated deterministically from dataset characteristics + sequence position.

---

## Preprocessing Pipeline

```text
1. LOAD        → Download/read CSV from UCI repository
2. VALIDATE    → Check for missing values, type consistency, range checks
3. CLEAN       → Remove UID/Product ID (not needed for telemetry)
4. NORMALIZE   → Convert units (K→°C), scale to elevator-appropriate ranges
5. MAP         → Apply sensor mapping transformations
6. SEQUENCE    → Order records to create temporal degradation patterns
7. AUGMENT     → Add simulated fields (brake, load, humidity, door)
8. EXPORT      → Produce normalized telemetry records matching sensor contract
```

---

## Failure Mode → Elevator Scenario Mapping

| Dataset Failure Mode | Elevator Scenario        | Description                                       |
|----------------------|--------------------------|---------------------------------------------------|
| HDF (Heat Dissipation)| MOTOR_OVERHEATING       | Process temp rise → motor temperature anomaly      |
| OSF (Overstrain)     | BEARING_DEGRADATION      | Torque × wear → bearing stress / vibration         |
| TWF (Tool Wear)      | WARNING                  | Gradual degradation comparable to component wear   |
| PWF (Power Failure)  | NORMAL → WARNING         | Power out of range → electrical anomaly            |
| No failure           | NORMAL                   | Baseline healthy operation                         |

---

## Deterministic Demo Scenario

The `KONE-ELEV-001` demo scenario uses a curated subset of ~500 records ordered to produce:

```text
PHASE 1: Normal operation          (records 1–100)
PHASE 2: Vibration increases       (records 101–200)
PHASE 3: Temperature increases     (records 201–300)
PHASE 4: Current increases         (records 301–400)
PHASE 5: RPM stability decreases   (records 401–450)
PHASE 6: Bearing degradation       (records 451–500)
```

This sequence is **deterministic** — the same seed and dataset always produces the same telemetry stream.

---

## Limitations

1. **Not real elevator data.** This is an industrial predictive maintenance dataset mapped to elevator sensor semantics.
2. **Synthetic origin.** The AI4I dataset itself is synthetic (designed to reflect real industrial patterns).
3. **Simulated fields.** 4 of 10 sensor channels (brake, load, humidity, door) are generated rather than measured.
4. **No spatial data.** No floor position, shaft vibration profile, or rope tension data.
5. **Temporal ordering is constructed.** The original dataset has no inherent time series; we impose ordering for degradation simulation.
6. **Scale mismatch.** Original data represents manufacturing processes, not vertical transportation — physical units are approximated.

---

## How to Obtain the Dataset

The pipeline automatically downloads the dataset on first run. Manual download:

```bash
# Option 1: Python package
pip install ucimlrepo
python -c "from ucimlrepo import fetch_ucirepo; d = fetch_ucirepo(id=601); d.data.features.to_csv('ai4i_dataset.csv')"

# Option 2: Direct download
curl -O https://archive.ics.uci.edu/static/public/601/ai4i+2020+predictive+maintenance+dataset.zip
```
