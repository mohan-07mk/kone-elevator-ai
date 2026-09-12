"""Maintenance API — Tasks management, assignment, completion, history, and AI recommendations."""

from __future__ import annotations

import datetime as dt
import uuid
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel, ConfigDict, Field
from sqlalchemy import select, desc
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.session import get_db
from app.models.models import MaintenanceTask, Elevator, Technician, Building

router = APIRouter(prefix="/api/maintenance", tags=["Maintenance"])


# ── Pydantic Schemas ─────────────────────────────────────────

class TaskCreate(BaseModel):
    elevator_id: str
    building_id: Optional[str] = None
    title: str
    fault_type: str = "Preventive Inspection"
    priority: str = Field("Medium", pattern="^(Low|Medium|High|Critical)$")
    due_days: int = 3
    technician_id: Optional[int] = None
    notes: Optional[str] = None


class TaskAssign(BaseModel):
    technician_id: int


class TaskResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    elevator_id: str
    building_id: Optional[str]
    title: str
    fault_type: str
    priority: str
    due_date: dt.datetime
    status: str
    technician_id: Optional[int]
    technician_name: Optional[str]
    notes: Optional[str]
    ai_recommendation: Optional[dict]
    scheduled_at: Optional[dt.datetime]
    completed_at: Optional[dt.datetime]
    created_at: dt.datetime


# ── Endpoints ────────────────────────────────────────────────

@router.get("/tasks", response_model=list[TaskResponse])
async def list_maintenance_tasks(
    status_filter: Optional[str] = Query(None, alias="status"),
    elevator_id: Optional[str] = None,
    building_id: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
):
    """Retrieve all maintenance tasks with optional status and location filters."""
    stmt = select(MaintenanceTask).order_by(desc(MaintenanceTask.created_at))

    if status_filter and status_filter != "All":
        stmt = stmt.where(MaintenanceTask.status == status_filter)
    if elevator_id and elevator_id != "ALL":
        stmt = stmt.where(MaintenanceTask.elevator_id == elevator_id)
    if building_id and building_id != "ALL":
        stmt = stmt.where(MaintenanceTask.building_id == building_id)

    res = await db.execute(stmt)
    return res.scalars().all()


@router.post("/tasks", response_model=TaskResponse, status_code=status.HTTP_201_CREATED)
async def create_maintenance_task(
    payload: TaskCreate,
    db: AsyncSession = Depends(get_db),
):
    """Create a new maintenance task with automated AI technician recommendation."""
    # Verify elevator exists
    e_res = await db.execute(select(Elevator).where(Elevator.id == payload.elevator_id))
    elevator = e_res.scalar_one_or_none()
    if not elevator:
        raise HTTPException(status_code=404, detail=f"Elevator {payload.elevator_id} not found")

    building_id = payload.building_id or elevator.building_id
    due_date = dt.datetime.now(dt.timezone.utc) + dt.timedelta(days=payload.due_days)
    task_id = f"TASK-{uuid.uuid4().hex[:6].upper()}"

    # AI Recommendation Logic
    tech_res = await db.execute(select(Technician).where(Technician.availability == "Available"))
    available_techs = tech_res.scalars().all()

    rec_dict = None
    assigned_tech_id = payload.technician_id
    assigned_tech_name = None

    if available_techs:
        # Match specialization to fault type
        matched = None
        for t in available_techs:
            if payload.fault_type.lower() in t.specialization.lower():
                matched = t
                break
        if not matched:
            matched = min(available_techs, key=lambda t: t.active_workload)

        rec_dict = {
            "recommended_tech_id": matched.id,
            "recommended_tech": matched.name,
            "match_reason": f"Skill match on '{matched.specialization}' & workload balance ({matched.active_workload} active tasks).",
        }
        if not assigned_tech_id:
            assigned_tech_id = matched.id
            assigned_tech_name = matched.name

    if assigned_tech_id and not assigned_tech_name:
        t_obj = await db.get(Technician, assigned_tech_id)
        if t_obj:
            assigned_tech_name = t_obj.name

    task = MaintenanceTask(
        id=task_id,
        elevator_id=payload.elevator_id,
        building_id=building_id,
        title=payload.title,
        fault_type=payload.fault_type,
        priority=payload.priority,
        due_date=due_date,
        status="Scheduled",
        technician_id=assigned_tech_id,
        technician_name=assigned_tech_name,
        ai_recommendation=rec_dict,
        notes=payload.notes,
        scheduled_at=dt.datetime.now(dt.timezone.utc),
    )
    db.add(task)
    await db.commit()
    await db.refresh(task)
    return task


@router.post("/tasks/{task_id}/assign", response_model=TaskResponse)
async def assign_technician(
    task_id: str,
    payload: TaskAssign,
    db: AsyncSession = Depends(get_db),
):
    """Assign or reassign a technician to a maintenance task."""
    task = await db.get(MaintenanceTask, task_id)
    if not task:
        raise HTTPException(status_code=404, detail=f"Task {task_id} not found")

    tech = await db.get(Technician, payload.technician_id)
    if not tech:
        raise HTTPException(status_code=404, detail=f"Technician {payload.technician_id} not found")

    task.technician_id = tech.id
    task.technician_name = tech.name
    task.status = "In Progress" if task.status == "Scheduled" else task.status
    tech.active_workload += 1

    await db.commit()
    await db.refresh(task)
    return task


@router.post("/tasks/{task_id}/complete", response_model=TaskResponse)
async def complete_maintenance_task(
    task_id: str,
    db: AsyncSession = Depends(get_db),
):
    """Mark a maintenance task as Completed."""
    task = await db.get(MaintenanceTask, task_id)
    if not task:
        raise HTTPException(status_code=404, detail=f"Task {task_id} not found")

    task.status = "Completed"
    task.completed_at = dt.datetime.now(dt.timezone.utc)

    if task.technician_id:
        tech = await db.get(Technician, task.technician_id)
        if tech:
            tech.active_workload = max(0, tech.active_workload - 1)
            tech.completed_count += 1

    await db.commit()
    await db.refresh(task)
    return task


@router.get("/history/{elevator_id}", response_model=list[TaskResponse])
async def get_elevator_maintenance_history(
    elevator_id: str,
    db: AsyncSession = Depends(get_db),
):
    """Retrieve full maintenance task history for a specific elevator."""
    stmt = (
        select(MaintenanceTask)
        .where(MaintenanceTask.elevator_id == elevator_id)
        .order_by(desc(MaintenanceTask.created_at))
    )
    res = await db.execute(stmt)
    return res.scalars().all()
