"""Tests for Buildings + Elevators APIs."""

import pytest
from tests.conftest import auth_header


pytestmark = pytest.mark.asyncio


# ── Buildings ───────────────────────────────────────────────

async def test_list_buildings(client, admin_token):
    """List buildings returns the 3 seeded buildings."""
    resp = await client.get("/api/buildings", headers=auth_header(admin_token))
    assert resp.status_code == 200
    data = resp.json()
    assert len(data) == 3
    names = {b["name"] for b in data}
    assert "Skyline Tower A" in names


async def test_get_building_detail(client, admin_token):
    """Get specific building includes elevators list."""
    resp = await client.get("/api/buildings/BLD-A", headers=auth_header(admin_token))
    assert resp.status_code == 200
    data = resp.json()
    assert data["id"] == "BLD-A"
    assert data["name"] == "Skyline Tower A"
    assert data["elevator_count"] == 4
    assert len(data["elevators"]) == 4


async def test_get_building_not_found(client, admin_token):
    """Non-existent building returns 404."""
    resp = await client.get("/api/buildings/NONEXISTENT", headers=auth_header(admin_token))
    assert resp.status_code == 404


async def test_create_building(client, admin_token):
    """Admin can create a building."""
    resp = await client.post("/api/buildings", json={
        "id": "BLD-TEST",
        "name": "Test Tower",
        "location": "Test City",
    }, headers=auth_header(admin_token))
    assert resp.status_code == 201
    data = resp.json()
    assert data["id"] == "BLD-TEST"
    assert data["name"] == "Test Tower"
    assert data["elevator_count"] == 0

    # Cleanup
    await client.delete("/api/buildings/BLD-TEST", headers=auth_header(admin_token))


async def test_create_building_duplicate(client, admin_token):
    """Duplicate building ID returns 409."""
    resp = await client.post("/api/buildings", json={
        "id": "BLD-A",
        "name": "Duplicate",
    }, headers=auth_header(admin_token))
    assert resp.status_code == 409


async def test_update_building(client, admin_token):
    """Admin can update building name."""
    # Create temp building
    await client.post("/api/buildings", json={
        "id": "BLD-UPD",
        "name": "Before",
        "location": "Loc",
    }, headers=auth_header(admin_token))

    resp = await client.patch("/api/buildings/BLD-UPD", json={
        "name": "After Update",
    }, headers=auth_header(admin_token))
    assert resp.status_code == 200
    assert resp.json()["name"] == "After Update"

    # Cleanup
    await client.delete("/api/buildings/BLD-UPD", headers=auth_header(admin_token))


# ── Elevators ───────────────────────────────────────────────

async def test_list_elevators(client, admin_token):
    """List all elevators returns 10 seeded elevators."""
    resp = await client.get("/api/elevators", headers=auth_header(admin_token))
    assert resp.status_code == 200
    data = resp.json()
    assert len(data) >= 10


async def test_list_elevators_by_building(client, admin_token):
    """Filter elevators by building_id."""
    resp = await client.get("/api/elevators?building_id=BLD-B", headers=auth_header(admin_token))
    assert resp.status_code == 200
    data = resp.json()
    assert all(e["building_id"] == "BLD-B" for e in data)
    assert len(data) == 3


async def test_list_elevators_by_status(client, admin_token):
    """Filter elevators by status."""
    resp = await client.get("/api/elevators?status=critical", headers=auth_header(admin_token))
    assert resp.status_code == 200
    data = resp.json()
    assert all(e["status"] == "critical" for e in data)
    assert len(data) == 2


async def test_fleet_summary(client, admin_token):
    """Fleet summary returns correct counts."""
    resp = await client.get("/api/elevators/summary", headers=auth_header(admin_token))
    assert resp.status_code == 200
    data = resp.json()
    assert data["total"] >= 10
    assert "healthy" in data
    assert "warning" in data
    assert "critical" in data
    assert "avg_health" in data


async def test_get_elevator(client, admin_token):
    """Get specific elevator by ID."""
    resp = await client.get("/api/elevators/KONE-ELEV-001", headers=auth_header(admin_token))
    assert resp.status_code == 200
    data = resp.json()
    assert data["id"] == "KONE-ELEV-001"
    assert data["status"] == "critical"
    assert data["health_score"] == 42
    assert data["active_fault"] == "Bearing Degradation"
    assert data["building_name"] == "Skyline Tower A"


async def test_get_elevator_not_found(client, admin_token):
    """Non-existent elevator returns 404."""
    resp = await client.get("/api/elevators/NONEXISTENT", headers=auth_header(admin_token))
    assert resp.status_code == 404


async def test_update_elevator(client, admin_token):
    """Admin can update elevator status."""
    resp = await client.patch("/api/elevators/KONE-ELEV-004", json={
        "current_floor": 5,
        "direction": "up",
    }, headers=auth_header(admin_token))
    assert resp.status_code == 200
    data = resp.json()
    assert data["current_floor"] == 5
    assert data["direction"] == "up"

    # Restore
    await client.patch("/api/elevators/KONE-ELEV-004", json={
        "current_floor": 1,
        "direction": "idle",
    }, headers=auth_header(admin_token))


# ── System / Health ─────────────────────────────────────────

async def test_health_endpoint(client):
    """Health check does not require auth."""
    resp = await client.get("/health")
    assert resp.status_code == 200
    assert resp.json()["status"] == "ok"


async def test_ready_endpoint(client):
    """Ready check verifies DB connection."""
    resp = await client.get("/ready")
    assert resp.status_code == 200
    assert resp.json()["status"] == "ok"


async def test_system_status(client, admin_token):
    """System status requires auth and returns entity counts."""
    resp = await client.get("/api/system/status", headers=auth_header(admin_token))
    assert resp.status_code == 200
    data = resp.json()
    assert data["status"] == "operational"
    assert data["total_buildings"] >= 3
    assert data["total_elevators"] >= 10
    assert data["total_users"] >= 7


async def test_system_status_unauthorized(client):
    """System status without auth returns 401."""
    resp = await client.get("/api/system/status")
    assert resp.status_code == 401
