"""User management API — CRUD operations (Admin only for create/update/delete)."""

from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.session import get_db
from app.models.models import User, Role
from app.schemas.schemas import UserCreate, UserUpdate, UserOut
from app.security.auth import hash_password
from app.security.dependencies import get_current_user, require_roles
from app.services.audit_service import log_action

router = APIRouter(prefix="/api/users", tags=["Users"])


@router.get("", response_model=list[UserOut])
async def list_users(
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(require_roles("Admin", "Manager"))],
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
    is_active: bool | None = None,
):
    """List users with optional active-status filter (Admin/Manager only)."""
    q = select(User).offset(skip).limit(limit).order_by(User.id)
    if is_active is not None:
        q = q.where(User.is_active == is_active)
    result = await db.execute(q)
    return result.scalars().all()


@router.get("/{user_id}", response_model=UserOut)
async def get_user(
    user_id: int,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
):
    """Get a specific user. Any authenticated user may view."""
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return user


@router.post("", response_model=UserOut, status_code=status.HTTP_201_CREATED)
async def create_user(
    body: UserCreate,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(require_roles("Admin"))],
):
    """Create a new user (Admin only)."""
    # Check duplicate email
    existing = await db.execute(select(User).where(User.email == body.email))
    if existing.scalar_one_or_none():
        raise HTTPException(status_code=409, detail="Email already registered")

    # Check role exists
    role = await db.execute(select(Role).where(Role.id == body.role_id))
    if role.scalar_one_or_none() is None:
        raise HTTPException(status_code=400, detail=f"Role ID {body.role_id} does not exist")

    user = User(
        email=body.email,
        name=body.name,
        password_hash=hash_password(body.password),
        role_id=body.role_id,
    )
    db.add(user)
    await db.flush()
    await db.refresh(user)

    await log_action(
        db, user_id=current_user.id, action="User Created",
        resource_type="user", resource_id=str(user.id),
    )
    return user


@router.patch("/{user_id}", response_model=UserOut)
async def update_user(
    user_id: int,
    body: UserUpdate,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(require_roles("Admin"))],
):
    """Update a user (Admin only)."""
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")

    update_data = body.model_dump(exclude_unset=True)
    if "email" in update_data:
        dup = await db.execute(
            select(User).where(User.email == update_data["email"], User.id != user_id)
        )
        if dup.scalar_one_or_none():
            raise HTTPException(status_code=409, detail="Email already in use")

    for field, value in update_data.items():
        setattr(user, field, value)

    await db.flush()
    await db.refresh(user)

    await log_action(
        db, user_id=current_user.id, action="User Updated",
        resource_type="user", resource_id=str(user.id), details=update_data,
    )
    return user


@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(
    user_id: int,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(require_roles("Admin"))],
):
    """Soft-delete a user by setting is_active=False (Admin only)."""
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    if user.id == current_user.id:
        raise HTTPException(status_code=400, detail="Cannot deactivate your own account")

    user.is_active = False
    await db.flush()

    await log_action(
        db, user_id=current_user.id, action="User Deactivated",
        resource_type="user", resource_id=str(user.id),
    )
