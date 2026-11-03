import logging
import uuid
from datetime import datetime, timezone
from typing import List, Optional, Tuple
from fastapi import HTTPException, status
from sqlalchemy import select, and_, func
from sqlalchemy.orm import Session, joinedload

from app.models.bin import Bin
from app.models.collection import CollectionRecord
from app.models.location import Location
from app.models.report import WasteReport
from app.models.role import Role
from app.models.task import CollectionTask
from app.models.user import User
from app.schemas.task import (
    TaskCreate,
    TaskDelegateReportRequest,
    TaskReassignRequest,
    TaskStatusUpdate,
)
from app.services.push_notification_service import push_notification_service

logger = logging.getLogger(__name__)


def _get_verified_collector(db: Session, collector_id: uuid.UUID) -> User:
    collector = db.get(User, collector_id)
    if not collector:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Collector with ID {collector_id} not found.",
        )
    if not collector.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Collector '{collector.name}' account is inactive.",
        )
    role_name = collector.role.role_name.upper() if collector.role else ""
    if role_name != "COLLECTOR":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"User '{collector.name}' does not have the COLLECTOR role.",
        )
    return collector


def create_task(
    db: Session,
    admin_user: User,
    task_in: TaskCreate,
) -> CollectionTask:
    # 1. Validate collector
    collector = _get_verified_collector(db, task_in.collector_id)

    # 2. Validate references
    bin_obj = None
    if task_in.bin_id:
        bin_obj = db.get(Bin, task_in.bin_id)
        if not bin_obj:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Bin with ID {task_in.bin_id} not found.",
            )

    loc_id = task_in.location_id
    if not loc_id and bin_obj:
        loc_id = bin_obj.location_id
    elif loc_id:
        loc = db.get(Location, loc_id)
        if not loc:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Location with ID {loc_id} not found.",
            )

    report_obj = None
    if task_in.report_id:
        report_obj = db.get(WasteReport, task_in.report_id)
        if not report_obj:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Waste report #{task_in.report_id} not found.",
            )
        if not task_in.bin_id and report_obj.bin_id:
            bin_obj = report_obj.bin
            task_in.bin_id = report_obj.bin_id

    # 3. Create task record
    now_utc = datetime.now(timezone.utc)
    task = CollectionTask(
        task_type=task_in.task_type,
        collector_id=collector.user_id,
        bin_id=task_in.bin_id,
        location_id=loc_id,
        report_id=task_in.report_id,
        priority=task_in.priority,
        title=task_in.title.strip(),
        instructions=task_in.instructions.strip() if task_in.instructions else None,
        due_date=task_in.due_date,
        status="ASSIGNED",
        created_by=admin_user.user_id,
        assigned_at=now_utc,
    )
    db.add(task)
    db.commit()
    db.refresh(task)

    # 4. FCM Web Push notification trigger boundary (post-commit, safe)
    try:
        push_notification_service.send_task_assignment_push(
            task=task,
            collector=collector,
            db=db,
        )
    except Exception as exc:
        logger.error(f"[Push Notification Failed] Task #{task.task_id} assigned successfully but notification failed: {exc}")

    return get_task(db, task.task_id) or task


def delegate_report_to_collector(
    db: Session,
    admin_user: User,
    req: TaskDelegateReportRequest,
) -> CollectionTask:
    report = db.get(WasteReport, req.report_id)
    if not report:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Report #{req.report_id} not found.",
        )

    # Build meaningful task title and instructions from original report
    clean_type = report.report_type.replace("_", " ").title()
    title = f"Resolve {clean_type} Issue (Report #{report.report_id})"
    instructions = req.instructions or report.description or f"Address reported {clean_type} on campus."

    task_in = TaskCreate(
        task_type="ISSUE_RESPONSE",
        collector_id=req.collector_id,
        bin_id=report.bin_id,
        location_id=report.bin.location_id if report.bin else None,
        report_id=report.report_id,
        priority=req.priority,
        title=title,
        instructions=instructions,
        due_date=req.due_date,
    )
    return create_task(db, admin_user, task_in)


