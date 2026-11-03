import uuid
from datetime import datetime, timedelta, timezone
from typing import Any, Dict, List, Optional
from fastapi import HTTPException, status
from sqlalchemy import func, select
from sqlalchemy.orm import Session, joinedload

from app.core.gamification_config import calculate_eco_stage
from app.models.disposal import DisposalRecord
from app.models.gamification import PointRule, PointTransaction, Reward, RewardRedemption
from app.models.report import WasteReport
from app.models.role import Role
from app.models.user import User
from app.schemas.gamification import PointAdjustmentCreate, RewardCreate, RewardUpdate


def get_user_point_balance(db: Session, user_id: uuid.UUID) -> Dict[str, Any]:
    # Compute totals from the immutable point ledger
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

    current_points = db.scalar(
        select(func.coalesce(func.sum(PointTransaction.points), 0)).where(
            PointTransaction.user_id == user_id,
        )
    ) or 0

    return {
        "user_id": user_id,
        "current_points": current_points,
        "total_earned": total_earned,
        "total_redeemed": abs(total_redeemed),
    }


def award_points_for_disposal(
    db: Session,
    user: User,
    disposal: DisposalRecord,
) -> Optional[PointTransaction]:
    # 1. Anti-duplication check: verify points haven't already been awarded for this disposal
    existing_txn = db.scalar(
        select(PointTransaction).where(
            PointTransaction.source_type == "DISPOSAL",
            PointTransaction.source_id == disposal.disposal_id,
            PointTransaction.transaction_type == "EARN",
        )
    )
    if existing_txn:
        return existing_txn

    # 2. Lookup active rule for DISPOSAL
    rule = db.scalar(
        select(PointRule).where(
            PointRule.action_type == "DISPOSAL",
            PointRule.is_active == True,
        )
    )
    if not rule or rule.points <= 0:
        return None

    # 3. Create immutable ledger EARN entry
    txn = PointTransaction(
        user_id=user.user_id,
        transaction_type="EARN",
        points=rule.points,
        source_type="DISPOSAL",
        source_id=disposal.disposal_id,
        description=f"Points awarded for valid waste disposal (#{disposal.disposal_id})",
        created_by=user.user_id,
    )
    db.add(txn)
    return txn


def award_points_for_report(
    db: Session,
    admin_user: User,
    report: WasteReport,
) -> Optional[PointTransaction]:
    # 1. Anti-duplication check: verify points haven't already been awarded for this report
    existing_txn = db.scalar(
        select(PointTransaction).where(
            PointTransaction.source_type == "REPORT",
            PointTransaction.source_id == report.report_id,
            PointTransaction.transaction_type == "EARN",
        )
    )
    if existing_txn:
        return existing_txn

    # 2. Lookup active rule for WASTE_REPORT
    rule = db.scalar(
        select(PointRule).where(
            PointRule.action_type == "WASTE_REPORT",
            PointRule.is_active == True,
        )
    )
    if not rule or rule.points <= 0:
        return None

    # 3. Create immutable ledger EARN entry for the student/user who reported the issue
    txn = PointTransaction(
        user_id=report.user_id,
        transaction_type="EARN",
        points=rule.points,
        source_type="REPORT",
        source_id=report.report_id,
        description=f"Points awarded for verified and resolved waste report (#{report.report_id})",
        created_by=admin_user.user_id,
    )
    db.add(txn)
    return txn


def create_admin_adjustment(
    db: Session,
    admin_user: User,
    target_user_id: uuid.UUID,
    adjustment_in: PointAdjustmentCreate,
) -> PointTransaction:
    target_user = db.get(User, target_user_id)
    if not target_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with ID {target_user_id} not found",
        )

    txn = PointTransaction(
        user_id=target_user.user_id,
        transaction_type="ADJUSTMENT",
        points=adjustment_in.points,
        source_type="ADMIN_ADJUSTMENT",
        source_id=None,
        description=adjustment_in.reason,
        created_by=admin_user.user_id,
    )
    db.add(txn)
    db.commit()
    db.refresh(txn)
    return txn


def list_user_transactions(
    db: Session,
    user_id: uuid.UUID,
    transaction_type: Optional[str] = None,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    skip: int = 0,
    limit: int = 50,
) -> List[PointTransaction]:
    statement = (
        select(PointTransaction)
        .where(PointTransaction.user_id == user_id)
        .order_by(PointTransaction.created_at.desc())
    )

    if transaction_type:
        statement = statement.where(
            PointTransaction.transaction_type == transaction_type.strip().upper()
        )

    if start_date is not None:
        statement = statement.where(PointTransaction.created_at >= start_date)

    if end_date is not None:
        statement = statement.where(PointTransaction.created_at <= end_date)

    statement = statement.offset(skip).limit(limit)
    return list(db.scalars(statement).all())


