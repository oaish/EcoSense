import uuid
from datetime import date, datetime
from typing import Any, List, Optional
from pydantic import BaseModel, ConfigDict, Field, model_validator


class AttendanceCheckInRequest(BaseModel):
    notes: Optional[str] = Field(None, max_length=500, description="Optional check-in notes or shift remarks")


class AttendanceCheckOutRequest(BaseModel):
    notes: Optional[str] = Field(None, max_length=500, description="Optional check-out handoff notes")


class AttendanceRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    attendance_id: int
    collector_id: uuid.UUID
    collector_name: Optional[str] = None
    collector_email: Optional[str] = None
    attendance_date: date
    check_in_at: datetime
    check_out_at: Optional[datetime] = None
    status: str
    notes: Optional[str] = None
    created_at: datetime

    @model_validator(mode="before")
    @classmethod
    def extract_collector_info(cls, data: Any) -> Any:
        if hasattr(data, "attendance_id"):
            collector_name = data.collector.name if getattr(data, "collector", None) else None
            collector_email = data.collector.email if getattr(data, "collector", None) else None
            return {
                "attendance_id": data.attendance_id,
                "collector_id": data.collector_id,
                "collector_name": collector_name,
                "collector_email": collector_email,
                "attendance_date": data.attendance_date,
                "check_in_at": data.check_in_at,
                "check_out_at": data.check_out_at,
                "status": data.status,
                "notes": data.notes,
                "created_at": data.created_at,
            }
        return data


class CollectorShiftSummary(BaseModel):
    collector_id: uuid.UUID
    name: str
    collector_name: str = ""
    email: str
    collector_email: str = ""
    is_active: bool = True
    attendance_status: str  # ON_SHIFT, NOT_CHECKED_IN, CHECKED_OUT
    status: str = ""
    active_attendance_id: Optional[int] = None
    check_in_at: Optional[datetime] = None
    check_out_at: Optional[datetime] = None
    active_tasks_count: int = 0
    active_task_count: int = 0
    completed_tasks_today_count: int = 0
    overdue_tasks_count: int = 0
    phone_number: Optional[str] = None
    has_sms_configured: bool = False
    has_phone_configured: bool = False
    active_session: Optional[dict] = None
    last_session: Optional[dict] = None

    @model_validator(mode="before")
    @classmethod
    def populate_aliases(cls, data: Any) -> Any:
        if isinstance(data, dict):
            if "name" in data and not data.get("collector_name"):
                data["collector_name"] = data["name"]
            if "collector_name" in data and not data.get("name"):
                data["name"] = data["collector_name"]
            if "email" in data and not data.get("collector_email"):
                data["collector_email"] = data["email"]
            if "collector_email" in data and not data.get("email"):
                data["email"] = data["collector_email"]
            if "attendance_status" in data and not data.get("status"):
                data["status"] = data["attendance_status"]
            if "status" in data and not data.get("attendance_status"):
                data["attendance_status"] = data["status"]
            if "active_tasks_count" in data and "active_task_count" not in data:
                data["active_task_count"] = data["active_tasks_count"]
            if "active_task_count" in data and "active_tasks_count" not in data:
                data["active_tasks_count"] = data["active_task_count"]
        return data


class AdminAttendanceOverview(BaseModel):
    total_collectors: int
    on_shift_collectors: int
    on_shift_count: int = 0
    not_checked_in_collectors: int
    not_checked_in_count: int = 0
    collectors_with_active_tasks: int
    with_active_tasks_count: int = 0
    overdue_tasks_count: int
    campus_date: Optional[str] = None
    collectors: List[CollectorShiftSummary]

    @model_validator(mode="before")
    @classmethod
    def populate_overview_aliases(cls, data: Any) -> Any:
        if isinstance(data, dict):
            if "on_shift_collectors" in data and "on_shift_count" not in data:
                data["on_shift_count"] = data["on_shift_collectors"]
            if "not_checked_in_collectors" in data and "not_checked_in_count" not in data:
                data["not_checked_in_count"] = data["not_checked_in_collectors"]
            if "collectors_with_active_tasks" in data and "with_active_tasks_count" not in data:
                data["with_active_tasks_count"] = data["collectors_with_active_tasks"]
        return data