def get_task(db: Session, task_id: int) -> Optional[CollectionTask]:
    statement = (
        select(CollectionTask)
        .options(
            joinedload(CollectionTask.collector),
            joinedload(CollectionTask.creator),
            joinedload(CollectionTask.bin).joinedload(Bin.location),
            joinedload(CollectionTask.location),
            joinedload(CollectionTask.report),
            joinedload(CollectionTask.collection_record),
        )
        .where(CollectionTask.task_id == task_id)
    )
    return db.scalar(statement)


def list_tasks(
    db: Session,
    current_user: User,
    collector_id: Optional[uuid.UUID] = None,
    status_filter: Optional[str] = None,
    task_type: Optional[str] = None,
    priority: Optional[str] = None,
    bin_id: Optional[uuid.UUID] = None,
    location_id: Optional[int] = None,
    report_id: Optional[int] = None,
    skip: int = 0,
    limit: int = 50,
) -> Tuple[List[CollectionTask], int]:
    base_query = (
        select(CollectionTask)
        .options(
            joinedload(CollectionTask.collector),
            joinedload(CollectionTask.creator),
            joinedload(CollectionTask.bin).joinedload(Bin.location),
            joinedload(CollectionTask.location),
            joinedload(CollectionTask.report),
            joinedload(CollectionTask.collection_record),
        )
        .order_by(
            # Sort: URGENT / HIGH first, then creation desc
            CollectionTask.created_at.desc()
        )
    )

    user_role = current_user.role.role_name.upper() if current_user.role else ""
    if user_role == "COLLECTOR":
        base_query = base_query.where(CollectionTask.collector_id == current_user.user_id)
    elif user_role == "ADMIN" and collector_id is not None:
        base_query = base_query.where(CollectionTask.collector_id == collector_id)

    if status_filter:
        base_query = base_query.where(CollectionTask.status == status_filter.strip().upper())
    if task_type:
        base_query = base_query.where(CollectionTask.task_type == task_type.strip().upper())
    if priority:
        base_query = base_query.where(CollectionTask.priority == priority.strip().upper())
    if bin_id:
        base_query = base_query.where(CollectionTask.bin_id == bin_id)
    if location_id:
        base_query = base_query.where(CollectionTask.location_id == location_id)
    if report_id:
        base_query = base_query.where(CollectionTask.report_id == report_id)

    # Total count query
    count_query = select(func.count(CollectionTask.task_id))
    if user_role == "COLLECTOR":
        count_query = count_query.where(CollectionTask.collector_id == current_user.user_id)
    elif user_role == "ADMIN" and collector_id is not None:
        count_query = count_query.where(CollectionTask.collector_id == collector_id)
    if status_filter:
        count_query = count_query.where(CollectionTask.status == status_filter.strip().upper())
    if task_type:
        count_query = count_query.where(CollectionTask.task_type == task_type.strip().upper())
    if priority:
        count_query = count_query.where(CollectionTask.priority == priority.strip().upper())
    if bin_id:
        count_query = count_query.where(CollectionTask.bin_id == bin_id)
    if location_id:
        count_query = count_query.where(CollectionTask.location_id == location_id)
    if report_id:
        count_query = count_query.where(CollectionTask.report_id == report_id)

    total = db.scalar(count_query) or 0
    tasks = list(db.scalars(base_query.offset(skip).limit(limit)).all())
    return tasks, total


