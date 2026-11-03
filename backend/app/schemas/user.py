import uuid
from datetime import datetime
from typing import Any, Optional
from pydantic import BaseModel, ConfigDict, EmailStr, field_validator

from app.core.phone_utils import normalize_phone_number


class RoleRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    role_id: int
    role_name: str
    description: Optional[str] = None


class AdminTestResponse(BaseModel):
    message: str
    admin_user: str
    timestamp: datetime


class UserBase(BaseModel):
    name: str
    email: EmailStr
    phone_number: Optional[str] = None

    @field_validator("phone_number", mode="before")
    @classmethod
    def validate_phone(cls, v: Any) -> Optional[str]:
        if v is None:
            return None
        return normalize_phone_number(str(v))


class UserCreate(UserBase):
    password: str
    role: str = "STUDENT"


class UserRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    user_id: uuid.UUID
    name: str
    email: str
    phone_number: Optional[str] = None
    role: str
    is_active: bool
    created_at: Optional[datetime] = None

    @field_validator("role", mode="before")
    @classmethod
    def extract_role_name(cls, value: Any) -> str:
        if hasattr(value, "role_name"):
            return str(value.role_name)
        return str(value)


class UserSummary(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    user_id: uuid.UUID
    name: str
    email: str
    phone_number: Optional[str] = None
    role: str
    is_active: bool

    @field_validator("role", mode="before")
    @classmethod
    def extract_role_name(cls, value: Any) -> str:
        if hasattr(value, "role_name"):
            return str(value.role_name)
        return str(value)


class AdminTestResponse(BaseModel):
    message: str
    admin_user: str
    timestamp: datetime


class AdminUserSummary(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    user_id: uuid.UUID
    name: str
    email: str
    phone_number: Optional[str] = None
    role: str
    is_active: bool
    total_earned_points: int = 0
    current_point_balance: int = 0
    stage_name: str = "Eco Seed"
    flair_icon: str = "seed"
    color_hex: str = "#10B981"
    created_at: datetime

    @field_validator("role", mode="before")
    @classmethod
    def extract_role_name(cls, value: Any) -> str:
        if hasattr(value, "role_name"):
            return str(value.role_name)
        return str(value)


class AdminUserCreate(BaseModel):
    name: str
    email: EmailStr
    password: str
    role: str = "STUDENT"
    is_active: bool = True
    phone_number: Optional[str] = None

    @field_validator("phone_number", mode="before")
    @classmethod
    def validate_phone(cls, v: Any) -> Optional[str]:
        if v is None:
            return None
        return normalize_phone_number(str(v))


class AdminUserUpdate(BaseModel):
    name: Optional[str] = None
    email: Optional[EmailStr] = None
    phone_number: Optional[str] = None
    role: Optional[str] = None
    is_active: Optional[bool] = None
    password: Optional[str] = None

    @field_validator("phone_number", mode="before")
    @classmethod
    def validate_phone(cls, v: Any) -> Optional[str]:
        if v is None:
            return None
        return normalize_phone_number(str(v))


class CollectorPhoneUpdate(BaseModel):
    phone_number: Optional[str] = None

    @field_validator("phone_number", mode="before")
    @classmethod
    def validate_phone(cls, v: Any) -> Optional[str]:
        if v is None:
            return None
        return normalize_phone_number(str(v))


class AdminUserDetail(BaseModel):
    user_id: uuid.UUID
    name: str
    email: str
    phone_number: Optional[str] = None
    role: str
    is_active: bool
    created_at: datetime
    total_earned_points: int
    total_redeemed_points: int
    current_point_balance: int
    stage: dict
    recent_transactions: list[dict]
    recent_redemptions: list[dict]
    total_disposals: int = 0
    total_reports: int = 0


class AdminUserListResponse(BaseModel):
    total_count: int
    users: list[AdminUserSummary]
