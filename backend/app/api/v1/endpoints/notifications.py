import logging
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.dependencies import get_current_active_user, require_roles
from app.models.notification import TaskNotification
from app.models.user import User
from app.schemas.notification import (
    DeviceTokenCreate,
    DeviceTokenDelete,
    DeviceTokenRead,
    NotificationHistoryRead,
    NotificationPreferencesRead,
    NotificationPreferencesUpdate,
    PushTestRequest,
    PushTestResponse,
)
from app.services.push_notification_service import push_notification_service

logger = logging.getLogger(__name__)

router = APIRouter()


@router.post(
    "/tokens",
    response_model=DeviceTokenRead,
    status_code=status.HTTP_200_OK,
    summary="Register or Refresh Web Push Device Token",
    description="Registers an FCM web push registration token for the authenticated user. Idempotent.",
)
def register_device_token(
    payload: DeviceTokenCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> DeviceTokenRead:
    token_obj = push_notification_service.register_device_token(
        db=db,
        user_id=current_user.user_id,
        fcm_token=payload.fcm_token,
        device_name=payload.device_name,
    )
    return DeviceTokenRead.model_validate(token_obj)


@router.delete(
    "/tokens",
    status_code=status.HTTP_200_OK,
    summary="Unregister Device Token",
    description="Deactivates an FCM device registration token for the authenticated user (e.g. on logout).",
)
def unregister_device_token(
    payload: DeviceTokenDelete,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> dict:
    success = push_notification_service.unregister_device_token(
        db=db,
        user_id=current_user.user_id,
        fcm_token=payload.fcm_token,
    )
    return {"success": success, "message": "Device token disassociated successfully"}


@router.get(
    "/preferences",
    response_model=NotificationPreferencesRead,
    summary="Get User Push Notification Preferences",
    description="Returns current push notification preference and active device count for the authenticated user.",
)
def get_notification_preferences(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> NotificationPreferencesRead:
    active_tokens = push_notification_service.get_user_device_tokens(
        db=db,
        user_id=current_user.user_id,
        active_only=True,
    )
    return NotificationPreferencesRead(
        push_notifications_enabled=current_user.push_notifications_enabled,
        active_device_count=len(active_tokens),
    )


@router.put(
    "/preferences",
    response_model=NotificationPreferencesRead,
    summary="Update User Push Notification Preferences",
    description="Enables or disables web push notifications for the authenticated user account.",
)
def update_notification_preferences(
    payload: NotificationPreferencesUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> NotificationPreferencesRead:
    updated_user = push_notification_service.update_user_push_preferences(
        db=db,
        user=current_user,
        enabled=payload.push_notifications_enabled,
    )
    active_tokens = push_notification_service.get_user_device_tokens(
        db=db,
        user_id=updated_user.user_id,
        active_only=True,
    )
    return NotificationPreferencesRead(
        push_notifications_enabled=updated_user.push_notifications_enabled,
        active_device_count=len(active_tokens),
    )


@router.get(
    "/history",
    response_model=List[NotificationHistoryRead],
    summary="Get Notification History",
    description="Retrieve recent notification delivery outcomes. Normal users see their own; Admins see all campus records.",
)
def get_notification_history(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> List[NotificationHistoryRead]:
    stmt = select(TaskNotification).order_by(TaskNotification.created_at.desc())
    user_role = current_user.role.role_name.upper() if current_user.role else ""

    if user_role != "ADMIN":
        stmt = stmt.where(TaskNotification.recipient_user_id == current_user.user_id)

    stmt = stmt.offset(skip).limit(limit)
    records = list(db.scalars(stmt).all())
    return [NotificationHistoryRead.model_validate(r) for r in records]


@router.post(
    "/test",
    response_model=PushTestResponse,
    summary="Send Test Push Notification",
    description="Dispatches a test push notification to all active devices registered to the calling user.",
)
def send_test_push_notification(
    payload: PushTestRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> PushTestResponse:
    res = push_notification_service.dispatch_push_to_user(
        db=db,
        recipient_user_id=current_user.user_id,
        title=payload.title or "EcoSense Push Notification Test",
        body=payload.body or "Web push notifications are working correctly on this device.",
        event_type="TEST_NOTIFICATION",
        target_path=payload.target_url or "/",
    )

    return PushTestResponse(
        status=res.get("status", "UNKNOWN"),
        devices_targeted=res.get("targeted_tokens", 0),
        success_count=res.get("success_count", 0),
        failure_count=res.get("failure_count", 0),
        message="Test notification processed. Check device or browser notification center.",
    )
