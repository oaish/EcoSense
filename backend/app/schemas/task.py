import uuid
from datetime import datetime
from typing import Any, List, Optional
from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

VALID_TASK_TYPES = {"COLLECTION", "INSPECTION", "ISSUE_RESPONSE"}
VALID_TASK_PRIORITIES = {"LOW", "MEDIUM", "HIGH", "URGENT"}
VALID_TASK_STATUSES = {"ASSIGNED", "ACCEPTED", "IN_PROGRESS", "COMPLETED", "CANCELLED"}


class TaskCreate(BaseModel):
    task_type: str = Field(..., description="Type of task: COLLECTION, INSPECTION, ISSUE_RESPONSE")
    collector_id: uuid.UUID = Field(..., description="UUID of the assigned collector")
    bin_id: Optional[uuid.UUID] = Field(None, description="Optional target bin UUID")
    location_id: Optional[int] = Field(None, description="Optional target location ID")
    report_id: Optional[int] = Field(None, description="Optional linked waste report ID")
    priority: str = Field("MEDIUM", description="Task priority: LOW, MEDIUM, HIGH, URGENT")
    title: str = Field(..., min_length=3, max_length=200, description="Brief task summary")
    instructions: Optional[str] = Field(None, description="Detailed field instructions")
    due_date: Optional[datetime] = Field(None, description="Optional target completion deadline (UTC)")

    @field_validator("task_type")
    @classmethod
    def validate_type(cls, v: str) -> str:
        norm = v.strip().upper()
        if norm not in VALID_TASK_TYPES:
            raise ValueError(f"Invalid task_type '{v}'. Allowed: {', '.join(sorted(VALID_TASK_TYPES))}")
        return norm

    @field_validator("priority")
    @classmethod
    def validate_priority(cls, v: str) -> str:
        norm = v.strip().upper()
        if norm not in VALID_TASK_PRIORITIES:
            raise ValueError(f"Invalid priority '{v}'. Allowed: {', '.join(sorted(VALID_TASK_PRIORITIES))}")
        return norm

    @model_validator(mode="after")
    def validate_combinations(self) -> "TaskCreate":
        if self.task_type == "ISSUE_RESPONSE" and not self.report_id:
            raise ValueError("ISSUE_RESPONSE tasks must specify a linked report_id")
        if self.task_type == "COLLECTION" and not self.bin_id and not self.location_id:
            raise ValueError("COLLECTION tasks must specify either a bin_id or a location_id")
        return self


class TaskReassignRequest(BaseModel):
    new_collector_id: uuid.UUID = Field(..., description="UUID of the new collector")
    instructions: Optional[str] = Field(None, description="Optional updated or added instructions")
    priority: Optional[str] = Field(None, description="Optional updated priority")
    due_date: Optional[datetime] = Field(None, description="Optional updated due date")

    @field_validator("priority")
    @classmethod
    def validate_priority(cls, v: Optional[str]) -> Optional[str]:
        if v is not None:
            norm = v.strip().upper()
            if norm not in VALID_TASK_PRIORITIES:
                raise ValueError(f"Invalid priority '{v}'. Allowed: {', '.join(sorted(VALID_TASK_PRIORITIES))}")
            return norm
        return v


class TaskStatusUpdate(BaseModel):
    status: str = Field(..., description="Target status: ACCEPTED, IN_PROGRESS, COMPLETED, CANCELLED")
    completion_notes: Optional[str] = Field(None, max_length=1000, description="Notes documenting resolution or inspection")
    collection_id: Optional[int] = Field(None, description="Linked collection record ID required for COLLECTION tasks")
    cancellation_reason: Optional[str] = Field(None, max_length=500, description="Reason if task is cancelled")

    @field_validator("status")
    @classmethod
    def validate_status(cls, v: str) -> str:
        norm = v.strip().upper()
        if norm not in VALID_TASK_STATUSES:
            raise ValueError(f"Invalid status '{v}'. Allowed: {', '.join(sorted(VALID_TASK_STATUSES))}")
        return norm


class TaskDelegateReportRequest(BaseModel):
    report_id: int = Field(..., description="ID of the waste report to delegate")
    collector_id: uuid.UUID = Field(..., description="UUID of the assigned collector")
    priority: str = Field("HIGH", description="Priority level for delegated response")
    due_date: Optional[datetime] = Field(None, description="Target resolution deadline")
    instructions: Optional[str] = Field(None, description="Specific instructions for the collector")

    @field_validator("priority")
    @classmethod
    def validate_priority(cls, v: str) -> str:
        norm = v.strip().upper()
        if norm not in VALID_TASK_PRIORITIES:
            raise ValueError(f"Invalid priority '{v}'. Allowed: {', '.join(sorted(VALID_TASK_PRIORITIES))}")
        return norm


class TaskRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    task_id: int
    task_type: str
    collector_id: uuid.UUID
    collector_name: Optional[str] = None
    collector_email: Optional[str] = None
    bin_id: Optional[uuid.UUID] = None
    bin_code: Optional[str] = None
    location_id: Optional[int] = None
    location_name: Optional[str] = None
    report_id: Optional[int] = None
    report_type: Optional[str] = None
    report_description: Optional[str] = None
    priority: str
    title: str
    instructions: Optional[str] = None
    due_date: Optional[datetime] = None
    status: str
    created_by: uuid.UUID
    creator_name: Optional[str] = None
    assigned_at: datetime
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    completion_notes: Optional[str] = None
    cancelled_at: Optional[datetime] = None
    cancellation_reason: Optional[str] = None
    collection_id: Optional[int] = None
    created_at: datetime
    updated_at: datetime

    @model_validator(mode="before")
    @classmethod
    def extract_nested_task_fields(cls, data: Any) -> Any:
        if hasattr(data, "task_id"):
            collector_name = data.collector.name if getattr(data, "collector", None) else None
            collector_email = data.collector.email if getattr(data, "collector", None) else None
            creator_name = data.creator.name if getattr(data, "creator", None) else None
            bin_code = data.bin.bin_code if getattr(data, "bin", None) else None
            
            location_name = None
            if getattr(data, "location", None):
                location_name = data.location.name
            elif getattr(data, "bin", None) and getattr(data.bin, "location", None):
                location_name = data.bin.location.name

            report_type = data.report.report_type if getattr(data, "report", None) else None
            report_description = data.report.description if getattr(data, "report", None) else None

            return {
                "task_id": data.task_id,
                "task_type": data.task_type,
                "collector_id": data.collector_id,
                "collector_name": collector_name,
                "collector_email": collector_email,
                "bin_id": data.bin_id,
                "bin_code": bin_code,
                "location_id": data.location_id,
                "location_name": location_name,
                "report_id": data.report_id,
                "report_type": report_type,
                "report_description": report_description,
                "priority": data.priority,
                "title": data.title,
                "instructions": data.instructions,
                "due_date": data.due_date,
                "status": data.status,
                "created_by": data.created_by,
                "creator_name": creator_name,
                "assigned_at": data.assigned_at,
                "started_at": data.started_at,
                "completed_at": data.completed_at,
                "completion_notes": data.completion_notes,
                "cancelled_at": data.cancelled_at,
                "cancellation_reason": data.cancellation_reason,
                "collection_id": data.collection_id,
                "created_at": data.created_at,
                "updated_at": data.updated_at,
            }
        return data


class TaskListResponse(BaseModel):
    total_count: int
    tasks: List[TaskRead]
