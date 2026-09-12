"""Seed script — populates roles, users, buildings, elevators, sensor_defs, thresholds."""

from __future__ import annotations

import logging
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.models import (
    Role, User, Building, Elevator, SensorDefinition,
    ThresholdConfig, Technician, SystemSetting,
)
from app.security.auth import hash_password
from app.core.config import get_settings

logger = logging.getLogger("elevator_ai.seed")
settings = get_settings()


# ── Role definitions ────────────────────────────────────────
ROLES = [
    {"name": "Admin", "description": "Full system access", "permissions": {"all": True}},
    {"name": "Maintenance Engineer", "description": "Fault analysis, maintenance, monitoring", "permissions": {"monitoring": True, "faults": True, "maintenance": True, "reports": True}},
    {"name": "Manager", "description": "Analytics, reports, fleet overview", "permissions": {"analytics": True, "reports": True, "monitoring": True}},
    {"name": "Technician", "description": "Task execution, basic monitoring", "permissions": {"monitoring": True, "tasks": True}},
]

# ── Building data (matches frontend) ───────────────────────
BUILDINGS = [
    {"id": "BLD-A", "name": "Skyline Tower A", "location": "Nungambakkam, Chennai"},
    {"id": "BLD-B", "name": "Horizon Business Park", "location": "Whitefield, Bengaluru"},
    {"id": "BLD-C", "name": "Marina Corporate Centre", "location": "OMR, Chennai"},
]

# ── Elevator fleet (matches frontend ELEVATORS const) ──────
ELEVATORS = [
    {"id": "KONE-ELEV-001", "building_id": "BLD-A", "current_floor": 8, "direction": "up", "status": "critical", "health_score": 42, "active_fault": "Bearing Degradation", "risk_level": "High", "speed": 1.6, "load_percentage": 62, "door_status": "closed", "connection_status": "online"},
    {"id": "KONE-ELEV-002", "building_id": "BLD-A", "current_floor": 3, "direction": "down", "status": "warning", "health_score": 74, "active_fault": "Door Alignment Drift", "risk_level": "Medium", "speed": 1.1, "load_percentage": 40, "door_status": "open", "connection_status": "online"},
    {"id": "KONE-ELEV-003", "building_id": "BLD-A", "current_floor": 12, "direction": "idle", "status": "healthy", "health_score": 89, "active_fault": None, "risk_level": "Low", "speed": 0, "load_percentage": 18, "door_status": "closed", "connection_status": "online"},
    {"id": "KONE-ELEV-004", "building_id": "BLD-A", "current_floor": 1, "direction": "idle", "status": "healthy", "health_score": 92, "active_fault": None, "risk_level": "Low", "speed": 0, "load_percentage": 5, "door_status": "open", "connection_status": "online"},
    {"id": "KONE-ELEV-005", "building_id": "BLD-B", "current_floor": 6, "direction": "up", "status": "warning", "health_score": 68, "active_fault": "Motor Temp Above Range", "risk_level": "Medium", "speed": 1.4, "load_percentage": 71, "door_status": "closed", "connection_status": "online"},
    {"id": "KONE-ELEV-006", "building_id": "BLD-B", "current_floor": 2, "direction": "idle", "status": "healthy", "health_score": 95, "active_fault": None, "risk_level": "Low", "speed": 0, "load_percentage": 12, "door_status": "closed", "connection_status": "online"},
    {"id": "KONE-ELEV-007", "building_id": "BLD-B", "current_floor": 15, "direction": "down", "status": "critical", "health_score": 38, "active_fault": "Motor Overheating", "risk_level": "High", "speed": 0.9, "load_percentage": 84, "door_status": "closed", "connection_status": "online"},
    {"id": "KONE-ELEV-008", "building_id": "BLD-C", "current_floor": 4, "direction": "idle", "status": "healthy", "health_score": 90, "active_fault": None, "risk_level": "Low", "speed": 0, "load_percentage": 22, "door_status": "open", "connection_status": "online"},
    {"id": "KONE-ELEV-009", "building_id": "BLD-C", "current_floor": 9, "direction": "up", "status": "healthy", "health_score": 87, "active_fault": None, "risk_level": "Low", "speed": 1.5, "load_percentage": 55, "door_status": "closed", "connection_status": "online"},
    {"id": "KONE-ELEV-010", "building_id": "BLD-C", "current_floor": 7, "direction": "down", "status": "warning", "health_score": 71, "active_fault": "Vibration Trending Up", "risk_level": "Medium", "speed": 1.2, "load_percentage": 48, "door_status": "closed", "connection_status": "online"},
]

