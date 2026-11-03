"""Tests for Collector Phone Management and Firebase Cloud Messaging (FCM) Web Push Notifications.

Covers:
- Collector phone number management preserved (admin update, E.164 normalization, role restrictions).
- Historical SMS notification records in task_notifications preserved.
- Firebase Admin graceful initialization and startup when unconfigured or disabled.
- Token registration, idempotent updates, multiple devices per user, and disassociation on logout.
- Notification preferences API (enable/disable push).
- FCM push dispatch with mocked Firebase messaging (success, UnregisteredError cleanup, failure isolation).
- Task assignment, reassignment, and report delegation notification hooks.
- Urgent waste reports notify admins.
- Report status updates notify reporters.
- Guarantee that task/report transactions remain committed even when push dispatch fails.
"""

from unittest.mock import MagicMock, patch
import uuid
import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from sqlalchemy import select

from app.core.config import settings
from app.core.phone_utils import (
    mask_phone_number,
    normalize_phone_number,
)
from app.models.device_token import DeviceToken
from app.models.location import Location
from app.models.notification import TaskNotification
from app.models.report import WasteReport
from app.models.role import Role
from app.models.task import CollectionTask
from app.models.user import User
from app.services.push_notification_service import (
    STATUS_FAILED,
    STATUS_SENT_OR_ACCEPTED,
    STATUS_SKIPPED_DISABLED,
    STATUS_SKIPPED_NO_TOKEN,
    STATUS_SKIPPED_NOT_CONFIGURED,
    PushNotificationService,
    push_notification_service,
)


# ==============================================================================
# 1. PHONE NUMBER MANAGEMENT PRESERVATION TESTS
# ==============================================================================

def test_phone_normalization_valid_formats() -> None:
    assert normalize_phone_number("9876543210") == "+919876543210"
    assert normalize_phone_number("+919876543210") == "+919876543210"
    assert normalize_phone_number("+91 98765 43210") == "+919876543210"
    assert normalize_phone_number("09876543210") == "+919876543210"


def test_phone_masking() -> None:
    assert mask_phone_number("+919876543210") == "+91******3210"
    assert mask_phone_number(None) == "<none>"


def test_admin_update_collector_phone(
    client: TestClient,
    admin_token: str,
    test_collector_user: User,
    db_session: Session,
) -> None:
    headers = {"Authorization": f"Bearer {admin_token}"}
    url = f"/api/v1/users/{test_collector_user.user_id}/phone"
    res = client.patch(url, json={"phone_number": "9876543210"}, headers=headers)
    assert res.status_code == 200
    data = res.json()
    assert data["phone_number"] == "+919876543210"

    # Verify DB persistence
    db_session.refresh(test_collector_user)
    assert test_collector_user.phone_number == "+919876543210"


def test_student_cannot_update_collector_phone(
    client: TestClient,
    student_token: str,
    test_collector_user: User,
) -> None:
    headers = {"Authorization": f"Bearer {student_token}"}
    url = f"/api/v1/users/{test_collector_user.user_id}/phone"
    res = client.patch(url, json={"phone_number": "9876543210"}, headers=headers)
    assert res.status_code == 403


# ==============================================================================
# 2. HISTORICAL NOTIFICATION DATA PRESERVATION TESTS
# ==============================================================================

def test_historical_sms_notifications_preserved(
    db_session: Session,
    test_collector_user: User,
) -> None:
    """Confirms that existing task_notifications rows with channel='SMS' remain intact."""
    historical_sms = TaskNotification(
        task_id=None,
        recipient_user_id=test_collector_user.user_id,
        channel="SMS",
        status="SENT_OR_ACCEPTED",
        provider_msg_id="HISTORICAL_SMS_12345",
        error_message=None,
    )
    db_session.add(historical_sms)
    db_session.commit()
    db_session.refresh(historical_sms)

    assert historical_sms.notification_id is not None
    assert historical_sms.channel == "SMS"
    assert historical_sms.status == "SENT_OR_ACCEPTED"

    # Query back
    record = db_session.get(TaskNotification, historical_sms.notification_id)
    assert record is not None
    assert record.channel == "SMS"


# ==============================================================================
# 3. FIREBASE INITIALIZATION & STARTUP SAFETY
# ==============================================================================

def test_firebase_service_graceful_when_disabled() -> None:
    service = PushNotificationService()
    with patch.object(settings, "FIREBASE_PUSH_ENABLED", False):
        assert service._ensure_firebase_initialized() is False
        assert service.is_configured_and_enabled is False


def test_firebase_dispatch_skipped_when_disabled(
    db_session: Session,
    test_collector_user: User,
) -> None:
    service = PushNotificationService()
    with patch.object(settings, "FIREBASE_PUSH_ENABLED", False):
        result = service.dispatch_push_to_user(
            db=db_session,
            recipient_user_id=test_collector_user.user_id,
            title="Test Push",
            body="Test Message",
            event_type="TEST",
        )
        assert result["status"] == STATUS_SKIPPED_DISABLED


