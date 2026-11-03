import uuid
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.dependencies import get_current_active_user, require_roles
from app.models.user import User
from app.schemas.report import ReportCreate, ReportRead, ReportUpdate
from app.services import report_service

router = APIRouter()


@router.post(
    "",
    response_model=ReportRead,
    status_code=status.HTTP_201_CREATED,
    summary="Submit Waste Issue Report",
    description="Submit an issue report regarding a bin (overflowing, damaged, missing, wrong segregation) or general campus waste issue (All authenticated roles).",
)
def submit_report(
    report_in: ReportCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> ReportRead:
    report = report_service.create_report(
        db=db,
        user=current_user,
        report_in=report_in,
    )
    return ReportRead.model_validate(report)


@router.get(
    "",
    response_model=List[ReportRead],
    summary="List Waste Issue Reports",
    description="Retrieve submitted waste problem reports. Students/Staff see their own; Admins and Collectors see all campus reports.",
)
def list_reports(
    status_filter: Optional[str] = Query(None, alias="status", description="Filter by status (PENDING, IN_PROGRESS, RESOLVED, REJECTED)"),
    report_type: Optional[str] = Query(None, description="Filter by report type"),
    bin_id: Optional[uuid.UUID] = Query(None, description="Filter by bin ID"),
    user_id: Optional[uuid.UUID] = Query(None, description="Filter by reporting user ID (Admin/Collector only)"),
    skip: int = Query(0, ge=0, description="Number of items to skip"),
    limit: int = Query(50, ge=1, le=100, description="Max items to return"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> List[ReportRead]:
    reports = report_service.list_reports(
        db=db,
        current_user=current_user,
        status_filter=status_filter,
        report_type=report_type,
        bin_id=bin_id,
        user_id=user_id,
        skip=skip,
        limit=limit,
    )
    return [ReportRead.model_validate(r) for r in reports]


@router.get(
    "/{report_id}",
    response_model=ReportRead,
    summary="Get Report by ID",
    description="Retrieve detailed status and timeline for a specific problem report.",
)
def get_report(
    report_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> ReportRead:
    report = report_service.get_report(db=db, report_id=report_id)
    if not report:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Report with ID {report_id} not found",
        )

    user_role = current_user.role.role_name.upper() if current_user.role else ""
    if user_role in {"STUDENT", "STAFF"} and report.user_id != current_user.user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Operation not permitted",
        )

    return ReportRead.model_validate(report)


@router.patch(
    "/{report_id}",
    response_model=ReportRead,
    summary="Update Report Status",
    description="Update problem report review status (IN_PROGRESS, RESOLVED, REJECTED) and automatically record resolver metadata (ADMIN only).",
)
def update_report(
    report_id: int,
    report_in: ReportUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles("ADMIN")),
) -> ReportRead:
    report = report_service.get_report(db=db, report_id=report_id)
    if not report:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Report with ID {report_id} not found",
        )

    updated = report_service.update_report(
        db=db,
        report=report,
        report_in=report_in,
        admin_user=current_user,
    )
    return ReportRead.model_validate(updated)
