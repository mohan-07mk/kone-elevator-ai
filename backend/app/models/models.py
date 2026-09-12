"""SQLAlchemy ORM models — Elevator AI."""

from __future__ import annotations

import datetime as dt
import uuid
from typing import Optional

from sqlalchemy import (
    Boolean, Column, DateTime, Float, ForeignKey, Index, Integer,
    String, Text, UniqueConstraint, func, JSON,
)
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.session import Base


# ────────────────────────────────────────────────────────────
#  ROLES
# ────────────────────────────────────────────────────────────
class Role(Base):
    __tablename__ = "roles"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    description: Mapped[Optional[str]] = mapped_column(String(200))
    permissions: Mapped[Optional[dict]] = mapped_column(JSON, default=dict)
    created_at: Mapped[dt.datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    users: Mapped[list["User"]] = relationship(back_populates="role")


# ────────────────────────────────────────────────────────────
#  USERS
# ────────────────────────────────────────────────────────────
class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False, index=True)
    name: Mapped[str] = mapped_column(String(150), nullable=False)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    role_id: Mapped[int] = mapped_column(Integer, ForeignKey("roles.id"), nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    created_at: Mapped[dt.datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[dt.datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    role: Mapped["Role"] = relationship(back_populates="users", lazy="joined")
    technician: Mapped[Optional["Technician"]] = relationship(back_populates="user", uselist=False)
    preferences: Mapped[Optional["UserPreference"]] = relationship(back_populates="user", uselist=False)
    audit_logs: Mapped[list["AuditLog"]] = relationship(back_populates="user")


# ────────────────────────────────────────────────────────────
#  USER PREFERENCES
# ────────────────────────────────────────────────────────────
class UserPreference(Base):
    __tablename__ = "user_preferences"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id", ondelete="CASCADE"), unique=True)
    dark_mode: Mapped[bool] = mapped_column(Boolean, default=True)
    language: Mapped[str] = mapped_column(String(30), default="English")
    notify_critical: Mapped[bool] = mapped_column(Boolean, default=True)
    notify_warning: Mapped[bool] = mapped_column(Boolean, default=True)
    notify_info: Mapped[bool] = mapped_column(Boolean, default=False)
    notify_email: Mapped[bool] = mapped_column(Boolean, default=True)

    user: Mapped["User"] = relationship(back_populates="preferences")


# ────────────────────────────────────────────────────────────
#  BUILDINGS
# ────────────────────────────────────────────────────────────
class Building(Base):
    __tablename__ = "buildings"

    id: Mapped[str] = mapped_column(String(20), primary_key=True)
    name: Mapped[str] = mapped_column(String(150), nullable=False)
    location: Mapped[Optional[str]] = mapped_column(String(300))
    created_at: Mapped[dt.datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[dt.datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    elevators: Mapped[list["Elevator"]] = relationship(back_populates="building", cascade="all, delete-orphan")


# ────────────────────────────────────────────────────────────
#  ELEVATORS
# ────────────────────────────────────────────────────────────
class Elevator(Base):
    __tablename__ = "elevators"

    id: Mapped[str] = mapped_column(String(30), primary_key=True)
    building_id: Mapped[str] = mapped_column(String(20), ForeignKey("buildings.id"), nullable=False, index=True)
    current_floor: Mapped[int] = mapped_column(Integer, default=1)
    direction: Mapped[str] = mapped_column(String(10), default="idle")
    status: Mapped[str] = mapped_column(String(20), default="healthy")
    health_score: Mapped[float] = mapped_column(Float, default=100.0)
    active_fault: Mapped[Optional[str]] = mapped_column(String(200))
    risk_level: Mapped[str] = mapped_column(String(10), default="Low")
    speed: Mapped[float] = mapped_column(Float, default=0.0)
    load_percentage: Mapped[float] = mapped_column(Float, default=0.0)
    door_status: Mapped[str] = mapped_column(String(10), default="closed")
    connection_status: Mapped[str] = mapped_column(String(10), default="offline")
    last_telemetry_at: Mapped[Optional[dt.datetime]] = mapped_column(DateTime(timezone=True))
    created_at: Mapped[dt.datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[dt.datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    building: Mapped["Building"] = relationship(back_populates="elevators", lazy="joined")
    sensor_readings: Mapped[list["SensorReading"]] = relationship(back_populates="elevator")
    devices: Mapped[list["Device"]] = relationship(back_populates="elevator")


# ────────────────────────────────────────────────────────────
#  SENSOR DEFINITIONS
# ────────────────────────────────────────────────────────────
class SensorDefinition(Base):
    __tablename__ = "sensor_definitions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    sensor_key: Mapped[str] = mapped_column(String(30), unique=True, nullable=False)
    label: Mapped[str] = mapped_column(String(80), nullable=False)
    unit: Mapped[str] = mapped_column(String(20), default="")
    normal_min: Mapped[float] = mapped_column(Float, nullable=False)
    normal_max: Mapped[float] = mapped_column(Float, nullable=False)
    created_at: Mapped[dt.datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())


# ────────────────────────────────────────────────────────────
#  SENSOR READINGS  (time-series)
# ────────────────────────────────────────────────────────────
class SensorReading(Base):
    __tablename__ = "sensor_readings"
    __table_args__ = (
        Index("ix_sensor_readings_lookup", "elevator_id", "sensor_key", "recorded_at"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    elevator_id: Mapped[str] = mapped_column(String(30), ForeignKey("elevators.id"), nullable=False)
    sensor_key: Mapped[str] = mapped_column(String(30), nullable=False)
    value: Mapped[float] = mapped_column(Float, nullable=False)
    is_anomaly: Mapped[bool] = mapped_column(Boolean, default=False)
    recorded_at: Mapped[dt.datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), index=True
    )

    elevator: Mapped["Elevator"] = relationship(back_populates="sensor_readings")


# ────────────────────────────────────────────────────────────
#  TECHNICIANS
# ────────────────────────────────────────────────────────────
class Technician(Base):
    __tablename__ = "technicians"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("users.id", ondelete="CASCADE"), unique=True)
    name: Mapped[str] = mapped_column(String(150), default="Field Technician")
    email: Mapped[str] = mapped_column(String(255), default="tech@kone.com")
    phone: Mapped[Optional[str]] = mapped_column(String(50))
    role_title: Mapped[str] = mapped_column(String(100), default="Field Technician Specialist")
    specialization: Mapped[Optional[str]] = mapped_column(String(150), default="Bearing & Drive Systems")
    availability: Mapped[str] = mapped_column(String(20), default="Available")
    active_workload: Mapped[int] = mapped_column(Integer, default=0)
    current_task_count: Mapped[int] = mapped_column(Integer, default=0)
    completed_count: Mapped[int] = mapped_column(Integer, default=0)
    completed_task_count: Mapped[int] = mapped_column(Integer, default=0)
    rating: Mapped[float] = mapped_column(Float, default=4.9)
    created_at: Mapped[dt.datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    user: Mapped[Optional["User"]] = relationship(back_populates="technician")
    tasks: Mapped[list["MaintenanceTask"]] = relationship(back_populates="technician")


# ────────────────────────────────────────────────────────────
#  DEVICES  (edge gateways, sensor modules)
# ────────────────────────────────────────────────────────────
class Device(Base):
    __tablename__ = "devices"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    elevator_id: Mapped[str] = mapped_column(String(30), ForeignKey("elevators.id"), nullable=False, index=True)
    device_type: Mapped[str] = mapped_column(String(50), nullable=False)  # e.g. "STM32", "Raspberry Pi"
    serial_number: Mapped[Optional[str]] = mapped_column(String(100), unique=True)
    firmware_version: Mapped[Optional[str]] = mapped_column(String(30))
    status: Mapped[str] = mapped_column(String(20), default="offline")
    last_seen_at: Mapped[Optional[dt.datetime]] = mapped_column(DateTime(timezone=True))
    created_at: Mapped[dt.datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    elevator: Mapped["Elevator"] = relationship(back_populates="devices")


# ────────────────────────────────────────────────────────────
#  THRESHOLD CONFIGURATIONS
# ────────────────────────────────────────────────────────────
class ThresholdConfig(Base):
    __tablename__ = "threshold_configs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    sensor_key: Mapped[str] = mapped_column(String(30), unique=True, nullable=False)
    warning_value: Mapped[float] = mapped_column(Float, nullable=False)
    critical_value: Mapped[float] = mapped_column(Float, nullable=False)
    updated_by: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("users.id"))
    updated_at: Mapped[dt.datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )


# ────────────────────────────────────────────────────────────
#  SYSTEM SETTINGS
# ────────────────────────────────────────────────────────────
class SystemSetting(Base):
    __tablename__ = "system_settings"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    key: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    value: Mapped[str] = mapped_column(Text, nullable=False)
    description: Mapped[Optional[str]] = mapped_column(String(300))
    updated_by: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("users.id"))
    updated_at: Mapped[dt.datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )


# ────────────────────────────────────────────────────────────
#  AUDIT LOG
# ────────────────────────────────────────────────────────────
class AuditLog(Base):
    __tablename__ = "audit_logs"
    __table_args__ = (
        Index("ix_audit_logs_created", "created_at"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("users.id"))
    action: Mapped[str] = mapped_column(String(100), nullable=False)
    resource_type: Mapped[Optional[str]] = mapped_column(String(50))
    resource_id: Mapped[Optional[str]] = mapped_column(String(50))
    details: Mapped[Optional[dict]] = mapped_column(JSON)
    ip_address: Mapped[Optional[str]] = mapped_column(String(45))
    created_at: Mapped[dt.datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    user: Mapped[Optional["User"]] = relationship(back_populates="audit_logs")


# ────────────────────────────────────────────────────────────
#  AI INFERENCES
# ────────────────────────────────────────────────────────────
class AIInference(Base):
    __tablename__ = "ai_inferences"
    __table_args__ = (
        Index("ix_ai_inferences_elevator_created", "elevator_id", "created_at"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    elevator_id: Mapped[str] = mapped_column(String(30), ForeignKey("elevators.id"), nullable=False)
    fault_detected: Mapped[bool] = mapped_column(Boolean, default=False)
    fault_type: Mapped[str] = mapped_column(String(100), default="Healthy Operational State")
    confidence: Mapped[float] = mapped_column(Float, default=0.0)
    severity: Mapped[str] = mapped_column(String(20), default="healthy")
    model_name: Mapped[str] = mapped_column(String(100), default="RandomForestClassifier")
    model_version: Mapped[str] = mapped_column(String(30), default="1.0.0")
    inference_time_ms: Mapped[float] = mapped_column(Float, default=0.0)
    features: Mapped[Optional[dict]] = mapped_column(JSON)
    created_at: Mapped[dt.datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    rca_result: Mapped[Optional["RCAResult"]] = relationship(back_populates="inference", uselist=False)


# ────────────────────────────────────────────────────────────
#  ROOT CAUSE ANALYSIS (RCA)
# ────────────────────────────────────────────────────────────
class RCAResult(Base):
    __tablename__ = "rca_results"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    elevator_id: Mapped[str] = mapped_column(String(30), ForeignKey("elevators.id"), nullable=False)
    inference_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("ai_inferences.id"))
    root_cause: Mapped[str] = mapped_column(String(300), nullable=False)
    affected_component: Mapped[str] = mapped_column(String(150), nullable=False)
    confidence: Mapped[float] = mapped_column(Float, default=0.0)
    contributing_factors: Mapped[Optional[dict]] = mapped_column(JSON)
    evidence: Mapped[Optional[dict]] = mapped_column(JSON)
    verification_steps: Mapped[Optional[dict]] = mapped_column(JSON)
    created_at: Mapped[dt.datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    inference: Mapped[Optional["AIInference"]] = relationship(back_populates="rca_result")


# ────────────────────────────────────────────────────────────
#  ELEVATOR HEALTH RECORDS
# ────────────────────────────────────────────────────────────
class ElevatorHealthRecord(Base):
    __tablename__ = "elevator_health_records"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    elevator_id: Mapped[str] = mapped_column(String(30), ForeignKey("elevators.id"), nullable=False)
    overall_health: Mapped[float] = mapped_column(Float, nullable=False)
    motor_health: Mapped[float] = mapped_column(Float, default=100.0)
    bearing_health: Mapped[float] = mapped_column(Float, default=100.0)
    door_health: Mapped[float] = mapped_column(Float, default=100.0)
    brake_health: Mapped[float] = mapped_column(Float, default=100.0)
    electrical_health: Mapped[float] = mapped_column(Float, default=100.0)
    status: Mapped[str] = mapped_column(String(20), default="healthy")
    contributing_factors: Mapped[Optional[dict]] = mapped_column(JSON)
    weights: Mapped[Optional[dict]] = mapped_column(JSON)
    recorded_at: Mapped[dt.datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())


# ────────────────────────────────────────────────────────────
#  PREDICTIVE MAINTENANCE & RUL
# ────────────────────────────────────────────────────────────
class PredictiveRecord(Base):
    __tablename__ = "predictive_records"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    elevator_id: Mapped[str] = mapped_column(String(30), ForeignKey("elevators.id"), nullable=False)
    failure_risk: Mapped[float] = mapped_column(Float, default=0.0)
    rul_hours: Mapped[float] = mapped_column(Float, default=2400.0)
    priority: Mapped[str] = mapped_column(String(20), default="Low")
    recommended_action: Mapped[str] = mapped_column(String(300), default="Routine Inspection")
    component_health: Mapped[Optional[dict]] = mapped_column(JSON)
    computed_at: Mapped[dt.datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())


# ────────────────────────────────────────────────────────────
#  ALERTS
# ────────────────────────────────────────────────────────────
class AlertRecord(Base):
    __tablename__ = "alert_records"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    elevator_id: Mapped[str] = mapped_column(String(30), ForeignKey("elevators.id"), nullable=False)
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    level: Mapped[str] = mapped_column(String(20), default="warning")  # "info", "warning", "critical"
    source: Mapped[str] = mapped_column(String(50), default="ai_pipeline")
    status: Mapped[str] = mapped_column(String(20), default="active")  # "active", "acknowledged", "resolved"
    details: Mapped[Optional[dict]] = mapped_column(JSON)
    acknowledged_at: Mapped[Optional[dt.datetime]] = mapped_column(DateTime(timezone=True))
    created_at: Mapped[dt.datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())





# ────────────────────────────────────────────────────────────
#  MAINTENANCE TASKS
# ────────────────────────────────────────────────────────────
class MaintenanceTask(Base):
    __tablename__ = "maintenance_tasks"

    id: Mapped[str] = mapped_column(String(30), primary_key=True)
    elevator_id: Mapped[str] = mapped_column(String(30), ForeignKey("elevators.id"), nullable=False)
    building_id: Mapped[Optional[str]] = mapped_column(String(20), ForeignKey("buildings.id"))
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    fault_type: Mapped[str] = mapped_column(String(100), default="Preventive Inspection")
    priority: Mapped[str] = mapped_column(String(20), default="Medium")  # "Low", "Medium", "High", "Critical"
    due_date: Mapped[dt.datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    status: Mapped[str] = mapped_column(String(20), default="Scheduled")  # "Scheduled", "In Progress", "Completed", "Overdue", "Cancelled"
    technician_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("technicians.id"))
    technician_name: Mapped[Optional[str]] = mapped_column(String(150))
    ai_recommendation: Mapped[Optional[dict]] = mapped_column(JSON)
    notes: Mapped[Optional[str]] = mapped_column(Text)
    scheduled_at: Mapped[Optional[dt.datetime]] = mapped_column(DateTime(timezone=True))
    completed_at: Mapped[Optional[dt.datetime]] = mapped_column(DateTime(timezone=True))
    created_at: Mapped[dt.datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    technician: Mapped[Optional["Technician"]] = relationship(back_populates="tasks")