def create_reward(db: Session, reward_in: RewardCreate) -> Reward:
    reward = Reward(
        name=reward_in.name.strip(),
        description=reward_in.description.strip() if reward_in.description else None,
        points_cost=reward_in.points_cost,
        stock_quantity=reward_in.stock_quantity,
        is_active=reward_in.is_active if reward_in.is_active is not None else True,
    )
    db.add(reward)
    db.commit()
    db.refresh(reward)
    return reward


def update_reward(
    db: Session,
    reward_id: int,
    reward_in: RewardUpdate,
) -> Reward:
    reward = db.get(Reward, reward_id)
    if not reward:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Reward with ID {reward_id} not found",
        )

    if reward_in.name is not None:
        reward.name = reward_in.name.strip()
    if reward_in.description is not None:
        reward.description = reward_in.description.strip()
    if reward_in.points_cost is not None:
        reward.points_cost = reward_in.points_cost
    if reward_in.stock_quantity is not None:
        reward.stock_quantity = reward_in.stock_quantity
    if reward_in.is_active is not None:
        reward.is_active = reward_in.is_active

    db.commit()
    db.refresh(reward)
    return reward


def list_rewards(
    db: Session,
    is_admin: bool = False,
    skip: int = 0,
    limit: int = 50,
) -> List[Reward]:
    statement = select(Reward).order_by(Reward.created_at.asc())
    if not is_admin:
        statement = statement.where(Reward.is_active == True)
    statement = statement.offset(skip).limit(limit)
    return list(db.scalars(statement).all())


def get_reward(db: Session, reward_id: int) -> Optional[Reward]:
    return db.get(Reward, reward_id)


def redeem_reward(
    db: Session,
    user: User,
    reward_id: int,
) -> Dict[str, Any]:
    # 1. Fetch reward
    reward = db.get(Reward, reward_id)
    if not reward:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Reward with ID {reward_id} not found",
        )

    if not reward.is_active:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Reward is currently inactive and cannot be redeemed.",
        )

    # 2. Check stock availability if finite
    if reward.stock_quantity is not None and reward.stock_quantity <= 0:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Reward is out of stock.",
        )

    # 3. Calculate current point balance from ledger
    balance_info = get_user_point_balance(db, user.user_id)
    current_points = balance_info["current_points"]
    if current_points < reward.points_cost:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"Insufficient points balance ({current_points} points). Required: {reward.points_cost} points.",
        )

    # 4. Decrease stock if applicable
    if reward.stock_quantity is not None:
        reward.stock_quantity -= 1

    # 5. Create redemption record
    redemption = RewardRedemption(
        reward_id=reward.reward_id,
        user_id=user.user_id,
        points_spent=reward.points_cost,
        status="PENDING",
    )
    db.add(redemption)
    db.flush()

    # 6. Create immutable REDEEM ledger entry
    point_txn = PointTransaction(
        user_id=user.user_id,
        transaction_type="REDEEM",
        points=-reward.points_cost,
        source_type="REWARD_REDEMPTION",
        source_id=redemption.redemption_id,
        description=f"Redeemed reward: {reward.name}",
        created_by=user.user_id,
    )
    db.add(point_txn)

    # 7. Commit atomically
    db.commit()
    db.refresh(redemption)

    remaining_points = current_points - reward.points_cost
    return {
        "redemption_id": redemption.redemption_id,
        "reward_id": reward.reward_id,
        "reward_name": reward.name,
        "user_id": user.user_id,
        "points_spent": redemption.points_spent,
        "remaining_points": remaining_points,
        "status": redemption.status,
        "notes": redemption.notes,
        "redeemed_at": redemption.redeemed_at,
        "fulfilled_at": redemption.fulfilled_at,
        "cancelled_at": redemption.cancelled_at,
        "created_at": redemption.created_at,
    }


def list_user_redemptions(
    db: Session,
    user_id: uuid.UUID,
    skip: int = 0,
    limit: int = 50,
) -> List[RewardRedemption]:
    statement = (
        select(RewardRedemption)
        .options(joinedload(RewardRedemption.reward))
        .where(RewardRedemption.user_id == user_id)
        .order_by(RewardRedemption.redeemed_at.desc())
        .offset(skip)
        .limit(limit)
    )
    return list(db.scalars(statement).all())


def list_all_redemptions(
    db: Session,
    skip: int = 0,
    limit: int = 50,
) -> List[RewardRedemption]:
    statement = (
        select(RewardRedemption)
        .options(
            joinedload(RewardRedemption.reward),
            joinedload(RewardRedemption.user),
        )
        .order_by(RewardRedemption.redeemed_at.desc())
        .offset(skip)
        .limit(limit)
    )
    return list(db.scalars(statement).all())


