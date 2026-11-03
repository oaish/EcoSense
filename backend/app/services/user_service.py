import uuid
from datetime import datetime
from typing import Any, Dict, List, Optional
from fastapi import HTTPException, status
from sqlalchemy import func, or_, select
from sqlalchemy.orm import Session, joinedload

from app.core.gamification_config import calculate_eco_stage
from app.core.security import hash_password
from app.models.disposal import DisposalRecord
from app.models.gamification import PointTransaction, RewardRedemption
from app.models.report import WasteReport
from app.models.role import Role
from app.models.user import User
from app.schemas.user import AdminUserCreate, AdminUserDetail, AdminUserSummary, AdminUserUpdate
from app.services.auth_service import get_role_by_name, get_user_by_email, get_user_by_id


def list_users_admin(
    db: Session,
    search: Optional[str] = None,
    role_name: Optional[str] = None,
    is_active: Optional[bool] = None,
    skip: int = 0,
    limit: int = 50,
) -> Dict[str, Any]:
    """Retrieve users with search, role, and active status filters, alongside point totals."""
    # Base conditions
    conditions = []

    if search:
        s = f"%{search.strip().lower()}%"
        conditions.append(or_(func.lower(User.name).like(s), func.lower(User.email).like(s)))

    if role_name:
        role_obj = get_role_by_name(db, role_name)
        if role_obj:
            conditions.append(User.role_id == role_obj.role_id)
        else:
            return {"total_count": 0, "users": []}

    if is_active is not None:
        conditions.append(User.is_active.is_(is_active))

    # Total count query
    count_stmt = select(func.count(User.user_id)).where(*conditions)
    total_count = db.scalar(count_stmt) or 0

    # User rows query
    user_stmt = (
        select(User)
        .options(joinedload(User.role))
        .where(*conditions)
        .order_by(User.created_at.desc())
        .offset(skip)
        .limit(limit)
    )
    users = list(db.scalars(user_stmt).all())
    if not users:
        return {"total_count": total_count, "users": []}

    user_ids = [u.user_id for u in users]

    # Batch compute EARN and NET points for retrieved users
    earned_pts_map = dict(
        db.execute(
            select(
                PointTransaction.user_id,
                func.coalesce(func.sum(PointTransaction.points), 0),
            )
            .where(
                PointTransaction.user_id.in_(user_ids),
                PointTransaction.transaction_type == "EARN",
            )
            .group_by(PointTransaction.user_id)
        ).all()
    )

    balance_pts_map = dict(
        db.execute(
            select(
                PointTransaction.user_id,
                func.coalesce(func.sum(PointTransaction.points), 0),
            )
            .where(PointTransaction.user_id.in_(user_ids))
            .group_by(PointTransaction.user_id)
        ).all()
    )

    summary_list: List[AdminUserSummary] = []
    for u in users:
        tot_earned = int(earned_pts_map.get(u.user_id, 0))
        cur_bal = int(balance_pts_map.get(u.user_id, 0))
        stage_info = calculate_eco_stage(tot_earned)

        summary_list.append(
            AdminUserSummary(
                user_id=u.user_id,
                name=u.name,
                email=u.email,
                role=u.role.role_name if u.role else "STUDENT",
                is_active=u.is_active,
                total_earned_points=tot_earned,
                current_point_balance=cur_bal,
                stage_name=stage_info["stage_name"],
                flair_icon=stage_info["flair_icon"],
                color_hex=stage_info["color_hex"],
                created_at=u.created_at,
            )
        )

    return {"total_count": total_count, "users": summary_list}