# ==============================================================================
# 4. DEVICE TOKEN REGISTRATION & MANAGEMENT API
# ==============================================================================

def test_register_device_token_authenticated(
    client: TestClient,
    collector_token: str,
    test_collector_user: User,
    db_session: Session,
) -> None:
    headers = {"Authorization": f"Bearer {collector_token}"}
    token_str = "fcm_test_token_collector_browser_chrome_123456"
    res = client.post(
        "/api/v1/notifications/tokens",
        json={"fcm_token": token_str, "device_name": "Collector Chrome Desktop"},
        headers=headers,
    )
    assert res.status_code == 200
    data = res.json()
    assert data["token_id"] > 0
    assert data["is_active"] is True
    assert data["device_name"] == "Collector Chrome Desktop"

    # Confirm associated with authenticated collector
    db_token = db_session.scalar(select(DeviceToken).where(DeviceToken.fcm_token == token_str))
    assert db_token is not None
    assert db_token.user_id == test_collector_user.user_id


def test_register_device_token_unauthenticated(client: TestClient) -> None:
    res = client.post(
        "/api/v1/notifications/tokens",
        json={"fcm_token": "some_test_token_12345"},
    )
    assert res.status_code == 401


def test_repeated_registration_idempotent(
    client: TestClient,
    collector_token: str,
    test_collector_user: User,
    db_session: Session,
) -> None:
    headers = {"Authorization": f"Bearer {collector_token}"}
    token_str = "fcm_test_idempotent_token_789"
    # First registration
    client.post(
        "/api/v1/notifications/tokens",
        json={"fcm_token": token_str, "device_name": "Device 1"},
        headers=headers,
    )
    # Second registration with updated device name
    res2 = client.post(
        "/api/v1/notifications/tokens",
        json={"fcm_token": token_str, "device_name": "Device 1 Renamed"},
        headers=headers,
    )
    assert res2.status_code == 200
    assert res2.json()["device_name"] == "Device 1 Renamed"

    tokens = list(db_session.scalars(select(DeviceToken).where(DeviceToken.fcm_token == token_str)).all())
    assert len(tokens) == 1


def test_account_switch_transfers_token(
    client: TestClient,
    collector_token: str,
    admin_token: str,
    test_collector_user: User,
    test_admin_user: User,
    db_session: Session,
) -> None:
    collector_headers = {"Authorization": f"Bearer {collector_token}"}
    admin_headers = {"Authorization": f"Bearer {admin_token}"}
    shared_token = "fcm_shared_browser_token_switch_999"

    # Collector registers token
    client.post(
        "/api/v1/notifications/tokens",
        json={"fcm_token": shared_token, "device_name": "Shared Lab PC"},
        headers=collector_headers,
    )
    # Admin logs in and registers same token
    res = client.post(
        "/api/v1/notifications/tokens",
        json={"fcm_token": shared_token, "device_name": "Shared Lab PC"},
        headers=admin_headers,
    )
    assert res.status_code == 200

    db_token = db_session.scalar(select(DeviceToken).where(DeviceToken.fcm_token == shared_token))
    assert db_token is not None
    assert db_token.user_id == test_admin_user.user_id  # Transferred to admin


def test_unregister_device_token(
    client: TestClient,
    collector_token: str,
    test_collector_user: User,
    db_session: Session,
) -> None:
    headers = {"Authorization": f"Bearer {collector_token}"}
    token_str = "fcm_to_unregister_token_456"
    client.post(
        "/api/v1/notifications/tokens",
        json={"fcm_token": token_str, "device_name": "Tablet"},
        headers=headers,
    )
    # Disassociate
    res = client.request(
        "DELETE",
        "/api/v1/notifications/tokens",
        json={"fcm_token": token_str},
        headers=headers,
    )
    assert res.status_code == 200
    assert res.json()["success"] is True

    db_token = db_session.scalar(select(DeviceToken).where(DeviceToken.fcm_token == token_str))
    assert db_token is not None
    assert db_token.is_active is False


def test_user_cannot_unregister_other_user_token(
    client: TestClient,
    collector_token: str,
    student_token: str,
    test_collector_user: User,
    db_session: Session,
) -> None:
    collector_headers = {"Authorization": f"Bearer {collector_token}"}
    student_headers = {"Authorization": f"Bearer {student_token}"}
    token_str = "fcm_collector_exclusive_token_999"

    client.post(
        "/api/v1/notifications/tokens",
        json={"fcm_token": token_str},
        headers=collector_headers,
    )

    # Student attempts to unregister collector's token
    res = client.request(
        "DELETE",
        "/api/v1/notifications/tokens",
        json={"fcm_token": token_str},
        headers=student_headers,
    )
    assert res.status_code == 200
    assert res.json()["success"] is False

    # Collector token is still active
    db_token = db_session.scalar(select(DeviceToken).where(DeviceToken.fcm_token == token_str))
    assert db_token is not None
    assert db_token.is_active is True