def get_user_stage(db: Session, user_id: uuid.UUID) -> Dict[str, Any]:
    """Retrieve the computed Eco Stage and milestone progression for a user based on lifetime EARN points."""
    total_earned = db.scalar(
        select(func.coalesce(func.sum(PointTransaction.points), 0)).where(
            PointTransaction.user_id == user_id,
            PointTransaction.transaction_type == "EARN",
        )
    ) or 0
    return calculate_eco_stage(int(total_earned))


def get_leaderboard(
    db: Session,
    period: str = "all-time",
    limit: int = 50,
    current_user_id: Optional[uuid.UUID] = None,
) -> Dict[str, Any]:
    """Calculate the campus student leaderboard based on cumulative EARN points in the selected period."""
    norm_period = (period or "all-time").lower().strip()
    if norm_period not in ("all-time", "month", "week"):
        norm_period = "all-time"

    now_utc = datetime.now(timezone.utc)
    date_filter = None
    if norm_period == "week":
        date_filter = now_utc - timedelta(days=7)
    elif norm_period == "month":
        date_filter = now_utc - timedelta(days=30)

    conditions = [
        Role.role_name == "STUDENT",
        User.is_active.is_(True),
        PointTransaction.transaction_type == "EARN",
    ]
    if date_filter is not None:
        conditions.append(PointTransaction.created_at >= date_filter)

    period_points_subq = (
        select(
            User.user_id.label("user_id"),
            User.name.label("name"),
            User.created_at.label("user_created_at"),
            func.coalesce(func.sum(PointTransaction.points), 0).label("earned_points"),
        )
        .join(Role, User.role_id == Role.role_id)
        .join(PointTransaction, User.user_id == PointTransaction.user_id)
        .where(*conditions)
        .group_by(User.user_id, User.name, User.created_at)
        .subquery()
    )

    ranked_query = (
        select(
            period_points_subq.c.user_id,
            period_points_subq.c.name,
            period_points_subq.c.earned_points,
        )
        .order_by(
            period_points_subq.c.earned_points.desc(),
            period_points_subq.c.user_created_at.asc(),
        )
    )

    all_ranked_rows = db.execute(ranked_query).all()
    total_participants = len(all_ranked_rows)

    lifetime_points_map = dict(
        db.execute(
            select(
                PointTransaction.user_id,
                func.coalesce(func.sum(PointTransaction.points), 0),
            )
            .where(PointTransaction.transaction_type == "EARN")
            .group_by(PointTransaction.user_id)
        ).all()
    )

    leaderboard_entries = []
    current_user_rank_entry = None

    for rank_idx, row in enumerate(all_ranked_rows, start=1):
        uid = row.user_id
        name = row.name
        pts = int(row.earned_points)
        lifetime_pts = int(lifetime_points_map.get(uid, pts))
        stage_info = calculate_eco_stage(lifetime_pts)

        is_curr = (current_user_id is not None and uid == current_user_id)

        entry_dict = {
            "rank": rank_idx,
            "user_id": uid,
            "display_name": name,
            "earned_points": pts,
            "stage_name": stage_info["stage_name"],
            "flair_icon": stage_info["flair_icon"],
            "color_hex": stage_info["color_hex"],
            "is_current_user": is_curr,
        }

        if rank_idx <= limit:
            leaderboard_entries.append(entry_dict)

        if is_curr:
            current_user_rank_entry = {
                "rank": rank_idx,
                "user_id": uid,
                "display_name": name,
                "earned_points": pts,
                "stage_name": stage_info["stage_name"],
                "flair_icon": stage_info["flair_icon"],
                "color_hex": stage_info["color_hex"],
            }

    if current_user_id is not None and current_user_rank_entry is None:
        curr_user = db.scalar(select(User).options(joinedload(User.role)).where(User.user_id == current_user_id))
        if curr_user and curr_user.role and curr_user.role.role_name == "STUDENT":
            lifetime_pts = int(lifetime_points_map.get(current_user_id, 0))
            stage_info = calculate_eco_stage(lifetime_pts)
            current_user_rank_entry = {
                "rank": total_participants + 1,
                "user_id": current_user_id,
                "display_name": curr_user.name,
                "earned_points": 0,
                "stage_name": stage_info["stage_name"],
                "flair_icon": stage_info["flair_icon"],
                "color_hex": stage_info["color_hex"],
            }

    return {
        "period": norm_period,
        "total_participants": total_participants,
        "leaderboard": leaderboard_entries,
        "current_user_rank": current_user_rank_entry,
    }

