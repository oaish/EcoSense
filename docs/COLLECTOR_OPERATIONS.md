# EcoSense — Collector Attendance, Availability & Task Management

**Institution**: Don Bosco Institute of Technology (DBIT), Mumbai  
**Project**: EcoSense — AI-Based Zero Waste Campus Management Platform  
**Module**: Collector Daily Attendance, Real-Time Availability & Collection Task Operations  

---

## 1. Executive Summary

The Collector Operations module bridges administrative oversight and daily physical waste management across the DBIT campus. It enables collectors to record app-based shift check-ins and check-outs, view and update assigned field tasks, link completed collections to verifiable bin telemetry, and respond to delegated student/staff waste issue reports.

---

## 2. Collector Attendance Workflow

### 2.1 Daily Shift Lifecycle
1. **Start Shift (Check-In)**:
   - At the beginning of their campus shift, the authenticated collector taps **"Start Shift"** on their Field Operations Hub.
   - The backend validates the authenticated JWT (`COLLECTOR` role), captures the server-side timezone-aware timestamp, and records the current campus date (`Asia/Kolkata` / IST).
   - The record enters status `ON_SHIFT` with `check_in_at` recorded.
   - At most **one active shift** is allowed per collector at any time (enforced via partial PostgreSQL unique constraint `uq_collector_active_shift`).
2. **Shift Active**:
   - The collector interface shows an active shift indicator and timestamp.
   - Administrators see the collector listed as **ON SHIFT** with their active check-in time and current job count.
3. **End Shift (Check-Out)**:
   - When finishing their duties, the collector taps **"End Shift"**.
   - The backend updates `check_out_at` and sets the session status to `CHECKED_OUT`.
   - The collector can check in again later if working a split shift; all historical sessions are preserved.
4. **Forgotten Check-Out Policy**:
   - Active sessions are never silently auto-closed with invented timestamps.
   - Open shifts from previous days remain flagged for administrative review on the Admin Collector Operations dashboard.

### 2.2 Campus Timezone Handling
- The campus date is governed by `settings.CAMPUS_TIMEZONE` (`"Asia/Kolkata"`), preventing shifts logged before UTC midnight (5:30 AM IST) from being misattributed to the previous day.

---

## 3. Admin Collector Availability Dashboard

**Route**: `/admin/collector-operations`

### 3.1 Real-Time KPI Cards
Derived directly from PostgreSQL queries (no hardcoded or simulated statistics):
1. **Active Accounts**: Total registered collector accounts (`is_active = True`).
2. **On Shift Today**: Collectors with an active session (`status = 'ON_SHIFT'`) on today's campus date.
3. **Not Checked In**: Active collectors who have not started a shift today.
4. **Active Workload**: Number of collectors with assigned/accepted/in-progress tasks.
5. **Overdue Tasks**: Tasks whose `due_date` is earlier than current campus time and status is not `COMPLETED` or `CANCELLED`.

### 3.2 Collector Availability Table
- **Collector Profile**: Full name and institutional email.
- **Attendance Status Badge**: `ON_SHIFT` (live pulsing indicator), `CHECKED_OUT`, or `NOT_CHECKED_IN`.
- **Shift Timestamps**: Exact IST check-in and check-out times.
- **Active Task Count & Workload Level**: Tagged as `Available` (0 tasks), `Moderate` (1–2 tasks), or `Heavy` (3+ tasks).
- **Actions**:
  - **History**: Opens an attendance log modal showing dates, check-in, check-out, and notes.
  - **Assign**: Quick launcher for task assignment pre-selecting the collector.

---

## 4. Collection Task Management

### 4.1 Task Types
| Task Type | Description | Required References |
|---|---|---|
| `COLLECTION` | Empty or service a campus bin | `bin_id` (Bin entity) |
| `INSPECTION` | Inspect a bin or facility location | `bin_id` or `location_id` |
| `ISSUE_RESPONSE` | Investigate and address a campus waste report | `report_id` (WasteReport entity) |

### 4.2 Task Status Lifecycle
```
[ASSIGNED] ──(Collector accepts)──> [ACCEPTED] ──(Collector starts)──> [IN_PROGRESS] ──(Evidence verified)──> [COMPLETED]
     │                                     │                                  │
     └─────────────────────────────────────┴──────────────────────────────────┴───────(Admin cancels)───────> [CANCELLED]
```
- **ASSIGNED**: Administrator has created the task assignment.
- **ACCEPTED**: Collector acknowledges the assignment.
- **IN_PROGRESS**: Collector initiates work on campus.
- **COMPLETED**: Collector submits required evidence (see Section 6).
- **CANCELLED**: Administrator cancels the task with an audit reason.

### 4.3 Assignment & Reassignment Rules
1. **Eligibility**: Tasks can be assigned only to active collector accounts (`COLLECTOR` role, `is_active=True`).
2. **Availability Preference**: On-shift collectors are highlighted first in assignment dropdowns.
3. **Off-Shift Warning**: If an administrator selects an off-shift collector, a warning banner is displayed. The assignment is permitted for urgent tasks.
4. **Audit Trail**: Reassigning a task creates an audit trail preserving `cancellation_reason` and historical logs without destroying task records.

