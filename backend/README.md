# EcoSense Backend

FastAPI backend service for **EcoSense: AI-Based Zero Waste Campus Management Platform** (Don Bosco Institute of Technology, Mumbai).

---

## 1. Technical Overview

- **Python Version:** 3.11+ / 3.12+
- **Framework:** FastAPI (async-ready REST API)
- **Database:** PostgreSQL (with `pgcrypto` extension for UUID generation)
- **ORM:** SQLAlchemy 2.x (Modern Declarative Mapped models)
- **Database Driver:** `psycopg` (psycopg v3 binary)
- **Migrations:** Alembic
- **Validation & Settings:** Pydantic v2 & `pydantic-settings`
- **Authentication:** JWT (`pyjwt` with `cryptography`)
- **Password Hashing:** Argon2id (`argon2-cffi`)
- **Testing:** pytest, pytest-asyncio, httpx

---

## 2. Directory Structure

```text
backend/
│
├── app/
│   ├── __init__.py
│   ├── main.py                  # FastAPI application entrypoint & middleware
│   │
│   ├── core/                    # Core configuration & infrastructure
│   │   ├── __init__.py
│   │   ├── config.py            # Pydantic Settings (.env configuration loader)
│   │   ├── database.py          # SQLAlchemy 2.x engine, session & get_db
│   │   ├── security.py          # Argon2id hashing & JWT encode/decode
│   │   └── dependencies.py      # Auth & role-based RBAC dependencies
│   │
│   ├── models/                  # SQLAlchemy 2.x ORM models
│   │   ├── __init__.py
│   │   ├── base.py              # DeclarativeBase
│   │   ├── role.py              # Role model (STUDENT, STAFF, COLLECTOR, ADMIN)
│   │   ├── user.py              # User model (UUID, role_id FK, password_hash)
│   │   ├── location.py          # Campus Locations model
│   │   ├── waste_type.py        # Waste Classification Categories model
│   │   ├── bin.py               # Physical Bins & QR tokens model
│   │   ├── disposal.py          # Digital Waste Disposal records model
│   │   ├── report.py            # Campus Waste Issue reports model
│   │   ├── fill_reading.py      # Historical bin fill percentage readings model
│   │   ├── collection.py        # Operational waste collection records model
│   │   ├── classification.py    # AI Waste Classification event records model
│   │   ├── prediction.py        # AI Bin Fill Level Prediction forecasts model
│   │   ├── processing.py        # Recycling & Composting Processing records model
│   │   └── gamification.py      # Points ledger, Point rules, Rewards, and Redemptions models
│   │
│   ├── schemas/                 # Pydantic v2 validation models
│   │   ├── __init__.py
│   │   ├── auth.py              # Login & Token schemas
│   │   ├── user.py              # User serialization schemas
│   │   ├── location.py          # LocationCreate, LocationUpdate, LocationRead
│   │   ├── waste_type.py        # WasteTypeCreate, WasteTypeRead, WasteTypeUpdate
│   │   ├── bin.py               # BinCreate, BinUpdate, BinRead, BinQRRead
│   │   ├── disposal.py          # DisposalCreate, DisposalRead
│   │   ├── report.py            # ReportCreate, ReportUpdate, ReportRead
│   │   ├── fill_reading.py      # FillReadingCreate, FillReadingRead
│   │   ├── collection.py        # CollectionCreate, CollectionRead
│   │   ├── classification.py    # ClassificationCreate, ClassificationRead
│   │   ├── prediction.py        # PredictionRequest, PredictionRead
│   │   ├── processing.py        # ProcessingCreate, ProcessingRead
│   │   ├── gamification.py      # PointBalanceRead, PointTransactionRead, PointAdjustmentCreate, RewardCreate, RewardRead, RewardRedemptionRead
│   │   └── analytics.py         # SummaryMetrics, OperationalMetrics, TrendAnalytics, AlertItem, BinFillAnalytics
│   │
│   ├── api/                     # API routers
│   │   ├── __init__.py
│   │   └── v1/
│   │       ├── __init__.py
│   │       ├── router.py        # v1 combined router
│   │       └── endpoints/
│   │           ├── __init__.py
│   │           ├── auth.py      # POST /auth/login, GET /auth/me
│   │           ├── users.py     # GET /users/me, GET /users/admin-test
│   │           ├── locations.py # CRUD for campus locations
│   │           ├── waste_types.py # Reference & management of waste categories
│   │           ├── bins.py      # CRUD for bins & GET /bins/qr/{qr_token}
│   │           ├── disposals.py # POST /disposals, GET /disposals, GET /disposals/{id}
│   │           ├── reports.py   # POST /reports, GET /reports, GET /reports/{id}, PATCH /reports/{id}
│   │           ├── fill_readings.py # POST/GET /bins/{bin_id}/fill-readings, GET /fill-readings/{id}
│   │           ├── collections.py # POST /collections, GET /collections, GET /collections/{id}
│   │           ├── classification.py # POST /classification, GET /classification, GET /classification/{id}
│   │           ├── predictions.py # POST/GET /bins/{bin_id}/predictions, GET /predictions/{id}
│   │           ├── processing.py  # POST/GET /processing, GET /processing/{id}, /collections/{id}/processing, /bins/{id}/processing
│   │           ├── gamification.py# GET /gamification/me, GET /gamification/me/transactions, POST /gamification/users/{id}/adjust
│   │           ├── rewards.py     # GET/POST /rewards, PATCH /rewards/{id}, POST /rewards/{id}/redeem
│   │           └── analytics.py   # 13 read-only admin analytics endpoints (/summary, /trends, /alerts, /processing, etc.)
│   │
│   └── services/                # Business logic services
│       ├── __init__.py
│       ├── auth_service.py      # Authentication queries
│       ├── location_service.py  # Location management
│       ├── waste_type_service.py# Waste classification management
│       ├── bin_service.py       # Bin and QR operations
│       ├── disposal_service.py  # Digital disposal operations & validation
│       ├── report_service.py    # Issue reporting, review & resolution
│       ├── fill_reading_service.py # Historical fill readings & current fill sync
│       ├── collection_service.py # Waste collection records & fill reset sync
│       ├── classification_service.py # AI inference orchestration & persistence
│       ├── prediction_service.py # Time-series forecasting & data sufficiency checks
│       ├── processing_service.py # Recycling/composting validation, quantity checks & persistence
│       ├── gamification_service.py # Point ledger management, automatic awards, rewards & redemptions
│       └── analytics_service.py # Read-only aggregated analytics & operational alert derivation
│
├── alembic/                     # Database migrations
│   ├── versions/
│   │   ├── 0001_initial_roles_and_users.py
│   │   ├── 0002_locations_waste_types_bins.py
│   │   ├── 0003_disposals_and_reports.py
│   │   ├── 0004_fill_monitoring_and_collections.py
│   │   ├── 0005_waste_classifications.py
│   │   ├── 0006_fill_predictions.py
│   │   ├── 0007_recycling_composting.py
│   │   └── 0008_gamification_rewards.py

│   ├── env.py
│   └── script.py.mako
│
├── scripts/
│   └── seed_dev_data.py         # Development seed script
│
├── tests/                       # Automated test suite
│   ├── __init__.py
│   ├── conftest.py              # Pytest fixtures & test database setup
│   ├── test_health.py           # Health check tests
│   ├── test_auth.py             # Login & JWT authentication tests
│   ├── test_users.py            # User profile & role-protection tests
│   ├── test_database.py         # Entity integrity & uniqueness tests
│   ├── test_locations.py        # Campus location CRUD & authorization tests
│   ├── test_waste_types.py      # Waste classification tests
│   ├── test_bins.py             # Bin lifecycle & QR lookup tests
│   ├── test_disposals.py        # Digital disposal recording & ownership scoping tests
│   ├── test_reports.py          # Waste issue reporting & review lifecycle tests
│   ├── test_fill_readings.py    # Historical fill reading tests & fill synchronization
│   ├── test_collections.py      # Collection lifecycle, role permissions & E2E workflow
│   ├── test_classification.py   # AI waste classification & model abstraction tests
│   └── test_predictions.py      # AI fill forecasting, feature pipeline & evaluation tests
│
├── .env.example
├── alembic.ini
├── Dockerfile
├── requirements.txt
└── README.md
```

