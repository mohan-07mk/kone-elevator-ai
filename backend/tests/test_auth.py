"""Tests for authentication — login, tokens, refresh, current user, permissions."""

import pytest
from tests.conftest import auth_header


pytestmark = pytest.mark.asyncio


# ── Login ───────────────────────────────────────────────────

async def test_login_success(client):
    """Valid credentials return access + refresh tokens."""
    resp = await client.post("/api/auth/login", data={
        "username": "mohan@elevatorai.io",
        "password": "change-this-password",
    })
    assert resp.status_code == 200
    data = resp.json()
    assert "access_token" in data
    assert "refresh_token" in data
    assert data["token_type"] == "bearer"


async def test_login_json(client):
    """JSON login endpoint works."""
    resp = await client.post("/api/auth/login/json", json={
        "email": "mohan@elevatorai.io",
        "password": "change-this-password",
    })
    assert resp.status_code == 200
    assert "access_token" in resp.json()


async def test_login_wrong_password(client):
    """Wrong password returns 401."""
    resp = await client.post("/api/auth/login", data={
        "username": "mohan@elevatorai.io",
        "password": "wrongpassword",
    })
    assert resp.status_code == 401


async def test_login_unknown_email(client):
    """Non-existent email returns 401."""
    resp = await client.post("/api/auth/login", data={
        "username": "nobody@test.io",
        "password": "whatever",
    })
    assert resp.status_code == 401


# ── Token validation ────────────────────────────────────────

async def test_me_with_valid_token(client, admin_token):
    """GET /api/auth/me with valid token returns user info."""
    resp = await client.get("/api/auth/me", headers=auth_header(admin_token))
    assert resp.status_code == 200
    data = resp.json()
    assert data["email"] == "mohan@elevatorai.io"
    assert data["role"]["name"] == "Admin"


async def test_me_without_token(client):
    """GET /api/auth/me without token returns 401."""
    resp = await client.get("/api/auth/me")
    assert resp.status_code == 401


async def test_me_with_invalid_token(client):
    """GET /api/auth/me with garbage token returns 401."""
    resp = await client.get("/api/auth/me", headers=auth_header("not-a-valid-token"))
    assert resp.status_code == 401


# ── Refresh ─────────────────────────────────────────────────

async def test_refresh_token(client):
    """Using a refresh token returns new access + refresh tokens."""
    login = await client.post("/api/auth/login", data={
        "username": "mohan@elevatorai.io",
        "password": "change-this-password",
    })
    refresh = login.json()["refresh_token"]

    resp = await client.post("/api/auth/refresh", json={"refresh_token": refresh})
    assert resp.status_code == 200
    data = resp.json()
    assert "access_token" in data
    assert "refresh_token" in data


async def test_refresh_with_access_token_fails(client, admin_token):
    """Using an access token for refresh should fail."""
    resp = await client.post("/api/auth/refresh", json={"refresh_token": admin_token})
    assert resp.status_code == 401


# ── Permissions ─────────────────────────────────────────────

async def test_technician_cannot_create_user(client, tech_token):
    """Technicians should not be able to create users (Admin-only)."""
    resp = await client.post("/api/users", json={
        "email": "newuser@test.io",
        "name": "New User",
        "password": "testpass123",
        "role_id": 4,
    }, headers=auth_header(tech_token))
    assert resp.status_code == 403


async def test_technician_cannot_create_building(client, tech_token):
    """Technicians should not be able to create buildings (Admin-only)."""
    resp = await client.post("/api/buildings", json={
        "id": "BLD-Z",
        "name": "Test Building",
        "location": "Nowhere",
    }, headers=auth_header(tech_token))
    assert resp.status_code == 403
