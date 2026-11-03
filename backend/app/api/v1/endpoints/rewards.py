from typing import List
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.dependencies import get_current_active_user, require_roles
from app.models.user import User
from app.schemas.gamification import (
    RewardCreate,
    RewardRead,
    RewardRedemptionRead,
    RewardUpdate,
)
from app.services import gamification_service

router = APIRouter()


@router.get(
    "",
    response_model=List[RewardRead],
    summary="List Rewards",
    description="Retrieve available rewards. Normal users view active rewards; Admins view all.",
)
def list_rewards(
    skip: int = Query(0, ge=0, description="Number of rewards to skip"),
    limit: int = Query(50, ge=1, le=100, description="Max rewards to return"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> List[RewardRead]:
    is_admin = bool(current_user.role and current_user.role.role_name.upper() == "ADMIN")
    rewards = gamification_service.list_rewards(
        db=db,
        is_admin=is_admin,
        skip=skip,
        limit=limit,
    )
    return [RewardRead.model_validate(r) for r in rewards]


@router.get(
    "/{reward_id}",
    response_model=RewardRead,
    summary="Get Reward by ID",
    description="Retrieve details of a specific reward.",
)
def get_reward(
    reward_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> RewardRead:
    reward = gamification_service.get_reward(db=db, reward_id=reward_id)
    if not reward:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Reward with ID {reward_id} not found",
        )
    return RewardRead.model_validate(reward)


@router.post(
    "",
    response_model=RewardRead,
    status_code=status.HTTP_201_CREATED,
    summary="Create Reward (Admin)",
    description="Create a new reward item redeemable by students with points (ADMIN only).",
)
def create_reward(
    reward_in: RewardCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles("ADMIN")),
) -> RewardRead:
    reward = gamification_service.create_reward(db=db, reward_in=reward_in)
    return RewardRead.model_validate(reward)


@router.patch(
    "/{reward_id}",
    response_model=RewardRead,
    summary="Update Reward (Admin)",
    description="Update reward details, price, inventory stock, or active status (ADMIN only).",
)
def update_reward(
    reward_id: int,
    reward_in: RewardUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles("ADMIN")),
) -> RewardRead:
    reward = gamification_service.update_reward(
        db=db,
        reward_id=reward_id,
        reward_in=reward_in,
    )
    return RewardRead.model_validate(reward)


@router.post(
    "/{reward_id}/redeem",
    response_model=RewardRedemptionRead,
    status_code=status.HTTP_201_CREATED,
    summary="Redeem Reward",
    description="Redeem a reward using earned student point balance (STUDENT only).",
)
def redeem_reward(
    reward_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles("STUDENT")),
) -> RewardRedemptionRead:
    redemption_data = gamification_service.redeem_reward(
        db=db,
        user=current_user,
        reward_id=reward_id,
    )
    return RewardRedemptionRead(**redemption_data)