---

## 3. Setup Instructions

### 3.1 Create and Activate Virtual Environment

```bash
# Windows
python -m venv .venv
.venv\Scripts\activate

# Linux / macOS
python3 -m venv .venv
source .venv/bin/activate
```

### 3.2 Install Dependencies

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

### 3.3 Configure Environment Variables

Copy `.env.example` to `.env` and configure your database and JWT parameters:

```bash
cp .env.example .env
```

Key environment variables:
```dotenv
DATABASE_URL=postgresql+psycopg://postgres:postgres@localhost:5432/ecosense
JWT_SECRET_KEY=your_secure_jwt_secret_key_here
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=1440
ENVIRONMENT=development
```

---

## 4. Database & Migrations

### 4.1 Running Migrations

Apply database migrations to the latest version:

```bash
alembic upgrade head
```

To roll back the last migration:

```bash
alembic downgrade -1
```

To inspect generated SQL without applying:

```bash
alembic upgrade head --sql
```

Migration Chain:
`0001_initial_roles_and_users` $\rightarrow$ `0002_locations_waste_types_bins` $\rightarrow$ `0003_disposals_and_reports` $\rightarrow$ `0004_fill_collections` $\rightarrow$ `0005_waste_classifications` $\rightarrow$ `0006_fill_predictions` $\rightarrow$ `0007_recycling_composting` $\rightarrow$ `0008_gamification_rewards`

