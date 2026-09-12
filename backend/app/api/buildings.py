"""Buildings API — CRUD with elevator counts."""

from __future__ import annotations

import datetime as dt
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload, joinedload

from app.database.session import get_db
from app.models.models import Building, Elevator, User
from app.schemas.schemas import BuildingCreate, BuildingUpdate, BuildingOut, BuildingDetail, ElevatorOut
from app.security.dependencies import get_current_user, require_roles
from app.services.audit_service import log_action

router = APIRouter(prefix="/api/buildings", tags=["Buildings"])


def _building_to_out(b: Building) -> BuildingOut:
    elevators_list = b.__dict__.get("elevators", [])
    now = dt.datetime.now(dt.timezone.utc)
    return BuildingOut(
        id=b.id,
        name=b.name,
        location=b.location,
        elevator_count=len(elevators_list) if elevators_list else 0,
        created_at=b.created_at or now,
        updated_at=b.updated_at or now,
    )


def _elevator_to_out(e: Elevator) -> ElevatorOut:
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


@router.get("", response_model=list[BuildingOut])
async def list_buildings(
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
):
    """List all buildings with elevator counts."""
    result = await db.execute(
        select(Building).options(selectinload(Building.elevators)).order_by(Building.id)
    )
    buildings = result.scalars().all()
    return [_building_to_out(b) for b in buildings]


@router.get("/{building_id}", response_model=BuildingDetail)
async def get_building(
    building_id: str,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
):
    """Get a building with its elevators."""
    result = await db.execute(
        select(Building)
        .options(selectinload(Building.elevators).joinedload(Elevator.building))
        .where(Building.id == building_id)
    )
    b = result.scalar_one_or_none()
    if b is None:
        raise HTTPException(status_code=404, detail="Building not found")

    elevators_list = b.__dict__.get("elevators", [])
    return BuildingDetail(
        id=b.id,
        name=b.name,
        location=b.location,
        elevator_count=len(elevators_list),
        created_at=b.created_at or dt.datetime.now(dt.timezone.utc),
        updated_at=b.updated_at or dt.datetime.now(dt.timezone.utc),
        elevators=[_elevator_to_out(e) for e in elevators_list],
    )


@router.post("", response_model=BuildingOut, status_code=status.HTTP_201_CREATED)
async def create_building(
    body: BuildingCreate,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(require_roles("Admin"))],
):
    """Create a new building (Admin only)."""
    existing = await db.execute(select(Building).where(Building.id == body.id))
    if existing.scalar_one_or_none():
        raise HTTPException(status_code=409, detail="Building ID already exists")

    building = Building(id=body.id, name=body.name, location=body.location)
    building.elevators = []
    out = _building_to_out(building)
    db.add(building)
    await db.flush()

    await log_action(
        db, user_id=current_user.id, action="Building Created",
        resource_type="building", resource_id=building.id,
    )
    return out


@router.patch("/{building_id}", response_model=BuildingOut)
async def update_building(
    building_id: str,
    body: BuildingUpdate,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(require_roles("Admin"))],
):
    """Update building name/location (Admin only)."""
    result = await db.execute(
        select(Building).options(selectinload(Building.elevators)).where(Building.id == building_id)
    )
    b = result.scalar_one_or_none()
    if b is None:
        raise HTTPException(status_code=404, detail="Building not found")

    for field, value in body.model_dump(exclude_unset=True).items():
        setattr(b, field, value)

    out = _building_to_out(b)

    await db.flush()

    await log_action(
        db, user_id=current_user.id, action="Building Updated",
        resource_type="building", resource_id=b.id,
    )
    return out


@router.delete("/{building_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_building(
    building_id: str,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(require_roles("Admin"))],
):
    """Delete a building and its elevators (Admin only)."""
    result = await db.execute(select(Building).where(Building.id == building_id))
    b = result.scalar_one_or_none()
    if b is None:
        raise HTTPException(status_code=404, detail="Building not found")

    await log_action(
        db, user_id=current_user.id, action="Building Deleted",
        resource_type="building", resource_id=b.id,
    )

    await db.delete(b)
    await db.flush()
