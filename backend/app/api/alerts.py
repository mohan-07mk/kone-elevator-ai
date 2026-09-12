"""FastAPI Router for Alert Management and Lifecycle."""

from __future__ import annotations

import datetime as dt
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc

from app.database.session import get_db
from app.models.models import AlertRecord

router = APIRouter(prefix="/api/alerts", tags=["Alert Lifecycle"])


@router.get("")
async def list_alerts(
    elevator_id: Optional[str] = Query(None),
    status: Optional[str] = Query(None),
    level: Optional[str] = Query(None),
    limit: int = Query(50, ge=1, le=200),
    db: AsyncSession = Depends(get_db),
):
    """Retrieve system alerts with optional filtering."""
    query = select(AlertRecord).order_by(desc(AlertRecord.created_at)).limit(limit)

    if elevator_id:
        query = query.where(AlertRecord.elevator_id == elevator_id)
    if status:
        query = query.where(AlertRecord.status == status)
    if level:
        query = query.where(AlertRecord.level == level)

    res = await db.execute(query)
    alerts = res.scalars().all()

    return [
        {
            "id": a.id,
            "elevator_id": a.elevator_id,
            "title": a.title,
            "level": a.level,
            "source": a.source,
            "status": a.status,
            "details": a.details or {},
            "acknowledged_at": a.acknowledged_at.isoformat() if a.acknowledged_at else None,
            "resolved_at": a.resolved_at.isoformat() if a.resolved_at else None,
            "created_at": a.created_at.isoformat() if a.created_at else None,
        }
        for a in alerts
    ]


@router.post("/{alert_id}/acknowledge")
async def acknowledge_alert(alert_id: int, db: AsyncSession = Depends(get_db)):
    """Acknowledge an active alert."""
    stmt = select(AlertRecord).where(AlertRecord.id == alert_id)
    res = await db.execute(stmt)
    alert = res.scalars().first()

    if not alert:
        raise HTTPException(status_code=404, detail=f"Alert {alert_id} not found")

    alert.status = "acknowledged"
    alert.acknowledged_at = dt.datetime.now(dt.timezone.utc)
    await db.commit()

    return {"message": f"Alert {alert_id} acknowledged", "alert_id": alert_id, "status": "acknowledged"}


@router.post("/{alert_id}/resolve")
async def resolve_alert(alert_id: int, db: AsyncSession = Depends(get_db)):
    """Mark an alert as resolved."""
    stmt = select(AlertRecord).where(AlertRecord.id == alert_id)
    res = await db.execute(stmt)
    alert = res.scalars().first()

    if not alert:
        raise HTTPException(status_code=404, detail=f"Alert {alert_id} not found")

    alert.status = "resolved"
    alert.resolved_at = dt.datetime.now(dt.timezone.utc)
    await db.commit()

    return {"message": f"Alert {alert_id} resolved", "alert_id": alert_id, "status": "resolved"}
