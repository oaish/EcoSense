import uuid
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict, Field


class DeviceTokenCreate(BaseModel):
    fcm_token: str = Field(..., min_length=10, max_length=512, description="FCM device registration token")
    device_name: Optional[str] = Field(None, max_length=100, description="Optional client device or browser description")


class DeviceTokenDelete(BaseModel):
    fcm_token: str = Field(..., min_length=10, max_length=512, description="FCM device registration token to disassociate")


class DeviceTokenRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    token_id: int
    device_name: Optional[str] = None
    is_active: bool
    created_at: datetime
    updated_at: datetime


class NotificationPreferencesRead(BaseModel):
    push_notifications_enabled: bool
    active_device_count: int = 0


class NotificationPreferencesUpdate(BaseModel):
    push_notifications_enabled: bool


class NotificationHistoryRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    notification_id: int
    task_id: Optional[int] = None
    report_id: Optional[int] = None
    recipient_user_id: uuid.UUID
    channel: str
    notification_type: Optional[str] = None
    title: Optional[str] = None
    body: Optional[str] = None
    status: str
    created_at: datetime


class PushTestRequest(BaseModel):
    title: Optional[str] = "EcoSense Push Notification Test"
    body: Optional[str] = "Web Push notifications are active and verified on this device."
    target_url: Optional[str] = None


class PushTestResponse(BaseModel):
    status: str
    devices_targeted: int
    success_count: int
    failure_count: int
    message: str