### 4.2 Seed Data

Seed development users, waste types, sample campus locations, and bins:

```bash
python scripts/seed_dev_data.py
```

Default dev accounts:
- **ADMIN:** `admin@dbit.in` (password: `adminpassword`)
- **STUDENT:** `student@dbit.in` (password: `studentpassword`)
- **COLLECTOR:** `collector@dbit.in` (password: `collectorpassword`)
- **STAFF:** `staff@dbit.in` (password: `staffpassword`)

---

## 5. Running the Backend

Start the Uvicorn ASGI server with live reloading:

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

---

## 6. Interactive API Documentation

Once the server is running, explore the interactive documentation:

- **Swagger UI:** [http://localhost:8000/docs](http://localhost:8000/docs)
- **ReDoc:** [http://localhost:8000/redoc](http://localhost:8000/redoc)
- **OpenAPI JSON:** [http://localhost:8000/openapi.json](http://localhost:8000/openapi.json)
- **Health Check:** [http://localhost:8000/health](http://localhost:8000/health)

---

## 7. Endpoints Implemented

### System & Authentication
| Method | Endpoint | Access | Description |
| :--- | :--- | :--- | :--- |
| `GET` | `/health` | Public | System uptime & health check |
| `POST` | `/api/v1/auth/login` | Public | Authenticates user & issues JWT token |
| `GET` | `/api/v1/auth/me` | Authenticated | Returns current authenticated user |
| `GET` | `/api/v1/users/me` | Authenticated | Returns detailed user profile |
| `GET` | `/api/v1/users/admin-test` | `ADMIN` only | Verifies role-based access control |

### Locations
| Method | Endpoint | Access | Description |
| :--- | :--- | :--- | :--- |
| `POST` | `/api/v1/locations` | `ADMIN` only | Creates a campus location |
| `GET` | `/api/v1/locations` | Authenticated | Lists campus locations with pagination & filters |
| `GET` | `/api/v1/locations/{location_id}` | Authenticated | Retrieves a specific campus location |
| `PATCH` | `/api/v1/locations/{location_id}` | `ADMIN` only | Updates location details or deactivates it (`is_active = false`) |

### Waste Types
| Method | Endpoint | Access | Description |
| :--- | :--- | :--- | :--- |
| `GET` | `/api/v1/waste-types` | Authenticated | Lists active waste classification types |
| `POST` | `/api/v1/waste-types` | `ADMIN` only | Registers a new waste type |
| `PATCH` | `/api/v1/waste-types/{waste_type_id}` | `ADMIN` only | Updates waste type metadata |

### Bins & QR Code Lookup
| Method | Endpoint | Access | Description |
| :--- | :--- | :--- | :--- |
| `POST` | `/api/v1/bins` | `ADMIN` only | Deploys a new bin with designated waste type & location |
| `GET` | `/api/v1/bins` | Authenticated | Lists bins with `location_id`, `waste_type_id`, `status` filters |
| `GET` | `/api/v1/bins/qr/{qr_token}` | Authenticated (`ALL`) | Looks up bin details by scanned opaque QR token |
| `GET` | `/api/v1/bins/{bin_id}` | Authenticated | Retrieves detailed bin specifications |
| `PATCH` | `/api/v1/bins/{bin_id}` | `ADMIN` only | Updates bin fill percentage, location, or status |

### Digital Waste Disposal
| Method | Endpoint | Access | Description |
| :--- | :--- | :--- | :--- |
| `POST` | `/api/v1/disposals` | `STUDENT`, `STAFF` | Records a waste disposal event into an active bin |
| `GET` | `/api/v1/disposals` | Authenticated | Lists disposal history (scoped to user for Student/Staff) |
| `GET` | `/api/v1/disposals/{disposal_id}` | Authenticated | Retrieves a specific disposal record |

### Waste Issue Reporting
| Method | Endpoint | Access | Description |
| :--- | :--- | :--- | :--- |
| `POST` | `/api/v1/reports` | Authenticated (`ALL`) | Submits an issue report regarding a bin or campus area |
| `GET` | `/api/v1/reports` | Authenticated | Lists reports (Students/Staff view their own; Admins/Collectors view all) |
| `GET` | `/api/v1/reports/{report_id}` | Authenticated | Retrieves details for a specific report |
| `PATCH` | `/api/v1/reports/{report_id}` | `ADMIN` only | Updates report status (`IN_PROGRESS`, `RESOLVED`, `REJECTED`) |

### Fill Readings (Historical Bin Fill Monitoring)
| Method | Endpoint | Access | Description |
| :--- | :--- | :--- | :--- |
| `POST` | `/api/v1/bins/{bin_id}/fill-readings` | `COLLECTOR`, `ADMIN` | Records a historical fill reading and atomically updates `bins.current_fill_percentage` |
| `GET` | `/api/v1/bins/{bin_id}/fill-readings` | Authenticated | Lists historical fill readings for a specific bin, ordered chronologically |
| `GET` | `/api/v1/fill-readings/{reading_id}` | Authenticated | Retrieves a single historical fill reading by ID |

### Collection Records
| Method | Endpoint | Access | Description |
| :--- | :--- | :--- | :--- |
| `POST` | `/api/v1/collections` | `COLLECTOR`, `ADMIN` | Records a completed waste collection event and resets `bins.current_fill_percentage` if `fill_level_after` is provided |
| `GET` | `/api/v1/collections` | Authenticated | Lists collection history (scoped to collector for `COLLECTOR`; all records for `ADMIN`) |
| `GET` | `/api/v1/collections/{collection_id}` | Authenticated | Retrieves a specific collection record |

### AI Waste Classification
| Method | Endpoint | Access | Description |
| :--- | :--- | :--- | :--- |
| `POST` | `/api/v1/classification` | Authenticated (`ALL`) | Submits an image reference for AI classification and receives predicted waste category, confidence score, and model version |
| `GET` | `/api/v1/classification/{classification_id}` | Authenticated | Retrieves a specific classification event (scoped to creator for normal users; platform-wide for Admin) |
| `GET` | `/api/v1/classification` | Authenticated | Lists classification history with pagination (`skip`, `limit`), scoped by user role |

### AI Bin Fill Level Prediction
| Method | Endpoint | Access | Description |
| :--- | :--- | :--- | :--- |
| `POST` | `/api/v1/bins/{bin_id}/predictions` | `COLLECTOR`, `ADMIN` | Triggers on-demand future fill level forecast for a bin using historical accumulation telemetry (status `201`) |
| `GET` | `/api/v1/bins/{bin_id}/predictions` | Authenticated | Lists historical prediction records for a specific bin with pagination (`skip`, `limit`) |
| `GET` | `/api/v1/predictions/{prediction_id}` | Authenticated | Retrieves a single prediction record by ID |

### Recycling & Composting Management
| Method | Endpoint | Access | Description |
| :--- | :--- | :--- | :--- |
| `POST` | `/api/v1/processing` | `COLLECTOR`, `ADMIN` | Records post-collection recycling or composting processing event (status `201`) |
| `GET` | `/api/v1/processing` | `STAFF`, `COLLECTOR`, `ADMIN` | Lists processing records with filtering (`processing_type`, `status`, `collection_id`, date range) |
| `GET` | `/api/v1/processing/{processing_id}` | `STAFF`, `COLLECTOR`, `ADMIN` | Retrieves details of a specific processing record |
| `GET` | `/api/v1/collections/{collection_id}/processing` | `STAFF`, `COLLECTOR`, `ADMIN` | Retrieves all processing records associated with a specific collection event |
| `GET` | `/api/v1/bins/{bin_id}/processing` | `STAFF`, `COLLECTOR`, `ADMIN` | Retrieves processing history for a specific bin through relational joins |

### Gamification & Rewards
| Method | Endpoint | Access | Description |
| :--- | :--- | :--- | :--- |
| `GET` | `/api/v1/gamification/me` | `STUDENT`, `ADMIN` | Retrieves current point balance, total earned, and total redeemed from the immutable ledger |
| `GET` | `/api/v1/gamification/me/transactions` | `STUDENT`, `ADMIN` | Lists paginated immutable point transactions for authenticated student |
| `GET` | `/api/v1/gamification/me/redemptions` | `STUDENT`, `ADMIN` | Lists reward redemption history for authenticated student |
| `GET` | `/api/v1/gamification/users/{user_id}` | `ADMIN` | Inspects points balance and statistics for a specific user |
| `GET` | `/api/v1/gamification/users/{user_id}/transactions` | `ADMIN` | Inspects transaction ledger entries for a specific user |
| `POST` | `/api/v1/gamification/users/{user_id}/adjust` | `ADMIN` | Posts an immutable manual point adjustment (`ADJUSTMENT` type) |
| `GET` | `/api/v1/gamification/redemptions` | `ADMIN` | Lists all reward redemptions across campus |
| `GET` | `/api/v1/rewards` | Authenticated (`ALL`) | Lists active redeemable rewards (Admins see all) |
| `GET` | `/api/v1/rewards/{reward_id}` | Authenticated (`ALL`) | Retrieves details of a specific reward |
| `POST` | `/api/v1/rewards` | `ADMIN` | Creates a new reward item (status `201`) |
| `PATCH` | `/api/v1/rewards/{reward_id}` | `ADMIN` | Updates reward name, description, points cost, inventory stock, or active status |
| `POST` | `/api/v1/rewards/{reward_id}/redeem` | `STUDENT` | Redeems reward atomically deducting points and decrementing finite inventory (status `201`) |

---

## 8. Core Architecture

### 8.1 Current Fill State vs. Historical Readings
- **`bins.current_fill_percentage`**: Represents the **CURRENT OPERATIONAL STATE** of a bin.
- **`bin_fill_readings`**: Represents **IMMUTABLE HISTORICAL LOGS** of fill percentages over time (used for auditing and future prediction modeling).
- When `POST /api/v1/bins/{bin_id}/fill-readings` is executed:
  1. A new record is inserted into `bin_fill_readings`.
  2. `bins.current_fill_percentage` is updated atomically in the same database transaction.
- **Append-Only History**: Historical records in `bin_fill_readings`, `collection_records`, `waste_classifications`, `fill_predictions`, `processing_records`, and `point_transactions` cannot be modified or deleted via API (`PATCH` / `DELETE` are disallowed).

### 8.2 Collection Events vs. Fill Readings
- A collection event represents the physical emptying or clearing of a bin by an authorized collector or admin.
- When `POST /api/v1/collections` is executed:
  1. `collection_records` stores `fill_level_before`, `collected_quantity_kg`, and `fill_level_after`.
  2. If `fill_level_after` is supplied, `bins.current_fill_percentage` is updated atomically to that value (e.g., `0.00%`).
  3. Physical bin status (e.g., `DAMAGED`) is preserved and not overwritten.
  4. Separate `bin_fill_readings` entries are **not** artificially generated, avoiding double-counting in operational history.

### 8.3 AI Classifier Abstraction & Decoupling
- Classification inference is isolated behind the `BaseWasteClassifier` abstract interface located in `ai/classification/`.
- The development environment uses a deterministic `MockWasteClassifier` (`v1.0-mock`) to ensure fast, offline, and repeatable testing.
- The model prediction maps strictly to the 6 core DBIT campus waste categories (`WET_ORGANIC`, `DRY_RECYCLABLE`, `PAPER`, `METAL`, `E_WASTE`, `GARDEN`).
- Predictions with confidence below `CLASSIFICATION_CONFIDENCE_THRESHOLD` (default: `0.70`) are flagged dynamically with `low_confidence: true`.

### 8.4 Time-Series Forecasting & Feature Pipeline
- Fill forecasting is isolated behind the `BaseFillPredictor` abstract interface located in `ai/prediction/`.
- The baseline model `BaselineFillPredictor` (`baseline-v1`) computes linear accumulation rates across post-collection cycles and projects future fill levels over a configurable horizon (default: 120 minutes).
- Bins with sparse data (fewer than `MIN_PREDICTION_READINGS = 3` readings) return HTTP 422 to prevent unreliable forecasts.
- Feature extraction guarantees strict temporal boundaries (no data leakage from future events).

### 8.5 Recycling & Composting Processing Management
- Represents downstream operational actions taken on waste **AFTER** it has been collected from bins (`Bin` $\rightarrow$ `CollectionRecord` $\rightarrow$ `ProcessingRecord`).
- **Processing Types:**
  - `COMPOSTING`: Valid for organic/wet waste streams (`WET_ORGANIC`, `GARDEN`, `FOOD_WASTE`).
  - `RECYCLING`: Valid for recyclable streams (`DRY_RECYCLABLE`, `PAPER`, `METAL`, `E_WASTE`, `PLASTIC`, `GLASS`).
- **Batch Processing & Quantity Integrity:**
  - Multiple processing records can partially consume a single collection (e.g., 20 kg collection $\rightarrow$ 12 kg batch 1 + 8 kg batch 2).
  - Cumulative processed quantity cannot exceed `collection.collected_quantity_kg` (returns HTTP 422).
  - Unmeasured collections (`collected_quantity_kg = null`) allow processing records without strict upper bounds.
- **Relational Integrity:**
  - `processing_records` avoids duplicate `waste_type_id` or `bin_id` columns, deriving category and origin relatonally via `collection_id` $\rightarrow$ `bins.waste_type_id`.
  - Processing actions do **NOT** modify or mutate original `collection_records`, `bin_fill_readings`, or `bins`.

### 8.7 Administrative Analytics & Read-Only Reporting (Phase 9)
- **Read-Only Guarantee:** The analytics service executes purely read-only database-side SQL aggregations across operational tables. It never mutates operational records, awards points, generates predictions, or modifies bin/report statuses.
- **Strict Role-Based Access Control:** All 13 analytics endpoints require authentication and are restricted strictly to `ADMIN` users.
- **Date Range Semantics:**
  - `start_date` is inclusive ($\ge$), `end_date` is exclusive ($<$).
  - Normalizes timezone-aware timestamps (UTC).
  - Defaults to the previous 30 days (`DEFAULT_ANALYTICS_DAYS = 30`) if no range is supplied.
- **Measured Quantity & NULL Semantics:**
  - Measured metrics use SQL `SUM`/`AVG`, naturally ignoring unmeasured `NULL` quantities without artificially defaulting them to zero.
  - Ratios such as `diversion_rate` ($\frac{\text{total processed kg}}{\text{total collected kg}} \times 100$) and `participation_rate` ($\frac{\text{participating students}}{\text{total active students}} \times 100$) strictly return `null` (`None`) when the denominator is missing or zero.
- **In-Memory Operational Alert Derivation:**
  - Operational indicators (`HIGH_FILL_BIN`, `OVERFLOW_REPORT`, `DAMAGED_BIN`, `MISSING_BIN`, `PENDING_REPORT`) are derived dynamically without separate alert database tables or stateful mutation.
- **Prediction & Classification Analytics Boundaries:**
  - AI prediction metrics summarize model forecasts, forecast fill averages, and high-fill forecast counts without evaluating against unobserved future states.
  - Classification metrics report classification volumes, confidence distributions, and predicted categories without inferring accuracy in the absence of labeled ground truth.
- **Zero Database Migrations:** Phase 9 is purely a query and API layer; Alembic migration head remains `0008_gamification_rewards`.

---

## 9. Operational Workflows

### 9.1 QR-to-Disposal Workflow
1. User scans physical QR code on bin.
2. App requests `GET /api/v1/bins/qr/{qr_token}`.
3. App receives `bin_id`, `bin_code`, `waste_type`, and `status`.
4. User disposes waste and submits `POST /api/v1/disposals` with `bin_id` (and optional `quantity_kg` & `notes`).
5. Backend verifies bin is active (rejects if `FULL`, `DAMAGED`, `MISSING`, or `INACTIVE`) and records disposal with authenticated `user_id`.
6. Gamification service atomically awards 10 points (`EARN`) in `point_transactions`.

### 9.2 QR-to-Reporting Workflow
1. User scans physical QR code or opens problem report form.
2. User submits `POST /api/v1/reports` with `bin_id` (optional for general campus issues), `report_type` (`OVERFLOWING`, `DAMAGED_BIN`, `MISSING_BIN`, `WRONG_SEGREGATION`, `OTHER`), and description/image URL.
3. Report is created with initial `PENDING` status.
4. Administrator reviews reports via `GET /api/v1/reports`.
5. Administrator updates status to `IN_PROGRESS` and subsequently `RESOLVED` via `PATCH /api/v1/reports/{report_id}`, which automatically records `resolved_at`, `resolved_by`, and atomically awards 5 points (`EARN`) to the reporting student.

### 9.3 QR-to-Fill Reading & Collection Workflow
1. Collector scans physical QR code on bin $\rightarrow$ `GET /api/v1/bins/qr/{qr_token}`.
2. Collector observes current fill level and records measurement $\rightarrow$ `POST /api/v1/bins/{bin_id}/fill-readings` (`fill_percentage: 85`, `source: "MANUAL"`).
3. System logs historical reading (85%) and updates `bins.current_fill_percentage` to 85%.
4. Collector collects waste and submits collection record $\rightarrow$ `POST /api/v1/collections` (`fill_level_before: 85`, `collected_quantity_kg: 12.4`, `fill_level_after: 0`).
5. System logs collection event and updates `bins.current_fill_percentage` to 0%.

### 9.4 AI Image Classification & Decoupled Disposal Workflow
1. Student/Staff takes photo of waste and submits `POST /api/v1/classification` (`image_url: "..."`).
2. Backend validates image input reference, executes inference via `BaseWasteClassifier`, and maps class to `WasteType` (e.g. `DRY_RECYCLABLE`, confidence `0.94`).
3. System stores classification event in `waste_classifications` and returns prediction.
4. AI classification does **NOT** auto-select a bin or modify bin records.
5. User navigates to the recommended bin category (e.g., Dry Recyclable Bin), scans its QR token, and submits an independent `POST /api/v1/disposals`.

### 9.5 On-Demand Bin Fill Level Forecasting Workflow
1. Collector or Admin requests prediction for a bin $\rightarrow$ `POST /api/v1/bins/{bin_id}/predictions` (optional `horizon_minutes: 120`).
2. Prediction service verifies bin existence, retrieves historical readings and collection cycles, and checks minimum data threshold.
3. Feature pipeline segments observations to the active accumulation cycle and computes hourly accumulation rate.
4. Predictor calculates future fill level clamped strictly to $[0.0\%, 100.0\%]$ with uncertainty bounds.
5. Persists prediction event in `fill_predictions` and returns structured forecast.

### 9.6 Collection-to-Processing (Recycling & Composting) Workflow
1. Collector empties bin and creates collection record $\rightarrow$ `POST /api/v1/collections` (`collected_quantity_kg: 30.0`).
2. Waste is transported to campus processing facility (e.g., bio-composting pit or recycling aggregation center).
3. Collector/Admin records processing event $\rightarrow$ `POST /api/v1/processing` (`collection_id: 10`, `processing_type: "COMPOSTING"`, `quantity_kg: 30.0`, `status: "COMPLETED"`).
4. System validates waste type compatibility and ensures cumulative quantity $\le$ collected quantity.
5. Record is persisted in `processing_records`.
6. Staff and Collectors can track processing history via `GET /api/v1/processing` or `GET /api/v1/collections/{id}/processing`.

### 9.7 Gamification & Reward Redemption Workflow
1. Student participates in proper waste disposal $\rightarrow$ Earns 10 pts per disposal.
2. Student reports overflowing bin $\rightarrow$ Earns 5 pts upon Admin resolution.
3. Student checks point balance $\rightarrow$ `GET /api/v1/gamification/me`.
4. Student browses catalog $\rightarrow$ `GET /api/v1/rewards`.
5. Student redeems reward $\rightarrow$ `POST /api/v1/rewards/{reward_id}/redeem`.
6. Points are deducted atomically in ledger (`REDEEM`), finite stock is decremented, and redemption status is created.

### 9.8 Administrative Analytics & Reporting Workflow
1. Administrator requests executive summary $\rightarrow$ `GET /api/v1/analytics/summary` (optional `start_date` and `end_date`).
2. Dashboard visualizes operational cards: disposal count, collected mass, processed mass, recycling/composting output, diversion rate, active bins, high-fill bins, pending reports, and student participation rate.
3. Administrator drills down by category:
   - Waste Types: `GET /api/v1/analytics/waste-types`
   - Physical Campus Locations: `GET /api/v1/analytics/locations`
   - Temporal Trends (day/week/month): `GET /api/v1/analytics/trends`
   - Collections & Frequently Serviced Bins: `GET /api/v1/analytics/collections`
   - Bin Fill Levels & High-Fill List: `GET /api/v1/analytics/bin-fill`
   - Operational Derived Alerts: `GET /api/v1/analytics/alerts`
   - Issue Reports & Resolution Times: `GET /api/v1/analytics/reports`
   - Processing & Diversion: `GET /api/v1/analytics/processing`
   - Student Participation & Engagement: `GET /api/v1/analytics/participation`
   - Gamification & Points Velocity: `GET /api/v1/analytics/gamification`
   - Prediction Forecaster Distributions: `GET /api/v1/analytics/predictions`
   - AI Classifier Confidence & Category Distributions: `GET /api/v1/analytics/classifications`

---

## 10. Future Compatibility (Not Yet Implemented)

> [!NOTE]
> The following capabilities are planned for subsequent phases and are **NOT** implemented in the current release:
> - **Green Index & Sustainability Scoring**: Environmental scoring and institution-wide sustainability indices (optional/future).
> - **IoT Sensor Ingestion & MQTT**: Telemetry stream processing from ESP32/ultrasonic hardware sensors.

---

## 11. Running Automated Tests

Run the full pytest test suite:

```bash
pytest -v
```


