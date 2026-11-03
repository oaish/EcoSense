import uuid
from datetime import datetime, timezone
from typing import List, Optional
from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session, joinedload

from app.models.bin import Bin
from app.models.report import WasteReport
from app.models.user import User
from app.schemas.report import ReportCreate, ReportUpdate


import logging

logger = logging.getLogger(__name__)


def create_report(
    db: Session,
    user: User,
    report_in: ReportCreate,
) -> WasteReport:
    bin_obj = None
    if report_in.bin_id is not None:
        bin_obj = db.get(Bin, report_in.bin_id)
        if not bin_obj:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Bin with ID {report_in.bin_id} not found",
            )

    report = WasteReport(
        user_id=user.user_id,
        bin_id=report_in.bin_id,
        report_type=report_in.report_type.strip().upper(),
        description=report_in.description.strip() if report_in.description else None,
        image_url=report_in.image_url.strip() if report_in.image_url else None,
        status="PENDING",
    )
    db.add(report)
    db.commit()
    db.refresh(report)

    # Notify admins for urgent reports (overflowing, damaged, missing) post-commit
    if report.report_type in {"OVERFLOWING", "DAMAGED_BIN", "MISSING_BIN"}:
        try:
            from app.services.push_notification_service import push_notification_service
            push_notification_service.send_urgent_report_admin_push(
                report=report,
                reporter=user,
                db=db,
            )
        except Exception as exc:
            logger.warning(f"Could not dispatch admin urgent report push notification: {exc}")

    return report


def get_report(db: Session, report_id: int) -> Optional[WasteReport]:
    statement = (
        select(WasteReport)
        .options(
            joinedload(WasteReport.bin),
            joinedload(WasteReport.user),
            joinedload(WasteReport.resolver),
        )
        .where(WasteReport.report_id == report_id)
    )
    return db.scalar(statement)


def list_reports(
    db: Session,
    current_user: User,
    status_filter: Optional[str] = None,
    report_type: Optional[str] = None,
    bin_id: Optional[uuid.UUID] = None,
    user_id: Optional[uuid.UUID] = None,
    skip: int = 0,
    limit: int = 50,
) -> List[WasteReport]:
    statement = (
        select(WasteReport)
        .options(
            joinedload(WasteReport.bin),
            joinedload(WasteReport.user),
            joinedload(WasteReport.resolver),
        )
        .order_by(WasteReport.created_at.desc())
    )

    user_role = current_user.role.role_name.upper() if current_user.role else ""

    # Students and Staff only see their own submitted reports
    if user_role in {"STUDENT", "STAFF"}:
        statement = statement.where(WasteReport.user_id == current_user.user_id)
    elif user_role in {"ADMIN", "COLLECTOR"} and user_id is not None:
        statement = statement.where(WasteReport.user_id == user_id)

    if status_filter is not None:
        statement = statement.where(WasteReport.status == status_filter.strip().upper())

    if report_type is not None:
        statement = statement.where(WasteReport.report_type == report_type.strip().upper())

    if bin_id is not None:
        statement = statement.where(WasteReport.bin_id == bin_id)

    statement = statement.offset(skip).limit(limit)
    return list(db.scalars(statement).all())


def update_report(
    db: Session,
    report: WasteReport,
    report_in: ReportUpdate,
    admin_user: User,
) -> WasteReport:
    if report_in.description is not None:
        report.description = report_in.description.strip()

    status_changed = False
    new_status = None
    if report_in.status is not None:
        new_status = report_in.status.strip().upper()
        if new_status != report.status:
            status_changed = True
        report.status = new_status
        if new_status == "RESOLVED":
            report.resolved_at = datetime.now(timezone.utc)
            report.resolved_by = admin_user.user_id

            # Atomically award points in the immutable ledger for verified and resolved report
            from app.services.gamification_service import award_points_for_report

            award_points_for_report(db, admin_user, report)
        else:
            report.resolved_at = None
            report.resolved_by = None

    db.commit()
    db.refresh(report)

    # Post-commit notification to original reporter if status changed
    if status_changed and new_status and report.user:
        try:
            from app.services.push_notification_service import push_notification_service
            push_notification_service.send_report_status_push(
                report=report,
                recipient=report.user,
                new_status=new_status,
                db=db,
            )
        except Exception as exc:
            logger.warning(f"Could not dispatch report status push notification: {exc}")

    return report
