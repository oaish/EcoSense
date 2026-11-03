import uuid
from datetime import date
from typing import List, Optional
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.dependencies import get_current_active_user, require_roles
from app.models.user import User
from app.schemas.attendance import (
    AdminAttendanceOverview,
    AttendanceCheckInRequest,
    AttendanceCheckOutRequest,
    AttendanceRead,
)
from app.services import attendance_service

router = APIRouter()


@router.post(
    "/check-in",
    response_model=AttendanceRead,
    status_code=status.HTTP_201_CREATED,
    summary="Collector Shift Check-In",
    description="Start a daily shift. Validates that no active shift is already open for this collector.",
)
def check_in_endpoint(
    check_in_in: Optional[AttendanceCheckInRequest] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles("COLLECTOR")),
) -> AttendanceRead:
    record = attendance_service.check_in(
        db=db,
        collector=current_user,
        check_in_in=check_in_in,
    )
    return AttendanceRead.model_validate(record)


@router.post(
    "/check-out",
    response_model=AttendanceRead,
    summary="Collector Shift Check-Out",
    description="End the active shift session. Validates that an active shift session exists.",
)
def check_out_endpoint(
    check_out_in: Optional[AttendanceCheckOutRequest] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles("COLLECTOR")),
) -> AttendanceRead:
    record = attendance_service.check_out(
        db=db,
        collector=current_user,
        check_out_in=check_out_in,
    )
    return AttendanceRead.model_validate(record)


@router.get(
    "/me",
    response_model=Optional[AttendanceRead],
    summary="Get Collector Active Shift",
    description="Retrieve the current active shift session for the authenticated collector, or null if off shift.",
)
def get_my_active_shift_endpoint(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles("COLLECTOR")),
) -> Optional[AttendanceRead]:
    record = attendance_service.get_current_active_shift(
        db=db,
        collector_id=current_user.user_id,
    )
    if not record:
        return None
    return AttendanceRead.model_validate(record)


@router.get(
    "/me/history",
    response_model=List[AttendanceRead],
    summary="Get Collector Attendance History",
    description="Retrieve past shifts and attendance history for the authenticated collector.",
)
def get_my_history_endpoint(
    skip: int = Query(0, ge=0, description="Offset"),
    limit: int = Query(50, ge=1, le=100, description="Page limit"),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles("COLLECTOR")),
) -> List[AttendanceRead]:
    records = attendance_service.get_collector_attendance_history(
        db=db,
        collector_id=current_user.user_id,
        skip=skip,
        limit=limit,
    )
    return [AttendanceRead.model_validate(r) for r in records]


@router.get(
    "/admin/overview",
    response_model=AdminAttendanceOverview,
    summary="Admin Collector Availability Overview",
    description="Retrieve campus-wide collector on-shift statuses, workload metrics, and active task statistics.",
)
def get_admin_overview_endpoint(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles("ADMIN")),
) -> AdminAttendanceOverview:
    return attendance_service.get_admin_attendance_overview(db=db)


@router.get(
    "/admin/history",
    response_model=List[AttendanceRead],
    summary="Admin All Collectors Attendance History",
    description="Query historical attendance logs across all campus collectors.",
)
def get_admin_history_endpoint(
    collector_id: Optional[uuid.UUID] = Query(None, description="Filter by collector UUID"),
    start_date: Optional[date] = Query(None, description="Filter from calendar date"),
    end_date: Optional[date] = Query(None, description="Filter to calendar date"),
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles("ADMIN")),
) -> List[AttendanceRead]:
    records = attendance_service.list_admin_attendance_history(
        db=db,
        collector_id=collector_id,
        start_date=start_date,
        end_date=end_date,
        skip=skip,
        limit=limit,
    )
    return [AttendanceRead.model_validate(r) for r in records]
