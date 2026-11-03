# EcoSense — Complete Startup, Running & Full-System Testing Guide

**Institution:** Don Bosco Institute of Technology (DBIT), Mumbai  
**Project:** EcoSense — AI-Based Zero Waste Campus Management Platform  

---

## 📌 Table of Contents
1. [Prerequisites & System Requirements](#1-prerequisites--system-requirements)
2. [Method A: Running with Docker Compose (Recommended)](#2-method-a-running-with-docker-compose-recommended)
3. [Method B: Running Locally (FastAPI + Vite)](#3-method-b-running-locally-fastapi--vite)
4. [Pre-Seeded Demo User Accounts](#4-pre-seeded-demo-user-accounts)
5. [End-to-End Testing & Verification Walkthrough](#5-end-to-end-testing--verification-walkthrough)
   - [🎓 Flow 1: Student Gamified Experience](#-flow-1-student-gamified-experience)
   - [🏢 Flow 2: Staff Operational Monitoring](#-flow-2-staff-operational-monitoring)
   - [🚛 Flow 3: Collector Field Operations](#-flow-3-collector-field-operations)
   - [⚡ Flow 4: Admin Control Center & Analytics](#-flow-4-admin-control-center--analytics)
6. [Automated Backend & Frontend Test Suites](#6-automated-backend--frontend-test-suites)
7. [Troubleshooting & FAQs](#7-troubleshooting--faqs)

---

## 1. Prerequisites & System Requirements

Ensure you have either Docker Desktop or a local Python + Node.js environment installed:

| Tool | Version Requirement | Purpose |
| :--- | :--- | :--- |
| **Docker Desktop** | Latest (WSL 2 on Windows) | Multi-container full-stack execution |
| **Python** | Python 3.11 or 3.12 | Backend development & pytest execution |
| **Node.js** | Node.js v18+ or v20+ (npm 10+) | Frontend development & Vite build |
| **PostgreSQL** | v15+ or v16+ | Local database (if not using Docker) |

---

## 2. Method A: Running with Docker Compose (Recommended)

### Step 1: Ensure Docker Desktop is Running
On Windows, make sure **Docker Desktop** is running:
1. Search for **Docker Desktop** in the Windows Start Menu and launch it.
2. Wait until the Docker whale icon in your system tray shows **"Docker Desktop is running"**.

> **Note on Windows Error:** If you see `failed to connect to the docker API at npipe:////./pipe/dockerDesktopLinuxEngine`, it simply means the Docker Desktop application has not been opened yet. Launching Docker Desktop resolves this immediately.

### Step 2: Start All Services
Open a terminal in the root directory `c:\dev\web\EcoSense` and run:

```bash
docker compose up --build
```

### What happens automatically:
1. **`ecosense-postgres`** initializes with persistent volume `postgres_data` on port `5432`.
2. **`ecosense-backend`** waits for Postgres to become healthy, runs `alembic upgrade head`, seeds initial DBIT data, and launches FastAPI on port `8000`.
3. **`ecosense-frontend`** builds the production React + TypeScript application and serves it via high-performance Nginx on port `5173`.

### Access URLs:
- 🌐 **Frontend Web App:** [http://localhost:5173](http://localhost:5173)
- 🔌 **FastAPI Backend API:** [http://localhost:8000](http://localhost:8000)
- 📖 **Interactive Swagger UI:** [http://localhost:8000/docs](http://localhost:8000/docs)
- 📚 **ReDoc Documentation:** [http://localhost:8000/redoc](http://localhost:8000/redoc)
- 💓 **Health Check Endpoint:** [http://localhost:8000/health](http://localhost:8000/health)

### Stopping the Services:
```bash
# Stop containers and preserve database records:
docker compose down

# Stop containers AND reset database to a clean state:
docker compose down -v
```

---

## 3. Method B: Running Locally (FastAPI + Vite)

If you prefer to run the services directly in terminal windows without Docker:

### Terminal 1: Backend (FastAPI + PostgreSQL)
```powershell
cd c:\dev\web\EcoSense\backend

# Activate virtual environment:
.\.venv\Scripts\activate

# Run migrations:
alembic upgrade head

# Seed initial roles and test accounts:
python scripts\seed_dev_data.py

# Start FastAPI server:
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Terminal 2: Frontend (React + Vite)
```powershell
cd c:\dev\web\EcoSense\frontend

# Start Vite dev server:
npm run dev
```

Open [http://localhost:5173](http://localhost:5173) in your browser.

---

## 4. Pre-Seeded Demo User Accounts

You can log in using either the quick-login buttons on the login page or with the following credentials:

| Role | Email | Password | Default Home | Key Permissions |
| :--- | :--- | :--- | :--- | :--- |
| **🎓 Student** | `student@dbit.in` | `Password123!` | `/student/dashboard` | Scan bins, record disposals, earn points, AI classify, redeem rewards, file reports |
| **🏢 Staff** | `staff@dbit.in` | `Password123!` | `/staff/dashboard` | Monitor campus reports, inspect bin fill levels, AI classify |
| **🚛 Collector** | `collector@dbit.in` | `Password123!` | `/collector/dashboard` | Scan bins, record fill telemetry, log collections, recycling/composting batches |
| **⚡ Admin** | `admin@dbit.in` | `Password123!` | `/admin/dashboard` | 13-tab analytics, deploy bins, resolve reports with points, manage reward store, ledger adjustments |

---

## 5. End-to-End Testing & Verification Walkthrough

Follow these 4 guided test flows to test the entire application in full:

---

### 🎓 Flow 1: Student Gamified Experience

1. **Log In:** Go to [http://localhost:5173/login](http://localhost:5173/login) and click **"🎓 Student"** (or enter `student@dbit.in` / `Password123!`).
2. **Explore Student Dashboard (`/student/dashboard`):**
   - Check the **Points Card** displaying your active ledger balance and active streak.
   - View quick action cards: *Scan a Bin*, *AI Classifier*, and *Report Waste Issue*.
3. **AI Waste Classifier (`/classify`):**
   - Click **"AI Classifier"** on the sidebar or home screen.
   - Click one of the quick samples (e.g. *Plastic Bottle*, *Cardboard Box*, or *Banana Peel*).
   - Click **"Classify Waste Item"**.
   - Observe the predicted category (e.g. `DRY RECYCLABLE`), model version, confidence rating, and the color-coded bin recommendation banner.
4. **Scan Bin & Record Disposal (`/scan`):**
   - Click **"Scan Bin & Earn"**.
   - Under *Manual QR Token Entry*, enter one of the campus bin QR tokens:
     - `550e8400-e29b-41d4-a716-446655440001` (or any active bin UUID)
     - Click **Lookup**.
   - Verify the bin details card shows the bin code (`BIN-DBIT-001`), location, designated waste type, and fill progress bar.
   - Enter optional weight (e.g. `0.25` kg) and notes (`Plastic bottle disposal`), then click **"Record Disposal & Earn Points"**.
   - 🎉 **Watch the Confetti & Celebration Modal** award **+10 Points**!
5. **Reward Store & Redemption (`/rewards`):**
   - Navigate to **"Rewards & Store"**.
   - Review available campus perks (e.g. *Campus Eco Badge*, *Cafeteria Discount Coupon*).
   - Click **"Redeem"** on an affordable reward.
   - Confirm redemption and see your points balance deduct with instant celebration feedback!
   - Click **"Redemption History"** (`/rewards/history`) to verify your claim.
6. **Submit Waste Report (`/student/report`):**
   - Click **"Report Waste"**.
   - Select an issue type (e.g. *Overflowing Bin*), select a bin, type a description, and submit.
   - View your report in **"My Reports"** (`/student/reports`).

---

### 🏢 Flow 2: Staff Operational Monitoring

1. **Log In:** Log out and log in as **`staff@dbit.in`** / `Password123!`.
2. **Staff Dashboard (`/staff/dashboard`):**
   - Review open issue count, high-fill bins, and active campus units.
3. **Inspect Campus Waste Reports (`/staff/reports`):**
   - Filter reports by status (*Pending*, *In Progress*, *Resolved*).
4. **Inspect Campus Bins (`/staff/bins`):**
   - Search bins by building or code to inspect current fill telemetry.

---

### 🚛 Flow 3: Collector Field Operations

1. **Log In:** Log out and log in as **`collector@dbit.in`** / `Password123!`.
2. **Collector Hub (`/collector/dashboard`):**
   - Check high-priority bins requiring emptying (fill $\ge 80\%$).
3. **Scan & Collect Bin (`/collector/scan`):**
   - Enter QR token `550e8400-e29b-41d4-a716-446655440001` and click **Lookup**.
   - **Log Fill Reading:** Switch to *Log Fill Reading*, set the slider to `90%`, and click *Update Fill State*.
   - **Record Waste Collection:** Switch to *Record Collection*, set *Fill Before* (`90%`), *Fill After* (`0%`), *Collected Weight* (`8.5` kg), and click *Complete & Log Collection*.
4. **View Collections Log (`/collector/collections`):**
   - Verify the collection record is logged in the timeline.
5. **Log Processing Batch (`/collector/processing`):**
   - Click **"Log Processing Batch"**.
   - Select the source collection, pick **"🍂 Composting"** or **"♻️ Recycling"**, enter quantity (`8.5` kg), and submit.
6. **AI Fill Predictions (`/collector/predictions`):**
   - Select a campus bin and choose a forecast horizon (e.g. *2 Hours*).
   - Click **"Generate Forecast"** to receive future fill accumulation telemetry.

---

### ⚡ Flow 4: Admin Control Center & Analytics

1. **Log In:** Log out and log in as **`admin@dbit.in`** / `Password123!`.
2. **Admin Dashboard (`/admin/dashboard`):**
   - Inspect the campus overview KPIs: *Total Waste Collected*, *Campus Landfill Diversion Rate*, *Active Students*, and *Points Distributed*.
   - Review real-time operational alerts.
3. **Deep Analytics Suite (`/admin/analytics`):**
   - Explore all 12 interactive analytics tabs:
     - 📊 **Summary:** Key operational and diversion aggregates.
     - ♻️ **Waste Types:** Breakdown across dry recyclables, compostable organics, and e-waste.
     - 📍 **Locations:** Waste generation across campus buildings.
     - 📈 **Trends:** Daily and weekly time-series trends.
     - 🚛 **Collections:** Average batch weights and servicing frequency.
     - 🗑️ **Bin Fill:** Monitored units and high-fill lists.
     - ⚠️ **Reports:** Breakdown of issue categories and resolution rates.
     - 🍂 **Processing:** Recycling vs. composting batches.
     - 🎓 **Participation:** Top contributing student leaderboard.
     - ⭐ **Gamification:** Points distributed vs. redeemed and top rewards.
     - 🔮 **Predictions:** Machine learning fill forecast counts.
     - 🤖 **AI Classifications:** Vision model confidence and category distributions.
4. **Bin & Location Management (`/admin/bins`, `/admin/locations`):**
   - Deploy new bins, inspect status, view and copy QR tokens.
   - Add new campus buildings or floor zones.
5. **Resolve Problem Reports (`/admin/reports`):**
   - Open a pending student report and click **"Resolve"**.
   - Enter resolution notes and submit — this automatically awards resolution points to the reporting student!
6. **Points Ledger & Financial Adjustments (`/admin/points`):**
   - Look up any student's UUID to view their complete immutable ledger.
   - Execute an administrative point adjustment (e.g. `+50 pts`) with audit notes.

---

## 6. Automated Backend & Frontend Test Suites

### Run Backend Unit & Integration Tests (183 tests):
```powershell
cd c:\dev\web\EcoSense\backend
.\.venv\Scripts\pytest.exe -v
```
**Expected Result:** `183 passed, 0 failed` (100% pass rate).

### Run Frontend Unit Tests (7 tests):
```powershell
cd c:\dev\web\EcoSense\frontend
npm test
```
**Expected Result:** `7 passed, 0 failed`.

### Run Frontend Production Build Check:
```powershell
cd c:\dev\web\EcoSense\frontend
npm run build
```
**Expected Result:** `✓ built in ~3.5s` (0 TypeScript / compilation errors).

---

## 7. Troubleshooting & FAQs

### Q1: `failed to connect to the docker API at npipe:////./pipe/dockerDesktopLinuxEngine`
**Cause:** Docker Desktop is not open in Windows.  
**Fix:** Open **Docker Desktop** from your Windows Start Menu, wait 10–15 seconds for the engine to start, then re-run `docker compose up --build`.

### Q2: How do I test with an empty database?
Run:
```bash
docker compose down -v
docker compose up --build
```
The startup script automatically executes all migrations and seeds default test users and locations.

### Q3: How do I access the backend API documentation?
Visit [http://localhost:8000/docs](http://localhost:8000/docs) when the backend is running.
