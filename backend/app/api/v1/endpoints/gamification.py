import uuid
from datetime import datetime
from typing import List, Optional
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.dependencies import get_current_active_user, require_roles
from app.models.user import User
from app.schemas.gamification import (
    EcoStageRead,
    LeaderboardResponseRead,
    PointAdjustmentCreate,
    PointBalanceRead,
    PointTransactionRead,
    RewardRedemptionRead,
)
from app.services import gamification_service

router = APIRouter()


@router.get(
    "/leaderboard",
    response_model=LeaderboardResponseRead,
    summary="Get Campus Student Leaderboard",
    description="Retrieve ranked student leaderboard based on cumulative lifetime EARN points with period filtering.",
)
def get_campus_leaderboard(
    period: str = Query("all-time", description="Leaderboard time window: 'all-time', 'month', 'week'"),
    limit: int = Query(50, ge=1, le=100, description="Max leaderboard entries to return"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> LeaderboardResponseRead:
    res = gamification_service.get_leaderboard(
        db=db,
        period=period,
        limit=limit,
        current_user_id=current_user.user_id,
    )
    return LeaderboardResponseRead(**res)


@router.get(
    "/me/stage",
    response_model=EcoStageRead,
    summary="Get My Eco Stage",
    description="Retrieve the authenticated user's current sustainability Eco Stage and progress milestone.",
)
def get_my_eco_stage(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> EcoStageRead:
    stage_data = gamification_service.get_user_stage(db, current_user.user_id)
    return EcoStageRead(**stage_data)


@router.get(
    "/stage",
    response_model=EcoStageRead,
    summary="Get My Eco Stage (Alias)",
    description="Alias endpoint to retrieve authenticated user's current sustainability Eco Stage.",
)
def get_my_eco_stage_alias(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> EcoStageRead:
    stage_data = gamification_service.get_user_stage(db, current_user.user_id)
    return EcoStageRead(**stage_data)


@router.get(
    "/me",
    response_model=PointBalanceRead,
    summary="Get My Point Balance",
    description="Retrieve the authenticated student's current point balance and historical earned/redeemed totals.",
)
def get_my_points(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles("STUDENT", "ADMIN")),
) -> PointBalanceRead:
    balance = gamification_service.get_user_point_balance(db, current_user.user_id)
    return PointBalanceRead(**balance)


@router.get(
    "/me/transactions",
    response_model=List[PointTransactionRead],
    summary="Get My Point Transactions",
    description="Retrieve the authenticated student's immutable point transaction ledger entries with pagination.",
)
def get_my_transactions(
    transaction_type: Optional[str] = Query(None, description="Filter by transaction type (EARN, REDEEM, ADJUSTMENT)"),
    start_date: Optional[datetime] = Query(None, description="Filter from timestamp"),
    end_date: Optional[datetime] = Query(None, description="Filter to timestamp"),
    skip: int = Query(0, ge=0, description="Number of transactions to skip"),
    limit: int = Query(50, ge=1, le=100, description="Max transactions to return"),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles("STUDENT", "ADMIN")),
) -> List[PointTransactionRead]:
    txns = gamification_service.list_user_transactions(
        db=db,
        user_id=current_user.user_id,
        transaction_type=transaction_type,
        start_date=start_date,
        end_date=end_date,
        skip=skip,
        limit=limit,
    )
    return [PointTransactionRead.model_validate(t) for t in txns]


@router.get(
    "/me/redemptions",
    response_model=List[RewardRedemptionRead],
    summary="Get My Reward Redemptions",
    description="Retrieve the authenticated student's reward redemption history.",
)
def get_my_redemptions(
    skip: int = Query(0, ge=0, description="Number of redemptions to skip"),
    limit: int = Query(50, ge=1, le=100, description="Max redemptions to return"),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles("STUDENT", "ADMIN")),
) -> List[RewardRedemptionRead]:
    redemptions = gamification_service.list_user_redemptions(
        db=db,
        user_id=current_user.user_id,
        skip=skip,
        limit=limit,
    )
    res = []
    for r in redemptions:
        data = RewardRedemptionRead.model_validate(r)
        if r.reward:
            data.reward_name = r.reward.name
        res.append(data)
    return res


@router.get(
    "/users/{user_id}",
    response_model=PointBalanceRead,
    summary="Get User Point Balance (Admin)",
    description="Inspect point balance and totals for any specific user (ADMIN only).",
)
def get_user_points_admin(
    user_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles("ADMIN")),
) -> PointBalanceRead:
    balance = gamification_service.get_user_point_balance(db, user_id)
    return PointBalanceRead(**balance)


@router.get(
    "/users/{user_id}/transactions",
    response_model=List[PointTransactionRead],
    summary="Get User Point Transactions (Admin)",
    description="Inspect point transaction ledger entries for a specific user (ADMIN only).",
)
def get_user_transactions_admin(
    user_id: uuid.UUID,
    transaction_type: Optional[str] = Query(None, description="Filter by transaction type"),
    start_date: Optional[datetime] = Query(None, description="Filter from timestamp"),
    end_date: Optional[datetime] = Query(None, description="Filter to timestamp"),
    skip: int = Query(0, ge=0, description="Number of items to skip"),
    limit: int = Query(50, ge=1, le=100, description="Max items to return"),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles("ADMIN")),
) -> List[PointTransactionRead]:
    txns = gamification_service.list_user_transactions(
        db=db,
        user_id=user_id,
        transaction_type=transaction_type,
        start_date=start_date,
        end_date=end_date,
        skip=skip,
        limit=limit,
    )
    return [PointTransactionRead.model_validate(t) for t in txns]


@router.post(
    "/users/{user_id}/adjust",
    response_model=PointTransactionRead,
    status_code=status.HTTP_201_CREATED,
    summary="Adjust User Points (Admin)",
    description="Manually adjust a user's point balance with an immutable administrative ledger entry (ADMIN only).",
)
def adjust_user_points(
    user_id: uuid.UUID,
    adjustment_in: PointAdjustmentCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles("ADMIN")),
) -> PointTransactionRead:
    txn = gamification_service.create_admin_adjustment(
        db=db,
        admin_user=current_user,
        target_user_id=user_id,
        adjustment_in=adjustment_in,
    )
    return PointTransactionRead.model_validate(txn)


@router.get(
    "/redemptions",
    response_model=List[RewardRedemptionRead],
    summary="List All Redemptions (Admin)",
    description="Retrieve all campus reward redemption requests platform-wide (ADMIN only).",
)
def list_all_redemptions_admin(
    skip: int = Query(0, ge=0, description="Number of redemptions to skip"),
    limit: int = Query(50, ge=1, le=100, description="Max redemptions to return"),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles("ADMIN")),
) -> List[RewardRedemptionRead]:
    redemptions = gamification_service.list_all_redemptions(
        db=db,
        skip=skip,
        limit=limit,
    )
    res = []
    for r in redemptions:
        data = RewardRedemptionRead.model_validate(r)
        if r.reward:
            data.reward_name = r.reward.name
        res.append(data)
    return res
