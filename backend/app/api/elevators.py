"""Elevators API — CRUD operations."""

from __future__ import annotations

import datetime as dt
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from app.database.session import get_db
from app.models.models import Building, Elevator, User
from app.schemas.schemas import ElevatorCreate, ElevatorUpdate, ElevatorOut
from app.security.dependencies import get_current_user, require_roles
from app.services.audit_service import log_action

router = APIRouter(prefix="/api/elevators", tags=["Elevators"])


def _to_out(e: Elevator) -> ElevatorOut:
    b_name = ""
    if "building" in e.__dict__ and e.building:
        b_name = e.building.name
    now = dt.datetime.now(dt.timezone.utc)
    return ElevatorOut(
        id=e.id,
        building_id=e.building_id,
        building_name=b_name,
        current_floor=e.current_floor,
        direction=e.direction,
        status=e.status,
        health_score=e.health_score,
        active_fault=e.active_fault,
        risk_level=e.risk_level,
        speed=e.speed,
        load_percentage=e.load_percentage,
        door_status=e.door_status,
        connection_status=e.connection_status,
        last_telemetry_at=e.last_telemetry_at,
        created_at=e.created_at or now,
        updated_at=e.updated_at or now,
    )


@router.get("", response_model=list[ElevatorOut])
async def list_elevators(
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
    building_id: str | None = Query(None),
    status_filter: str | None = Query(None, alias="status"),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
):
    """List elevators with optional building and status filters."""
    q = select(Elevator).options(joinedload(Elevator.building)).order_by(Elevator.id).offset(skip).limit(limit)
    if building_id:
        q = q.where(Elevator.building_id == building_id)
    if status_filter:
        q = q.where(Elevator.status == status_filter)
    result = await db.execute(q)
    elevators = result.scalars().all()
    return [_to_out(e) for e in elevators]


@router.get("/summary")
async def fleet_summary(
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
):
    """Fleet summary — counts by status and average health."""
    result = await db.execute(select(Elevator))
    elevators = result.scalars().all()

    total = len(elevators)
    healthy = sum(1 for e in elevators if e.status == "healthy")
    warning = sum(1 for e in elevators if e.status == "warning")
    critical = sum(1 for e in elevators if e.status == "critical")
    avg_health = round(sum(e.health_score for e in elevators) / total, 1) if total > 0 else 0.0

    return {
        "total": total,
        "healthy": healthy,
        "warning": warning,
        "critical": critical,
        "avg_health": avg_health,
        "online": sum(1 for e in elevators if e.connection_status == "online"),
        "offline": sum(1 for e in elevators if e.connection_status != "online"),
    }


@router.get("/{elevator_id}", response_model=ElevatorOut)
async def get_elevator(
    elevator_id: str,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
):
    """Get a single elevator by ID."""
    result = await db.execute(
        select(Elevator).options(joinedload(Elevator.building)).where(Elevator.id == elevator_id)
    )
    e = result.scalar_one_or_none()
    if e is None:
        raise HTTPException(status_code=404, detail="Elevator not found")
    return _to_out(e)


@router.post("", response_model=ElevatorOut, status_code=status.HTTP_201_CREATED)
async def create_elevator(
    body: ElevatorCreate,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(require_roles("Admin"))],
):
    """Register a new elevator (Admin only)."""
    # Validate building
    bld_res = await db.execute(select(Building).where(Building.id == body.building_id))
    bld = bld_res.scalar_one_or_none()
    if bld is None:
        raise HTTPException(status_code=400, detail="Building not found")

    # Check duplicate
    existing = await db.execute(select(Elevator).where(Elevator.id == body.id))
    if existing.scalar_one_or_none():
        raise HTTPException(status_code=409, detail="Elevator ID already exists")

    elevator = Elevator(
        id=body.id,
        building_id=body.building_id,
        current_floor=body.current_floor,
        status=body.status,
        health_score=body.health_score,
        risk_level=body.risk_level,
    )
    elevator.building = bld
    out = _to_out(elevator)
    db.add(elevator)
    await db.flush()

    await log_action(
        db, user_id=current_user.id, action="Elevator Created",
        resource_type="elevator", resource_id=elevator.id,
    )
    return out


@router.patch("/{elevator_id}", response_model=ElevatorOut)
async def update_elevator(
    elevator_id: str,
    body: ElevatorUpdate,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(require_roles("Admin", "Maintenance Engineer"))],
):
    """Update elevator state (Admin or Maintenance Engineer)."""
    result = await db.execute(
        select(Elevator).options(joinedload(Elevator.building)).where(Elevator.id == elevator_id)
    )
    e = result.scalar_one_or_none()
    if e is None:
        raise HTTPException(status_code=404, detail="Elevator not found")

    update_data = body.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(e, field, value)

    out = _to_out(e)

    await db.flush()

    await log_action(
        db, user_id=current_user.id, action="Elevator Updated",
        resource_type="elevator", resource_id=e.id, details=update_data,
    )
    return out


@router.delete("/{elevator_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_elevator(
    elevator_id: str,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(require_roles("Admin"))],
):
    """Delete an elevator (Admin only)."""
    result = await db.execute(select(Elevator).where(Elevator.id == elevator_id))
    e = result.scalar_one_or_none()
    if e is None:
        raise HTTPException(status_code=404, detail="Elevator not found")

    await log_action(
        db, user_id=current_user.id, action="Elevator Deleted",
        resource_type="elevator", resource_id=e.id,
    )

    await db.delete(e)
    await db.flush()
