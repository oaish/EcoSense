# EcoSense — Firebase Cloud Messaging (FCM) Web Push Notifications Architecture & Setup Guide

This guide details the integration of Firebase Cloud Messaging (FCM) Web Push notifications in EcoSense, replacing the legacy SMS Horizon integration while completely preserving collector phone numbers and notification operational history.

---

## 1. Executive Summary & Migration Overview

EcoSense operates as a zero-waste campus management platform at Don Bosco Institute of Technology (DBIT), Mumbai. Web push notifications provide real-time operational alerts for task assignments, collection schedules, and waste report response without ongoing SMS gateway costs.

### 1.1 SMS Components Removed
- **Removed Service**: `backend/app/services/sms_service.py` (and all HTTP calls to `smshorizon.co.in/api/v2/sendsms.php`).
- **Removed Configuration**: `SMS_HORIZON_*` variables from `backend/app/core/config.py` and active configuration.
- **Removed Obsolete Tests**: `backend/tests/test_sms_operations.py` replaced by `backend/tests/test_push_notifications.py`.
- **Cleaned UI**: Removed "SMS Horizon Notifications" banners and SMS badges from `AdminCollectorOperationsPage.tsx`.

### 1.2 Critical Data Preserved
- **Collector Phone Numbers**: `users.phone_number` column and administrative phone management functionality (`PATCH /api/v1/users/{user_id}/phone`) remain 100% active and untouched. Phone numbers are preserved for direct communication.
- **Notification History**: The existing `task_notifications` table was evolved rather than dropped. All historical SMS logs remain stored with `channel = 'SMS'` and original `provider_msg_id` values intact.
- **Unrelated Modules**: Attendance, gamification ledger, QR scanning, bin fill readings, waste classifications, and RBAC remain intact with 0 regressions.

---

## 2. Firebase Project & Web Push Configuration

To activate live web push notifications, configure your Firebase project in the Firebase Console:

