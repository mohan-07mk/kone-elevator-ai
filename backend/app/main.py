"""Elevator AI — FastAPI application entry point."""

from __future__ import annotations

import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI, Response
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import get_settings
from app.database.session import Base, engine, async_session_factory
from app.database.seed import seed_all

# ── Import routers ──────────────────────────────────────────
from app.api.auth import router as auth_router
from app.api.users import router as users_router
from app.api.buildings import router as buildings_router
from app.api.elevators import router as elevators_router
from app.api.system import router as system_router
from app.api.telemetry import router as telemetry_router
from app.api.simulator import router as simulator_router
from app.api.ws import router as ws_router
from app.api.ai import router as ai_router
from app.api.predictive import router as predictive_router
from app.api.health import router as health_router
from app.api.alerts import router as alerts_router
from app.api.maintenance import router as maintenance_router
from app.api.technicians import router as technicians_router
from app.api.analytics import router as analytics_router
from app.api.timeline import router as timeline_router
from app.api.reports import router as reports_router
from app.api.assistant import router as assistant_router
from app.api.devices import router as devices_router

settings = get_settings()
logging.basicConfig(level=logging.INFO if not settings.debug else logging.DEBUG)
logger = logging.getLogger("elevator_ai")


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup: create tables + seed + preload dataset; Shutdown: dispose engine."""
    logger.info("Starting Elevator AI backend v%s", settings.app_version)

    # Database tables are managed via Alembic migrations in production.
    # For local dev / SQLite fallback, ensure tables exist if debug is True.
    try:
        if settings.debug or "sqlite" in settings.normalized_database_url:
            async with engine.begin() as conn:
                await conn.run_sync(Base.metadata.create_all)
            logger.info("Local database tables ensured via create_all")

        # Run seed
        async with async_session_factory() as session:
            counts = await seed_all(session)
            if any(v > 0 for v in counts.values()):
                logger.info("Seed data created: %s", counts)
            else:
                logger.info("Seed data already present — no changes")
    except Exception as db_err:
        logger.warning("Database startup notice (non-fatal, simulator active): %s", db_err)

    # Preload dataset for simulator & register default gateway
    try:
        from app.simulator.engine import get_simulator
        from app.devices.edge_buffer import get_edge_manager
        sim = get_simulator()
        await sim.load_dataset()
        edge_mgr = get_edge_manager()
        edge_mgr.register_device("SIM-GATEWAY-001", "simulator", "BLD-A", "KONE-ELEV-001")
        logger.info("Simulator dataset preloaded & SIM-GATEWAY-001 registered")
    except Exception as exc:
        logger.warning("Simulator dataset preload failed (non-fatal): %s", exc)

    yield

    # Shutdown — stop simulator if running
    try:
        from app.simulator.engine import get_simulator
        sim = get_simulator()
        await sim.reset()
    except Exception:
        pass

    await engine.dispose()
    logger.info("Elevator AI backend stopped")


app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description="Predictive Maintenance Intelligence Platform — FastAPI Backend",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
)

# ── CORS ────────────────────────────────────────────────────
allow_origins = [
    "https://eloquent-eclair-c69e60.netlify.app",
    "https://elevator-ai.netlify.app",
    "http://localhost:3000",
    "http://localhost:5173",
    "http://localhost:8000",
    "http://127.0.0.1:3000",
    "http://127.0.0.1:5173",
    "http://127.0.0.1:8000",
]

# Merge extra non-wildcard origins from settings/env if present
for item in settings.cors_origin_list:
    cleaned = item.strip().strip('"\'').rstrip("/")
    if cleaned and cleaned != "*" and cleaned not in allow_origins:
        allow_origins.append(cleaned)

app.add_middleware(
    CORSMiddleware,
    allow_origins=allow_origins,
    allow_origin_regex=r"https://.*\.netlify\.app",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"],
    max_age=600,
)

# ── Register routers ───────────────────────────────────────
app.include_router(auth_router)
app.include_router(users_router)
app.include_router(buildings_router)
app.include_router(elevators_router)
app.include_router(system_router)
app.include_router(telemetry_router)
app.include_router(simulator_router)
app.include_router(ws_router)
app.include_router(ai_router)
app.include_router(predictive_router)
app.include_router(health_router)
app.include_router(alerts_router)
app.include_router(maintenance_router)
app.include_router(technicians_router)
app.include_router(analytics_router)
app.include_router(timeline_router)
app.include_router(reports_router)
app.include_router(assistant_router)
app.include_router(devices_router)


@app.get("/", include_in_schema=False)
async def root():
    return {
        "app": settings.app_name,
        "version": settings.app_version,
        "docs": "/docs",
        "health": "/health",
    }
