# EcoSense: AI-Based Zero Waste Campus Management Platform

**Institution:** Don Bosco Institute of Technology (DBIT), Mumbai  
**Platform Name:** EcoSense  

---

## 1. Project Overview

EcoSense is an AI-powered campus zero-waste platform designed to automate waste segregation, bin fill monitoring, digital reporting, collection lifecycle management, recycling & composting batch tracking, and campus community engagement through role-based access control (RBAC) and gamification.

---

## 2. Full-Stack Architecture

```
        ┌─────────────────────────────────────────┐
        │       EcoSense Frontend (React + TS)    │
        │   Gamified UI / Duolingo-inspired / SPA │
        │   Port: 5173 (Served via Nginx in Prod) │
        └────────────────────┬────────────────────┘
                             │ HTTP / JSON / JWT
                             ▼
        ┌─────────────────────────────────────────┐
        │       EcoSense Backend (FastAPI)        │
        │   JWT Auth, RBAC, 13 Analytics Endpoints│
        │   Port: 8000                            │
        └────────────────────┬────────────────────┘
                             │ SQLAlchemy 2.x (psycopg v3)
                             ▼
        ┌─────────────────────────────────────────┐
        │       PostgreSQL 16 Database            │
        │   Alembic Migrations / Persistent Volume│
        │   Port: 5432                            │
        └─────────────────────────────────────────┘
```

---

## 3. Technology Stack

- **Frontend:** React 18, TypeScript, Vite, React Router v6, Tailwind CSS, Lucide Icons, Canvas Confetti, HTML5-QRCode
- **Backend:** FastAPI (Python 3.12), Pydantic v2, `pydantic-settings`
- **Database:** PostgreSQL 16+ with `pgcrypto`
- **ORM & Migrations:** SQLAlchemy 2.x, Alembic
- **DB Driver:** `psycopg` (v3 binary)
- **Authentication:** JWT (JSON Web Tokens) with PyJWT & Argon2id password hashing
- **Containerization:** Docker & Docker Compose (Multi-stage build & Nginx static serving)
- **Testing:** `pytest` (183 tests) & `vitest` (7 tests)

---

## 4. Running EcoSense with Docker Compose (Recommended)

### Prerequisites
- [Docker Desktop](https://www.docker.com/products/docker-desktop/) with Docker Compose v2+

### 1. Start the entire application:
```bash
docker compose up --build
```

This single command automatically:
1. Starts the `ecosense-postgres` database service and verifies health.
2. Starts the `ecosense-backend` container, executes `alembic upgrade head`, seeds initial DBIT data, and launches FastAPI.
3. Builds the production frontend bundle and serves it via `ecosense-frontend` (Nginx).

### 2. Accessing the Services:
- **Frontend App:** [http://localhost:5173](http://localhost:5173)
- **FastAPI Backend:** [http://localhost:8000](http://localhost:8000)
- **Interactive OpenAPI Docs (Swagger UI):** [http://localhost:8000/docs](http://localhost:8000/docs)
- **Alternative API Docs (ReDoc):** [http://localhost:8000/redoc](http://localhost:8000/redoc)
- **Backend Health Check:** [http://localhost:8000/health](http://localhost:8000/health)

### 3. Stopping the Application:
```bash
# Stop containers while preserving database volume:
docker compose down

# Stop containers and RESET all database data:
docker compose down -v
```

---

## 5. Local Development Workflow (Without Docker)

### Option A: Running Locally

#### 1. Start Backend:
```bash
cd backend
python -m venv .venv
# Windows:
.venv\Scripts\activate
# Linux/macOS:
source .venv/bin/activate

pip install -r requirements.txt
cp .env.example .env

# Run database migrations:
alembic upgrade head

# Start FastAPI server:
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```
OR
```bash
cd backend
python -m venv .venv
.venv\Scripts\activate
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

#### 2. Start Frontend:
```bash
cd frontend
npm install
cp .env.example .env
npm run dev
```
OR 
```bash
cd frontend
npm run dev
```
The frontend will be live at `http://localhost:5173`.

---

## 6. Demo User Accounts (Pre-Seeded)

| Role | Email | Password | Default Interface |
| :--- | :--- | :--- | :--- |
| **Student** | `student@dbit.in` | `studentpassword` | `/student/dashboard` |
| **Staff** | `staff@dbit.in` | `staffpassword` | `/staff/dashboard` |
| **Collector** | `collector@dbit.in` | `collectorpassword` | `/collector/dashboard` |
| **Admin** | `admin@dbit.in` | `adminpassword` | `/admin/dashboard` |

---

## 7. Running the Test Suites

### Backend Test Suite (183 tests):
```bash
cd backend
.\.venv\Scripts\pytest.exe -v
```

### Frontend Test Suite (7 tests):
```bash
cd frontend
npm test
```

### Production Build Verification:
```bash
cd frontend
npm run build
```

---

## 8. Repository Structure

```text
EcoSense/
├── frontend/             # React + TypeScript + Vite SPA
│   ├── src/
│   │   ├── api/          # Typed API client & domain modules
│   │   ├── components/   # EcoSense design system components
│   │   ├── context/      # AuthContext & JWT session store
│   │   ├── layouts/      # AppShell, Sidebar, Header, MobileNav
│   │   ├── pages/        # Role-tailored views (Student, Staff, Collector, Admin)
│   │   ├── routes/       # ProtectedRoute, RoleRoute, AppRoutes
│   │   └── types/        # TypeScript schemas matching Backend
│   ├── Dockerfile        # Multi-stage production container
│   ├── nginx.conf        # Production Nginx SPA configuration
│   └── package.json
├── backend/              # FastAPI Backend
│   ├── app/
│   │   ├── api/v1/       # 13 REST API domain routers
│   │   ├── core/         # Config, Database engine, Security, Dependencies
│   │   ├── models/       # SQLAlchemy 2.x ORM models
│   │   ├── schemas/      # Pydantic v2 schemas
│   │   └── services/     # Business logic & algorithms
│   ├── alembic/          # Database migrations (0001 to 0008)
│   ├── scripts/          # start.sh container entrypoint & seed scripts
│   ├── Dockerfile        # Python 3.12 container
│   └── requirements.txt
├── docker-compose.yml    # Root multi-container orchestration
└── README.md
```
