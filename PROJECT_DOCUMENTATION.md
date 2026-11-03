# EcoSense: AI-Based Zero Waste Campus Management Platform
## Single Authoritative Technical Reference and Architecture Documentation

**Institution:** Don Bosco Institute of Technology (DBIT), Mumbai  
**Platform Name:** EcoSense  
**Document Classification:** Comprehensive Technical Reference & Codebase Architecture Specification  
**Current Codebase Version:** 1.0.0 (Production Architecture & FastAI Integrated Pipeline)  
**Last Codebase Audit:** October 2026  

---

## Table of Contents

1. [Project Overview](#1-project-overview)
2. [Repository Structure and Codebase Organization](#2-repository-structure-and-codebase-organization)
3. [Complete Technology Stack](#3-complete-technology-stack)
4. [System Architecture](#4-system-architecture)
5. [Detailed Implementation of Every Major Feature](#5-detailed-implementation-of-every-major-feature)
6. [Dataset and Data Engineering Documentation](#6-dataset-and-data-engineering-documentation)
7. [Machine Learning, AI, and Algorithmic Implementation](#7-machine-learning-ai-and-algorithmic-implementation)
8. [Complete API and Interface Documentation](#8-complete-api-and-interface-documentation)
9. [Database, Storage, and Data Models](#9-database-storage-and-data-models)
10. [Configuration and Environment Setup](#10-configuration-and-environment-setup)
11. [End-to-End Workflows and Execution Lifecycle](#11-end-to-end-workflows-and-execution-lifecycle)
12. [UI/UX and Frontend Design System](#12-uiux-and-frontend-design-system)
13. [Security, Privacy, and Reliability](#13-security-privacy-and-reliability)
14. [Testing and Quality Assurance](#14-testing-and-quality-assurance)

---

## 1. Project Overview

### 1.1 Executive Summary

**EcoSense** is an enterprise-grade, full-stack, AI-integrated campus zero-waste management platform engineered specifically for **Don Bosco Institute of Technology (DBIT), Mumbai**. It unifies physical waste monitoring, computer-vision-assisted material segregation, telemetry-driven fill forecasting, digital issue escalation, collector workforce operations, recycling and composting batch tracking, and community gamification into a single, cohesive institutional platform.

The system bridges physical campus assets (waste bins, collection carts, organic composting pits) with digital actors (students, faculty/department staff, sanitation workers, and sustainability administrators). By pairing **opaque UUID-encoded physical QR code placards** on campus bins with an asynchronous **FastAPI backend**, a **PostgreSQL 16 relational ledger**, and a responsive **React 18 TypeScript Single-Page Application (SPA)**, EcoSense digitizes every stage of the campus waste lifecycle—from the moment an item is disposed of to its final diversion into recyclers or composting.

### 1.2 Problem Statement & Motivation

Educational institutions generate heterogeneous waste streams across distinct functional zones (canteens, computer laboratories, mechanical workshops, administrative offices, and botanical gardens). Conventional campus waste management suffers from several systemic failures:

1. **Segregation Failure at Source:** Students and visitors frequently deposit recyclables or electronic waste into organic bins due to ambiguity or lack of real-time guidance.
2. **Invisible Bin Fill Levels:** Sanitation staff follow rigid, time-based collection rounds rather than demand-driven routes, leading to overflowing bins in peak hours and premature emptyings in off-peak periods.
3. **Lack of Verifiable Accountability:** Campus administrators lack verified, auditable data regarding how much waste is collected, how much is composted or recycled, and whether reported issues (overflows, damaged lids) are ever addressed.
4. **Zero Community Engagement:** Passive recycling awareness campaigns fail to establish sustained behavioral modification without tangible feedback loops, recognition, or gamified incentives.

EcoSense solves these challenges by combining verifiable telemetry, mobile-first QR workflows, computer vision AI classification, and an append-only double-entry gamification ledger.

### 1.3 Target Users and Roles

The platform enforces strict **Role-Based Access Control (RBAC)** across five distinct user classifications:

| Role Code | User Persona | Primary Responsibilities & Interfaces |
| :--- | :--- | :--- |
| **`STUDENT`** | Undergraduate & postgraduate students | Scans physical bin QR codes; logs waste disposals; utilizes AI camera classification; reports campus waste hazards; tracks EcoPoints, streaks, and EcoStages; redeems institutional rewards; views campus leaderboard. |
| **`STAFF`** | Departmental faculty & administrative staff | Monitors departmental waste bins; files institutional waste hazard reports; tracks departmental resolution progress; views localized campus bin statuses. |
| **`COLLECTOR`** | Campus housekeeping & waste collection personnel | Records daily shift check-in/check-out; receives real-time field task notifications; scans bins to log collection metrics (fill level before/after, kilograms collected); initiates composting and recycling batches; views predictive fill horizons. |
| **`ADMIN`** | Sustainability directors & facilities administrators | Manages campus assets (bins, locations, waste types); delegates waste reports into collector tasks; manages collector availability and shift assignments; monitors real-time operational alerts; administers rewards catalog; inspects 13 analytics domain dashboards; prints physical QR placards. |
| **`PUBLIC`** | Unauthenticated visitors & unregistered students | Scans physical QR codes using native smartphone cameras / Google Lens; views public-safe real-time bin status, location, and capacity; seamlessly redirects to authenticated disposal logging. |

### 1.4 Primary Objectives

1. **Automate Waste Segregation Guidance:** Provide instant, on-device AI computer vision inference to categorize items into DBIT-standard waste streams (`WET_ORGANIC`, `DRY_RECYCLABLE`, `PAPER`, `METAL`, `E_WASTE`, `GARDEN`).
2. **Establish Closed-Loop Collection Telemetry:** Transition collection rounds from static schedules to dynamic, fill-monitored task dispatches with verified pre- and post-collection measurements.
3. **Trace Waste Diversion:** Track organic waste diverted into DBIT composting pits and dry recyclables diverted to municipal scrap partners.
4. **Incentivize Sustainable Habits:** Cultivate zero-waste habits through verified disposal points, milestone stages (Eco Seed to Campus Earth Hero), and redeemable campus rewards (canteen vouchers, reusable bottles).
5. **Provide Verifiable Governance:** Deliver 13 dedicated analytics endpoints with zero simulated metrics, providing verifiable operational numbers for NAAC/NIRF green institutional audits.

### 1.5 Scope and Explicit Boundaries

To maintain operational feasibility within an enclosed educational campus, the project intentionally defines clear architectural boundaries:

- **Included in Scope:**
  - Campus-wide QR bin network and public/authenticated resolution routes.
  - Multi-class FastAI computer vision classifier (`waste_classifier_v2.pkl`) and mock fallback.
  - Time-series fill rate extrapolation baseline model with cycle segmentation.
  - Digital waste issue reporting with administrative task delegation.
  - Collector attendance operations (shift check-in, check-out, availability).
  - Cross-platform Web Push notifications via Firebase Cloud Messaging (FCM).
  - One-bin-per-page printable vector QR placard generation.
  - Immutable point ledger with lifetime stage calculations.
- **Explicitly Excluded from Scope:**
  - *Vehicle Route Optimization:* Excluded because waste is collected manually using localized handcarts at end-of-day; campus roads do not utilize internal GPS vehicle fleets.
  - *Green Index Composite Scoring:* Excluded to prevent unverified arbitrary formulas; raw diversion rates and mass metrics are preserved for future index formalization.
  - *Automatic Disposal Logging via Vision AI:* Strictly prohibited by design. Computer vision classification only suggests waste categories; a physical QR code scan at a verified campus bin is required to register a disposal and earn points, preventing photographic fraud.

---

## 2. Repository Structure and Codebase Organization

The EcoSense repository is structured as a modular monorepo containing distinct backend, frontend, artificial intelligence, database, and documentation subsystems:

```text
EcoSense/
├── .dockerignore                            # Root Docker ignore rules
├── .gitignore                               # Git exclusion patterns
├── docker-compose.yml                       # Multi-service production orchestration
├── EcoSense_PostgreSQL_V1_Schema.md         # Schema specification reference
├── ecosense_PostgreSQL_V1_schema.sql        # Full PostgreSQL database schema dump
├── README.md                                # Platform overview & quickstart
├── RUN.md                                   # Operational cheat-sheet
├── test_classifier.py                       # CLI inference test utility for FastAI model
│
├── ai/                                      # Artificial Intelligence Subsystem
│   ├── README.md                            # AI architecture & feature guide
│   ├── models/                              # Serialized model checkpoints
│   │   ├── .gitkeep
│   │   └── waste_classifier_v2.pkl          # FastAI PyTorch vision learner (103.18 MB)
│   ├── classification/                      # Computer Vision Classification Module
│   │   ├── __init__.py                      # Package exports
│   │   ├── classifier.py                    # BaseWasteClassifier abstract interface
│   │   ├── config.py                        # Class categories & confidence thresholds
│   │   ├── fastai_model.py                  # Production FastAI vision model implementation
│   │   ├── model.py                         # Deterministic keyword/hash development mock
│   │   └── preprocessing.py                 # URI & binary image validation/sanitization
│   └── prediction/                          # Time-Series Waste Accumulation Forecasting
│       ├── __init__.py                      # Package exports
│       ├── config.py                        # Forecasting parameters & reading thresholds
│       ├── evaluation.py                    # Time-aware MAE/RMSE & chronological split
│       ├── features.py                      # 13-element feature extraction & cycle boundary logic
│       ├── model.py                         # Baseline linear rate extrapolation model
│       ├── predictor.py                     # BaseFillPredictor abstract interface
│       └── preprocessing.py                 # Telemetry chronological normalization & rate computation
│
├── backend/                                 # FastAPI Backend Service
│   ├── Dockerfile                           # Python 3.12 production container definition
│   ├── requirements.txt                     # Pinned Python package dependencies
│   ├── alembic.ini                          # Alembic migration configuration
│   ├── .env.example                         # Reference environment variables
│   ├── alembic/                             # Database Schema Migration History
│   │   ├── env.py                           # SQLAlchemy migration runner
│   │   └── versions/                        # 11 sequential migration scripts
│   │       ├── 0001_initial_roles_and_users.py
│   │       ├── 0002_locations_waste_types_bins.py
│   │       ├── 0003_disposals_and_reports.py
│   │       ├── 0004_fill_monitoring_and_collections.py
│   │       ├── 0005_waste_classifications.py
│   │       ├── 0006_fill_predictions.py
│   │       ├── 0007_recycling_composting.py
│   │       ├── 0008_gamification_rewards.py
│   │       ├── 0009_collector_attendance_and_tasks.py
│   │       ├── 0010_add_user_phone_and_notifications.py
│   │       └── 0011_device_tokens_and_fcm.py
│   ├── app/                                 # Core Application Logic
│   │   ├── main.py                          # FastAPI application factory & middleware setup
│   │   ├── core/                            # Infrastructure & Security Configuration
│   │   │   ├── config.py                    # Pydantic BaseSettings management
│   │   │   ├── database.py                  # SQLAlchemy engine & session factory
│   │   │   ├── dependencies.py              # JWT authentication & RBAC guards
│   │   │   ├── gamification_config.py       # 6 EcoStages & milestone progression rules
│   │   │   ├── phone_utils.py               # Phone normalization & formatting utilities
│   │   │   └── security.py                  # Argon2id hashing & PyJWT token creation
│   │   ├── models/                          # 20 SQLAlchemy 2.x Declarative Models
│   │   │   ├── base.py                      # DeclarativeBase foundation
│   │   │   ├── role.py                      # Roles table
│   │   │   ├── user.py                      # Users table (auth, phone, status)
│   │   │   ├── location.py                  # Locations table (campus buildings/floors)
│   │   │   ├── waste_type.py                # Waste streams table
│   │   │   ├── bin.py                       # Bins table (code, QR token, capacity, status)
│   │   │   ├── disposal.py                  # Disposal records table
│   │   │   ├── report.py                    # Waste issue reports table
│   │   │   ├── fill_reading.py              # Bin fill level readings table
│   │   │   ├── collection.py                # Collector collection records table
│   │   │   ├── classification.py            # AI classification inference logs table
│   │   │   ├── prediction.py                # Predictive fill forecasts table
│   │   │   ├── processing.py                # Recycling & composting batches table
│   │   │   ├── gamification.py              # Point transactions, rules, rewards, redemptions
│   │   │   ├── attendance.py                # Collector attendance & shift records
│   │   │   ├── task.py                      # Field tasks & delegations table
│   │   │   ├── notification.py              # Task notification audit records table
│   │   │   └── device_token.py              # FCM Web Push registration tokens table
│   │   ├── schemas/                         # Pydantic v2 Data Transfer Objects (DTOs)
│   │   │   ├── analytics.py, attendance.py, auth.py, bin.py, classification.py,
│   │   │   ├── collection.py, disposal.py, fill_reading.py, gamification.py,
│   │   │   ├── location.py, notification.py, prediction.py, processing.py,
│   │   │   └── report.py, task.py, user.py, waste_type.py
│   │   ├── services/                        # Domain Business Logic & Algorithms
│   │   │   ├── analytics_service.py         # 13 analytics aggregations & KPI calculation
│   │   │   ├── attendance_service.py        # Shift check-in/out & availability logic
│   │   │   ├── auth_service.py              # User authentication & token issuance
│   │   │   ├── bin_service.py               # Asset inventory & QR lookups
│   │   │   ├── classification_service.py    # AI model dispatch & classification persistence
│   │   │   ├── collection_service.py        # Collection event processing & fill updates
│   │   │   ├── disposal_service.py          # Disposal logging & point triggering
│   │   │   ├── fill_reading_service.py      # Telemetry logging & bin state updates
│   │   │   ├── gamification_service.py      # Immutable point ledger & reward redemptions
│   │   │   ├── location_service.py          # Location management
│   │   │   ├── prediction_service.py        # Forecasting pipeline orchestration
│   │   │   ├── processing_service.py        # Composting/recycling batch lifecycle
│   │   │   ├── push_notification_service.py # FCM Admin dispatch & token pruning
│   │   │   ├── report_service.py            # Report creation, resolution & points
│   │   │   ├── task_service.py              # Field task lifecycle & delegation
│   │   │   ├── user_service.py              # Administrative user profile & stage management
│   │   │   └── waste_type_service.py        # Waste stream definitions
│   │   └── api/v1/                          # REST API Routers
│   │       ├── router.py                    # Root v1 APIRouter mounting 18 sub-routers
│   │       └── endpoints/                   # 18 dedicated endpoint modules
│   ├── scripts/                             # Server Entrypoint & Seeding Utilities
│   │   ├── start.sh                         # Container startup, migration & seed orchestrator
│   │   └── seed_dev_data.py                 # Initial DBIT campus users, bins, locations, rewards
│   └── tests/                               # Backend Automated Pytest Suite
│       ├── conftest.py                      # Test client fixtures, SQLite in-memory engine, auth headers
│       └── test_*.py                        # 22 test files covering all 243 test cases
│
├── frontend/                                # React 18 TypeScript Single-Page Application
│   ├── Dockerfile                           # Multi-stage build & Nginx container
│   ├── nginx.conf                           # Production SPA routing & reverse proxy configuration
│   ├── package.json                         # NPM dependencies & test/build scripts
│   ├── tsconfig.json                        # Strict TypeScript compilation options
│   ├── vite.config.ts                       # Vite bundler configuration & vitest test runner
│   ├── tailwind.config.js                   # EcoSense design system tokens & colors
│   ├── public/                              # Static public assets
│   │   └── firebase-messaging-sw.js         # Service worker for background Web Push alerts
│   └── src/                                 # Frontend Source Code
│       ├── main.tsx                         # Client application entrypoint
│       ├── App.tsx                          # Root provider wrapper (Auth, Notifications, Router)
│       ├── index.css                        # Tailwind directives & print media rules
│       ├── api/                             # Typed API client & 18 domain HTTP modules
│       ├── context/                         # React Context State Stores
│       │   ├── AuthContext.tsx              # JWT session persistence & role decoding
│       │   └── NotificationContext.tsx      # FCM token registration & foreground banner provider
│       ├── layouts/                         # Application Structure Components
│       │   ├── AppShell.tsx                 # Main authenticated layout shell
│       │   ├── Header.tsx                   # Top navigation bar with notification bells & points
│       │   ├── Sidebar.tsx                  # Role-aware desktop sidebar
│       │   └── MobileNav.tsx                # Bottom navigation bar for mobile smartphones
│       ├── routes/                          # Application Routing & RBAC Guards
│       │   ├── AppRoutes.tsx                # Master route manifest (30+ registered views)
│       │   ├── ProtectedRoute.tsx           # Authentication barrier
│       │   └── RoleRoute.tsx                # Role-specific access enforcement
│       ├── pages/                           # Role-Tailored Interface Views
│       │   ├── auth/LoginPage.tsx           # Campus credentials login
│       │   ├── public/PublicBinPage.tsx     # Unauthenticated QR scanner landing page
│       │   ├── student/                     # Student Experience (9 pages)
│       │   ├── staff/                       # Staff Experience (3 pages)
│       │   ├── collector/                   # Collector Operations (6 pages)
│       │   └── admin/                       # Administrative Control Suite (11 pages)
│       ├── components/common/               # Shared EcoSense Design System Components
│       │   ├── BinQRPdfDocument.tsx         # Vector PDF placard rendering (@react-pdf/renderer)
│       │   ├── BinQRPrintSheet.tsx          # Browser-native printable QR layout
│       │   ├── CelebrationModal.tsx         # Canvas confetti reward modal
│       │   ├── EcoStageBadge.tsx            # Gamification flair badges
│       │   ├── EcoStageCard.tsx             # Interactive milestone progress bar card
│       │   ├── QRScanner.tsx                # html5-qrcode camera capture component
│       │   ├── NotificationSettingsModal.tsx# FCM permissions & push toggle dialog
│       │   └── StatCard.tsx, PointsCard.tsx, StatusBadge.tsx, etc.
│       ├── utils/                           # Client-side utility functions
│       │   └── pdfGenerator.ts              # PDF document generation helper
│       └── tests/                           # Frontend Vitest Suite
│           └── *.test.tsx                   # 38 unit & integration tests across 9 test files
│
├── database/                                # Database Assets & Reference Files
│   ├── README.md                            # Database configuration documentation
│   └── ecosense_PostgreSQL_V1_schema.sql    # DDL schema backup
│
└── docs/                                    # Technical Documentation & Architectural Guides
    ├── AI_ML_IMPLEMENTATION_REPORT.md       # Baseline AI audit report
    ├── COLLECTOR_OPERATIONS.md              # Shift & task management architecture
    ├── FIREBASE_FCM_SETUP.md                # Web Push notification setup & migration guide
    ├── QR_WORKFLOW_AND_QOL_GUIDE.md         # QR placard & public lookup reference
    ├── RUNNING_AND_TESTING_GUIDE.md         # Deployment & testing instructions
    └── WALKTHROUGH_QR_AND_QOL.md            # Feature walkthrough verification
```

---

## 3. Complete Technology Stack

### 3.1 Technology Inventory

| Category | Technology | Verified Version | Purpose & Architectural Role | Evidence / File Reference |
| :--- | :--- | :--- | :--- | :--- |
| **Runtime & Language** | Python | `3.12` | Backend runtime environment | [`backend/Dockerfile`](file:///c:/dev/web/EcoSense/backend/Dockerfile) |
| **Runtime & Language** | Node.js | `20+` / `22+` | Frontend build & test execution environment | [`frontend/package.json`](file:///c:/dev/web/EcoSense/frontend/package.json) |
| **Runtime & Language** | TypeScript | `^5.6.3` | Type-safe frontend client development | [`frontend/package.json`](file:///c:/dev/web/EcoSense/frontend/package.json) |
| **Backend Framework** | FastAPI | `>=0.115.0,<1.0.0` | High-performance asynchronous REST API framework | [`backend/requirements.txt`](file:///c:/dev/web/EcoSense/backend/requirements.txt) |
| **ASGI Web Server** | Uvicorn (standard) | `>=0.32.0,<1.0.0` | Production ASGI web server running FastAPI | [`backend/requirements.txt`](file:///c:/dev/web/EcoSense/backend/requirements.txt) |
| **Data Validation** | Pydantic v2 | `>=2.9.0,<3.0.0` | Request/response serialization & schema validation | [`backend/requirements.txt`](file:///c:/dev/web/EcoSense/backend/requirements.txt) |
| **Configuration** | Pydantic-Settings | `>=2.5.0,<3.0.0` | Environment variable management (`.env`) | [`backend/app/core/config.py`](file:///c:/dev/web/EcoSense/backend/app/core/config.py) |
| **Database Engine** | PostgreSQL | `16-alpine` | Primary ACID relational database | [`docker-compose.yml`](file:///c:/dev/web/EcoSense/docker-compose.yml) |
| **ORM Framework** | SQLAlchemy | `>=2.0.35,<3.0.0` | Object Relational Mapping (Mapped/mapped_column) | [`backend/requirements.txt`](file:///c:/dev/web/EcoSense/backend/requirements.txt) |
| **Database Driver** | Psycopg (v3 binary) | `>=3.2.0,<4.0.0` | Native C-backed PostgreSQL driver for Python | [`backend/requirements.txt`](file:///c:/dev/web/EcoSense/backend/requirements.txt) |
| **Schema Migrations** | Alembic | `>=1.13.0,<2.0.0` | Database schema version control (11 versions) | [`backend/alembic/`](file:///c:/dev/web/EcoSense/backend/alembic/) |
| **Authentication** | PyJWT [crypto] | `>=2.9.0,<3.0.0` | Stateless HMAC-SHA256 JWT token generation/validation | [`backend/app/core/security.py`](file:///c:/dev/web/EcoSense/backend/app/core/security.py) |
| **Password Hashing** | Argon2id (`argon2-cffi`)| `>=23.1.0,<24.0.0` | Memory-hard cryptographic password hashing | [`backend/app/core/security.py`](file:///c:/dev/web/EcoSense/backend/app/core/security.py) |
| **Push Notifications** | Firebase Admin SDK | `>=7.0.0,<8.0.0` | Server-side FCM Web Push message dispatching | [`backend/app/services/push_notification_service.py`](file:///c:/dev/web/EcoSense/backend/app/services/push_notification_service.py) |
| **AI Vision Learner** | FastAI | `>=2.8.0` | Deep learning computer vision inference runtime | [`backend/requirements.txt`](file:///c:/dev/web/EcoSense/backend/requirements.txt) |
| **Machine Learning** | PyTorch / Torchvision | `>=2.0.0` / `>=0.15.0` | Neural network tensor execution backend | [`backend/requirements.txt`](file:///c:/dev/web/EcoSense/backend/requirements.txt) |
| **Image Processing** | Pillow (PIL) | `>=10.0.0` | Image loading, resizing, and format conversions | [`ai/classification/fastai_model.py`](file:///c:/dev/web/EcoSense/ai/classification/fastai_model.py) |
| **Frontend Framework** | React | `^18.3.1` | Declarative component UI library | [`frontend/package.json`](file:///c:/dev/web/EcoSense/frontend/package.json) |
| **Frontend Router** | React Router DOM | `^6.28.0` | Client-side routing, protected routes, URL parameters | [`frontend/src/routes/AppRoutes.tsx`](file:///c:/dev/web/EcoSense/frontend/src/routes/AppRoutes.tsx) |
| **Frontend Build Tool** | Vite | `^6.0.1` | Ultra-fast development server & production bundler | [`frontend/vite.config.ts`](file:///c:/dev/web/EcoSense/frontend/vite.config.ts) |
| **CSS Styling Engine** | Tailwind CSS | `^3.4.16` | Utility-first responsive styling framework | [`frontend/tailwind.config.js`](file:///c:/dev/web/EcoSense/frontend/tailwind.config.js) |
| **Icon Library** | Lucide React | `^1.16.0` | Modern, consistent vector UI icons | [`frontend/package.json`](file:///c:/dev/web/EcoSense/frontend/package.json) |
| **Data Visualization** | Recharts | `^2.13.3` | Composable SVG charts for administrative analytics | [`frontend/src/pages/admin/AdminAnalyticsPage.tsx`](file:///c:/dev/web/EcoSense/frontend/src/pages/admin/AdminAnalyticsPage.tsx) |
| **QR Generation (UI)** | `qrcode.react` / `qrcode`| `^4.2.0` / `^1.5.4` | In-app QR rendering & SVG generation | [`frontend/src/components/common/BinQRPrintSheet.tsx`](file:///c:/dev/web/EcoSense/frontend/src/components/common/BinQRPrintSheet.tsx) |
| **QR Scanning (Camera)**| `html5-qrcode` | `^2.3.8` | Cross-platform camera video stream QR decoder | [`frontend/src/components/common/QRScanner.tsx`](file:///c:/dev/web/EcoSense/frontend/src/components/common/QRScanner.tsx) |
| **Vector PDF Placards**| `@react-pdf/renderer` | `^4.9.0` | Client-side vector PDF generation for bin placards | [`frontend/src/components/common/BinQRPdfDocument.tsx`](file:///c:/dev/web/EcoSense/frontend/src/components/common/BinQRPdfDocument.tsx) |
| **Micro-Animations** | Canvas Confetti | `^1.9.4` | Particle celebration modal for reward redemptions | [`frontend/src/components/common/CelebrationModal.tsx`](file:///c:/dev/web/EcoSense/frontend/src/components/common/CelebrationModal.tsx) |
| **Web Push Client** | Firebase JS SDK | `^13.0.0` | Browser service worker registration & VAPID tokens | [`frontend/src/context/NotificationContext.tsx`](file:///c:/dev/web/EcoSense/frontend/src/context/NotificationContext.tsx) |
| **Backend Testing** | Pytest & pytest-asyncio| `>=8.3.0` / `>=0.24.0` | Automated backend testing harness (243 tests) | [`backend/requirements.txt`](file:///c:/dev/web/EcoSense/backend/requirements.txt) |
| **HTTP Test Client** | HTTPX | `>=0.27.0,<1.0.0` | Synchronous/asynchronous API test client | [`backend/tests/conftest.py`](file:///c:/dev/web/EcoSense/backend/tests/conftest.py) |
| **Frontend Testing** | Vitest & Testing Library| `^5.0.1` / `^16.3.3` | Vite-native unit and component test runner (38 tests) | [`frontend/src/tests/`](file:///c:/dev/web/EcoSense/frontend/src/tests/) |
| **Production Web Server**| Nginx | `alpine` | Static frontend serving & SPA fallback proxy | [`frontend/nginx.conf`](file:///c:/dev/web/EcoSense/frontend/nginx.conf) |
| **Containerization** | Docker & Compose | Compose v2 | Multi-container reproducible deployment | [`docker-compose.yml`](file:///c:/dev/web/EcoSense/docker-compose.yml) |

---

## 4. System Architecture

EcoSense adopts a modern **Three-Tier Service-Oriented Architecture (SOA)** with an embedded Machine Learning inference pipeline and event-driven Web Push alerts:

### 4.1 High-Level Architecture Diagram

```mermaid
graph TB
    subgraph ClientLayer ["Client Presentation Tier (React 18 + Vite)"]
        UI_Student["Student Experience<br/>(Scan, Classify, Rewards)"]
        UI_Staff["Staff Experience<br/>(Monitor, Report)"]
        UI_Collector["Collector Hub<br/>(Attendance, Tasks, Collections)"]
        UI_Admin["Admin Control Center<br/>(Analytics, Assets, Operations)"]
        UI_Public["Public QR Resolver<br/>(/bin/:qr_token)"]
        SW["Service Worker<br/>(firebase-messaging-sw.js)"]
    end

    subgraph GatewayLayer ["Reverse Proxy & Web Gateway (Nginx)"]
        Nginx["Nginx Reverse Proxy<br/>(Port 5173 / 80)"]
    end

    subgraph APILayer ["Application Tier (FastAPI Asynchronous Engine)"]
        FastAPI["FastAPI Application Server<br/>(Port 8000)"]
        AuthMiddleware["JWT Bearer & RBAC Guard<br/>(Argon2id + PyJWT)"]
        Router["APIRouter (18 Domain Routers)"]
        
        subgraph Services ["Service Domain Layer"]
            S_Analytics["AnalyticsService<br/>(13 Endpoints)"]
            S_Attendance["AttendanceService<br/>(Shift & Availability)"]
            S_Task["TaskService<br/>(Assignment & Delegation)"]
            S_Gamification["GamificationService<br/>(Ledger & EcoStages)"]
            S_Push["PushNotificationService<br/>(FCM Web Push)"]
            S_Classify["ClassificationService<br/>(FastAI + Mock Dispatch)"]
            S_Predict["PredictionService<br/>(Time-Series Forecaster)"]
            S_Core["Core Entity Services<br/>(Bins, Locations, Users, Reports)"]
        end
    end

    subgraph InferenceLayer ["AI / Machine Learning Inference Pipeline"]
        FastAI_Model["FastAI Vision Classifier<br/>(waste_classifier_v2.pkl)"]
        Mock_Classifier["Mock Waste Classifier<br/>(Fallback Heuristic)"]
        Baseline_Predictor["Baseline Fill Forecaster<br/>(Linear Rate Model)"]
        Feature_Pipeline["Time-Series Feature Extractor<br/>(Cycle Segmentation)"]
    end

    subgraph DataLayer ["Persistence Tier (PostgreSQL 16)"]
        Postgres[("PostgreSQL 16 Database<br/>(20 Relational Tables)")]
    end

    subgraph CloudLayer ["External Services"]
        FCM["Google Firebase Cloud Messaging<br/>(Web Push Gateway)"]
    end

    %% Interactions
    UI_Student --> Nginx
    UI_Staff --> Nginx
    UI_Collector --> Nginx
    UI_Admin --> Nginx
    UI_Public --> Nginx

    Nginx --> FastAPI
    FastAPI --> AuthMiddleware --> Router
    Router --> Services

    S_Classify --> FastAI_Model
    S_Classify -. Fallback .-> Mock_Classifier
    S_Predict --> Feature_Pipeline --> Baseline_Predictor

    Services --> Postgres
    S_Push --> FCM
    FCM --> SW --> UI_Collector
```

### 4.2 Component Dependency Diagram

```mermaid
graph LR
    subgraph FrontendComponents ["Frontend Components (src/)"]
        Pages["Pages (30 Views)"]
        Contexts["Auth & Notification Contexts"]
        APIClient["Typed API Clients (client.ts)"]
        DesignSystem["Common Design System"]
        PDFGen["PDF Placard Generator"]
    end

    subgraph BackendModules ["Backend App (app/)"]
        Endpoints["API Endpoints (v1/endpoints)"]
        ServicesBackend["Services Business Logic"]
        Models["SQLAlchemy Models (20 Tables)"]
        Schemas["Pydantic Schemas"]
        Core["Core (Config, Security, DB)"]
    end

    subgraph AISubsystem ["AI Subsystem (ai/)"]
        CV["Classification Module"]
        TS["Prediction Module"]
        Weights["Serialized Model Weights"]
    end

    Pages --> Contexts
    Pages --> APIClient
    Pages --> DesignSystem
    Pages --> PDFGen

    APIClient -- HTTP / JSON --> Endpoints
    Endpoints --> ServicesBackend
    Endpoints --> Schemas
    ServicesBackend --> Models
    ServicesBackend --> Core
    ServicesBackend --> CV
    ServicesBackend --> TS
    CV --> Weights
    Models --> Core
```

### 4.3 End-to-End Execution and Data Flow Diagram

```mermaid
sequenceDiagram
    autonumber
    actor User as Campus User (Student/Collector)
    participant UI as React Frontend SPA
    participant API as FastAPI Backend
    participant Auth as Security & RBAC Guard
    participant Svc as Domain Services
    participant AI as AI Subsystem (FastAI / Forecaster)
    participant DB as PostgreSQL 16 Database
    participant FCM as Firebase Cloud Messaging

    Note over User, DB: Scenario: Student Scans Bin and Records Waste Disposal
    User->>UI: Scans physical QR placard at campus bin
    UI->>API: GET /api/v1/bins/public/{qr_token}
    API->>DB: Query bin by qr_token with joined location & waste_type
    DB-->>API: Return bin record
    API-->>UI: Return 200 OK (BinQRRead specifications)
    
    User->>UI: Submits disposal record (quantity_kg, notes)
    UI->>API: POST /api/v1/disposals (with Bearer JWT)
    API->>Auth: Validate JWT signature, expiry & active account
    Auth-->>API: Authenticated User context
    API->>Svc: disposal_service.create_disposal()
    Svc->>DB: Insert into disposal_records
    Svc->>Svc: gamification_service.award_points_for_disposal()
    Svc->>DB: Check anti-duplication index (source_type='DISPOSAL', source_id)
    Svc->>DB: Insert into point_transactions (EARN, +10 points)
    DB-->>Svc: Transaction committed
    Svc-->>API: Return DisposalRead with awarded points
    API-->>UI: Return 201 Created
    UI->>User: Displays CelebrationModal with confetti (+10 EcoPoints)

    Note over User, FCM: Scenario: Automatic Alert & Push Notification Dispatch
    API->>Svc: Evaluate bin fill status & collector task dispatch
    opt If bin fill exceeds 80% or urgent report filed
        Svc->>DB: Insert into collection_tasks (status='ASSIGNED')
        Svc->>DB: Query active device_tokens for on-shift collectors
        Svc->>FCM: Dispatch FCM Web Push payload (title, body, deep-link)
        FCM-->>UI: Push received by service worker
        UI->>User: Displays native notification banner to Collector
    end
```

---

## 5. Detailed Implementation of Every Major Feature

### Feature 1: Authentication & Role-Based Access Control (RBAC)
- **Purpose:** Secure platform access, enforce least privilege across institutional personas, and manage stateless sessions.
- **Source Files:**
  - Backend: [`backend/app/core/security.py`](file:///c:/dev/web/EcoSense/backend/app/core/security.py), [`backend/app/core/dependencies.py`](file:///c:/dev/web/EcoSense/backend/app/core/dependencies.py), [`backend/app/api/v1/endpoints/auth.py`](file:///c:/dev/web/EcoSense/backend/app/api/v1/endpoints/auth.py), [`backend/app/services/auth_service.py`](file:///c:/dev/web/EcoSense/backend/app/services/auth_service.py).
  - Frontend: [`frontend/src/context/AuthContext.tsx`](file:///c:/dev/web/EcoSense/frontend/src/context/AuthContext.tsx), [`frontend/src/routes/ProtectedRoute.tsx`](file:///c:/dev/web/EcoSense/frontend/src/routes/ProtectedRoute.tsx), [`frontend/src/routes/RoleRoute.tsx`](file:///c:/dev/web/EcoSense/frontend/src/routes/RoleRoute.tsx).
- **Implementation Mechanics:**
  - Passwords hashed using **Argon2id** (`argon2-cffi`) with custom salt generation.
  - Access tokens generated using **PyJWT** (`HS256` algorithm) with configurable expiration (`ACCESS_TOKEN_EXPIRE_MINUTES`, default: 1440 mins / 24 hours).
  - Claims structure: `{"sub": "<uuid>", "role": "STUDENT|STAFF|COLLECTOR|ADMIN", "iat": <timestamp>, "exp": <timestamp>}`.
  - Enforcement via FastAPI dependency injection: `Depends(require_roles("ADMIN", "COLLECTOR"))`.
  - Frontend decoding parses JWT payload, hydrates user state into `localStorage`, and handles automatic 401 redirection.

### Feature 2: QR-Based Campus Bin Lifecycle & Public Resolution
- **Purpose:** Associate physical bins with digital database entities using tamper-resistant identifiers.
- **Source Files:**
  - Backend: [`backend/app/models/bin.py`](file:///c:/dev/web/EcoSense/backend/app/models/bin.py), [`backend/app/api/v1/endpoints/bins.py`](file:///c:/dev/web/EcoSense/backend/app/api/v1/endpoints/bins.py), [`backend/app/services/bin_service.py`](file:///c:/dev/web/EcoSense/backend/app/services/bin_service.py).
  - Frontend: [`frontend/src/pages/public/PublicBinPage.tsx`](file:///c:/dev/web/EcoSense/frontend/src/pages/public/PublicBinPage.tsx), [`frontend/src/pages/student/ScanBinPage.tsx`](file:///c:/dev/web/EcoSense/frontend/src/pages/student/ScanBinPage.tsx).
- **Implementation Mechanics:**
  - Each physical bin is provisioned with an immutable, cryptographically generated UUID `qr_token` (`server_default=text("gen_random_uuid()")`).
  - QR Code Payload Format: `http://<domain>/bin/<qr_token>`.
  - Endpoint `GET /api/v1/bins/public/{qr_token}` provides public unauthenticated read access to bin code, location, waste type, capacity, and current fill percentage without exposing database IDs.
  - When scanned by unauthenticated visitors, displays real-time telemetry and a "Log In to Record Disposal" button that redirects to `/login?returnUrl=/bin/<qr_token>`.

### Feature 3: Digital Waste Issue Reporting & Status Progression
- **Purpose:** Enable campus community members to report overflowing bins, damaged lids, missing containers, or bio-hazards.
- **Source Files:**
  - Backend: [`backend/app/models/report.py`](file:///c:/dev/web/EcoSense/backend/app/models/report.py), [`backend/app/api/v1/endpoints/reports.py`](file:///c:/dev/web/EcoSense/backend/app/api/v1/endpoints/reports.py), [`backend/app/services/report_service.py`](file:///c:/dev/web/EcoSense/backend/app/services/report_service.py).
  - Frontend: [`frontend/src/pages/student/StudentReportPage.tsx`](file:///c:/dev/web/EcoSense/frontend/src/pages/student/StudentReportPage.tsx), [`frontend/src/pages/admin/AdminReportsPage.tsx`](file:///c:/dev/web/EcoSense/frontend/src/pages/admin/AdminReportsPage.tsx).
- **Implementation Mechanics:**
  - Supported report types: `OVERFLOWING_BIN`, `DAMAGED_BIN`, `MISPLACED_WASTE`, `HAZARDOUS_WASTE`, `OTHER`.
  - Status lifecycle: `PENDING` $\rightarrow$ `IN_PROGRESS` $\rightarrow$ `RESOLVED` / `REJECTED`.
  - When an administrator resolves a valid report (`PATCH /api/v1/reports/{id}/resolve`), the system automatically awards **+25 EcoPoints** to the reporting student via `award_points_for_report()`.

### Feature 4: Waste Disposal Logging & Telemetry Recording
- **Purpose:** Enable students and staff to record verified disposals after segregating waste at physical bins.
- **Source Files:**
  - Backend: [`backend/app/models/disposal.py`](file:///c:/dev/web/EcoSense/backend/app/models/disposal.py), [`backend/app/api/v1/endpoints/disposals.py`](file:///c:/dev/web/EcoSense/backend/app/api/v1/endpoints/disposals.py), [`backend/app/services/disposal_service.py`](file:///c:/dev/web/EcoSense/backend/app/services/disposal_service.py).
  - Frontend: [`frontend/src/pages/student/ScanBinPage.tsx`](file:///c:/dev/web/EcoSense/frontend/src/pages/student/ScanBinPage.tsx).
- **Implementation Mechanics:**
  - Endpoint `POST /api/v1/disposals` requires `bin_id` (UUID), optional `quantity_kg`, and notes.
  - Upon persistence, invokes `award_points_for_disposal()`, crediting **+10 EcoPoints** into `point_transactions`.
  - Includes a partial unique constraint preventing duplicate point awarding for the same disposal event.

### Feature 5: AI Computer Vision Waste Classification
- **Purpose:** Analyze waste photographs via mobile camera or upload and suggest appropriate campus bins.
- **Source Files:**
  - Subsystem: [`ai/classification/fastai_model.py`](file:///c:/dev/web/EcoSense/ai/classification/fastai_model.py), [`ai/classification/model.py`](file:///c:/dev/web/EcoSense/ai/classification/model.py), [`ai/classification/preprocessing.py`](file:///c:/dev/web/EcoSense/ai/classification/preprocessing.py).
  - Service & API: [`backend/app/services/classification_service.py`](file:///c:/dev/web/EcoSense/backend/app/services/classification_service.py), [`backend/app/api/v1/endpoints/classification.py`](file:///c:/dev/web/EcoSense/backend/app/api/v1/endpoints/classification.py).
  - Frontend: [`frontend/src/pages/student/AIClassificationPage.tsx`](file:///c:/dev/web/EcoSense/frontend/src/pages/student/AIClassificationPage.tsx).
- **Implementation Mechanics:**
  - Supports both multi-part file upload (`/api/v1/classification/upload`) and Base64 Data URI strings (`/api/v1/classification`).
  - Model loader dynamically checks for the presence of `ai/models/waste_classifier_v2.pkl`. If present, initializes `FastAIWasteClassifier`; otherwise, falls back to `MockWasteClassifier` (`v1.0-mock`).
  - FastAI vocabulary mapped to DBIT campus categories:
    - `organic` $\rightarrow$ `WET_ORGANIC`
    - `plastic`, `glass`, `textile` $\rightarrow$ `DRY_RECYCLABLE`
    - `paper`, `cardboard` $\rightarrow$ `PAPER`
    - `metal` $\rightarrow$ `METAL`
    - `e-waste` $\rightarrow$ `E_WASTE`
  - Inferences logged in `waste_classifications` with confidence score, probabilities, and model version. Low-confidence flag (`< 0.70`) triggers manual inspection advice in UI.

### Feature 6: Time-Series Bin Fill Level Monitoring & Forecasting
- **Purpose:** Ingest periodic fill readings and forecast future fill levels to anticipate overflows.
- **Source Files:**
  - Subsystem: [`ai/prediction/features.py`](file:///c:/dev/web/EcoSense/ai/prediction/features.py), [`ai/prediction/model.py`](file:///c:/dev/web/EcoSense/ai/prediction/model.py), [`ai/prediction/preprocessing.py`](file:///c:/dev/web/EcoSense/ai/prediction/preprocessing.py).
  - Service & API: [`backend/app/services/prediction_service.py`](file:///c:/dev/web/EcoSense/backend/app/services/prediction_service.py), [`backend/app/api/v1/endpoints/predictions.py`](file:///c:/dev/web/EcoSense/backend/app/api/v1/endpoints/predictions.py).
  - Frontend: [`frontend/src/pages/collector/CollectorPredictionsPage.tsx`](file:///c:/dev/web/EcoSense/frontend/src/pages/collector/CollectorPredictionsPage.tsx).
- **Implementation Mechanics:**
  - Enforces minimum data sufficiency (`MIN_PREDICTION_READINGS = 3`); returns HTTP 422 if insufficient data.
  - Feature pipeline (`segment_cycle_readings`) segments telemetry to isolate the current accumulation cycle following the last collection event ($85\% \rightarrow 0\%$).
  - Baseline linear rate extrapolation model computes accumulation rate $r = \frac{\Delta \text{fill}}{\Delta t}$ and projects target fill percentage clamped to $[0.0, 100.0]$.
  - Forecasts persisted in `fill_predictions` with lower and upper confidence bounds.

### Feature 7: Waste Collection Lifecycle & Field Task Operations
- **Purpose:** Manage sanitation rounds, record collected weights, and track bin emptyings.
- **Source Files:**
  - Backend: [`backend/app/models/collection.py`](file:///c:/dev/web/EcoSense/backend/app/models/collection.py), [`backend/app/models/task.py`](file:///c:/dev/web/EcoSense/backend/app/models/task.py), [`backend/app/services/collection_service.py`](file:///c:/dev/web/EcoSense/backend/app/services/collection_service.py), [`backend/app/services/task_service.py`](file:///c:/dev/web/EcoSense/backend/app/services/task_service.py).
  - Frontend: [`frontend/src/pages/collector/CollectorScanPage.tsx`](file:///c:/dev/web/EcoSense/frontend/src/pages/collector/CollectorScanPage.tsx), [`frontend/src/pages/collector/CollectorTasksPage.tsx`](file:///c:/dev/web/EcoSense/frontend/src/pages/collector/CollectorTasksPage.tsx).
- **Implementation Mechanics:**
  - Collectors record `fill_level_before` (e.g., $90\%$), `collected_quantity_kg` (e.g., $18.5\text{ kg}$), and `fill_level_after` (typically $0\%$).
  - Updating a collection automatically updates `bins.current_fill_percentage` to `fill_level_after`.
  - Field task status progression: `ASSIGNED` $\rightarrow$ `ACCEPTED` $\rightarrow$ `IN_PROGRESS` $\rightarrow$ `COMPLETED` / `CANCELLED`.
  - Task completion optionally links to a newly created `collection_id`.

### Feature 8: Collector Daily Shift Attendance & Availability Operations
- **Purpose:** Track real-time campus housekeeping presence and ensure tasks are delegated to active personnel.
- **Source Files:**
  - Backend: [`backend/app/models/attendance.py`](file:///c:/dev/web/EcoSense/backend/app/models/attendance.py), [`backend/app/services/attendance_service.py`](file:///c:/dev/web/EcoSense/backend/app/services/attendance_service.py), [`backend/app/api/v1/endpoints/attendance.py`](file:///c:/dev/web/EcoSense/backend/app/api/v1/endpoints/attendance.py).
  - Frontend: [`frontend/src/pages/collector/CollectorDashboard.tsx`](file:///c:/dev/web/EcoSense/frontend/src/pages/collector/CollectorDashboard.tsx), [`frontend/src/pages/admin/AdminCollectorOperationsPage.tsx`](file:///c:/dev/web/EcoSense/frontend/src/pages/admin/AdminCollectorOperationsPage.tsx).
- **Implementation Mechanics:**
  - Collectors execute app-based shift check-in and check-out.
  - Server-side timezone validation (`settings.CAMPUS_TIMEZONE = "Asia/Kolkata"`) prevents UTC date discrepancies.
  - Constraint enforces at most one `ACTIVE` shift per collector at any time.
  - Admin dashboard displays real-time attendance badges (`ON_SHIFT`, `CHECKED_OUT`, `NOT_CHECKED_IN`) and active task workloads.

### Feature 9: Waste Recycling & Organic Composting Batch Tracking
- **Purpose:** Track physical processing of collected waste into compost or recycled raw materials.
- **Source Files:**
  - Backend: [`backend/app/models/processing.py`](file:///c:/dev/web/EcoSense/backend/app/models/processing.py), [`backend/app/services/processing_service.py`](file:///c:/dev/web/EcoSense/backend/app/services/processing_service.py), [`backend/app/api/v1/endpoints/processing.py`](file:///c:/dev/web/EcoSense/backend/app/api/v1/endpoints/processing.py).
  - Frontend: [`frontend/src/pages/collector/CollectorProcessingPage.tsx`](file:///c:/dev/web/EcoSense/frontend/src/pages/collector/CollectorProcessingPage.tsx), [`frontend/src/pages/admin/AdminProcessingPage.tsx`](file:///c:/dev/web/EcoSense/frontend/src/pages/admin/AdminProcessingPage.tsx).
- **Implementation Mechanics:**
  - Processing records link directly to a source `collection_id`.
  - Domain rules:
    - `COMPOSTING` permitted only for `WET_ORGANIC` and `GARDEN` waste streams.
    - `RECYCLING` permitted only for `DRY_RECYCLABLE`, `PAPER`, `METAL`, and `E_WASTE`.
  - Cumulative quantity check: Sum of processed quantities across batches cannot exceed `collection_records.collected_quantity_kg`.

### Feature 10: Gamification Ledger, EcoStages, and Rewards Redemption
- **Purpose:** Incentivize campus participation through an auditable, append-only points economy.
- **Source Files:**
  - Backend: [`backend/app/models/gamification.py`](file:///c:/dev/web/EcoSense/backend/app/models/gamification.py), [`backend/app/core/gamification_config.py`](file:///c:/dev/web/EcoSense/backend/app/core/gamification_config.py), [`backend/app/services/gamification_service.py`](file:///c:/dev/web/EcoSense/backend/app/services/gamification_service.py).
  - Frontend: [`frontend/src/pages/student/RewardsCatalogPage.tsx`](file:///c:/dev/web/EcoSense/frontend/src/pages/student/RewardsCatalogPage.tsx), [`frontend/src/pages/student/StudentLeaderboardPage.tsx`](file:///c:/dev/web/EcoSense/frontend/src/pages/student/StudentLeaderboardPage.tsx).
- **Implementation Mechanics:**
  - Points ledger enforces balance integrity:
    $$\text{Current Balance} = \sum \text{EARN} - \sum |\text{REDEEM}| \pm \sum \text{ADJUSTMENT}$$
  - **Six EcoStages:**
    1. *Eco Seed* (0 pts)
    2. *Green Sprout* (100 pts)
    3. *Eco Explorer* (300 pts)
    4. *Sustainability Champion* (750 pts)
    5. *Eco Guardian* (1,500 pts)
    6. *Campus Earth Hero* (3,000 pts)
  - EcoStages are computed strictly from **lifetime cumulative `EARN` points** so that spending points on rewards never degrades a user's stage rank.
  - Redeeming rewards deducts stock transactionally and records a `REDEEM` entry in `point_transactions`.

### Feature 11: Real-Time Web Push Notifications via Firebase Cloud Messaging (FCM)
- **Purpose:** Dispatch instant alerts for new task assignments, delegated waste reports, and urgent collections without recurrent SMS costs.
- **Source Files:**
  - Backend: [`backend/app/models/device_token.py`](file:///c:/dev/web/EcoSense/backend/app/models/device_token.py), [`backend/app/models/notification.py`](file:///c:/dev/web/EcoSense/backend/app/models/notification.py), [`backend/app/services/push_notification_service.py`](file:///c:/dev/web/EcoSense/backend/app/services/push_notification_service.py), [`backend/app/api/v1/endpoints/notifications.py`](file:///c:/dev/web/EcoSense/backend/app/api/v1/endpoints/notifications.py).
  - Frontend: [`frontend/src/context/NotificationContext.tsx`](file:///c:/dev/web/EcoSense/frontend/src/context/NotificationContext.tsx), [`frontend/public/firebase-messaging-sw.js`](file:///c:/dev/web/EcoSense/frontend/public/firebase-messaging-sw.js).
- **Implementation Mechanics:**
  - Browsers register service worker and obtain VAPID token via `getToken(messaging, { vapidKey })`.
  - Token uploaded to `POST /api/v1/notifications/devices`.
  - Backend initializes Firebase Admin SDK singleton with service account JSON (`secrets/serviceAccountKey.json`).
  - Dispatching sends payload with `title`, `body`, and `click_action` URL.
  - Automatic pruning: If Firebase returns `UnregisteredError` or `InvalidArgumentError`, the dead token is automatically set to `is_active = False` in the database.

### Feature 12: Administrative Analytics Engine (13 Dedicated Endpoints)
- **Purpose:** Compute operational, participatory, and environmental diversion metrics for administrative governance and institutional audits.
- **Source Files:**
  - Backend: [`backend/app/services/analytics_service.py`](file:///c:/dev/web/EcoSense/backend/app/services/analytics_service.py), [`backend/app/api/v1/endpoints/analytics.py`](file:///c:/dev/web/EcoSense/backend/app/api/v1/endpoints/analytics.py).
  - Frontend: [`frontend/src/pages/admin/AdminAnalyticsPage.tsx`](file:///c:/dev/web/EcoSense/frontend/src/pages/admin/AdminAnalyticsPage.tsx).
- **Implementation Mechanics:**
  - 13 distinct endpoints: `/summary`, `/waste-types`, `/locations`, `/trends`, `/collections`, `/bin-fill`, `/alerts`, `/reports`, `/processing`, `/participation`, `/gamification`, `/predictions`, `/classifications`.
  - Database-side aggregation with strict UTC date range normalization (`_normalize_date_range`).
  - Real-time operational alerts derived dynamically from current system state without requiring static alert tables.

### Feature 13: Physical Placard PDF & Print Engine (One-Bin-Per-Page)
- **Purpose:** Generate print-ready vector placards for physical installation on campus bins.
- **Source Files:**
  - Frontend: [`frontend/src/components/common/BinQRPdfDocument.tsx`](file:///c:/dev/web/EcoSense/frontend/src/components/common/BinQRPdfDocument.tsx), [`frontend/src/components/common/BinQRPrintSheet.tsx`](file:///c:/dev/web/EcoSense/frontend/src/components/common/BinQRPrintSheet.tsx), [`frontend/src/utils/pdfGenerator.ts`](file:///c:/dev/web/EcoSense/frontend/src/utils/pdfGenerator.ts).
- **Implementation Mechanics:**
  - Uses `@react-pdf/renderer` to generate multi-page PDF documents where each bin occupies exactly **one page**.
  - Features high-contrast QR matrix (`level="H"`, 240px+), official DBIT branding, bin code, waste stream color tag, and scan instructions.
  - Browser print stylesheet utilizes `@media print { .qr-print-sheet { page-break-after: always; } }`.

### Feature 14: Administrative User & Campus Asset Management
- **Purpose:** Full administrative CRUD control over campus bins, locations, waste streams, and user accounts.
- **Source Files:**
  - Backend: [`backend/app/services/user_service.py`](file:///c:/dev/web/EcoSense/backend/app/services/user_service.py), [`backend/app/api/v1/endpoints/users.py`](file:///c:/dev/web/EcoSense/backend/app/api/v1/endpoints/users.py).
  - Frontend: [`frontend/src/pages/admin/AdminUsersPage.tsx`](file:///c:/dev/web/EcoSense/frontend/src/pages/admin/AdminUsersPage.tsx), [`frontend/src/pages/admin/AdminBinsPage.tsx`](file:///c:/dev/web/EcoSense/frontend/src/pages/admin/AdminBinsPage.tsx).
- **Implementation Mechanics:**
  - Admins can create users, change roles, deactivate accounts, and update contact phone numbers.
  - Bins can be reassigned between locations or marked `DAMAGED` / `MISSING`.

---

## 6. Dataset and Data Engineering Documentation

### 6.1 Dataset Inventory

| Dataset / Source | Origin & Format | Storage Location | Size / Volume | Purpose in System | Implementation Status |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **Initial DBIT Seed Data** | Python Seed Script (`seed_dev_data.py`) | [`backend/scripts/seed_dev_data.py`](file:///c:/dev/web/EcoSense/backend/scripts/seed_dev_data.py) | 4 users, 5 locations, 6 waste types, 5 bins, 5 rewards | Bootstrapping fresh development and Docker instances | **ACTIVE** |
| **FastAI Pretrained Weights** | PyTorch / FastAI Pickle (`.pkl`) | [`ai/models/waste_classifier_v2.pkl`](file:///c:/dev/web/EcoSense/ai/models/waste_classifier_v2.pkl) | 103.18 MB (Serialized network graph & weights) | Transfer-learning vision classification across 8 categories | **ACTIVE** |
| **Operational Bin Telemetry** | PostgreSQL Table (`bin_fill_readings`) | Database `bin_fill_readings` table | Dynamic operational records | Time-series inputs for accumulation forecasting | **ACTIVE** |
| **Collection & Disposal Logs**| PostgreSQL Tables (`collection_records`, `disposals`) | Database relational tables | Dynamic operational records | Input features for recycling, composting, and diversion rate | **ACTIVE** |
| **Ground-Truth Campus Benchmark**| Labeled DBIT Campus Benchmark Photos | *Not bundled in repository* | Target: 2,000–5,000 photos | Formal empirical benchmark evaluation | *PLANNED* |

### 6.2 Schema and Feature Descriptions

#### Initial Seed Data (DBIT Campus Baseline)
- **Waste Types:**
  - `WET_ORGANIC`: Food leftovers, canteen kitchen scraps, tea leaves.
  - `DRY_RECYCLABLE`: Plastic containers, PET bottles, clean packaging.
  - `PAPER`: Exam papers, cardboard boxes, shredded office documents.
  - `METAL`: Soda cans, scrap wire, tin foil containers.
  - `E_WASTE`: Obsolete circuit boards, broken cables, computer mice.
  - `GARDEN`: Grass clippings, dry leaves, botanical trimmings.
- **Sample Locations:**
  - `Canteen`: Main Building, Ground Floor.
  - `Computer Lab`: Engineering Block, 2nd Floor.
  - `Admin Office`: Admin Block, 1st Floor.
  - `Workshop`: Mechanical Shed, Ground Floor.
  - `Campus Garden`: Campus Grounds, Ground Floor.

### 6.3 Data Preparation & Time-Series Preprocessing

The time-series feature engineering pipeline is implemented in [`ai/prediction/features.py`](file:///c:/dev/web/EcoSense/ai/prediction/features.py) and [`ai/prediction/preprocessing.py`](file:///c:/dev/web/EcoSense/ai/prediction/preprocessing.py):

```text
Raw Database Readings ──> Chronological Sorting ──> Datetime Normalization (UTC)
                                                            │
                                                            ▼
Cycle Boundary Isolation <── Segmentation Filter <── Post-Collection Slicing
       │
       ▼
Weighted Rate Computation:
  Δfill = fill[t] - fill[t-1]
  Δt    = hours(t - t_prev)
  r     = Σ(Δfill) / Σ(Δt)  (%/hour)
       │
       ▼
Temporal Horizon Encoding ──> 13-Element Feature Vector (BinFillFeatures)
```

1. **Cycle Boundary Isolation:** Because emptying a bin introduces a dramatic non-linear drop (e.g., $90\% \rightarrow 0\%$), standard linear regression across historical data would calculate negative accumulation rates. `segment_cycle_readings()` identifies collection timestamps and isolates telemetry recorded *after* the most recent collection.
2. **Weighted Rate Calculation:** Handles irregular reading intervals by weighting fill deltas across elapsed hours:
   $$r_{\text{hourly}} = \frac{y_{\text{last}} - y_{\text{first}}}{\Delta t_{\text{total}}}$$
3. **Strict No-Lookahead Temporal Boundary:** Only telemetry timestamped $\le \text{prediction\_timestamp}$ is supplied to the feature extractor, preventing temporal leakage during training and backtesting.

### 6.4 Data Lineage Diagram

```mermaid
graph TD
    Physical[Physical Campus Activity] -->|User Scans & Disposes| D_Disposal[disposal_records]
    Physical -->|Sensor / Manual Reading| D_Reading[bin_fill_readings]
    Physical -->|Collector Empties Bin| D_Collection[collection_records]
    Physical -->|Student Files Issue| D_Report[waste_reports]

    D_Reading --> Preprocessing[ai.prediction.preprocessing]
    D_Collection --> Preprocessing
    Preprocessing --> FeatureExtractor[ai.prediction.features]
    FeatureExtractor --> Forecaster[BaselineFillPredictor]
    Forecaster --> D_Prediction[fill_predictions]

    D_Disposal --> GamificationService[app.services.gamification_service]
    D_Report --> AdminResolution[app.services.report_service]
    AdminResolution --> GamificationService
    GamificationService --> D_Ledger[point_transactions]
    D_Ledger --> EcoStages[Lifetime Stage Progress & Leaderboard]

    D_Collection --> ProcessingService[app.services.processing_service]
    ProcessingService --> D_Processing[processing_records]

    D_Disposal --> AnalyticsService[app.services.analytics_service]
    D_Reading --> AnalyticsService
    D_Collection --> AnalyticsService
    D_Processing --> AnalyticsService
    D_Prediction --> AnalyticsService
    AnalyticsService --> AdminDashboard[13 Domain Analytics Dashboards]
```

---

## 7. Machine Learning, AI, or Algorithmic Implementation

### 7.1 Computer Vision Waste Classifier

The classification subsystem employs an abstract interface design:

- **Interface:** `BaseWasteClassifier` ([`ai/classification/classifier.py`](file:///c:/dev/web/EcoSense/ai/classification/classifier.py)) defining `classify(image_input: str) -> ClassificationPrediction`.
- **Production Model (`FastAIWasteClassifier`):**
  - **Framework:** FastAI 2.8+ on PyTorch 2.x.
  - **Artifact:** [`ai/models/waste_classifier_v2.pkl`](file:///c:/dev/web/EcoSense/ai/models/waste_classifier_v2.pkl) (103.18 MB).
  - **Input:** PIL RGB Image decoded from Base64 Data URI, HTTP/HTTPS URL, or local file reference.
  - **Inference Pipeline:**
    1. Validate input URI string using regex and path-traversal sanitizers (`validate_image_reference`).
    2. Decode binary data into an in-memory buffer (`io.BytesIO`) and convert to RGB.
    3. Execute inference via `self.learn.predict(img)`.
    4. Extract predicted category, index, and Softmax probability distribution.
    5. Map model label to standard campus category via `FASTAI_TO_ECOSENSE_CLASS_MAP`.
    6. Return `ClassificationPrediction` containing `predicted_class`, `confidence_score`, `model_version`, and full probability breakdown dictionary.
- **Fallback Mock Model (`MockWasteClassifier`):**
  - Used when FastAI weights are absent or during headless unit testing.
  - Analyzes keywords (e.g. `"bottle"`, `"banana"`, `"battery"`) or generates deterministic category assignments using SHA-256 string hashing.

### 7.2 Waste Generation & Bin Fill Forecasting Model

- **Interface:** `BaseFillPredictor` ([`ai/prediction/predictor.py`](file:///c:/dev/web/EcoSense/ai/prediction/predictor.py)).
- **Current Model (`BaselineFillPredictor`, version `baseline-v1`):**
  - **Type:** Time-series cycle-segmented linear extrapolation baseline.
  - **Mathematical Formulation:**
    $$\hat{y} = \min\left(100.0, \max\left(0.0, y_{\text{current}} + r_{\text{hourly}} \times \Delta t_{\text{hours}}\right)\right)$$
  - **Uncertainty Bounds:**
    $$\text{Margin} = \begin{cases} \pm 5.0\% & \text{if } N_{\text{readings}} \ge 5 \\ \pm 8.0\% & \text{otherwise} \end{cases}$$
    $$\text{Lower Bound} = \max(0.0, \hat{y} - \text{Margin}), \quad \text{Upper Bound} = \min(100.0, \hat{y} + \text{Margin})$$

### 7.3 Forecasting Model Evaluation Framework

Implemented in [`ai/prediction/evaluation.py`](file:///c:/dev/web/EcoSense/ai/prediction/evaluation.py):

1. **Mean Absolute Error (MAE):**
   $$\text{MAE} = \frac{1}{N} \sum_{i=1}^N |y_i - \hat{y}_i|$$
2. **Root Mean Squared Error (RMSE):**
   $$\text{RMSE} = \sqrt{\frac{1}{N} \sum_{i=1}^N (y_i - \hat{y}_i)^2}$$
3. **Chronological Splitting (`chronological_train_test_split`):** Splits time-series sequentially without shuffling to prevent temporal lookahead leakage.

### 7.4 Strategic 8-Stage AI/ML Production Roadmap

```text
[Stage 1: Campus Data Gathering] (Capture 2,000+ DBIT photos across lighting conditions)
                  │
                  ▼
[Stage 2: Ground-Truth Annotation] (Annotate with 6 DBIT waste classes)
                  │
                  ▼
[Stage 3: Baseline Benchmarking] (CURRENT STATUS: FastAI v2.0 + Baseline-v1 active)
                  │
                  ▼
[Stage 4: Supervised Model Training] (Fine-tune MobileNetV3 / Train LightGBM Forecaster)
                  │
                  ▼
[Stage 5: Offline Model Evaluation] (Benchmark MAE/RMSE against baseline-v1)
                  │
                  ▼
[Stage 6: Serialization to ONNX] (Export to .onnx for lightweight CPU inference)
                  │
                  ▼
[Stage 7: Production Frontend Testing] (Validate camera streams across student devices)
                  │
                  ▼
[Stage 8: Continuous Drift Monitoring] (Monitor confidence drift in waste_classifications)
```

---

## 8. Complete API and Interface Documentation

The FastAPI backend exposes **18 domain routers** under the `/api/v1` prefix:

### 8.1 API Router Summary Table

| Domain Router | Prefix | Tag | Primary Endpoints & Operations | Auth Requirements |
| :--- | :--- | :--- | :--- | :--- |
| **Authentication** | `/api/v1/auth` | Authentication | `POST /login`, `GET /me` | Public login; Bearer token for `/me` |
| **Users** | `/api/v1/users` | Users | `GET /`, `POST /`, `GET /{id}`, `PATCH /{id}`, `PATCH /{id}/phone` | `ADMIN` only (except `/me`) |
| **Locations** | `/api/v1/locations`| Locations | `GET /`, `POST /`, `GET /{id}` | Authenticated read; `ADMIN` write |
| **Waste Types** | `/api/v1/waste-types`| Waste Types | `GET /`, `POST /`, `GET /{id}` | Authenticated read; `ADMIN` write |
| **Bins** | `/api/v1/bins` | Bins | `GET /`, `POST /`, `GET /{id}`, `PATCH /{id}`, `GET /public/{qr_token}`, `GET /qr/{qr_token}` | `/public/{qr}` is Unauthenticated; Others Authenticated |
| **Fill Readings**| `/api/v1/fill-readings`| Fill Readings | `POST /`, `GET /bins/{id}/fill-readings` | Authenticated |
| **Collections** | `/api/v1/collections`| Collections | `POST /`, `GET /`, `GET /{id}` | `COLLECTOR` or `ADMIN` |
| **Disposals** | `/api/v1/disposals`| Disposals | `POST /`, `GET /my`, `GET /` | `STUDENT`/`STAFF` write; `ADMIN` list |
| **Reports** | `/api/v1/reports` | Reports | `POST /`, `GET /`, `GET /my`, `PATCH /{id}/resolve` | Authenticated; Resolve is `ADMIN` only |
| **Classification**| `/api/v1/classification`| Classification | `POST /`, `POST /upload`, `GET /` | Authenticated |
| **Predictions** | `/api/v1/bins/{id}/predictions`| Predictions | `POST /`, `GET /` | Authenticated |
| **Processing** | `/api/v1/processing`| Recycling & Composting | `POST /`, `GET /`, `GET /{id}` | `COLLECTOR` or `ADMIN` |
| **Gamification** | `/api/v1/gamification`| Gamification | `GET /balance`, `GET /transactions`, `GET /leaderboard`, `POST /adjustments` | Authenticated; Adjustments `ADMIN` |
| **Rewards** | `/api/v1/rewards` | Rewards | `GET /`, `POST /`, `POST /{id}/redeem`, `GET /redemptions` | Catalog Authenticated; Redeem is Student |
| **Analytics** | `/api/v1/analytics`| Analytics | 13 Dedicated GET endpoints (`/summary`, `/trends`, etc.) | `ADMIN` only |
| **Attendance** | `/api/v1/attendance`| Attendance | `POST /check-in`, `POST /check-out`, `GET /status`, `GET /admin/overview` | `COLLECTOR` check-in/out; `ADMIN` overview |
| **Tasks** | `/api/v1/tasks` | Tasks | `POST /`, `GET /`, `PATCH /{id}/status`, `POST /delegate-report` | `ADMIN` manage; `COLLECTOR` view & status |
| **Notifications**| `/api/v1/notifications`| Notifications | `POST /devices`, `DELETE /devices`, `GET /history`, `POST /test-push` | Authenticated |

### 8.2 Representative API Endpoint Specifications

#### 1. Public Bin Lookup (`GET /api/v1/bins/public/{qr_token}`)
- **Method & Path:** `GET /api/v1/bins/public/{qr_token}`
- **Authentication:** None (Public Endpoint).
- **Path Parameters:** `qr_token` (UUID).
- **Response Schema (`BinQRRead`):**
  ```json
  {
    "bin_id": "9b1deb4d-3b7d-4bad-9bdd-2b0d7b3dcb6d",
    "bin_code": "CANTEEN-WET-01",
    "qr_token": "550e8400-e29b-41d4-a716-446655440000",
    "status": "ACTIVE",
    "current_fill_percentage": 45.0,
    "capacity_litres": 80.0,
    "location": {
      "location_id": 1,
      "name": "Canteen",
      "building": "Main Building",
      "floor": "Ground Floor"
    },
    "waste_type": {
      "waste_type_id": 1,
      "name": "WET_ORGANIC",
      "description": "Organic and food waste"
    }
  }
  ```
- **Error Responses:** 404 Not Found if `qr_token` does not exist.

#### 2. Create Waste Disposal (`POST /api/v1/disposals`)
- **Method & Path:** `POST /api/v1/disposals`
- **Authentication:** Bearer JWT (`STUDENT`, `STAFF`, or `ADMIN`).
- **Request Body (`DisposalCreate`):**
  ```json
  {
    "bin_id": "9b1deb4d-3b7d-4bad-9bdd-2b0d7b3dcb6d",
    "quantity_kg": 0.35,
    "notes": "Canteen lunch food scraps"
  }
  ```
- **Response (`DisposalRead`):**
  ```json
  {
    "disposal_id": 1042,
    "user_id": "a1b2c3d4-e5f6-7a8b-9c0d-1e2f3a4b5c6d",
    "bin_id": "9b1deb4d-3b7d-4bad-9bdd-2b0d7b3dcb6d",
    "quantity_kg": 0.35,
    "recorded_at": "2026-10-23T14:30:00Z",
    "notes": "Canteen lunch food scraps",
    "points_awarded": 10
  }
  ```
- **Error Responses:** 404 Bin Not Found, 400 Inactive Bin, 401 Unauthorized.

#### 3. AI Waste Classification (`POST /api/v1/classification`)
- **Method & Path:** `POST /api/v1/classification`
- **Authentication:** Bearer JWT.
- **Request Body (`ClassificationCreate`):**
  ```json
  {
    "image_url": "data:image/jpeg;base64,/9j/4AAQSkZJRg...",
    "disposal_id": null
  }
  ```
- **Response (`ClassificationRead`):**
  ```json
  {
    "classification_id": 851,
    "user_id": "a1b2c3d4-e5f6-7a8b-9c0d-1e2f3a4b5c6d",
    "image_url": "data:image/jpeg;base64,...",
    "predicted_waste_type_id": 2,
    "predicted_waste_type": {
      "waste_type_id": 2,
      "name": "DRY_RECYCLABLE"
    },
    "confidence_score": 0.9421,
    "model_version": "v2.0-fastai",
    "low_confidence": false,
    "metadata": {
      "raw_prediction": "plastic",
      "probabilities": {
        "organic": 0.012,
        "plastic": 0.9421,
        "glass": 0.021,
        "paper": 0.015,
        "metal": 0.009
      }
    }
  }
  ```

---

## 9. Database, Storage, and Data Models

### 9.1 Database Architecture

The persistence layer runs on **PostgreSQL 16**. It leverages the `pgcrypto` extension for server-side cryptographic UUID generation (`gen_random_uuid()`). All primary keys for users and physical bins utilize 128-bit UUIDs, while sequential transactional records (disposals, collections, ledger entries) utilize 64-bit `BigInteger` keys for indexing efficiency.

### 9.2 Complete Entity-Relationship (ER) Diagram

```mermaid
erDiagram
    roles ||--o{ users : "has"
    users ||--o{ disposal_records : "logs"
    users ||--o{ waste_reports : "submits"
    users ||--o{ collection_records : "collects"
    users ||--o{ waste_classifications : "classifies"
    users ||--o{ processing_records : "processes"
    users ||--o{ point_transactions : "earns/redeems"
    users ||--o{ reward_redemptions : "claims"
    users ||--o{ collector_attendance : "records"
    users ||--o{ collection_tasks : "assigned_to"
    users ||--o{ task_notifications : "receives"
    users ||--o{ device_tokens : "registers"

    locations ||--o{ bins : "houses"
    locations ||--o{ collection_tasks : "target_location"

    waste_types ||--o{ bins : "designated_stream"
    waste_types ||--o{ waste_classifications : "predicted_stream"

    bins ||--o{ disposal_records : "receives"
    bins ||--o{ waste_reports : "associated_with"
    bins ||--o{ bin_fill_readings : "telemetry"
    bins ||--o{ collection_records : "emptied"
    bins ||--o{ fill_predictions : "forecasted"
    bins ||--o{ collection_tasks : "target_bin"

    collection_records ||--o{ processing_records : "supplies"
    collection_records ||--o{ collection_tasks : "verifies"

    rewards ||--o{ reward_redemptions : "redeemed_item"
    waste_reports ||--o{ collection_tasks : "delegated_as"
    collection_tasks ||--o{ task_notifications : "triggers"

    roles {
        smallint role_id PK
        varchar role_name UK
    }

    users {
        uuid user_id PK
        smallint role_id FK
        varchar name
        varchar email UK
        text password_hash
        varchar phone_number
        boolean is_active
        boolean push_notifications_enabled
        timestamp created_at
    }

    locations {
        bigint location_id PK
        varchar name
        varchar location_type
        varchar building
        varchar floor
        text description
        timestamp created_at
    }

    waste_types {
        smallint waste_type_id PK
        varchar name UK
        text description
        timestamp created_at
    }

    bins {
        uuid bin_id PK
        varchar bin_code UK
        bigint location_id FK
        smallint waste_type_id FK
        numeric capacity_litres
        uuid qr_token UK
        numeric current_fill_percentage
        varchar status
        timestamp installed_at
        timestamp created_at
        timestamp updated_at
    }

    disposal_records {
        bigint disposal_id PK
        uuid user_id FK
        uuid bin_id FK
        numeric quantity_kg
        timestamp recorded_at
        text notes
    }

    waste_reports {
        bigint report_id PK
        uuid user_id FK
        uuid bin_id FK
        varchar report_type
        text description
        text image_url
        varchar status
        timestamp created_at
        timestamp resolved_at
        uuid resolved_by FK
    }

    bin_fill_readings {
        bigint reading_id PK
        uuid bin_id FK
        numeric fill_percentage
        timestamp recorded_at
        varchar source
        text notes
    }

    collection_records {
        bigint collection_id PK
        uuid bin_id FK
        uuid collector_id FK
        numeric fill_level_before
        numeric collected_quantity_kg
        numeric fill_level_after
        timestamp collected_at
        text notes
    }

    waste_classifications {
        bigint classification_id PK
        uuid user_id FK
        bigint disposal_id FK
        text image_url
        smallint predicted_waste_type_id FK
        numeric confidence_score
        varchar model_version
        timestamp created_at
    }

    fill_predictions {
        bigint prediction_id PK
        uuid bin_id FK
        numeric predicted_fill_percentage
        timestamp prediction_timestamp
        timestamp target_timestamp
        varchar model_version
        numeric confidence_score
        numeric lower_bound
        numeric upper_bound
        timestamp created_at
    }

    processing_records {
        bigint processing_id PK
        bigint collection_id FK
        varchar processing_type
        numeric quantity_kg
        timestamp processed_at
        uuid processed_by FK
        varchar status
        text notes
        timestamp created_at
    }

    point_transactions {
        bigint transaction_id PK
        uuid user_id FK
        varchar transaction_type
        int points
        varchar source_type
        bigint source_id
        text description
        timestamp created_at
        uuid created_by FK
    }

    point_rules {
        smallint rule_id PK
        varchar action_type UK
        int points
        text description
        boolean is_active
        timestamp created_at
        timestamp updated_at
    }

    rewards {
        bigint reward_id PK
        varchar name
        text description
        int points_cost
        int stock_quantity
        boolean is_active
        timestamp created_at
        timestamp updated_at
    }

    reward_redemptions {
        bigint redemption_id PK
        bigint reward_id FK
        uuid user_id FK
        int points_spent
        varchar status
        timestamp redeemed_at
        timestamp fulfilled_at
        timestamp cancelled_at
        text notes
        timestamp created_at
    }

    collector_attendance {
        bigint attendance_id PK
        uuid collector_id FK
        date attendance_date
        timestamp check_in_at
        timestamp check_out_at
        varchar status
        text notes
        timestamp created_at
        timestamp updated_at
    }

    collection_tasks {
        bigint task_id PK
        varchar task_type
        uuid collector_id FK
        uuid bin_id FK
        bigint location_id FK
        bigint report_id FK
        varchar priority
        varchar title
        text instructions
        timestamp due_date
        varchar status
        uuid created_by FK
        timestamp assigned_at
        timestamp started_at
        timestamp completed_at
        text completion_notes
        timestamp cancelled_at
        text cancellation_reason
        bigint collection_id FK
        timestamp created_at
        timestamp updated_at
    }

    task_notifications {
        bigint notification_id PK
        bigint task_id FK
        bigint report_id FK
        uuid recipient_user_id FK
        varchar notification_type
        varchar channel
        varchar title
        text body
        varchar status
        varchar provider_msg_id
        text error_message
        timestamp created_at
    }

    device_tokens {
        bigint token_id PK
        uuid user_id FK
        varchar fcm_token UK
        varchar device_name
        boolean is_active
        timestamp created_at
        timestamp updated_at
    }
```

### 9.3 Database Integrity Constraints & Partial Indexes

1. **Anti-Duplication Ledger Index:**
   `ix_point_transactions_unique_earn_source` on `(source_type, source_id, transaction_type)` ensures points can be earned at most once for any given disposal or report.
2. **Single Active Shift Constraint:**
   A partial index/constraint prevents collectors from opening multiple simultaneous shifts (`status = 'ACTIVE'`).
3. **Fill Percentage Bounds:**
   Check constraints verify $0 \le \text{fill\_percentage} \le 100$ on `bins`, `bin_fill_readings`, `collection_records`, and `fill_predictions`.
4. **Positive Quantities:**
   Check constraints verify `quantity_kg > 0` on `disposal_records`, `collection_records`, and `processing_records`.

---

## 10. Configuration and Environment Setup

### 10.1 Environment Variables Reference

#### Backend (`backend/.env`)

| Variable Name | Type | Required | Default / Example | Purpose |
| :--- | :--- | :--- | :--- | :--- |
| `DATABASE_URL` | String | Yes | `postgresql+psycopg://postgres:tiger@localhost:5432/ecosense` | Database connection URL |
| `JWT_SECRET_KEY` | String | Yes | *Cryptographic 64-char string* | Secret key for signing JWT tokens |
| `JWT_ALGORITHM` | String | No | `HS256` | JWT signing algorithm |
| `ACCESS_TOKEN_EXPIRE_MINUTES`| Integer | No | `1440` (24 Hours) | JWT expiration lifetime |
| `APP_NAME` | String | No | `EcoSense API` | OpenAPI application title |
| `ENVIRONMENT` | String | No | `development` | Runtime environment name |
| `API_V1_STR` | String | No | `/api/v1` | Root API route prefix |
| `CORS_ORIGINS` | JSON Array | No | `["http://localhost:5173", ...]` | Allowed CORS origin URLs |
| `CLASSIFICATION_MODEL_PATH` | Path | No | `ai/models/waste_classifier_v2.pkl` | Path to vision classifier checkpoint |
| `CLASSIFICATION_MODEL_VERSION`| String | No | `v2.0-fastai` | Classification model version tag |
| `CLASSIFICATION_CONFIDENCE_THRESHOLD`| Float | No | `0.70` | Threshold below which low-confidence banner displays |
| `PREDICTION_HORIZON_MINUTES`| Integer | No | `120` | Default forecasting horizon in minutes |
| `MIN_PREDICTION_READINGS` | Integer | No | `3` | Minimum readings required for forecasting |
| `CAMPUS_TIMEZONE` | String | No | `Asia/Kolkata` | Institutional timezone for attendance dates |
| `FIREBASE_PUSH_ENABLED` | Boolean | No | `false` | Enable/disable FCM Web Push dispatch |
| `FIREBASE_PROJECT_ID` | String | Cond. | `ecosense-98229` | Firebase project identifier |
| `FIREBASE_SERVICE_ACCOUNT_PATH`| Path | Cond. | `secrets/serviceAccountKey.json` | Path to Firebase Admin service account JSON |
| `PUBLIC_FRONTEND_URL` | URL | No | `https://www.ecosenseapp.site` | Public frontend URL for deep-links |
| `DEV_ADMIN_EMAIL` | Email | No | `admin@dbit.in` | Seed admin email address |
| `DEV_ADMIN_PASSWORD` | String | No | `adminpassword` | Seed admin password |

#### Frontend (`frontend/.env`)

| Variable Name | Type | Required | Default / Example | Purpose |
| :--- | :--- | :--- | :--- | :--- |
| `VITE_API_BASE_URL` | URL | Yes | `http://localhost:8000` | Backend API base URL |
| `VITE_FIREBASE_API_KEY` | String | Cond. | `AIzaSy...` | Firebase Web App public API key |
| `VITE_FIREBASE_AUTH_DOMAIN` | String | Cond. | `ecosense-98229.firebaseapp.com` | Firebase authentication domain |
| `VITE_FIREBASE_PROJECT_ID` | String | Cond. | `ecosense-98229` | Firebase project identifier |
| `VITE_FIREBASE_MESSAGING_SENDER_ID`| String | Cond. | `123456789012` | FCM messaging sender ID |
| `VITE_FIREBASE_APP_ID` | String | Cond. | `1:123456789012:web:abcdef` | Firebase Web App ID |
| `VITE_FIREBASE_VAPID_KEY` | String | Cond. | `B...PublicKey...` | Public VAPID key for web push |

### 10.2 Pre-Seeded Development User Accounts

| Role | Email | Password | Default Landing Interface |
| :--- | :--- | :--- | :--- |
| **System Admin** | `admin@dbit.in` | `adminpassword` | `/admin/dashboard` |
| **Campus Student** | `student@dbit.in` | `studentpassword` | `/student/dashboard` |
| **Department Staff** | `staff@dbit.in` | `staffpassword` | `/staff/dashboard` |
| **Waste Collector** | `collector@dbit.in` | `collectorpassword` | `/collector/dashboard` |

### 10.3 Deployment & Startup Commands

#### Option 1: Docker Compose (Recommended)
```bash
# Build images and start all services:
docker compose up --build

# Stop services preserving database volume:
docker compose down

# Reset all database records to clean state:
docker compose down -v
```

#### Option 2: Bare-Metal Local Development
```powershell
# 1. Start Backend:
cd backend
python -m venv .venv
.\.venv\Scripts\activate
pip install -r requirements.txt
alembic upgrade head
python scripts\seed_dev_data.py
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# 2. Start Frontend (in separate terminal):
cd frontend
npm install
npm run dev
```

---

## 11. End-to-End Workflows and Execution Lifecycle

### 11.1 Student Disposal & Gamification Lifecycle

```mermaid
sequenceDiagram
    autonumber
    actor Student
    participant Scanner as html5-qrcode (Mobile Camera)
    participant UI as Student Web App
    participant API as FastAPI Backend
    participant Ledger as Point Ledger (PostgreSQL)

    Student->>Scanner: Scans QR Code on Canteen Bin
    Scanner-->>UI: Decodes URL /bin/550e8400...
    UI->>API: GET /api/v1/bins/public/550e8400...
    API-->>UI: Bin Info (Canteen Wet Organic, Fill: 45%)
    Student->>UI: Selects Approximate Weight (0.2 kg) & Taps "Log Disposal"
    UI->>API: POST /api/v1/disposals (with Student Bearer JWT)
    API->>Ledger: Insert disposal_records row
    API->>Ledger: Verify anti-duplication index
    API->>Ledger: Insert point_transactions (type='EARN', points=10)
    API-->>UI: Return 201 Created (+10 EcoPoints)
    UI->>UI: Triggers CelebrationModal with confetti
    UI->>Student: Displays updated balance & progress toward Green Sprout
```

### 11.2 Waste Report, Collector Delegation & Resolution Lifecycle

```mermaid
sequenceDiagram
    autonumber
    actor Reporter as Student / Staff
    actor Admin as Facilities Admin
    actor Collector as Sanitation Worker
    participant API as FastAPI Backend
    participant FCM as Firebase Push Gateway
    participant DB as PostgreSQL Database

    Reporter->>API: POST /api/v1/reports (OVERFLOWING_BIN, photo, description)
    DB-->>API: Persist report (status='PENDING')
    Admin->>API: GET /api/v1/reports (Review pending issues)
    Admin->>API: POST /api/v1/tasks/delegate-report (Assign to Collector)
    API->>DB: Create collection_tasks (type='ISSUE_RESPONSE', status='ASSIGNED')
    API->>DB: Update report status='IN_PROGRESS'
    API->>FCM: Dispatch Web Push alert to Collector device
    FCM-->>Collector: Push Notification: "New Urgent Task: Canteen Bin Overflow"
    Collector->>API: PATCH /api/v1/tasks/{id}/status (status='IN_PROGRESS')
    Collector->>API: POST /api/v1/collections (Empty bin: 15.0 kg collected)
    Collector->>API: PATCH /api/v1/tasks/{id}/status (status='COMPLETED')
    Admin->>API: PATCH /api/v1/reports/{id}/resolve (status='RESOLVED')
    API->>DB: Award +25 EcoPoints to Reporter in point_transactions
```

---

## 12. UI/UX and Frontend Design System

### 12.1 Design Aesthetics and Philosophy

The EcoSense frontend is styled using custom **Tailwind CSS design tokens** inspired by clean, modern consumer applications:
- **Palette:** Eco-Emerald primary (`#10B981` / `#059669`), Sky Blue secondary (`#0284C7`), Amber warning (`#F59E0B`), and Rose critical (`#EF4444`).
- **Typography:** System font stack optimized for rapid legibility on mobile hardware.
- **Micro-Interactions:** Confetti particles on point milestones (`canvas-confetti`), live pulsing shift indicators for collectors, and smooth SVG fill level meters.

### 12.2 Role-Tailored Screen Matrix

| Role | View / Page | File Reference | Primary User Functions |
| :--- | :--- | :--- | :--- |
| **Public** | Public Bin Page | [`PublicBinPage.tsx`](file:///c:/dev/web/EcoSense/frontend/src/pages/public/PublicBinPage.tsx) | Scan landing page; view location & fill status; login redirect |
| **Student** | Student Dashboard | [`StudentDashboard.tsx`](file:///c:/dev/web/EcoSense/frontend/src/pages/student/StudentDashboard.tsx) | Points balance, active streak, recent disposals, quick action shortcuts |
| **Student** | Scan & Dispose | [`ScanBinPage.tsx`](file:///c:/dev/web/EcoSense/frontend/src/pages/student/ScanBinPage.tsx) | Integrated camera scanner; manual code fallback; inline disposal form |
| **Student** | AI Classifier | [`AIClassificationPage.tsx`](file:///c:/dev/web/EcoSense/frontend/src/pages/student/AIClassificationPage.tsx)| Camera capture & file dropzone; class breakdown; confidence alerts |
| **Student** | Issue Reporting | [`StudentReportPage.tsx`](file:///c:/dev/web/EcoSense/frontend/src/pages/student/StudentReportPage.tsx)| Report campus waste hazards with photos and location tagging |
| **Student** | Rewards Catalog | [`RewardsCatalogPage.tsx`](file:///c:/dev/web/EcoSense/frontend/src/pages/student/RewardsCatalogPage.tsx)| Browse canteen meal vouchers, bamboo bottles; 1-click redemption |
| **Student** | Leaderboard | [`StudentLeaderboardPage.tsx`](file:///c:/dev/web/EcoSense/frontend/src/pages/student/StudentLeaderboardPage.tsx)| Top campus eco-warriors ranked by verified lifetime earned points |
| **Collector**| Collector Operations| [`CollectorDashboard.tsx`](file:///c:/dev/web/EcoSense/frontend/src/pages/collector/CollectorDashboard.tsx)| Shift check-in/out button; assigned task count; shift history log |
| **Collector**| Empty & Collect | [`CollectorScanPage.tsx`](file:///c:/dev/web/EcoSense/frontend/src/pages/collector/CollectorScanPage.tsx)| Bin QR scan; fill before/after sliders; mass collected (kg) |
| **Collector**| Composting / Recycling| [`CollectorProcessingPage.tsx`](file:///c:/dev/web/EcoSense/frontend/src/pages/collector/CollectorProcessingPage.tsx)| Log organic composting batches and dry recyclable handoffs |
| **Collector**| Predictive Horizons | [`CollectorPredictionsPage.tsx`](file:///c:/dev/web/EcoSense/frontend/src/pages/collector/CollectorPredictionsPage.tsx)| Bins forecasted to exceed 80% fill level within next 2 hours |
| **Admin** | Operations Center | [`AdminCollectorOperationsPage.tsx`](file:///c:/dev/web/EcoSense/frontend/src/pages/admin/AdminCollectorOperationsPage.tsx)| Live collector attendance grid; task assignment; shift audits |
| **Admin** | 13 Analytics Suites | [`AdminAnalyticsPage.tsx`](file:///c:/dev/web/EcoSense/frontend/src/pages/admin/AdminAnalyticsPage.tsx)| Real-time Recharts graphs; diversion rate; waste type breakdown |
| **Admin** | Asset & Placard Print| [`AdminBinsPage.tsx`](file:///c:/dev/web/EcoSense/frontend/src/pages/admin/AdminBinsPage.tsx)| Asset table; create/edit bins; bulk vector PDF placard export |

---

## 13. Security, Privacy, and Reliability

### 13.1 Security Review & Verified Protections

| Security Domain | Mechanism Implemented | Verification & Evidence |
| :--- | :--- | :--- |
| **Password Storage** | Argon2id memory-hard password hashing | Passwords stored with random cryptographic salt; verified in [`backend/app/core/security.py`](file:///c:/dev/web/EcoSense/backend/app/core/security.py) |
| **API Authentication** | Stateless Bearer JSON Web Tokens (JWT) | PyJWT HMAC-SHA256 with 24-hour expiration and user UUID claims |
| **Authorization** | Strict Role-Based Access Control (RBAC) | Enforced server-side via `require_roles("ADMIN", "COLLECTOR")` dependencies |
| **QR Asset Security** | Opaque UUID `qr_token` payloads | Physical QR codes contain NO database IDs, credentials, or mutable parameters |
| **Input Sanitization** | Image URI & Path Traversal Validation | Regex enforces allowed schemes (`http://`, `https://`, `data:image/`); blocks `file://` |
| **Push Privacy** | Decoupled Token Management | FCM tokens stored per user with deactivation on logout; dead tokens auto-pruned |
| **Ledger Integrity** | Double-Entry Append-Only Ledger | Points awarded strictly through `point_transactions`; anti-duplication unique constraints |
| **Timezone Consistency**| Server-Side Normalization | All operational dates stamped server-side in `Asia/Kolkata` (IST) and UTC |

### 13.2 Reliability & Error Handling

- **Database Session Isolation:** Managed via FastAPI `get_db` generator with automatic `try ... finally: db.close()`.
- **Foreign Key Cascades:** Deleting a user cascade-removes their ephemeral device tokens and notifications while preserving historical operational collection and disposal logs.
- **Graceful Push Degradation:** If Firebase service account keys are unconfigured or FCM is disabled, the system logs `SKIPPED_NOT_CONFIGURED` without raising 500 internal server exceptions.

---

## 14. Testing and Quality Assurance

The codebase contains a comprehensive automated test harness spanning both backend services and frontend interfaces:

### 14.1 Test Suite Inventory & Verified Results

```text
============================== TEST EXECUTION SUMMARY ==============================
  Backend Test Suite (Pytest 8.3.0 + HTTPX + Asyncio):
    - Total Test Cases  : 243
    - Passed            : 239
    - Skipped           : 4 (FastAI local model skips when run in headless mock mode)
    - Execution Duration: ~20.06 seconds
    - Coverage Domains  : Auth, Users, Bins, Disposals, Reports, Collections,
                          Processing, Predictions, FastAI Classifier, Gamification,
                          Attendance, Task Operations, Push Notifications, Analytics.

  Frontend Test Suite (Vitest 5.0.1 + Testing Library):
    - Total Test Files  : 9
    - Total Test Cases  : 38
    - Passed            : 38 (100% Passing)
    - Execution Duration: ~5.02 seconds
    - Coverage Domains  : Auth Context, Design System Components, PDF Generator,
                          QR Workflow & Null Safety, Student Reporting Flow,
                          Rewards Redemption, Push Notifications, Collector Operations.

  Production Bundling Verification (Vite 6.4.3 + TypeScript 5.6.3):
    - TypeScript Check  : Passed cleanly (0 errors)
    - Production Bundle : Built in 7.40s (dist/index.html, CSS, JS assets)
====================================================================================
```

### 14.2 Running the Test Suites

```powershell
# 1. Execute Backend Pytest Suite:
cd backend
.\.venv\Scripts\pytest.exe -v

# 2. Execute Frontend Vitest Suite:
cd frontend
npm test

# 3. Verify Production Frontend Build:
cd frontend
npm run build
```

---

## 15. Conclusion and Architectural Sign-Off

The **EcoSense** platform represents a fully realized, academically rigorous, and production-ready campus waste management system. With its modular FastAPI architecture, PostgreSQL relational schema, verified FastAI computer vision integration, time-series forecasting baseline, and Duolingo-inspired student gamification, EcoSense provides Don Bosco Institute of Technology (DBIT), Mumbai, with the technological infrastructure required to achieve a verified Zero Waste Campus.

*Document compiled and verified against active repository implementation.*
