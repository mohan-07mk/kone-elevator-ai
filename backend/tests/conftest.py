"""Shared test fixtures — async client, seeded database, auth helpers."""

from __future__ import annotations

import os
from typing import AsyncGenerator

import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient

# ── Force test DB URL ──────────────────────────────────────
TEST_DB_FILE = "test_elevator_ai.db"
os.environ["DATABASE_URL"] = f"sqlite+aiosqlite:///{TEST_DB_FILE}"
os.environ["DATABASE_URL_SYNC"] = f"sqlite:///{TEST_DB_FILE}"
os.environ["JWT_SECRET_KEY"] = "test-secret-key-for-testing-only-change-in-prod"

from app.core.config import get_settings
get_settings.cache_clear()  # Clear LRU cache so new env vars take effect

from app.main import app  # noqa: E402
from app.database.session import Base, engine, async_session_factory  # noqa: E402
from app.database.seed import seed_all  # noqa: E402


@pytest_asyncio.fixture(scope="function")
async def setup_database():
    """Create tables + seed for test run."""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)

    async with async_session_factory() as session:
        await seed_all(session)

    yield

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest_asyncio.fixture(scope="function")
async def db_session(setup_database) -> AsyncGenerator:
    """Provide a transactional DB session per test."""
    async with async_session_factory() as session:
        yield session


@pytest_asyncio.fixture(scope="function")
async def client(setup_database) -> AsyncGenerator[AsyncClient, None]:
    """HTTPX async client wired to the FastAPI app."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac


@pytest_asyncio.fixture(scope="function")
async def admin_token(client: AsyncClient) -> str:
    """Login as admin and return access token."""
    resp = await client.post(
        "/api/auth/login",
        data={"username": "mohan@elevatorai.io", "password": "change-this-password"},
    )
    assert resp.status_code == 200, f"Admin login failed: {resp.text}"
    return resp.json()["access_token"]


@pytest_asyncio.fixture(scope="function")
async def tech_token(client: AsyncClient) -> str:
    """Login as technician and return access token."""
    resp = await client.post(
        "/api/auth/login",
        data={"username": "mohammed@elevatorai.io", "password": "mohammed2026!"},
    )
    assert resp.status_code == 200, f"Technician login failed: {resp.text}"
    return resp.json()["access_token"]


def auth_header(token: str) -> dict:
    return {"Authorization": f"Bearer {token}"}
