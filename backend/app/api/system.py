"""System health and status endpoints — no auth required for health/ready."""

from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import func, select, text
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import get_settings
from app.database.session import get_db
from app.models.models import Building, Elevator, User
from app.schemas.schemas import HealthCheck, SystemStatus
from app.security.dependencies import get_current_user

router = APIRouter(tags=["System"])
settings = get_settings()


@router.get("/health", response_model=HealthCheck)
async def health():
    """Basic liveness check — does not check DB."""
    return HealthCheck(status="ok")


@router.get("/ready", response_model=HealthCheck)
async def ready(db: Annotated[AsyncSession, Depends(get_db)]):
    """Readiness check — verifies the database connection."""
    try:
        await db.execute(text("SELECT 1"))
        return HealthCheck(status="ok")
    except Exception as exc:
        raise HTTPException(status_code=503, detail=f"Database connection error: {exc}")


@router.get("/api/system/status", response_model=SystemStatus)
async def system_status(
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
):
    """Full system status including entity counts (authenticated)."""
    buildings = (await db.execute(select(func.count(Building.id)))).scalar() or 0
    elevators = (await db.execute(select(func.count(Elevator.id)))).scalar() or 0
    users = (await db.execute(select(func.count(User.id)))).scalar() or 0

    db_ok = True
    try:
        await db.execute(text("SELECT 1"))
    except Exception:
        db_ok = False

    return SystemStatus(
        status="operational",
        version=settings.app_version,
        database="connected" if db_ok else "disconnected",
        total_buildings=buildings,
        total_elevators=elevators,
        total_users=users,
    )