# ==============================================================================
# 5. NOTIFICATION PREFERENCES API
# ==============================================================================

def test_notification_preferences_get_and_put(
    client: TestClient,
    student_token: str,
    test_student_user: User,
) -> None:
    headers = {"Authorization": f"Bearer {student_token}"}

    # GET preferences
    res = client.get("/api/v1/notifications/preferences", headers=headers)
    assert res.status_code == 200
    assert res.json()["push_notifications_enabled"] is True

    # PUT preferences (disable)
    res_update = client.put(
        "/api/v1/notifications/preferences",
        json={"push_notifications_enabled": False},
        headers=headers,
    )
    assert res_update.status_code == 200
    assert res_update.json()["push_notifications_enabled"] is False

    # PUT preferences (re-enable)
    res_enable = client.put(
        "/api/v1/notifications/preferences",
        json={"push_notifications_enabled": True},
        headers=headers,
    )
    assert res_enable.status_code == 200
    assert res_enable.json()["push_notifications_enabled"] is True


# ==============================================================================
# 6. DISPATCH ENGINE WITH MOCKED FIREBASE MESSAGING
# ==============================================================================

def test_dispatch_push_skipped_when_no_active_tokens(
    db_session: Session,
    test_collector_user: User,
) -> None:
    with patch.object(settings, "FIREBASE_PUSH_ENABLED", True), \
         patch.object(push_notification_service, "_ensure_firebase_initialized", return_value=True):
        res = push_notification_service.dispatch_push_to_user(
            db=db_session,
            recipient_user_id=test_collector_user.user_id,
            title="Task Assigned",
            body="Collect Bin B01",
            event_type="TASK_ASSIGNED",
        )
        assert res["status"] == STATUS_SKIPPED_NO_TOKEN


def test_dispatch_push_success_mock(
    db_session: Session,
    test_collector_user: User,
) -> None:
    # Register active token
    push_notification_service.register_device_token(
        db=db_session,
        user_id=test_collector_user.user_id,
        fcm_token="fcm_valid_mock_token_12345",
        device_name="Test Phone",
    )

    with patch.object(settings, "FIREBASE_PUSH_ENABLED", True), \
         patch.object(push_notification_service, "_ensure_firebase_initialized", return_value=True), \
         patch("firebase_admin.messaging.send", return_value="projects/test/messages/msg_123") as mock_send:

        res = push_notification_service.dispatch_push_to_user(
            db=db_session,
            recipient_user_id=test_collector_user.user_id,
            title="Task Assigned",
            body="Collection at Block A",
            event_type="TASK_ASSIGNED",
            target_path="/collector/tasks",
        )

        assert res["status"] == STATUS_SENT_OR_ACCEPTED
        assert res["success_count"] == 1
        assert mock_send.call_count == 1

        # Check payload
        call_msg = mock_send.call_args[0][0]
        assert call_msg.notification.title == "Task Assigned"
        assert call_msg.data["event_type"] == "TASK_ASSIGNED"
        assert call_msg.data["target_url"] == f"{settings.PUBLIC_FRONTEND_URL}/collector/tasks"


def test_dispatch_push_unregistered_token_cleaned_up(
    db_session: Session,
    test_collector_user: User,
) -> None:
    from firebase_admin import messaging

    tok = push_notification_service.register_device_token(
        db=db_session,
        user_id=test_collector_user.user_id,
        fcm_token="fcm_expired_token_unregistered_999",
        device_name="Old Phone",
    )
    assert tok.is_active is True

    with patch.object(settings, "FIREBASE_PUSH_ENABLED", True), \
         patch.object(push_notification_service, "_ensure_firebase_initialized", return_value=True), \
         patch("firebase_admin.messaging.send", side_effect=messaging.UnregisteredError("Token unregistered")):

        res = push_notification_service.dispatch_push_to_user(
            db=db_session,
            recipient_user_id=test_collector_user.user_id,
            title="Notice",
            body="Hello",
            event_type="NOTICE",
        )

        assert res["status"] == STATUS_FAILED
        assert res["failure_count"] == 1

        # Confirm token was marked is_active = False
        db_session.refresh(tok)
        assert tok.is_active is False


# ==============================================================================
# 7. OPERATIONAL WORKFLOW DISPATCH HOOKS (TASK & REPORT)
# ==============================================================================