def update_task_status(
    db: Session,
    current_user: User,
    task: CollectionTask,
    update_in: TaskStatusUpdate,
) -> CollectionTask:
    user_role = current_user.role.role_name.upper() if current_user.role else ""
    is_admin = user_role == "ADMIN"
    is_assigned_collector = task.collector_id == current_user.user_id

    # 1. Authorization: Only the assigned collector or admin can update status
    if not is_admin and not is_assigned_collector:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You are not authorized to modify tasks assigned to another collector.",
        )

    # 2. Cannot modify terminal tasks
    if task.status in {"COMPLETED", "CANCELLED"}:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Cannot change status of task #{task.task_id} because it is already {task.status}.",
        )

    target_status = update_in.status.strip().upper()
    now_utc = datetime.now(timezone.utc)

    # 3. Valid state transitions
    allowed_transitions = {
        "ASSIGNED": {"ACCEPTED", "IN_PROGRESS", "CANCELLED"},
        "ACCEPTED": {"IN_PROGRESS", "CANCELLED"},
        "IN_PROGRESS": {"COMPLETED", "CANCELLED"},
    }

    if target_status not in allowed_transitions.get(task.status, set()):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid transition from '{task.status}' to '{target_status}'.",
        )

    # 4. Action-specific validation
    if target_status == "IN_PROGRESS":
        if not task.started_at:
            task.started_at = now_utc

    elif target_status == "COMPLETED":
        # Check required evidence by task type
        if task.task_type == "COLLECTION":
            collection_record = None
            if update_in.collection_id:
                collection_record = db.get(CollectionRecord, update_in.collection_id)
            elif task.bin_id:
                # Find most recent collection record for this bin and collector
                collection_record = db.scalar(
                    select(CollectionRecord)
                    .where(
                        and_(
                            CollectionRecord.bin_id == task.bin_id,
                            CollectionRecord.collector_id == task.collector_id,
                            CollectionRecord.collected_at >= task.assigned_at,
                        )
                    )
                    .order_by(CollectionRecord.collected_at.desc())
                )

            if not collection_record:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Collection task requires a completed waste collection record as proof of work. Please scan the bin and log the collection first.",
                )
            task.collection_id = collection_record.collection_id

        elif task.task_type in {"INSPECTION", "ISSUE_RESPONSE"}:
            if not update_in.completion_notes or not update_in.completion_notes.strip():
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Completion notes are required to complete an {task.task_type} task.",
                )

        task.completed_at = now_utc
        task.completion_notes = update_in.completion_notes.strip() if update_in.completion_notes else None

    elif target_status == "CANCELLED":
        task.cancelled_at = now_utc
        task.cancellation_reason = update_in.cancellation_reason.strip() if update_in.cancellation_reason else "Cancelled by operator"

    task.status = target_status
    db.commit()
    db.refresh(task)
    return get_task(db, task.task_id) or task


def reassign_task(
    db: Session,
    admin_user: User,
    task: CollectionTask,
    reassign_in: TaskReassignRequest,
) -> CollectionTask:
    if task.status in {"COMPLETED", "CANCELLED"}:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Cannot reassign task #{task.task_id} because it is already {task.status}.",
        )

    new_collector = _get_verified_collector(db, reassign_in.new_collector_id)
    old_collector = task.collector

    now_utc = datetime.now(timezone.utc)
    audit_entry = (
        f"\n[Reassigned]: From {old_collector.name} to {new_collector.name} "
        f"on {now_utc.strftime('%Y-%m-%d %H:%M UTC')} by {admin_user.name}."
    )
    if reassign_in.instructions:
        audit_entry += f" Note: {reassign_in.instructions.strip()}"

    existing_instructions = task.instructions or ""
    task.instructions = f"{existing_instructions}{audit_entry}".strip()
    task.collector_id = new_collector.user_id
    task.status = "ASSIGNED"
    task.assigned_at = now_utc
    task.started_at = None

    if reassign_in.priority:
        task.priority = reassign_in.priority
    if reassign_in.due_date:
        task.due_date = reassign_in.due_date

    db.commit()
    db.refresh(task)

    # FCM Web Push notification trigger boundary for new collector (post-commit, safe)
    try:
        push_notification_service.send_task_reassignment_push(
            task=task,
            new_collector=new_collector,
            db=db,
        )
    except Exception as exc:
        logger.error(f"[Push Notification Failed] Task #{task.task_id} reassigned successfully but notification failed: {exc}")

    return get_task(db, task.task_id) or task


def cancel_task(
    db: Session,
    admin_user: User,
    task: CollectionTask,
    reason: Optional[str] = None,
) -> CollectionTask:
    if task.status in {"COMPLETED", "CANCELLED"}:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Task #{task.task_id} is already {task.status}.",
        )

    now_utc = datetime.now(timezone.utc)
    task.status = "CANCELLED"
    task.cancelled_at = now_utc
    task.cancellation_reason = reason.strip() if reason else f"Cancelled by admin {admin_user.name}"

    db.commit()
    db.refresh(task)
    return get_task(db, task.task_id) or task
