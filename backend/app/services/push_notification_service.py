import logging
import os
import uuid
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
from sqlalchemy import func, select, update
from sqlalchemy.orm import Session

import firebase_admin
from firebase_admin import credentials, messaging
from firebase_admin.exceptions import FirebaseError

from app.core.config import settings
from app.models.device_token import DeviceToken
from app.models.notification import TaskNotification
from app.models.user import User

logger = logging.getLogger(__name__)

# Status outcome constants
STATUS_SENT_OR_ACCEPTED = "SENT_OR_ACCEPTED"
STATUS_FAILED = "FAILED"
STATUS_SKIPPED_NO_TOKEN = "SKIPPED_NO_TOKEN"
STATUS_SKIPPED_DISABLED = "SKIPPED_DISABLED"
STATUS_SKIPPED_NOT_CONFIGURED = "SKIPPED_NOT_CONFIGURED"


class PushNotificationService:
    """Service boundary for Firebase Cloud Messaging (FCM) Web Push notifications.
    
    Responsibilities:
    - Safe singleton Firebase Admin initialization.
    - Graceful startup when Firebase is unconfigured or disabled.
    - Token registration, deactivation, and disassociation per authenticated user.
    - Post-commit notification dispatch with transaction isolation.
    - Inactive / unregistered token self-cleaning.
    - Audit logging into the channel-neutral task_notifications table.
    """

    def __init__(self) -> None:
        self._firebase_app: Optional[firebase_admin.App] = None
        self._init_attempted: bool = False

    def _ensure_firebase_initialized(self) -> bool:
        """Initializes Firebase Admin once. Returns True if initialized and ready to send."""
        if not settings.FIREBASE_PUSH_ENABLED:
            return False

        if self._firebase_app is not None:
            return True

        if self._init_attempted and self._firebase_app is None:
            return False

        self._init_attempted = True

        try:
            # Check if default app is already initialized in this process
            try:
                self._firebase_app = firebase_admin.get_app()
                logger.info("[FCM] Attached to existing Firebase Admin application instance.")
                return True
            except ValueError:
                pass  # Not yet initialized

            cred = None
            cred_path = settings.FIREBASE_SERVICE_ACCOUNT_PATH
            resolved_cred_path = None
            if cred_path:
                from pathlib import Path
                candidate = Path(cred_path)
                if candidate.exists() and candidate.is_file() and candidate.stat().st_size > 0:
                    resolved_cred_path = str(candidate)
                else:
                    backend_dir = Path(__file__).resolve().parent.parent.parent
                    bp = backend_dir / cred_path
                    if bp.exists() and bp.is_file() and bp.stat().st_size > 0:
                        resolved_cred_path = str(bp)

            if resolved_cred_path:
                logger.info(f"[FCM] Loading Firebase credentials from service account file: {resolved_cred_path}")
                cred = credentials.Certificate(resolved_cred_path)
            elif os.environ.get("GOOGLE_APPLICATION_CREDENTIALS"):
                logger.info("[FCM] Loading Firebase credentials from GOOGLE_APPLICATION_CREDENTIALS.")
                cred = credentials.ApplicationDefault()

            init_options: Dict[str, Any] = {}
            if settings.FIREBASE_PROJECT_ID:
                init_options["projectId"] = settings.FIREBASE_PROJECT_ID

            if cred:
                self._firebase_app = firebase_admin.initialize_app(cred, init_options or None)
            else:
                # Initialize with Application Default Credentials or project settings
                self._firebase_app = firebase_admin.initialize_app(options=init_options or None)

            logger.info("[FCM] Firebase Admin successfully initialized for Web Push.")
            return True
        except Exception as exc:
            logger.warning(
                f"[FCM Init Skipped] Firebase Admin could not be initialized ({type(exc).__name__}: {exc}). "
                "Web push notifications will be safely bypassed."
            )
            self._firebase_app = None
            return False

    @property
    def is_configured_and_enabled(self) -> bool:
        return bool(settings.FIREBASE_PUSH_ENABLED) and self._ensure_firebase_initialized()

    # --------------------------------------------------------------------------
    # Token Management
    # --------------------------------------------------------------------------

    def register_device_token(
        self,
        db: Session,
        user_id: uuid.UUID,
        fcm_token: str,
        device_name: Optional[str] = None,
    ) -> DeviceToken:
        """Associates or updates an FCM registration token with the authenticated user."""
        token_str = fcm_token.strip()
        existing = db.scalar(
            select(DeviceToken).where(DeviceToken.fcm_token == token_str)
        )

        now = datetime.now(timezone.utc)
        if existing:
            # Handle user transfer (e.g. account switching on shared browser)
            existing.user_id = user_id
            existing.is_active = True
            if device_name:
                existing.device_name = device_name[:100]
            existing.updated_at = now
            db.commit()
            db.refresh(existing)
            logger.info(f"[FCM Token] Re-activated/re-associated token ID {existing.token_id} for user {user_id}")
            return existing

        new_token = DeviceToken(
            user_id=user_id,
            fcm_token=token_str,
            device_name=device_name[:100] if device_name else None,
            is_active=True,
            created_at=now,
            updated_at=now,
        )
        db.add(new_token)
        db.commit()
        db.refresh(new_token)
        logger.info(f"[FCM Token] Registered new device token ID {new_token.token_id} for user {user_id}")
        return new_token

    def unregister_device_token(
        self,
        db: Session,
        user_id: uuid.UUID,
        fcm_token: str,
    ) -> bool:
        """Deactivates an FCM token owned by the authenticated user (e.g. on logout or toggle off)."""
        token_str = fcm_token.strip()
        record = db.scalar(
            select(DeviceToken).where(
                DeviceToken.fcm_token == token_str,
                DeviceToken.user_id == user_id,
            )
        )
        if record:
            record.is_active = False
            record.updated_at = datetime.now(timezone.utc)
            db.commit()
            logger.info(f"[FCM Token] Deactivated token ID {record.token_id} for user {user_id}")
            return True
        return False

    def get_user_device_tokens(
        self,
        db: Session,
        user_id: uuid.UUID,
        active_only: bool = True,
    ) -> List[DeviceToken]:
        stmt = select(DeviceToken).where(DeviceToken.user_id == user_id)
        if active_only:
            stmt = stmt.where(DeviceToken.is_active.is_(True))
        return list(db.scalars(stmt).all())

    def update_user_push_preferences(
        self,
        db: Session,
        user: User,
        enabled: bool,
    ) -> User:
        user.push_notifications_enabled = enabled
        db.commit()
        db.refresh(user)
        logger.info(f"[FCM Preferences] User {user.user_id} push_notifications_enabled set to {enabled}")
        return user

    # --------------------------------------------------------------------------
    # Notification Dispatch Engine
    # --------------------------------------------------------------------------

    def dispatch_push_to_user(
        self,
        db: Optional[Session],
        recipient_user_id: uuid.UUID,
        title: str,
        body: str,
        event_type: str,
        target_path: str = "/",
        task_id: Optional[int] = None,
        report_id: Optional[int] = None,
    ) -> Dict[str, Any]:
        """Dispatches an FCM Web Push notification to all active devices registered to recipient_user_id."""
        # 1. Check if disabled globally
        if not settings.FIREBASE_PUSH_ENABLED:
            logger.info(f"[FCM Skipped Disabled] Push notifications disabled globally. Target user: {recipient_user_id}")
            self._record_notification(
                db=db,
                recipient_user_id=recipient_user_id,
                status=STATUS_SKIPPED_DISABLED,
                title=title,
                body=body,
                notification_type=event_type,
                task_id=task_id,
                report_id=report_id,
                error_message="Push notifications are disabled in application settings.",
            )
            return {
                "status": STATUS_SKIPPED_DISABLED,
                "recipient_user_id": str(recipient_user_id),
                "targeted_tokens": 0,
                "success_count": 0,
                "failure_count": 0,
            }

        # 2. Check if Firebase Admin SDK initialized
        if not self._ensure_firebase_initialized():
            logger.warning(f"[FCM Skipped Not Configured] Firebase credentials missing or not configured. User: {recipient_user_id}")
            self._record_notification(
                db=db,
                recipient_user_id=recipient_user_id,
                status=STATUS_SKIPPED_NOT_CONFIGURED,
                title=title,
                body=body,
                notification_type=event_type,
                task_id=task_id,
                report_id=report_id,
                error_message="Firebase Admin SDK is not configured with valid credentials.",
            )
            return {
                "status": STATUS_SKIPPED_NOT_CONFIGURED,
                "recipient_user_id": str(recipient_user_id),
                "targeted_tokens": 0,
                "success_count": 0,
                "failure_count": 0,
            }

        # 3. Check recipient user preferences & device tokens
        if db is None:
            return {"status": STATUS_FAILED, "error": "No database session available"}

        recipient = db.get(User, recipient_user_id)
        if recipient and not recipient.push_notifications_enabled:
            logger.info(f"[FCM Skipped User Disabled] User {recipient_user_id} has push notifications toggled OFF.")
            self._record_notification(
                db=db,
                recipient_user_id=recipient_user_id,
                status=STATUS_SKIPPED_DISABLED,
                title=title,
                body=body,
                notification_type=event_type,
                task_id=task_id,
                report_id=report_id,
                error_message="Recipient has disabled push notifications in their profile preferences.",
            )
            return {
                "status": STATUS_SKIPPED_DISABLED,
                "recipient_user_id": str(recipient_user_id),
                "targeted_tokens": 0,
                "success_count": 0,
                "failure_count": 0,
            }

        active_tokens = self.get_user_device_tokens(db=db, user_id=recipient_user_id, active_only=True)
        if not active_tokens:
            logger.info(f"[FCM Skipped No Token] No active device tokens registered for user {recipient_user_id}.")
            self._record_notification(
                db=db,
                recipient_user_id=recipient_user_id,
                status=STATUS_SKIPPED_NO_TOKEN,
                title=title,
                body=body,
                notification_type=event_type,
                task_id=task_id,
                report_id=report_id,
                error_message="No registered web push device tokens for this user.",
            )
            return {
                "status": STATUS_SKIPPED_NO_TOKEN,
                "recipient_user_id": str(recipient_user_id),
                "targeted_tokens": 0,
                "success_count": 0,
                "failure_count": 0,
            }

        # 4. Construct Public Navigation URL
        frontend_base = settings.PUBLIC_FRONTEND_URL.rstrip("/")
        clean_path = target_path if target_path.startswith("/") else f"/{target_path}"
        full_target_url = f"{frontend_base}{clean_path}"

        # 5. Build Webpush message payload
        data_payload: Dict[str, str] = {
            "title": title,
            "body": body,
            "event_type": event_type,
            "target_url": full_target_url,
        }
        if task_id is not None:
            data_payload["task_id"] = str(task_id)
        if report_id is not None:
            data_payload["report_id"] = str(report_id)

        webpush_config = messaging.WebpushConfig(
            headers={"Urgency": "high"},
            notification=messaging.WebpushNotification(
                title=title,
                body=body,
                icon=f"{frontend_base}/leaf.svg",
                badge=f"{frontend_base}/leaf.svg",
            ),
            fcm_options=messaging.WebpushFCMOptions(
                link=full_target_url,
            ),
        )

        success_count = 0
        failure_count = 0
        provider_msg_ids: List[str] = []
        tokens_to_deactivate: List[int] = []

        # 6. Multicast / individual dispatch
        for tok in active_tokens:
            try:
                message = messaging.Message(
                    token=tok.fcm_token,
                    notification=messaging.Notification(title=title, body=body),
                    data=data_payload,
                    webpush=webpush_config,
                )
                response_id = messaging.send(message)
                success_count += 1
                provider_msg_ids.append(response_id)
            except messaging.UnregisteredError:
                # Token expired or browser unregistered
                logger.info(f"[FCM Token Unregistered] Device token ID {tok.token_id} is no longer registered. Marking inactive.")
                tokens_to_deactivate.append(tok.token_id)
                failure_count += 1
            except messaging.SenderIdMismatchError:
                logger.warning(f"[FCM Token Mismatch] Token ID {tok.token_id} sender mismatch. Marking inactive.")
                tokens_to_deactivate.append(tok.token_id)
                failure_count += 1
            except Exception as exc:
                err_msg = str(exc)
                logger.warning(f"[FCM Token Dispatch Error] Token ID {tok.token_id} failed: {type(exc).__name__} - {err_msg}")
                if "registration-token-not-registered" in err_msg.lower() or "invalid-argument" in err_msg.lower():
                    tokens_to_deactivate.append(tok.token_id)
                failure_count += 1

        # 7. Clean up invalid tokens
        if tokens_to_deactivate:
            try:
                db.execute(
                    update(DeviceToken)
                    .where(DeviceToken.token_id.in_(tokens_to_deactivate))
                    .values(is_active=False, updated_at=datetime.now(timezone.utc))
                )
                db.commit()
            except Exception as exc:
                logger.warning(f"Could not update deactivated tokens: {exc}")

        # 8. Record notification audit outcome
        final_status = STATUS_SENT_OR_ACCEPTED if success_count > 0 else STATUS_FAILED
        provider_id_str = ",".join(provider_msg_ids) if provider_msg_ids else None
        err_detail = None if success_count > 0 else f"Failed to deliver to {failure_count} devices."

        self._record_notification(
            db=db,
            recipient_user_id=recipient_user_id,
            status=final_status,
            title=title,
            body=body,
            notification_type=event_type,
            task_id=task_id,
            report_id=report_id,
            provider_msg_id=provider_id_str,
            error_message=err_detail,
        )

        return {
            "status": final_status,
            "recipient_user_id": str(recipient_user_id),
            "targeted_tokens": len(active_tokens),
            "success_count": success_count,
            "failure_count": failure_count,
            "provider_msg_ids": provider_msg_ids,
        }

    # --------------------------------------------------------------------------
    # Specialized EcoSense Event Triggers
    # --------------------------------------------------------------------------

    def send_task_assignment_push(
        self,
        task: Any,
        collector: User,
        db: Optional[Session] = None,
    ) -> Dict[str, Any]:
        """Dispatches a push notification when a task is assigned to a collector."""
        target_info = (
            f"Bin {task.bin.bin_code}" if getattr(task, "bin", None)
            else (getattr(task, "location", None).name if getattr(task, "location", None) else "Campus Facility")
        )
        due_info = f" • Due {task.due_date.strftime('%b %d, %I:%M %p')}" if getattr(task, "due_date", None) else ""
        title = f"New Task #{task.task_id} Assigned"
        body = f"{task.priority} Priority {task.task_type.replace('_', ' ').title()}: {target_info}{due_info}"

        return self.dispatch_push_to_user(
            db=db,
            recipient_user_id=collector.user_id,
            title=title,
            body=body,
            event_type="TASK_ASSIGNED",
            target_path=f"/collector/tasks?task_id={task.task_id}",
            task_id=task.task_id,
        )

    def send_task_reassignment_push(
        self,
        task: Any,
        new_collector: User,
        db: Optional[Session] = None,
    ) -> Dict[str, Any]:
        """Dispatches a push notification when a task is reassigned to a new collector."""
        target_info = (
            f"Bin {task.bin.bin_code}" if getattr(task, "bin", None)
            else (getattr(task, "location", None).name if getattr(task, "location", None) else "Campus Facility")
        )
        title = f"Task #{task.task_id} Reassigned To You"
        body = f"{task.priority} Priority {task.task_type.replace('_', ' ').title()}: {target_info}. Review instructions in EcoSense."

        return self.dispatch_push_to_user(
            db=db,
            recipient_user_id=new_collector.user_id,
            title=title,
            body=body,
            event_type="TASK_REASSIGNED",
            target_path=f"/collector/tasks?task_id={task.task_id}",
            task_id=task.task_id,
        )

    def send_urgent_report_admin_push(
        self,
        report: Any,
        reporter: User,
        db: Session,
    ) -> List[Dict[str, Any]]:
        """Notifies active administrators when an urgent issue report (overflowing, damaged) is submitted."""
        clean_type = report.report_type.replace("_", " ").title()
        bin_code = report.bin.bin_code if getattr(report, "bin", None) else "Campus"
        title = f"New Waste Issue: {clean_type}"
        body = f"Reported at Bin {bin_code} by {reporter.name}. Action required."

        # Find active ADMIN users
        admin_users = list(
            db.scalars(
                select(User)
                .join(User.role)
                .where(
                    func.upper(User.role.property.mapper.class_.role_name) == "ADMIN",
                    User.is_active.is_(True),
                )
            ).all()
        )

        results = []
        for admin in admin_users:
            res = self.dispatch_push_to_user(
                db=db,
                recipient_user_id=admin.user_id,
                title=title,
                body=body,
                event_type="REPORT_SUBMITTED",
                target_path=f"/admin/reports?report_id={report.report_id}",
                report_id=report.report_id,
            )
            results.append(res)
        return results

    def send_report_status_push(
        self,
        report: Any,
        recipient: User,
        new_status: str,
        db: Optional[Session] = None,
    ) -> Dict[str, Any]:
        """Notifies the student or staff reporter when their waste report status changes."""
        clean_type = report.report_type.replace("_", " ").title()
        title = f"Waste Report #{report.report_id} {new_status.title()}"
        if new_status == "RESOLVED":
            body = f"Great news! Your {clean_type} report has been resolved. Points have been credited to your EcoSense wallet!"
        elif new_status == "IN_PROGRESS":
            body = f"Your {clean_type} report has been assigned for campus response."
        else:
            body = f"Your {clean_type} report status updated to {new_status}."

        return self.dispatch_push_to_user(
            db=db,
            recipient_user_id=recipient.user_id,
            title=title,
            body=body,
            event_type="REPORT_STATUS_CHANGED",
            target_path=f"/student/reports?report_id={report.report_id}",
            report_id=report.report_id,
        )

    # --------------------------------------------------------------------------
    # Audit Persistence Helper
    # --------------------------------------------------------------------------

    def _record_notification(
        self,
        db: Optional[Session],
        recipient_user_id: uuid.UUID,
        status: str,
        title: Optional[str] = None,
        body: Optional[str] = None,
        notification_type: Optional[str] = None,
        task_id: Optional[int] = None,
        report_id: Optional[int] = None,
        provider_msg_id: Optional[str] = None,
        error_message: Optional[str] = None,
    ) -> None:
        """Safely saves an audit record in task_notifications."""
        if db is None:
            return
        try:
            record = TaskNotification(
                task_id=task_id,
                report_id=report_id,
                recipient_user_id=recipient_user_id,
                channel="PUSH",
                notification_type=notification_type,
                title=title[:200] if title else None,
                body=body,
                status=status,
                provider_msg_id=provider_msg_id[:100] if provider_msg_id else None,
                error_message=error_message,
            )
            db.add(record)
            db.commit()
        except Exception as exc:
            logger.warning(f"Could not persist TaskNotification record: {exc}")
            try:
                db.rollback()
            except Exception:
                pass


push_notification_service = PushNotificationService()