def test_task_assignment_dispatches_push(
    client: TestClient,
    admin_token: str,
    test_collector_user: User,
    test_location: Location,
    db_session: Session,
) -> None:
    headers = {"Authorization": f"Bearer {admin_token}"}
    with patch.object(push_notification_service, "send_task_assignment_push") as mock_push:
        mock_push.return_value = {"status": STATUS_SENT_OR_ACCEPTED}

        payload = {
            "task_type": "COLLECTION",
            "collector_id": str(test_collector_user.user_id),
            "location_id": test_location.location_id,
            "priority": "HIGH",
            "title": "Clear North Quad Bins",
            "instructions": "Empty all recycling bins.",
        }
        res = client.post("/api/v1/tasks", json=payload, headers=headers)
        assert res.status_code == 201

        mock_push.assert_called_once()
        call_kwargs = mock_push.call_args[1]
        assert call_kwargs["collector"].user_id == test_collector_user.user_id
        assert call_kwargs["task"].title == "Clear North Quad Bins"


def test_task_reassignment_dispatches_push(
    client: TestClient,
    admin_token: str,
    test_collector_user: User,
    test_location: Location,
    test_admin_user: User,
    db_session: Session,
) -> None:
    headers = {"Authorization": f"Bearer {admin_token}"}

    # Create second collector
    role = db_session.scalar(select(Role).where(Role.role_name == "COLLECTOR"))
    new_collector = User(
        name="Second Collector",
        email=f"col2_{uuid.uuid4().hex[:6]}@dbit.in",
        password_hash="hashed",
        role_id=role.role_id,
    )
    db_session.add(new_collector)
    db_session.commit()

    # Create task
    task = CollectionTask(
        task_type="COLLECTION",
        collector_id=test_collector_user.user_id,
        location_id=test_location.location_id,
        priority="MEDIUM",
        title="Initial Task",
        status="ASSIGNED",
        created_by=test_admin_user.user_id,
    )
    db_session.add(task)
    db_session.commit()
    db_session.refresh(task)

    with patch.object(push_notification_service, "send_task_reassignment_push") as mock_push:
        mock_push.return_value = {"status": STATUS_SENT_OR_ACCEPTED}

        res = client.post(
            f"/api/v1/tasks/{task.task_id}/reassign",
            json={"new_collector_id": str(new_collector.user_id), "instructions": "Reassigned due to shift change."},
            headers=headers,
        )
        assert res.status_code == 200

        mock_push.assert_called_once()
        call_kwargs = mock_push.call_args[1]
        assert call_kwargs["new_collector"].user_id == new_collector.user_id


def test_task_persists_when_push_fails(
    client: TestClient,
    admin_token: str,
    test_collector_user: User,
    test_location: Location,
    db_session: Session,
) -> None:
    """Guarantee: Task creation succeeds even if push dispatch raises an uncaught exception."""
    headers = {"Authorization": f"Bearer {admin_token}"}
    with patch.object(push_notification_service, "send_task_assignment_push", side_effect=RuntimeError("Firebase timeout")):
        payload = {
            "task_type": "INSPECTION",
            "collector_id": str(test_collector_user.user_id),
            "location_id": test_location.location_id,
            "priority": "LOW",
            "title": "Check Bin Sensors",
        }
        res = client.post("/api/v1/tasks", json=payload, headers=headers)
        assert res.status_code == 201
        data = res.json()
        assert data["title"] == "Check Bin Sensors"
        assert data["status"] == "ASSIGNED"


def test_urgent_report_notifies_admins(
    client: TestClient,
    student_token: str,
    db_session: Session,
) -> None:
    headers = {"Authorization": f"Bearer {student_token}"}
    with patch.object(push_notification_service, "send_urgent_report_admin_push") as mock_admin_push:
        mock_admin_push.return_value = []
        payload = {
            "report_type": "OVERFLOWING",
            "description": "Bin is completely full and spilling.",
        }
        res = client.post("/api/v1/reports", json=payload, headers=headers)
        assert res.status_code == 201

        mock_admin_push.assert_called_once()


def test_report_resolution_notifies_reporter(
    client: TestClient,
    admin_token: str,
    test_student_user: User,
    db_session: Session,
) -> None:
    headers = {"Authorization": f"Bearer {admin_token}"}
    report = WasteReport(
        user_id=test_student_user.user_id,
        report_type="OVERFLOWING",
        description="Spill in cafeteria",
        status="PENDING",
    )
    db_session.add(report)
    db_session.commit()
    db_session.refresh(report)

    with patch.object(push_notification_service, "send_report_status_push") as mock_status_push:
        mock_status_push.return_value = {"status": STATUS_SENT_OR_ACCEPTED}

        res = client.patch(
            f"/api/v1/reports/{report.report_id}",
            json={"status": "RESOLVED"},
            headers=headers,
        )
        assert res.status_code == 200

        mock_status_push.assert_called_once()
        assert mock_status_push.call_args[1]["new_status"] == "RESOLVED"