# ── Sensor definitions (matches telemetry contract) ────────
SENSOR_DEFS = [
    {"sensor_key": "motor_temp", "label": "Motor Temperature", "unit": "°C", "normal_min": 40, "normal_max": 65},
    {"sensor_key": "voltage", "label": "Voltage", "unit": "V", "normal_min": 380, "normal_max": 420},
    {"sensor_key": "current", "label": "Current", "unit": "A", "normal_min": 10, "normal_max": 18},
    {"sensor_key": "power", "label": "Power Consumption", "unit": "kW", "normal_min": 4, "normal_max": 8},
    {"sensor_key": "rpm", "label": "Motor RPM", "unit": "rpm", "normal_min": 900, "normal_max": 1500},
    {"sensor_key": "vibration", "label": "Vibration", "unit": "mm/s", "normal_min": 0, "normal_max": 4.5},
    {"sensor_key": "brake", "label": "Brake Condition", "unit": "%", "normal_min": 80, "normal_max": 100},
    {"sensor_key": "load", "label": "Load Percentage", "unit": "%", "normal_min": 0, "normal_max": 90},
    {"sensor_key": "humidity", "label": "Humidity", "unit": "%", "normal_min": 30, "normal_max": 60},
    {"sensor_key": "door", "label": "Door Sensor", "unit": "", "normal_min": 0, "normal_max": 0},
]

# ── Default thresholds ─────────────────────────────────────
THRESHOLDS = [
    {"sensor_key": "vibration", "warning_value": 4.5, "critical_value": 7.0},
    {"sensor_key": "motor_temp", "warning_value": 65, "critical_value": 85},
    {"sensor_key": "current", "warning_value": 18, "critical_value": 22},
]

# ── Users (matches frontend admin panel + technicians) ─────
USERS = [
    {"email": settings.admin_email, "name": "Mohan K.", "role": "Admin", "password": settings.admin_password},
    {"email": "karthik@elevatorai.io", "name": "R. Karthik", "role": "Maintenance Engineer", "password": "karthik2026!", "tech_spec": "Motor & Drive Systems"},
    {"email": "priya@elevatorai.io", "name": "S. Priya", "role": "Maintenance Engineer", "password": "priya2026!", "tech_spec": "Electrical Systems"},
    {"email": "manager@elevatorai.io", "name": "Manager Desk", "role": "Manager", "password": "manager2026!"},
    {"email": "mohammed@elevatorai.io", "name": "A. Mohammed", "role": "Technician", "password": "mohammed2026!", "tech_spec": "Door Systems"},
    {"email": "lakshmi@elevatorai.io", "name": "V. Lakshmi", "role": "Technician", "password": "lakshmi2026!", "tech_spec": "Brake Systems"},
    {"email": "suresh@elevatorai.io", "name": "D. Suresh", "role": "Technician", "password": "suresh2026!", "tech_spec": "Bearing & Vibration Analysis"},
]


