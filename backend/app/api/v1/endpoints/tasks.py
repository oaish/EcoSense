import uuid
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.dependencies import get_current_active_user, require_roles
from app.models.user import User
from app.schemas.task import (
    TaskCreate,
    TaskDelegateReportRequest,
    TaskListResponse,
    TaskRead,
    TaskReassignRequest,
    TaskStatusUpdate,
)
from app.services import task_service

router = APIRouter()


@router.post(
    "",
    response_model=TaskRead,
    status_code=status.HTTP_201_CREATED,
    summary="Create & Assign Collection Task",
    description="Assign a collection, inspection, or issue response task to an active collector (ADMIN only).",
)
def create_task_endpoint(
    task_in: TaskCreate,
    db: Session = Depends(get_db),
    admin_user: User = Depends(require_roles("ADMIN")),
) -> TaskRead:
    task = task_service.create_task(db=db, admin_user=admin_user, task_in=task_in)
    return TaskRead.model_validate(task)


@router.post(
    "/delegate-report",
    response_model=TaskRead,
    status_code=status.HTTP_201_CREATED,
    summary="Delegate Waste Report to Collector",
    description="Delegate an existing campus waste report to an active collector as an ISSUE_RESPONSE task (ADMIN only).",
)
def delegate_report_endpoint(
    req: TaskDelegateReportRequest,
    db: Session = Depends(get_db),
    admin_user: User = Depends(require_roles("ADMIN")),
) -> TaskRead:
    task = task_service.delegate_report_to_collector(db=db, admin_user=admin_user, req=req)
    return TaskRead.model_validate(task)


@router.get(
    "",
    response_model=TaskListResponse,
    summary="List Collection Tasks",
    description="Query tasks with filters. Collectors view their own tasks; Admins view all campus tasks.",
)
def list_tasks_endpoint(
    collector_id: Optional[uuid.UUID] = Query(None, description="Filter by collector UUID (Admin only)"),
    status: Optional[str] = Query(None, description="Filter by status: ASSIGNED, ACCEPTED, IN_PROGRESS, COMPLETED, CANCELLED"),
    task_type: Optional[str] = Query(None, description="Filter by task type: COLLECTION, INSPECTION, ISSUE_RESPONSE"),
    priority: Optional[str] = Query(None, description="Filter by priority: LOW, MEDIUM, HIGH, URGENT"),
    bin_id: Optional[uuid.UUID] = Query(None, description="Filter by bin UUID"),
    location_id: Optional[int] = Query(None, description="Filter by location ID"),
    report_id: Optional[int] = Query(None, description="Filter by linked report ID"),
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles("COLLECTOR", "ADMIN")),
) -> TaskListResponse:
    tasks, total = task_service.list_tasks(
        db=db,
        current_user=current_user,
        collector_id=collector_id,
        status_filter=status,
        task_type=task_type,
        priority=priority,
        bin_id=bin_id,
        location_id=location_id,
        report_id=report_id,
        skip=skip,
        limit=limit,
    )
    return TaskListResponse(
        total_count=total,
        tasks=[TaskRead.model_validate(t) for t in tasks],
    )


@router.get(
    "/me",
    response_model=TaskListResponse,
    summary="Get My Assigned Tasks",
    description="Retrieve all tasks assigned to the authenticated collector.",
)
@router.get(
    "/my",
    response_model=TaskListResponse,
    summary="Get My Assigned Tasks (legacy alias)",
    description="Retrieve all tasks assigned to the authenticated collector.",
)
def get_my_tasks_endpoint(
    status: Optional[str] = Query(None, description="Filter by status"),
    task_type: Optional[str] = Query(None, description="Filter by task type"),
    priority: Optional[str] = Query(None, description="Filter by priority"),
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles("COLLECTOR", "ADMIN")),
) -> TaskListResponse:
    tasks, total = task_service.list_tasks(
        db=db,
        current_user=current_user,
        collector_id=current_user.user_id,
        status_filter=status,
        task_type=task_type,
        priority=priority,
        skip=skip,
        limit=limit,
    )
    return TaskListResponse(
        total_count=total,
        tasks=[TaskRead.model_validate(t) for t in tasks],
    )


@router.get(
    "/{task_id}",
    response_model=TaskRead,
    summary="Get Task Details by ID",
    description="Retrieve details of a specific collection task.",
)
def get_task_endpoint(
    task_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles("COLLECTOR", "ADMIN")),
) -> TaskRead:
    task = task_service.get_task(db=db, task_id=task_id)
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Task #{task_id} not found.",
        )

    user_role = current_user.role.role_name.upper() if current_user.role else ""
    if user_role == "COLLECTOR" and task.collector_id != current_user.user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You are not authorized to view tasks assigned to another collector.",
        )

    return TaskRead.model_validate(task)


@router.patch(
    "/{task_id}/status",
    response_model=TaskRead,
    summary="Update Task Progress / Completion",
    description="Update task status (ACCEPTED, IN_PROGRESS, COMPLETED, CANCELLED). Verifies proof of collection for COLLECTION tasks.",
)
def update_task_status_endpoint(
    task_id: int,
    update_in: TaskStatusUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles("COLLECTOR", "ADMIN")),
) -> TaskRead:
    task = task_service.get_task(db=db, task_id=task_id)
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Task #{task_id} not found.",
        )

    updated = task_service.update_task_status(
        db=db,
        current_user=current_user,
        task=task,
        update_in=update_in,
    )
    return TaskRead.model_validate(updated)


@router.post(
    "/{task_id}/reassign",
    response_model=TaskRead,
    summary="Reassign Task to Another Collector",
    description="Reassign an active task to a different active collector (ADMIN only).",
)
def reassign_task_endpoint(
    task_id: int,
    reassign_in: TaskReassignRequest,
    db: Session = Depends(get_db),
    admin_user: User = Depends(require_roles("ADMIN")),
) -> TaskRead:
    task = task_service.get_task(db=db, task_id=task_id)
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Task #{task_id} not found.",
        )

    reassigned = task_service.reassign_task(
        db=db,
        admin_user=admin_user,
        task=task,
        reassign_in=reassign_in,
    )
    return TaskRead.model_validate(reassigned)


@router.post(
    "/{task_id}/cancel",
    response_model=TaskRead,
    summary="Cancel Task",
    description="Cancel an incomplete task with reason (ADMIN only).",
)
def cancel_task_endpoint(
    task_id: int,
    reason: Optional[str] = Query(None, description="Cancellation reason"),
    db: Session = Depends(get_db),
    admin_user: User = Depends(require_roles("ADMIN")),
) -> TaskRead:
    task = task_service.get_task(db=db, task_id=task_id)
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Task #{task_id} not found.",
        )

    cancelled = task_service.cancel_task(
        db=db,
        admin_user=admin_user,
        task=task,
        reason=reason,
    )
    return TaskRead.model_validate(cancelled)
