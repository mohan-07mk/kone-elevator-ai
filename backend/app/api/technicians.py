"""Technician Management API — profiles, availability, workload, and AI recommendation logic."""

from __future__ import annotations

from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel, ConfigDict
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.session import get_db
from app.models.models import Technician, MaintenanceTask

router = APIRouter(prefix="/api/technicians", tags=["Technicians"])


# ── Pydantic Schemas ─────────────────────────────────────────

class TechResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    user_id: Optional[int]
    name: str
    email: str
    phone: Optional[str]
    role_title: str
    specialization: str
    availability: str
    active_workload: int
    completed_count: int
    rating: float


class TechRecommendRequest(BaseModel):
    elevator_id: str
    fault_type: str


class TechRecommendResponse(BaseModel):
    recommended_technician: TechResponse
    match_score: float
    explanation: str
    reasoning_factors: list[str]


# ── Endpoints ────────────────────────────────────────────────

@router.get("", response_model=list[TechResponse])
async def list_technicians(
    availability: Optional[str] = None,
    specialization: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
):
    """Retrieve technician directory with workload and availability."""
    stmt = select(Technician)
    if availability and availability != "All":
        stmt = stmt.where(Technician.availability == availability)
    if specialization:
        stmt = stmt.where(Technician.specialization.contains(specialization))

    res = await db.execute(stmt)
    techs = res.scalars().all()
    return techs


@router.get("/{tech_id}", response_model=TechResponse)
async def get_technician(
    tech_id: int,
    db: AsyncSession = Depends(get_db),
):
    """Get profile details for a specific technician."""
    tech = await db.get(Technician, tech_id)
    if not tech:
        raise HTTPException(status_code=404, detail=f"Technician {tech_id} not found")
    return tech


@router.post("/recommend", response_model=TechRecommendResponse)
async def recommend_technician(
    payload: TechRecommendRequest,
    db: AsyncSession = Depends(get_db),
):
    """AI Recommendation Logic:

    Selects best technician based on:
    - Fault Component / Skill Match
    - Availability ("Available" vs "On Job")
    - Workload (lowest active tasks)
    - Historical Performance / Rating
    """
    res = await db.execute(select(Technician))
    all_techs = res.scalars().all()
    if not all_techs:
        raise HTTPException(status_code=404, detail="No technicians available in system")

    fault_lower = payload.fault_type.lower()

    best_tech = None
    best_score = -1.0
    best_factors = []

    for tech in all_techs:
        score = 0.0
        factors = []

        # 1. Skill match (+40 pts)
        if any(term in tech.specialization.lower() for term in fault_lower.split()):
            score += 40.0
            factors.append(f"Specialization '{tech.specialization}' directly matches fault '{payload.fault_type}'")
        else:
            score += 15.0
            factors.append("General electrical & mechanical diagnostic capability")

        # 2. Availability (+30 pts)
        if tech.availability == "Available":
            score += 30.0
            factors.append("Currently available for immediate dispatch")
        elif tech.availability == "On Job":
            score += 10.0
            factors.append("Currently on active assignment")

        # 3. Workload (+20 pts max)
        workload_score = max(0, 20 - (tech.active_workload * 5))
        score += workload_score
        factors.append(f"Low active workload ({tech.active_workload} active tasks)")

        # 4. Rating (+10 pts)
        score += (tech.rating / 5.0) * 10.0

        if score > best_score:
            best_score = score
            best_tech = tech
            best_factors = factors

    explanation = (
        f"Selected {best_tech.name} as the primary technician with a {best_score:.0f}% match score. "
        f"{' '.join(best_factors[:2])}."
    )

    return TechRecommendResponse(
        recommended_technician=TechResponse.model_validate(best_tech),
        match_score=best_score,
        explanation=explanation,
        reasoning_factors=best_factors,
    )
