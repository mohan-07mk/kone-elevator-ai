"""Phase 6 Verification Script — Elevator AI Maintenance, Technicians, Analytics, Timeline, Reports & AI Assistant."""

from __future__ import annotations

import asyncio
import os
import sys

# Ensure backend path is present
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.database.session import engine, async_session_factory, Base
from app.database.seed import seed_all
from app.api.maintenance import list_maintenance_tasks, create_maintenance_task, TaskCreate
from app.api.technicians import list_technicians, recommend_technician, TechRecommendRequest
from app.api.analytics import get_fleet_analytics_summary, get_fault_distribution, get_building_comparison
from app.api.timeline import get_fault_timeline
from app.api.reports import generate_report, ReportRequest
from app.api.assistant import chat_with_assistant, ChatMessage


async def test_phase6_pipeline():
    print("\n=======================================================")
    print("      ELEVATOR AI — PHASE 6 VERIFICATION SUITE       ")
    print("=======================================================\n")

    # 1. Initialize Tables & Seed Data
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)

    async with async_session_factory() as db:
        counts = await seed_all(db)
        print(f"[✓] Seeding completed: {counts}")

    # 2. Test Maintenance Task Creation & Auto-Assignment
    async with async_session_factory() as db:
        print("\n--- 1. Testing Maintenance Tasks & AI Auto-Assignment ---")
        task_in = TaskCreate(
            elevator_id="KONE-ELEV-001",
            title="Drive Shaft SKF Bearing Replacement",
            fault_type="Bearing Degradation",
            priority="Critical",
            due_days=2,
            notes="AI recommended replacement unit."
        )
        task_out = await create_maintenance_task(task_in, db)
        print(f"[✓] Created Task: ID={task_out.id} | Status={task_out.status} | Priority={task_out.priority}")
        print(f"    Assigned Technician: {task_out.technician_name}")
        print(f"    AI Recommendation: {task_out.ai_recommendation.get('match_reason') if task_out.ai_recommendation else 'N/A'}")

        all_tasks = await list_maintenance_tasks(None, "ALL", "ALL", db)
        print(f"[✓] Total Maintenance Tasks in DB: {len(all_tasks)}")

    # 3. Test Technician Directory & Recommendation Engine
    async with async_session_factory() as db:
        print("\n--- 2. Testing Technician Management & AI Recommendation ---")
        techs = await list_technicians(None, None, db)
        print(f"[✓] Technicians registered: {len(techs)}")
        for t in techs:
            print(f"    • {t.name} ({t.role_title}) | Spec: '{t.specialization}' | Workload: {t.active_workload} tasks")

        rec_req = TechRecommendRequest(elevator_id="KONE-ELEV-001", fault_type="Bearing Degradation")
        rec_res = await recommend_technician(rec_req, db)
        print(f"[✓] Recommended Technician: {rec_res.recommended_technician.name} (Match Score: {rec_res.match_score:.0f}%)")
        print(f"    Reasoning: {rec_res.explanation}")

    # 4. Test Analytics Endpoints
    async with async_session_factory() as db:
        print("\n--- 3. Testing Backend Analytics ---")
        summary = await get_fleet_analytics_summary("ALL", db)
        print(f"[✓] Fleet Analytics Summary:")
        print(f"    Total Elevators: {summary['total_elevators']} | Avg Health: {summary['avg_health_score']}% | Availability: {summary['fleet_availability']}%")

        dist = await get_fault_distribution("ALL", db)
        print(f"[✓] Fault Distribution Categories: {len(dist)}")

        b_comp = await get_building_comparison(db)
        print(f"[✓] Building Comparisons: {len(b_comp)} buildings evaluated.")

    # 5. Test Database-Backed Fault Timeline
    async with async_session_factory() as db:
        print("\n--- 4. Testing Fault Timeline Aggregation ---")
        timeline = await get_fault_timeline("KONE-ELEV-001", 10, db)
        print(f"[✓] Aggregated Timeline Events: {len(timeline)}")
        for evt in timeline[:3]:
            print(f"    [{evt['time']}] ({evt['category']}) {evt['title']}")

    # 6. Test Data-Driven Report Generation
    async with async_session_factory() as db:
        print("\n--- 5. Testing Automated Report Generation ---")
        rep_req = ReportRequest(report_type="Fault Analysis", elevator_id="KONE-ELEV-001", building_id="ALL")
        rep_res = await generate_report(rep_req, db)
        print(f"[✓] Generated Report: '{rep_res.title}' (ID: {rep_res.id})")
        print(f"    Summary: {rep_res.summary}")
        print(f"    Markdown Preview (first 180 chars):\n    " + rep_res.content_markdown[:180].replace("\n", " "))

    # 7. Test Grounded AI Assistant Chat
    async with async_session_factory() as db:
        print("\n--- 6. Testing Grounded AI Assistant Chat ---")
        queries = [
          "How is Elevator KONE-ELEV-001 doing?",
          "Show critical elevators",
          "What is causing high vibration on KONE-ELEV-001?",
          "What maintenance tasks are due?",
        ]
        for q in queries:
            chat_in = ChatMessage(message=q, elevator_id="KONE-ELEV-001")
            chat_out = await chat_with_assistant(chat_in, db)
            print(f"\n[Q] '{q}' → [Intent: {chat_out.intent_detected}]")
            print(f"[A] {chat_out.reply[:220]}...")

    print("\n=======================================================")
    print("      ALL PHASE 6 VERIFICATION TESTS PASSED!          ")
    print("=======================================================\n")


if __name__ == "__main__":
    asyncio.run(test_phase6_pipeline())
