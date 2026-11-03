import uuid
from datetime import date, datetime, timezone
from typing import List, Optional
from zoneinfo import ZoneInfo
from fastapi import HTTPException, status
from sqlalchemy import select, and_, func
from sqlalchemy.orm import Session, joinedload

from app.core.config import settings
from app.models.attendance import CollectorAttendance
from app.models.role import Role
from app.models.task import CollectionTask
from app.models.user import User
from app.schemas.attendance import (
    AdminAttendanceOverview,
    AttendanceCheckInRequest,
    AttendanceCheckOutRequest,
    CollectorShiftSummary,
)


def get_campus_local_now() -> datetime:
    """Returns the current timezone-aware timestamp adjusted to the campus timezone."""
    try:
        tz = ZoneInfo(settings.CAMPUS_TIMEZONE)
    except Exception:
        tz = timezone.utc
    return datetime.now(timezone.utc).astimezone(tz)


def get_campus_today_date() -> date:
    """Returns today's date in the DBIT campus operational timezone."""
    return get_campus_local_now().date()


def check_in(
    db: Session,
    collector: User,
    check_in_in: Optional[AttendanceCheckInRequest] = None,
) -> CollectorAttendance:
    # 1. Enforce that only users with the COLLECTOR role can check in
    collector_role = collector.role.role_name.upper() if collector.role else ""
    if collector_role != "COLLECTOR":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only collector accounts may record shift attendance.",
        )

    # 2. Check for an existing active shift
    active_stmt = select(CollectorAttendance).where(
        and_(
            CollectorAttendance.collector_id == collector.user_id,
            CollectorAttendance.status == "ACTIVE",
        )
    )
    existing_active = db.scalar(active_stmt)
    if existing_active:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Active shift already in progress since {existing_active.check_in_at.strftime('%Y-%m-%d %H:%M:%S UTC')}. Please end your current shift first.",
        )

    # 3. Create new attendance record using server-generated timestamps
    now_utc = datetime.now(timezone.utc)
    today_date = get_campus_today_date()
    notes = check_in_in.notes.strip() if check_in_in and check_in_in.notes else None

    attendance = CollectorAttendance(
        collector_id=collector.user_id,
        attendance_date=today_date,
        check_in_at=now_utc,
        status="ACTIVE",
        notes=notes,
    )
    db.add(attendance)
    db.commit()
    db.refresh(attendance)
    return attendance


def check_out(
    db: Session,
    collector: User,
    check_out_in: Optional[AttendanceCheckOutRequest] = None,
) -> CollectorAttendance:
    collector_role = collector.role.role_name.upper() if collector.role else ""
    if collector_role != "COLLECTOR":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only collector accounts may record shift attendance.",
        )

    # 1. Locate active session
    active_stmt = select(CollectorAttendance).where(
        and_(
            CollectorAttendance.collector_id == collector.user_id,
            CollectorAttendance.status == "ACTIVE",
        )
    )
    active_shift = db.scalar(active_stmt)
    if not active_shift:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No active shift found. You must start a shift before checking out.",
        )

    # 2. Close active session
    now_utc = datetime.now(timezone.utc)
    active_shift.check_out_at = now_utc
    active_shift.status = "COMPLETED"

    if check_out_in and check_out_in.notes and check_out_in.notes.strip():
        existing_notes = active_shift.notes or ""
        checkout_note = f"[Check-out]: {check_out_in.notes.strip()}"
        active_shift.notes = f"{existing_notes}\n{checkout_note}".strip()

    db.commit()
    db.refresh(active_shift)
    return active_shift


def get_current_active_shift(
    db: Session,
    collector_id: uuid.UUID,
) -> Optional[CollectorAttendance]:
    statement = (
        select(CollectorAttendance)
        .options(joinedload(CollectorAttendance.collector))
        .where(
            and_(
                CollectorAttendance.collector_id == collector_id,
                CollectorAttendance.status == "ACTIVE",
            )
        )
    )
    return db.scalar(statement)


def get_collector_attendance_history(
    db: Session,
    collector_id: uuid.UUID,
    skip: int = 0,
    limit: int = 50,
) -> List[CollectorAttendance]:
    statement = (
        select(CollectorAttendance)
        .options(joinedload(CollectorAttendance.collector))
        .where(CollectorAttendance.collector_id == collector_id)
        .order_by(CollectorAttendance.check_in_at.desc())
        .offset(skip)
        .limit(limit)
    )
    return list(db.scalars(statement).all())