---

## 5. Waste Report Delegation

**Route**: `/admin/reports`

- When administrators review student or staff waste issue reports (overflowing bins, broken lids, missing bins, wrong segregation), they can tap **"Assign Collector"**.
- An `ISSUE_RESPONSE` task is created referencing the original `report_id`, bin, and location.
- The waste report status updates to `IN_PROGRESS`.
- **Preserved Lifecycle**: Completing an `ISSUE_RESPONSE` task does **not** automatically mark the report `RESOLVED`. Only authorized administrators can formally resolve reports to trigger gamification points awarding.

---

## 6. Collection Workflow & Evidence Verification

- For `COLLECTION` tasks, a collector must empty the bin using the existing collection workflow (`/collector/scan` or logging a collection record).
- To mark a `COLLECTION` task as `COMPLETED`, the system requires verification of a valid `CollectionRecord` (`collection_id`) associated with that bin.
- Retrying completion uses idempotent database updates, avoiding duplicate collection records.
- For `INSPECTION` and `ISSUE_RESPONSE` tasks, non-empty `completion_notes` are required as qualitative evidence.

---

## 7. API Endpoints and Authorization

### Attendance Endpoints (`/api/v1/attendance`)
| Method | Endpoint | Allowed Roles | Description |
|---|---|---|---|
| `POST` | `/api/v1/attendance/check-in` | `COLLECTOR` | Start daily shift session |
| `POST` | `/api/v1/attendance/check-out` | `COLLECTOR` | End active shift session |
| `GET` | `/api/v1/attendance/me` | `COLLECTOR` | Get current active shift |
| `GET` | `/api/v1/attendance/me/history` | `COLLECTOR` | Get own attendance history |
| `GET` | `/api/v1/attendance/admin/overview` | `ADMIN` | Get campus availability summary & metrics |
| `GET` | `/api/v1/attendance/admin/collector/{id}` | `ADMIN` | Get specific collector attendance history |

### Collection Task Endpoints (`/api/v1/tasks`)
| Method | Endpoint | Allowed Roles | Description |
|---|---|---|---|
| `POST` | `/api/v1/tasks` | `ADMIN` | Create and assign a task |
| `POST` | `/api/v1/tasks/delegate-report` | `ADMIN` | Delegate waste report to collector |
| `GET` | `/api/v1/tasks` | `ADMIN` | List all campus tasks (filterable) |
| `GET` | `/api/v1/tasks/me` | `COLLECTOR` | List own assigned tasks |
| `GET` | `/api/v1/tasks/{id}` | `ADMIN`, `COLLECTOR` (own) | Get task details |
| `PATCH`| `/api/v1/tasks/{id}/status` | `ADMIN`, `COLLECTOR` (own) | Update task lifecycle status |
| `POST` | `/api/v1/tasks/{id}/reassign` | `ADMIN` | Reassign task to another collector |
| `POST` | `/api/v1/tasks/{id}/cancel` | `ADMIN` | Cancel task with audit reason |

---

## 8. Database Migrations

### Alembic Revisions
1. **Revision `0009_collector_attendance_tasks` (`0009_collector_attendance_and_tasks.py`)**:
   - `collector_attendance` table: Tracks daily shifts, check-in, check-out, and active shift uniqueness (`uq_collector_active_shift`).
   - `collection_tasks` table: Stores assignment records, prioritization, lifecycle status, proof-of-work link, and cancellation audit.
2. **Revision `0010_collector_phone_sms` (`0010_add_user_phone_and_notifications.py`)**:
   - `users.phone_number`: Nullable `VARCHAR(20)` column storing normalized E.164 phone numbers (e.g. `+919876543210`).
   - `task_notifications` table: Audit log for SMS notifications dispatched to collectors:
     - `notification_id` (Primary Key, integer autoincrement)
     - `task_id` (Foreign Key -> `collection_tasks.task_id`, indexed)
     - `recipient_user_id` (Foreign Key -> `users.user_id`, indexed)
     - `channel` (`VARCHAR(20)`, default `"SMS"`)
     - `status` (`VARCHAR(30)`: `SENT_OR_ACCEPTED`, `FAILED`, `SKIPPED_NO_PHONE`, `SKIPPED_DISABLED`, `SKIPPED_NOT_CONFIGURED`, indexed)
     - `provider_msg_id` (`VARCHAR(100)`, nullable)
     - `error_message` (`TEXT`, nullable, sanitized without credentials)
     - `created_at` (`TIMESTAMPTZ`, default `now()`)

---

## 9. SMS Horizon Integration & Collector Phone Management

EcoSense uses the official **SMS Horizon HTTP API v2** for automated collector SMS notifications across campus.

