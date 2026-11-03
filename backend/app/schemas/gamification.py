import uuid
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict, Field, field_validator


class PointBalanceRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    user_id: uuid.UUID
    current_points: int
    total_earned: int
    total_redeemed: int


class PointTransactionRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    transaction_id: int
    user_id: uuid.UUID
    transaction_type: str
    points: int
    source_type: str
    source_id: Optional[int] = None
    description: Optional[str] = None
    created_at: datetime
    created_by: Optional[uuid.UUID] = None


class PointAdjustmentCreate(BaseModel):
    points: int = Field(
        ...,
        description="Point adjustment value (positive to award points, negative to deduct; cannot be zero)",
    )
    reason: str = Field(
        ...,
        min_length=1,
        description="Mandatory administrative justification for the point adjustment",
    )

    @field_validator("points")
    @classmethod
    def validate_points_not_zero(cls, v: int) -> int:
        if v == 0:
            raise ValueError("Adjustment points cannot be zero")
        return v

    @field_validator("reason")
    @classmethod
    def validate_reason_not_empty(cls, v: str) -> str:
        stripped = v.strip()
        if not stripped:
            raise ValueError("Adjustment reason cannot be empty")
        return stripped


class PointRuleRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    rule_id: int
    action_type: str
    points: int
    description: Optional[str] = None
    is_active: bool
    created_at: datetime
    updated_at: datetime


class RewardCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=150, description="Name of the reward")
    description: Optional[str] = Field(None, description="Detailed reward description")
    points_cost: int = Field(..., gt=0, description="Points cost to redeem (must be > 0)")
    stock_quantity: Optional[int] = Field(None, ge=0, description="Available stock quantity (null for unlimited)")
    is_active: Optional[bool] = Field(True, description="Whether reward is currently redeemable")


class RewardUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=150)
    description: Optional[str] = None
    points_cost: Optional[int] = Field(None, gt=0)
    stock_quantity: Optional[int] = Field(None, ge=0)
    is_active: Optional[bool] = None


class RewardRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    reward_id: int
    name: str
    description: Optional[str] = None
    points_cost: int
    stock_quantity: Optional[int] = None
    is_active: bool
    created_at: datetime
    updated_at: datetime


class RewardRedemptionRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    redemption_id: int
    reward_id: int
    reward_name: Optional[str] = None
    user_id: uuid.UUID
    points_spent: int
    remaining_points: Optional[int] = None
    status: str
    notes: Optional[str] = None
    redeemed_at: datetime
    fulfilled_at: Optional[datetime] = None
    cancelled_at: Optional[datetime] = None
    created_at: datetime


class EcoStageRead(BaseModel):
    stage_id: int
    stage_name: str
    description: str
    flair_icon: str
    color_hex: str
    min_points: int
    lifetime_earned_points: int
    next_stage_name: Optional[str] = None
    next_stage_min_points: Optional[int] = None
    points_to_next_stage: int
    progress_percentage: float
    is_max_stage: bool


class LeaderboardEntryRead(BaseModel):
    rank: int
    user_id: uuid.UUID
    display_name: str
    earned_points: int
    stage_name: str
    flair_icon: str
    color_hex: str
    is_current_user: bool = False


class UserRankRead(BaseModel):
    rank: int
    user_id: uuid.UUID
    display_name: str
    earned_points: int
    stage_name: str
    flair_icon: str
    color_hex: str


class LeaderboardResponseRead(BaseModel):
    period: str
    total_participants: int
    leaderboard: list[LeaderboardEntryRead]
    current_user_rank: Optional[UserRankRead] = None
