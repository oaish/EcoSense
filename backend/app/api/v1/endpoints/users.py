import uuid
from datetime import datetime, timezone
from typing import Optional
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.dependencies import get_current_active_user, require_roles
from app.models.user import User
from app.schemas.user import (
    AdminTestResponse,
    AdminUserCreate,
    AdminUserDetail,
    AdminUserListResponse,
    AdminUserSummary,
    AdminUserUpdate,
    CollectorPhoneUpdate,
    UserRead,
)
from app.services import user_service

router = APIRouter()


@router.get(
    "",
    response_model=AdminUserListResponse,
    summary="List Users (Admin Only)",
    description="Retrieve paginated users with search by name/email, role filtering, active status filtering, and computed point totals.",
)
@router.get(
    "/",
    response_model=AdminUserListResponse,
    include_in_schema=False,
)
def list_users(
    search: Optional[str] = Query(None, description="Search term for user name or email"),
    role: Optional[str] = Query(None, description="Filter by role: STUDENT, STAFF, COLLECTOR, ADMIN"),
    is_active: Optional[bool] = Query(None, description="Filter by active status"),
    skip: int = Query(0, ge=0, description="Records to skip"),
    limit: int = Query(50, ge=1, le=100, description="Max records to return"),
    db: Session = Depends(get_db),
    admin_user: User = Depends(require_roles("ADMIN")),
) -> AdminUserListResponse:
    res = user_service.list_users_admin(
        db=db,
        search=search,
        role_name=role,
        is_active=is_active,
        skip=skip,
        limit=limit,
    )
    return AdminUserListResponse(**res)


@router.post(
    "",
    response_model=AdminUserSummary,
    status_code=status.HTTP_201_CREATED,
    summary="Create User (Admin Only)",
    description="Provision a new user account with assigned role and Argon2id hashed password.",
)
@router.post(
    "/",
    response_model=AdminUserSummary,
    status_code=status.HTTP_201_CREATED,
    include_in_schema=False,
)
def create_user_by_admin(
    user_data: AdminUserCreate,
    db: Session = Depends(get_db),
    admin_user: User = Depends(require_roles("ADMIN")),
) -> AdminUserSummary:
    user = user_service.create_admin_user(db=db, data=user_data)
    return AdminUserSummary.model_validate(user)


@router.get(
    "/{user_id}/detail",
    response_model=AdminUserDetail,
    summary="Get User Administrative Details (Admin Only)",
    description="Retrieve comprehensive metrics, point ledger transactions, redemptions, and activity counts for a user.",
)
def get_user_detail(
    user_id: uuid.UUID,
    db: Session = Depends(get_db),
    admin_user: User = Depends(require_roles("ADMIN")),
) -> AdminUserDetail:
    return user_service.get_user_admin_detail(db=db, user_id=user_id)


@router.patch(
    "/{user_id}",
    response_model=AdminUserSummary,
    summary="Update User (Admin Only)",
    description="Update user profile fields, role, active/inactive state, or reset password.",
)
def update_user_by_admin(
    user_id: uuid.UUID,
    update_data: AdminUserUpdate,
    db: Session = Depends(get_db),
    admin_user: User = Depends(require_roles("ADMIN")),
) -> AdminUserSummary:
    updated = user_service.update_admin_user(db=db, user_id=user_id, data=update_data)
    return AdminUserSummary.model_validate(updated)


@router.patch(
    "/{user_id}/phone",
    response_model=AdminUserSummary,
    summary="Update User Phone Number (Admin Only)",
    description="Add, update, or remove a user's phone number with E.164 normalization.",
)
def update_user_phone_number(
    user_id: uuid.UUID,
    payload: CollectorPhoneUpdate,
    db: Session = Depends(get_db),
    admin_user: User = Depends(require_roles("ADMIN")),
) -> AdminUserSummary:
    updated = user_service.update_user_phone(db=db, user_id=user_id, phone_number=payload.phone_number)
    return AdminUserSummary.model_validate(updated)


@router.get(
    "/me",
    response_model=UserRead,
    summary="Get Detailed Current User Profile",
    description="Retrieve detailed account information for the active user.",
)
def get_user_profile(
    current_user: User = Depends(get_current_active_user),
) -> UserRead:
    return UserRead.model_validate(current_user)


@router.get(
    "/admin-test",
    response_model=AdminTestResponse,
    summary="Admin Role Verification Endpoint",
    description="Protected endpoint accessible only by users with the ADMIN role.",
)
def admin_role_test(
    current_user: User = Depends(require_roles("ADMIN")),
) -> AdminTestResponse:
    return AdminTestResponse(
        message="Admin privilege verified successfully.",
        admin_user=current_user.email,
        timestamp=datetime.now(timezone.utc),
    )