### 2.1 Firebase Project Setup
1. Open the [Firebase Console](https://console.firebase.google.com/).
2. Create or select your project (e.g., `ecosense-dbit`).
3. Under **Project Settings** > **General**, register a **Web App** (e.g., `EcoSense Web`).
4. Copy the public Firebase SDK configuration credentials:
   - `apiKey`
   - `authDomain`
   - `projectId`
   - `storageBucket`
   - `messagingSenderId`
   - `appId`

### 2.2 Web Push / VAPID Key Pair Generation
1. In Firebase Console, navigate to **Project Settings** > **Cloud Messaging**.
2. Scroll to the **Web configuration** section (**Web Push certificates**).
3. Click **Generate key pair**.
4. Copy the generated public key. This is your `VITE_FIREBASE_VAPID_KEY`.
   *(Note: The VAPID public key is safe for frontend use and proves to browser push services that notifications originate from your authorized server).*

### 2.3 Firebase Admin SDK Service Account Setup
1. In Firebase Console, navigate to **Project Settings** > **Service accounts**.
2. Select **Python** and click **Generate new private key**.
3. Download the JSON key file.
4. Place the file outside publicly served directories, for example:
   `backend/secrets/serviceAccountKey.json`.
5. Ensure the file is ignored by git (`.gitignore` contains `*firebase*.json`, `*serviceAccount*.json`, `secrets/`).
6. Set `FIREBASE_SERVICE_ACCOUNT_PATH=secrets/serviceAccountKey.json` in `backend/.env`.

---

## 3. Environment Variables Reference

### Backend (`backend/.env`)

```env
# Database & Authentication
DATABASE_URL=postgresql+psycopg://postgres:postgres@localhost:5432/ecosense
JWT_SECRET_KEY=your_jwt_secret_key

# Firebase Cloud Messaging (Web Push)
FIREBASE_PUSH_ENABLED=true
FIREBASE_PROJECT_ID=your_firebase_project_id
FIREBASE_SERVICE_ACCOUNT_PATH=secrets/serviceAccountKey.json

# Public Deployment Hostnames (Cloudflare Tunnel)
PUBLIC_FRONTEND_URL=https://ecosenseapp.site
PUBLIC_BACKEND_URL=https://api.ecosenseapp.site
```

### Frontend (`frontend/.env`)

```env
# Backend API Base URL
VITE_API_BASE_URL=http://localhost:8000

# Firebase Web App Public Configuration
VITE_FIREBASE_API_KEY=AIzaSy...
VITE_FIREBASE_AUTH_DOMAIN=your_project.firebaseapp.com
VITE_FIREBASE_PROJECT_ID=your_firebase_project_id
VITE_FIREBASE_STORAGE_BUCKET=your_project.appspot.com
VITE_FIREBASE_MESSAGING_SENDER_ID=123456789012
VITE_FIREBASE_APP_ID=1:123456789012:web:abcdef123456
VITE_FIREBASE_VAPID_KEY=B...YourVapidPublicKeyHere...
```

> [!IMPORTANT]
> Never put Firebase Admin service account keys or private keys into frontend `.env` files or commit them to source control.

---

## 4. Architecture & Implementation Details

```mermaid
sequenceDiagram
    participant User as Collector / Admin Browser
    participant SW as Service Worker (sw.js)
    participant FCM as Firebase Cloud Messaging
    participant API as FastAPI Backend
    participant DB as PostgreSQL

    Note over User,SW: 1. Token Registration Flow
    User->>User: Clicks "Enable Push"
    User->>SW: navigator.serviceWorker.register('/firebase-messaging-sw.js')
    User->>FCM: getToken(messaging, { vapidKey })
    FCM-->>User: Returns FCM Device Token
    User->>API: POST /api/v1/notifications/tokens (Bearer JWT)
    API->>DB: Upsert into device_tokens (is_active=true)

    Note over API,FCM: 2. Operational Trigger (e.g. Task Assigned)
    API->>DB: INSERT collection_tasks & COMMIT
    API->>DB: Query active tokens for collector
    API->>FCM: messaging.send(multicast_message)
    FCM-->>API: Provider Msg ID / UnregisteredError
    API->>DB: INSERT task_notifications audit record (channel='PUSH')

    Note over SW,User: 3. Notification Arrival & Navigation
    FCM->>SW: Push event / onBackgroundMessage
    SW->>User: showNotification("Task Assigned", "Collect Bin B01")
    User->>SW: Clicks Notification
    SW->>User: Focuses browser & navigates to internal route (/collector/tasks)
```

### 4.1 Database Models & Migration `0011_device_tokens_fcm`
1. **`device_tokens` Table**:
   - `token_id` (BigInteger PK)
   - `user_id` (UUID FK to `users.user_id`, CASCADE)
   - `fcm_token` (VARCHAR(512), unique, indexed)
   - `device_name` (VARCHAR(100), optional device/browser label)
   - `is_active` (Boolean, default True, indexed)
   - `created_at`, `updated_at` (Timestamps)
2. **`task_notifications` Table Evolution**:
   - `task_id`: Altered to `nullable=True` (permits non-task push notifications like report status).
   - `report_id`: Added BigInteger FK to `waste_reports.report_id` (nullable=True).
   - `notification_type`: VARCHAR(50) (e.g. `TASK_ASSIGNED`, `REPORT_STATUS_CHANGED`).
   - `title`: VARCHAR(200) nullable.
   - `body`: TEXT nullable.
   - `channel`: Default updated to `PUSH` (existing rows remain `SMS`).
3. **`users.push_notifications_enabled`**:
   - Boolean default `true` for individual account preference control.

### 4.2 Service Worker Architecture
- **Location**: `frontend/public/firebase-messaging-sw.js` (automatically bundled to `/firebase-messaging-sw.js` at root scope `/`).
- **Background Message Handling**: Extracts operational title, body, and internal deep-links. Shows system notification with DBIT EcoSense leaf icon (`/leaf.svg`).
- **Click Navigation**: Strictly validates the target URL origin to match `self.location.origin` before focusing existing tabs or opening safe internal routes (`/collector/tasks`, `/admin/reports`, `/student/reports`). Never executes untrusted external redirects.

### 4.3 Foreground Notification Toast
When EcoSense is open in the active browser tab, `onForegroundMessage` triggers an interactive toast in the bottom-right corner of the application (`ForegroundNotificationBanner`), enabling direct one-click navigation to the referenced task or report without duplicate OS-level notifications.

### 4.4 Graceful Fallback
When `FIREBASE_PUSH_ENABLED=false` or Firebase credentials are not supplied:
- FastAPI starts up completely normally.
- Authentication, check-ins, task assignments, and waste reports function with zero disruption.
- Notification dispatch is safely skipped and recorded with status `SKIPPED_DISABLED` or `SKIPPED_NOT_CONFIGURED`.
- Expired or invalid tokens automatically transition to `is_active = false` without impacting business transactions.

---

## 5. API Endpoints

All notification endpoints require valid JWT authentication:

| Method | Endpoint | Description |
|---|---|---|
| `POST` | `/api/v1/notifications/tokens` | Registers or re-associates an FCM token with authenticated user |
| `DELETE` | `/api/v1/notifications/tokens` | Deactivates token owned by authenticated user (e.g. on logout) |
| `GET` | `/api/v1/notifications/preferences` | Retrieves push preference status and active device count |
| `PUT` | `/api/v1/notifications/preferences` | Updates push notifications preference toggle |
| `GET` | `/api/v1/notifications/history` | Retrieves notification dispatch audit records |
| `POST` | `/api/v1/notifications/test` | Dispatches a test push notification to caller's registered devices |

---

## 6. Cloudflare Tunnel & Android Chrome Configuration

### 6.1 Public Origin Consistency
When serving EcoSense through Cloudflare Tunnel (e.g. `https://ecosenseapp.site`):
- Ensure `PUBLIC_FRONTEND_URL` in `backend/.env` matches the public HTTPS frontend hostname.
- Notification payloads link to `PUBLIC_FRONTEND_URL` (never `localhost` or local LAN IP).
- Cloudflare Tunnel serves the frontend over HTTPS, which is **mandatory** for Service Workers and Push API.

### 6.2 Service Worker Caching & Headers
Ensure your Cloudflare Tunnel / reverse proxy does not cache `firebase-messaging-sw.js`:
- `Cache-Control: no-cache, no-store, must-revalidate`
- `Content-Type: application/javascript; charset=utf-8`

### 6.3 Android Chrome Considerations
1. Open `https://ecosenseapp.site` in Chrome on Android.
2. Log in as a Collector or Student.
3. Tap the **Bell** icon in the header to open **Notification Settings**.
4. Tap **Enable Push**. When prompted by Android Chrome, tap **Allow**.
5. Once granted, verify that the device token shows as **Registered**.
6. Use **Send Test Alert** to verify prompt reception in the Android notification shade.

---

## 7. Verification & Testing

### 7.1 Automated Backend Suite
```bash
cd backend
.\.venv\Scripts\pytest tests/test_push_notifications.py -v
```
*Result: 22 passed.*

Full suite:
```bash
.\.venv\Scripts\pytest -q
```
*Result: 239 passed, 4 skipped, 0 failed.*

### 7.2 Automated Frontend Suite & Production Build
```bash
cd frontend
npm test
npm run build
```
*Result: 9 test files, 38 passed. TypeScript compiled cleanly, dist bundle generated with service worker.*

---

## 8. Known Limitations & Best Practices

1. **Best-Effort Delivery**: Web Push delivery depends on device power management (Android Doze mode), network connectivity, and browser background process restrictions. Push notifications must never be the sole source of truth; tasks and reports remain authoritatively recorded in the PostgreSQL database.
2. **Account Switching**: When a user logs out, the frontend unregisters the token with the backend and purges local storage. When a different user logs in on the same browser, registering the token re-associates it with the new user ID to prevent cross-account notification leaks.
3. **Private Window / Incognito**: Web Push notifications and persistent service worker registrations are blocked by design in private browsing modes across most modern browsers.