### 9.1 Collector Phone Number Management
- **Administrative Control**: Only authorized administrators can configure or update collector contact numbers (`PATCH /api/v1/users/{id}/phone` or via the User Management modal).
- **Format Normalization**: All numbers are validated and converted to standard international E.164 format (`+91XXXXXXXXXX` for Indian mobile numbers starting with 6, 7, 8, or 9).
- **Privacy & Security**:
  - Phone numbers are never exposed to students or unauthorized roles.
  - Numbers are never logged in full plain text; the backend utility `mask_phone_number()` masks digits (e.g. `+91******3210`).
  - Existing collectors without phone numbers continue to function normally.

### 9.2 Firebase Cloud Messaging (FCM) Web Push Architecture
- **Protocol**: Web Push Protocol (RFC 8030, RFC 8291, RFC 8292) over HTTPS with VAPID authorization.
- **Provider**: Firebase Cloud Messaging (FCM) official Google Admin SDK for Python and Firebase JavaScript SDK v10+ modular client.
- **Service Worker**: `frontend/public/firebase-messaging-sw.js` running at root scope `/` for background push reception and click routing.
- **Device Registration**: Multi-device support via `device_tokens` table. Authenticated users register FCM tokens via `POST /api/v1/notifications/tokens`.
- **Deep-Link Targets**: Notifications contain validated internal routes (`/collector/tasks?task_id=...`, `/admin/reports?report_id=...`).
- **Legacy SMS Transition**: The previous SMS Horizon gateway integration has been retired and removed from active configuration. Historical SMS dispatch audit rows remain preserved in `task_notifications` (`channel = 'SMS'`).

### 9.4 Critical Transaction Safety
- **Post-Commit Dispatch**: Database records (`CollectionTask`, `WasteReport`, `CollectionRecord`) are always committed to PostgreSQL **before** push dispatch is attempted.
- **Fault Tolerance**: A Firebase failure, network timeout, or expired token will **never** roll back the task assignment or raise an unhandled exception to the client.
- **Provider Acceptance vs. Delivery**: Acceptance by Firebase Cloud Messaging indicates successful receipt and queueing by FCM servers. Push notifications are best-effort alerts and depend on browser state, network, and device notification permissions.
- **Collector Phone Preservation**: Administrator-managed collector phone numbers (`users.phone_number`) remain preserved in PostgreSQL for direct operational contact. Historical SMS audit records remain preserved in `task_notifications` with `channel='SMS'`.

### 9.5 Environment Configuration

Backend (`backend/.env`):
```env
# Firebase Cloud Messaging (FCM) Web Push Configuration
FIREBASE_PUSH_ENABLED=true
FIREBASE_PROJECT_ID=your_firebase_project_id
FIREBASE_SERVICE_ACCOUNT_PATH=secrets/serviceAccountKey.json
PUBLIC_FRONTEND_URL=https://ecosenseapp.site
PUBLIC_BACKEND_URL=https://api.ecosenseapp.site
```

Frontend (`frontend/.env`):
```env
# Firebase Web App Client Configuration
VITE_FIREBASE_API_KEY=your_firebase_api_key
VITE_FIREBASE_AUTH_DOMAIN=your_project.firebaseapp.com
VITE_FIREBASE_PROJECT_ID=your_firebase_project_id
VITE_FIREBASE_STORAGE_BUCKET=your_project.appspot.com
VITE_FIREBASE_MESSAGING_SENDER_ID=your_messaging_sender_id
VITE_FIREBASE_APP_ID=your_firebase_app_id
VITE_FIREBASE_VAPID_KEY=your_public_vapid_key
```

---

## 10. Automated Testing Results

### Backend Test Suite (`pytest`)
- **Dedicated Push & Phone Suite**: `backend/tests/test_push_notifications.py` (22 automated tests).
  - Validates E.164 phone normalization, phone masking, admin update endpoints, student/unauthenticated RBAC blocking, historical SMS notification row preservation, graceful Firebase initialization when disabled/unconfigured, device token registration, idempotent updates, token transfer on account switch, token removal, user preferences toggle, mocked Firebase dispatch, token self-cleanup on UnregisteredError, task assignment, reassignment, and report delegation hooks.
- **Overall Suite**:
  - Total collected: **243 test items**
  - Passed: **239 passed**, 4 skipped (fastai tests requiring mock classifier weights)
  - Regression: **0 regressions** across all existing modules.

### Frontend Test Suite (`vitest` & `tsc`)
- **Collector & Admin Operations**: `frontend/src/tests/collector_operations.test.tsx` (4 automated tests).
- **Push Notification UI & Context**: `frontend/src/tests/push_notifications.test.tsx` (4 automated tests).
- **Overall Suite**:
  - **9 test files, 38 tests passed** with 0 errors.
- **Production Build**:
  - `npm run build` (`tsc && vite build`) compiles with zero TypeScript errors.

---

## 11. Known Limitations
- Attendance verification is app-based; biometric hardware integration or campus geofencing is deliberately excluded.
- Handset delivery receipts (DLR) require configuring SMS Horizon webhook callbacks; current tracking captures gateway queue acceptance (`SENT_OR_ACCEPTED`).
- Live SMS dispatch requires valid DLT entity registration and sender ID approved on Indian telecom networks.