async def seed_all(db: AsyncSession) -> dict:
    """Run the full seed process. Returns counts of entities created."""
    counts = {}

    # 1. Roles
    created_roles = 0
    role_map: dict[str, int] = {}
    for r in ROLES:
        existing = await db.execute(select(Role).where(Role.name == r["name"]))
        role_obj = existing.scalar_one_or_none()
        if role_obj is None:
            role_obj = Role(**r)
            db.add(role_obj)
            await db.flush()
            created_roles += 1
        role_map[role_obj.name] = role_obj.id
    counts["roles"] = created_roles

    # 2. Users + Technicians
    created_users = 0
    created_techs = 0
    for u in USERS:
        existing = await db.execute(select(User).where(User.email == u["email"]))
        if existing.scalar_one_or_none():
            continue
        user_obj = User(
            email=u["email"],
            name=u["name"],
            password_hash=hash_password(u["password"]),
            role_id=role_map[u["role"]],
        )
        db.add(user_obj)
        await db.flush()
        created_users += 1

        # Create technician profile if specialization given
        if "tech_spec" in u:
            tech = Technician(
                user_id=user_obj.id,
                name=u["name"],
                email=u["email"],
                phone="+91 98765 43210",
                role_title=u["role"],
                specialization=u["tech_spec"],
                availability="Available",
                active_workload=1,
                completed_count=12,
                rating=4.9,
            )
            db.add(tech)
            await db.flush()
            created_techs += 1

    counts["users"] = created_users
    counts["technicians"] = created_techs

    # 3. Buildings
    created_buildings = 0
    for b in BUILDINGS:
        existing = await db.execute(select(Building).where(Building.id == b["id"]))
        if existing.scalar_one_or_none():
            continue
        db.add(Building(**b))
        await db.flush()
        created_buildings += 1
    counts["buildings"] = created_buildings

    # 4. Elevators
    created_elevators = 0
    for e in ELEVATORS:
        existing = await db.execute(select(Elevator).where(Elevator.id == e["id"]))
        if existing.scalar_one_or_none():
            continue
        db.add(Elevator(**e))
        await db.flush()
        created_elevators += 1
    counts["elevators"] = created_elevators

    # 5. Seed Maintenance Tasks
    from app.models.models import MaintenanceTask
    import datetime as dt
    now = dt.datetime.now(dt.timezone.utc)

    TASKS = [
        {
            "id": "TASK-101",
            "elevator_id": "KONE-ELEV-001",
            "building_id": "BLD-A",
            "title": "Drive Shaft Bearing Replacement",
            "fault_type": "Bearing Degradation",
            "priority": "Critical",
            "due_date": now + dt.timedelta(days=1),
            "status": "In Progress",
            "technician_name": "D. Suresh",
            "notes": "Replace SKF-6208 bearing unit and measure axial tolerance.",
            "ai_recommendation": {"recommended_tech": "D. Suresh", "match_reason": "Bearing & Vibration Specialist"},
        },
        {
            "id": "TASK-102",
            "elevator_id": "KONE-ELEV-002",
            "building_id": "BLD-A",
            "title": "Door Interlock Realignment",
            "fault_type": "Door Alignment Drift",
            "priority": "Medium",
            "due_date": now + dt.timedelta(days=3),
            "status": "Scheduled",
            "technician_name": "A. Mohammed",
            "notes": "Clean sill track & adjust optical interlock sensors.",
            "ai_recommendation": {"recommended_tech": "A. Mohammed", "match_reason": "Door Systems Expert"},
        },
        {
            "id": "TASK-103",
            "elevator_id": "KONE-ELEV-007",
            "building_id": "BLD-B",
            "title": "Stator Winding Thermal Inspection",
            "fault_type": "Motor Overheating",
            "priority": "High",
            "due_date": now - dt.timedelta(days=1),
            "status": "Overdue",
            "technician_name": "R. Karthik",
            "notes": "Check cooling fan airflow and measure coil phase resistance.",
            "ai_recommendation": {"recommended_tech": "R. Karthik", "match_reason": "Motor Systems Specialist"},
        },
        {
            "id": "TASK-104",
            "elevator_id": "KONE-ELEV-003",
            "building_id": "BLD-A",
            "title": "Routine Preventive Inspection",
            "fault_type": "Preventive Inspection",
            "priority": "Low",
            "due_date": now - dt.timedelta(days=5),
            "status": "Completed",
            "technician_name": "V. Lakshmi",
            "notes": "Completed routine lube and brake gap adjustment.",
            "completed_at": now - dt.timedelta(days=5),
        },
    ]

    created_tasks = 0
    for t_data in TASKS:
        existing = await db.execute(select(MaintenanceTask).where(MaintenanceTask.id == t_data["id"]))
        if existing.scalar_one_or_none():
            continue
        db.add(MaintenanceTask(**t_data))
        await db.flush()
        created_tasks += 1
    counts["maintenance_tasks"] = created_tasks

    # 6. Sensor definitions
    created_sensors = 0
    for s in SENSOR_DEFS:
        existing = await db.execute(select(SensorDefinition).where(SensorDefinition.sensor_key == s["sensor_key"]))
        if existing.scalar_one_or_none():
            continue
        db.add(SensorDefinition(**s))
        await db.flush()
        created_sensors += 1
    counts["sensor_definitions"] = created_sensors

    # 7. Thresholds
    created_thresholds = 0
    for th in THRESHOLDS:
        existing = await db.execute(select(ThresholdConfig).where(ThresholdConfig.sensor_key == th["sensor_key"]))
        if existing.scalar_one_or_none():
            continue
        db.add(ThresholdConfig(**th))
        await db.flush()
        created_thresholds += 1
    counts["thresholds"] = created_thresholds

    # 8. System settings
    default_settings = [
        {"key": "app.version", "value": settings.app_version, "description": "Application version"},
        {"key": "telemetry.interval_ms", "value": "3000", "description": "Sensor push interval in milliseconds"},
        {"key": "ai.fault_detection.enabled", "value": "true", "description": "Enable AI fault detection"},
    ]
    created_settings = 0
    for ss in default_settings:
        existing = await db.execute(select(SystemSetting).where(SystemSetting.key == ss["key"]))
        if existing.scalar_one_or_none():
            continue
        db.add(SystemSetting(**ss))
        await db.flush()
        created_settings += 1
    counts["system_settings"] = created_settings

    await db.commit()
    return counts
