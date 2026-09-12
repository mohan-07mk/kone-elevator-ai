"""Pydantic v2 schemas for request/response validation."""

from __future__ import annotations

import datetime as dt
from typing import Optional

from pydantic import BaseModel, EmailStr, Field, ConfigDict


# ════════════════════════════════════════════════════════════
#  AUTH
# ════════════════════════════════════════════════════════════
class LoginRequest(BaseModel):
    email: EmailStr
    password: str = Field(min_length=4)


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class RefreshRequest(BaseModel):
    refresh_token: str


# ════════════════════════════════════════════════════════════
#  ROLES
# ════════════════════════════════════════════════════════════
class RoleOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    name: str
    description: Optional[str] = None


# ════════════════════════════════════════════════════════════
#  USERS
# ════════════════════════════════════════════════════════════
class UserCreate(BaseModel):
    email: EmailStr
    name: str = Field(min_length=1, max_length=150)
    password: str = Field(min_length=6)
    role_id: int


class UserUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=150)
    email: Optional[EmailStr] = None
    role_id: Optional[int] = None
    is_active: Optional[bool] = None


class UserOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    email: str
    name: str
    is_active: bool
    role: RoleOut
    created_at: dt.datetime
    updated_at: dt.datetime


class UserMe(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    email: str
    name: str
    role: RoleOut
    is_active: bool


# ════════════════════════════════════════════════════════════
#  BUILDINGS
# ════════════════════════════════════════════════════════════
class BuildingCreate(BaseModel):
    id: str = Field(min_length=1, max_length=20)
    name: str = Field(min_length=1, max_length=150)
    location: Optional[str] = None


class BuildingUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=150)
    location: Optional[str] = None


class BuildingOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: str
    name: str
    location: Optional[str]
    elevator_count: int = 0
    created_at: Optional[dt.datetime] = None
    updated_at: Optional[dt.datetime] = None


class BuildingDetail(BuildingOut):
    elevators: list[ElevatorOut] = []


# ════════════════════════════════════════════════════════════
#  ELEVATORS
# ════════════════════════════════════════════════════════════
class ElevatorCreate(BaseModel):
    id: str = Field(min_length=1, max_length=30)
    building_id: str
    current_floor: int = 1
    status: str = "healthy"
    health_score: float = 100.0
    risk_level: str = "Low"


class ElevatorUpdate(BaseModel):
    current_floor: Optional[int] = None
    direction: Optional[str] = None
    status: Optional[str] = None
    health_score: Optional[float] = None
    active_fault: Optional[str] = None
    risk_level: Optional[str] = None
    speed: Optional[float] = None
    load_percentage: Optional[float] = None
    door_status: Optional[str] = None
    connection_status: Optional[str] = None


class ElevatorOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: str
    building_id: str
    building_name: str = ""
    current_floor: int
    direction: str
    status: str
    health_score: float
    active_fault: Optional[str]
    risk_level: str
    speed: float
    load_percentage: float
    door_status: str
    connection_status: str
    last_telemetry_at: Optional[dt.datetime]
    created_at: Optional[dt.datetime] = None
    updated_at: Optional[dt.datetime] = None


# ════════════════════════════════════════════════════════════
#  SYSTEM STATUS
# ════════════════════════════════════════════════════════════
class SystemStatus(BaseModel):
    status: str
    version: str
    database: str
    total_buildings: int
    total_elevators: int
    total_users: int


class HealthCheck(BaseModel):
    status: str


# Forward-ref resolution
BuildingDetail.model_rebuild()
