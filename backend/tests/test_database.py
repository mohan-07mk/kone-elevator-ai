"""Tests for database connection and seed data integrity."""

import pytest
from sqlalchemy import select, text

from app.models.models import Role, User, Building, Elevator, SensorDefinition


pytestmark = pytest.mark.asyncio


async def test_db_connection(db_session):
    """Verify the database is reachable."""
    result = await db_session.execute(text("SELECT 1"))
    assert result.scalar() == 1


async def test_roles_seeded(db_session):
    """All 4 roles must exist."""
    result = await db_session.execute(select(Role).order_by(Role.id))
    roles = result.scalars().all()
    names = {r.name for r in roles}
    assert names == {"Admin", "Maintenance Engineer", "Manager", "Technician"}


async def test_users_seeded(db_session):
    """At least the admin and core users exist."""
    result = await db_session.execute(select(User))
    users = result.scalars().all()
    assert len(users) >= 7
    emails = {u.email for u in users}
    assert "mohan@elevatorai.io" in emails
    assert "karthik@elevatorai.io" in emails


async def test_buildings_seeded(db_session):
    """3 buildings seeded."""
    result = await db_session.execute(select(Building))
    buildings = result.scalars().all()
    assert len(buildings) == 3
    ids = {b.id for b in buildings}
    assert ids == {"BLD-A", "BLD-B", "BLD-C"}


async def test_elevators_seeded(db_session):
    """10 elevators seeded with correct building assignments."""
    result = await db_session.execute(select(Elevator).order_by(Elevator.id))
    elevators = result.scalars().all()
    assert len(elevators) == 10
    # BLD-A has 4 elevators
    bld_a = [e for e in elevators if e.building_id == "BLD-A"]
    assert len(bld_a) == 4
    # KONE-ELEV-001 is critical
    e001 = next(e for e in elevators if e.id == "KONE-ELEV-001")
    assert e001.status == "critical"
    assert e001.health_score == 42
    assert e001.active_fault == "Bearing Degradation"


async def test_sensor_definitions_seeded(db_session):
    """10 sensor definitions seeded."""
    result = await db_session.execute(select(SensorDefinition))
    defs = result.scalars().all()
    assert len(defs) == 10
    keys = {d.sensor_key for d in defs}
    assert "vibration" in keys
    assert "motor_temp" in keys or "motorTemp" in keys
