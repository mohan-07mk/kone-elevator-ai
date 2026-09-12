"""Phase 5 Verification Script — Elevator AI Intelligence, RCA, RUL, Health & Alerts."""

from __future__ import annotations

import asyncio
import os
import sys

# Ensure backend path is present
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.database.session import async_session_factory, engine, Base
from app.models.models import AIInference, RCAResult, ElevatorHealthRecord, PredictiveRecord, AlertRecord
from app.ai.feature_extractor import extract_features
from app.ai.fault_detector import get_fault_detector
from app.ai.rca_engine import get_rca_engine
from app.ai.health_engine import get_health_engine
from app.ai.rul_engine import get_rul_engine
from app.ai.alert_engine import get_alert_engine
from app.ai.evaluator import evaluate_models
from app.ai.pipeline import get_ai_pipeline


async def test_ai_phase5():
    print("=== ELEVATOR AI — PHASE 5 VERIFICATION ===")

    # 1. Database Schema
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    print("✓ Database tables created & verified (AIInference, RCAResult, ElevatorHealthRecord, PredictiveRecord, AlertRecord)")

    # 2. Feature Extraction
    sample_window = [
        {"motor_temp": 45.0, "vibration": 1.5, "current": 12.0, "rpm": 1450.0, "voltage": 400.0, "load": 40.0},
        {"motor_temp": 48.2, "vibration": 5.8, "current": 14.5, "rpm": 1420.0, "voltage": 398.0, "load": 40.0},
        {"motor_temp": 52.4, "vibration": 12.6, "current": 18.2, "rpm": 1390.0, "voltage": 395.0, "load": 40.0},
    ]
    features = extract_features(sample_window)
    print(f"✓ Feature Extraction: vibration_rms={features['vibration_rms']} mm/s, temp_slope={features['temp_slope']} °C/step, current_dev={features['current_dev']} A")
    assert "vibration_rms" in features
    assert "temp_slope" in features

    # 3. Scikit-Learn ML Fault Classifier & Anomaly Detector
    detector = get_fault_detector()
    detector.train_models()
    inf_res = detector.predict(features)
    print(f"✓ ML Fault Classifier: fault_detected={inf_res.fault_detected}, fault_type='{inf_res.fault_type}', confidence={inf_res.confidence*100:.1f}%, severity='{inf_res.severity}', latency={inf_res.inference_time_ms} ms")
    assert inf_res.fault_detected is True
    assert inf_res.fault_type == "Bearing Degradation"

    # 4. Root Cause Analysis (RCA)
    rca_engine = get_rca_engine()
    rca_res = rca_engine.analyze("KONE-ELEV-001", inf_res, features)
    print(f"✓ Root Cause Analysis: affected_component='{rca_res.affected_component}', factors={len(rca_res.contributing_factors)}, steps={len(rca_res.verification_steps)}")
    assert "Bearing" in rca_res.affected_component
    assert len(rca_res.contributing_factors) >= 2

    # 5. Health Engine
    health_engine = get_health_engine()
    health_res = health_engine.calculate_health("KONE-ELEV-001", features)
    print(f"✓ Explainable Health: overall={health_res.overall_health}%, status='{health_res.status}', bearing_health={health_res.components.bearing}%")
    assert health_res.overall_health < 80.0

    # 6. RUL & Failure Risk Engine
    rul_engine = get_rul_engine()
    pred_res = rul_engine.predict("KONE-ELEV-001", health_res, features)
    print(f"✓ RUL Engine: failure_risk={pred_res.failure_risk}%, rul_hours={pred_res.rul_hours} hrs, priority='{pred_res.priority}'")
    assert pred_res.priority in ["High", "Critical"]
    assert pred_res.rul_hours < 500.0

    # 7. Automated Alert Generation
    alert_engine = get_alert_engine()
    alerts = alert_engine.evaluate_alerts("KONE-ELEV-001", inf_res, health_res, pred_res)
    print(f"✓ Alert Generator: generated {len(alerts)} alerts (Top alert: '{alerts[0].title}')")
    assert len(alerts) >= 1

    # 8. End-to-End Async AI Pipeline & DB Persistence
    async with async_session_factory() as session:
        pipeline_output = await get_ai_pipeline().process_telemetry(session, "KONE-ELEV-001", sample_window)
        print("✓ End-to-End AI Pipeline execution and DB persistence complete!")
        assert pipeline_output["elevator_id"] == "KONE-ELEV-001"

    # 9. ML Evaluation Metrics
    eval_res = evaluate_models()
    print(f"✓ ML Evaluation Metrics: Accuracy={eval_res['accuracy']*100:.1f}%, Precision={eval_res['precision']*100:.1f}%, F1={eval_res['f1_score']*100:.1f}%, RUL MAE={eval_res['rul_metrics']['mae_hours']} hrs")
    assert eval_res["accuracy"] > 0.80

    print("\n=== ALL PHASE 5 TESTS PASSED SUCCESSFULLY! ===")


if __name__ == "__main__":
    asyncio.run(test_ai_phase5())