def get_admin_attendance_overview(db: Session) -> AdminAttendanceOverview:
    today_date = get_campus_today_date()
    now_utc = datetime.now(timezone.utc)

    # 1. Find all active collectors
    collectors_stmt = (
        select(User)
        .join(Role, User.role_id == Role.role_id)
        .where(
            and_(
                Role.role_name == "COLLECTOR",
                User.is_active == True,
            )
        )
        .order_by(User.name.asc())
    )
    collectors = list(db.scalars(collectors_stmt).all())

    summaries: List[CollectorShiftSummary] = []
    on_shift_count = 0
    not_checked_in_count = 0
    with_active_tasks_count = 0
    total_overdue_tasks = 0

    for c in collectors:
        # Check active shift
        active_shift = db.scalar(
            select(CollectorAttendance).where(
                and_(
                    CollectorAttendance.collector_id == c.user_id,
                    CollectorAttendance.status == "ACTIVE",
                )
            )
        )

        last_shift_today = db.scalar(
            select(CollectorAttendance)
            .where(
                and_(
                    CollectorAttendance.collector_id == c.user_id,
                    CollectorAttendance.attendance_date == today_date,
                )
            )
            .order_by(CollectorAttendance.check_in_at.desc())
        )

        active_session = None
        last_session = None

        if active_shift:
            attendance_status = "ON_SHIFT"
            on_shift_count += 1
            check_in_at = active_shift.check_in_at
            check_out_at = None
            active_id = active_shift.attendance_id
            active_session = {
                "attendance_id": active_shift.attendance_id,
                "collector_id": str(active_shift.collector_id),
                "attendance_date": str(active_shift.attendance_date),
                "check_in_at": active_shift.check_in_at.isoformat() if active_shift.check_in_at else None,
                "check_out_at": None,
                "status": "ON_SHIFT",
            }
        elif last_shift_today and last_shift_today.status == "COMPLETED":
            attendance_status = "CHECKED_OUT"
            check_in_at = last_shift_today.check_in_at
            check_out_at = last_shift_today.check_out_at
            active_id = None
            last_session = {
                "attendance_id": last_shift_today.attendance_id,
                "collector_id": str(last_shift_today.collector_id),
                "attendance_date": str(last_shift_today.attendance_date),
                "check_in_at": last_shift_today.check_in_at.isoformat() if last_shift_today.check_in_at else None,
                "check_out_at": last_shift_today.check_out_at.isoformat() if last_shift_today.check_out_at else None,
                "status": "CHECKED_OUT",
            }
        else:
            attendance_status = "NOT_CHECKED_IN"
            not_checked_in_count += 1
            check_in_at = None
            check_out_at = None
            active_id = None

        # Workload metrics
        active_tasks = db.scalar(
            select(func.count(CollectionTask.task_id)).where(
                and_(
                    CollectionTask.collector_id == c.user_id,
                    CollectionTask.status.in_(["ASSIGNED", "ACCEPTED", "IN_PROGRESS"]),
                )
            )
        ) or 0

        completed_today = db.scalar(
            select(func.count(CollectionTask.task_id)).where(
                and_(
                    CollectionTask.collector_id == c.user_id,
                    CollectionTask.status == "COMPLETED",
                    func.date(CollectionTask.completed_at) == today_date,
                )
            )
        ) or 0

        overdue_tasks = db.scalar(
            select(func.count(CollectionTask.task_id)).where(
                and_(
                    CollectionTask.collector_id == c.user_id,
                    CollectionTask.status.in_(["ASSIGNED", "ACCEPTED", "IN_PROGRESS"]),
                    CollectionTask.due_date != None,
                    CollectionTask.due_date < now_utc,
                )
            )
        ) or 0

        total_overdue_tasks += overdue_tasks

        if active_tasks > 0:
            with_active_tasks_count += 1

        summaries.append(
            CollectorShiftSummary(
                collector_id=c.user_id,
                name=c.name or "",
                collector_name=c.name or "",
                email=c.email or "",
                collector_email=c.email or "",
                is_active=c.is_active,
                attendance_status=attendance_status,
                status=attendance_status,
                active_attendance_id=active_id,
                check_in_at=check_in_at,
                check_out_at=check_out_at,
                active_tasks_count=active_tasks,
                active_task_count=active_tasks,
                completed_tasks_today_count=completed_today,
                overdue_tasks_count=overdue_tasks,
                phone_number=c.phone_number,
                has_sms_configured=bool(c.phone_number and c.phone_number.strip()),
                has_phone_configured=bool(c.phone_number and c.phone_number.strip()),
                active_session=active_session,
                last_session=last_session,
            )
        )

    # Sort collectors: ON_SHIFT first, then active tasks, then name
    summaries.sort(
        key=lambda s: (
            0 if s.attendance_status == "ON_SHIFT" else (1 if s.attendance_status == "CHECKED_OUT" else 2),
            -s.active_tasks_count,
            s.name.lower(),
        )
    )

    return AdminAttendanceOverview(
        total_collectors=len(collectors),
        on_shift_collectors=on_shift_count,
        on_shift_count=on_shift_count,
        not_checked_in_collectors=not_checked_in_count,
        not_checked_in_count=not_checked_in_count,
        collectors_with_active_tasks=with_active_tasks_count,
        with_active_tasks_count=with_active_tasks_count,
        overdue_tasks_count=total_overdue_tasks,
        campus_date=str(today_date),
        collectors=summaries,
    )


def list_admin_attendance_history(
    db: Session,
    collector_id: Optional[uuid.UUID] = None,
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
    skip: int = 0,
    limit: int = 50,
) -> List[CollectorAttendance]:
    statement = (
        select(CollectorAttendance)
        .options(joinedload(CollectorAttendance.collector))
        .order_by(CollectorAttendance.check_in_at.desc())
    )

    if collector_id is not None:
        statement = statement.where(CollectorAttendance.collector_id == collector_id)

    if start_date is not None:
        statement = statement.where(CollectorAttendance.attendance_date >= start_date)

    if end_date is not None:
        statement = statement.where(CollectorAttendance.attendance_date <= end_date)

    statement = statement.offset(skip).limit(limit)
    return list(db.scalars(statement).all())