def get_user_admin_detail(db: Session, user_id: uuid.UUID) -> AdminUserDetail:
    """Retrieve detailed user account metrics, recent transactions, and activity counts."""
    user = db.scalar(select(User).options(joinedload(User.role)).where(User.user_id == user_id))
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    # Point totals
    total_earned = db.scalar(
        select(func.coalesce(func.sum(PointTransaction.points), 0)).where(
            PointTransaction.user_id == user_id,
            PointTransaction.transaction_type == "EARN",
        )
    ) or 0

    total_redeemed = db.scalar(
        select(func.coalesce(func.sum(PointTransaction.points), 0)).where(
            PointTransaction.user_id == user_id,
            PointTransaction.transaction_type == "REDEEM",
        )
    ) or 0

    current_balance = db.scalar(
        select(func.coalesce(func.sum(PointTransaction.points), 0)).where(
            PointTransaction.user_id == user_id,
        )
    ) or 0

    stage_info = calculate_eco_stage(int(total_earned))

    # Activity counts
    disposal_count = db.scalar(
        select(func.count(DisposalRecord.disposal_id)).where(DisposalRecord.user_id == user_id)
    ) or 0

    report_count = db.scalar(
        select(func.count(WasteReport.report_id)).where(WasteReport.user_id == user_id)
    ) or 0

    # Recent transactions (up to 10)
    txns = list(
        db.scalars(
            select(PointTransaction)
            .where(PointTransaction.user_id == user_id)
            .order_by(PointTransaction.created_at.desc())
            .limit(10)
        ).all()
    )
    recent_txns = [
        {
            "transaction_id": t.transaction_id,
            "transaction_type": t.transaction_type,
            "points": t.points,
            "source_type": t.source_type,
            "description": t.description,
            "created_at": t.created_at.isoformat() if t.created_at else None,
        }
        for t in txns
    ]

    # Recent redemptions (up to 10)
    redemptions = list(
        db.scalars(
            select(RewardRedemption)
            .options(joinedload(RewardRedemption.reward))
            .where(RewardRedemption.user_id == user_id)
            .order_by(RewardRedemption.redeemed_at.desc())
            .limit(10)
        ).all()
    )
    recent_reds = [
        {
            "redemption_id": r.redemption_id,
            "reward_name": r.reward.name if r.reward else "Reward",
            "points_spent": r.points_spent,
            "status": r.status,
            "redeemed_at": r.redeemed_at.isoformat() if r.redeemed_at else None,
        }
        for r in redemptions
    ]

    return AdminUserDetail(
        user_id=user.user_id,
        name=user.name,
        email=user.email,
        role=user.role.role_name if user.role else "STUDENT",
        is_active=user.is_active,
        created_at=user.created_at,
        total_earned_points=int(total_earned),
        total_redeemed_points=abs(int(total_redeemed)),
        current_point_balance=int(current_balance),
        stage=stage_info,
        recent_transactions=recent_txns,
        recent_redemptions=recent_reds,
        total_disposals=disposal_count,
        total_reports=report_count,
    )


def create_admin_user(db: Session, data: AdminUserCreate) -> User:
    """Create a new user account with hashed password and assigned role."""
    norm_email = data.email.strip().lower()
    existing = get_user_by_email(db, norm_email)
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"User with email '{norm_email}' already exists.",
        )

    role_obj = get_role_by_name(db, data.role)
    if not role_obj:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid role '{data.role}'. Allowed roles: STUDENT, STAFF, COLLECTOR, ADMIN",
        )

    user = User(
        name=data.name.strip(),
        email=norm_email,
        phone_number=data.phone_number,
        password_hash=hash_password(data.password),
        role_id=role_obj.role_id,
        is_active=data.is_active,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def update_admin_user(db: Session, user_id: uuid.UUID, data: AdminUserUpdate) -> User:
    """Update user account details, role, active status, phone, or password."""
    user = db.scalar(select(User).options(joinedload(User.role)).where(User.user_id == user_id))
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    if data.email is not None:
        norm_email = data.email.strip().lower()
        if norm_email != user.email:
            existing = get_user_by_email(db, norm_email)
            if existing:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Email '{norm_email}' is already taken.",
                )
            user.email = norm_email

    if data.name is not None and data.name.strip():
        user.name = data.name.strip()

    if "phone_number" in data.model_fields_set:
        user.phone_number = data.phone_number

    if data.role is not None:
        role_obj = get_role_by_name(db, data.role)
        if not role_obj:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid role '{data.role}'.",
            )
        user.role_id = role_obj.role_id

    if data.is_active is not None:
        user.is_active = data.is_active

    if data.password is not None and len(data.password) >= 8:
        user.password_hash = hash_password(data.password)

    db.commit()
    db.refresh(user)
    return user


def update_user_phone(db: Session, user_id: uuid.UUID, phone_number: Optional[str]) -> User:
    """Administratively updates or removes a user's phone number."""
    user = db.scalar(select(User).options(joinedload(User.role)).where(User.user_id == user_id))
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    user.phone_number = phone_number
    db.commit()
    db.refresh(user)
    return user

